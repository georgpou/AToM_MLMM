"""Local single-controller round transactions and strict inert prefix validation."""
from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path
import re
import uuid

from .persistence import read_json,write_json
from .schema import IdentityError


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sync_directory(path):
    fd=os.open(path,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


@contextmanager
def controller_lock(directory):
    with (Path(directory)/'.controller.lock').open('a') as handle:
        try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise IdentityError('another exchange controller owns this local attempt') from error
        try: yield
        finally: fcntl.flock(handle,fcntl.LOCK_UN)


def seal(directory, *, index=None):
    files={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file()}
    write_json(directory/'manifest.json',{'version':1,'index':index,'files':files})
    for p in directory.iterdir():
        with p.open('rb') as handle: os.fsync(handle.fileno())
    sync_directory(directory)
    return sha(directory/'manifest.json')


def verify(directory, *, index=None):
    if directory.is_symlink() or not directory.is_dir():
        raise IdentityError('exchange transaction directory identity mismatch')
    manifest=read_json(directory/'manifest.json')
    required={'record.json','rng.json','worker-0.xml','worker-1.xml','worker-0.chk','worker-1.chk'}
    if index is not None: required |= {'evaluated.json','decision.json','refreshed.json'}
    if (manifest.get('version')!=1 or manifest.get('index')!=index or
            set(manifest.get('files',{}))!=required or
            {p.name for p in directory.iterdir()}!=required|{'manifest.json'}):
        raise IdentityError('exchange transaction complete artifact identity mismatch')
    for name,digest in manifest['files'].items():
        path=directory/name
        if path.is_symlink() or not path.is_file() or sha(path)!=digest:
            raise IdentityError(f'exchange transaction hash mismatch: {path}')
    return manifest


def read_exchange_rounds(directory, *, allow_pending=False):
    """Return hash/identity/history-verified committed records; never load code."""
    directory=Path(directory)
    if sha(directory/'metadata.json')!=(directory/'metadata.sha256').read_text().strip():
        raise IdentityError('exchange metadata hash mismatch')
    metadata=read_json(directory/'metadata.json')
    initial=directory/'initial'
    verify(initial)
    previous=sha(initial/'manifest.json')
    if previous!=metadata['initial_manifest_sha256']:
        raise IdentityError('exchange initial boundary identity mismatch')
    initial_record=read_json(initial/'record.json')
    states=list(metadata['initial_state_ids'])
    walkers=metadata['walker_ids']
    if initial_record['state_ids']!=states or initial_record['walker_ids']!=walkers:
        raise IdentityError('exchange initial worker/state identity mismatch')
    rounds=directory/'rounds'
    paths=sorted(rounds.iterdir())
    pending=[p for p in paths if p.name.startswith('.pending-')]
    if pending and not allow_pending:
        raise IdentityError('incomplete exchange transaction preserved; inspect before explicit rollback/replay')
    paths=[p for p in paths if p not in pending]
    if any(not re.fullmatch(r'\d{6}',p.name) for p in paths):
        raise IdentityError('unrecognized exchange journal entry')
    if len(paths)>metadata['rounds']:
        raise IdentityError('exchange journal exceeds declared rounds')
    rows=[]; sample_ids=set()
    for index,path in enumerate(paths):
        if path.name!=f'{index:06d}': raise IdentityError('missing/reordered exchange round')
        manifest=verify(path,index=index)
        row=read_json(path/'record.json'); report=row['exchange']
        expected_after=list(reversed(states)) if report['accepted'] is True else states
        if (type(report['accepted']) is not bool or row['round_index']!=index or
            row['previous_manifest_sha256']!=previous or report['state_ids_before']!=states or
            report['state_ids_after']!=expected_after or report['walker_ids']!=walkers or
            len(row['samples'])!=2 or row['state_ids_after']!=expected_after or
            row['rng_before_sha256']!=sha((initial if index==0 else paths[index-1])/'rng.json')):
            raise IdentityError('exchange state/walker/RNG history identity mismatch')
        for w,sample in enumerate(row['samples']):
            expected=f"{metadata['run_id']}:walker-{w}:round-{index+1}"
            if (sample['sample_id']!=expected or sample['sample_id'] in sample_ids or
                sample['walker_id']!=walkers[w] or sample['state_id']!=states[w] or
                sample['sequence_number']!=index+1):
                raise IdentityError('exchange sample/sequence identity mismatch')
            sample_ids.add(sample['sample_id'])
        evaluated=read_json(path/'evaluated.json'); decision=read_json(path/'decision.json')
        if (read_json(path/'refreshed.json')!=report or
            any(evaluated[k]!=report[k] for k in evaluated) or
            any(decision[k]!=report[k] for k in decision)):
            raise IdentityError('exchange decision/refresh history mismatch')
        previous=sha(path/'manifest.json'); states=expected_after; rows.append(row)
    return rows


def preserve_pending(directory):
    """Explicit rollback: retain whole incomplete trees and their inert hashes."""
    directory=Path(directory)
    for pending in sorted((directory/'rounds').glob('.pending-*')):
        target=directory/'failures'/f'rollback-{uuid.uuid4().hex}'
        target.parent.mkdir(exist_ok=True)
        files={str(p.relative_to(pending)):sha(p) for p in pending.rglob('*') if p.is_file()}
        write_json(pending/'rollback.json',{'policy':'replay from last committed checkpoints and both host RNG streams',
            'original_pending_name':pending.name,'preserved_file_hashes':files})
        os.rename(pending,target)
        sync_directory(target.parent); sync_directory(directory/'rounds')
