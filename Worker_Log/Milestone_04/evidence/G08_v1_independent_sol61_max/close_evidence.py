"""Losslessly archive closed in-repository pytest temp trees and recheck source."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile

out=Path(__file__).resolve().parent
root=out.parents[3]
archives=[]
for name in ('full-pytest-temp','focused-pytest-temp'):
    source=out/name
    entries=[]
    for path in [source,*sorted(source.rglob('*'))]:
        rel=path.relative_to(out).as_posix()
        info=path.lstat()
        entry=dict(path=rel,mode=stat.S_IMODE(info.st_mode))
        if path.is_symlink():
            entry.update(kind='symlink',target=os.readlink(path))
        elif path.is_dir():
            entry.update(kind='directory')
        elif path.is_file():
            data=path.read_bytes()
            entry.update(kind='file',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        else:
            raise RuntimeError('Unexpected temporary node '+rel)
        entries.append(entry)
    archive=out/(name+'.tar.gz')
    with tarfile.open(archive,'w:gz',compresslevel=3) as tar:
        tar.add(source,arcname=name,recursive=True)
    with tarfile.open(archive,'r:gz') as tar:
        members={member.name:member for member in tar.getmembers()}
        assert set(members)=={entry['path'] for entry in entries}
        for entry in entries:
            member=members[entry['path']]
            assert member.mode==entry['mode']
            if entry['kind']=='file':
                data=tar.extractfile(member).read()
                assert (member.isfile() or member.islnk()) and len(data)==entry['bytes']
                assert hashlib.sha256(data).hexdigest()==entry['sha256']
            elif entry['kind']=='symlink':
                assert member.issym() and member.linkname==entry['target']
            else:
                assert member.isdir()
    (out/(name+'.manifest.json')).write_text(json.dumps(entries,indent=2)+'\n')
    archives.append(dict(path=archive.name,nodes=len(entries),bytes=archive.stat().st_size,
                         sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),all_members_verified=True))
    shutil.rmtree(source)  # only this audit's closed, verified temporary tree

frozen=json.loads((out/'frozen-tracked-manifest.json').read_text())
for entry in frozen:
    path=root/entry['path']
    data=os.readlink(path).encode() if entry['kind']=='symlink' else path.read_bytes()
    assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()=='29847120ec99c472580ce23c7b1b317c690c3784'
assert subprocess.check_output(['git','branch','--show-current'],cwd=root).decode().strip()=='m04-engine-readiness'
result=dict(timestamp=datetime.now(timezone.utc).isoformat(),unchanged_tracked_files=len(frozen),
            submission='29847120ec99c472580ce23c7b1b317c690c3784',archives=archives,
            cgroup_memory_events=Path('/sys/fs/cgroup/memory.events').read_text())
(out/'closing-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
