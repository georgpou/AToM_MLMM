
import os, runpy, sys
from argparse import Namespace
from pathlib import Path
sys.path.insert(0, '/workspace/AToM_MLMM/tools')
functions = runpy.run_path('/workspace/AToM_MLMM/tools/resume_neutral_quantum.py')
namespace = functions['run'].__globals__
original_receipt = namespace['exclusive_dump']
def receipt(path, data):
    original_receipt(path, data)
    if 'promotion' == 'receipt' and Path(path).name == 'receipt.json': os._exit(99)
namespace['exclusive_dump'] = receipt
original_publish = namespace['publish_record']
def publish(source, target):
    original_publish(source, target)
    if 'promotion' == 'promotion': os._exit(99)
namespace['publish_record'] = publish
original_checkpoint = namespace['atomic_dump']
def checkpoint(path, data):
    original_checkpoint(path, data)
    if 'promotion' == 'progress' and Path(path).name == 'progress.json' and data['record_hashes']: os._exit(99)
namespace['atomic_dump'] = checkpoint
functions['run'](Namespace(**{'plan_root': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_completion_boundary_crash1/plan', 'approval': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_completion_boundary_crash1/approval.json', 'output': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_completion_boundary_crash1/output', 'reference_python': '/workspace/AToM_MLMM/Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/pytest-repaired/test_completion_boundary_crash1/reference/bin/python', 'resume_from': None, 'stop_state': None, 'prior_launch': None, 'check_resume': False, 'memory_gib': 3.0, 'wall_limit_seconds': None}))
