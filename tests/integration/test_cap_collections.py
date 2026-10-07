"""Weight-free collection and full-coordinate controls for Before HPC Batch B."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import openmm as mm
from openmm import unit
import pytest

from tests.cap_collection_oracle import DATA, IDS, analytic_force_answer, input_case


class FaultyCollectionCallback:
    def __init__(self, normal, *, omit_cap=None, omit_environment=None):
        self.normal = normal
        self.omit_cap = omit_cap
        self.omit_environment = omit_environment

    def __call__(self, state):
        energy, forces = self.normal(state)
        if self.omit_cap is not None:
            forces[self.omit_cap] = 0.
        if self.omit_environment is not None:
            forces[self.omit_environment] = 0.
        return energy, forces


def collection_probe():
    from atm_mlmm.models.analytic_caps import CapCollectionProbe, CapParameters, LigandTerm

    return CapCollectionProbe(
        cap_parameters=(
            CapParameters("p1_ml", "p1_mm", 6.0, (.12, .16, -.08), "p1_env", 2.5),
            CapParameters("p2_ml", "p2_mm", 8.0, (.53, .12, .14), "p2_env", 3.5),
        ),
        ligand_terms=(
            LigandTerm("lA_c", 2.0, (.23, .76, .02)),
            LigandTerm("lB_c", 1.5, (.62, .72, .04)),
        ),
    )


def collection_model_spec(probe):
    from atm_mlmm.schema import ModelSpec

    locality = "environment_dependent" if probe.environment_dependent else "local"
    return ModelSpec("analytic-cap-collection", None, "declared_relative_energy",
                     ("H", "C"), "neutral_singlet", locality, "float64")


def build_collection(probe=None, *, mixed_zero_cut=False):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec

    original, spec, snapshot = input_case(mixed_zero_cut=mixed_zero_cut)
    resolved = resolve_partition(original.topology, spec)
    probe = collection_probe() if probe is None else probe
    bundle = build_physical(
        original, resolved, collection_model_spec(probe),
        EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
        probe=probe, cap_distance_nm=DATA["cap_distance_nm"],
    )
    return bundle, snapshot, probe


def model_result(bundle, snapshot, *, system=None):
    from atm_mlmm.atm import physical_system
    from atm_mlmm.geometry import final_positions

    system = physical_system(bundle) if system is None else system
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName("Reference"))
    try:
        context.setPositions(final_positions(bundle, snapshot) * unit.nanometer)
        context.computeVirtualSites()
        state = context.getState(getEnergy=True, getForces=True, getPositions=True, groups=1 << 2)
        energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        forces = state.getForces(asNumpy=True).value_in_unit(
            unit.kilojoule_per_mole / unit.nanometer
        )
        return float(energy), forces[list(bundle.old_to_new)], state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    finally:
        del context, integrator


def oracle_terms(probe):
    caps = []
    for term in probe.cap_parameters:
        cap_id = "cap:" + __import__("hashlib").sha256(
            (term.ml_parent_id + "\0" + term.mm_parent_id).encode()
        ).hexdigest()
        caps.append({
            "cap_id": cap_id,
            "ml_parent_id": term.ml_parent_id,
            "mm_parent_id": term.mm_parent_id,
            "cap_k": term.cap_k,
            "center_nm": term.cap_center_nm,
            "environment_id": term.environment_id,
            "environment_k": term.environment_k,
            "distance_nm": DATA["cap_distance_nm"],
        })
    environments = tuple({
        "model_id": term.model_id,
        "environment_id": term.environment_id,
        "k": term.k,
    } for term in probe.environment_terms)
    ligands = tuple({
        "atom_id": term.atom_id,
        "k": term.k,
        "center_nm": term.center_nm,
    } for term in probe.ligand_terms)
    return caps, environments, ligands


def test_two_cap_collection_probe_matches_independent_per_edge_force_oracle():
    bundle, snapshot, probe = build_collection()
    caps, environments, ligands = oracle_terms(probe)
    expected_energy, expected_forces, expected_caps = analytic_force_answer(
        snapshot.positions_nm, cap_terms=caps,
        direct_environment_terms=environments, ligand_terms=ligands,
    )
    actual_energy, actual_forces, final_positions = model_result(bundle, snapshot)
    assert len(bundle.links) == 2
    assert abs(actual_energy - expected_energy) <= 1e-8
    np.testing.assert_allclose(actual_forces, expected_forces, rtol=0, atol=1e-7)
    for link in bundle.links:
        assert np.linalg.norm(final_positions[link.final_particle_index] - expected_caps[link.cap_id]) <= 1e-12
    assert np.linalg.norm(actual_forces[IDS.index("p1_env")]) > 1e-4
    assert np.linalg.norm(actual_forces[IDS.index("p2_env")]) > 1e-4


def test_zero_cut_mixed_collection_keeps_model_to_mm_environment_derivative():
    from atm_mlmm.models.analytic_caps import CapCollectionProbe, EnvironmentTerm, LigandTerm

    probe = CapCollectionProbe(
        cap_parameters=(),
        environment_terms=(EnvironmentTerm("lA_c", "p1_env", 4.0),),
        ligand_terms=(LigandTerm("lB_c", 1.25, (.6, .75, .0)),),
    )
    bundle, snapshot, probe = build_collection(probe, mixed_zero_cut=True)
    caps, environments, ligands = oracle_terms(probe)
    expected_energy, expected_forces, _ = analytic_force_answer(
        snapshot.positions_nm, cap_terms=caps,
        direct_environment_terms=environments, ligand_terms=ligands,
    )
    actual_energy, actual_forces, _ = model_result(bundle, snapshot)
    assert bundle.links == ()
    assert set(bundle.ml_atom_ids) < set(IDS)
    assert abs(actual_energy - expected_energy) <= 1e-8
    np.testing.assert_allclose(actual_forces, expected_forces, rtol=0, atol=1e-7)
    assert np.linalg.norm(actual_forces[IDS.index("p1_env")]) > 1e-4
    assert bundle.manifest["retained_mm_xml"]


def test_two_cap_parent_cartesian_derivatives_both_maps():
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.rbfe import make_protocol
    from atm_mlmm.schedule import linear_schedule
    from atm_mlmm.schema import MobileGroup, RestraintSpec, RuntimeSpec
    from tests.link_permutation import plain_result

    bundle, snapshot, probe = build_collection()
    group_a = MobileGroup("A", ("lA_c", "lA_h1", "lA_h2"), ("ligand",), "ligand-A")
    group_b = MobileGroup("B", ("lB_c", "lB_h1", "lB_h2", "lB_h3"), ("ligand",), "ligand-B")
    transfer = resolve_protocol(bundle, make_protocol((group_a, group_b), (.04, -.025, .015)))
    schedule = linear_schedule((("map0", 0.), ("map1", 1.)))
    restraint = RestraintSpec("zero-spring-control", ("lA_c",), 0., DATA["positions_nm"][IDS.index("lA_c")])
    atm = build_atm(bundle, transfer, schedule, restraint)
    runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "Verlet")
    retained = mm.XmlSerializer.deserialize(bundle.manifest["retained_mm_xml"])
    cap_terms, environment_terms, ligand_terms = oracle_terms(probe)
    base = np.asarray(snapshot.positions_nm, dtype=float)
    parent_ids = ("p1_ml", "p1_mm", "p2_ml", "p2_mm", "p1_env", "p2_env")
    expected_by_map = {}
    for state_id, displacement in (
            ("map0", transfer.displacement0_nm), ("map1", transfer.displacement1_nm)):
        real_displacements = np.asarray([
            displacement[bundle.real_to_final[atom_id]] for atom_id in IDS
        ])
        mapped = base + real_displacements
        expected_mm_energy, expected_mm_forces = plain_result(retained, mapped)
        expected_model_energy, expected_model_forces, expected_caps = analytic_force_answer(
            mapped, cap_terms=cap_terms,
            direct_environment_terms=environment_terms, ligand_terms=ligand_terms,
        )
        expected_by_map[state_id] = (
            expected_mm_energy + expected_model_energy,
            expected_mm_forces + expected_model_forces,
            expected_caps,
        )
    assert abs(expected_by_map["map0"][0] - expected_by_map["map1"][0]) > 1e-6

    with AtmEvaluator(atm, runtime) as evaluator:
        for state_id in ("map0", "map1"):
            expected_energy, expected_forces, expected_caps = expected_by_map[state_id]
            result = evaluator.evaluate(snapshot, state_id)
            assert abs(result.total.energy_kj_mol - expected_energy) <= 1e-4
            np.testing.assert_allclose(result.total.forces_kj_mol_nm, expected_forces,
                                       rtol=0, atol=5e-3)
            assert abs(result.raw.u0_raw_kJ_mol - expected_by_map["map0"][0]) <= 1e-4
            assert abs(result.raw.u1_raw_kJ_mol - expected_by_map["map1"][0]) <= 1e-4
            final = evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            for link in bundle.links:
                np.testing.assert_allclose(final[link.final_particle_index],
                                           expected_caps[link.cap_id], rtol=0, atol=1e-12)

            reference_components = np.asarray([
                expected_forces[IDS.index(atom_id), axis]
                for atom_id in parent_ids for axis in range(3)
            ])
            rms_reference = float(np.sqrt(np.mean(reference_components**2)))
            errors_by_step = []
            for step_nm in (1e-3, 1e-4, 1e-5):
                estimates = []
                for atom_id in parent_ids:
                    atom = IDS.index(atom_id)
                    for axis in range(3):
                        plus, minus = base.copy(), base.copy()
                        plus[atom, axis] += step_nm
                        minus[atom, axis] -= step_nm
                        e_plus = evaluator.evaluate(replace(snapshot, positions_nm=plus), state_id).total.energy_kj_mol
                        e_minus = evaluator.evaluate(replace(snapshot, positions_nm=minus), state_id).total.energy_kj_mol
                        estimates.append(-(e_plus-e_minus)/(2*step_nm))
                component_errors = np.asarray(estimates) - reference_components
                errors_by_step.append(float(np.sqrt(np.mean(component_errors**2))))
            evaluator.evaluate(snapshot, state_id)
            assert errors_by_step[-1] <= 1e-3 + 1e-4*rms_reference, errors_by_step
            assert errors_by_step[-1] <= errors_by_step[0] + 1e-6, errors_by_step


@pytest.mark.model_assets
def test_approved_mace_two_cap_fixed_coordinate_parent_derivatives():
    """One fixed-coordinate derivative check; this is not chemistry acceptance."""
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec, RuntimeSpec

    original, spec, snapshot = input_case()
    bundle = build_physical(
        original, resolve_partition(original.topology, spec), model_spec(),
        EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
        probe=None, cap_distance_nm=DATA["cap_distance_nm"],
    )
    assert len(bundle.links) == 2
    runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "Verlet")
    parent_ids = ("p1_ml", "p1_mm", "p2_ml", "p2_mm", "p1_env", "p2_env")
    with PhysicalEvaluator(bundle, runtime) as evaluator:
        reference = evaluator.evaluate(snapshot)
        forces = np.asarray(reference.forces_kj_mol_nm)
        errors_by_step = []
        for step_nm in (1e-4, 1e-5):
            errors = []
            for atom_id in parent_ids:
                atom = IDS.index(atom_id)
                for axis in range(3):
                    energies = []
                    for sign in (1., -1.):
                        positions = np.asarray(snapshot.positions_nm, dtype=float).copy()
                        positions[atom, axis] += sign * step_nm
                        energies.append(evaluator.evaluate(
                            replace(snapshot, positions_nm=positions)
                        ).energy_kj_mol)
                    estimate = -(energies[0] - energies[1]) / (2 * step_nm)
                    errors.append(estimate - forces[atom, axis])
            errors_by_step.append(float(np.sqrt(np.mean(np.square(errors)))))
        selected_force = np.asarray([
            forces[IDS.index(atom_id), axis]
            for atom_id in parent_ids for axis in range(3)
        ])
        rms_reference = float(np.sqrt(np.mean(np.square(selected_force))))
        limit = 1e-3 + 1e-4 * rms_reference
        assert errors_by_step[-1] <= limit, (errors_by_step, rms_reference, limit)
        assert errors_by_step[-1] <= errors_by_step[0] + 1e-6, errors_by_step


def test_two_cap_alchemical_bundle_trusted_reload_in_fresh_process(tmp_path):
    from atm_mlmm.atm import AtmEvaluator, build_atm, save_bundle
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.rbfe import make_protocol
    from atm_mlmm.schedule import linear_schedule
    from atm_mlmm.schema import MobileGroup, RestraintSpec, RuntimeSpec, to_json

    bundle, snapshot, _ = build_collection()
    groups = (
        MobileGroup("A", ("lA_c", "lA_h1", "lA_h2"), ("ligand",), "ligand-A"),
        MobileGroup("B", ("lB_c", "lB_h1", "lB_h2", "lB_h3"), ("ligand",), "ligand-B"),
    )
    transfer = resolve_protocol(bundle, make_protocol(groups, (.04, -.025, .015)))
    schedule = linear_schedule((("map0", 0.), ("map1", 1.)))
    restraint = RestraintSpec(
        "zero-spring-control", ("lA_c",), 0., DATA["positions_nm"][IDS.index("lA_c")]
    )
    alchemical = build_atm(bundle, transfer, schedule, restraint)
    artifact = tmp_path / "two-cap-alchemical.json"
    digest = save_bundle(artifact, alchemical)
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(to_json(snapshot) + "\n")
    runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "Verlet")
    expected = {}
    with AtmEvaluator(alchemical, runtime) as evaluator:
        for state_id in ("map0", "map1"):
            result = evaluator.evaluate(snapshot, state_id)
            expected[state_id] = {
                "energy": result.total.energy_kj_mol,
                "forces": result.total.forces_kj_mol_nm,
                "raw": result.raw.__dict__,
                "cap_ids": [link.cap_id for link in bundle.links],
                "model_input_ids": list(bundle.model_input_ids),
            }
    child = r'''
import json, pathlib, sys
from atm_mlmm.atm import AtmEvaluator, load_bundle
from atm_mlmm.schema import RuntimeSpec, from_json
bundle = load_bundle(sys.argv[1], sys.argv[2], trusted=True)
snapshot = from_json(pathlib.Path(sys.argv[3]).read_text())
runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "Verlet")
rows = {"cap_ids": [x.cap_id for x in bundle.physical.links],
        "model_input_ids": list(bundle.physical.model_input_ids),
        "boundary_builder_version": bundle.physical.manifest["boundary_builder_version"],
        "states": {}}
with AtmEvaluator(bundle, runtime) as evaluator:
    for state_id in ("map0", "map1"):
        result = evaluator.evaluate(snapshot, state_id)
        rows["states"][state_id] = {"energy": result.total.energy_kj_mol,
            "forces": result.total.forces_kj_mol_nm,
            "raw": result.raw.__dict__}
print(json.dumps(rows))
'''
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src"),
           "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"}
    child_result = subprocess.run(
        [sys.executable, "-c", child, str(artifact), digest, str(snapshot_path)],
        cwd=tmp_path, env=env, text=True, capture_output=True, timeout=90,
    )
    assert child_result.returncode == 0, child_result.stdout + child_result.stderr
    actual = json.loads(child_result.stdout.splitlines()[-1])
    assert actual["boundary_builder_version"] == 2
    for key in ("cap_ids", "model_input_ids"):
        assert actual[key] == expected["map0"][key]
    for state_id in ("map0", "map1"):
        assert abs(actual["states"][state_id]["energy"] - expected[state_id]["energy"]) <= 1e-10
        np.testing.assert_allclose(actual["states"][state_id]["forces"],
                                   expected[state_id]["forces"], rtol=0, atol=1e-9)
        assert actual["states"][state_id]["raw"] == expected[state_id]["raw"]


def test_two_cap_bounded_restart_through_common_runner_in_fresh_process(tmp_path):
    import hashlib
    from atm_mlmm.schema import to_json
    from atm_mlmm.workflow import run_configuration

    original, partition, snapshot = input_case()
    # This restart input keeps the fixture's bonded geometry and identities,
    # while placing the second complete ligand in a separated host-free region
    # required by the common runner's bounded bulk-geometry admission.
    separated = np.asarray(snapshot.positions_nm, dtype=float).copy()
    for atom_id in ("lB_c", "lB_h1", "lB_h2", "lB_h3"):
        separated[IDS.index(atom_id), 1] += 1.0
    snapshot = replace(snapshot, positions_nm=tuple(tuple(row) for row in separated))
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    files = {}
    for name, record in (("system-input.json", original), ("partition.json", partition),
                         ("snapshot.json", snapshot)):
        payload = to_json(record).encode()
        (inputs / name).write_bytes(payload)
        files[name] = hashlib.sha256(payload).hexdigest()
    manifest_path = inputs / "manifest.json"
    manifest_payload = json.dumps({"files": files}, sort_keys=True).encode()
    manifest_path.write_bytes(manifest_payload)
    config = inputs / "config.json"
    config.write_text(json.dumps({
        "version": 1,
        "input_manifest": "manifest.json",
        "input_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "settings": {
            "temperature_K": 300., "timestep_ps": .0005, "platform": "Reference",
            "seed": 41, "temperatures_K": [10., 100., 300.],
            "steps_per_phase": 1, "minimization_iterations": 3,
            "frames_per_state": 1, "steps_per_frame": 1,
            "displacement_nm": [0., 0., 1.2],
            "outside_spring_kj_mol_nm2": 1., "protocol_kind": "rbfe",
        },
    }))
    output = tmp_path / "bounded-run"
    prefix = run_configuration(config, output, trusted=True, stop_after_samples=1)
    assert prefix["status"] == "interrupted" and prefix["samples"] == 1
    sealed = json.loads((output / "worker/bundle.json").read_text())
    assert len(sealed["data"]["physical"]["data"]["links"]) == 2
    child = r'''
import json, sys
from atm_mlmm.workflow import resume_run
print(json.dumps(resume_run(sys.argv[1], trusted=True)))
'''
    env = {**os.environ,
           "PYTHONPATH": str(output / "worker/runtime/source"),
           "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
           "XDG_CACHE_HOME": str(tmp_path / "empty-xdg"),
           "TORCH_HOME": str(tmp_path / "empty-torch"),
           "MACE_CACHE_DIR": str(tmp_path / "empty-mace")}
    child_result = subprocess.run(
        [sys.executable, "-c", child, str(output)], cwd=tmp_path,
        env=env, text=True, capture_output=True, timeout=180,
    )
    assert child_result.returncode == 0, child_result.stdout + child_result.stderr
    final = json.loads(child_result.stdout.splitlines()[-1])
    assert final["status"] == "complete" and final["samples"] == 3
    assert final["profile"]["openmm_platform"] == "Reference"
    assert final["profile"]["model_device"] == "CPU"


def test_two_cap_force_and_torque_balance_under_rigid_motion():
    from atm_mlmm.models.analytic_caps import CapCollectionProbe, CapParameters

    probe = CapCollectionProbe((
        CapParameters("p1_ml", "p1_mm", 0., (.0, .0, .0), "p1_env", 2.5),
        CapParameters("p2_ml", "p2_mm", 0., (.0, .0, .0), "p2_env", 3.5),
    ))
    bundle, snapshot, _ = build_collection(probe)
    reference_energy, reference_forces, _ = model_result(bundle, snapshot)
    coordinates = np.asarray(snapshot.positions_nm)
    np.testing.assert_allclose(reference_forces.sum(axis=0), np.zeros(3), rtol=0, atol=1e-8)
    np.testing.assert_allclose(np.cross(coordinates, reference_forces).sum(axis=0),
                               np.zeros(3), rtol=0, atol=1e-8)
    rotation = np.asarray(((0., -1., 0.), (1., 0., 0.), (0., 0., 1.)))
    moved = replace(snapshot, positions_nm=coordinates @ rotation.T + (.31, -.17, .23))
    energy, forces, _ = model_result(bundle, moved)
    assert abs(energy-reference_energy) <= 1e-8
    np.testing.assert_allclose(forces, reference_forces @ rotation.T, rtol=0, atol=1e-8)
    np.testing.assert_allclose(forces.sum(axis=0), np.zeros(3), rtol=0, atol=1e-8)
    np.testing.assert_allclose(np.cross(moved.positions_nm, forces).sum(axis=0),
                               np.zeros(3), rtol=0, atol=1e-8)


@pytest.mark.parametrize("fault", ("omit-second-cap", "omit-second-environment"))
def test_two_cap_controls_detect_one_missing_projection_or_environment_derivative(fault):
    from atm_mlmm.atm import physical_system
    from atm_mlmm.models.analytic_caps import collection_callback

    bundle, snapshot, probe = build_collection()
    caps, environments, ligands = oracle_terms(probe)
    expected_energy, expected_forces, _ = analytic_force_answer(
        snapshot.positions_nm, cap_terms=caps,
        direct_environment_terms=environments, ligand_terms=ligands,
    )
    system = physical_system(bundle)
    force_index = next(i for i, force in enumerate(system.getForces())
                       if force.getName() == "analytic:cap-collection-probe-v2")
    force = system.getForce(force_index)
    selected = list(force.getParticles())
    callback, selected = collection_callback(probe, selected, system, bundle.real_to_final)
    if fault == "omit-second-cap":
        broken_callback = FaultyCollectionCallback(callback, omit_cap=callback.cap_indices[1])
    else:
        broken_callback = FaultyCollectionCallback(
            callback, omit_environment=callback.cap_environment_indices[1]
        )
    broken = mm.PythonForce(broken_callback)
    broken.setParticles(selected)
    broken.setForceGroup(force.getForceGroup())
    broken.setName("analytic:deliberately-broken-cap-collection")
    system.removeForce(force_index)
    system.addForce(broken)
    energy, forces, _ = model_result(bundle, snapshot, system=system)
    assert abs(energy-expected_energy) <= 1e-8
    difference = forces-expected_forces
    affected_id = "p2_mm" if fault == "omit-second-cap" else "p2_env"
    assert np.linalg.norm(difference[IDS.index(affected_id)]) > 1e-3


def test_two_cap_ledger_and_nonidentity_particle_mapping():
    from atm_mlmm.atm import physical_system
    from atm_mlmm.embeddings.mechanical import openmm_topology, seal_boundary_result
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import IdentityError, UnsupportedCapability
    from tests.link_permutation import permute_info

    bundle, snapshot, _ = build_collection()
    expected_cuts = {frozenset(edge) for edge in DATA["permitted_cuts"]}
    ml_ids = set(DATA["ml_ids"])
    expected_removed = {frozenset((row["atom1"], row["atom2"])) for row in DATA["bonds"]
                        if row["atom1"] in ml_ids and row["atom2"] in ml_ids}
    expected_retained = {frozenset((row["atom1"], row["atom2"])) for row in DATA["bonds"]
                         if row["atom1"] not in ml_ids or row["atom2"] not in ml_ids}
    removed_bonds = {frozenset(row["atom_ids"]) for row in bundle.manifest["boundary_terms"]
                     if row["kind"] == "bond" and row["disposition"] == "removed"}
    retained_bonds = {frozenset(row["atom_ids"]) for row in bundle.manifest["boundary_terms"]
                      if row["kind"] == "bond" and row["disposition"] == "retained"}
    assert removed_bonds == expected_removed
    assert retained_bonds == expected_retained
    assert expected_cuts <= retained_bonds
    inert_caps = [row for row in bundle.manifest["boundary_terms"]
                  if row["kind"] == "nonbonded_particle" and row["disposition"] == "added_inert_cap"]
    assert len(inert_caps) == 2
    assert {entry["projection_owner"] for entry in bundle.manifest["cap_force_ownership"]} == {
        "native LocalCoordinatesSite exactly once"
    }
    system = physical_system(bundle)
    nonbonded = next(force for force in system.getForces() if isinstance(force, mm.NonbondedForce))
    for link in bundle.links:
        assert bundle.masses_da[link.final_particle_index] == 0.
        q, sigma, epsilon = nonbonded.getParticleParameters(link.final_particle_index)
        assert q.value_in_unit(unit.elementary_charge) == 0.
        assert epsilon.value_in_unit(unit.kilojoule_per_mole) == 0.

    original, spec, _ = input_case()
    info = dict(system=system, topology=openmm_topology(bundle.topology),
                oldToNew=list(bundle.old_to_new))
    topology = info["topology"]
    for _ in bundle.links:
        cap_residue = topology.addResidue("CAP", topology.addChain("CAP"))
        topology.addAtom("Hcap", mm.app.element.hydrogen, cap_residue)
    permutation = (8, 1, 13, 0, 11, 4, 16, 2, 15, 5, 10, 3, 14, 6, 12, 9, 7)
    remapped_info = permute_info(info, permutation)
    remapped = seal_boundary_result(
        original, resolve_partition(original.topology, spec), remapped_info,
        manifest=dict(bundle.manifest),
    )
    assert remapped.old_to_new == tuple(permutation[i] for i in range(len(IDS)))
    assert set(remapped.model_input_ids) == set(bundle.model_input_ids)
    assert {link.cap_id: link.final_particle_index for link in remapped.links} == {
        link.cap_id: permutation[link.final_particle_index] for link in bundle.links
    }
    energy_a, forces_a, _ = model_result(bundle, snapshot)
    energy_b, forces_b, _ = model_result(remapped, snapshot)
    assert abs(energy_a-energy_b) <= 1e-8
    np.testing.assert_allclose(forces_a, forces_b, rtol=0, atol=1e-8)

    link0, link1 = bundle.links
    with pytest.raises(IdentityError):
        replace(bundle, links=(link0, replace(link1, cap_id=link0.cap_id)))
    shared_parent_link = replace(link1, mm_parent_id=link0.mm_parent_id)
    shared_parent_manifest = {
        **bundle.manifest,
        "boundary_edges": ((link0.ml_parent_id, link0.mm_parent_id),
                           (shared_parent_link.ml_parent_id, shared_parent_link.mm_parent_id)),
    }
    with pytest.raises(IdentityError, match="duplicate cap identity, parent"):
        replace(bundle, links=(link0, shared_parent_link), manifest=shared_parent_manifest)
    with pytest.raises(UnsupportedCapability, match="unsupported boundary builder version"):
        replace(bundle, manifest={**bundle.manifest, "boundary_builder_version": 2.0})
    with pytest.raises(UnsupportedCapability, match="unsupported boundary builder version"):
        replace(bundle, manifest={**bundle.manifest, "boundary_builder_version": 3})
    owners = bundle.manifest["cap_force_ownership"]
    with pytest.raises(IdentityError, match="every cap exactly once"):
        replace(bundle, manifest={**bundle.manifest,
                                  "cap_force_ownership": owners + (owners[0],)})
    distances = bundle.manifest["cap_distances_nm"]
    bad_distances = ((distances[0][0], distances[0][1] + .01), distances[1])
    with pytest.raises(IdentityError, match="cap distances disagree"):
        replace(bundle, manifest={**bundle.manifest, "cap_distances_nm": bad_distances})
    for field in ("boundary_edges", "cap_distances_nm", "cap_force_ownership"):
        incomplete = dict(bundle.manifest)
        incomplete.pop(field)
        with pytest.raises(IdentityError, match="requires complete edge"):
            replace(bundle, manifest=incomplete)


def test_two_cap_periodic_pme_ledger_preserves_exclusions_and_inert_caps():
    from atm_mlmm.atm import physical_system
    from atm_mlmm.ledger import inventory_system
    from atm_mlmm.models.analytic_caps import CapCollectionProbe, CapParameters
    from atm_mlmm.schema import EmbeddingSpec
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.partition import resolve_partition

    original, spec, snapshot = input_case()
    source = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    nonbonded = next(force for force in source.getForces() if isinstance(force, mm.NonbondedForce))
    nonbonded.setNonbondedMethod(mm.NonbondedForce.PME)
    nonbonded.setCutoffDistance(.9 * unit.nanometer)
    nonbonded.setEwaldErrorTolerance(1e-7)
    box = ((4., 0., 0.), (0., 4., 0.), (0., 0., 4.))
    source.setDefaultPeriodicBoxVectors(*(mm.Vec3(*vector) * unit.nanometer for vector in box))
    xml = mm.XmlSerializer.serialize(source)
    parameter_identity = inventory_system(source).content_identity
    original = replace(
        original,
        prepared_mm_artifact=xml,
        prepared_mm_sha256=hashlib.sha256(xml.encode()).hexdigest(),
        box_nm=box,
        force_field_provenance={**original.force_field_provenance,
                                "parameter_identity": parameter_identity},
        prepared_mm_inventory_identity=parameter_identity,
    )
    snapshot = replace(snapshot, box_nm=box)
    probe = CapCollectionProbe((
        CapParameters("p1_ml", "p1_mm", 0., (0., 0., 0.)),
        CapParameters("p2_ml", "p2_mm", 0., (0., 0., 0.)),
    ))
    resolved = resolve_partition(original.topology, spec)
    bundle = build_physical(
        original, resolved, collection_model_spec(probe),
        EmbeddingSpec("mechanical", "1", "protein_c_c", "orthorhombic-pme-v1"),
        probe=probe, cap_distance_nm=DATA["cap_distance_nm"],
    )
    assert bundle.manifest["periodicity"] == "orthorhombic-pme-v1"
    assert bundle.manifest["model_long_range"] is False
    retained = mm.XmlSerializer.deserialize(bundle.manifest["retained_mm_xml"])
    retained_nb = next(force for force in retained.getForces() if isinstance(force, mm.NonbondedForce))
    assert retained_nb.getNonbondedMethod() == mm.NonbondedForce.PME
    exclusions = [row for row in bundle.manifest["boundary_terms"]
                  if row["kind"] == "exception" and row["disposition"] == "added_exclusion"]
    assert exclusions
    assert all({row["atom_ids"][0], row["atom_ids"][1]} <= set(bundle.ml_atom_ids)
               for row in exclusions)
    actual = physical_system(bundle)
    cap_nonbonded = next(force for force in actual.getForces() if isinstance(force, mm.NonbondedForce))
    for link in bundle.links:
        q, sigma, epsilon = cap_nonbonded.getParticleParameters(link.final_particle_index)
        assert q.value_in_unit(unit.elementary_charge) == 0.
        assert epsilon.value_in_unit(unit.kilojoule_per_mole) == 0.
