"""Crash-boundary tests run synthetic subprocesses, never a QM interpreter."""
from argparse import Namespace
import fcntl
import json
import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
import time

import pytest

REPO = Path(__file__).resolve().parents[2]
UNIT = runpy.run_path(str(REPO / 'tests/unit/test_quantum_recovery.py'))


@pytest.fixture
def synthetic(tmp_path):
    return UNIT['synthetic'].__wrapped__(tmp_path)


def load_recovery(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / 'tools'))
    return runpy.run_path(str(REPO / 'tools/resume_neutral_quantum.py'))


def arguments(synthetic):
    root, approval, executable, output = synthetic
    return dict(plan_root=str(root), approval=str(approval), output=str(output),
                reference_python=str(executable), resume_from=None, stop_state=None,
                prior_launch=None, check_resume=False, memory_gib=3., wall_limit_seconds=None)


def wait_for(predicate, seconds=5):
    deadline = time.monotonic() + seconds
    while not predicate() and time.monotonic() < deadline:
        time.sleep(.01)
    return predicate()


@pytest.mark.parametrize('boundary', ['before_spawn', 'after_spawn', 'after_identity', 'after_authorize'])
def test_coordinator_crash_cannot_leave_live_or_duplicate_work(synthetic, monkeypatch, boundary):
    functions = load_recovery(monkeypatch)
    output = synthetic[-1]
    guard_pid = output.parent / 'guard.pid'
    child_pid = output.parent / 'child.pid'
    script = output.parent / 'crash.py'
    script.write_text(f'''
import os, runpy, subprocess, sys, time
from argparse import Namespace
from pathlib import Path
sys.path.insert(0, {str(REPO / 'tools')!r})
functions = runpy.run_path({str(REPO / 'tools/resume_neutral_quantum.py')!r})
real_popen = subprocess.Popen
def spawn(*args, **kwargs):
    if {boundary!r} == 'before_spawn': os._exit(99)
    process = real_popen(*args, **kwargs)
    Path({str(guard_pid)!r}).write_text(str(process.pid))
    if {boundary!r} == 'after_spawn': os._exit(99)
    return process
subprocess.Popen = spawn
real_dump = functions['atomic_dump']
def checkpoint(path, data):
    real_dump(path, data)
    if {boundary!r} == 'after_identity' and Path(path).name == 'progress.json' and data['sessions'][-1].get('active_worker'):
        os._exit(99)
    active = data.get('sessions', [{{}}])[-1].get('active_worker')
    if {boundary!r} == 'after_authorize' and active and not active.get('guarded'):
        deadline = time.monotonic() + 5
        while not Path({str(child_pid)!r}).exists() and time.monotonic() < deadline: time.sleep(.01)
        os._exit(99)
functions['run'].__globals__['atomic_dump'] = checkpoint
real_write = os.write
def authorize(fd, data):
    result = real_write(fd, data)
    if {boundary!r} == 'after_authorize' and data == b'G':
        deadline = time.monotonic() + 5
        while not Path({str(child_pid)!r}).exists() and time.monotonic() < deadline: time.sleep(.01)
        os._exit(99)
    return result
os.write = authorize
functions['run'](Namespace(**{arguments(synthetic)!r}))
''')
    env = {**os.environ, 'QUANTUM_RECOVERY_TEST_MODE': 'timeout',
           'QUANTUM_RECOVERY_TEST_CHILD': str(child_pid)}
    try:
        first = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True, timeout=15)
        assert first.returncode == 99, first.stderr
        if guard_pid.exists():
            pid = int(guard_pid.read_text())
            assert wait_for(lambda: functions['process_identity'](pid) is None), 'Orphan launch group survived coordinator death'
        if boundary == 'after_authorize':
            assert child_pid.exists(), 'Fault did not reach an actual synthetic descendant'
            assert wait_for(lambda: functions['process_identity'](int(child_pid.read_text())) is None)
        result = UNIT['run_synthetic'](synthetic)
        assert result.returncode == 0, result.stderr
        state = json.loads((output / 'progress.json').read_text())
        assert state['ready_for_comparison']
        assert state['sessions'][-2]['status'] == 'interrupted'
        assert state['wall_seconds_debited'] >= state['sessions'][-2]['wall_seconds']
    finally:
        if guard_pid.exists():
            try:
                os.killpg(int(guard_pid.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass


def assert_durable_run(synthetic, monkeypatch):
    functions = load_recovery(monkeypatch)
    output = synthetic[-1]
    actual_sync = os.fsync
    file_syncs, directory_syncs = {}, {}
    sequence = 0

    def trace(fd):
        nonlocal sequence
        path = Path(os.readlink(f'/proc/self/fd/{fd}'))
        sequence += 1
        if path.is_dir():
            directory_syncs[path] = sequence
        else:
            file_syncs[path] = sequence
            if path.name == 'progress.json.tmp':
                state = json.loads(path.read_text())
                for name in state['record_hashes']:
                    target = output / 'records' / (name + '.json')
                    assert file_syncs.get(target, 0) or file_syncs.get(target.with_suffix('.json.tmp'), 0), 'Unsynced promoted record'
                    latest = max(file_syncs.get(target, 0), file_syncs.get(target.with_suffix('.json.tmp'), 0))
                    assert directory_syncs.get(target.parent, 0) > latest, 'Record entry not durable'
                    if state['provenance'][name].get('receipt'):
                        receipt = Path(state['provenance'][name]['receipt'])
                        assert receipt in file_syncs, 'Receipt not durable before admission'
                        assert directory_syncs.get(receipt.parent, 0) > file_syncs[receipt], 'Receipt entry not durable'
        actual_sync(fd)

    monkeypatch.setattr(os, 'fsync', trace)
    assert functions['run'](Namespace(**arguments(synthetic))) == 0
    assert len(list(output.glob('records/*.json'))) == 3


def test_progress_never_references_unsynced_record_or_receipt(synthetic, monkeypatch):
    assert_durable_run(synthetic, monkeypatch)


@pytest.mark.parametrize('unknown_exit', [False, True])
def test_legacy_and_salvaged_data_are_synced_before_new_progress(synthetic, monkeypatch, unknown_exit):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    output = synthetic[-1]
    state = json.loads((output / 'progress.json').read_text())
    state['record_hashes'].pop('two')
    state['provenance'].pop('two')
    UNIT['write'](output / 'progress.json', state)
    (output / 'records/two.json').unlink()
    (output / 'manifest.json').unlink()
    if unknown_exit:
        (output / 'jobs/two/attempt-0001/receipt.json').unlink()
    assert_durable_run(synthetic, monkeypatch)


@pytest.mark.parametrize('boundary', ['receipt', 'promotion', 'progress'])
def test_completion_boundary_crash_reuses_the_durable_record(synthetic, boundary):
    output = synthetic[-1]
    script = output.parent / 'completion_crash.py'
    script.write_text(f'''
import os, runpy, sys
from argparse import Namespace
from pathlib import Path
sys.path.insert(0, {str(REPO / 'tools')!r})
functions = runpy.run_path({str(REPO / 'tools/resume_neutral_quantum.py')!r})
namespace = functions['run'].__globals__
original_receipt = namespace['exclusive_dump']
def receipt(path, data):
    original_receipt(path, data)
    if {boundary!r} == 'receipt' and Path(path).name == 'receipt.json': os._exit(99)
namespace['exclusive_dump'] = receipt
original_publish = namespace['publish_record']
def publish(source, target):
    original_publish(source, target)
    if {boundary!r} == 'promotion': os._exit(99)
namespace['publish_record'] = publish
original_checkpoint = namespace['atomic_dump']
def checkpoint(path, data):
    original_checkpoint(path, data)
    if {boundary!r} == 'progress' and Path(path).name == 'progress.json' and data['record_hashes']: os._exit(99)
namespace['atomic_dump'] = checkpoint
functions['run'](Namespace(**{arguments(synthetic)!r}))
''')
    first = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=15)
    assert first.returncode == 99, first.stderr
    originals = {p: UNIT['sha'](p) for p in output.glob('jobs/one/attempt-0001/*') if p.is_file()}
    result = UNIT['run_synthetic'](synthetic)
    assert result.returncode == 0, result.stderr
    assert len(list(output.glob('jobs/one/attempt-*'))) == 1
    assert all(UNIT['sha'](p) == sha for p, sha in originals.items())


def test_legacy_live_worker_without_saved_identity_blocks_recovery(synthetic):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    output = synthetic[-1]
    state = json.loads((output / 'progress.json').read_text())
    state['sessions'][-1]['status'] = 'running'
    state['sessions'][-1].pop('active_worker', None)
    UNIT['write'](output / 'progress.json', state)
    process = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                               cwd=output / 'jobs/one/attempt-0001', start_new_session=True)
    try:
        result = UNIT['run_synthetic'](synthetic)
        assert result.returncode == 2
        assert 'remains active' in result.stderr
        assert len(list(output.glob('jobs/one/attempt-*'))) == 1
    finally:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def test_reused_pid_does_not_identify_an_unrelated_process_as_the_old_worker(synthetic):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    output = synthetic[-1]
    state = json.loads((output / 'progress.json').read_text())
    state['sessions'][-1].update(status='running', active_worker=dict(pid=os.getpid(), start_ticks='different-start'))
    UNIT['write'](output / 'progress.json', state)
    result = UNIT['run_synthetic'](synthetic)
    assert result.returncode == 0, result.stderr


def test_known_failure_in_an_old_ready_checkpoint_is_rejected(synthetic):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    receipt = synthetic[-1] / 'jobs/two/attempt-0001/receipt.json'
    data = json.loads(receipt.read_text())
    data['exit'] = 23
    UNIT['write'](receipt, data)
    result = UNIT['run_synthetic'](synthetic)
    assert result.returncode == 2
    assert 'known failed completion' in result.stderr


def test_resource_samples_include_reference_children_not_only_supervisor(tmp_path, monkeypatch):
    functions = load_recovery(monkeypatch)
    marker = tmp_path / 'child-ready'
    child_code = f"from pathlib import Path; import time; allocation=bytearray(64*2**20); Path({str(marker)!r}).touch(); time.sleep(30)"
    code = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child_code!r}]); time.sleep(30)"
    process = subprocess.Popen([sys.executable, '-c', code], start_new_session=True)
    try:
        assert wait_for(marker.exists)
        assert functions['measurements'](process.pid)['VmRSS'] > 64 * 2**20
    finally:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def test_uncheckpointed_supervisor_inherits_the_queue_lock(synthetic):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    output = synthetic[-1]
    launch = output / 'jobs/one/lease-probe/launch.json'
    ran = output.parent / 'unauthorized-execution'
    UNIT['write'](launch, dict(command=[sys.executable, '-c', f'from pathlib import Path; Path({str(ran)!r}).touch()']))
    lease = (output / 'coordinator.lock').open('a')
    fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
    control_read, control_write = os.pipe()
    process = subprocess.Popen([sys.executable, str(REPO / 'tools/quantum_worker_guard.py'),
        '--launch', str(launch), '--lease-fd', str(lease.fileno()), '--control-fd', str(control_read)],
        cwd=launch.parent, start_new_session=True, pass_fds=(lease.fileno(), control_read))
    os.close(control_read)
    lease.close()
    try:
        assert wait_for(launch.with_name('worker-identity.json').exists)
        result = UNIT['run_synthetic'](synthetic)
        assert result.returncode == 2
        assert 'another coordinator' in result.stderr
        assert not ran.exists()
    finally:
        os.close(control_write)
        process.wait(timeout=5)
    assert process.returncode == 125


def test_supervisor_loss_cleans_reference_group_before_next_launch(synthetic, monkeypatch):
    functions = load_recovery(monkeypatch)
    output = synthetic[-1]
    marker = output.parent / 'orphan.json'
    later = output.parent / 'later-job.json'
    original = synthetic[2]
    executable = original.with_name('supervisor-loss-worker')
    header, body = original.read_text().split('\n', 1)
    injection = f'''
import signal
marker=Path({str(marker)!r});later=Path({str(later)!r})
if name=='one':
    marker.write_text(json.dumps({{'pid':os.getpid(),'group':os.getpgrp(),'supervisor':os.getppid()}}))
    os.kill(os.getppid(),signal.SIGKILL)
    time.sleep(30)
elif not later.exists():
    info=json.loads(marker.read_text())
    try:
        fields=(Path('/proc')/str(info['pid'])/'stat').read_text().rsplit(')',1)[1].split()
        live=fields[0]!='Z'
    except OSError:live=False
    later.write_text(json.dumps({{'old_reference_child_live':live}}))
'''
    needle = "mode=os.environ.get('QUANTUM_RECOVERY_TEST_MODE', '')\n"
    assert needle in body
    executable.write_text(header + '\n' + body.replace(needle, needle + injection))
    executable.chmod(0o755)
    try:
        result = UNIT['run_synthetic']((*synthetic[:2], executable, output))
        assert result.returncode == 1, result.stderr
        assert marker.exists() and later.exists(), 'Fault did not reach the intended scheduling boundary'
        child = json.loads(marker.read_text())
        assert not json.loads(later.read_text())['old_reference_child_live'], 'Overlapping reference workers after supervisor loss'
        assert functions['process_identity'](child['pid']) is None
        receipt = json.loads((output / 'jobs/one/attempt-0001/receipt.json').read_text())
        assert receipt['exit'] == -signal.SIGKILL
        assert not json.loads((output / 'progress.json').read_text())['ready_for_comparison']
        assert not (output / 'manifest.json').exists()
    finally:
        if marker.exists():
            try:
                os.killpg(json.loads(marker.read_text())['group'], signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_worker_completion_is_atomic_and_durable_before_replace(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / 'tools'))
    worker = runpy.run_path(str(REPO / 'tools/generate_neutral_quantum.py'))
    path = tmp_path / 'record.json'
    path.write_text('{"status":"previous"}\n')
    original = path.read_bytes()
    synced = []
    actual_sync = os.fsync

    def trace(fd):
        synced.append(os.readlink(f'/proc/self/fd/{fd}'))
        actual_sync(fd)

    def interrupt(source, target):
        assert str(source) in synced, 'Completed bytes were not synced before rename'
        raise OSError('simulated interruption before replace')

    monkeypatch.setattr(os, 'fsync', trace)
    monkeypatch.setattr(os, 'replace', interrupt)
    with pytest.raises(OSError, match='simulated interruption'):
        worker['dump'](path, {'status': 'computed'})
    assert path.read_bytes() == original


def test_missing_promoted_copy_is_restored_from_validated_attempt(synthetic):
    assert UNIT['run_synthetic'](synthetic).returncode == 0
    output = synthetic[-1]
    target = output / 'records/two.json'
    original = UNIT['sha'](target)
    target.unlink()
    result = UNIT['run_synthetic'](synthetic)
    assert result.returncode == 0, result.stderr
    assert UNIT['sha'](target) == original
    assert len(list(output.glob('jobs/two/attempt-*'))) == 1
