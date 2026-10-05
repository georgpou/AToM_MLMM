"""Verify exact v2 submission, scientific inputs and all retained evidence."""
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
CLONE=Path('/tmp/atm-mlmm-g09-v2-independent-readonly')
SUBMISSION='9fe93357f0852d7c018ab41923cc0d58cb0615e1'
SOURCE='3246f0cbd6f66702e4b196bace593efba776a25e'
BASE='3fc194dc84bc3711a21ec88812fa7442e4d84d0e'
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root)
def data(path):return os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
assert git(ROOT,'branch','--show-current').decode().strip()=='m04-engine-readiness'
counts={}
for root in (ROOT,CLONE):
    assert git(root,'rev-parse','HEAD').decode().strip()==SUBMISSION
    count=0
    for row in git(root,'ls-tree','-rz',SUBMISSION).split(b'\0'):
        if not row:continue
        header,name=row.split(b'\t',1);mode,kind,blob=header.split()
        assert kind==b'blob'
        actual=data(root/name.decode())
        assert hashlib.sha1(b'blob '+str(len(actual)).encode()+b'\0'+actual).hexdigest()==blob.decode(),name.decode()
        count+=1
    counts[str(root)]=count
manifest=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v2/source-input-test-manifest.json').read_text())
assert manifest['source_commit']==SOURCE and len(manifest['files'])==111
for name,digest in manifest['files'].items():
    actual=data(ROOT/name)
    assert hashlib.sha256(actual).hexdigest()==digest,name
    assert git(ROOT,'show',SOURCE+':'+name)==actual,name
retained=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v2/retained-submission-manifest.json').read_text())
assert len(retained)==507
for name,digest in retained.items():
    actual=data(ROOT/name)
    assert hashlib.sha256(actual).hexdigest()==digest,name
    assert git(ROOT,'show',BASE+':'+name)==actual,name
paths=['Worker_Log/Milestone_04','Worker_Log/Milestone_05/Gate_09_v1_worker.md',
       'Worker_Log/Milestone_05/Gate_09_v1_audit.md','Worker_Log/Milestone_05/evidence/G09_v1',
       'Worker_Log/Milestone_05/evidence/G09_v1_independent_sol61_max']
assert not git(ROOT,'diff','--name-only',BASE,SUBMISSION,'--',*paths)
result=dict(submission=SUBMISSION,source=SOURCE,base=BASE,
            tree=git(ROOT,'rev-parse',SUBMISSION+'^{tree}').decode().strip(),
            tracked_blobs_verified=counts,scientific_files=111,unchanged_retained_artifacts=507,
            all_v1_m04_artifacts_unchanged=True,
            source_delta=git(ROOT,'diff','--name-only',BASE,SOURCE).decode().splitlines(),
            source_to_submission=git(ROOT,'diff','--name-only',SOURCE,SUBMISSION).decode().splitlines(),
            cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
            memory_max=Path('/sys/fs/cgroup/memory.max').read_text().strip(),
            swap=Path('/proc/swaps').read_text().strip(),
            memory_events=Path('/sys/fs/cgroup/memory.events').read_text().strip(),
            timestamp=datetime.now(timezone.utc).isoformat())
name='closing-preservation.json' if len(sys.argv)>1 and sys.argv[1]=='closing' else 'snapshot-check.json'
(OUT/name).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='source_to_submission'},indent=2))
