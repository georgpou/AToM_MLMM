"""G00-T1 checks for the inherited CPU candidate, not molecular qualification."""
import json
import hashlib
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.environment


def test_required_apis_and_versions():
    from atm_mlmm.persistence import check_required_apis
    result = check_required_apis()
    assert result["status"] == "passed"
    assert result["python_force_selected_particles"] == [0]
    assert result["torch_backend"] == "cpu"


def test_environment_manifest_complete():
    from atm_mlmm.persistence import validate_environment_manifest
    manifest = Path(os.environ["ATM_MLMM_MANIFEST"])
    report = json.loads(manifest.read_text())
    candidate = Path(__file__).parents[2] / "ATM_MLMM_environment.yml"
    assert report["candidate_sha256"] == hashlib.sha256(candidate.read_bytes()).hexdigest()
    validate_environment_manifest(report)


def test_unavailable_platform_is_unqualified():
    report = json.loads(Path(os.environ["ATM_MLMM_MANIFEST"]).read_text())
    assert report["gpu"]["status"] == "not_run"
    assert report["qualification_status"] == "not_qualified"
    assert report["model"]["status"] == "not_run"
