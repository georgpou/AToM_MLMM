"""Validation-only HPC profile admission; this module never submits jobs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


_REQUIRED = {
    "platform": ("name", "device", "driver"),
    "software": ("python", "openmm", "model"),
    "artifacts": ("source_sha256", "wheel_sha256", "asset_manifest_sha256", "input_manifest_sha256"),
    "storage": ("path", "filesystem", "lock_rename_fsync_test_required"),
    "allocation": ("threads", "memory_gib", "walltime_seconds", "workers", "scheduler"),
    "checkpoint": ("compatible_with", "portable_state_promises_identical_rng"),
}


def _inventory_sha256(rows):
    entries = [{key: row[key] for key in ("bundle_path", "bytes", "sha256")}
               for row in sorted(rows, key=lambda row: row["bundle_path"])]
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _validate_profile(profile, missing, errors):
    allowed = {"schema_version", "profile_id", *_REQUIRED}
    unknown = set(profile) - allowed
    if unknown:
        errors.append(f"unknown profile fields: {', '.join(sorted(map(str, unknown)))}")
    if type(profile.get("schema_version")) is not int or profile.get("schema_version") != 1:
        errors.append("schema_version must be integer 1")
    profile_id = profile.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        missing.append("profile_id")

    for group, keys in _REQUIRED.items():
        values = profile.get(group)
        if not isinstance(values, dict):
            missing.extend(f"{group}.{key}" for key in keys)
            continue
        unknown = set(values) - set(keys)
        if unknown:
            errors.append(f"unknown {group} fields: {', '.join(sorted(map(str, unknown)))}")
        for key in keys:
            value = values.get(key)
            if key not in values or value is None or value == "":
                missing.append(f"{group}.{key}")

    def values_for(group):
        values = profile.get(group)
        return values if isinstance(values, dict) else {}

    platform = values_for("platform")
    for key in ("name", "driver"):
        value = platform.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"platform.{key} must be a nonempty string")
    if platform.get("device") not in (None, "CPU", "GPU"):
        errors.append("platform.device must be CPU or GPU")

    software = values_for("software")
    for key in _REQUIRED["software"]:
        value = software.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"software.{key} must be a nonempty string")

    artifacts = values_for("artifacts")
    for key in _REQUIRED["artifacts"]:
        value = artifacts.get(key)
        if value is not None and value != "" and (
                not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)):
            errors.append(f"artifacts.{key} must be a lowercase SHA-256")

    storage = values_for("storage")
    path = storage.get("path")
    if path is not None and path != "":
        if not isinstance(path, str) or not Path(path).is_absolute():
            errors.append("storage.path must be an absolute path")
    filesystem = storage.get("filesystem")
    if filesystem is not None and (not isinstance(filesystem, str) or not filesystem.strip()):
        errors.append("storage.filesystem must be a nonempty string")
    lock_test = storage.get("lock_rename_fsync_test_required")
    if lock_test is not None and type(lock_test) is not bool:
        errors.append("storage.lock_rename_fsync_test_required must be boolean true")
    elif lock_test is False:
        errors.append("storage.lock_rename_fsync_test_required must be true")

    allocation = values_for("allocation")
    for key in ("threads", "memory_gib", "walltime_seconds", "workers"):
        value = allocation.get(key)
        if value is not None and (type(value) is not int or value <= 0):
            errors.append(f"allocation.{key} must be a positive integer")
    scheduler = allocation.get("scheduler")
    if scheduler not in (None, "none"):
        errors.append("scheduler is not validated by this local profile checker")

    checkpoint = values_for("checkpoint")
    if checkpoint.get("compatible_with") not in (None, "same-platform-identical-source-profile"):
        errors.append("checkpoint.compatible_with is not a validated compatibility scope")
    rng_promise = checkpoint.get("portable_state_promises_identical_rng")
    if rng_promise is not None and type(rng_promise) is not bool:
        errors.append("checkpoint.portable_state_promises_identical_rng must be boolean false")
    elif rng_promise is True:
        errors.append("checkpoint portable-state RNG identity promise is unsupported")


def check_profile(profile, *, bundle_manifest=None, bundle_directory=None):
    """Check typed profile values and bind them to a verified bundle directory.

    ``bundle_manifest`` remains accepted for callers of the earlier API, but a
    JSON object alone is not evidence that the referenced bundle bytes exist.
    """
    missing, errors = [], []
    if not isinstance(profile, dict):
        raise ValueError("profile must be a JSON object")
    _validate_profile(profile, missing, errors)

    if bundle_manifest is not None:
        errors.append("bundle manifest content is unverified; provide its actual bundle directory")
    elif bundle_directory is None:
        missing.append("verified_release_bundle")
    else:
        try:
            from .release import verify_release_bundle
            root = Path(bundle_directory)
            if root.is_symlink() or not root.is_dir():
                raise ValueError("bundle directory is missing or unsafe")
            manifest_path = root / "manifest.json"
            if manifest_path.is_symlink() or not manifest_path.is_file():
                raise ValueError("bundle manifest is missing or unsafe")
            verify_release_bundle(root)
            manifest = json.loads(manifest_path.read_text())
            rows = manifest["files"]
            by_category = {category: [row for row in rows if row.get("category") == category]
                           for category in ("source", "input", "wheel")}
            asset_rows = [row for row in rows
                          if row.get("bundle_path") == "assets/mace-off23-small/manifest.json"]
            if not by_category["source"] or not by_category["input"]:
                errors.append("verified bundle lacks source or input artifacts")
            if len(by_category["wheel"]) != 1 or len(asset_rows) != 1:
                errors.append("verified bundle must contain one wheel and the approved asset manifest")
            else:
                actual = {
                    "source_sha256": _inventory_sha256(by_category["source"]),
                    "wheel_sha256": by_category["wheel"][0]["sha256"],
                    "asset_manifest_sha256": asset_rows[0]["sha256"],
                    "input_manifest_sha256": _inventory_sha256(by_category["input"]),
                }
                for key, digest in actual.items():
                    if profile.get("artifacts", {}).get(key) != digest:
                        errors.append(f"artifacts.{key} does not match verified bundle")
        except (OSError, ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
            errors.append(f"release bundle verification failed: {exc}")

    if missing or errors:
        status = "held"
    else:
        status = "ready_for_local_trial_dry_run"
    return {"profile_id": profile.get("profile_id"), "status": status,
            "missing_fields": sorted(set(missing)), "errors": errors,
            "submission_performed": False, "scheduler_submission": "not_implemented",
            "scope": "profile validation and local trial dry-run only; cluster parity/restart remains untested"}
