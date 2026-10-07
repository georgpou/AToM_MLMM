import hashlib
from pathlib import Path
import shutil

import pytest

from atm_mlmm.runtime_validation import verify_source_inventory
from atm_mlmm.schema import IdentityError


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/atm_mlmm"
PREFIX = "runtime/source/atm_mlmm/"


def _bundle(tmp_path):
    root = tmp_path / "worker"
    source = root / "runtime/source/atm_mlmm"
    source.parent.mkdir(parents=True)
    shutil.copytree(SOURCE, source)
    files = {}
    for path in sorted(source.rglob("*.py")):
        name = PREFIX + path.relative_to(source).as_posix()
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return root, files


def test_bundle_python_source_inventory_must_match_recursively(tmp_path):
    root, files = _bundle(tmp_path)
    verify_source_inventory(root, files, current_source_root=SOURCE)

    relocated = tmp_path / "relocated-worker"
    shutil.copytree(root, relocated)
    verify_source_inventory(relocated, files, current_source_root=SOURCE)

    undeclared = root / "runtime/source/atm_mlmm/nested/undeclared.py"
    undeclared.parent.mkdir()
    undeclared.write_text("VALUE = 'not in manifest'\n")
    with pytest.raises(IdentityError, match="source inventory"):
        verify_source_inventory(root, files, current_source_root=SOURCE)


def test_bundle_python_source_inventory_rejects_nested_symlink(tmp_path):
    root, files = _bundle(tmp_path)
    source = root / "runtime/source/atm_mlmm"
    link = source / "linked-package"
    link.symlink_to(SOURCE, target_is_directory=True)
    with pytest.raises(IdentityError, match="symbolic link"):
        verify_source_inventory(root, files, current_source_root=SOURCE)
