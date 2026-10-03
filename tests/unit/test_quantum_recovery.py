"""Recovery software tests; synthetic records are never chemical evidence."""
import hashlib
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import runpy

import pytest

REPO = Path(__file__).resolve().parents[2]
PROGRAM = REPO / 'tools/resume_neutral_quantum.py'
PLAN = REPO / 'fixtures/chemical_reference_v3'
HISTORY = REPO / 'Worker_Log/Milestone_00/evidence/M00_reference_v3'
APPROVAL = REPO / 'Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json'


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(root=PLAN, approval=APPROVAL, output=None, extra=()):
    return [sys.executable, str(PROGRAM), '--plan-root', str(root),
            '--approval', str(approval), '--output', str(output), *extra]


def historic_args():
    return ['--resume-from', str(HISTORY / 'quantum-attempt-v1'),
            '--stop-state', str(HISTORY / 'stop-state-20261003.json'),
            '--prior-launch', str(HISTORY / 'launch-v1.json')]


def test_frozen_partial_check_schedules_only_38_and_preserves_history(tmp_path):
    originals = {p: sha(p) for p in (HISTORY / 'quantum-attempt-v1').rglob('*') if p.is_file()}
    result = subprocess.run(command(output=tmp_path / 'output',
                           extra=historic_args() + ['--check-resume']), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['expected_count'] == 46
    assert data['reused_count'] == 8
    assert len(data['remaining']) == 38
    assert data['prior_wall_seconds'] > 1931.9925
    assert data['prior_wall_seconds'] < 2400
    assert not (tmp_path / 'output').exists()
    assert originals == {p: sha(p) for p in originals}


@pytest.fixture
def synthetic(tmp_path):
    root = tmp_path / 'plan'
    settings = dict(settings={'basis': 'def2-tzvppd'}, basis_file_sha256={'basis.gbs': 'a' * 64},
                    convergence_checks={'rows': ['one'], 'settings': {'dft_radial_points': 199}},
                    wall_cap_hours=12, threads=2, memory='5 GiB')
    for name in ('one', 'two'):
        write(root / 'structures' / (name + '.json'),
              dict(name=name, elements=['H'], atomic_numbers=[1], positions_angstrom=[[0., 0., 0.]]))
    write(root / 'reference-settings.json', settings)
    (root / 'reference-explicit.lock').write_text('@EXPLICIT\nhttps://example.invalid/fake.conda#' + 'b' * 64 + '\n')
    files = {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}
    write(root / 'input-manifest.json', dict(files=files))
    approval = tmp_path / 'approval.json'
    write(approval, dict(user_agreed=True, design_verdict='accepted_for_scope', reviewer_model='gpt-6-astra',
                         reasoning_effort='high', fresh_context=True, reviewed_commit='c' * 40,
                         input_manifest_sha256=sha(root / 'input-manifest.json'),
                         approved_resource_cap=dict(wall_hours=12, cpu_threads=2, psi4_memory='5 GiB'),
                         notice='SYNTHETIC SOFTWARE TEST ONLY'))
    executable = tmp_path / 'reference' / 'bin' / 'python'
    executable.parent.mkdir(parents=True)
    write(executable.parents[1] / 'conda-meta/fake.json', dict(url='https://example.invalid/fake.conda', sha256='b' * 64))
    # Stand-in executable at the subprocess boundary, never a test switch in production code.
    executable.write_text('#!' + sys.executable + '\n' + '''
import json, os, resource, sys, time
from pathlib import Path
order=json.loads(Path(sys.argv[-1]).read_text())
data=order['structure']; name=order['job_name']; output=Path(order['output'])
mode=os.environ.get('QUANTUM_RECOVERY_TEST_MODE', '')
if mode=='timeout':
    child=os.fork()
    if child==0:
        Path(os.environ['QUANTUM_RECOVERY_TEST_CHILD']).write_text(str(os.getpid()))
    time.sleep(10)
if mode=='fail' and name=='two':
    output.write_text(json.dumps(dict(status='failed',name=name,exception='synthetic failure')))
    sys.exit(1)
record=dict(status='computed', name=name, source_input_sha256=order['source_input_sha256'],
            method='wb97m-d3bj/def2-tzvppd', psi4_version='1.10.2', formal_charge=0, multiplicity=1,
            atomic_numbers=data['atomic_numbers'], positions_angstrom=data['positions_angstrom'],
            energy_hartree=-1., gradient_hartree_bohr=[[0.,0.,0.]],
            quantum_energy_variables={'DISPERSION CORRECTION ENERGY':-.001,'DFT VV10 ENERGY':0.},
            basis_file_sha256=order['basis_file_sha256'], settings=order['settings'], network_denied=True,
            wall_seconds=.001, threads=2, memory=order['runtime_memory'],
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
output.write_text(json.dumps(record))
print(json.dumps(dict(name=name,status='computed')))
if mode=='computed_fail' and name=='two':
    sys.exit(23)
''')
    executable.chmod(0o755)
    return root, approval, executable, tmp_path / 'output'


def run_synthetic(synthetic, extra=(), mode=''):
    root, approval, executable, output = synthetic
    env = {**os.environ, 'QUANTUM_RECOVERY_TEST_MODE': mode,
           'QUANTUM_RECOVERY_TEST_CHILD': str(output.parent / 'child.pid')}
    return subprocess.run(command(root, approval, output,
                          ['--reference-python', str(executable), *extra]),
                          env=env, capture_output=True, text=True)


def test_completed_bundle_has_exact_names_runtime_allocation_and_durable_receipts(synthetic):
    result = run_synthetic(synthetic)
    assert result.returncode == 0, result.stderr
    output = synthetic[-1]
    manifest = json.loads((output / 'manifest.json').read_text())
    assert manifest['ready_for_comparison'] is True
    assert set(manifest['files']) == {'records/one.json', 'records/two.json', 'records/one-fine-grid.json'}
    for name, digest in manifest['files'].items():
        assert sha(output / name) == digest
        record = json.loads((output / name).read_text())
        assert record['name'] == Path(name).stem
        assert record['memory'] == '3 GiB'
    receipts = list(output.glob('jobs/*/attempt-*/receipt.json'))
    assert len(receipts) == 3
    assert all(json.loads(p.read_text())['exit'] == 0 for p in receipts)
    assert not list(output.glob('jobs/*/attempt-*/scratch'))


def test_retry_reuses_successes_keeps_failed_attempt_and_debits_previous_time(synthetic):
    failed = run_synthetic(synthetic, mode='fail')
    assert failed.returncode == 1, failed.stderr
    output = synthetic[-1]
    assert not (output / 'manifest.json').exists()
    originals = {p: sha(p) for p in output.glob('jobs/*/attempt-*/*') if p.is_file()}
    prior = json.loads((output / 'progress.json').read_text())['wall_seconds_debited']
    passed = run_synthetic(synthetic)
    assert passed.returncode == 0, passed.stderr
    assert all(sha(p) == digest for p, digest in originals.items())
    assert len(list(output.glob('jobs/one/attempt-*'))) == 1
    assert len(list(output.glob('jobs/two/attempt-*'))) == 2
    assert json.loads((output / 'progress.json').read_text())['wall_seconds_debited'] > prior


def test_tampered_reused_record_blocks_before_launch(synthetic):
    assert run_synthetic(synthetic).returncode == 0
    output = synthetic[-1]
    (output / 'records/one.json').write_text('{}')
    result = run_synthetic(synthetic)
    assert result.returncode != 0
    assert 'digest' in result.stderr.lower()
    assert len(list(output.glob('jobs/*/attempt-*'))) == 3


@pytest.mark.parametrize('memory', ['0', '6', 'nan'])
def test_invalid_runtime_memory_is_rejected(synthetic, memory):
    result = run_synthetic(synthetic, ['--memory-gib', memory])
    assert result.returncode != 0
    assert not synthetic[-1].exists()


def test_exhausted_budget_does_not_create_ready_manifest_or_launch(synthetic):
    result = run_synthetic(synthetic, ['--wall-limit-seconds', '0.01'])
    assert result.returncode == 1, result.stderr
    output = synthetic[-1]
    assert not (output / 'manifest.json').exists()
    assert json.loads((output / 'progress.json').read_text())['ready_for_comparison'] is False
    assert not list(output.glob('jobs/*/attempt-*'))


@pytest.mark.parametrize('mutation', ['gradient', 'settings', 'dispersion', 'status'])
def test_historical_content_is_validated_even_if_checkpoint_hash_is_updated(tmp_path, mutation):
    history = tmp_path / 'history'
    shutil.copytree(HISTORY / 'quantum-attempt-v1', history / 'quantum-attempt-v1')
    stop = json.loads((HISTORY / 'stop-state-20261003.json').read_text())
    record = history / 'quantum-attempt-v1/records/acetamide-0.json'
    data = json.loads(record.read_text())
    if mutation == 'gradient':
        data['gradient_hartree_bohr'] = [[0., 0., 0.]]
    elif mutation == 'settings':
        data['settings']['dft_radial_points'] = 1
    elif mutation == 'dispersion':
        data['quantum_energy_variables']['DFT VV10 ENERGY'] = 1.
    else:
        data['status'] = 'failed'
    write(record, data)
    next(r for r in stop['completed'] if r['name'] == 'acetamide-0')['sha256'] = sha(record)
    write(history / 'stop.json', stop)
    result = subprocess.run(command(output=tmp_path / 'output', extra=[
        '--resume-from', str(history / 'quantum-attempt-v1'), '--stop-state', str(history / 'stop.json'),
        '--prior-launch', str(HISTORY / 'launch-v1.json'), '--check-resume']), capture_output=True, text=True)
    assert result.returncode == 2
    assert 'Recovery rejected:' in result.stderr
    assert not (tmp_path / 'output').exists()


def test_second_coordinator_is_rejected_by_lock(synthetic):
    output = synthetic[-1]
    output.mkdir()
    with (output / 'coordinator.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = run_synthetic(synthetic)
    assert result.returncode == 2
    assert 'another coordinator' in result.stderr
    assert not (output / 'progress.json').exists()


@pytest.mark.parametrize('missing_identity', [False, True])
def test_recovery_refuses_a_live_old_worker(synthetic, missing_identity):
    assert run_synthetic(synthetic).returncode == 0
    output = synthetic[-1]
    progress = json.loads((output / 'progress.json').read_text())
    session = progress['sessions'][-1]
    session['status'] = 'running'
    fields = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()
    session['active_worker'] = dict(pid=os.getpid(), start_ticks=None if missing_identity else fields[19])
    write(output / 'progress.json', progress)
    result = run_synthetic(synthetic)
    assert result.returncode == 2
    assert 'remains active' in result.stderr


def test_record_saved_before_progress_survives_lost_worker_identity(synthetic):
    assert run_synthetic(synthetic).returncode == 0
    output = synthetic[-1]
    progress = json.loads((output / 'progress.json').read_text())
    progress['record_hashes'].pop('two')
    progress['sessions'][-1].update(status='running', active_worker=dict(pid=99999999, start_ticks=None))
    write(output / 'progress.json', progress)
    (output / 'records/two.json').unlink()
    (output / 'manifest.json').unlink()
    result = run_synthetic(synthetic)
    assert result.returncode == 0, result.stderr
    final = json.loads((output / 'progress.json').read_text())
    assert final['provenance']['two']['recovered'] is True
    assert final['provenance']['two']['coordinator_exit'] == 0
    assert final['sessions'][-2]['status'] == 'interrupted'
    assert len(list(output.glob('jobs/two/attempt-*'))) == 1


def test_resume_preserves_known_failed_exit_and_retries_computed_record(synthetic):
    first = run_synthetic(synthetic, mode='computed_fail')
    assert first.returncode == 1, first.stderr
    output = synthetic[-1]
    receipt = output / 'jobs/two/attempt-0001/receipt.json'
    assert json.loads(receipt.read_text())['exit'] == 23
    assert json.loads(receipt.with_name('record.json').read_text())['status'] == 'computed'
    original = sha(receipt)
    second = run_synthetic(synthetic, mode='computed_fail')
    assert second.returncode == 1, second.stderr
    state = json.loads((output / 'progress.json').read_text())
    assert not state['ready_for_comparison']
    assert 'two' not in state['record_hashes']
    assert len(list(output.glob('jobs/two/attempt-*'))) == 2
    assert sha(receipt) == original


@pytest.mark.parametrize('field,value', [('reason', 'timeout'),
    ('reason', 'memory_headroom_exhausted'), ('reason', 'scratch_disk_headroom_exhausted'),
    ('validation_error', 'invalid original completion')])
def test_resume_does_not_salvage_a_record_with_a_known_stop_or_validation_failure(synthetic, field, value):
    assert run_synthetic(synthetic).returncode == 0
    output = synthetic[-1]
    state = json.loads((output / 'progress.json').read_text())
    state['record_hashes'].pop('two')
    state['provenance'].pop('two')
    write(output / 'progress.json', state)
    (output / 'records/two.json').unlink()
    (output / 'manifest.json').unlink()
    receipt = output / 'jobs/two/attempt-0001/receipt.json'
    data = json.loads(receipt.read_text())
    data[field] = value
    write(receipt, data)
    original = sha(receipt)
    assert run_synthetic(synthetic).returncode == 0
    final = json.loads((output / 'progress.json').read_text())
    assert len(list(output.glob('jobs/two/attempt-*'))) == 2
    assert final['provenance']['two']['coordinator_exit'] == 0
    assert final['provenance']['two']['source'].endswith('attempt-0002/record.json')
    assert sha(receipt) == original


def test_resume_keeps_genuinely_missing_exit_receipt_unknown(synthetic):
    assert run_synthetic(synthetic).returncode == 0
    output = synthetic[-1]
    state = json.loads((output / 'progress.json').read_text())
    state['record_hashes'].pop('two')
    state['provenance'].pop('two')
    write(output / 'progress.json', state)
    (output / 'records/two.json').unlink()
    (output / 'manifest.json').unlink()
    (output / 'jobs/two/attempt-0001/receipt.json').unlink()
    assert run_synthetic(synthetic).returncode == 0
    final = json.loads((output / 'progress.json').read_text())
    assert final['provenance']['two']['coordinator_exit'] is None
    assert len(list(output.glob('jobs/two/attempt-*'))) == 1


def test_clean_file_cache_does_not_consume_unreclaimable_memory_headroom(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / 'tools'))
    functions = runpy.run_path(str(PROGRAM))
    (tmp_path / 'memory.current').write_text(str(8 * 2**30))
    (tmp_path / 'memory.stat').write_text('anon 1073741824\nfile 6442450944\n'
                                         'shmem 0\nkernel 1073741824\nslab_reclaimable 536870912\n'
                                         'file_dirty 0\nfile_writeback 0\n')
    original = Path
    monkeypatch.setitem(functions['measurements'].__globals__, 'Path',
                        lambda p: tmp_path if p == '/sys/fs/cgroup' else original(p))
    sample = functions['measurements']()
    assert sample.get('memory.pressure_bytes') == int(1.5 * 2**30)


def test_timeout_terminates_worker_process_group_and_preserves_receipt(synthetic):
    result = run_synthetic(synthetic, ['--wall-limit-seconds', '0.3'], mode='timeout')
    assert result.returncode == 1, result.stderr
    output = synthetic[-1]
    receipts = list(output.glob('jobs/*/attempt-*/receipt.json'))
    assert len(receipts) == 1
    assert json.loads(receipts[0].read_text())['reason'] == 'timeout'
    child_pid = int((output.parent / 'child.pid').read_text())
    status = Path('/proc') / str(child_pid) / 'stat'
    assert not status.exists() or status.read_text().split()[2] == 'Z'
