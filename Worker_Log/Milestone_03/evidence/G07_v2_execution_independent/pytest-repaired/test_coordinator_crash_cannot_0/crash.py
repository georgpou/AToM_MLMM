
import os, runpy, subprocess, sys, time
from argparse import Namespace
from pathlib import Path
sys.path.insert(0, '/workspace/AToM_MLMM/tools')
functions = runpy.run_path('/workspace/AToM_MLMM/tools/resume_neutral_quantum.py')
real_popen = subprocess.Popen
def spawn(*args, **kwargs):
    if 'before_spawn' == 'before_spawn': os._exit(99)
    process = real_popen(*args, **kwargs)
    Path('/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/guard.pid').write_text(str(process.pid))
    if 'before_spawn' == 'after_spawn': os._exit(99)
    return process
subprocess.Popen = spawn
real_dump = functions['atomic_dump']
def checkpoint(path, data):
    real_dump(path, data)
    if 'before_spawn' == 'after_identity' and Path(path).name == 'progress.json' and data['sessions'][-1].get('active_worker'):
        os._exit(99)
    active = data.get('sessions', [{}])[-1].get('active_worker')
    if 'before_spawn' == 'after_authorize' and active and not active.get('guarded'):
        deadline = time.monotonic() + 5
        while not Path('/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/child.pid').exists() and time.monotonic() < deadline: time.sleep(.01)
        os._exit(99)
functions['run'].__globals__['atomic_dump'] = checkpoint
real_write = os.write
def authorize(fd, data):
    result = real_write(fd, data)
    if 'before_spawn' == 'after_authorize' and data == b'G':
        deadline = time.monotonic() + 5
        while not Path('/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/child.pid').exists() and time.monotonic() < deadline: time.sleep(.01)
        os._exit(99)
    return result
os.write = authorize
functions['run'](Namespace(**{'plan_root': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/plan', 'approval': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/approval.json', 'output': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/output', 'reference_python': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_coordinator_crash_cannot_0/reference/bin/python', 'resume_from': None, 'stop_state': None, 'prior_launch': None, 'check_resume': False, 'memory_gib': 3.0, 'wall_limit_seconds': None}))
