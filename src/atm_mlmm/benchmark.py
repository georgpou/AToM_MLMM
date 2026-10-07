"""Small, explicit resource metric helpers used by the release benchmark."""
from __future__ import annotations

import math
import statistics


def ns_per_day(timestep_fs: float, step_seconds: float) -> float:
    """Convert a measured step duration at an unchanged timestep to ns/day."""
    if (isinstance(timestep_fs, bool) or isinstance(step_seconds, bool)
            or not math.isfinite(float(timestep_fs)) or not math.isfinite(float(step_seconds))
            or timestep_fs <= 0 or step_seconds <= 0):
        raise ValueError("timestep_fs and step_seconds must be finite positive values")
    return 0.0864 * float(timestep_fs) / float(step_seconds)


def summarize_case(*, case, context_startup_seconds, model_load_seconds,
                   first_evaluation_seconds, repeated_evaluation_seconds,
                   timestep_fs, per_worker, aggregate_simulated_ns,
                   total_cpu_seconds):
    repeated = tuple(float(value) for value in repeated_evaluation_seconds)
    if not repeated or any(not math.isfinite(value) or value <= 0 for value in repeated):
        raise ValueError("at least one finite positive repeated evaluation is required")
    mean = statistics.fmean(repeated)
    if type(per_worker) is not bool:
        raise ValueError("per_worker must be an explicit boolean")
    if aggregate_simulated_ns is not None and aggregate_simulated_ns < 0:
        raise ValueError("aggregate simulated time must be nonnegative")
    if total_cpu_seconds is not None and total_cpu_seconds < 0:
        raise ValueError("total CPU time must be nonnegative")
    return {
        "case": str(case),
        "context_startup_seconds": context_startup_seconds,
        "model_load_seconds": model_load_seconds,
        "first_evaluation_seconds": first_evaluation_seconds,
        "repeat_count": len(repeated),
        "repeated_mean_seconds": mean,
        "repeated_min_seconds": min(repeated),
        "repeated_max_seconds": max(repeated),
        "repeated_stdev_seconds": statistics.stdev(repeated) if len(repeated) > 1 else 0.0,
        "timestep_fs": float(timestep_fs),
        "ns_per_day": ns_per_day(timestep_fs, mean),
        "per_worker": per_worker,
        "aggregate_simulated_ns": aggregate_simulated_ns,
        "total_cpu_seconds": total_cpu_seconds,
    }


def serial_resource_totals(runs):
    """Sum serial wall/CPU/simulated time without multiplying throughput."""
    rows = tuple(runs)
    if not rows:
        raise ValueError("at least one run receipt is required")
    wall = sum(float(row["wall_seconds"]) for row in rows)
    cpu = sum(float(row["cpu_seconds"]) for row in rows)
    simulated = sum(float(row["simulated_ns"]) for row in rows)
    return {
        "serial_wall_seconds": wall,
        "total_cpu_seconds": cpu,
        "aggregate_simulated_ns": simulated,
        "aggregate_ns_per_day": None if wall <= 0 else simulated * 86400.0 / wall,
    }
