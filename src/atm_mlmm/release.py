"""Hash-bound local release bundles and a machine-checkable support matrix."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess


_PROFILE_FIELDS = ("model", "embedding", "protocol", "hardware", "precision", "ensemble", "input")
_EVIDENCE_STATES = {
    "accepted_prior", "worker_tested_pending_review", "missing_implementation",
    "physical_hold", "unavailable_hardware", "not_assessed",
}
_ASSET_FILES = ("MACE-OFF23_small.model", "manifest.json", "LICENSE.md")


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _copy_tree_or_file(source, destination):
    source = Path(source)
    if source.is_symlink() or not source.exists():
        raise ValueError(f"release input is absent or a symlink: {source}")
    source = source.resolve()
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        return [destination]
    copied = []
    for item in sorted(source.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"release tree contains a symlink: {item}")
        if item.is_file():
            relative = item.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, target)
            copied.append(target)
    return copied


def _git_identity(root):
    def run(args):
        try:
            return subprocess.check_output(args, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    commit = run(["git", "rev-parse", "HEAD"])
    tree = run(["git", "rev-parse", "HEAD^{tree}"])
    dirty = None if commit is None else bool(run(["git", "status", "--porcelain"]))
    return {"commit": commit, "tree": tree, "working_tree_dirty": dirty}


def build_release_bundle(output, *, source_root, source_paths, wheel, inputs, assets, evidence):
    """Create a new bundle; all listed bytes are copied and SHA-256 recorded."""
    output = Path(output)
    if output.is_symlink():
        raise ValueError("release output must not be a symlink")
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    source_root = Path(source_root).resolve()
    wheel = Path(wheel)
    asset_dir = Path(assets)
    if wheel.is_symlink() or asset_dir.is_symlink():
        raise ValueError("wheel and approved asset directory must not be symlinks")
    wheel = wheel.resolve()
    asset_dir = asset_dir.resolve()
    try:
        from .models.mace import verify_asset
        verify_asset(asset_dir / _ASSET_FILES[0], asset_dir / "manifest.json")
    except (ImportError, OSError, ValueError) as exc:
        raise ValueError(f"approved model asset identity/authorization rejected: {exc}") from exc
    if not wheel.is_file() or wheel.is_symlink():
        raise ValueError("project wheel must be a regular file")

    staged = []
    try:
        output.mkdir(parents=True, exist_ok=False)
        for relative in source_paths:
            rel = PurePosixPath(str(relative))
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"unsafe source path: {relative}")
            source = source_root.joinpath(*rel.parts)
            if source.is_symlink() or not source.exists():
                raise ValueError(f"source path is absent or a symlink: {relative}")
            target = output / "source" / Path(*rel.parts)
            if source.is_dir():
                copied = _copy_tree_or_file(source, target)
                staged.extend(("source", source / path.relative_to(target), path) for path in copied)
            elif source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                staged.append(("source", source, target))
            else:
                raise ValueError(f"source path is not a regular file or directory: {relative}")

        wheel_target = output / "wheel" / wheel.name
        wheel_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(wheel, wheel_target)
        staged.append(("wheel", wheel, wheel_target))

        for category, paths in (("input", inputs), ("evidence", evidence)):
            names = set()
            for item in paths:
                item = Path(item)
                if item.is_symlink():
                    raise ValueError(f"release {category} must not be a symlink: {item}")
                item = item.resolve()
                name = item.name
                if name in names:
                    raise ValueError(f"duplicate {category} basename: {name}")
                names.add(name)
                target = output / ("inputs" if category == "input" else "evidence") / name
                copied = _copy_tree_or_file(item, target)
                source_base = item if item.is_dir() else item.parent
                for target_file in copied:
                    source_file = item / target_file.relative_to(target) if item.is_dir() else item
                    staged.append((category, source_file, target_file))

        for name in _ASSET_FILES:
            source = asset_dir / name
            if not source.is_file() or source.is_symlink():
                raise ValueError(f"approved model asset is missing: {name}")
            target = output / "assets" / "mace-off23-small" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            staged.append(("asset", source, target))

        rows = [{"category": category,
                 "source_path": str(source),
                 "bundle_path": target.relative_to(output).as_posix(),
                 "bytes": target.stat().st_size,
                 "sha256": _sha(target)}
                for category, source, target in staged]
        rows.sort(key=lambda row: row["bundle_path"])
        manifest = {
            "format": "atom-mlmm-release-bundle-v1",
            "source_identity": _git_identity(source_root),
            "files": rows,
            "model_asset": {"checkpoint_sha256": _sha(output / "assets/mace-off23-small/MACE-OFF23_small.model"),
                            "manifest_sha256": _sha(output / "assets/mace-off23-small/manifest.json"),
                            "license_sha256": _sha(output / "assets/mace-off23-small/LICENSE.md"),
                            "authorization": "I will use it for academic purposes.",
                            "authorization_sha256": hashlib.sha256(
                                b"I will use it for academic purposes.").hexdigest(),
                            "license": "Academic Software Licence v1.0; academic noncommercial use"},
            "project_license": "not_declared; external distribution is a release hold",
            "dependencies": {"fully_offline_reinstall": False,
                             "note": "The bundle does not assert a complete cached dependency artifact set; use the validated locked CPU profile."},
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise


def verify_release_bundle(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("format") != "atom-mlmm-release-bundle-v1":
        raise ValueError("unsupported release bundle format")
    seen = set()
    for row in manifest.get("files", []):
        rel = PurePosixPath(row.get("bundle_path", ""))
        if rel.is_absolute() or ".." in rel.parts or str(rel) in seen:
            raise ValueError("bundle manifest contains an unsafe or duplicate path")
        seen.add(str(rel))
        path = directory.joinpath(*rel.parts)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"bundle file is missing or unsafe: {rel}")
        if path.stat().st_size != row.get("bytes") or _sha(path) != row.get("sha256"):
            raise ValueError(f"bundle file identity mismatch: {rel}")
    for required in ("source", "wheel", "input", "asset", "evidence"):
        if required not in {row.get("category") for row in manifest.get("files", [])}:
            raise ValueError(f"bundle lacks required {required} content")
    return {"status": "verified", "file_count": len(seen),
            "fully_offline_reinstall": manifest.get("dependencies", {}).get("fully_offline_reinstall") is True}


def validate_support_matrix(matrix):
    if not isinstance(matrix, dict) or matrix.get("format") != "atom-mlmm-support-matrix-v1":
        raise ValueError("unsupported support matrix format")
    profiles = matrix.get("profiles")
    claims = matrix.get("claims")
    if not isinstance(profiles, list) or not isinstance(claims, list) or not profiles or not claims:
        raise ValueError("support matrix needs profiles and claims")
    profile_ids = set()
    for profile in profiles:
        if not isinstance(profile, dict) or not profile.get("profile_id"):
            raise ValueError("every profile needs a profile_id")
        missing = [field for field in _PROFILE_FIELDS if not profile.get(field)]
        if missing:
            raise ValueError(f"profile {profile.get('profile_id')} missing {', '.join(missing)}")
        profile_ids.add(profile["profile_id"])
    claim_ids = set()
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("claim_id"):
            raise ValueError("every claim needs a claim_id")
        if claim["claim_id"] in claim_ids:
            raise ValueError("duplicate claim_id")
        claim_ids.add(claim["claim_id"])
        if claim.get("profile_id") not in profile_ids:
            raise ValueError(f"claim {claim['claim_id']} references an unknown profile")
        state = claim.get("evidence_status")
        if state not in _EVIDENCE_STATES:
            raise ValueError(f"claim {claim['claim_id']} has an unknown evidence_status")
        evidence = claim.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("claim evidence must be a list")
        if state == "accepted_prior":
            if not evidence or any(not isinstance(row, dict) or
                                   row.get("evidence_kind") != "reviewed_gate" or
                                   not row.get("review_id") or not row.get("snapshot") or
                                   not row.get("path") or not row.get("sha256") or
                                   row.get("profile_id") != claim["profile_id"] for row in evidence):
                raise ValueError(f"claim {claim['claim_id']} lacks accepted evidence bound to its exact profile")
            for row in evidence:
                path = Path(row["path"])
                if not path.is_file() or path.is_symlink() or _sha(path) != row["sha256"]:
                    raise ValueError(f"claim {claim['claim_id']} accepted evidence bytes do not match the referenced hash")
        elif state == "worker_tested_pending_review":
            if not evidence or any(not isinstance(row, dict) or
                                   row.get("evidence_kind") != "worker_run" or
                                   not row.get("snapshot") or not row.get("path") or
                                   not row.get("source_tree") or not row.get("sha256") for row in evidence):
                raise ValueError(f"claim {claim['claim_id']} lacks exact worker evidence")
            for row in evidence:
                path = Path(row["path"])
                if not path.is_file() or path.is_symlink() or _sha(path) != row["sha256"]:
                    raise ValueError(f"claim {claim['claim_id']} worker evidence bytes do not match the referenced hash")
        elif state in ("physical_hold", "unavailable_hardware", "missing_implementation", "not_assessed"):
            if not claim.get("hold_reason"):
                raise ValueError(f"claim {claim['claim_id']} requires an explicit hold_reason")
        if claim.get("support_claim") is True and state != "accepted_prior":
            raise ValueError(f"claim {claim['claim_id']} cannot be supported at evidence level {state}")
    return {"profile_count": len(profiles), "capability_rows": len(claims),
            "unavailable_hardware_rows": sum(row["evidence_status"] == "unavailable_hardware" for row in claims),
            "physical_hold_rows": sum(row["evidence_status"] == "physical_hold" for row in claims)}
