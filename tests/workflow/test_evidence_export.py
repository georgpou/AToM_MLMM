"""A disconnect/partial copy must never masquerade as a saved calculation."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


def api():
    assert importlib.util.find_spec('atm_mlmm.evidence'), 'verified evidence transport is missing'
    from atm_mlmm.evidence import export_evidence, verify_evidence
    return export_evidence, verify_evidence


def attempt(root):
    root.mkdir()
    (root/'worker').mkdir()
    (root/'worker/checkpoint.chk').write_bytes(b'\0checkpoint\xff')
    (root/'records.json').write_text('{"sample_ids":["a"]}\n')
    (root/'samples').mkdir()
    (root/'samples/.pending-000001-interrupted').mkdir()
    (root/'samples/.pending-000001-interrupted/record.json').write_text('{"uncommitted":true}')
    (root/'empty').mkdir()
    return root


def test_complete_copy_retains_failed_transaction_and_is_verified(tmp_path):
    export, verify = api()
    source = attempt(tmp_path/'local')
    target = tmp_path/'durable'
    result = export(source, target)
    assert result == verify(target)
    assert result['files']['worker/checkpoint.chk'] == hashlib.sha256(b'\0checkpoint\xff').hexdigest()
    assert (target/'samples/.pending-000001-interrupted/record.json').read_bytes() == (source/'samples/.pending-000001-interrupted/record.json').read_bytes()
    assert (source/'worker/checkpoint.chk').is_file() and (target/'empty').is_dir()
    with pytest.raises(FileExistsError):
        export(source, target)


@pytest.mark.parametrize('change', ('modified', 'missing', 'extra', 'empty-directory'))
def test_verify_rejects_partial_or_changed_copy(tmp_path, change):
    export, verify = api()
    source = attempt(tmp_path/'local')
    target = tmp_path/'durable'
    export(source, target)
    if change == 'modified':
        (target/'worker/checkpoint.chk').write_bytes(b'changed')
    elif change == 'missing':
        (target/'records.json').unlink()
    elif change == 'extra':
        (target/'unbound').write_text('extra')
    else:
        (target/'empty').rmdir()
    with pytest.raises(ValueError, match='identity|mismatch'):
        verify(target)


def test_copy_failure_keeps_local_and_partial_bytes(tmp_path, monkeypatch):
    export, _ = api()
    source = attempt(tmp_path/'local')
    import atm_mlmm.evidence as evidence
    original = evidence.shutil.copy2
    copied = []
    def fail_after_one(src, dst, *args, **kwargs):
        if copied:
            raise OSError('simulated disconnect')
        result = original(src, dst, *args, **kwargs)
        copied.append(Path(dst))
        return result
    monkeypatch.setattr(evidence.shutil, 'copy2', fail_after_one)
    with pytest.raises(OSError, match='disconnect'):
        export(source, tmp_path/'durable')
    assert not (tmp_path/'durable').exists()
    assert copied[0].is_file()
    assert (source/'worker/checkpoint.chk').read_bytes() == b'\0checkpoint\xff'


def test_rejects_symlinks_and_recursive_copy(tmp_path):
    export, _ = api()
    source = attempt(tmp_path/'local')
    with pytest.raises(ValueError, match='inside|overlap'):
        export(source, source/'copy')
    (source/'outside').symlink_to(tmp_path)
    with pytest.raises(ValueError, match='symlink'):
        export(source, tmp_path/'durable')


def test_manifest_path_traversal_is_rejected_without_reading_outside(tmp_path):
    export, verify = api()
    target = tmp_path/'durable'
    export(attempt(tmp_path/'local'), target)
    manifest = target/'.evidence.json'
    data = json.loads(manifest.read_text())
    data['files']['../secret'] = '0'*64
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='path'):
        verify(target)
