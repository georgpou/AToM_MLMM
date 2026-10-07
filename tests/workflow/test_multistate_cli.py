import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def _cli(*args, cwd=ROOT):
    import os
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    environment.update(OPENBLAS_NUM_THREADS="2", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
    return subprocess.run([sys.executable, "-m", "atm_mlmm", *map(str, args)],
                          cwd=cwd, env=environment, capture_output=True, text=True, timeout=30)


def test_existing_module_command_and_new_multistate_help_are_preserved():
    help_result = _cli("--help")
    assert help_result.returncode == 0
    for command in ("exchange-multistate", "resume-multistate", "analyze"):
        assert command in help_result.stdout
    check = _cli("check", ROOT / "fixtures/cloud_host_guest/v2/config.json")
    assert check.returncode == 0, check.stdout + check.stderr
    assert json.loads(check.stdout)["status"] == "valid"


def test_multistate_cli_requires_explicit_trust_before_loading(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"state_ids": ["a", "b", "c"],
                                "state_pairs": [["a", "b"], ["b", "c"]],
                                "boundaries": 1, "steps_per_boundary": 1, "seed": 41}))
    result = _cli("exchange-multistate", tmp_path / "prepared", plan,
                  "--output", tmp_path / "run")
    assert result.returncode == 2
    assert "explicitly trusted" in result.stderr
    assert not (tmp_path / "run").exists()


def test_multistate_plan_rejects_missing_explicit_count_or_pair_graph(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"state_ids": ["a", "b", "c"], "seed": 41}))
    result = _cli("exchange-multistate", tmp_path / "prepared", plan,
                  "--output", tmp_path / "run", "--trusted")
    assert result.returncode == 2
    assert "must contain exactly" in result.stderr


def test_analysis_cli_rejects_incomplete_serialized_inputs(tmp_path):
    document = tmp_path / "analysis.json"
    document.write_text(json.dumps({"histories": [], "thermodynamics": {}, "resampling": {}}))
    result = _cli("analyze", document)
    assert result.returncode == 2
    assert "nonempty list" in result.stderr


def test_analysis_cli_roundtrips_explicit_synthetic_records(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import to_json
    from tests.sampling.test_exchange_uncertainty import make_synthetic_history, restrained_spec

    history = make_synthetic_history(tmp_path, 0, seed=104729, frames=32)
    thermodynamics = restrained_spec()
    resampling = ExchangeResamplingSpec(
        "synchronized_blocks", 8, 8, 91,
        "fixtures/analytic/exchange-analysis-v1/design.json")
    expected = analyze_exchange((history,), thermodynamics, resampling=resampling,
                                estimator="pymbar")
    input_file = tmp_path / "analysis.json"
    input_file.write_text(json.dumps({
        "histories": [json.loads(to_json(history))],
        "thermodynamics": json.loads(to_json(thermodynamics)),
        "resampling": json.loads(to_json(resampling)),
        "estimator": "pymbar",
    }))

    result = _cli("analyze", input_file)

    assert result.returncode == 0, result.stdout + result.stderr
    output = json.loads(result.stdout)
    assert output["scope"].startswith("explicit exchange analysis")
    assert output["analysis_result"] == json.loads(to_json(expected))
