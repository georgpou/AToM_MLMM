"""Parent's inert checks of the two remaining admissions, without estimation."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tests.sampling.test_exchange_uncertainty import make_synthetic_history, restrained_spec
from atm_mlmm import exchange_journal
from atm_mlmm.exchange_analysis import analyze_exchange
from atm_mlmm.schema import ExchangeResamplingSpec, IdentityError


class AdmissionReached(Exception):
    pass


outcomes = {}
with tempfile.TemporaryDirectory(prefix="parent-v2-verification-") as directory:
    root = Path(directory)
    first = make_synthetic_history(root, 0, seed=254347, frames=32)
    duplicate = make_synthetic_history(root, 1, seed=254347, frames=32)
    distinct = make_synthetic_history(root, 2, seed=278933, frames=32)
    for method in ("independent_runs", "synchronized_blocks"):
        spec = ExchangeResamplingSpec(method, 8 if method == "synchronized_blocks" else None,
                                      8, 99, "parent inert admission verification")
        with patch("atm_mlmm.exchange_analysis._fit_pairs", side_effect=AdmissionReached):
            try:
                analyze_exchange((first, duplicate), restrained_spec(), resampling=spec)
            except IdentityError as error:
                assert "initialization" in str(error)
                outcomes[f"{method}_duplicate"] = "rejected before estimation"
            else:
                raise AssertionError(f"duplicate histories admitted under {method}")
            try:
                analyze_exchange((first, distinct), restrained_spec(), resampling=spec)
            except AdmissionReached:
                outcomes[f"{method}_distinct"] = "admitted to estimation boundary"
            else:
                raise AssertionError(f"distinct histories did not reach fitting under {method}")

    source = Path(exchange_journal.__file__).resolve().parent
    journal = root / "journal"
    worker = journal / "worker"
    tree = worker / "runtime/source/atm_mlmm"
    files = {}
    for path in sorted(source.rglob("*.py")):
        target = tree / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        files[target.relative_to(worker).as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = worker / "manifest.json"
    manifest.write_text(json.dumps({"files": files}, sort_keys=True) + "\n")
    metadata = {"mode": "persistent-multistate-exchange-v1",
                "worker_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()}
    metadata_path = journal / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, sort_keys=True) + "\n")
    (journal / "metadata.sha256").write_text(hashlib.sha256(metadata_path.read_bytes()).hexdigest() + "\n")

    def check_reader(path, name, reject=False):
        # Stop after real metadata hashing and real source admission; this does
        # not fabricate a physically qualified journal or load copied code.
        with patch.object(exchange_journal, "_validate_multistate_metadata", side_effect=AdmissionReached):
            try:
                exchange_journal.read_multistate_boundaries(path)
            except IdentityError:
                assert reject, name
                outcomes[name] = "rejected at journal source admission"
            except AdmissionReached:
                assert not reject, name
                outcomes[name] = "passed journal source admission"
            else:
                raise AssertionError(name)

    check_reader(journal, "matching_source")
    relocated = root / "relocated-journal"
    shutil.move(journal, relocated)
    check_reader(relocated, "relocated_source")
    tree = relocated / "worker/runtime/source/atm_mlmm"
    extra = tree / "nested/undeclared.py"
    extra.parent.mkdir()
    extra.write_text("INERT_PARENT_VALUE = 1\n")
    check_reader(relocated, "undeclared_python_file", reject=True)
    extra.unlink()
    (tree / "undeclared-link.py").symlink_to(source / "schema.py")
    check_reader(relocated, "undeclared_python_symlink", reject=True)

print(json.dumps({"outcomes": outcomes, "checks": len(outcomes),
                  "estimation_or_dynamics_executed": False}, indent=2, sort_keys=True))
