#!/usr/bin/env python
"""Print or run only the bounded post-E checks reserved by the orchestrator."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FOCUSED = [
    [sys.executable, "-m", "pytest", "tests/workflow/test_release_bundle.py",
     "tests/contracts/test_release_evidence.py", "tests/unit/test_benchmark_metrics.py",
     "tests/environment/test_hpc_profile.py", "-q"],
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-focused", action="store_true",
                        help="run only the listed bounded E checks; never launches the full suite")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if not args.run_focused:
        print(json.dumps({"mode": "dry_run", "commands": FOCUSED,
                          "full_suite": "parent-owned single run",
                          "hidden_jobs": False}, indent=2))
        return 0
    outcomes = []
    for command in FOCUSED:
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        outcomes.append({"argv": command, "exit_code": process.returncode,
                         "stdout": process.stdout, "stderr": process.stderr})
        if process.returncode:
            break
    result = {"mode": "bounded_focused", "outcomes": outcomes,
              "full_suite": "not_run", "hidden_jobs": False}
    payload = json.dumps(result, indent=2)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload + "\n")
    print(payload)
    return 0 if all(item["exit_code"] == 0 for item in outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
