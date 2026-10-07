import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _profile():
    return json.loads((ROOT / "environment/hpc/profile-template.json").read_text())


def _complete_profile():
    profile = _profile()
    profile.update({
        "profile_id": "example-fully-declared-local-validation",
        "platform": {"name": "explicit-test-platform", "device": "CPU", "driver": "not-applicable"},
        "software": {"python": "3.11.16", "openmm": "8.6.1", "model": "analytic-control"},
        "artifacts": {"source_sha256": "a" * 64, "wheel_sha256": "b" * 64,
                      "asset_manifest_sha256": "c" * 64, "input_manifest_sha256": "d" * 64},
        "storage": {"path": "/tmp/atom-hpc-trial", "filesystem": "local-test",
                    "lock_rename_fsync_test_required": True},
        "allocation": {"threads": 2, "memory_gib": 8, "walltime_seconds": 600,
                       "workers": 1, "scheduler": "none"},
        "checkpoint": {"compatible_with": "same-platform-identical-source-profile",
                       "portable_state_promises_identical_rng": False},
    })
    return profile


def _inventory_digest(rows):
    entries = [{key: row[key] for key in ("bundle_path", "bytes", "sha256")}
               for row in sorted(rows, key=lambda row: row["bundle_path"])]
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _verified_bundle(root):
    root.mkdir()
    contents = {
        "source/module.py": ("source", b"VALUE = 1\n"),
        "wheel/atom_mlmm-test.whl": ("wheel", b"wheel-bytes"),
        "inputs/case.json": ("input", b"{\"case\": \"tiny\"}\n"),
        "assets/mace-off23-small/manifest.json": ("asset", b"{\"asset\": \"test\"}\n"),
        "evidence/check.log": ("evidence", b"input-only bundle control\n"),
    }
    rows = []
    for name, (category, content) in contents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        rows.append({"category": category, "bundle_path": name, "bytes": len(content),
                     "sha256": hashlib.sha256(content).hexdigest()})
    manifest = {"format": "atom-mlmm-release-bundle-v1", "files": rows}
    (root / "manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n")
    profile = _complete_profile()
    profile["artifacts"] = {
        "source_sha256": _inventory_digest([row for row in rows if row["category"] == "source"]),
        "wheel_sha256": next(row["sha256"] for row in rows if row["category"] == "wheel"),
        "asset_manifest_sha256": next(row["sha256"] for row in rows
                                       if row["bundle_path"] == "assets/mace-off23-small/manifest.json"),
        "input_manifest_sha256": _inventory_digest([row for row in rows if row["category"] == "input"]),
    }
    return root, profile


def test_hpc_profile_template_is_incomplete_and_defaults_to_validation_only():
    from atm_mlmm.hpc import check_profile

    result = check_profile(_profile(), bundle_manifest=None)
    assert result["status"] == "held"
    assert result["submission_performed"] is False
    assert "platform.name" in result["missing_fields"]
    assert "storage.path" in result["missing_fields"]


def test_format_only_manifest_cannot_authorize_profile_readiness():
    from atm_mlmm.hpc import check_profile

    result = check_profile(_complete_profile(),
                           bundle_manifest={"format": "atom-mlmm-release-bundle-v1"})
    assert result["status"] == "held"
    assert result["submission_performed"] is False
    assert "verified" in " ".join(result["errors"]).lower()


@pytest.mark.parametrize("change,expected_error", (
    ("schema", "schema_version"), ("resources", "allocation."),
    ("storage", "lock_rename_fsync_test_required"),
    ("checkpoint", "checkpoint."), ("unknown-field", "unknown profile fields"),
    ("storage-type", "must be boolean true"),
    ("checkpoint-type", "must be boolean false"),
))
def test_hpc_profile_rejects_unknown_or_contradictory_typed_values(change, expected_error):
    from atm_mlmm.hpc import check_profile

    profile = _complete_profile()
    if change == "schema":
        profile["schema_version"] = 999
    elif change == "resources":
        profile["allocation"].update(threads=-1, memory_gib=0, walltime_seconds=0, workers=0)
    elif change == "storage":
        profile["storage"]["lock_rename_fsync_test_required"] = False
    elif change == "checkpoint":
        profile["checkpoint"].update(compatible_with="unknown",
                                     portable_state_promises_identical_rng=True)
    elif change == "storage-type":
        profile["storage"]["lock_rename_fsync_test_required"] = 1
    elif change == "checkpoint-type":
        profile["checkpoint"]["portable_state_promises_identical_rng"] = 0
    else:
        profile["unexpected_profile_mode"] = "unknown"
    result = check_profile(profile, bundle_manifest={"format": "atom-mlmm-release-bundle-v1"})
    assert result["status"] == "held"
    assert expected_error in " ".join(result["errors"])


def test_hpc_cli_verifies_bundle_bytes_and_matches_profile_artifacts(tmp_path):
    bundle, profile = _verified_bundle(tmp_path / "bundle")
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile, sort_keys=True) + "\n")
    output = tmp_path / "result.json"
    command = [sys.executable, str(ROOT / "tools/check_hpc_profile.py"), str(profile_path),
               "--bundle-manifest", str(bundle / "manifest.json"), "--output", str(output)]

    valid = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert valid.returncode == 0, valid.stdout + valid.stderr
    assert json.loads(output.read_text())["status"] == "ready_for_local_trial_dry_run"

    profile["artifacts"]["source_sha256"] = "e" * 64
    profile_path.write_text(json.dumps(profile, sort_keys=True) + "\n")
    mismatched = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert mismatched.returncode == 2
    assert "artifacts.source_sha256 does not match verified bundle" in " ".join(
        json.loads(output.read_text())["errors"])

    profile["artifacts"]["source_sha256"] = _inventory_digest(
        [{"bundle_path": "source/module.py", "bytes": len(b"VALUE = 1\n"),
          "sha256": hashlib.sha256(b"VALUE = 1\n").hexdigest()}])
    profile_path.write_text(json.dumps(profile, sort_keys=True) + "\n")
    (bundle / "source/module.py").write_text("VALUE = 2\n")
    damaged = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert damaged.returncode == 2
    assert json.loads(output.read_text())["status"] == "held"


def test_hpc_profile_rejects_unknown_scheduler_or_missing_input_hash():
    from atm_mlmm.hpc import check_profile

    profile = _profile()
    profile.update({"platform": {"name": "cpu", "device": "CPU", "driver": "none"},
                    "software": {"python": "3.11", "openmm": "8.6", "model": "analytic"},
                    "artifacts": {"source_sha256": "a" * 64},
                    "storage": {"path": "/tmp", "filesystem": "local"},
                    "allocation": {"threads": 2, "memory_gib": 8, "walltime_seconds": 60,
                                   "workers": 1, "scheduler": "guess-slurm"},
                    "checkpoint": {"compatible_with": "unknown",
                                   "portable_state_promises_identical_rng": False}})
    result = check_profile(profile, bundle_manifest=None)
    assert result["status"] == "held"
    assert "artifacts.input_manifest_sha256" in result["missing_fields"]
    assert result["submission_performed"] is False
