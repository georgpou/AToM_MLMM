"""Deterministic, finite JSON artifacts with atomic replacement."""
import json
import os
from pathlib import Path
import tempfile
import hashlib
import re


def write_json(path, document):
    text = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + '\n'
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_json(path):
    def reject_constant(value):
        raise ValueError(f'nonfinite JSON constant: {value}')
    return json.loads(Path(path).read_text(), parse_constant=reject_constant)


def commit_sample_chunk(directory, index, record, state_xml, checkpoint):
    """Single-controller immutable sample + State/checkpoint transaction.

    A directory rename publishes only complete hash-bound chunks. Failed pending
    trees remain inspectable; no interrupted output is silently discarded.
    """
    if isinstance(index,bool) or not isinstance(index,int) or not 0 <= index < 1000000:
        raise ValueError('sample index must be a nonnegative six-digit integer')
    directory = Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    target = directory/f'{index:06d}'
    if target.exists():
        raise FileExistsError(f'immutable sample already exists: {target}')
    pending = Path(tempfile.mkdtemp(prefix=f'.pending-{index:06d}-',dir=directory))
    write_json(pending/'record.json',record)
    (pending/'state.xml').write_text(state_xml)
    (pending/'checkpoint.chk').write_bytes(checkpoint)
    files = {name:hashlib.sha256((pending/name).read_bytes()).hexdigest()
             for name in ('record.json','state.xml','checkpoint.chk')}
    write_json(pending/'manifest.json',{'version':1,'index':index,'files':files})
    for path in pending.iterdir():
        with path.open('rb') as handle:
            os.fsync(handle.fileno())
    descriptor = os.open(pending,os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if target.exists():
        raise FileExistsError(f'immutable sample appeared during transaction: {target}')
    os.rename(pending,target)
    descriptor = os.open(directory,os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return target


def read_sample_chunks(directory):
    """Verify committed prefix and reject incomplete/potentially lost records."""
    from .schema import IdentityError
    directory = Path(directory)
    if not directory.exists():
        return []
    pending = sorted(directory.glob('.pending-*'))
    if pending:
        raise IdentityError(f'incomplete sample transaction preserved for inspection: {pending[0]}')
    paths = sorted(directory.iterdir())
    if any(not re.fullmatch(r'\d{6}',p.name) or not p.is_dir() for p in paths):
        raise IdentityError('unrecognized sample journal entry; preserve and inspect before resuming')
    records, ids, sequences = [], set(), {}
    for index,path in enumerate(paths):
        manifest = read_json(path/'manifest.json')
        if path.name != f'{index:06d}' or manifest.get('version') != 1 or manifest.get('index') != index:
            raise IdentityError('sample journal has missing/reordered transaction identities')
        if set(manifest['files']) != {'record.json','state.xml','checkpoint.chk'}:
            raise IdentityError('sample journal must bind all record/State/checkpoint artifacts')
        for name,digest in manifest['files'].items():
            if hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
                raise IdentityError(f'sample journal artifact mismatch: {path/name}')
        record = read_json(path/'record.json')
        sample,walker,sequence = record['sample_id'],record['walker_id'],record['sequence_number']
        if sample in ids or sequence <= sequences.get(walker,-1):
            raise IdentityError('duplicate sample identity or nonincreasing walker sequence')
        ids.add(sample)
        sequences[walker] = sequence
        records.append(record)
    return records
