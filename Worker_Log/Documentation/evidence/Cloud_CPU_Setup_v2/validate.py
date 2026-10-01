"""Record readiness checks and each underlying exit status independently."""
import datetime
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parent
repo = Path(os.environ.get("ATOM_MLMM_REPOSITORY", "/workspace/AToM_MLMM"))
python = str(root / "env/bin/python")
checks = [
    ("core_pip_check", [python, "-m", "pip", "check"], repo),
    ("amber_pip_check", [str(root / "amber-env/bin/python"), "-m", "pip", "check"], repo),
    ("openmm_installation", [python, "-m", "openmm.testInstallation"], repo),
    ("cpu_potentials_and_atm", [python, str(root / "smoke_cpu.py")], repo),
    ("separate_ambertools_integration", [python, str(root / "smoke_prep.py")], root / "prep-smoke"),
    ("atom_uwham", [python, "-m", "pytest", "-q", "tests/test_uwham.py"], root / "sources/AToM-OpenMM"),
    ("repository_documentation", [python, "tools/check_docs.py", "--self-test"], repo),
]
results = []
for name, command, cwd in checks:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    (root / f"final-{name}.log").write_text(result.stdout + result.stderr)
    results.append({"name": name, "command": command, "cwd": str(cwd),
                    "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    print(f"{name}: exit {result.returncode}", flush=True)
data = {"finished": datetime.datetime.now(ZoneInfo("Europe/Copenhagen")).isoformat(),
        "scope": "CPU development installation only; no weights or scientific gate qualification",
        "results": results}
(root / "validation-target-v2.json").write_text(json.dumps(data, indent=2) + "\n")
raise SystemExit(0 if all(result["exit_code"] == 0 for result in results) else 1)
