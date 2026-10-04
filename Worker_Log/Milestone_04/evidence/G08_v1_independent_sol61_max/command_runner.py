"""Run one scientific command and preserve argv, output, resources and status."""
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

out = Path(__file__).resolve().parent
name, *cmd = sys.argv[1:]
start = datetime.now(timezone.utc).isoformat()
events_before = Path('/sys/fs/cgroup/memory.events').read_text()
t0 = time.monotonic()
with (out/f'{name}.stdout').open('w') as stdout, (out/f'{name}.stderr').open('w') as stderr:
    result = subprocess.run(cmd, stdout=stdout, stderr=stderr)
metadata = dict(command=cmd, cwd=str(Path.cwd()), started=start,
                finished=datetime.now(timezone.utc).isoformat(), exit_code=result.returncode,
                wall_seconds=time.monotonic()-t0,
                maximum_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                memory_events_before=events_before,
                memory_events_after=Path('/sys/fs/cgroup/memory.events').read_text())
(out/f'{name}.result.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(json.dumps(metadata, indent=2))
raise SystemExit(result.returncode)
