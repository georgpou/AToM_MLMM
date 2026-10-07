"""Inert comparison of shared admission with the journal reader's verifier."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from atm_mlmm import exchange_journal
from atm_mlmm.runtime_validation import verify_source_inventory
from atm_mlmm.schema import IdentityError

source = Path(exchange_journal.__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='audit-v2-source-') as temporary:
    root = Path(temporary)
    worker = root/'worker'
    tree = worker/'runtime/source/atm_mlmm'
    files = {}
    for path in sorted(source.rglob('*.py')):
        destination = tree/path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        files[destination.relative_to(worker).as_posix()] = hashlib.sha256(destination.read_bytes()).hexdigest()
    manifest = worker/'manifest.json'
    manifest.write_text(json.dumps({'files': files}, sort_keys=True)+'\n')
    metadata = {'worker_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}
    exchange_journal._verify_multistate_source(root, metadata)
    verify_source_inventory(worker, files, current_source_root=source)
    outcomes = {'declared_modules': len(files), 'matching_tree': 'both_verifiers_accept'}
    extra = tree/'nested/undeclared.py'
    extra.parent.mkdir()
    extra.write_text('INERT_AUDIT_VALUE = 1\n')
    exchange_journal._verify_multistate_source(root, metadata)
    outcomes['undeclared_nested_module_journal_verifier'] = 'accepted'
    try:
        verify_source_inventory(worker, files, current_source_root=source)
    except IdentityError as error:
        outcomes['undeclared_nested_module_shared_verifier'] = str(error)
    else:
        raise AssertionError('shared verifier must reject the extra module')
    extra.unlink()
    (tree/'undeclared-link.py').symlink_to(source/'schema.py')
    exchange_journal._verify_multistate_source(root, metadata)
    outcomes['undeclared_symlink_journal_verifier'] = 'accepted'
    try:
        verify_source_inventory(worker, files, current_source_root=source)
    except IdentityError as error:
        outcomes['undeclared_symlink_shared_verifier'] = str(error)
    else:
        raise AssertionError('shared verifier must reject the symlink')
    print(json.dumps(outcomes, indent=2, sort_keys=True))
    print('CHARACTERIZATION CONFIRMED; copied source never imported or executed')
