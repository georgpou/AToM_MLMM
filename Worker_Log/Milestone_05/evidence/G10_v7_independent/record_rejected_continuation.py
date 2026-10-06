"""Complement all-accepted saved records without repeating their arithmetic.

The first driver completed three record controls then correctly detected a
coverage gap: none of those natural histories rejected. Preserve that script,
results and raw exit; only this new tiny public run forces a valid high draw.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from unittest.mock import patch

import repair_probe as p
from atom_openmm import gibbs_sampling

HERE=p.HERE
source=HERE/'record_controls_probe.py'
namespace={'__name__':'record_control_definitions','__file__':str(source)}
syntax=ast.parse(source.read_text())
definitions=[node for node in syntax.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
exec(compile(ast.Module(body=definitions,type_ignores=[]),str(source),'exec'),namespace)
RESULTS=json.loads((HERE/'record-controls-results.json').read_text())['probes']
namespace.update(HERE=HERE,RESULTS=RESULTS)


def record(name,**details):
    RESULTS.append(dict(name=name,status='PASS',**details))
    result=dict(probes=RESULTS,original_accepted_record_controls_reused=3,
                original_script_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                original_exit_classification='coverage assertion: 12 accepted, zero rejected; no product failure',
                finished_utc=datetime.now(timezone.utc).isoformat(),exit_status=0)
    (HERE/'record-continuation-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(RESULTS[-1],sort_keys=True),flush=True)


namespace['record']=record
run=p.ART/'records-forced-rejection'; draw=1.0-1e-12
with patch.object(gibbs_sampling,'_random',lambda:draw):
    p.c.run_multistate_exchange(p.ART/'prepared',run,state_ids=('first','middle','third'),
        state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
decision=p.read_json(run/'boundaries/000000/attempts/0000/decision.json')
assert decision['exponent']>0 and draw>math.exp(-decision['exponent']) and decision['accepted'] is False
outcomes=namespace['records'](run)
assert outcomes[False]>0
record('actual-pinned-positive-exponent-rejection',draw=draw,exponent=decision['exponent'],
       independently_computed_threshold=math.exp(-decision['exponent']),accepted=decision['accepted'],
       actual_adapter_and_metropolis=True,new_preparation_frames=0,analytic_steps_per_worker=1)
namespace['symlink']()
print(json.dumps({'probes':len(RESULTS),'prior_accepted_attempts':12,
                  'additional_accepted_attempts':outcomes[True],'additional_rejected_attempts':outcomes[False],
                  'exit_status':0}))
