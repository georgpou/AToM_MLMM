"""Bounded persistent multistate pilots on the immutable v2 water fixtures."""
from contextlib import ExitStack, contextmanager
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import threading
import time

import numpy as np
import pytest


REPOSITORY = Path(__file__).resolve().parents[2]
PILOTS = (
    pytest.param(
        "abfe", 224,
        "95442f332740badd917230a5d7fd96786640eb371383d184b3947405668a57ac",
        id="solvated-abfe-224",
    ),
    pytest.param(
        "rbfe", 233,
        "ea2accbd2902e9a3caa8eeea20deda99e2ff656bb3b7dac004b394950c11ecb9",
        id="unequal-ligand-rbfe-233",
    ),
)
GAS_CONSTANT_KJ_MOL_K = 0.00831446261815324
ENERGY_TOLERANCE_KJ_MOL = 1.0e-8


def _write_json(path, document):
    Path(path).write_text(json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _rss_bytes():
    try:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


@contextmanager
def _measure_process_window():
    """Sample parent-process RSS during one operation; report the scope plainly."""
    stop = threading.Event()
    samples = [_rss_bytes()]

    def sample_until_done():
        while not stop.wait(0.01):
            samples.append(_rss_bytes())

    monitor = threading.Thread(target=sample_until_done, name="g10-rss-sampler", daemon=True)
    started = time.perf_counter()
    monitor.start()
    metrics = {}
    try:
        yield metrics
    finally:
        stop.set()
        monitor.join()
        samples.append(_rss_bytes())
        values = [value for value in samples if value is not None]
        metrics.update(
            wall_seconds=time.perf_counter() - started,
            peak_process_rss_bytes=max(values) if values else None,
            rss_sampling_interval_seconds=0.01,
            rss_scope="pytest parent process VmRSS sampled during this operation; includes Python/test harness",
        )


def _snapshot(sample):
    from atm_mlmm.schema import Snapshot

    velocities = sample["velocities_nm_ps"]
    box = sample["box_nm"]
    return Snapshot(
        tuple(sample["real_atom_ids"]),
        tuple(tuple(row) for row in sample["positions_nm"]),
        None if box is None else tuple(tuple(row) for row in box),
        None if velocities is None else tuple(tuple(row) for row in velocities),
    )


def _assert_finite_raw(raw):
    required = {
        "u0_raw_kJ_mol",
        "u1_raw_kJ_mol",
        "delta_u_raw_kJ_mol",
        "delta_u_softcore_kJ_mol",
        "atm_expression_energy_kJ_mol",
        "outside_energy_kJ_mol",
        "system_total_energy_kJ_mol",
    }
    assert set(raw) == required
    assert all(math.isfinite(float(value)) for value in raw.values())
    assert raw["system_total_energy_kJ_mol"] == pytest.approx(
        raw["atm_expression_energy_kJ_mol"] + raw["outside_energy_kJ_mol"],
        abs=ENERGY_TOLERANCE_KJ_MOL,
        rel=0,
    )


def _tree_bytes(root):
    root = Path(root)
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _stale_coordinate_rejection_probe(run_root, probe_root, metadata, expected_atom_ids, state_ids, monkeypatch):
    """Reseal a portable/checkpoint-consistent stale coordinate and require early rejection."""
    import openmm as mm
    from openmm import unit

    from atm_mlmm.adapters.atom import WorkerRun, load_worker_run
    from atm_mlmm.exchange import resume_multistate_exchange
    from atm_mlmm.exchange_journal import read_multistate_boundaries, seal_tree
    from atm_mlmm.persistence import read_json
    from atm_mlmm.schema import IdentityError

    shutil.copytree(run_root, probe_root)
    final_index = metadata["boundaries"] - 1
    boundary = probe_root / "boundaries" / f"{final_index:06d}"
    checkpoint_path = boundary / "workers" / "worker-000.chk"
    state_path = boundary / "workers" / "worker-000-state.xml"
    final_permutation = read_json(boundary / "record.json")["walker_to_state_final"]
    state_id = state_ids[final_permutation[0]]
    original_checkpoint_sha256 = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    sample_positions = np.asarray(
        read_json(boundary / "samples" / "worker-000.json")["positions_nm"], dtype=float
    )
    with load_worker_run(
        probe_root / "worker",
        metadata["worker_manifest_sha256"],
        trusted=True,
        integrator_seed=metadata["integrator_seed_base"],
    ) as worker:
        atom_particle_indices = [
            worker.bundle.physical.real_to_final[atom_id] for atom_id in expected_atom_ids
        ]
        worker.restore_checkpoint(checkpoint_path.read_bytes(), state_id)
        context = worker.evaluator.context
        positions = context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        atom_index = worker.bundle.physical.real_to_final[expected_atom_ids[0]]
        positions[atom_index, 0] += 2.0e-12
        context.setPositions(positions * unit.nanometer)
        changed_state = context.getState(
            getPositions=True, getVelocities=True, getParameters=True
        )
        checkpoint_path.write_bytes(context.createCheckpoint())
        state_path.write_text(mm.XmlSerializer.serialize(changed_state))
        checkpoint_positions = np.asarray(
            changed_state.getPositions(asNumpy=True).value_in_unit(unit.nanometer), dtype=float
        )
    displacement_nm = float(np.max(np.abs(checkpoint_positions[atom_particle_indices] - sample_positions)))
    assert displacement_nm > 1.0e-15
    seal_tree(boundary, index=final_index)
    # The inert journal remains structurally and cryptographically valid; the
    # runtime stale-coordinate guard must reject the checkpoint/sample mismatch.
    assert len(read_multistate_boundaries(probe_root)) == metadata["boundaries"]

    evaluations = []
    original_evaluate = WorkerRun.evaluate

    def counted_evaluate(self, snapshot, requested_state_id):
        evaluations.append((self.integrator_seed, requested_state_id))
        return original_evaluate(self, snapshot, requested_state_id)

    monkeypatch.setattr(WorkerRun, "evaluate", counted_evaluate)
    with pytest.raises(IdentityError, match="beyond unit-conversion roundoff") as caught:
        resume_multistate_exchange(probe_root, trusted=True)
    assert evaluations == []
    assert not (probe_root / "pending").exists()
    _write_json(probe_root.parent / "stale-coordinate-rejection.json", {
        "case": probe_root.name,
        "tampered_worker_index": 0,
        "sample_coordinate_identity_preserved": True,
        "original_checkpoint_sha256": original_checkpoint_sha256,
        "resealed_checkpoint_sha256": hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(),
        "deliberate_coordinate_displacement_nm": displacement_nm,
        "guard_bound_nm": 1.0e-15,
        "inert_journal_validation": "passed after resealing the altered State/checkpoint pair",
        "runtime_rejection": str(caught.value),
        "worker_evaluate_calls_before_rejection": len(evaluations),
        "pending_transaction_created": False,
    })


@pytest.mark.parametrize("kind,atom_count,config_sha256", PILOTS)
def test_solvated_abfe_and_unequal_rbfe_multistate_pilot(
    tmp_path, kind, atom_count, config_sha256, monkeypatch
):
    """Run two actual v2 water pilots and independently check saved exchanges."""
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.exchange import resume_multistate_exchange, run_multistate_exchange
    from atm_mlmm.exchange_journal import read_multistate_boundaries
    from atm_mlmm.persistence import read_json
    from atm_mlmm.schema import EvaluationRecords, from_json
    from atm_mlmm.schedule import reduced_potentials
    from atm_mlmm.workflow import run_configuration

    source = REPOSITORY / "fixtures" / "solvated_fragment" / "v2" / kind
    source_config = source / "config.json"
    assert hashlib.sha256(source_config.read_bytes()).hexdigest() == config_sha256
    evidence_root = Path(os.environ.get("G10_PILOT_EVIDENCE", tmp_path / "g10-v5-pilots")).resolve()
    run_id = os.environ.get("G10_PILOT_RUN_ID", f"pytest-{os.getpid()}")
    case_root = evidence_root / run_id / kind
    case_root.mkdir(parents=True, exist_ok=False)
    fixture_copy = case_root / "fixture-input"
    shutil.copytree(source, fixture_copy)
    copied_hashes = {
        relative.as_posix(): hashlib.sha256((fixture_copy / relative).read_bytes()).hexdigest()
        for relative in (Path("manifest.json"), Path("system-input.json"), Path("partition.json"), Path("snapshot.json"))
    }

    config_path = fixture_copy / "config.json"
    config = json.loads(config_path.read_text())
    config["settings"].update(
        frames_per_state=1,
        steps_per_frame=1,
        steps_per_phase=1,
        minimization_iterations=3,
    )
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    preparation_root = case_root / "prepared-run"
    with _measure_process_window() as preparation_metrics:
        prepared_summary = run_configuration(config_path, preparation_root, trusted=True)

    worker_bundle = from_json((preparation_root / "worker" / "bundle.json").read_text())
    runtime = from_json((preparation_root / "worker" / "runtime.json").read_text())
    states = tuple(worker_bundle.schedule.states)
    state_ids = tuple(state.state_id for state in states)
    assert len(states) == 3
    assert worker_bundle.schedule.temperature_K == 300.0
    assert prepared_summary["samples"] == len(states)
    assert len(worker_bundle.physical.topology.atoms) == atom_count
    assert runtime.platform == "Reference"
    assert runtime.precision == "double"
    assert runtime.ensemble == "NVT"
    assert runtime.temperature_K == 300.0

    expected_atom_ids = tuple(atom.atom_id for atom in worker_bundle.physical.topology.atoms)
    cap_parent_ids = {
        parent
        for link in worker_bundle.physical.links
        for parent in (link.ml_parent_id, link.mm_parent_id)
    }
    assert cap_parent_ids
    atom_indices = {atom_id: index for index, atom_id in enumerate(expected_atom_ids)}
    assert cap_parent_ids <= set(atom_indices)
    ligand_molecules = tuple(
        molecule for molecule in worker_bundle.physical.topology.molecules if molecule.role == "ligand"
    )
    assert len(ligand_molecules) == (1 if kind == "abfe" else 2)
    assert all(set(molecule.atom_ids) <= set(expected_atom_ids) for molecule in ligand_molecules)
    mobile_membership = {
        atom_id
        for group in worker_bundle.transfer.protocol.mobile_groups
        for atom_id in group.atom_ids
    }
    assert all(set(molecule.atom_ids) <= mobile_membership for molecule in ligand_molecules)

    multistate_root = case_root / "multistate-run"
    replay_copy = case_root / "identical-prefix-replay"
    state_pairs = ((0, 1), (1, 2))
    with _measure_process_window() as prefix_metrics:
        prefix_summary = run_multistate_exchange(
            preparation_root,
            multistate_root,
            state_ids=state_ids,
            state_pairs=state_pairs,
            boundaries=2,
            steps_per_boundary=1,
            seed=247,
            trusted=True,
            stop_after_boundaries=1,
        )
    assert prefix_summary["status"] == "interrupted"
    assert prefix_summary["boundaries"] == 1
    assert prefix_summary["samples"] == 3

    prefix_paths = (multistate_root / "initial", multistate_root / "boundaries" / "000000")
    prefix_bytes = {path.name: _tree_bytes(path) for path in prefix_paths}
    shutil.copytree(multistate_root, replay_copy)
    assert _tree_bytes(replay_copy / "initial") == prefix_bytes["initial"]
    assert _tree_bytes(replay_copy / "boundaries" / "000000") == prefix_bytes["000000"]

    with _measure_process_window() as replay_metrics:
        replay_summary = resume_multistate_exchange(replay_copy, trusted=True)
    with _measure_process_window() as continuation_metrics:
        final_summary = resume_multistate_exchange(multistate_root, trusted=True)
    assert replay_summary["status"] == final_summary["status"] == "complete"
    assert replay_summary["boundaries"] == final_summary["boundaries"] == 2
    assert replay_summary["samples"] == final_summary["samples"] == 6

    # The copied prefix is byte-identical at fork time and remains immutable
    # after both serial continuations.
    assert _tree_bytes(multistate_root / "initial") == prefix_bytes["initial"]
    assert _tree_bytes(multistate_root / "boundaries" / "000000") == prefix_bytes["000000"]
    assert _tree_bytes(replay_copy / "initial") == prefix_bytes["initial"]
    assert _tree_bytes(replay_copy / "boundaries" / "000000") == prefix_bytes["000000"]
    assert read_multistate_boundaries(multistate_root) == read_multistate_boundaries(replay_copy)
    final_tree = _tree_bytes(multistate_root / "boundaries" / "000001")
    assert final_tree == _tree_bytes(replay_copy / "boundaries" / "000001")
    assert read_json(multistate_root / "boundaries" / "000001" / "rng.json") == read_json(
        replay_copy / "boundaries" / "000001" / "rng.json"
    )

    metadata = read_json(multistate_root / "metadata.json")
    assert metadata["mode"] == "persistent-multistate-exchange-v1"
    assert metadata["boundaries"] == 2
    assert metadata["steps_per_boundary"] == 1
    assert metadata["state_ids"] == list(state_ids)
    assert metadata["state_pairs"] == [[0, 1], [1, 2]]
    assert len(metadata["walker_ids"]) == 3
    assert len(set(metadata["walker_ids"])) == 3
    assert final_summary["walker_ids"] == metadata["walker_ids"]
    assert final_summary["binding_result"] == "not_evaluated"
    assert final_summary["attempts_per_boundary"] == 2
    assert final_summary["all_real_atoms"] == atom_count
    assert final_summary["reconstructed_matrix_shape"] == [3, 6]

    boundaries = read_multistate_boundaries(multistate_root)
    assert len(boundaries) == 2
    samples = [sample for boundary in boundaries for sample in boundary["samples"]]
    assert len(samples) == 6
    assert len({sample["sample_id"] for sample in samples}) == 6
    assert {sample["walker_id"] for sample in samples} == set(metadata["walker_ids"])
    assert {len(boundary["samples"]) for boundary in boundaries} == {3}
    sample_by_boundary_worker = {}
    for boundary_index, boundary in enumerate(boundaries):
        assert boundary["boundary_index"] == boundary_index
        start_permutation = boundary["walker_to_state_start"]
        final_permutation = boundary["walker_to_state_final"]
        assert sorted(start_permutation) == sorted(final_permutation) == [0, 1, 2]
        assert boundary["pair_count"] == 2
        assert {sample["state_id"] for sample in boundary["samples"]} == set(state_ids)
        assert len(boundary["attempts"]) == 2
        for worker_index, sample in enumerate(boundary["samples"]):
            assert sample["walker_index"] == worker_index
            assert sample["walker_id"] == metadata["walker_ids"][worker_index]
            assert sample["sequence_number"] == boundary_index + 1
            assert sample["sample_id"] == (
                f"{metadata['run_id']}:walker-{worker_index}:boundary-{boundary_index + 1}"
            )
            assert sample["state_id"] == state_ids[start_permutation[worker_index]]
            assert sample["real_atom_ids"] == list(expected_atom_ids)
            positions = np.asarray(sample["positions_nm"], dtype=float)
            velocities = np.asarray(sample["velocities_nm_ps"], dtype=float)
            forces = np.asarray(sample["real_forces_kj_mol_nm"], dtype=float)
            assert positions.shape == velocities.shape == forces.shape == (atom_count, 3)
            assert np.isfinite(positions).all()
            assert np.isfinite(velocities).all()
            assert np.isfinite(forces).all()
            assert all(np.isfinite(forces[atom_indices[parent]]).all() for parent in cap_parent_ids)
            assert sample["box_nm"] is not None
            assert np.asarray(sample["box_nm"], dtype=float).shape == (3, 3)
            assert np.isfinite(np.asarray(sample["box_nm"], dtype=float)).all()
            assert sample["temperature_K"] == 300.0
            expected_parameters = next(state.parameters for state in states if state.state_id == sample["state_id"])
            assert sample["parameters"] == dict(expected_parameters)
            _assert_finite_raw(sample["raw"])
            diagnostics = sample["domain"]
            map_diagnostics = [item for item in diagnostics if "map" in item]
            assert [item["map"] for item in map_diagnostics] == ["map0", "map1"]
            assert all(
                math.isfinite(item["minimum_intermolecular_Bondi_ratio"])
                and item["minimum_intermolecular_Bondi_ratio"] >= 0.65
                for item in map_diagnostics
            )
            assert all(
                "minimum_ligand_cap_distance_nm" in item
                and math.isfinite(item["minimum_ligand_cap_distance_nm"])
                for item in map_diagnostics
            )
            sample_by_boundary_worker[(boundary_index, worker_index)] = sample

    for worker_index in range(3):
        walker_samples = [
            sample for sample in samples if sample["walker_id"] == metadata["walker_ids"][worker_index]
        ]
        assert [sample["sequence_number"] for sample in walker_samples] == [1, 2]
        assert walker_samples[1]["step"] - walker_samples[0]["step"] == 1
        assert walker_samples[1]["time_ps"] - walker_samples[0]["time_ps"] == pytest.approx(
            runtime.timestep_ps, abs=1.0e-12, rel=0
        )

    attempted_count = 0
    oracle_rows = []
    with ExitStack() as stack:
        actual_workers = [
            stack.enter_context(
                load_worker_run(
                    multistate_root / "worker",
                    metadata["worker_manifest_sha256"],
                    trusted=True,
                    integrator_seed=metadata["integrator_seed_base"] + worker_index,
                )
            )
            for worker_index in range(3)
        ]
        reconstructed_records = from_json((multistate_root / "records.json").read_text())
        assert isinstance(reconstructed_records, EvaluationRecords)
        raw_reconstructed_matrix = reduced_potentials(reconstructed_records)
        actual_schedule_matrix = np.empty_like(raw_reconstructed_matrix)
        actual_raw_by_boundary_state_worker = {}
        actual_force_by_boundary_worker = {}
        for boundary_index, boundary in enumerate(boundaries):
            for worker_index in range(3):
                sample = sample_by_boundary_worker[(boundary_index, worker_index)]
                snapshot = _snapshot(sample)
                for state_index, state in enumerate(states):
                    evaluated = actual_workers[worker_index].evaluate(snapshot, state.state_id)
                    raw = asdict(evaluated.raw)
                    _assert_finite_raw(raw)
                    assert evaluated.parameters == dict(state.parameters)
                    actual_schedule_matrix[state_index, boundary_index * 3 + worker_index] = (
                        evaluated.total.energy_kj_mol
                        / (GAS_CONSTANT_KJ_MOL_K * worker_bundle.schedule.temperature_K)
                    )
                    actual_raw_by_boundary_state_worker[(boundary_index, state.state_id, worker_index)] = raw
                    outside = raw["outside_energy_kJ_mol"]
                    assert abs(outside) > 1.0e-10
                    if state.state_id == sample["state_id"]:
                        for field, value in raw.items():
                            assert sample["raw"][field] == pytest.approx(
                                value, abs=ENERGY_TOLERANCE_KJ_MOL, rel=0
                            )
                        saved_forces = np.asarray(sample["real_forces_kj_mol_nm"], dtype=float)
                        actual_forces = np.asarray(evaluated.total.forces_kj_mol_nm, dtype=float)
                        np.testing.assert_allclose(
                            saved_forces, actual_forces, atol=ENERGY_TOLERANCE_KJ_MOL, rtol=0
                        )
                        actual_force_by_boundary_worker[(boundary_index, worker_index)] = actual_forces
                        for parent in cap_parent_ids:
                            assert np.isfinite(actual_forces[atom_indices[parent]]).all()

            outside_by_worker = [
                actual_raw_by_boundary_state_worker[
                    (boundary_index, states[0].state_id, worker_index)
                ]["outside_energy_kJ_mol"]
                for worker_index in range(3)
            ]
            for state in states[1:]:
                for worker_index in range(3):
                    assert actual_raw_by_boundary_state_worker[
                        (boundary_index, state.state_id, worker_index)
                    ]["outside_energy_kJ_mol"] == pytest.approx(
                        outside_by_worker[worker_index], abs=ENERGY_TOLERANCE_KJ_MOL, rel=0
                    )

        np.testing.assert_allclose(
            raw_reconstructed_matrix,
            actual_schedule_matrix,
            atol=ENERGY_TOLERANCE_KJ_MOL,
            rtol=0,
        )

        for boundary_index, boundary in enumerate(boundaries):
            for attempt_index, attempt in enumerate(boundary["attempts"]):
                attempted_count += 1
                attempt_dir = (
                    multistate_root
                    / "boundaries"
                    / f"{boundary_index:06d}"
                    / "attempts"
                    / f"{attempt_index:04d}"
                )
                attempt_doc = read_json(attempt_dir / "attempt.json")
                evaluated_doc = read_json(attempt_dir / "evaluated.json")
                decision_doc = read_json(attempt_dir / "decision.json")
                refreshed_doc = read_json(attempt_dir / "refreshed.json")
                history_doc = read_json(attempt_dir / "history.json")
                state_pair_indices = state_pairs[attempt_index]
                assert attempt_doc["state_pair_indices"] == list(state_pair_indices)
                assert attempt_doc["state_ids"] == [state_ids[index] for index in state_pair_indices]
                selected_workers = [
                    attempt_doc["walker_to_state_before"].index(state_index)
                    for state_index in state_pair_indices
                ]
                assert attempt_doc["worker_indices"] == selected_workers
                assert attempt_doc["walker_ids"] == [metadata["walker_ids"][index] for index in selected_workers]
                assert attempt_doc["walker_to_state_before"] == attempt["walker_to_state_before"]
                assert attempt_doc["sample_ids"] == [
                    sample_by_boundary_worker[(boundary_index, index)]["sample_id"]
                    for index in selected_workers
                ]
                before = list(attempt_doc["walker_to_state_before"])
                expected_after = list(before)
                if decision_doc["accepted"]:
                    expected_after[selected_workers[0]], expected_after[selected_workers[1]] = (
                        expected_after[selected_workers[1]], expected_after[selected_workers[0]]
                    )
                assert sorted(before) == sorted(expected_after) == [0, 1, 2]
                assert decision_doc["walker_to_state_before"] == before
                assert decision_doc["walker_to_state_after"] == expected_after
                assert history_doc["walker_to_state_before"] == before
                assert history_doc["walker_to_state_after"] == expected_after
                assert refreshed_doc["walker_to_state_after"] == expected_after
                assert decision_doc["state_ids_after"] == [
                    state_ids[expected_after[worker_index]] for worker_index in selected_workers
                ]
                assert attempt["walker_to_state_after"] == expected_after
                assert attempt["attempt"]["worker_indices"] == selected_workers
                assert all(
                    expected_after[worker_index] == before[worker_index]
                    for worker_index in set(range(3)) - set(selected_workers)
                )

                actual_matrix = []
                actual_raw_matrix = []
                for state_id in attempt_doc["state_ids"]:
                    reduced_row = []
                    raw_row = []
                    for worker_index in selected_workers:
                        raw = actual_raw_by_boundary_state_worker[(
                            boundary_index, state_id, worker_index
                        )]
                        raw_row.append(raw)
                        reduced_row.append(
                            raw["system_total_energy_kJ_mol"]
                            / (GAS_CONSTANT_KJ_MOL_K * worker_bundle.schedule.temperature_K)
                        )
                    actual_matrix.append(reduced_row)
                    actual_raw_matrix.append(raw_row)
                np.testing.assert_allclose(
                    evaluated_doc["reduced_energies"], actual_matrix,
                    atol=ENERGY_TOLERANCE_KJ_MOL, rtol=0,
                )
                assert len(evaluated_doc["raw_energies"]) == len(actual_raw_matrix) == 2
                for state_row in range(2):
                    for walker_column in range(2):
                        saved_raw = evaluated_doc["raw_energies"][state_row][walker_column]
                        actual_raw = actual_raw_matrix[state_row][walker_column]
                        _assert_finite_raw(saved_raw)
                        for field, value in actual_raw.items():
                            assert saved_raw[field] == pytest.approx(
                                value, abs=ENERGY_TOLERANCE_KJ_MOL, rel=0
                            )
                exponent = (
                    actual_matrix[0][1] + actual_matrix[1][0]
                    - actual_matrix[0][0] - actual_matrix[1][1]
                )
                assert evaluated_doc["exponent"] == pytest.approx(
                    exponent, abs=ENERGY_TOLERANCE_KJ_MOL, rel=0
                )
                assert decision_doc["exponent"] == pytest.approx(
                    exponent, abs=ENERGY_TOLERANCE_KJ_MOL, rel=0
                )
                assert decision_doc["accepted"] is attempt["accepted"]
                assert refreshed_doc["energies_after_kj_mol"] == pytest.approx(
                    [
                        actual_raw_by_boundary_state_worker[(
                            boundary_index,
                            state_ids[expected_after[worker_index]],
                            worker_index,
                        )]["system_total_energy_kJ_mol"]
                        for worker_index in selected_workers
                    ],
                    abs=ENERGY_TOLERANCE_KJ_MOL,
                    rel=0,
                )
                oracle_rows.append({
                    "boundary_index": boundary_index,
                    "attempt_index": attempt_index,
                    "state_pair_indices": list(state_pair_indices),
                    "worker_indices": selected_workers,
                    "reduced_energies_actual_context": actual_matrix,
                    "raw_energies_actual_context": actual_raw_matrix,
                    "exponent_actual_context": exponent,
                    "accepted": bool(decision_doc["accepted"]),
                })

    assert attempted_count == 4
    assert final_summary["accepted_exchanges"] == sum(bool(attempt["accepted"]) for boundary in boundaries for attempt in boundary["attempts"])
    run_configuration_after = {
        relative.as_posix(): hashlib.sha256((fixture_copy / relative).read_bytes()).hexdigest()
        for relative in (Path("manifest.json"), Path("system-input.json"), Path("partition.json"), Path("snapshot.json"))
    }
    assert run_configuration_after == copied_hashes
    metrics = {
        "preparation": preparation_metrics,
        "initial_one_boundary_prefix": prefix_metrics,
        "continued_replay_copy_to_two_boundaries": replay_metrics,
        "continued_original_to_two_boundaries": continuation_metrics,
        "pilot_scope": "serial CPU technical execution; includes the prepared-run handoff and two-boundary committed prefix",
        "machine_memory_limit_bytes": int(Path("/sys/fs/cgroup/memory.max").read_text().strip())
        if Path("/sys/fs/cgroup/memory.max").is_file()
        and Path("/sys/fs/cgroup/memory.max").read_text().strip().isdigit()
        else None,
    }
    _write_json(case_root / "resource-metrics.json", metrics)
    _write_json(case_root / "actual-context-oracle.json", {
        "case": kind,
        "state_ids": list(state_ids),
        "ordered_state_pairs": [list(pair) for pair in state_pairs],
        "energy_tolerance_kJ_mol": ENERGY_TOLERANCE_KJ_MOL,
        "full_schedule_matrix_reconstruction_shape": list(raw_reconstructed_matrix.shape),
        "full_schedule_matrix_max_abs_error_reduced_energy": float(
            np.max(np.abs(raw_reconstructed_matrix - actual_schedule_matrix))
        ),
        "attempted_pair_matrices": oracle_rows,
        "sample_count": len(samples),
        "pair_attempt_count": attempted_count,
        "nonzero_outside_anchor_energy_count": sum(
            abs(raw["outside_energy_kJ_mol"]) > 1.0e-10
            for raw in actual_raw_by_boundary_state_worker.values()
        ),
        "cap_parent_atom_ids": sorted(cap_parent_ids),
        "cap_parent_forces_checked_from_saved_samples": len(actual_force_by_boundary_worker),
        "binding_result": "not_evaluated",
    })
    _stale_coordinate_rejection_probe(
        multistate_root,
        case_root / "stale-coordinate-probe",
        metadata,
        expected_atom_ids,
        state_ids,
        monkeypatch,
    )
    _write_json(case_root / "pilot-check.json", {
        "case": kind,
        "real_atom_count": atom_count,
        "input_config_original_sha256": config_sha256,
        "input_manifest_sha256": hashlib.sha256((fixture_copy / "manifest.json").read_bytes()).hexdigest(),
        "copied_input_hashes_unchanged": copied_hashes,
        "worker_ids": metadata["walker_ids"],
        "schedule_state_ids": list(state_ids),
        "committed_boundaries": 2,
        "steps_per_worker_per_boundary": 1,
        "sample_count": len(samples),
        "pair_attempt_count": attempted_count,
        "prefix_replay_equal": True,
        "prefix_bytes_preserved": True,
        "final_boundary_tree_byte_equal": True,
        "raw_full_schedule_reconstruction_matches_actual_contexts": True,
        "binding_result": "not_evaluated",
    })
