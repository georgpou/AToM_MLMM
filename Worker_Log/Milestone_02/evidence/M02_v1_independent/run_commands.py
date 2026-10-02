"""Independent review command capture; does not alter implementation inputs."""
import datetime
import gzip
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parent
PREFIX = pathlib.Path('/workspace/.onboarding/atom-mlmm-m02')
commands = [
    ('g02', [sys.executable, '-m', 'pytest', 'tests/integration/test_pythonforce_atm.py', 'tests/contracts/test_transfer_protocols.py', 'tests/contracts/test_physical_evaluator.py', 'tests/contracts/test_fault_injection.py', '-v'], ROOT),
    ('g03', [sys.executable, '-m', 'pytest', 'tests/workflow/test_atom_force_routing.py', 'tests/workflow/test_active_force_groups.py', '-v'], ROOT),
    ('full', [sys.executable, '-m', 'pytest', '-q'], ROOT),
    ('analytic', [sys.executable, '-m', 'pytest', '-m', 'not gpu and not model_assets and not slow', '-q'], ROOT),
    ('strict', [sys.executable, str(PREFIX/'validate.py'), '--repository', str(ROOT)], ROOT),
    ('upstream', [sys.executable, '-m', 'pytest', '-q', 'tests/test_uwham.py'], PREFIX/'sources'/'AToM-OpenMM'),
    ('docs', [sys.executable, 'tools/check_docs.py', '--self-test'], ROOT),
    ('whitespace', ['git', 'diff', '--check'], ROOT),
]
records = []
for name, command, cwd in commands:
    start = datetime.datetime.now(datetime.timezone.utc)
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    record = {'name': name, 'command': command, 'cwd': str(cwd), 'started_utc': start.isoformat(), 'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exit_code': result.returncode, 'output': result.stdout}
    records.append(record)
    with gzip.open(OUT/'command-results.json.gz', 'wt') as stream:
        json.dump(records, stream, indent=2)
    print(name, 'exit', result.returncode, result.stdout[-400:].strip(), flush=True)
if any(item['exit_code'] for item in records):
    sys.exit(1)
