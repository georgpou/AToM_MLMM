"""Capture a new worker check without overwriting any existing evidence."""
import datetime
import gzip
import json
from pathlib import Path
import subprocess
import sys

target = Path(__file__).with_name(sys.argv[1] + '.json.gz')
if target.exists():
    raise SystemExit(f'refusing to overwrite evidence: {target}')
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
command = sys.argv[2:]
result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
record = dict(command=command, cwd=str(Path.cwd()), started_utc=started,
              finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True,
                                           cwd=Path(__file__).resolve().parents[4]).strip(),
              exit_code=result.returncode, output=result.stdout)
with gzip.open(target, 'wt') as stream:
    json.dump(record, stream, indent=2)
print(result.stdout[-3500:], end='')
print(f'Captured exit {result.returncode}: {target.name}', flush=True)
sys.exit(result.returncode)
