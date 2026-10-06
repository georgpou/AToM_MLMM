"""Record exact independent audit command, UTC, status and raw output."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
label, command = sys.argv[1:]
start = datetime.now(timezone.utc).isoformat()
clock = time.perf_counter()
log = HERE / (label + '.log')
with log.open('wb') as out:
    result = subprocess.run(command, shell=True, executable='/bin/bash',
                            cwd=HERE.parents[3], stdout=out, stderr=subprocess.STDOUT)
entry = dict(label=label, command=command, started_utc=start,
             finished_utc=datetime.now(timezone.utc).isoformat(),
             elapsed_s=time.perf_counter()-clock, exit_status=result.returncode,
             log=log.name, raw_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
             auditor_model='gpt-6.1-sol', reasoning_effort='max',
             scientific_profile='serial CPU 2 threads / 8 GiB')
with (HERE/'commands.jsonl').open('a') as out:
    out.write(json.dumps(entry, sort_keys=True)+'\n')
print(json.dumps(entry, sort_keys=True))
print('\n'.join(log.read_text().splitlines()[-5:]))
sys.exit(result.returncode)
