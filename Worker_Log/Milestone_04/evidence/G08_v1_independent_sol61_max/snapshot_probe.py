"""Independent immutable submission/manifests check, using only stdlib."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SUBMISSION = '29847120ec99c472580ce23c7b1b317c690c3784'
SOURCE = '966a8d61347f65a69f8ba7e6750c4379d4e0503f'
BASE = 'e24e880abcb0353b8f9c2f2e509d6cbb46174f3b'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

manifest = json.loads((ROOT/'Worker_Log/Milestone_04/evidence/G08_v1/source-test-manifest.json').read_text())
md_manifest = json.loads((ROOT/'Worker_Log/Milestone_04/evidence/G08_v1/md-file-manifest.json').read_text())
assert git('rev-parse', 'HEAD').decode().strip() == SUBMISSION
assert git('branch', '--show-current').decode().strip() == 'm04-engine-readiness'
for ancestor in (SOURCE, BASE, '6015a652c4a9a9c968ab7933c07ac7bbb4573e12', 'fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86'):
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, SUBMISSION], cwd=ROOT).returncode == 0
for item in manifest:
    data = (ROOT/item['path']).read_bytes()
    assert len(data) == item['bytes']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    assert git('show', f"{SOURCE}:{item['path']}") == data, item['path']
    assert git('show', f"{SUBMISSION}:{item['path']}") == data, item['path']
if isinstance(md_manifest, dict):
    md_manifest = md_manifest.get('files', md_manifest.get('artifacts'))
for item in md_manifest:
    path = Path(item['path'])
    if not path.is_absolute():
        path = ROOT/path
        if not path.exists():
            path = ROOT/'Worker_Log/Milestone_04/evidence/G08_v1'/item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], item['path']
frozen = []
for path in git('ls-files', '-z').decode().split('\0'):
    if path:
        candidate = ROOT/path
        data = os.readlink(candidate).encode() if candidate.is_symlink() else candidate.read_bytes()
        assert data == git('show', f'{SUBMISSION}:{path}'), path
        frozen.append(dict(path=path, kind='symlink' if candidate.is_symlink() else 'file',
                           bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
result = dict(timestamp=datetime.now(timezone.utc).isoformat(), submission=SUBMISSION,
              source=SOURCE, base=BASE, branch='m04-engine-readiness',
              tree=git('rev-parse', f'{SUBMISSION}^{{tree}}').decode().strip(),
              scientific_manifest_files=len(manifest), original_md_manifest_files=len(md_manifest),
              all_tracked_files=len(frozen), ancestors_verified=True,
              source_to_submission=git('diff', '--name-only', SOURCE, SUBMISSION).decode().splitlines(),
              cgroup_cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
              cgroup_memory_max=Path('/sys/fs/cgroup/memory.max').read_text().strip(),
              cgroup_memory_events=Path('/sys/fs/cgroup/memory.events').read_text().strip(),
              swap=Path('/proc/swaps').read_text().strip())
(OUT/'frozen-tracked-manifest.json').write_text(json.dumps(frozen, indent=2)+'\n')
(OUT/'snapshot-check.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
