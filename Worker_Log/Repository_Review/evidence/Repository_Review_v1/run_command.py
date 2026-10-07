"""Serial audit command recorder; does not modify reviewed code or failures."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
label, *command = sys.argv[1:]
if not command or (root / (label + '.json')).exists():
    raise SystemExit('supply a fresh label and command')
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
tic = time.monotonic()
log = root / (label + '.log')
with log.open('xb') as output:
    result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
record = {
    'command': command, 'cwd': str(Path.cwd()), 'start_utc': start,
    'end_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - tic,
    'peak_child_rss_bytes': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
    'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'environment_prefix': os.environ.get('ATOM_MLMM_SETUP_ROOT'),
    'python_executable': sys.executable,
    'thread_settings': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')},
    'pythonpath': os.environ.get('PYTHONPATH'),
    'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
}
(root / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
print(log.read_text(errors='replace')[-3500:])
raise SystemExit(result.returncode)
