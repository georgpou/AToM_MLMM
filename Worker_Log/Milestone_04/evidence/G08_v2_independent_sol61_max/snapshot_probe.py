"""Verify exact v2 Git blobs/manifests and unchanged v1 evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

out=Path(__file__).resolve().parent
root=out.parents[3]
submission='c0280818ad18fa5e95a022eccc892e2310a41721'
source='8cf2494424d796fc3fc393e25b00e05b6281a85f'
base=subprocess.check_output(['git','rev-parse','89eb8b9'],cwd=root).decode().strip()
def git(*args):
    return subprocess.check_output(['git',*args],cwd=root)
def data(path):
    return os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
assert git('rev-parse','HEAD').decode().strip()==submission
assert git('branch','--show-current').decode().strip()=='m04-engine-readiness'
closing=len(sys.argv)>1 and sys.argv[1]=='closing'
if closing:
    frozen=json.loads((out/'frozen-tracked-manifest.json').read_text())
    for entry in frozen:
        actual=data(root/entry['path'])
        assert len(actual)==entry['bytes'] and hashlib.sha256(actual).hexdigest()==entry['sha256'],entry['path']
    result=dict(submission=submission,unchanged_tracked_files=len(frozen),timestamp=datetime.now(timezone.utc).isoformat())
    target='closing-preservation.json'
else:
    manifest=json.loads((root/'Worker_Log/Milestone_04/evidence/G08_v2/source-test-manifest.json').read_text())
    for entry in manifest:
        actual=data(root/entry['path'])
        assert len(actual)==entry['bytes'] and hashlib.sha256(actual).hexdigest()==entry['sha256'],entry['path']
        assert git('show',source+':'+entry['path'])==actual,entry['path']
        assert git('show',submission+':'+entry['path'])==actual,entry['path']
    frozen=[]
    for row in git('ls-tree','-rz',submission).split(b'\0'):
        if not row:continue
        metadata,path=row.split(b'\t',1)
        mode,kind,blob=metadata.split()
        assert kind==b'blob'
        path=path.decode()
        actual=data(root/path)
        actual_blob=hashlib.sha1(b'blob '+str(len(actual)).encode()+b'\0'+actual).hexdigest()
        assert actual_blob==blob.decode(),path
        frozen.append(dict(path=path,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest()))
    preserved=git('diff','--name-only',base,submission,'--',
                  'Worker_Log/Milestone_04/Gate_08_v1_audit.md','Worker_Log/Milestone_04/Gate_08_v1_worker.md',
                  'Worker_Log/Milestone_04/evidence/G08_v1','Worker_Log/Milestone_04/evidence/G08_v1_independent_sol61_max')
    assert not preserved,preserved.decode()
    for ancestor in (base,source,'6015a652c4a9a9c968ab7933c07ac7bbb4573e12'):
        assert subprocess.run(['git','merge-base','--is-ancestor',ancestor,submission],cwd=root).returncode==0
    (out/'frozen-tracked-manifest.json').write_text(json.dumps(frozen,indent=2)+'\n')
    result=dict(submission=submission,source=source,base=base,branch='m04-engine-readiness',
                tree=git('rev-parse',submission+'^{tree}').decode().strip(),
                scientific_manifest_files=len(manifest),all_tracked_files=len(frozen),v1_evidence_unchanged=True,
                source_to_submission=git('diff','--name-only',source,submission).decode().splitlines(),
                base_to_source=git('diff','--name-only',base,source).decode().splitlines(),
                timestamp=datetime.now(timezone.utc).isoformat())
    target='snapshot-check.json'
result.update(cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
              memory_max=Path('/sys/fs/cgroup/memory.max').read_text().strip(),
              swap=Path('/proc/swaps').read_text().strip(),
              memory_events=Path('/sys/fs/cgroup/memory.events').read_text().strip())
(out/target).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
