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
    approved_output = json.loads(AUTH.read_text())['attempt_path']
    result = subprocess.run([sys.executable,str(PROGRAM),'--plan-root',str(PLAN),
        '--approval',str(AUTH),'--matrix',str(MATRIX),'--output',approved_output,'--check-resume'],
        capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['expected_count'] == 30
    assert data['remaining'][0] == 'ethanol-methanol-d3-r0--full-parent'
    assert len(data['remaining']) == 30
    assert data['remaining_wall_seconds'] == 86400
    assert not (tmp_path/'output').exists()


def test_copied_approval_cannot_reset_budget_by_changing_attempt(tmp_path):
    result = subprocess.run(command(tmp_path/'fresh-ledger', ['--check-resume']), capture_output=True, text=True)
    assert result.returncode == 2, 'copied authorization incorrectly admitted a fresh 86400-second budget'


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
    assert 'authorization' in result.stderr.lower()


def test_stricter_resource_and_pilot_policy(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO/'tools'))
    import resume_joint_quantum as joint
    policy = joint.execution_policy(json.loads(AUTH.read_text()), continuation=False)
    assert policy['rss_max_bytes'] <= 6*2**30
    assert policy['disk_min_bytes'] == 5*2**30
    assert policy['pilot_wall_seconds'] == 3600
    assert policy['stop_after_job'] == 'ethanol-methanol-d3-r0--full-parent'


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
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
    output = tmp_path/'output'
    command(output)
    monkeypatch.syspath_prepend(str(REPO/'tools'))
    import resume_joint_quantum as joint
    from generate_neutral_quantum import digest
    # Substitute the trusted decision dependency in this test process only.
    # The real CLI always verifies the actual recorded authorization constant.
    monkeypatch.setattr(joint,'APPROVAL_PATH',tmp_path/'bound-authorization.json')
    monkeypatch.setattr(joint,'APPROVAL_SHA256',digest(joint.APPROVAL_PATH))
    return executable, output


def run_fake(synthetic, mode='', extra=()):
    import argparse
    import resume_joint_quantum as joint
    exe, output = synthetic
    cmd = command(output)
    parser = argparse.ArgumentParser()
    parser.add_argument('--wall-limit-seconds',type=float)
    parser.add_argument('--continue-batch',action='store_true')
    parser.add_argument('--pilot-assessment')
    options = vars(parser.parse_args(extra))
    args = argparse.Namespace(plan_root=str(PLAN),approval=str(output.parent/'bound-authorization.json'),
        matrix=str(MATRIX),output=str(output),reference_python=str(exe),check_resume=False,
        memory_gib=3.,**options)
    previous = os.environ.get('JOINT_QUANTUM_TEST_MODE')
    os.environ['JOINT_QUANTUM_TEST_MODE'] = mode
    try:
        try:
            return subprocess.CompletedProcess(cmd,joint.run(args),'','')
        except (ValueError,KeyError,OSError,TypeError) as error:
            return subprocess.CompletedProcess(cmd,2,'',str(error))
    finally:
        if previous is None:os.environ.pop('JOINT_QUANTUM_TEST_MODE',None)
        else:os.environ['JOINT_QUANTUM_TEST_MODE'] = previous


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


def test_actual_psi4_1102_convergence_message_is_admitted(synthetic):
    exe = synthetic[0]
    exe.write_text(exe.read_text().replace('SCF has converged.', 'Energy and wave function converged.'))
    assert run_fake(synthetic).returncode == 1
    state = json.loads((synthetic[1]/'progress.json').read_text())
    assert len(state['record_hashes']) == 1


@pytest.fixture
def rejected_converged_pilot(synthetic, monkeypatch):
    import resume_joint_quantum as joint
    from generate_neutral_quantum import digest
    exe, output = synthetic
    exe.write_text(exe.read_text().replace('SCF has converged.', 'Energy and wave function converged.'))
    validator = joint.validate_joint_record
    def previous_parser(*args):
        raise ValueError('explicit SCF convergence is absent from the saved Psi4 log')
    monkeypatch.setattr(joint, 'validate_joint_record', previous_parser)
    assert run_fake(synthetic).returncode == 1
    monkeypatch.setattr(joint, 'validate_joint_record', validator)
    source = next(output.glob('jobs/*/attempt-*/receipt.json'))
    monkeypatch.setattr(joint, 'REJECTED_PILOT_RECEIPT_SHA256', digest(source))
    return source


def revalidate_fake(synthetic):
    import resume_joint_quantum as joint
    exe, output = synthetic
    approval, matrix = joint.validate_authorization(PLAN, joint.APPROVAL_PATH, MATRIX)
    return joint.revalidate_pilot(output, PLAN, approval, matrix, str(exe))


def test_posthoc_validation_preserves_rejection_and_debit_without_qm(synthetic, rejected_converged_pilot):
    import resume_joint_quantum as joint
    from generate_neutral_quantum import digest
    output = synthetic[1]
    original = rejected_converged_pilot.read_bytes()
    charged = json.loads((output/'progress.json').read_text())['wall_seconds_debited']
    receipt_path = revalidate_fake(synthetic)
    receipt = json.loads(receipt_path.read_text())
    assert receipt['completion_kind'] == 'validation_only_correction'
    assert receipt['original_receipt_sha256'] == digest(rejected_converged_pilot)
    assert 'validation_error' not in receipt
    assert rejected_converged_pilot.read_bytes() == original
    # A future executable must not be called while recovering this record.
    synthetic[0].write_text('#!'+sys.executable+'\nraise SystemExit(91)\n')
    assert run_fake(synthetic).returncode == 1
    state = json.loads((output/'progress.json').read_text())
    assert len(state['record_hashes']) == 1 and state['wall_seconds_debited'] >= charged
    assert len(list(output.glob('jobs/*/attempt-*'))) == 2
    assert revalidate_fake(synthetic) == receipt_path
    assert rejected_converged_pilot.read_bytes() == original
    assert joint.recovery.completion_receipt(receipt_path.with_name('record.json'), joint.PILOT)


@pytest.mark.parametrize('target', ['receipt.json', 'record.json', 'record.psi4.txt'])
def test_revalidation_rejects_changed_original_evidence(synthetic, rejected_converged_pilot, target):
    path = rejected_converged_pilot.with_name(target)
    path.write_text(path.read_text()+'\nchanged\n')
    with pytest.raises(ValueError):
        revalidate_fake(synthetic)
    assert len(list(synthetic[1].glob('jobs/*/attempt-*'))) == 1


def test_revalidation_respects_lease_and_live_worker(synthetic, rejected_converged_pilot, monkeypatch):
    import fcntl
    import resume_joint_quantum as joint
    with (synthetic[1].parent/'queue-lease.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match='coordinator'):
            revalidate_fake(synthetic)
    monkeypatch.setattr(joint.recovery, 'attempt_processes', lambda output: [1234])
    with pytest.raises(ValueError, match='active'):
        revalidate_fake(synthetic)
    assert len(list(synthetic[1].glob('jobs/*/attempt-*'))) == 1


@pytest.mark.parametrize('mode', ['missing', 'changed'])
def test_recovery_rejects_missing_or_changed_convergence_log(synthetic, mode):
    assert run_fake(synthetic).returncode == 1
    log = next(synthetic[1].glob('jobs/*/attempt-*/record.psi4.txt'))
    if mode == 'missing':log.unlink()
    else:log.write_text(log.read_text()+'tampered diagnostic\n')
    result = run_fake(synthetic)
    assert result.returncode == 2, result.stderr


def test_zero_projection_assessment_cannot_replace_measured_evidence(synthetic):
    import resume_joint_quantum as joint
    from generate_neutral_quantum import digest
    assert run_fake(synthetic).returncode == 1
    output = synthetic[1]; state = json.loads((output/'progress.json').read_text())
    pilot = state['provenance'][joint.PILOT]
    data = dict(continue_authorized=True,matrix_sha256=json.loads(AUTH.read_text())['matrix_sha256'],
        pilot_record_sha256=state['record_hashes'][joint.PILOT],pilot_receipt_sha256=digest(pilot['receipt']),
        projected_remaining_worker_seconds=0.,projected_max_rss_bytes=0.,projected_scratch_bytes=0.)
    path = output.parent/'assessment.json'; path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='measured'):
        joint.validate_assessment(path,output,json.loads(AUTH.read_text()))


def test_measured_pilot_continues_exact_matrix_and_never_recalculates(synthetic):
    import resume_joint_quantum as joint
    assert run_fake(synthetic).returncode == 1
    output = synthetic[1]
    assessment = dict(joint.pilot_evidence(output),continue_authorized=True,
        matrix_sha256=json.loads(AUTH.read_text())['matrix_sha256'],
        projected_remaining_worker_seconds=1000.,projected_max_rss_bytes=2**30,
        projected_scratch_bytes=0.,notice='SYNTHETIC SOFTWARE TEST ONLY')
    path = output.parent/'assessment.json'; path.write_text(json.dumps(assessment))
    result = run_fake(synthetic,extra=['--continue-batch','--pilot-assessment',str(path)])
    assert result.returncode == 0, result.stderr
    state = json.loads((output/'progress.json').read_text())
    assert len(state['record_hashes']) == 30 and state['ready_for_comparison']
    assert len(list(output.glob('jobs/*/attempt-*'))) == 30
    for p in output.glob('jobs/*/attempt-*/receipt.json'):
        receipt = json.loads(p.read_text())
        assert 'resources.jsonl' in receipt['diagnostic_sha256']
        assert 'record.psi4.txt' in receipt['diagnostic_sha256']
    prior = state['wall_seconds_debited']
    repeated = run_fake(synthetic,extra=['--continue-batch','--pilot-assessment',str(path)])
    assert repeated.returncode == 0, repeated.stderr
    assert len(list(output.glob('jobs/*/attempt-*'))) == 30
    assert json.loads((output/'progress.json').read_text())['wall_seconds_debited'] >= prior


def test_pilot_ceiling_cannot_reset_on_retry(synthetic):
    assert run_fake(synthetic,'computed_fail').returncode == 1
    output = synthetic[1]; path = output/'progress.json'; state = json.loads(path.read_text())
    state['sessions'][-1]['wall_seconds'] = 3600.
    path.write_text(json.dumps(state))
    assert run_fake(synthetic).returncode == 1
    assert len(list(output.glob('jobs/*/attempt-*'))) == 1
    assert json.loads(path.read_text())['sessions'][-1]['stop_reason'] == 'pilot_budget_exhausted'
