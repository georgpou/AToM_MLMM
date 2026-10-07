import hashlib
import json
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "models/mace-off23-small"


def test_release_bundle_hashes_source_wheel_inputs_assets_and_evidence(tmp_path):
    from atm_mlmm.release import build_release_bundle, verify_release_bundle

    source = tmp_path / "source"
    (source / "src/atm_mlmm").mkdir(parents=True)
    (source / "src/atm_mlmm/__init__.py").write_text("VERSION = 'test'\n")
    wheel = tmp_path / "atm_mlmm-0.1.0-py3-none-any.whl"
    wheel.write_bytes(b"validated-wheel-placeholder")
    input_file = tmp_path / "case.json"
    input_file.write_text('{"case":"tiny-control"}\n')
    evidence_file = tmp_path / "check.log"
    evidence_file.write_text("focused check: passed\n")
    output = tmp_path / "offline-bundle"

    result = build_release_bundle(
        output,
        source_root=source,
        source_paths=("src/atm_mlmm/__init__.py",),
        wheel=wheel,
        inputs=(input_file,),
        assets=ASSET,
        evidence=(evidence_file,),
    )

    assert result["format"] == "atom-mlmm-release-bundle-v1"
    assert {row["category"] for row in result["files"]} == {
        "source", "wheel", "input", "asset", "evidence"
    }
    for row in result["files"]:
        path = output / row["bundle_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    assert verify_release_bundle(output)["status"] == "verified"


def test_release_bundle_is_immutable_and_rejects_asset_damage(tmp_path):
    from atm_mlmm.release import build_release_bundle

    source = tmp_path / "src"
    source.mkdir()
    (source / "module.py").write_text("x = 1\n")
    wheel = tmp_path / "pkg.whl"
    wheel.write_bytes(b"wheel")
    input_file = tmp_path / "input.json"
    input_file.write_text("{}\n")
    damaged = tmp_path / "assets"
    shutil.copytree(ASSET, damaged)
    (damaged / "LICENSE.md").write_text("changed\n")

    with pytest.raises(ValueError, match="licen|asset"):
        build_release_bundle(tmp_path / "bad", source_root=source,
                             source_paths=("module.py",), wheel=wheel,
                             inputs=(input_file,), assets=damaged, evidence=())


def test_release_bundle_refuses_overwrite(tmp_path):
    from atm_mlmm.release import build_release_bundle

    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        build_release_bundle(output, source_root=tmp_path, source_paths=(), wheel=tmp_path / "w.whl",
                             inputs=(), assets=ASSET, evidence=())
