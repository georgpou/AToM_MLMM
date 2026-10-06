"""Independent repaired admission/runtime/durability controls and characterizations.

Fresh current-source tiny analytic bundles only. Negative cases reach their
intended validator; actual fsync syscall interception records the failing fd.
"""
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET

import numpy as np
import openmm as mm
from openmm import unit

ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = Path(__file__).resolve().parent
ART = Path('/tmp/G10_v7_independent_artifacts')
sys.path.insert(0,str(ROOT))
from atm_mlmm import exchange as c, exchange_journal as j
from atm_mlmm.adapters import atom
from atm_mlmm.persistence import read_json, write_json
from atm_mlmm.workflow import _snapshot
from tests.workflow.test_persistent_exchange import prepare_multistate, _reseal_multistate_geometry_collision

RESULTS = []
def tree(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()}
def record(name, status='PASS', **details):
    RESULTS.append(dict(name=name,status=status,**details))
    (HERE/'repair-results.json').write_text(json.dumps(dict(probes=RESULTS,
        pass_count=sum(r['status']=='PASS' for r in RESULTS),
        violation_count=sum(r['status']=='VIOLATION' for r in RESULTS),
        artifacts=str(ART),finished_utc=datetime.now(timezone.utc).isoformat()),indent=2,sort_keys=True)+'\n')
    print(json.dumps(RESULTS[-1],sort_keys=True),flush=True)
def clone(name):
    run=ART/name; shutil.copytree(ART/'prefix',run)
    return run,read_json(run/'metadata.json'),run/'boundaries/000000'
def edit(path, action):
    d=read_json(path); action(d); write_json(path,d)
def reseal(run, initial=False):
    if initial:
        digest=j.seal_tree(run/'initial',index=-1)
        edit(run/'metadata.json',lambda d:d.update(initial_manifest_sha256=digest))
        edit(run/'boundaries/000000/record.json',lambda d:d.update(previous_manifest_sha256=digest))
    j.seal_tree(run/'boundaries/000000',index=0)
    (run/'metadata.sha256').write_text(j.sha(run/'metadata.json')+'\n')
def error_call(action):
    try: action()
    except Exception as e: return f'{type(e).__name__}: {e}'
    return None
def inert(name, action, initial=False, expect_reject=True):
    run,meta,b=clone(name); action(run,meta,b); reseal(run,initial)
    before=tree(run); calls=[]
    def loader(*args,**kw):
        calls.append(kw.get('integrator_seed')); raise RuntimeError('independent loader sentinel')
    reader=error_call(lambda:j.read_multistate_boundaries(run))
    with patch.object(atom,'load_worker_run',loader):
        resume=error_call(lambda:c.resume_multistate_exchange(run,trusted=True))
    rejected=reader is not None and not calls and before==tree(run)
    status='PASS' if rejected else 'VIOLATION'
    record(name,status,reader_error=reader,resume_error=resume,loader_calls=calls,
           tree_unchanged=before==tree(run),intended_rejection=expect_reject,
           boundary_manifest_sha256=j.sha(b/'manifest.json'))

def inert_controls():
    cases=[
      ('numpy-key-boolean',lambda r,m,b:edit(b/'rng.json',lambda d:d['numpy'][1].__setitem__(0,True))),
      ('numpy-key-overflow',lambda r,m,b:edit(b/'rng.json',lambda d:d['numpy'][1].__setitem__(0,2**32))),
      ('numpy-index-boolean',lambda r,m,b:edit(b/'rng.json',lambda d:d['numpy'].__setitem__(2,True))),
      ('numpy-cache-nonfinite',lambda r,m,b:edit(b/'rng.json',lambda d:d['numpy'].__setitem__(4,float('inf')))),
      ('numpy-cache-flag-invalid',lambda r,m,b:edit(b/'rng.json',lambda d:d['numpy'].__setitem__(3,2))),
      ('python-version-two',lambda r,m,b:edit(b/'rng.json',lambda d:d['python'].__setitem__(0,2))),
      ('python-internal-short',lambda r,m,b:edit(b/'rng.json',lambda d:d['python'][1].pop())),
      ('python-index-overflow',lambda r,m,b:edit(b/'rng.json',lambda d:d['python'][1].__setitem__(-1,625))),
      ('sample-time-boolean',lambda r,m,b:edit(b/'samples/worker-000.json',lambda d:d.update(time_ps=True))),
      ('sample-time-string',lambda r,m,b:edit(b/'samples/worker-000.json',lambda d:d.update(time_ps='.0005'))),
      ('nested-manifest-resealed',lambda r,m,b:(b/'attempts/0001/manifest.json').write_text('new nested bytes\n')),
      ('nested-extra-directory',lambda r,m,b:(b/'unexpected').mkdir()),
      ('same-step-time-shift',lambda r,m,b:(edit(b/'samples/worker-000.json',lambda d:d.update(time_ps=.0105)),
                                            edit(b/'final-state-reports.json',lambda d:d['workers'][0].update(time_ps=.0105)))),
    ]
    for name,action in cases: inert(name,action)
    py=random.Random(31); nu=np.random.RandomState(33)
    py.gauss(0,1); nu.normal()
    doc=json.loads(json.dumps(c._rng_document(py,nu)))
    j._validate_rng_document(doc); p2,n2=c._rng_from_document(doc)
    assert [py.gauss(0,1) for _ in range(5)]==[p2.gauss(0,1) for _ in range(5)]
    assert nu.normal(size=9).tolist()==n2.normal(size=9).tolist()
    record('both-finite-gaussian-cache-roundtrip',python_cache=doc['python'][2],numpy_cache=doc['numpy'][4])
    # Entire timeline has negative times but exact positive elapsed increments.
    def negative(r,m,b):
        edit(r/'initial/final-state-reports.json',lambda d:d['workers'][0].update(time_ps=-1.0))
        edit(b/'samples/worker-000.json',lambda d:d.update(time_ps=-.9995))
        edit(b/'final-state-reports.json',lambda d:d['workers'][0].update(time_ps=-.9995))
    inert('negative-clock-domain',negative,initial=True)
    # Finite nonnegative origin causes the arithmetic envelope to overflow.
    def huge_origin(r,m,b):
        reports=r/'initial/final-state-reports.json'
        state_id=m['state_ids'][0]
        with atom.load_worker_run(r/'worker',m['worker_manifest_sha256'],trusted=True,
                                 integrator_seed=m['integrator_seed_base']) as worker:
            worker.restore_checkpoint((r/'initial/workers/worker-000.chk').read_bytes(),state_id)
            before=_snapshot(worker); worker.evaluator.context.setTime(1e308*unit.picosecond)
            assert before==_snapshot(worker)
            (r/'initial/workers/worker-000.chk').write_bytes(worker.evaluator.context.createCheckpoint())
            state=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
            (r/'initial/workers/worker-000-state.xml').write_text(mm.XmlSerializer.serialize(state))
        edit(reports,lambda d:d['workers'][0].update(time_ps=1e308))
    inert('finite-origin-overflow-admits-backward-clock',huge_origin,initial=True)

def arithmetic():
    controls=[]
    for origin,n in ((0.,100000),(0.,999999),(10.,999999),(123.25,100000),(1e6,100000)):
        time_ps=origin; dt=.0005
        for _ in range(n): time_ps+=dt
        j._validate_expected_clock(17+n,time_ps,{'step':17,'time_ps':origin},n,dt)
        controls.append(dict(origin_ps=origin,steps=n,repeated_time_ps=time_ps,
                             product_time_ps=origin+n*dt,error_ps=abs(time_ps-(origin+n*dt))))
    record('gamma-n-valid-repeated-additions',controls=controls)
    failures=[]
    for step,time_ps in ((18,.0105),(19,.0005),(17,0.)):
        e=error_call(lambda:j._validate_expected_clock(step,time_ps,{'step':17,'time_ps':0.},1,.0005))
        assert e; failures.append(dict(step=step,time_ps=time_ps,error=e))
    record('gamma-n-normal-invalid-increments',controls=failures)
    e=error_call(lambda:j._validate_expected_clock(1,0.,{'step':0,'time_ps':1e308},1,.0005))
    record('gamma-n-finite-domain-overflow', 'VIOLATION' if e is None else 'PASS',
           origin_ps=1e308,actual_time_ps=0.,steps=1,timestep_ps=.0005,error=e,
           mathematical_bound_infinite=True,observed_backward_delta_ps=-1e308)

def runtime_controls():
    for name,w,portable_only,time_only in (
        ('actual-clock-step99-time999',0,False,False),
        ('later-worker-actual-clock',2,False,True),
        ('portable-clock-mismatch',1,True,False)):
        run,m,b=clone(name); stem=f'worker-{w:03d}'
        state=m['state_ids'][read_json(b/'record.json')['walker_to_state_final'][w]]
        if portable_only:
            path=b/'workers'/f'{stem}-state.xml'; doc=ET.fromstring(path.read_text())
            doc.set('stepCount','99'); doc.set('time','9.99'); path.write_text(ET.tostring(doc,encoding='unicode'))
        else:
            with atom.load_worker_run(run/'worker',m['worker_manifest_sha256'],trusted=True,
                integrator_seed=m['integrator_seed_base']+w) as worker:
                worker.restore_checkpoint((b/'workers'/f'{stem}.chk').read_bytes(),state)
                before=_snapshot(worker)
                if not time_only: worker.evaluator.context.setStepCount(99)
                worker.evaluator.context.setTime(9.99*unit.picosecond)
                assert before==_snapshot(worker)
                (b/'workers'/f'{stem}.chk').write_bytes(worker.evaluator.context.createCheckpoint())
                saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                (b/'workers'/f'{stem}-state.xml').write_text(mm.XmlSerializer.serialize(saved))
        reseal(run); assert len(j.read_multistate_boundaries(run))==1
        evaluations=[]; steps=[]; before=tree(run)
        with patch.object(atom.WorkerRun,'evaluate',lambda *a,**kw:evaluations.append(True)), \
             patch.object(mm.LangevinMiddleIntegrator,'step',lambda *a,**kw:steps.append(True)):
            e=error_call(lambda:c.resume_multistate_exchange(run,trusted=True))
        assert e and 'clock' in e and not evaluations and not steps and not (run/'pending').exists()
        assert before==tree(run)
        record(name,reader_admitted=True,error=e,evaluations=evaluations,integration_steps=steps,tree_unchanged=True)
    for w,map_index in ((2,0),(0,1)):
        name=f'actual-map{map_index}-worker{w}'
        run,m,b=clone(name); _reseal_multistate_geometry_collision(run,w,map_index)
        assert len(j.read_multistate_boundaries(run))==1
        evaluations=[]; steps=[]; guards=[]; before=tree(run); original=c._geometry
        def geometry(worker,snapshot,settings):
            guards.append({'seed':worker.integrator_seed,'step':worker.evaluator.context.getStepCount()})
            return original(worker,snapshot,settings)
        with patch.object(atom.WorkerRun,'evaluate',lambda *a,**kw:evaluations.append(True)), \
             patch.object(mm.LangevinMiddleIntegrator,'step',lambda *a,**kw:steps.append(True)), \
             patch.object(c,'_geometry',geometry):
            e=error_call(lambda:c.resume_multistate_exchange(run,trusted=True))
        assert e and f'map{map_index}' in e and not evaluations and not steps
        assert before==tree(run) and not (run/'pending').exists()
        record(name,reader_admitted=True,error=e,guard_calls=guards,evaluations=evaluations,
               integration_steps=steps,energy_consistent_all_phases=True,tree_unchanged=True)

def transaction_controls():
    reference=ART/'reference'; shutil.copytree(ART/'prefix',reference)
    c.resume_multistate_exchange(reference,trusted=True)
    reference_tree=tree(reference/'boundaries/000001')
    for fault in ('destination-parent','source-parent','records','observations','summary','secondary-checkpoint-open'):
        run,m,b=clone('transaction-'+fault); target=run/'boundaries/000001'
        old=tree(b); events=[]; post_evals=[]; published=[False]; injected=[False]
        old_fsync=os.fsync; old_rename=os.rename; old_evaluate=atom.WorkerRun.evaluate; old_open=Path.open
        old_write=c.write_json
        def rename(source,destination):
            result=old_rename(source,destination)
            if Path(destination)==target: published[0]=True
            events.append({'op':'rename','source':str(source),'target':str(destination)})
            return result
        def fsync(fd):
            path=Path(os.readlink(f'/proc/self/fd/{fd}')); fail=False
            if published[0] and fault.endswith('parent') and not injected[0]:
                expected=run/'boundaries' if fault.startswith('destination') else run
                fail=path==expected
            events.append({'op':'fsync','path':str(path),'injected_EIO':fail})
            if fail: injected[0]=True; raise OSError('independent actual '+fault+' fsync EIO')
            return old_fsync(fd)
        def evaluate(self,*args,**kwargs):
            if published[0]: post_evals.append(self.integrator_seed)
            return old_evaluate(self,*args,**kwargs)
        def write(path,document):
            name=Path(path).name
            if fault in ('observations','summary') and name==fault+'.json':
                raise OSError('independent '+fault+' write failure')
            return old_write(path,document)
        def open_file(self,*args,**kwargs):
            if (fault=='secondary-checkpoint-open' and self.name=='checkpoint.chk' and
                self.parent.name=='worker-001' and self.parent.parent.name.startswith('postcommit-')):
                raise OSError('secondary checkpoint actual open ENOSPC')
            return old_open(self,*args,**kwargs)
        with ExitStack() as stack:
            stack.enter_context(patch.object(os,'fsync',fsync)); stack.enter_context(patch.object(os,'rename',rename))
            stack.enter_context(patch.object(atom.WorkerRun,'evaluate',evaluate))
            stack.enter_context(patch.object(c,'write_json',write)); stack.enter_context(patch.object(Path,'open',open_file))
            if fault in ('records','secondary-checkpoint-open'):
                stack.enter_context(patch.object(c,'to_json',lambda *a:(_ for _ in ()).throw(OSError('independent records primary failure'))))
            e=error_call(lambda:c.resume_multistate_exchange(run,trusted=True))
        assert e and not post_evals and len(j.read_multistate_boundaries(run))==2
        assert tree(b)==old and tree(target)==reference_tree and not (run/'pending').exists()
        archive=next((run/'failures').glob('postcommit-*')); primary=read_json(archive/'error.json')
        assert primary['message'] in e and primary['commit_authoritative']
        for w in range(3):
            folder=archive/f'worker-{w:03d}'
            for name in ('state.xml','map0-state.xml','map1-state.xml','error.json'):
                assert (folder/name).is_file()
            assert (folder/'state.xml').read_bytes()==(target/'workers'/f'worker-{w:03d}-state.xml').read_bytes()
            if not (fault=='secondary-checkpoint-open' and w==1):
                assert (folder/'checkpoint.chk').read_bytes()==(target/'workers'/f'worker-{w:03d}.chk').read_bytes()
        assert bool(primary['archive_errors'])==(fault=='secondary-checkpoint-open')
        c.resume_multistate_exchange(run,trusted=True)
        assert tree(target)==reference_tree and len(read_json(run/'observations.json'))==6
        record('postcommit-'+fault,error=e,primary=primary,no_evaluation_reentry=True,
               authoritative_and_replayed_bytes_equal=True,fsync_fault_events=[e for e in events if e.get('injected_EIO')],
               postrename_parent_events=[e for e in events[1:] if e['op']=='fsync' and e['path'] in (str(run),str(run/'boundaries'))])

def rollback_controls():
    old_fsync=os.fsync; old_rename=os.rename
    for fault in ('none','source-parent','destination-parent'):
        run,m,b=clone('rollback-'+fault); prefix=tree(b)
        pending=run/'pending'; nested=pending/'failures/worker-001/nested'
        nested.mkdir(parents=True); (nested/'state.xml').write_text('<State />\n')
        write_json(pending/'failure.json',{'error_type':'OSError','message':'retained scientific primary'})
        before=tree(pending); files={str(pending/p) for p in before}; dirs={str(p) for p in pending.rglob('*') if p.is_dir()}|{str(pending)}
        events=[]; renamed=[False]; injected=[False]
        def fsync(fd):
            path=os.readlink(f'/proc/self/fd/{fd}')
            expected=str(run if fault=='source-parent' else run/'failures')
            fail=renamed[0] and fault!='none' and path==expected and not injected[0]
            events.append({'op':'fsync','path':path,'injected_EIO':fail})
            if fail: injected[0]=True; raise OSError('independent rollback '+fault+' actual fsync EIO')
            return old_fsync(fd)
        def rename(source,target):
            result=old_rename(source,target); renamed[0]=True
            events.append({'op':'rename','source':str(source),'target':str(target)})
            return result
        with patch.object(os,'fsync',fsync),patch.object(os,'rename',rename):
            e=error_call(lambda:j.preserve_multistate_pending(run))
        cut=next(i for i,e in enumerate(events) if e['op']=='rename')
        synced={e['path'] for e in events[:cut] if e['op']=='fsync'}
        assert files<=synced and dirs<=synced and str(pending/'rollback.json') in synced
        after={e['path'] for e in events[cut+1:] if e['op']=='fsync'}
        assert {str(run),str(run/'failures')}<=after
        assert (e is not None)==(fault!='none') and tree(b)==prefix
        archive=next((run/'failures').glob('rollback-*')); saved=read_json(archive/'rollback.json')
        assert saved['preserved_file_hashes']==before
        assert read_json(archive/'failure.json')['message']=='retained scientific primary'
        c.resume_multistate_exchange(run,trusted=True)
        assert tree(run/'boundaries/000001')==tree(ART/'reference/boundaries/000001')
        record('rollback-'+fault,error=e,events=events,preserved_files=len(before),
               all_files_and_nested_directories_synced_before_rename=True,both_parents_attempted_after_rename=True,
               authoritative_prefix_and_exact_replay=True,power_loss_test=False)

def main():
    ART.mkdir(exist_ok=False)
    prepared=prepare_multistate(ART/'prepared')
    c.run_multistate_exchange(prepared,ART/'prefix',state_ids=('first','middle','third'),
        state_pairs=((0,1),(1,2)),boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    inert_controls(); arithmetic(); runtime_controls(); transaction_controls(); rollback_controls()
    failures=sum(r['status']=='VIOLATION' for r in RESULTS)
    print(json.dumps({'probe_count':len(RESULTS),'violation_count':failures,'exit_status':int(bool(failures))}))
    return int(bool(failures))

if __name__=='__main__': sys.exit(main())
