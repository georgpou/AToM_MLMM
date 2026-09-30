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


def _complete_manifest():
    from atm_mlmm.persistence import REQUIRED_VERSIONS, SOURCE_TAGS, REQUIRED_CHECKS
    packages = [{"name": name, "version": version, "origin": None}
                for name, version in REQUIRED_VERSIONS.items()]
    for package in packages:
        if package["name"] in SOURCE_TAGS:
            url = "https://github.com/openmm/openmm-ml.git" if package["name"] == "openmmml" else "https://github.com/Gallicchio-Lab/AToM-OpenMM.git"
            package["origin"] = {"url": url, "vcs_info": {"commit_id": "a" * 40,
                                             "requested_revision": SOURCE_TAGS[package["name"]]}}
    return {"schema_version": 1, "python": {"version": "3.11.13", "build": ["main", "date"]},
            "platform": {"system": "Linux", "machine": "x86_64", "release": "6.8"},
            "repository": {"commit": "b" * 40, "working_tree": ""}, "candidate_sha256": "c" * 64,
            "artifact_hashes": {name: "e" * 64 for name in ("conda-explicit.txt", "pip-wheels.lock", "source-origins.json")},
            "conda_packages": [{"name": "python", "version": "3.11.13", "build": "example",
                                "url": "https://example.invalid/python.conda", "sha256": "d" * 64}],
            "packages": packages, "checks": {name: {"exit_code": 0} for name in REQUIRED_CHECKS},
            "installation_status": "installed", "qualification_status": "not_qualified"}


@pytest.mark.parametrize("field", ["python", "platform", "repository", "candidate_sha256"])
def test_manifest_requires_runtime_and_input_identity(field):
    from atm_mlmm.persistence import validate_environment_manifest
    report = _complete_manifest()
    del report[field]
    with pytest.raises(ValueError, match="identity|Python|platform|candidate|repository"):
        validate_environment_manifest(report)


def test_manifest_rejects_wrong_installed_source_wheel_hash():
    from atm_mlmm.persistence import validate_environment_manifest
    report = _complete_manifest()
    package = next(p for p in report["packages"] if p["name"] == "openmmml")
    package["origin"] = {"archive_info": {"hashes": {"sha256": "a" * 64}}}
    report["archived_source_origins"] = {"openmmml": {"vcs_info": {"commit_id": "b" * 40},
                                                      "wheel_sha256": "c" * 64}}
    with pytest.raises(ValueError, match="source wheel"):
        validate_environment_manifest(report)


def test_complete_manifest_is_accepted_for_installation_only():
    from atm_mlmm.persistence import validate_environment_manifest
    validate_environment_manifest(_complete_manifest())


@pytest.mark.parametrize("mutation", ["conda_digest", "candidate_digest", "source_url", "source_tag", "artifacts"])
def test_manifest_rejects_unverifiable_provenance(mutation):
    from atm_mlmm.persistence import validate_environment_manifest
    report = _complete_manifest()
    if mutation == "conda_digest":
        report["conda_packages"][0]["sha256"] = "x"
    elif mutation == "candidate_digest":
        report["candidate_sha256"] = "x"
    elif mutation == "artifacts":
        report["artifact_hashes"] = {}
    else:
        source = next(p["origin"] for p in report["packages"] if p["name"] == "openmmml")
        if mutation == "source_url": source["url"] = "https://wrong.invalid/repo.git"
        else: source["vcs_info"]["requested_revision"] = "main"
    with pytest.raises(ValueError):
        validate_environment_manifest(report)


def test_conda_integrity_rejects_overwritten_file(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    import hashlib
    prefix = tmp_path
    (prefix / "conda-meta").mkdir()
    (prefix / "metadata").write_text("original")
    record = {"name": "example", "files": ["metadata"], "paths_data": {"paths": [
        {"_path": "metadata", "path_type": "hardlink",
         "sha256": hashlib.sha256(b"original").hexdigest()}]}}
    (prefix / "conda-meta/example.json").write_text(json.dumps(record))
    assert verify_conda_files(prefix)["checked_files"] == 1
    (prefix / "metadata").write_text("overwritten")
    with pytest.raises(ValueError, match="overwritten|integrity"):
        verify_conda_files(prefix)


def test_conda_integrity_uses_relocated_hash(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    import hashlib
    (tmp_path / "conda-meta").mkdir()
    (tmp_path / "metadata").write_text("relocated")
    record = {"name": "example", "files": ["metadata"], "paths_data": {"paths": [
        {"_path": "metadata", "path_type": "hardlink", "prefix_placeholder": "/old/prefix",
         "sha256": hashlib.sha256(b"original").hexdigest(),
         "sha256_in_prefix": hashlib.sha256(b"relocated").hexdigest()}]}}
    (tmp_path / "conda-meta/example.json").write_text(json.dumps(record))
    assert verify_conda_files(tmp_path)["checked_files"] == 1


def test_bootstrap_refuses_existing_evidence_before_solver(tmp_path):
    script = Path(__file__).parents[2] / "environment/bootstrap_cpu.sh"
    result = subprocess.run(["bash", str(script), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Evidence path already exists" in result.stderr


def test_qualification_refuses_stale_checks(tmp_path):
    script = Path(__file__).parents[2] / "environment/qualify_cpu.sh"
    (tmp_path / "solver.exit").write_text("0\n")
    (tmp_path / "project_install.exit").write_text("0\n")
    result = subprocess.run(["bash", str(script), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "fresh successful solve" in result.stderr


def _bytecode_fixture(prefix):
    import hashlib
    (prefix / "conda-meta").mkdir()
    source = prefix / "lib/python3.11/example.py"
    cache = source.parent / "__pycache__/example.cpython-311.pyc"
    cache.parent.mkdir(parents=True)
    source.write_bytes(b"value = 1\n")
    cache.write_bytes(b"regenerated cache")
    entries = [
        {"_path": source.relative_to(prefix).as_posix(), "path_type": "hardlink",
         "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        {"_path": cache.relative_to(prefix).as_posix(), "path_type": "hardlink",
         "sha256": hashlib.sha256(b"packaged cache").hexdigest()},
    ]
    (prefix / "conda-meta/example.json").write_text(json.dumps(
        {"name": "example", "files": [p["_path"] for p in entries],
         "paths_data": {"paths": entries}}))
    return source, cache


def test_conda_integrity_records_regenerated_source_backed_cache(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    _, cache = _bytecode_fixture(tmp_path)
    report = verify_conda_files(tmp_path)
    assert report["checked_files"] == 1
    assert report["regenerable_bytecode"] == [cache.relative_to(tmp_path).as_posix()]


def test_conda_integrity_still_rejects_changed_bytecode_source(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    source, _ = _bytecode_fixture(tmp_path)
    source.write_bytes(b"value = 2\n")
    with pytest.raises(ValueError, match="overwritten|integrity"):
        verify_conda_files(tmp_path)


def test_conda_integrity_does_not_exempt_sourceless_bytecode(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    _, cache = _bytecode_fixture(tmp_path)
    record_path = tmp_path / "conda-meta/example.json"
    record = json.loads(record_path.read_text())
    record["paths_data"]["paths"] = [record["paths_data"]["paths"][1]]
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="overwritten|integrity"):
        verify_conda_files(tmp_path)


def _collision_fixture(prefix, relative="lib/python3.11/site-packages/docs/conf.py",
                       names=("openff-utilities", "openff-toolkit-base")):
    import hashlib
    (prefix / "conda-meta").mkdir()
    target = prefix / relative
    target.parent.mkdir(parents=True)
    for index, name in enumerate(names):
        content = f"package = {index}\n".encode()
        target.write_bytes(content)
        record = {"name": name, "files": [relative], "paths_data": {"paths": [
            {"_path": relative, "path_type": "hardlink",
             "sha256": hashlib.sha256(content).hexdigest()}]}}
        (prefix / f"conda-meta/{name}.json").write_text(json.dumps(record))
    return target


def test_conda_integrity_records_known_documentation_collision(tmp_path):
    from atm_mlmm.persistence import verify_conda_files
    target = _collision_fixture(tmp_path)
    report = verify_conda_files(tmp_path)
    collision, = report["documented_collisions"]
    assert collision["path"] == target.relative_to(tmp_path).as_posix()
    assert {owner["name"] for owner in collision["owners"]} == {
        "openff-utilities", "openff-toolkit-base"}
    assert report["checked_files"] == 1


@pytest.mark.parametrize("kind", ["unknown_owner", "runtime_module", "unrecorded_hash"])
def test_conda_integrity_rejects_unapproved_collision(tmp_path, kind):
    from atm_mlmm.persistence import verify_conda_files
    names = ("openff-utilities", "openff-toolkit-base")
    relative = "lib/python3.11/site-packages/docs/conf.py"
    if kind == "unknown_owner":
        names = ("unknown-package", "openff-toolkit-base")
    elif kind == "runtime_module":
        relative = "lib/python3.11/site-packages/openff/example.py"
    target = _collision_fixture(tmp_path, relative=relative, names=names)
    if kind == "unrecorded_hash":
        target.write_bytes(b"not any installed package")
    with pytest.raises(ValueError, match="overwritten|integrity"):
        verify_conda_files(tmp_path)


def test_qualification_refuses_failed_solver_before_install(tmp_path):
    import os
    script = Path(__file__).parents[2] / "environment/qualify_cpu.sh"
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "solver.exit").write_text("1\n")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python"
    fake_python.write_text("#!/bin/sh\nexit 91\n")
    fake_python.chmod(0o755)
    result = subprocess.run(["bash", str(script), str(evidence)],
                            env={**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]},
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "fresh successful solve" in result.stderr
    assert not (evidence / "project_install.exit").exists()


def test_archive_keeps_conda_distribution_without_record(tmp_path, monkeypatch):
    import importlib.util
    import sys
    from importlib import metadata
    script = Path(__file__).parents[2] / "tools/archive_pip.py"
    spec = importlib.util.spec_from_file_location("archive_pip_under_test", script)
    archive = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archive)
    prefix = tmp_path / "prefix"
    dist_info = prefix / "lib/python3.11/site-packages/jaxlib-0.9.0.dist-info"
    dist_info.mkdir(parents=True)
    (dist_info / "METADATA").write_text("Name: jaxlib\nVersion: 0.9.0\n")
    (dist_info / "direct_url.json").write_text(json.dumps({
        "url": "file:///conda-build/work/dist/jaxlib.whl",
        "archive_info": {"hashes": {"sha256": "a" * 64}}}))
    (prefix / "conda-meta").mkdir()
    (prefix / "conda-meta/jaxlib.json").write_text(json.dumps({
        "name": "jaxlib",
        "files": [str((dist_info / "METADATA").relative_to(prefix))]}))
    dist = metadata.PathDistribution(dist_info)
    assert dist.files is None  # Conda need not retain the wheel RECORD.
    output = tmp_path / "output"
    output.mkdir()
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(sys, "argv", [str(script), str(output)])
    monkeypatch.setattr(archive.metadata, "distributions", lambda: [dist])
    monkeypatch.setattr(archive.subprocess, "run", lambda *args, **kwargs: None)
    archive.main()
    assert (output / "pip-source-lock.txt").read_text().strip() == ""
    assert json.loads((output / "source-origins.json").read_text()) == {}


def test_archive_does_not_treat_neighboring_pip_metadata_as_conda_owned(tmp_path, monkeypatch):
    import importlib.util
    import sys
    from importlib import metadata
    script = Path(__file__).parents[2] / "tools/archive_pip.py"
    spec = importlib.util.spec_from_file_location("archive_pip_under_test", script)
    archive = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archive)
    prefix = tmp_path / "prefix"
    site = prefix / "lib/python3.11/site-packages"
    conda_info = site / "jaxlib-0.9.0.dist-info"
    pip_info = site / "ase-3.29.0.dist-info"
    for path, name, version in ((conda_info, "jaxlib", "0.9.0"), (pip_info, "ase", "3.29.0")):
        path.mkdir(parents=True)
        (path / "METADATA").write_text(f"Name: {name}\nVersion: {version}\n")
    (prefix / "conda-meta").mkdir()
    (prefix / "conda-meta/jaxlib.json").write_text(json.dumps({
        "name": "jaxlib", "files": [(conda_info / "METADATA").relative_to(prefix).as_posix()]}))
    output = tmp_path / "output"
    output.mkdir()
    def fake_run(args, **kwargs):
        if "wheel" in args:
            wheelhouse = Path(args[args.index("--wheel-dir") + 1])
            (wheelhouse / "ase-3.29.0-py3-none-any.whl").write_bytes(b"fixture wheel")
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(sys, "argv", [str(script), str(output)])
    monkeypatch.setattr(archive.metadata, "distributions",
                        lambda: [metadata.PathDistribution(conda_info), metadata.PathDistribution(pip_info)])
    monkeypatch.setattr(archive.subprocess, "run", fake_run)
    archive.main()
    assert (output / "pip-source-lock.txt").read_text().strip() == "ase==3.29.0"
    assert "ase-3.29.0" in (output / "pip-wheels.lock").read_text()
