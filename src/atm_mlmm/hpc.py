"""Validation-only HPC profile admission; this module never submits jobs."""
from __future__ import annotations

import re


_REQUIRED = {
    "platform": ("name", "device", "driver"),
    "software": ("python", "openmm", "model"),
    "artifacts": ("source_sha256", "wheel_sha256", "asset_manifest_sha256", "input_manifest_sha256"),
    "storage": ("path", "filesystem", "lock_rename_fsync_test_required"),
    "allocation": ("threads", "memory_gib", "walltime_seconds", "workers", "scheduler"),
    "checkpoint": ("compatible_with", "portable_state_promises_identical_rng"),
}


def check_profile(profile, *, bundle_manifest=None):
    missing, errors = [], []
    if not isinstance(profile, dict):
        raise ValueError("profile must be a JSON object")
    for group, keys in _REQUIRED.items():
        values = profile.get(group)
        if not isinstance(values, dict):
            missing.extend(f"{group}.{key}" for key in keys)
            continue
        missing.extend(f"{group}.{key}" for key in keys if key not in values or values[key] in (None, ""))
    artifacts = profile.get("artifacts", {})
    for key in _REQUIRED["artifacts"]:
        value = artifacts.get(key)
        if value not in (None, "") and (not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)):
            errors.append(f"{key} must be a lowercase SHA-256")
    allocation = profile.get("allocation", {})
    if allocation.get("scheduler") not in (None, "", "none"):
        errors.append("scheduler is not validated by this local profile checker")
    if bundle_manifest is not None and bundle_manifest.get("format") != "atom-mlmm-release-bundle-v1":
        errors.append("release bundle format is unsupported")
    if not profile.get("profile_id"):
        missing.append("profile_id")
    if missing or errors or bundle_manifest is None:
        if bundle_manifest is None:
            missing.append("verified_release_bundle")
        status = "held"
    else:
        status = "ready_for_local_trial_dry_run"
    return {"profile_id": profile.get("profile_id"), "status": status,
            "missing_fields": sorted(set(missing)), "errors": errors,
            "submission_performed": False, "scheduler_submission": "not_implemented",
            "scope": "profile validation and local trial dry-run only; cluster parity/restart remains untested"}
