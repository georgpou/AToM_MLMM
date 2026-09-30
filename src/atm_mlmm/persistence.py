"""G00 installation provenance; this module imports no molecular backend."""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import platform
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

SOURCE_TAGS = {"openmmml": "1.8", "atom-openmm": "v8.5.0"}
SOURCE_URLS = {"openmmml": "https://github.com/openmm/openmm-ml.git",
               "atom-openmm": "https://github.com/Gallicchio-Lab/AToM-OpenMM.git"}
REQUIRED_VERSIONS = {
    "openmm": "8.6.1", "openmmml": "1.8", "atom-openmm": "8.5.0b0",
    "torch": "2.8.0", "mace-torch": "0.3.16", "e3nn": "0.4.4",
    "pymbar": "4.0.3", "openmmforcefields": "0.16.0", "configobj": "5.0.9",
}
REQUIRED_CHECKS = ("solver", "project_install", "conda_integrity", "conda_packages",
                   "conda_explicit", "environment_export", "archive_pip",
                   "pip_check", "openmm_installation", "api_check")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def capture_environment(repo_root: Path, conda_prefix: Path | None,
                        checks: dict) -> dict:
    """Capture an installation record, never infer scientific qualification."""
    root = Path(repo_root)
    candidate = root / "ATM_MLMM_environment.yml"
    candidate_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
    packages = []
    for dist in metadata.distributions():
        origin = dist.read_text("direct_url.json")
        packages.append({"name": dist.metadata["Name"], "version": dist.version,
                         "installer": (dist.read_text("INSTALLER") or "unknown").strip(),
                         "origin": json.loads(origin) if origin else None})
    conda_packages = []
    if conda_prefix is not None:
        for path in sorted((Path(conda_prefix) / "conda-meta").glob("*.json")):
            record = json.loads(path.read_text())
            conda_packages.append({key: record.get(key) for key in
                ("name", "version", "build", "build_number", "subdir", "channel",
                 "url", "sha256", "md5")})
    if any(record.get("exit_code") != 0 for record in checks.values()):
        status = "failed"
    elif all(name in checks for name in REQUIRED_CHECKS):
        status = "installed"
    else:
        status = "not_run"
    return {
        "schema_version": 1, "profile": "core-analytic-cpu-installation",
        "installation_status": status, "qualification_status": "not_qualified",
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation(),
                   "executable": sys.executable, "build": platform.python_build()},
        "platform": {"system": platform.system(), "machine": platform.machine(),
                     "release": platform.release(), "description": platform.platform(),
                     "libc": platform.libc_ver()},
        "repository": {"commit": _git(root, "rev-parse", "HEAD"),
                       "branch": _git(root, "branch", "--show-current"),
                       "working_tree": _git(root, "status", "--porcelain")},
        "candidate_sha256": candidate_hash, "source_tags": SOURCE_TAGS,
        "packages": sorted(packages, key=lambda p: p["name"].lower()),
        "conda_packages": conda_packages, "checks": checks,
        "runtime_settings": {key: os.environ.get(key) for key in
            ("CUDA_VISIBLE_DEVICES", "OPENMM_CPU_THREADS", "OMP_NUM_THREADS",
             "TORCH_FORCE_WEIGHTS_ONLY_LOAD", "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD")},
        "model": {"status": "not_run", "reason": "No approved checkpoint or license decision"},
        "gpu": {"status": "not_run", "reason": "Separate hardware profile not executed"},
    }


def validate_environment_manifest(report: dict) -> None:
    """Reject incomplete G00-T1 evidence before it can advance a CPU claim."""
    if report.get("schema_version") != 1:
        raise ValueError("Unsupported environment evidence schema")
    if not re.fullmatch(r"3\.11\.\d+", report.get("python", {}).get("version", "")) or not report.get("python", {}).get("build"):
        raise ValueError("Missing exact candidate Python patch/build identity")
    target = report.get("platform", {})
    if target.get("system") != "Linux" or target.get("machine") != "x86_64" or not target.get("release"):
        raise ValueError("Missing or unsupported CPU platform identity")
    if not re.fullmatch(r"[0-9a-f]{40}", report.get("repository", {}).get("commit", "")):
        raise ValueError("Missing repository commit identity")
    if report.get("repository", {}).get("working_tree") != "":
        raise ValueError("Uncommitted repository changes require separate content identity")
    if not re.fullmatch(r"[0-9a-f]{64}", report.get("candidate_sha256", "")):
        raise ValueError("Missing candidate content identity")
    artifacts = report.get("artifact_hashes", {})
    if not all(name in artifacts for name in ("conda-explicit.txt", "pip-wheels.lock", "source-origins.json")) or any(not re.fullmatch(r"[0-9a-f]{64}", h) for h in artifacts.values()):
        raise ValueError("Missing or malformed archived artifact identity")
    conda = report.get("conda_packages", [])
    if not conda or any(not all(p.get(k) for k in ("name", "version", "build", "url", "sha256"))
                        for p in conda):
        raise ValueError("Missing Conda package build, URL or SHA-256 evidence")
    if any(not re.fullmatch(r"[0-9a-f]{64}", p["sha256"]) or not p["url"].startswith("https://") for p in conda):
        raise ValueError("Malformed Conda artifact identity")
    packages = {p["name"].lower().replace("_", "-"): p for p in report["packages"]}
    for name, version in REQUIRED_VERSIONS.items():
        if name not in packages or packages[name]["version"].split("+")[0] != version:
            raise ValueError(f"Missing or inconsistent package version: {name} == {version}")
    for name in SOURCE_TAGS:
        origin = packages[name].get("origin") or {}
        commit = origin.get("vcs_info", {}).get("commit_id", "")
        if not commit:
            archived = report.get("archived_source_origins", {}).get(name, {})
            installed_hash = origin.get("archive_info", {}).get("hashes", {}).get("sha256")
            wheel_hash = archived.get("wheel_sha256")
            if not installed_hash or installed_hash != wheel_hash or wheel_hash not in report.get("artifact_hashes", {}).values():
                raise ValueError(f"Installed source wheel is not tied to archived provenance: {name}")
            commit = archived.get("vcs_info", {}).get("commit_id", "")
            origin = archived
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError(f"Missing installed source commit: {name}")
        if origin.get("url") != SOURCE_URLS[name] or origin.get("vcs_info", {}).get("requested_revision") != SOURCE_TAGS[name]:
            raise ValueError(f"Source URL/tag differs from reviewed candidate: {name}")
    for name in REQUIRED_CHECKS:
        if report.get("checks", {}).get(name, {}).get("exit_code") != 0:
            raise ValueError(f"Required installation check did not pass: {name}")
    if report.get("installation_status") != "installed":
        raise ValueError("Installation is incomplete")
    if report.get("qualification_status") != "not_qualified":
        raise ValueError("G00 cannot establish molecular qualification")


def verify_conda_files(prefix: Path) -> dict:
    """Detect clobbered Conda files using recorded installed/relocated hashes."""
    prefix = Path(prefix)
    checked, prefix_unverifiable = 0, []
    records = list((prefix / "conda-meta").glob("*.json"))
    if not records:
        raise ValueError("No Conda metadata for integrity check")
    for path in records:
        record = json.loads(path.read_text())
        entries = record.get("paths_data", {}).get("paths", [])
        if not entries:
            source = Path(record.get("link", {}).get("source", "")) / "info/paths.json"
            if source.is_file():
                entries = json.loads(source.read_text()).get("paths", [])
        if record.get("files") and not entries:
            raise ValueError(f"Missing file integrity evidence: {record['name']}")
        for entry in entries:
            relative = entry["_path"]
            if entry.get("path_type") == "softlink":
                continue
            digest = entry.get("sha256_in_prefix")
            if not digest and entry.get("prefix_placeholder"):
                prefix_unverifiable.append(relative)
                continue
            digest = digest or entry.get("sha256")
            if not digest:
                continue  # e.g. generated bytecode/directory; recorded separately
            target = prefix / relative
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Conda file overwritten or missing (integrity): {record['name']}: {relative}")
            checked += 1
    if not checked:
        raise ValueError("No Conda files had verifiable hashes")
    return {"status": "passed", "checked_files": checked,
            "prefix_relocated_without_installed_hash": prefix_unverifiable}


def _zero_energy(state):
    """Trusted API-only callback; force composition is tested later in G02."""
    import numpy as np
    return 0.0, np.zeros((len(state.getPositions()), 3))


def check_required_apis() -> dict:
    """Exercise the source-verified G00 APIs without loading neural weights."""
    for name, expected in REQUIRED_VERSIONS.items():
        actual = metadata.version(name)
        if actual.split("+")[0] != expected:
            raise RuntimeError(f"{name}: expected {expected}, installed {actual}")
    import openmm
    import torch
    from openmmml import MLPotential
    for owner, names in ((openmm.ATMForce, ("addForce", "getPerturbationEnergy")),
                         (openmm.PythonForce, ("getParticles", "setParticles")),
                         (openmm.XmlSerializer, ("serialize", "deserialize", "clone"))):
        for name in names:
            if not hasattr(owner, name):
                raise RuntimeError(f"Required API unavailable: {owner.__name__}.{name}")
    if "returnInfo" not in inspect.signature(MLPotential.createMixedSystem).parameters:
        raise RuntimeError("Required mixed-system returnInfo API unavailable")
    force = openmm.PythonForce(_zero_energy)
    force.setParticles([0])
    restored = openmm.XmlSerializer.deserialize(openmm.XmlSerializer.serialize(force))
    selected = list(restored.getParticles())
    if selected != [0]:
        raise RuntimeError("PythonForce particle subset lost during serialization")
    if torch.version.cuda is not None or getattr(torch.version, "hip", None) is not None:
        raise RuntimeError("Inherited CPU candidate unexpectedly has CUDA/HIP runtime")
    if str(torch.ones(1, device="cpu").device) != "cpu":
        raise RuntimeError("Explicit CPU tensor placement failed")
    return {"status": "passed", "python_force_selected_particles": selected,
            "mixed_system_return_info": True, "torch_backend": "cpu",
            "platforms": [openmm.Platform.getPlatform(i).getName()
                          for i in range(openmm.Platform.getNumPlatforms())]}
