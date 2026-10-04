"""G07 queue/authorization and synthetic recovery; never chemical evidence."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / 'fixtures/chemical_reference_v3'
AUTH = REPO / 'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
MATRIX = REPO / 'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
PROGRAM = REPO / 'tools/resume_joint_quantum.py'


@pytest.fixture(autouse=True)
def source_imports(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', str(REPO/'src'))


def command(output, extra=(), root=PLAN, auth=AUTH, matrix=MATRIX):
    bound = output.parent/'bound-authorization.json'
    approval = json.loads(Path(auth).read_text()); approval['attempt_path'] = str(output.resolve())
    bound.write_text(json.dumps(approval, indent=2)+'\n')
    return [sys.executable, str(PROGRAM), '--plan-root', str(root), '--approval', str(bound),
            '--matrix', str(matrix), '--output', str(output), *extra]


def test_only_frozen_thirty_jobs_with_pilot_first_and_no_g05_budget(tmp_path):
    result = subprocess.run(command(tmp_path/'output', ['--check-resume']), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['expected_count'] == 30
    assert data['remaining'][0] == 'ethanol-methanol-d3-r0--full-parent'
    assert len(data['remaining']) == 30
    assert data['remaining_wall_seconds'] == 86400
    assert not (tmp_path/'output').exists()


@pytest.mark.parametrize('field', ['matrix_sha256', 'user_agreed', 'reference_lock_sha256', 'pilot_job'])
def test_tampered_authorization_rejects_before_launch(tmp_path, field):
    approval = json.loads(AUTH.read_text())
    approval[field] = False if field == 'user_agreed' else 'invalid'
    path = tmp_path/'authorization.json'; path.write_text(json.dumps(approval))
    result = subprocess.run(command(tmp_path/'output', ['--check-resume'], auth=path), capture_output=True, text=True)
    assert result.returncode == 2
    assert not (tmp_path/'output').exists()


def test_matrix_tamper_rejects_even_with_rebound_authorization(tmp_path):
    import hashlib
    matrix = json.loads(MATRIX.read_text()); matrix['new_jobs'][0]['positions_angstrom'][0][0] += .1
    path = tmp_path/'matrix.json'; path.write_text(json.dumps(matrix))
    approval = json.loads(AUTH.read_text()); approval['matrix_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    auth = tmp_path/'authorization.json'; auth.write_text(json.dumps(approval))
    result = subprocess.run(command(tmp_path/'output', ['--check-resume'], auth=auth, matrix=path), capture_output=True, text=True)
    assert result.returncode == 2
    assert 'frozen' in result.stderr.lower()


def test_stricter_resource_and_pilot_policy(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO/'tools'))
    import resume_joint_quantum as joint
    policy = joint.execution_policy(json.loads(AUTH.read_text()), continuation=False)
    assert policy['rss_max_bytes'] <= 6*2**30
    assert policy['disk_min_bytes'] == 5*2**30
    assert policy['pilot_wall_seconds'] == 3600
    assert policy['stop_after_job'] == 'ethanol-methanol-d3-r0--full-parent'


@pytest.fixture
def synthetic(tmp_path):
    """Real frozen queue; substitute only the separate executable boundary."""
    executable = tmp_path/'reference/bin/python'; executable.parent.mkdir(parents=True)
    meta = executable.parents[1]/'conda-meta'; meta.mkdir()
    for i, line in enumerate((PLAN/'reference-explicit.lock').read_text().splitlines()):
        if line.startswith('https://'):
            url, sha = line.rsplit('#',1)
            (meta/f'{i}.json').write_text(json.dumps(dict(url=url, sha256=sha)))
    executable.write_text('#!'+sys.executable+'\n'+'''
import json,os,sys,time
from pathlib import Path
order=json.loads(Path(sys.argv[-1]).read_text());d=order['structure'];out=Path(order['output'])
mode=os.environ.get('JOINT_QUANTUM_TEST_MODE','')
if mode=='wait':time.sleep(20)
r=dict(status='computed',name=order['job_name'],source_input_sha256=order['source_input_sha256'],
method='wb97m-d3bj/def2-tzvppd',psi4_version='1.10.2',formal_charge=0,multiplicity=1,
positions_angstrom=d['positions_angstrom'],atomic_numbers=d['atomic_numbers'],
energy_hartree=-1.,gradient_hartree_bohr=[[0.,0.,0.] for _ in d['atomic_numbers']],
quantum_energy_variables={'DISPERSION CORRECTION ENERGY':-.001,'DFT VV10 ENERGY':0.},
basis_file_sha256=order['basis_file_sha256'],settings=order['settings'],network_denied=True,
wall_seconds=.001,threads=2,memory=order['runtime_memory'])
out.write_text(json.dumps(r));out.with_suffix('.psi4.txt').write_text('SCF has converged.\\n')
if mode=='computed_fail':sys.exit(23)
''')
    executable.chmod(0o755)
    return executable, tmp_path/'output'


def run_fake(synthetic, mode='', extra=()):
    exe, output = synthetic
    return subprocess.run(command(output, ['--reference-python', str(exe), *extra]),
        env={**os.environ,'JOINT_QUANTUM_TEST_MODE':mode},capture_output=True,text=True,timeout=50)


def test_pilot_completion_stops_for_assessment_and_durable_receipt(synthetic):
    result = run_fake(synthetic)
    assert result.returncode == 1, result.stderr
    output = synthetic[1]; state = json.loads((output/'progress.json').read_text())
    assert len(state['record_hashes']) == 1
    assert state['sessions'][-1]['stop_reason'] == 'pilot_assessment_pending'
    assert not state['ready_for_comparison']
    receipt = next(output.glob('jobs/*/attempt-*/receipt.json'))
    assert json.loads(receipt.read_text())['group_cleanup_verified']
    assert not list(output.glob('jobs/*/attempt-*/scratch'))
    samples = [json.loads(x) for x in next(output.glob('jobs/*/attempt-*/resources.jsonl')).read_text().splitlines()]
    assert all(x['job_name'] == 'ethanol-methanol-d3-r0--full-parent' and 'elapsed_seconds' in x for x in samples)


def test_failed_pilot_receipt_is_never_promoted_and_retry_keeps_budget(synthetic):
    first = run_fake(synthetic, 'computed_fail'); assert first.returncode == 1, first.stderr
    output = synthetic[1]; state = json.loads((output/'progress.json').read_text())
    assert not state['record_hashes']
    charged = state['wall_seconds_debited']
    receipt = next(output.glob('jobs/*/attempt-*/receipt.json')); original = receipt.read_bytes()
    second = run_fake(synthetic); assert second.returncode == 1, second.stderr
    state = json.loads((output/'progress.json').read_text())
    assert len(state['record_hashes']) == 1 and state['wall_seconds_debited'] > charged
    assert receipt.read_bytes() == original
    assert len(list(output.glob('jobs/*/attempt-*'))) == 2


def test_timeout_kills_worker_and_charges_resume(synthetic):
    first = run_fake(synthetic,'wait', ['--wall-limit-seconds','1.5'])
    assert first.returncode == 1, first.stderr
    output = synthetic[1]; state = json.loads((output/'progress.json').read_text())
    assert not state['record_hashes'] and state['wall_seconds_debited'] >= 1.5
    second = run_fake(synthetic,'', ['--wall-limit-seconds','1.5'])
    assert second.returncode == 1, second.stderr
    assert len(list(output.glob('jobs/*/attempt-*'))) == 1


def test_resume_requires_pilot_assessment_and_rejects_changed_receipt(synthetic, tmp_path):
    assert run_fake(synthetic).returncode == 1
    result = run_fake(synthetic, extra=['--continue-batch'])
    assert result.returncode == 2 and 'assessment' in result.stderr.lower()


def test_concurrent_queue_lease_blocks_launch(synthetic):
    import fcntl
    exe, output = synthetic
    command(output)  # Bind synthetic authorization, without a launch.
    with (output.parent/'queue-lease.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = run_fake(synthetic)
    assert result.returncode == 2 and 'another coordinator' in result.stderr
    assert not (output/'progress.json').exists()


@pytest.mark.parametrize('guard', ['rss', 'disk', 'oom'])
def test_g07_guards_stop_safely_before_promoting(monkeypatch, synthetic, guard):
    from argparse import Namespace
    monkeypatch.syspath_prepend(str(REPO/'tools'))
    import resume_joint_quantum as joint
    exe, output = synthetic
    cmd = command(output, ['--reference-python',str(exe)])
    args = Namespace(plan_root=str(PLAN), approval=cmd[cmd.index('--approval')+1],
        matrix=str(MATRIX),output=str(output), reference_python=str(exe),
        check_resume=False,memory_gib=3.,wall_limit_seconds=None,
        continue_batch=False,pilot_assessment=None)
    actual = joint.recovery.measurements
    def measured(pid=None):
        data = actual(pid)
        if guard == 'disk':data['disk_free_bytes'] = 5*2**30-1
        if pid is not None and guard == 'rss':data['VmRSS'] = 6*2**30+1
        if guard == 'oom':data['memory.events'] = 'oom 1\noom_kill 0\n' if pid else 'oom 0\noom_kill 0\n'
        return data
    monkeypatch.setattr(joint.recovery,'measurements',measured)
    assert joint.run(args) == 1
    state = json.loads((output/'progress.json').read_text())
    assert not state['record_hashes']
    assert state['sessions'][-1]['stop_reason'] == {'rss':'process_group_rss_exhausted',
        'disk':'scratch_disk_headroom_exhausted','oom':'cgroup_oom_event'}[guard]
    for path in output.glob('jobs/*/attempt-*/receipt.json'):
        assert json.loads(path.read_text())['group_cleanup_verified']


def test_nonconverged_zero_exit_record_is_not_promoted(synthetic):
    exe = synthetic[0]
    exe.write_text(exe.read_text().replace("SCF has converged.","SCF did not converge."))
    result = run_fake(synthetic)
    assert result.returncode == 1, result.stderr
    state = json.loads((synthetic[1]/'progress.json').read_text())
    assert not state['record_hashes']
    receipt = json.loads(next(synthetic[1].glob('jobs/*/attempt-*/receipt.json')).read_text())
    assert 'converg' in receipt['validation_error']
