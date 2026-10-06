"""Resume the frozen audit without preparing or repeating completed cases.

The original script, its failed log/results, and pause archive stay immutable.
All new copies use cont-* names. JSON 1e309 is a syntactically valid raw number;
the production serializer is never weakened to create nonfinite declarations.
"""
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
from unittest.mock import patch

import numpy as np
import openmm as mm

import repair_probe as p

HERE = p.HERE
ORIGINAL = HERE / 'repair-results.json'
ORIGINAL_HASH = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
p.RESULTS = json.loads(ORIGINAL.read_text())['probes']
original_clone = p.clone
p.clone = lambda name: original_clone('cont-' + name)


def record(name, status='PASS', **details):
    p.RESULTS.append(dict(name=name, status=status, **details))
    result = dict(probes=p.RESULTS, pass_count=sum(r['status']=='PASS' for r in p.RESULTS),
                  violation_count=sum(r['status']=='VIOLATION' for r in p.RESULTS),
                  artifacts=str(p.ART), resumed_original_sha256=ORIGINAL_HASH,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    (HERE/'repair-continuation-results.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(p.RESULTS[-1], sort_keys=True), flush=True)


p.record = record


def raw_overflow(run, metadata, boundary):
    path = boundary/'rng.json'
    document = p.read_json(path)
    document['numpy'][4] = '__AUDIT_RAW_OVERFLOW__'
    path.write_text(json.dumps(document, sort_keys=True).replace('"__AUDIT_RAW_OVERFLOW__"','1e309')+'\n')


def remaining_inert():
    cases = [
        ('numpy-cache-nonfinite', raw_overflow),
        ('numpy-cache-flag-invalid', lambda r,m,b:p.edit(b/'rng.json',lambda d:d['numpy'].__setitem__(3,2))),
        ('python-version-two',lambda r,m,b:p.edit(b/'rng.json',lambda d:d['python'].__setitem__(0,2))),
        ('python-internal-short',lambda r,m,b:p.edit(b/'rng.json',lambda d:d['python'][1].pop())),
        ('python-index-overflow',lambda r,m,b:p.edit(b/'rng.json',lambda d:d['python'][1].__setitem__(-1,625))),
        ('sample-time-boolean',lambda r,m,b:p.edit(b/'samples/worker-000.json',lambda d:d.update(time_ps=True))),
        ('sample-time-string',lambda r,m,b:p.edit(b/'samples/worker-000.json',lambda d:d.update(time_ps='.0005'))),
        ('nested-manifest-resealed',lambda r,m,b:(b/'attempts/0001/manifest.json').write_text('new nested bytes\n')),
        ('nested-extra-directory',lambda r,m,b:(b/'unexpected').mkdir()),
        ('same-step-time-shift',lambda r,m,b:(p.edit(b/'samples/worker-000.json',lambda d:d.update(time_ps=.0105)),
                                              p.edit(b/'final-state-reports.json',lambda d:d['workers'][0].update(time_ps=.0105)))),
    ]
    for name, action in cases:
        p.inert(name, action)
    py=random.Random(31); nu=np.random.RandomState(33)
    py.gauss(0,1); nu.normal()
    document=json.loads(json.dumps(p.c._rng_document(py,nu)))
    p.j._validate_rng_document(document); p2,n2=p.c._rng_from_document(document)
    assert [py.gauss(0,1) for _ in range(5)]==[p2.gauss(0,1) for _ in range(5)]
    assert nu.normal(size=9).tolist()==n2.normal(size=9).tolist()
    record('both-finite-gaussian-cache-roundtrip',python_cache=document['python'][2],numpy_cache=document['numpy'][4])


def arithmetic():
    controls=[]
    for origin,n in ((0.,100000),(0.,999999),(10.,999999),(123.25,100000),(1e6,100000)):
        time_ps=origin; dt=.0005
        for _ in range(n): time_ps+=dt
        p.j._validate_expected_clock(17+n,time_ps,{'step':17,'time_ps':origin},n,dt)
        controls.append(dict(origin_ps=origin,steps=n,repeated_time_ps=time_ps,
                             product_time_ps=origin+n*dt,error_ps=abs(time_ps-(origin+n*dt))))
    record('gamma-n-valid-repeated-additions',controls=controls)
    failures=[]
    for step,time_ps in ((18,.0105),(19,.0005),(17,0.)):
        error=p.error_call(lambda:p.j._validate_expected_clock(step,time_ps,{'step':17,'time_ps':0.},1,.0005))
        assert error; failures.append(dict(step=step,time_ps=time_ps,error=error))
    record('gamma-n-normal-invalid-increments',controls=failures)
    u=sys.float_info.epsilon/2; n=1; t0=1e308; t=0.; dt=.0005
    gamma=(n*u)/(1-n*u); observed=t-t0; expected=n*dt
    scale=abs(t0)+n*abs(dt)
    bound=gamma*scale+(u/(1-u))*(n*abs(dt)+abs(t)+abs(t0)+abs(expected)+abs(observed))
    error=p.error_call(lambda:p.j._validate_expected_clock(1,t,{'step':0,'time_ps':t0},n,dt))
    record('gamma-n-overflow-helper-characterization',status='CHARACTERIZATION',
           origin_ps=t0,actual_time_ps=t,steps=n,timestep_ps=dt,error=error,
           computed_bound_finite=math.isfinite(bound),computed_bound=str(bound),
           claimed_product_finding=False)


def transactions():
    reference=p.ART/'reference'
    p.shutil.copytree(p.ART/'prefix',reference)
    p.c.resume_multistate_exchange(reference,trusted=True)
    reference_tree=p.tree(reference/'boundaries/000001')
    faults=('destination-parent','source-parent','records','observations','summary',
            'secondary-checkpoint-open','secondary-portable-open','secondary-map0-open','secondary-map1-open')
    for fault in faults:
        run,m,b=p.clone('transaction-'+fault); target=run/'boundaries/000001'
        original_boundary=p.tree(b); events=[]; post_evals=[]; post_force_states=[]
        published=[False]; injected=[False]
        old_fsync=os.fsync; old_rename=os.rename; old_evaluate=p.atom.WorkerRun.evaluate
        old_open=Path.open; old_write=p.c.write_json; old_get_state=mm.Context.getState
        publication_inventory={}
        def rename(source,destination):
            if Path(destination)==target:
                source=Path(source)
                publication_inventory['files']={str(q) for q in source.rglob('*') if q.is_file()}
                publication_inventory['dirs']={str(q) for q in source.rglob('*') if q.is_dir()}|{str(source)}
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
        def get_state(self,*args,**kwargs):
            if published[0] and (kwargs.get('getEnergy') or kwargs.get('getForces')):
                post_force_states.append(dict(args=str(args),kwargs=str(kwargs)))
            return old_get_state(self,*args,**kwargs)
        def write(path,document):
            if fault in ('observations','summary') and Path(path)==run/(fault+'.json'):
                raise OSError('independent '+fault+' actual writer failure')
            return old_write(path,document)
        failed_capture={'secondary-checkpoint-open':'checkpoint.chk',
                        'secondary-portable-open':'state.xml',
                        'secondary-map0-open':'map0-state.xml',
                        'secondary-map1-open':'map1-state.xml'}.get(fault)
        def open_file(self,*args,**kwargs):
            mode=args[0] if args else kwargs.get('mode','r')
            if published[0] and fault=='records' and self==run/'records.json' and 'w' in mode:
                raise OSError('independent records actual open EIO')
            if (failed_capture and self.name==failed_capture and self.parent.name=='worker-001'
                    and self.parent.parent.name.startswith('postcommit-') and 'w' in mode):
                raise OSError('secondary '+failed_capture+' actual open ENOSPC')
            return old_open(self,*args,**kwargs)
        with ExitStack() as stack:
            stack.enter_context(patch.object(os,'fsync',fsync)); stack.enter_context(patch.object(os,'rename',rename))
            stack.enter_context(patch.object(p.atom.WorkerRun,'evaluate',evaluate))
            stack.enter_context(patch.object(mm.Context,'getState',get_state))
            stack.enter_context(patch.object(p.c,'write_json',write)); stack.enter_context(patch.object(Path,'open',open_file))
            if failed_capture:
                stack.enter_context(patch.object(p.c,'to_json',lambda *a:(_ for _ in ()).throw(OSError('independent records primary failure'))))
            error=p.error_call(lambda:p.c.resume_multistate_exchange(run,trusted=True))
        assert error and not post_evals and not post_force_states and len(p.j.read_multistate_boundaries(run))==2
        assert p.tree(b)==original_boundary and p.tree(target)==reference_tree and not (run/'pending').exists()
        publication=next(i for i,event in enumerate(events) if event['op']=='rename' and event['target']==str(target))
        synced={event['path'] for event in events[:publication] if event['op']=='fsync'}
        assert publication_inventory['files']<=synced and publication_inventory['dirs']<=synced
        parents={event['path'] for event in events[publication+1:] if event['op']=='fsync'}
        assert {str(run),str(run/'boundaries')}<=parents
        if fault.endswith('parent'): assert injected[0]
        archives=list((run/'failures').glob('postcommit-*')); assert len(archives)==1
        archive=archives[0]; primary=p.read_json(archive/'error.json')
        assert primary['message'] in error and primary['commit_authoritative']
        captures=[]
        for w in range(3):
            folder=archive/f'worker-{w:03d}'; missing=[]
            for name in ('state.xml','checkpoint.chk','map0-state.xml','map1-state.xml','error.json'):
                if w==1 and name==failed_capture:
                    assert not (folder/name).exists(); missing.append(name); continue
                assert (folder/name).is_file()
            portable=(target/'workers'/f'worker-{w:03d}-state.xml').read_bytes()
            if (folder/'state.xml').exists(): assert (folder/'state.xml').read_bytes()==portable
            if (folder/'checkpoint.chk').exists():
                assert (folder/'checkpoint.chk').read_bytes()==(target/'workers'/f'worker-{w:03d}.chk').read_bytes()
            from atm_mlmm.schema import from_json
            bundle=from_json((run/'worker/bundle.json').read_text())
            for label,displacement in (('map0',bundle.transfer.displacement0_nm),('map1',bundle.transfer.displacement1_nm)):
                if (folder/(label+'-state.xml')).exists():
                    assert (folder/(label+'-state.xml')).read_text()==p.c._mapped_state_xml(portable.decode(),displacement)
            diagnostics=p.read_json(folder/'error.json')
            assert diagnostics['message']==primary['message']
            captures.append(dict(worker=w,missing=missing,archive_errors=diagnostics['archive_errors']))
        assert bool(primary['archive_errors'])==bool(failed_capture)
        p.c.resume_multistate_exchange(run,trusted=True)
        assert p.tree(target)==reference_tree and len(p.read_json(run/'observations.json'))==6
        for name in ('records.json','observations.json'):
            assert (run/name).read_bytes()==(reference/name).read_bytes()
        summary=p.read_json(run/'summary.json'); expected=p.read_json(reference/'summary.json')
        for document in (summary,expected):
            document.pop('elapsed_execution_seconds'); document.pop('peak_process_rss_bytes')
        assert summary==expected
        record('postcommit-'+fault,error=error,primary=primary,captures=captures,
               no_energy_force_reentry=True,authoritative_and_replayed_bytes_equal=True,
               all_publication_files_and_nested_dirs_synced_before_rename=True,
               both_publication_parents_attempted_after_rename=True,events=events,power_loss_test=False)


def main():
    assert p.ART.is_dir() and not (p.ART/'reference').exists()
    remaining_inert(); arithmetic(); p.runtime_controls(); transactions(); p.rollback_controls()
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==ORIGINAL_HASH
    failures=sum(r['status']=='VIOLATION' for r in p.RESULTS)
    print(json.dumps({'probe_count':len(p.RESULTS),'violation_count':failures,'exit_status':int(bool(failures))}))
    return int(bool(failures))


if __name__=='__main__': sys.exit(main())
