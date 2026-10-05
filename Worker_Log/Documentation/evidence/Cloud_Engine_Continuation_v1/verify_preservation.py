"""Read-only baseline check for the administrative engine handoff cleanup.

Run from the repository root with Python's standard library. Symlinks are
compared as Git stores them, including historical links to unavailable scratch.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess


BASE = "2c02cc2713924140a82aefda37fd5885747e5837"
PROTECTED = ("src/", "tests/", "fixtures/", "models/", "environment/cloud-cpu/", "Worker_Log/")
EXCEPTIONS = {
    "src/atm_mlmm/tpu_experiment.py",
    "tests/environment/test_tpu_experiment.py",
    "tests/environment/test_m05_notebooks.py",
    "Worker_Log/Documentation/M05_Colab_Handoff_v1_worker.md",
    "Worker_Log/Milestone_05/M05-colab-implementation-plan.md",
    "Worker_Log/Milestone_05/Gate_09_v5_worker.md",
    "Worker_Log/Milestone_05/Gate_10_v2_audit.md",
}


def main():
    expected, modes = {}, {}
    rows = subprocess.check_output(["git", "ls-tree", "-r", BASE], text=True).splitlines()
    for row in rows:
        meta, name = row.split("\t", 1)
        if name.startswith(PROTECTED) and name not in EXCEPTIONS:
            mode, _, oid = meta.split()
            expected[name], modes[name] = oid, mode
    regular = [name for name in expected if modes[name] != "120000"]
    hashes = subprocess.check_output(
        ["git", "hash-object", "--stdin-paths"],
        input="\n".join(regular) + "\n", text=True,
    ).splitlines()
    assert len(hashes) == len(regular)
    actual = dict(zip(regular, hashes))
    for name in expected:
        if modes[name] == "120000":
            content = os.fsencode(os.readlink(name))
            actual[name] = hashlib.sha1(
                b"blob " + str(len(content)).encode() + b"\0" + content
            ).hexdigest()
    changed = [name for name in expected if expected[name] != actual[name]]
    assert not changed, changed
    target = f"https://github.com/georgpou/AToM_MLMM/blob/{BASE}/notebooks/README.md"
    for name in ("Gate_09_v5_worker.md", "Gate_10_v2_audit.md"):
        path = "Worker_Log/Milestone_05/" + name
        original = subprocess.check_output(["git", "show", BASE + ":" + path], text=True)
        assert original.count("(../../notebooks/README.md)") == 1
        assert Path(path).read_text() == original.replace(
            "(../../notebooks/README.md)", "(" + target + ")"
        ), path
    spec = "docs/project-0/specs/m05-dense-exchange-amendment.md"
    original = subprocess.check_output(["git", "show", BASE + ":" + spec], text=True)
    assert Path(spec).read_text().split("## Accepted CPU scope")[0] == original.split("## TPU scope")[0]
    print(json.dumps({
        "base": BASE,
        "preserved_tracked_files": len(expected),
        "preserved_symlinks": sum(mode == "120000" for mode in modes.values()),
        "changed": changed,
        "explicit_cleanup_exceptions": sorted(EXCEPTIONS),
        "historical_report_changes": "two link targets only; original records remain in Git",
        "accepted_scientific_definition": "unchanged before withdrawn optional experiment section",
        "quantum_ledger_sha256": hashlib.sha256(Path(
            "Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1/progress.json"
        ).read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
