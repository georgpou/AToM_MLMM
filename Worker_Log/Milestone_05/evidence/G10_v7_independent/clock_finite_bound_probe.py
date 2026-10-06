"""Check the concrete positive-addition invariant with a finite clock bound.

Independent of the overflow case: this determines whether repairing overflow
alone would satisfy the already-required backward-clock rejection.
"""
import ast
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

import openmm as mm
from openmm import unit
import repair_probe as p

HERE=p.HERE
source=HERE/'clock_domain_probe.py'
syntax=ast.parse(source.read_text())
namespace={'__name__':'clock_domain_definitions','__file__':str(source)}
definitions=[node for node in syntax.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
exec(compile(ast.Module(body=definitions,type_ignores=[]),str(source),'exec'),namespace)
RESULTS=[]


def save(name,status='PASS',**details):
    RESULTS.append(dict(name=name,status=status,**details))
    result=dict(probes=RESULTS,finished_utc=datetime.now(timezone.utc).isoformat(),
                violation_count=sum(r['status']=='VIOLATION' for r in RESULTS))
    (HERE/'clock-finite-bound-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(RESULTS[-1],sort_keys=True),flush=True)


namespace.update(HERE=HERE,RESULTS=RESULTS,save=save)
origin=1e14; current=math.nextafter(origin,-math.inf); dt=.0005
valid=namespace['public_control']('large-finite-bound',origin)
run=p.ART/'clock-public-finite-bound-backward'; shutil.copytree(valid,run)
metadata=p.read_json(run/'metadata.json'); boundary=run/'boundaries/000000'
row=p.j.read_multistate_boundaries(run)[0]; sample=p.read_json(boundary/'samples/worker-000.json')
final_state=metadata['state_ids'][row['walker_to_state_final'][0]]
with p.atom.load_worker_run(run/'worker',metadata['worker_manifest_sha256'],trusted=True,
                           integrator_seed=metadata['integrator_seed_base']) as worker:
    sample_clock=namespace['change_cached_time'](worker,boundary/'samples/worker-000.chk',
        boundary/'samples/worker-000-state.xml',sample['state_id'],current)
    final_clock=namespace['change_cached_time'](worker,boundary/'workers/worker-000.chk',
        boundary/'workers/worker-000-state.xml',final_state,current)
before_sample=p.read_json(boundary/'samples/worker-000.json')
before_report=p.read_json(boundary/'final-state-reports.json')['workers'][0]
p.edit(boundary/'samples/worker-000.json',lambda d:d.update(time_ps=current))
p.edit(boundary/'final-state-reports.json',lambda d:d['workers'][0].update(time_ps=current))
after_sample=p.read_json(boundary/'samples/worker-000.json')
after_report=p.read_json(boundary/'final-state-reports.json')['workers'][0]
for document in (before_sample,before_report,after_sample,after_report): document.pop('time_ps')
assert before_sample==after_sample and before_report==after_report
p.j.seal_tree(boundary,index=0)
inert_error=p.error_call(lambda:p.j.read_multistate_boundaries(run)); assert inert_error is None
loads=[]; evaluations=[]; steps=[]
old_load=p.atom.load_worker_run; old_evaluate=p.atom.WorkerRun.evaluate; old_step=mm.LangevinMiddleIntegrator.step
def load(*args,**kwargs):
    loads.append(kwargs.get('integrator_seed')); return old_load(*args,**kwargs)
def evaluate(self,*args,**kwargs):
    evaluations.append(self.integrator_seed); return old_evaluate(self,*args,**kwargs)
def step(self,count):
    steps.append(count); return old_step(self,count)
with patch.object(p.atom,'load_worker_run',load),patch.object(p.atom.WorkerRun,'evaluate',evaluate), \
        patch.object(mm.LangevinMiddleIntegrator,'step',step):
    error=p.error_call(lambda:p.c.resume_multistate_exchange(run,trusted=True))
rows=p.j.read_multistate_boundaries(run)
u=sys.float_info.epsilon/2; gamma=u/(1-u); observed=current-origin
bound=gamma*(abs(origin)+dt)+gamma*(dt+abs(current)+abs(origin)+dt+abs(observed))
assert math.isfinite(bound) and current<origin and origin+dt==origin
violated=error is None and len(rows)==2 and bool(evaluations) and steps==[1,1,1]
save('public-finite-bound-backward-clock','VIOLATION' if violated else 'PASS',
     origin_ps=origin,actual_sample_time_ps=current,observed_delta_ps=observed,
     expected_delta_ps=dt,computed_bound_ps=bound,computed_bound_finite=True,
     numerical_residual_within_bound=abs(observed-dt)<=bound,
     actual_repeated_addition_time_ps=origin+dt,positive_binary64_addition_cannot_decrease=True,
     sample_clock=sample_clock,final_clock=final_clock,
     snapshot_energy_force_and_all_other_json_fields_unchanged=True,
     inert_reader_error=inert_error,resume_error=error,loader_seeds=loads,
     evaluation_count=len(evaluations),integration_step_calls=steps,
     authoritative_boundary_count=len(rows),new_commit_index=rows[-1]['boundary_index'],
     final_worker0_time_ps=rows[-1]['samples'][0]['time_ps'],artifacts=str(run),source_substitution=False)
violations=sum(r['status']=='VIOLATION' for r in RESULTS)
print(json.dumps({'probes':len(RESULTS),'violations':violations,'exit_status':int(bool(violations))}))
sys.exit(int(bool(violations)))
