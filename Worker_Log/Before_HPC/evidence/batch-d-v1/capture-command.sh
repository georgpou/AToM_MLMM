#!/usr/bin/env bash
set -uo pipefail

cd /workspace/AToM_MLMM-before-HPC
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"

if [[ $# -lt 2 ]]; then
  echo "usage: capture-command.sh NAME COMMAND [ARG ...]" >&2
  exit 64
fi

name="$1"
shift
evidence="Worker_Log/Before_HPC/evidence/batch-d-v1"
mkdir -p "$evidence"
log="$evidence/$name.log"
receipt="$evidence/$name.json"
start_utc="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
head="$(git rev-parse HEAD)"
activation_sha256="$(sha256sum /workspace/before-hpc-cpu-v2/activate.sh | awk '{print $1}')"

python - "$receipt" "$start_utc" "$head" "$activation_sha256" "$@" <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys

receipt, start, head, activation, *argv = sys.argv[1:]
root = Path('/workspace/AToM_MLMM-before-HPC')
changed = subprocess.check_output(
    ['git', 'diff', '--name-only', 'HEAD'], cwd=root, text=True
).splitlines()
untracked = subprocess.check_output(
    ['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=root
).decode().split('\0')
paths = sorted({p for p in changed + untracked if p.startswith(('src/', 'tools/', 'tests/', 'fixtures/'))})
rows = []
for relative in paths:
    path = root / relative
    if path.is_file():
        rows.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
payload = ''.join(f'{path}\0{digest}\n' for path, digest in rows).encode()
source_identity = hashlib.sha256((head + '\0').encode() + payload).hexdigest()
document = {
    'argv': argv,
    'cwd': str(root),
    'start_utc': start,
    'head': head,
    'source_patch_identity_sha256': source_identity,
    'source_files': dict(rows),
    'activation_script': '/workspace/before-hpc-cpu-v2/activate.sh',
    'activation_script_sha256': activation,
    'environment': {
        'OPENBLAS_NUM_THREADS': '2',
        'OMP_NUM_THREADS': '2',
        'MKL_NUM_THREADS': '2',
        'PYTHONPATH': str(root / 'src'),
        'memory_limit': '8 GiB cgroup',
    },
}
Path(receipt).write_text(json.dumps(document, indent=2, sort_keys=True) + '\n')
PY

set +e
"$@" >"$log" 2>&1
exit_code=$?
set -e
end_utc="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

python - "$receipt" "$log" "$end_utc" "$exit_code" <<'PY'
import json
from pathlib import Path
import re
import sys

receipt, log, end, exit_code = sys.argv[1:]
document = json.loads(Path(receipt).read_text())
lines = Path(log).read_text(errors='replace').splitlines()
summary = next((line.strip() for line in reversed(lines)
                if re.search(r'\b\d+ passed\b|\b\d+ failed\b|\b\d+ error', line)), '')
counts = {}
for key, pattern in (
    ('passed', r'(\d+) passed'), ('failed', r'(\d+) failed'),
    ('skipped', r'(\d+) skipped'), ('deselected', r'(\d+) deselected'),
    ('errors', r'(\d+) error(?:s)?'),
):
    match = re.search(pattern, summary)
    counts[key] = int(match.group(1)) if match else 0
document.update({
    'end_utc': end,
    'exit_code': int(exit_code),
    'log': str(Path(log)),
    'pytest_summary': summary or None,
    'pytest_counts': counts,
})
Path(receipt).write_text(json.dumps(document, indent=2, sort_keys=True) + '\n')
print(json.dumps({
    'receipt': str(Path(receipt)), 'log': str(Path(log)),
    'exit_code': int(exit_code), 'pytest_summary': summary or None,
}, sort_keys=True))
PY

exit "$exit_code"
