"""Preserve every check's output and exit status; keep docs failures explicit."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=Path(os.environ.get("ATOM_MLMM_SETUP_ROOT", Path(__file__).resolve().parent)))
parser.add_argument("--repository", type=Path, default=Path(os.environ.get("ATOM_MLMM_REPOSITORY", Path.cwd())))
parser.add_argument("--environment-only", action="store_true", help="Still run/report docs, but base exit status on environment checks only.")
args = parser.parse_args()
root, repo = args.root.resolve(), args.repository.resolve()
python, amber = str(root / "env/bin/python"), str(root / "amber-env/bin/python")
run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{os.getpid()}"
logs = root / "logs" / f"validation-{run_id}"
logs.mkdir(parents=True)
prep = logs / "prep"
prep.mkdir()
checks = [
    ("core_exact_versions", [python, str(root / "check_versions.py"), str(root), "core"], repo),
    ("amber_exact_versions", [amber, str(root / "check_versions.py"), str(root), "amber"], repo),
    ("core_pip_check", [python, "-m", "pip", "check"], repo),
    ("amber_pip_check", [amber, "-m", "pip", "check"], repo),
    ("openmm_installation", [python, "-m", "openmm.testInstallation"], repo),
    ("cpu_potentials_and_atm", [python, str(root / "smoke_cpu.py")], repo),
    ("separate_ambertools_integration", [python, str(root / "smoke_prep.py")], prep),
    ("atom_uwham", [python, "-m", "pytest", "-q", "tests/test_uwham.py"], root / "sources/AToM-OpenMM"),
    ("repository_documentation", [python, "tools/check_docs.py", "--self-test"], repo),
]
results = []
for name, command, cwd in checks:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
        status, output = completed.returncode, completed.stdout + completed.stderr
    except OSError as exc:
        status, output = 127, str(exc) + "\n"
    (logs / f"{name}.log").write_text(output)
    results.append(dict(name=name, command=command, cwd=str(cwd), exit_code=status, output=output))
    print(f"{name}: exit {status}", flush=True)
    if status:
        print(output, flush=True)
environment_ok = all(item["exit_code"] == 0 for item in results if item["name"] != "repository_documentation")
docs_ok = results[-1]["exit_code"] == 0
data = dict(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            profile="core-analytic-cpu development installation; no weights or gate acceptance",
            root=str(root), repository=str(repo), environment_ok=environment_ok,
            documentation_ok=docs_ok, environment_only_exit=args.environment_only, results=results)
(logs / "results.json").write_text(json.dumps(data, indent=2) + "\n")
(root / "latest-validation.json").write_text(json.dumps(data, indent=2) + "\n")
print(f"Environment checks: {'PASS' if environment_ok else 'FAIL'}; documentation: {'PASS' if docs_ok else 'FAIL'}")
print(f"Full results: {logs / 'results.json'}")
sys.exit(0 if environment_ok and (docs_ok or args.environment_only) else 1)
