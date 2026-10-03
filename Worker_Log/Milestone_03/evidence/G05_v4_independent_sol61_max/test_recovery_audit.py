"""Independent expected-contract probes. Only synthetic worker stubs are run.

These are intentionally outside the submitted test/source tree. All durable
probe artifacts are new reviewer evidence; no real quantum executable is used.
"""
from pathlib import Path
import json
import os
import runpy
import signal
import subprocess
import sys
import time

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
UNIT = runpy.run_path(str(REPO / 'tests/unit/test_quantum_recovery.py'))


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def fixture(name):
    path = HERE / 'recovery-probes' / name
    path.mkdir(parents=True, exist_ok=False)
    return UNIT['synthetic'].__wrapped__(path)


def mutate_new_worker(synthetic, suffix='', prefix=''):
    original = synthetic[2]
    replacement = original.with_name('audit-worker')
    text = original.read_text()
    header, body = text.split('\n', 1)
    with replacement.open('x') as stream:
        stream.write(header + '\n' + prefix + body + suffix)
    replacement.chmod(0o755)
    return (*synthetic[:2], replacement, synthetic[3])


def test_resume_must_not_promote_a_known_nonzero_computed_record():
    synthetic = fixture('known-nonzero')
    synthetic = mutate_new_worker(synthetic, suffix="\nif name=='two':sys.exit(23)\n")
    first = UNIT['run_synthetic'](synthetic)
    output = synthetic[-1]
    receipt_path = output / 'jobs/two/attempt-0001/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    assert first.returncode == 1 and receipt['exit'] == 23
    assert json.loads((receipt_path.parent/'record.json').read_text())['status']=='computed'
    second = UNIT['run_synthetic'](synthetic)
    state = json.loads((output/'progress.json').read_text())
    write_new(output.parent/'observed.json', {
        'first_exit': first.returncode, 'authoritative_worker_exit': receipt['exit'],
        'resume_exit': second.returncode, 'resume_stdout':second.stdout,
        'two_provenance_after_resume':state['provenance'].get('two'),
        'ready_for_comparison':state['ready_for_comparison'],
        'two_attempt_count':len(list(output.glob('jobs/two/attempt-*'))),
        'requirement':'known failed exits must remain failed; unknown is only for genuinely missing receipts',
    })
    assert not state['ready_for_comparison'], 'Known exit 23 was changed to unknown and admitted without retry'


def test_recovery_must_refuse_worker_spawned_before_first_identity_checkpoint():
    synthetic = fixture('spawn-checkpoint-gap')
    marker = synthetic[-1].parent/'first-worker.json'
    prefix = (
        "from pathlib import Path\nimport os,time,json\n"
        f"marker=Path({str(marker)!r})\n"
        "if not marker.exists():\n"
        "    marker.write_text(json.dumps({'pid':os.getpid(),'note':'SYNTHETIC NON-QM WORKER'}))\n"
        "    time.sleep(30)\n"
    )
    synthetic = mutate_new_worker(synthetic, prefix=prefix)
    root, approval, executable, output = synthetic
    launcher = output.parent/'crash_launcher.py'
    code = (
        "import argparse,os,runpy,subprocess,sys\n"
        f"sys.path.insert(0,{str(REPO/'tools')!r})\n"
        f"functions=runpy.run_path({str(REPO/'tools/resume_neutral_quantum.py')!r})\n"
        "real_popen=subprocess.Popen\n"
        "def crash_after_spawn(*args,**kwargs):\n"
        "    worker=real_popen(*args,**kwargs)\n"
        "    os._exit(99)\n"
        "subprocess.Popen=crash_after_spawn\n"
        f"args=argparse.Namespace(plan_root={str(root)!r},approval={str(approval)!r},output={str(output)!r},reference_python={str(executable)!r},resume_from=None,stop_state=None,prior_launch=None,check_resume=False,memory_gib=3.,wall_limit_seconds=None)\n"
        "functions['run'](args)\n"
    )
    launcher.open('x').write(code)
    first = subprocess.run([sys.executable,str(launcher)],capture_output=True,text=True)
    assert first.returncode==99
    deadline=time.monotonic()+5
    while not marker.exists() and time.monotonic()<deadline:time.sleep(.01)
    assert marker.exists(),'synthetic worker failed to start'
    pid=json.loads(marker.read_text())['pid']
    before=json.loads((output/'progress.json').read_text())
    sys.path.insert(0,str(REPO/'tools'))
    recovery=runpy.run_path(str(REPO/'tools/resume_neutral_quantum.py'))
    try:
        assert recovery['process_identity'](pid) is not None
        second=UNIT['run_synthetic'](synthetic)
        state=json.loads((output/'progress.json').read_text())
        alive=recovery['process_identity'](pid) is not None
        write_new(output.parent/'observed.json', {
            'first_coordinator_exit':first.returncode,
            'old_worker_pid':pid,'old_worker_live_at_resume_end':alive,
            'last_durable_session_before_resume':before['sessions'][-1],
            'resume_exit':second.returncode,'resume_stdout':second.stdout,
            'ready_for_comparison':state['ready_for_comparison'],
            'one_attempt_count':len(list(output.glob('jobs/one/attempt-*'))),
            'requirement':'spawned but not checkpointed live worker must block concurrent recovery',
        })
        assert second.returncode==2, 'Recovery launched duplicate work while the original worker was live'
    finally:
        try:os.killpg(pid,signal.SIGKILL)
        except ProcessLookupError:pass


def test_recovery_must_not_make_progress_durable_before_record_data(monkeypatch):
    synthetic=fixture('record-fsync-order')
    root,approval,executable,output=synthetic
    sys.path.insert(0,str(REPO/'tools'))
    recovery=runpy.run_path(str(REPO/'tools/resume_neutral_quantum.py'))
    actual_fsync=os.fsync
    events=[]
    def trace_fsync(descriptor):
        try:target=os.readlink(f'/proc/self/fd/{descriptor}')
        except OSError:target='<unresolved>'
        events.append({'target':target,'sequence':len(events)})
        actual_fsync(descriptor)
    monkeypatch.setattr(os,'fsync',trace_fsync)
    from argparse import Namespace
    args=Namespace(plan_root=str(root),approval=str(approval),output=str(output),reference_python=str(executable),resume_from=None,stop_state=None,prior_launch=None,check_resume=False,memory_gib=3.,wall_limit_seconds=None)
    assert recovery['run'](args)==0
    write_new(output.parent/'observed.json', {'fsync_events':events,'requirement':'fsync record files and containing directories before a durable checkpoint references them'})
    record_sync=[e for e in events if e['target'].endswith('/records/one.json')]
    assert record_sync, 'Record bytes were not fsynced before atomic progress checkpoint'
