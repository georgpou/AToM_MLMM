"""Publicly reachable finite-clock domain and energy-consistent backward clock.

Reuse the tiny already prepared analytic bundle, no preparation or molecular MD.
Only portable clock bytes/seals are changed; all source and scientific bytes stay
current. Full public run/resume distinguishes clock admission from helper misuse.
"""
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET

import openmm as mm
from openmm import unit

import repair_probe as p

HERE=p.HERE
RESULTS=[]


def save(name,status='PASS',**details):
    RESULTS.append(dict(name=name,status=status,**details))
    result=dict(probes=RESULTS,pass_count=sum(r['status']=='PASS' for r in RESULTS),
                violation_count=sum(r['status']=='VIOLATION' for r in RESULTS),
                finished_utc=datetime.now(timezone.utc).isoformat())
    (HERE/'clock-domain-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(RESULTS[-1],sort_keys=True),flush=True)


def prepared_with_clock(label,time_ps):
    prepared=p.ART/('clock-public-'+label+'-prepared')
    shutil.copytree(p.ART/'prepared',prepared)
    state=prepared/'worker/handover_0.xml'
    document=ET.fromstring(state.read_text()); document.set('time',repr(time_ps))
    state.write_text(ET.tostring(document,encoding='unicode'))
    p.edit(prepared/'worker/manifest.json',lambda d:d['files'].update({'handover_0.xml':p.j.sha(state)}))
    p.edit(prepared/'metadata.json',lambda d:d.update(worker_manifest_sha256=p.j.sha(prepared/'worker/manifest.json')))
    (prepared/'metadata.sha256').write_text(p.j.sha(prepared/'metadata.json')+'\n')
    return prepared


def public_control(label,time_ps):
    prepared=prepared_with_clock(label,time_ps); run=p.ART/('clock-public-'+label+'-run')
    summary=p.c.run_multistate_exchange(prepared,run,state_ids=('first','middle','third'),
        state_pairs=((0,1),(1,2)),boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    rows=p.j.read_multistate_boundaries(run)
    initial=p.read_json(run/'initial/final-state-reports.json')['workers']
    assert len(rows)==1 and summary['samples']==3
    actual=[r['time_ps'] for r in initial]; assert actual==[time_ps]*3
    final=[s['time_ps'] for s in rows[0]['samples']]
    assert final==[time_ps+.0005]*3
    save('public-'+label+'-origin-control',initial_times_ps=actual,final_times_ps=final,
         initial_steps=[r['step'] for r in initial],final_steps=[s['step'] for s in rows[0]['samples']],
         public_api='run_multistate_exchange',steps_per_worker=1,prepared_frames_added=0,
         source_substitution=False,negative_time_forbidden_by_contract=False if time_ps<0 else None,
         unsupported_absolute_clock_claim=False)
    return run


def change_cached_time(worker,checkpoint,portable,state_id,time_ps):
    worker.restore_checkpoint(checkpoint.read_bytes(),state_id)
    before=p._snapshot(worker); step=worker.evaluator.context.getStepCount()
    worker.evaluator.context.setTime(time_ps*unit.picosecond)
    assert before==p._snapshot(worker) and step==worker.evaluator.context.getStepCount()
    checkpoint.write_bytes(worker.evaluator.context.createCheckpoint())
    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
    portable.write_text(mm.XmlSerializer.serialize(saved))
    assert saved.getTime().value_in_unit(unit.picosecond)==time_ps
    return dict(step=step,time_ps=saved.getTime().value_in_unit(unit.picosecond),
                snapshot_unchanged=True,portable_step=saved.getStepCount())


def backward_clock(valid):
    run=p.ART/'clock-public-large-backward'; shutil.copytree(valid,run)
    metadata=p.read_json(run/'metadata.json'); boundary=run/'boundaries/000000'
    row=p.j.read_multistate_boundaries(run)[0]
    initial=p.read_json(run/'initial/final-state-reports.json')['workers'][0]
    sample_path=boundary/'samples/worker-000.json'; sample=p.read_json(sample_path)
    report_path=boundary/'final-state-reports.json'; report=p.read_json(report_path)['workers'][0]
    old_sample=dict(sample); old_report=dict(report)
    final_state=metadata['state_ids'][row['walker_to_state_final'][0]]
    with p.atom.load_worker_run(run/'worker',metadata['worker_manifest_sha256'],trusted=True,
                               integrator_seed=metadata['integrator_seed_base']) as worker:
        clocks={}
        clocks['sample']=change_cached_time(worker,boundary/'samples/worker-000.chk',
            boundary/'samples/worker-000-state.xml',sample['state_id'],.0005)
        clocks['final']=change_cached_time(worker,boundary/'workers/worker-000.chk',
            boundary/'workers/worker-000-state.xml',final_state,.0005)
    p.edit(sample_path,lambda d:d.update(time_ps=.0005))
    p.edit(report_path,lambda d:d['workers'][0].update(time_ps=.0005))
    changed_sample=p.read_json(sample_path); changed_report=p.read_json(report_path)['workers'][0]
    for document in (old_sample,changed_sample,old_report,changed_report): document.pop('time_ps')
    assert old_sample==changed_sample and old_report==changed_report
    p.j.seal_tree(boundary,index=0)
    before=p.tree(run); inert_error=p.error_call(lambda:p.j.read_multistate_boundaries(run))
    assert inert_error is None and before==p.tree(run)
    loaded=[]; evaluations=[]; steps=[]; commits=[]
    old_load=p.atom.load_worker_run; old_evaluate=p.atom.WorkerRun.evaluate
    old_step=mm.LangevinMiddleIntegrator.step; old_publish=p.c._publish_multistate_boundary
    def load(*args,**kwargs):
        loaded.append(kwargs.get('integrator_seed')); return old_load(*args,**kwargs)
    def evaluate(self,*args,**kwargs):
        evaluations.append(dict(seed=self.integrator_seed,step=self.evaluator.context.getStepCount(),
                                time_ps=self.evaluator.context.getState().getTime().value_in_unit(unit.picosecond)))
        return old_evaluate(self,*args,**kwargs)
    def step(self,count):
        steps.append(count); return old_step(self,count)
    def publish(pending,target,index):
        result=old_publish(pending,target,index); commits.append(index); return result
    with patch.object(p.atom,'load_worker_run',load),patch.object(p.atom.WorkerRun,'evaluate',evaluate), \
            patch.object(mm.LangevinMiddleIntegrator,'step',step),patch.object(p.c,'_publish_multistate_boundary',publish):
        error=p.error_call(lambda:p.c.resume_multistate_exchange(run,trusted=True))
    final_rows=p.j.read_multistate_boundaries(run)
    origin=initial['time_ps']; current=.0005; observed=current-origin; expected=.0005
    u=sys.float_info.epsilon/2; gamma=u/(1-u)
    computed=gamma*(abs(origin)+expected)+gamma*(expected+abs(current)+abs(origin)+expected+abs(observed))
    finite_reordered=math.fsum((gamma*abs(origin),gamma*expected,gamma*expected,
                              gamma*abs(current),gamma*abs(origin),gamma*expected,gamma*abs(observed)))
    with localcontext() as context:
        context.prec=90
        du=Decimal.from_float(u); dg=du/(1-du)
        dorigin=Decimal.from_float(origin); dcurrent=Decimal.from_float(current); ddt=Decimal.from_float(expected)
        ddelta=Decimal.from_float(observed)
        exact_bound=dg*(abs(dorigin)+ddt)+dg*(ddt+abs(dcurrent)+abs(dorigin)+ddt+abs(ddelta))
        true_gap=abs((dcurrent-dorigin)-ddt)
    violated=(error is None and bool(evaluations) and bool(steps) and commits==[1] and len(final_rows)==2)
    save('public-finite-origin-backward-clock','VIOLATION' if violated else 'PASS',
         inert_reader_error=inert_error,resume_error=error,source_substitution=False,
         initial_clock=initial|{'raw':'UNCHANGED','total':'UNCHANGED'},current_clock=clocks,
         sample_and_final_json_only_time_changed=True,all_energy_force_snapshot_fields_unchanged=True,
         origin_ps=origin,actual_sample_time_ps=current,observed_delta_ps=observed,expected_delta_ps=expected,
         original_binary64_bound=str(computed),original_bound_finite=math.isfinite(computed),
         independently_reordered_finite_bound_ps=finite_reordered,
         decimal_90_digit_bound_ps=str(exact_bound),decimal_gap_ps=str(true_gap),
         delta_exceeds_finite_roundoff_bound=true_gap>exact_bound,loader_seeds=loaded,
         evaluations=evaluations,integration_step_calls=steps,new_committed_boundaries=commits,
         authoritative_boundary_count=len(final_rows),final_worker0_time_ps=final_rows[-1]['samples'][0]['time_ps'],
         artifacts=str(run),public_api='read_multistate_boundaries + resume_multistate_exchange')


def main():
    public_control('negative',-1.)
    large=public_control('large',1e308)
    backward_clock(large)
    violations=sum(r['status']=='VIOLATION' for r in RESULTS)
    print(json.dumps({'probes':len(RESULTS),'violations':violations,'exit_status':int(bool(violations))}))
    return int(bool(violations))


if __name__=='__main__': sys.exit(main())
