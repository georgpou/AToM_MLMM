import pytest


def test_ns_per_day_uses_declared_timestep_and_step_seconds():
    from atm_mlmm.benchmark import ns_per_day

    assert ns_per_day(0.5, 0.1) == pytest.approx(0.432, abs=1e-15, rel=0)


@pytest.mark.parametrize("timestep,seconds", [(0.0, 1.0), (-0.5, 1.0), (0.5, 0.0), (0.5, -1.0)])
def test_ns_per_day_rejects_nonpositive_inputs(timestep, seconds):
    from atm_mlmm.benchmark import ns_per_day

    with pytest.raises(ValueError):
        ns_per_day(timestep, seconds)


def test_benchmark_summary_separates_startup_and_repeat_variability():
    from atm_mlmm.benchmark import summarize_case

    row = summarize_case(
        case="all-mm",
        context_startup_seconds=2.0,
        model_load_seconds=None,
        first_evaluation_seconds=0.4,
        repeated_evaluation_seconds=[0.1, 0.2, 0.3],
        timestep_fs=0.5,
        per_worker=True,
        aggregate_simulated_ns=None,
        total_cpu_seconds=None,
    )
    assert row["repeat_count"] == 3
    assert row["repeated_mean_seconds"] == pytest.approx(0.2)
    assert row["repeated_min_seconds"] == pytest.approx(0.1)
    assert row["repeated_max_seconds"] == pytest.approx(0.3)
    assert row["ns_per_day"] == pytest.approx(0.0864 * 0.5 / 0.2)
    assert row["context_startup_seconds"] == 2.0
    assert row["first_evaluation_seconds"] == 0.4
    assert row["per_worker"] is True
    assert row["aggregate_simulated_ns"] is None


def test_serial_replicas_are_not_double_counted_as_aggregate_throughput():
    from atm_mlmm.benchmark import serial_resource_totals

    result = serial_resource_totals([{"wall_seconds": 2.0, "cpu_seconds": 1.8,
                                      "simulated_ns": 0.01},
                                     {"wall_seconds": 3.0, "cpu_seconds": 2.9,
                                      "simulated_ns": 0.01}])
    assert result == {"serial_wall_seconds": 5.0, "total_cpu_seconds": 4.7,
                      "aggregate_simulated_ns": 0.02,
                      "aggregate_ns_per_day": pytest.approx(345.6)}
