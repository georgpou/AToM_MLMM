import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _profile():
    return json.loads((ROOT / "environment/hpc/profile-template.json").read_text())


def test_hpc_profile_template_is_incomplete_and_defaults_to_validation_only():
    from atm_mlmm.hpc import check_profile

    result = check_profile(_profile(), bundle_manifest=None)
    assert result["status"] == "held"
    assert result["submission_performed"] is False
    assert "platform.name" in result["missing_fields"]
    assert "storage.path" in result["missing_fields"]


def test_complete_profile_only_authorizes_local_trial_dry_run():
    from atm_mlmm.hpc import check_profile

    profile = _profile()
    profile.update({
        "profile_id": "example-fully-declared-local-validation",
        "platform": {"name": "explicit-test-platform", "device": "CPU", "driver": "not-applicable"},
        "software": {"python": "3.11.16", "openmm": "8.6.1", "model": "MACE-OFF23-small"},
        "artifacts": {"source_sha256": "a" * 64, "wheel_sha256": "b" * 64,
                      "asset_manifest_sha256": "c" * 64, "input_manifest_sha256": "d" * 64},
        "storage": {"path": "/tmp/atom-hpc-trial", "filesystem": "local-test",
                    "lock_rename_fsync_test_required": True},
        "allocation": {"threads": 2, "memory_gib": 8, "walltime_seconds": 600,
                       "workers": 1, "scheduler": "none"},
        "checkpoint": {"compatible_with": "same-platform-identical-source-profile",
                       "portable_state_promises_identical_rng": False},
    })
    result = check_profile(profile, bundle_manifest={"format": "atom-mlmm-release-bundle-v1"})
    assert result["status"] == "ready_for_local_trial_dry_run"
    assert result["submission_performed"] is False
    assert result["scheduler_submission"] == "not_implemented"


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
