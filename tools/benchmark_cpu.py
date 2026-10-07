#!/usr/bin/env python
"""Run predeclared evaluation commands in fresh serial CPU processes.

Each JSON case has: name, argv, cwd, source_identity, model_identity,
input_identity, profile_identity, timestep_fs, context_startup_seconds,
model_load_seconds, first_evaluation_seconds, repeated_evaluations (8).
The command must print one JSON object with wall_seconds, cpu_seconds,
peak_rss_bytes and simulated_ns. No shell is used to interpret argv.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atm_mlmm.benchmark import ns_per_day, serial_resource_totals


def measure_case(row):
    repeated = row.get("repeated_evaluations")
    if repeated != 8:
        raise ValueError("steady fixed-coordinate benchmarks require exactly eight evaluations")
    command = row.get("argv")
    if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
        raise ValueError("case argv must be a nonempty string list")
    environment = os.environ.copy()
    environment.update(OPENBLAS_NUM_THREADS="2", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
    started = time.perf_counter()
    process = subprocess.run(command, cwd=row.get("cwd", str(ROOT)), env=environment,
                             text=True, capture_output=True, timeout=180)
    wall = time.perf_counter() - started
    if process.returncode:
        raise RuntimeError(f"{row['name']} exited {process.returncode}: {process.stderr[-2000:]}")
    try:
        raw = json.loads(process.stdout.splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise ValueError(f"{row['name']} must print a final JSON receipt") from exc
    required = {"wall_seconds", "cpu_seconds", "peak_rss_bytes", "simulated_ns",
                "evaluation_seconds", "step_seconds"}
    if not required.issubset(raw) or len(raw["evaluation_seconds"]) != 8:
        raise ValueError(f"{row['name']} receipt must contain eight measured fixed-coordinate evaluations")
    mean = sum(raw["evaluation_seconds"]) / 8
    cpu_model = platform.processor()
    if not cpu_model and Path("/proc/cpuinfo").is_file():
        for line in Path("/proc/cpuinfo").read_text(errors="replace").splitlines():
            if line.lower().startswith(("model name", "hardware")) and ":" in line:
                cpu_model = line.split(":", 1)[1].strip()
                if cpu_model:
                    break
    return {
        "case": row["name"], "argv": command, "cwd": row.get("cwd", str(ROOT)),
        "source_identity": raw.get("source_identity", row.get("source_identity")),
        "model_identity": raw.get("model_identity", row.get("model_identity")),
        "input_identity": raw.get("input_identity", row.get("input_identity")),
        "profile_identity": raw.get("profile_identity", row.get("profile_identity")),
        "cpu_model": cpu_model or platform.machine(),
        "cpu_architecture": platform.machine(),
        "thread_environment": {key: environment.get(key) for key in
                               ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        "context_startup_seconds": raw.get("context_startup_seconds"),
        "model_load_seconds": raw.get("model_load_seconds"),
        "first_evaluation_seconds": raw.get("first_evaluation_seconds"),
        "repeated_evaluations": raw["evaluation_seconds"],
        "repeat_count": 8, "repeated_mean_seconds": mean,
        "repeated_min_seconds": min(raw["evaluation_seconds"]),
        "repeated_max_seconds": max(raw["evaluation_seconds"]),
        "timestep_fs": row["timestep_fs"],
        "step_seconds_per_step": raw["step_seconds"],
        "ns_per_day": ns_per_day(row["timestep_fs"], raw["step_seconds"]),
        "worker_wall_seconds": raw["wall_seconds"], "process_wall_seconds": wall,
        "process_cpu_seconds": raw["cpu_seconds"], "peak_rss_bytes": raw["peak_rss_bytes"],
        "real_atoms": raw.get("real_atoms"), "ml_atoms": raw.get("ml_atoms"),
        "caps": raw.get("caps"),
        "per_worker_rate": True, "aggregate_simulated_ns": raw["simulated_ns"],
        "scope": "one fresh serial process; fixed coordinates except declared tiny steps",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path, help="explicit JSON list of fresh-process benchmark cases")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark case list must be nonempty")
    if args.dry_run:
        print(json.dumps({"mode": "dry_run", "cases": [row.get("name") for row in cases],
                          "fresh_process_per_case": True, "submission": False}, indent=2))
        return 0
    results = [measure_case(row) for row in cases]
    summary = serial_resource_totals([{"wall_seconds": row["process_wall_seconds"],
                                       "cpu_seconds": row["process_cpu_seconds"],
                                       "simulated_ns": row["aggregate_simulated_ns"]}
                                      for row in results])
    document = {"format": "atom-mlmm-cpu-benchmark-v1", "cases": results,
                "serial_totals": summary,
                "qualification": "resource measurements only; no optimization or physics promotion"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
