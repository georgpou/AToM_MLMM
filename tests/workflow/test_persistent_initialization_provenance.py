"""Persistent independent-run identity comes from saved state and RNG streams."""
from __future__ import annotations

import hashlib
import shutil

import pytest


def _analysis_input(run_dir, evidence_path, *, initialization_claim="identity derived from journal artifacts"):
    from atm_mlmm.exchange_journal import read_multistate_boundaries
    from atm_mlmm.persistence import read_json, write_json
    from atm_mlmm.schema import ExchangeAnalysisInput, from_json

    metadata = read_json(run_dir / "metadata.json")
    rows = read_multistate_boundaries(run_dir)
    frames = tuple(tuple(sample["sample_id"] for sample in row["samples"]) for row in rows)
    write_json(evidence_path, {
        "format": "exchange-retained-window-v1",
        "version": 1,
        "source_kind": "persistent_multistate_journal",
        "run_id": metadata["run_id"],
        "boundary_source": str(run_dir),
        "retained_frames": [list(frame) for frame in frames],
        "excluded_frames": [],
        "selection_evidence": "all two bounded persistent boundaries retained",
        "independent_initialization_evidence": initialization_claim,
    })
    records = from_json((run_dir / "records.json").read_text())
    return ExchangeAnalysisInput(records, frames, metadata["run_id"], str(evidence_path))


def _run(prepared, output, *, host_seed):
    from atm_mlmm.exchange import run_multistate_exchange

    return run_multistate_exchange(
        prepared, output, state_ids=("first", "middle", "third"),
        state_pairs=((0, 1), (1, 2)), boundaries=2,
        steps_per_boundary=1, seed=host_seed, trusted=True)


def _analysis_contract(method="independent_runs"):
    from atm_mlmm.schema import ExchangeResamplingSpec, ThermodynamicSpec

    states = ("first", "middle", "third")
    thermo = ThermodynamicSpec(
        "restrained_free_energy", {states[0]: -1.0, states[2]: 1.0},
        "endpoint_difference", ((states[0], states[1]), (states[1], states[2])),
        {states[0]: "initial test state", states[2]: "final test state"},
        (), (), None, "bounded provenance control", "none", "none", "none")
    if method == "synchronized_blocks":
        resampling = ExchangeResamplingSpec(
            "synchronized_blocks", 1, 2, 19, "bounded persistent initialization control")
    else:
        resampling = ExchangeResamplingSpec(
            "independent_runs", None, 2, 19, "bounded persistent initialization control")
    return thermo, resampling


@pytest.fixture(scope="module")
def persistent_stream_cases(tmp_path_factory):
    from atm_mlmm.exchange_analysis import _validate_window
    from atm_mlmm.persistence import read_json, write_json
    from tests.workflow.test_persistent_exchange import prepare_multistate

    tmp_path = tmp_path_factory.mktemp("persistent-initialization")
    prepared = prepare_multistate(tmp_path / "prepared")
    duplicate_a = tmp_path / "duplicate-a"
    duplicate_b = tmp_path / "duplicate-b"
    distinct_host = tmp_path / "distinct-host-rng"
    distinct_integrator = tmp_path / "distinct-integrator-rng"
    distinct_state = tmp_path / "distinct-state"
    _run(prepared, duplicate_a, host_seed=73)
    _run(prepared, duplicate_b, host_seed=73)
    _run(prepared, distinct_host, host_seed=74)

    integrator_prepared = tmp_path / "prepared-integrator-distinct"
    shutil.copytree(prepared, integrator_prepared)
    metadata_path = integrator_prepared / "metadata.json"
    metadata = read_json(metadata_path)
    metadata["settings"]["seed"] = 43
    write_json(metadata_path, metadata)
    (integrator_prepared / "metadata.sha256").write_text(
        hashlib.sha256(metadata_path.read_bytes()).hexdigest() + "\n")
    _run(integrator_prepared, distinct_integrator, host_seed=73)
    state_prepared = prepare_multistate(
        tmp_path / "prepared-state-distinct", initial_shift_nm=(0.01, 0., 0.))
    _run(state_prepared, distinct_state, host_seed=73)

    duplicate_inputs = (
        _analysis_input(duplicate_a, tmp_path / "duplicate-a-window.json"),
        _analysis_input(duplicate_b, tmp_path / "duplicate-b-window.json",
                        initialization_claim="claimed distinct stream label"),
    )
    distinct_host_inputs = (duplicate_inputs[0],
                            _analysis_input(distinct_host, tmp_path / "distinct-host-window.json"))
    distinct_integrator_inputs = (duplicate_inputs[0],
                                  _analysis_input(distinct_integrator,
                                                  tmp_path / "distinct-integrator-window.json"))
    distinct_state_inputs = (
        duplicate_inputs[0],
        _analysis_input(distinct_state, tmp_path / "distinct-state-window.json"),
    )
    duplicate_a_metadata = read_json(duplicate_a / "metadata.json")
    duplicate_b_metadata = read_json(duplicate_b / "metadata.json")
    duplicate_a_initialization = _validate_window(duplicate_inputs[0])["initialization_identity"]
    duplicate_b_initialization = _validate_window(duplicate_inputs[1])["initialization_identity"]
    distinct_host_initialization = _validate_window(distinct_host_inputs[1])["initialization_identity"]
    distinct_integrator_initialization = _validate_window(
        distinct_integrator_inputs[1])["initialization_identity"]
    distinct_state_initialization = _validate_window(distinct_state_inputs[1])["initialization_identity"]
    assert duplicate_a_metadata["run_id"] != duplicate_b_metadata["run_id"]
    assert duplicate_a_metadata["walker_ids"] != duplicate_b_metadata["walker_ids"]
    assert duplicate_a_initialization == duplicate_b_initialization
    duplicate_state = (duplicate_a / "initial" / "workers" / "worker-000-state.xml").read_bytes()
    for run_dir in (distinct_host, distinct_integrator):
        changed_stream_state = (run_dir / "initial" / "workers" / "worker-000-state.xml").read_bytes()
        assert hashlib.sha256(duplicate_state).digest() == hashlib.sha256(changed_stream_state).digest()
    assert read_json(duplicate_a / "initial" / "rng.json") != read_json(distinct_host / "initial" / "rng.json")
    assert duplicate_a_metadata["integrator_seed_base"] == read_json(distinct_host / "metadata.json")["integrator_seed_base"]
    assert distinct_host_initialization != duplicate_a_initialization
    assert read_json(duplicate_a / "initial" / "rng.json") == read_json(distinct_integrator / "initial" / "rng.json")
    assert duplicate_a_metadata["integrator_seed_base"] != read_json(distinct_integrator / "metadata.json")["integrator_seed_base"]
    assert distinct_integrator_initialization != duplicate_a_initialization
    distinct_state_state = (distinct_state / "initial" / "workers" / "worker-000-state.xml").read_bytes()
    assert hashlib.sha256(duplicate_state).digest() != hashlib.sha256(distinct_state_state).digest()
    assert read_json(duplicate_a / "initial" / "rng.json") == read_json(distinct_state / "initial" / "rng.json")
    assert duplicate_a_metadata["integrator_seed_base"] == read_json(distinct_state / "metadata.json")["integrator_seed_base"]
    assert distinct_state_initialization != duplicate_a_initialization

    return {
        "duplicate_inputs": duplicate_inputs,
        "distinct_inputs": (distinct_host_inputs, distinct_integrator_inputs, distinct_state_inputs),
    }


@pytest.mark.parametrize("method", ("independent_runs", "synchronized_blocks"))
def test_persistent_analyzer_rejects_duplicate_producer_streams_but_accepts_distinct_streams(
        persistent_stream_cases, method):
    from atm_mlmm.exchange_analysis import analyze_exchange
    from atm_mlmm.schema import IdentityError, QualificationError

    thermo, resampling = _analysis_contract(method)
    duplicate_inputs = persistent_stream_cases["duplicate_inputs"]
    with pytest.raises(IdentityError, match="initialization"):
        analyze_exchange(duplicate_inputs, thermo, resampling=resampling)

    for changed_inputs in persistent_stream_cases["distinct_inputs"]:
        try:
            analyze_exchange(changed_inputs, thermo, resampling=resampling)
        except IdentityError as error:
            assert "initialization" not in str(error)
        except QualificationError:
            pass  # Two retained boundaries test stream admission, not sampling adequacy.
