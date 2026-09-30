"""Lightweight tests: no molecular packages, model assets or GPU required."""
import json
import subprocess
from pathlib import Path

import pytest


def _repository(tmp_path):
    subprocess.run(["git", "init", "-b", "M00", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "ATM_MLMM_environment.yml").write_text("candidate: unchanged\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test",
                    "-c", "user.email=test@example.invalid", "commit", "-m", "fixture"],
                   check=True, capture_output=True)
    return tmp_path


def test_capture_records_exact_repository_and_candidate_identity(tmp_path):
    from atm_mlmm.persistence import capture_environment
    root = _repository(tmp_path)
    result = capture_environment(root, conda_prefix=None, checks={})
    assert result["schema_version"] == 1
    assert result["repository"]["commit"] == subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    assert len(result["candidate_sha256"]) == 64
    assert result["python"]["version"].count(".") == 2
    assert result["installation_status"] == "not_run"
    assert result["qualification_status"] == "not_qualified"
    assert result["model"]["status"] == result["gpu"]["status"] == "not_run"
    json.dumps(result)


def test_failed_checks_cannot_report_installed(tmp_path):
    from atm_mlmm.persistence import capture_environment
    result = capture_environment(_repository(tmp_path), conda_prefix=None,
                                 checks={"pip_check": {"exit_code": 1}})
    assert result["installation_status"] == "failed"


def test_manifest_rejects_missing_source_and_build_evidence():
    from atm_mlmm.persistence import validate_environment_manifest
    with pytest.raises(ValueError, match="source|build|Conda"):
        validate_environment_manifest({"schema_version": 1, "conda_packages": [],
                                       "packages": [], "checks": {}})


def test_missing_candidate_is_an_error(tmp_path):
    from atm_mlmm.persistence import capture_environment
    with pytest.raises(FileNotFoundError):
        capture_environment(tmp_path, conda_prefix=None, checks={})


def test_package_import_does_not_initialize_backends():
    code = "import sys, atm_mlmm; assert not {'openmm','torch','mace'} & sys.modules.keys()"
    subprocess.run([__import__("sys").executable, "-c", code], check=True,
                   env={**__import__("os").environ, "PYTHONPATH": str(Path(__file__).parents[2] / "src")})
