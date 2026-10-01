"""Check real Git fallback selection, checkout preservation and exit status."""
import os
from pathlib import Path
import subprocess

import pytest


def git(directory, *arguments):
    return subprocess.check_output(
        ["git", "-C", str(directory), *arguments], text=True, stderr=subprocess.PIPE,
    ).strip()


@pytest.mark.parametrize("installer_status", [0, 17])
def test_cloud_fallback_uses_current_development_branch(tmp_path, installer_status):
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "fixture-base")
    (seed / "README.md").write_text("fixture\n")
    git(seed, "add", ".")
    git(seed, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-q", "-m", "base")
    for branch, marker in [
        ("m01-g00-cloud-environment-setup", "obsolete-setup"),
        ("m01-g00-environment-audit-v1", "current-development"),
    ]:
        git(seed, "switch", "-q", "-c", branch, "fixture-base")
        installer = seed / "environment/cloud-cpu/install.sh"
        installer.parent.mkdir(parents=True)
        installer.write_text(
            '#!/usr/bin/env bash\nset -eu\n'
            f'printf "%s\\n" "{marker}" > "$ATOM_MLMM_TEST_RECEIPT"\n'
            'exit "$ATOM_MLMM_TEST_STATUS"\n'
        )
        git(seed, "add", ".")
        git(seed, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-q", "-m", marker)
    git(seed, "switch", "-q", "fixture-base")
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "clone", "-q", str(seed), str(checkout)], check=True)
    before = (git(checkout, "rev-parse", "HEAD"), git(checkout, "status", "--porcelain"))
    receipt = tmp_path / "receipt"
    hook = Path(__file__).resolve().parents[2] / "environment/cloud-cpu/cloud-install.sh"
    environment = os.environ | {
        "ATOM_MLMM_REPOSITORY": str(checkout),
        "ATOM_MLMM_TEST_RECEIPT": str(receipt),
        "ATOM_MLMM_TEST_STATUS": str(installer_status),
    }
    completed = subprocess.run(["bash", str(hook)], env=environment,
                               capture_output=True, text=True, timeout=30)
    assert receipt.read_text().strip() == "current-development", completed.stderr
    assert completed.returncode == installer_status, completed.stdout + completed.stderr
    assert (git(checkout, "rev-parse", "HEAD"), git(checkout, "status", "--porcelain")) == before
    assert (checkout / "README.md").read_text() == "fixture\n"
    assert not (checkout / "environment").exists()
