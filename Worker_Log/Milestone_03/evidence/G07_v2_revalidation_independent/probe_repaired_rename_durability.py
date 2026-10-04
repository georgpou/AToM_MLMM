"""Check both recovery paths after rename loss on isolated actual-data copies."""
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import os
import shutil
import sys

E = Path(__file__).resolve().parent
REPO = E.parents[3]
sys.path[:0] = [str(E/'source-durable/tools'), str(REPO/'src')]
import resume_joint_quantum as joint

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

ACTUAL = REPO/'Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1'
original = ACTUAL/'jobs'/joint.PILOT/'attempt-0001'
original_hashes = {p.name:sha(p) for p in original.iterdir() if p.is_file()}
progress_sha = sha(ACTUAL/'progress.json')
plan = REPO/'fixtures/chemical_reference_v3'
matrix_path = REPO/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
matrix = json.loads(matrix_path.read_text())
reference = '/workspace/atom-mlmm-g07/reference-env/bin/python'
launches = 0

def forbidden(*args, **kwargs):
    global launches
    launches += 1
    raise AssertionError('No worker launch is authorized in this independent check')

joint.recovery.subprocess.Popen = forbidden

class Crash(Exception):
    pass

results = {}
for corrective in (True, False):
    folder = E/('durable-rename-corrective-case' if corrective else 'durable-rename-ordinary-case')
    folder.mkdir()
    output = folder/'output'
    source = output/'jobs'/joint.PILOT/'attempt-0001'
    shutil.copytree(original, source)
    (output/'records').mkdir()
    approval = json.loads((REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json').read_text())
    approval['attempt_path'] = str(output)
    authorization = folder/'authorization.json'
    authorization.write_text(json.dumps(approval, indent=2)+'\n')
    joint.APPROVAL_PATH = authorization
    joint.APPROVAL_SHA256 = sha(authorization)
    state = json.loads((ACTUAL/'progress.json').read_text())
    state['identity']['approval_sha256'] = sha(authorization)
    (output/'progress.json').write_text(json.dumps(state, indent=2)+'\n')
    staging = source.parent/'.revalidation-staging-v1'
    target = source.parent/'attempt-0002'
    real_rename = os.rename

    def interrupted_rename(a, b):
        answer = real_rename(a, b)
        if Path(a) == staging:
            raise Crash('after directory rename before parent-directory fsync')
        return answer

    with patch.object(os, 'rename', interrupted_rename):
        try:
            joint.revalidate_pilot(output, plan, approval, matrix, reference)
        except Crash:
            pass
    assert target.exists() and not staging.exists()
    real_fsync = os.fsync
    real_dump = joint.recovery.atomic_dump
    events = []

    def trace(fd):
        path = Path(os.readlink('/proc/self/fd/'+str(fd)))
        answer = real_fsync(fd)
        events.append({'fsync':str(path), 'directory':path.is_dir()})
        return answer

    def checkpoint(path, data):
        if Path(path) == output/'progress.json' and data['record_hashes']:
            events.append({'checkpoint_with_record':joint.PILOT,
                           'parent_synced_before':any(e.get('fsync') == str(source.parent) for e in events)})
        return real_dump(path, data)

    args = Namespace(plan_root=str(plan), approval=str(authorization), matrix=str(matrix_path),
        output=str(output), reference_python=reference, check_resume=False, memory_gib=3.,
        wall_limit_seconds=None, continue_batch=False, pilot_assessment=None, revalidate_pilot=corrective)
    with patch.object(os, 'fsync', trace), patch.object(joint.recovery, 'atomic_dump', checkpoint):
        code = joint.run(args)
    checkpoints = [event for event in events if 'checkpoint_with_record' in event]
    after = json.loads((output/'progress.json').read_text())
    result = dict(source_sha256=sha(E/'source-durable/tools/resume_joint_quantum.py'),
        corrective_option=corrective, injected_after_rename=True, exit=code,
        admitted_records=len(after['record_hashes']),
        parent_synced_before_admitted_checkpoint=checkpoints[0]['parent_synced_before'],
        parent_synced_at_all=any(e.get('fsync') == str(source.parent) for e in events),
        stopped_at_pilot=after['sessions'][-1]['stop_reason'] == 'pilot_assessment_pending',
        cumulative_debit_preserved=after['wall_seconds_debited'] >= 2325.6432226409997,
        events=events)
    (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    results['corrective' if corrective else 'ordinary'] = {k:v for k,v in result.items() if k != 'events'}
    assert code == 1 and result['admitted_records'] == 1
    assert result['parent_synced_before_admitted_checkpoint'] and result['parent_synced_at_all']
    assert result['stopped_at_pilot'] and result['cumulative_debit_preserved']

results['worker_launch_calls'] = launches
results['actual_original_unchanged'] = original_hashes == {p.name:sha(p) for p in original.iterdir() if p.is_file()}
results['actual_progress_unchanged'] = progress_sha == sha(ACTUAL/'progress.json')
(E/'rename-durability-repaired-results.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2))
assert not launches and results['actual_original_unchanged'] and results['actual_progress_unchanged']
