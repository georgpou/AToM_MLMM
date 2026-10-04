"""Independently challenge declarative settings, journal and actual handover."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import openmm as mm
from atm_mlmm.adapters.atom import build_atom,export_worker_run,load_worker_run
from atm_mlmm.persistence import commit_sample_chunk,read_sample_chunks,write_json
from atm_mlmm.schema import IdentityError,MalformedInput,UnsupportedCapability
from atm_mlmm.workflow import load_configuration
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE

OUT=Path(__file__).resolve().parent
ROOT=Path('/tmp/atm-mlmm-g09-independent-readonly')
work=Path(tempfile.mkdtemp(prefix='g09-independent-admission-',dir='/tmp'))
rejections=[]
def reject(name,call,types=(IdentityError,MalformedInput,UnsupportedCapability,ValueError,FileExistsError)):
    try:call()
    except types as error:
        rejections.append(dict(name=name,type=type(error).__name__,message=str(error)))
    else:raise AssertionError('unexpected admission: '+name)

fixture=ROOT/'fixtures/cloud_host_guest/v2'
base=json.loads((fixture/'config.json').read_text())
base['input_manifest']=str(fixture/'manifest.json')
for name,key,value in (
    ('boolean seed','seed',True),('negative seed','seed',-1),('too large seed','seed',2**31),
    ('zero dt','timestep_ps',0.),('NaN dt','timestep_ps',float('nan')),
    ('infinite temperature','temperature_K',float('inf')),('CPU platform','platform','CPU'),
    ('unknown integrator','integrator','Verlet'),('solvent setting','solvent','water'),
    ('wrong ligand count','protocol_kind','rbfe'),('unknown protocol','protocol_kind','relax'),
    ('zero displacement','displacement_nm',[0.,0.,0.]),('bool displacement','displacement_nm',[True,0.,0.]),
    ('infinite displacement','displacement_nm',[float('inf'),0.,0.]),
    ('negative restraint','outside_spring_kj_mol_nm2',-1.),
    ('phase equality','temperatures_K',[10.,10.,300.]),('wrong last temperature','temperatures_K',[10.,200.]),
    ('negative phase step','steps_per_phase',-1),('boolean frame count','frames_per_state',True),
    ('float frame step','steps_per_frame',1.5),('unbounded sample count','frames_per_state',999999)):
    doc=deepcopy(base);doc['settings'][key]=value
    path=work/'config.json';path.write_text(json.dumps(doc))
    reject(name,lambda:load_configuration(path))
valid=work/'valid-config.json';valid.write_text(json.dumps(base))
cfg=load_configuration(valid)
assert len(cfg.original.topology.atoms)==48 and len(cfg.schedule.states)==3
for kind,atoms in (('abfe',32),('rbfe',41)):
    config=load_configuration(ROOT/'fixtures/cloud_fragment_controls/v1'/kind/'config.json')
    assert len(config.original.topology.atoms)==atoms
doc=deepcopy(base);doc['input_manifest_sha256']='0'*64
(work/'config.json').write_text(json.dumps(doc))
reject('manifest wrong identity',lambda:load_configuration(work/'config.json'))
from atm_mlmm.partition import resolve_partition
host=cfg.original.topology.molecules[0]
topology=replace(cfg.original.topology,molecules=(replace(host,multiplicity=3),cfg.original.topology.molecules[1]))
reject('host triplet',lambda:resolve_partition(topology,cfg.partition))
reject('host negative charge',lambda:resolve_partition(replace(topology,molecules=(replace(host,formal_charge=-1),topology.molecules[1])),cfg.partition))
reject('partial host',lambda:resolve_partition(cfg.original.topology,replace(cfg.partition,ml_ids=cfg.partition.ml_ids[1:])))

record=dict(sample_id='first',walker_id='walker',sequence_number=1)
journal=work/'journal'
commit_sample_chunk(journal,0,record,'<State/>',b'checkpoint')
assert read_sample_chunks(journal)==[record]
reject('immutable existing chunk',lambda:commit_sample_chunk(journal,0,record,'<State/>',b'checkpoint'))
for index in (-1,True,1000000,1.5):
    reject('journal index '+repr(index),lambda index=index:commit_sample_chunk(work/'bad-index',index,record,'<State/>',b'checkpoint'))
for name,mutation in (
    ('record corruption',lambda p:(p/'000000/record.json').write_text('{}')),
    ('State corruption',lambda p:(p/'000000/state.xml').write_text('<State bad="1"/>')),
    ('checkpoint corruption',lambda p:(p/'000000/checkpoint.chk').write_bytes(b'wrong')),
    ('unknown entry',lambda p:(p/'lost-record.json').write_text('{}')),
    ('missing first index',lambda p:(p/'000000').rename(p/'000001')),
    ('pending transaction',lambda p:(p/'.pending-000001-probe').mkdir()),
    ('duplicate sample',lambda p:commit_sample_chunk(p,1,{**record,'sequence_number':2},'<State/>',b'checkpoint')),
    ('repeated walker sequence',lambda p:commit_sample_chunk(p,1,{**record,'sample_id':'second'},'<State/>',b'checkpoint'))):
    candidate=work/name.replace(' ','-');shutil.copytree(journal,candidate);mutation(candidate)
    before={str(p.relative_to(candidate)):hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate.rglob('*') if p.is_file()}
    reject(name,lambda:read_sample_chunks(candidate))
    after={str(p.relative_to(candidate)):hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate.rglob('*') if p.is_file()}
    assert before==after,'rejection discarded evidence: '+name

physical,transfer,schedule,restraints,snapshot=atom_case('rbfe',old_to_new=(6,2,4,0,5,1,3))
export=work/'export'
with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
    _,digest=export_worker_run(source,export,snapshot,'second',integrator_seed=719)
with load_worker_run(export,digest,trusted=True) as worker:
    assert type(worker.worker).__name__=='OMMWorkerATMSync'
    assert worker.worker.context is worker.evaluator.context
    assert worker.evaluator.integrator.getRandomNumberSeed()==719
    assert len(worker.bundle.transfer.protocol.mobile_groups)==2
    valid_checkpoint=worker.evaluator.context.createCheckpoint()
    reject('checkpoint wrong state',lambda:worker.restore_checkpoint(valid_checkpoint,'first'))
reject('absent trust',lambda:load_worker_run(export,digest))
reject('wrong manifest hash',lambda:load_worker_run(export,'0'*64,trusted=True))
for name,mutation in (
    ('worker unknown state',lambda m,d:m.update(state_id='unknown')),
    ('worker reversed real ids',lambda m,d:m['real_atom_ids'].reverse()),
    ('worker physical identity',lambda m,d:m.update(physical_identity='0'*64)),
    ('worker runtime identity',lambda m,d:m.update(runtime_identity='0'*64)),
    ('worker parameter mismatch',lambda m,d:m['parameters'].update(UOffset=42.)),
    ('worker invalid seed',lambda m,d:m.update(integrator_seed=True)),
    ('worker missing core file',lambda m,d:m['files'].pop('handover_0.xml')),
    ('worker path escape',lambda m,d:m['files'].update({'../outside.txt':'0'*64}))):
    candidate=work/name.replace(' ','-');shutil.copytree(export,candidate)
    manifest=json.loads((candidate/'manifest.json').read_text());mutation(manifest,candidate)
    write_json(candidate/'manifest.json',manifest)
    expected=hashlib.sha256((candidate/'manifest.json').read_bytes()).hexdigest()
    reject(name,lambda:load_worker_run(candidate,expected,trusted=True))
report=dict(rejections=len(rejections),cases=rejections,valid_configurations=[48,32,41],
            actual_constructor='OMMWorkerATMSync',rbfe_groups=2,seed_before_context=719,
            work_directory=str(work),failed_evidence_unchanged=True)
(OUT/'admission-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
