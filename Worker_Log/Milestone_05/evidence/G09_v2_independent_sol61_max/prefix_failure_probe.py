"""Actual ABFE/RBFE failure origins after one immutable committed sample.

This is an exception-boundary oracle on the accepted analytic toy. Geometry
admission is stubbed explicitly; it makes no additional molecular-domain claim.
"""
from pathlib import Path
from unittest.mock import patch
import hashlib,json,shutil,tempfile
import openmm as mm
from openmm import unit
import atm_mlmm.adapters.atom as adapter
import atm_mlmm.workflow as workflow
from atm_mlmm.persistence import read_sample_chunks
from atm_mlmm.schema import NumericalDomainError
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE

OUT=Path(__file__).resolve().parent
WORK=Path(tempfile.mkdtemp(prefix='g09-v2-independent-prefix-',dir='/tmp'))
reports=[]
normal_load=adapter.load_worker_run
normal_step=mm.LangevinMiddleIntegrator.step
normal_state=mm.Context.getState
normal_evaluate=adapter.WorkerRun.evaluate
normal_restore=adapter.WorkerRun.restore_checkpoint
for kind in ('abfe','rbfe'):
    base=WORK/kind
    physical,transfer,schedule,restraints,snapshot=atom_case(kind)
    with adapter.build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        _,digest=adapter.export_worker_run(source,base/'worker',snapshot,'first',integrator_seed=701)
    metadata={'settings':{'frames_per_state':2,'steps_per_frame':2,'seed':701,
                         'displacement_nm':[.3,0.,0.],'protocol_kind':kind},
              'worker_manifest_sha256':digest,'run_id':'independent-'+kind,
              'runtime_identity':REFERENCE.content_identity,'profile':{}}
    with patch.object(workflow,'_domain',lambda *args:[]):
        assert workflow._execute(base,metadata,stop_after_samples=1)['samples']==1
    prefix=read_sample_chunks(base/'samples')
    for origin in ('guard','integration','final_state'):
        directory=WORK/(kind+'-'+origin);shutil.copytree(base,directory)
        before={str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (directory/'samples').rglob('*') if p.is_file()}
        owners={};fault={}
        injected=NumericalDomainError('independent '+origin+' failure after committed prefix')
        def capture(worker):
            assert type(worker.worker).__name__=='OMMWorkerATMSync'
            context=worker.evaluator.context
            state=normal_state(context,getPositions=True,getVelocities=True,getParameters=True)
            fault.update(xml=mm.XmlSerializer.serialize(state),checkpoint=context.createCheckpoint(),
                         step=context.getStepCount(),time=state.getTime().value_in_unit(unit.picosecond),
                         triggered=True)
        def load(*args,**kwargs):
            worker=normal_load(*args,**kwargs);owners[id(worker.evaluator.integrator)]=worker
            return worker
        def step(integrator,steps):
            normal_step(integrator,steps)
            if origin=='integration':
                capture(owners[id(integrator)]);raise injected
        def restore(worker,*args,**kwargs):
            normal_restore(worker,*args,**kwargs)
            if origin=='guard':
                def fail_guard():
                    capture(worker);raise injected
                worker.evaluator._guard=fail_guard
        def evaluate(worker,*args,**kwargs):
            result=normal_evaluate(worker,*args,**kwargs)
            if origin=='final_state':capture(worker);fault['pending_state_failure']=True
            return result
        def state(context,*args,**kwargs):
            if fault.get('pending_state_failure') and kwargs.get('getPositions') and kwargs.get('getEnergy'):
                fault['pending_state_failure']=False;raise injected
            if fault.get('triggered') and (kwargs.get('getEnergy') or kwargs.get('getForces')):
                raise AssertionError('failure capture reentered energy/forces')
            return normal_state(context,*args,**kwargs)
        with patch.object(workflow,'_domain',lambda *args:[]),patch.object(adapter,'load_worker_run',load),\
             patch.object(mm.LangevinMiddleIntegrator,'step',step),patch.object(adapter.WorkerRun,'restore_checkpoint',restore),\
             patch.object(adapter.WorkerRun,'evaluate',evaluate),patch.object(mm.Context,'getState',state):
            try:workflow._execute(directory,metadata)
            except NumericalDomainError as error:assert error is injected
            else:raise AssertionError('injected error did not propagate')
        assert read_sample_chunks(directory/'samples')==prefix
        after={str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (directory/'samples').rglob('*') if p.is_file()}
        assert before==after and len(after)==4
        failed=directory/'failure-000001'
        assert (failed/'state.xml').read_text()==fault['xml']
        assert (failed/'checkpoint.chk').read_bytes()==fault['checkpoint']
        error=json.loads((failed/'error.json').read_text())
        expected=dict(error_type='NumericalDomainError',message=str(injected),state_id='first',
                      walker_id=metadata['run_id']+':first',attempted_sample_id=metadata['run_id']+':first:2',
                      sequence_number=2,journal_index=1,actual_step=fault['step'],actual_time_ps=fault['time'])
        assert error==expected
        assert fault['step']==(2 if origin=='guard' else 4)
        assert len(list(directory.glob('failure-*')))==1
        destination=OUT/'retained-faults'/(kind+'-'+origin)
        shutil.copytree(failed,destination)
        report=dict(protocol=kind,origin=origin,exact_State=True,exact_checkpoint=True,
                    original_exception_object=True,energy_force_reentry=False,
                    committed_prefix_unchanged=True,committed_samples=1,provenance=error,
                    archive_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir()})
        reports.append(report)
(OUT/'prefix-failure-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(dict(cases=len(reports),all_passed=True,origins=['guard','integration','final_state'],
                     protocols=['abfe','rbfe'],existing_prefix_samples=1,work_directory=str(WORK)),indent=2))
