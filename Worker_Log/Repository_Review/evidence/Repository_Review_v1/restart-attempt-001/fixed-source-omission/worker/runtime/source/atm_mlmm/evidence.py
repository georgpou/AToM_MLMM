"""Inert hash verification and complete evidence copies at quiescent safe points.

Keep the active journal on local storage. A durable copy is a sealed snapshot,
not a transactional journal and not permission to deserialize executable assets.
"""
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

from .persistence import read_json, write_json
from .schema import IdentityError

MANIFEST = '.evidence.json'


def _tree(root, *, sealed=False):
    if root.is_symlink() or not root.is_dir():
        raise IdentityError('evidence root must be a directory without symlinks')
    files, directories = {}, []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise IdentityError(f'evidence symlink is not admitted: {path}')
        name = path.relative_to(root).as_posix()
        if sealed and name == MANIFEST:
            continue
        if path.is_dir():
            directories.append(name)
        elif path.is_file():
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            raise IdentityError(f'evidence entry is not a regular file/directory: {name}')
    return {'version':1, 'files':files, 'directories':directories}


def _safe_name(name):
    return (isinstance(name,str) and bool(name) and '\\' not in name and
            not PurePosixPath(name).is_absolute() and
            all(part not in ('.','..','') for part in name.split('/')))


def verify_evidence(directory):
    """Verify exact files, empty directories and hashes without trusted loading."""
    directory = Path(directory)
    if (directory/MANIFEST).is_symlink():
        raise IdentityError('evidence manifest symlink is not admitted')
    document = read_json(directory/MANIFEST)
    if (not isinstance(document,dict) or set(document) != {'version','files','directories'}
            or type(document['version']) is not int or document['version'] != 1
            or not isinstance(document['files'],dict) or not isinstance(document['directories'],list)):
        raise IdentityError('unsupported evidence manifest identity')
    if any(not _safe_name(name) or name == MANIFEST for name in document['files']) or any(
            not _safe_name(name) for name in document['directories']):
        raise IdentityError('unsafe evidence manifest path')
    if any(not isinstance(d,str) or not re.fullmatch('[0-9a-f]{64}',d)
           for d in document['files'].values()):
        raise IdentityError('invalid evidence hash identity')
    if _tree(directory,sealed=True) != document:
        raise IdentityError('evidence file/directory/hash identity mismatch')
    return document


def export_evidence(source, destination):
    """Copy, verify and publish a complete safe-point snapshot; never delete input.

    Destination must be unused. Failed partial copies remain in a named sibling
    pending directory for inspection. Caller must stop active writers first.
    """
    source, destination = Path(source), Path(destination)
    if source.is_symlink():
        raise IdentityError('evidence source symlink is not admitted')
    source, destination = source.resolve(), destination.absolute()
    resolved_destination = destination.resolve()
    if (resolved_destination == source or source in resolved_destination.parents
            or resolved_destination in source.parents):
        raise IdentityError('evidence source/destination overlap; copy cannot be inside source')
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f'evidence destination already exists: {destination}')
    before = _tree(source)
    if MANIFEST in before['files']:
        raise IdentityError('source already has an evidence seal; verify and copy that sealed tree explicitly')
    destination.parent.mkdir(parents=True,exist_ok=True)
    pending = Path(tempfile.mkdtemp(prefix='.pending-export-',dir=destination.parent))
    try:
        for name in before['directories']:
            (pending/name).mkdir(parents=True,exist_ok=True)
        for name in before['files']:
            shutil.copy2(source/name,pending/name)
        if _tree(source) != before or _tree(pending) != before:
            raise IdentityError('source changed or partial evidence copy identity mismatch')
        write_json(pending/MANIFEST,before)
        verify_evidence(pending)
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f'evidence destination appeared during copy: {destination}')
        os.rename(pending,destination)
        return verify_evidence(destination)
    except Exception as error:
        error.add_note(f'Partial evidence preserved at {pending}; local source remains at {source}')
        raise
