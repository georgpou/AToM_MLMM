"""Certificate override must survive main activation on non-Debian hosts."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_main_activation_preserves_explicit_certificate_bundle(tmp_path):
    setup = tmp_path / "setup"
    profile = setup / "conda/etc/profile.d"
    profile.mkdir(parents=True)
    # The test isolates shell configuration, without installing Conda or packages.
    (profile / "conda.sh").write_text("conda() { :; }\n")
    shutil.copy2(ROOT / "environment/cloud-cpu/activate.sh", setup / "activate.sh")
    certificate = tmp_path / "system-ca.pem"
    certificate.write_text("test CA path only; no network use\n")
    env = dict(os.environ, ATOM_MLMM_CA_BUNDLE=str(certificate))
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-c",
         'source "$1/activate.sh"; printf "%s\\n" "$SSL_CERT_FILE" "$REQUESTS_CA_BUNDLE" "$PIP_CERT" "$GIT_SSL_CAINFO"',
         "test", str(setup)], env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout.splitlines() == [str(certificate)] * 4


@pytest.mark.parametrize("generated_root", [".runtime", ".tmp"])
def test_documentation_walk_prunes_local_installed_environment(tmp_path, generated_root):
    import importlib.util
    spec = importlib.util.spec_from_file_location("project_doc_checker", ROOT / "tools/check_docs.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    (tmp_path / "README.md").write_text("# Project\n")
    installed = tmp_path / generated_root / "env/site-packages/third_party"
    installed.mkdir(parents=True)
    (installed / "README.md").write_text("[third-party link](absent.md)\n")
    report = checker.check(tmp_path)
    assert report["errors"] == []
    assert report["counts"]["markdown_files"] == 1


def test_repository_local_temporary_path_supports_multiprocessing_sockets(tmp_path):
    import sys
    certificate = tmp_path / "ca.pem"
    certificate.write_text("fixture path only; no network use\n")
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-c",
         'source "$1"; "$2" -c "from multiprocessing.connection import Listener; listener=Listener(); listener.close()"',
         "test", str(ROOT / "environment/hpc/cosmos/settings.sh"), sys.executable],
        capture_output=True, text=True,
        env=dict(os.environ, ATOM_MLMM_CA_BUNDLE=str(certificate)),
    )
    assert result.returncode == 0, result.stderr
