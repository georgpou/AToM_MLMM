"""Verify the exact G09 submission, its scientific manifest, and preservation."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
CHECKOUT=Path('/tmp/atm-mlmm-g09-independent-readonly')
SUBMISSION='9e7a84c91e8c252c33221b8e2331e595d54315ca'
SOURCE='34cc6ba0d3e618450128b4a679ffc64046c48733'
BASE='8692138bac7d7324ac4d2ef13bfb58075b874202'

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root)

def payload(path):
    return os.readlink(path).encode() if path.is_symlink() else path.read_bytes()

assert git(ROOT,'rev-parse','HEAD').decode().strip()==SUBMISSION
assert git(ROOT,'branch','--show-current').decode().strip()=='m04-engine-readiness'
assert git(CHECKOUT,'rev-parse','HEAD').decode().strip()==SUBMISSION
tree=git(ROOT,'ls-tree','-rz',SUBMISSION).split(b'\0')
counts={}
for root in (ROOT,CHECKOUT):
    count=0
    for row in tree:
        if not row:continue
        header,name=row.split(b'\t',1)
        mode,kind,blob=header.split()
        assert kind==b'blob'
        actual=payload(root/name.decode())
        assert hashlib.sha1(b'blob '+str(len(actual)).encode()+b'\0'+actual).hexdigest()==blob.decode(),name.decode()
        count+=1
    counts[str(root)]=count
manifest=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v1/source-input-test-manifest.json').read_text())
for name,digest in manifest['files'].items():
    actual=payload(ROOT/name)
    assert hashlib.sha256(actual).hexdigest()==digest,name
    assert git(ROOT,'show',SOURCE+':'+name)==actual,name
assert len(manifest['files'])==110
reports=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v1/retained-g08-reports.json').read_text())
for name,digest in reports.items():
    assert hashlib.sha256(payload(ROOT/name)).hexdigest()==digest,name
    assert git(ROOT,'show',BASE+':'+name)==payload(ROOT/name),name
assert not git(ROOT,'diff','--name-only',BASE,SUBMISSION,'--','Worker_Log/Milestone_04')
result=dict(submission=SUBMISSION,source=SOURCE,base=BASE,
            tree=git(ROOT,'rev-parse',SUBMISSION+'^{tree}').decode().strip(),
            all_tracked_blobs_verified=counts,scientific_manifest_files=110,
            all_prior_m04_artifacts_unchanged=True,
            source_to_submission=git(ROOT,'diff','--name-only',SOURCE,SUBMISSION).decode().splitlines(),
            cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
            memory_max=Path('/sys/fs/cgroup/memory.max').read_text().strip(),
            swap=Path('/proc/swaps').read_text().strip(),
            memory_events=Path('/sys/fs/cgroup/memory.events').read_text().strip(),
            timestamp=datetime.now(timezone.utc).isoformat())
target='closing-preservation.json' if len(sys.argv)>1 and sys.argv[1]=='closing' else 'snapshot-check.json'
(OUT/target).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='source_to_submission'},indent=2))
