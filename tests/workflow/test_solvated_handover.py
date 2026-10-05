"""Periodic solvent workflow contracts; no density or affinity claim."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'fixtures/solvated_fragment/v1'


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_frozen_water_control_preserves_solute_and_fixed_membership(kind):
    import hashlib
    import json
    import openmm as mm
    from openmm import unit
    from atm_mlmm.schema import from_json
    from atm_mlmm.partition import resolve_partition
    base = ROOT / 'fixtures/cloud_fragment_controls/v1' / kind
    fixture = FIXTURE / kind
    manifest = json.loads((fixture / 'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((fixture / name).read_bytes()).hexdigest() == digest
    original = from_json((base / 'system-input.json').read_text())
    solvated = from_json((fixture / 'system-input.json').read_text())
    partition = from_json((fixture / 'partition.json').read_text())
    assert partition == from_json((base / 'partition.json').read_text())
    n = len(original.topology.atoms)
    assert len(solvated.topology.atoms) == n + 24
    assert solvated.topology.atoms[:n] == original.topology.atoms
    assert solvated.positions_nm[:n] == original.positions_nm
    assert solvated.masses_da[:n] == original.masses_da
    assert solvated.topology.bonds[:len(original.topology.bonds)] == original.topology.bonds
    assert solvated.topology.molecules[:len(original.topology.molecules)] == original.topology.molecules
    resolved = resolve_partition(solvated.topology, partition)
    assert set(resolved.ml_ids) == set(partition.ml_ids)
    assert all(a not in resolved.ml_ids for m in solvated.topology.molecules if m.role == 'solvent' for a in m.atom_ids)
    before, after = (mm.XmlSerializer.deserialize(s.prepared_mm_artifact) for s in (original, solvated))
    old_nb, new_nb = (next(f for f in s.getForces() if isinstance(f, mm.NonbondedForce)) for s in (before, after))
    for i in range(n):
        assert old_nb.getParticleParameters(i) == new_nb.getParticleParameters(i)
    for i in range(old_nb.getNumExceptions()):
        assert old_nb.getExceptionParameters(i) == new_nb.getExceptionParameters(i)
    assert len(solvated.constraints) == len(original.constraints) + 24
    assert after.getNumConstraints() == before.getNumConstraints() + 24
    assert new_nb.getNonbondedMethod() == mm.NonbondedForce.PME
    assert not new_nb.getUseDispersionCorrection()
    for m in solvated.topology.molecules[len(original.topology.molecules):]:
        assert m.role == 'solvent' and m.formal_charge == 0 and len(m.atom_ids) == 3
        indices = [solvated.topology.atoms.index(next(a for a in solvated.topology.atoms if a.atom_id == atom)) for atom in m.atom_ids]
        assert sum(new_nb.getParticleParameters(i)[0].value_in_unit(unit.elementary_charge) for i in indices) == pytest.approx(0., abs=1e-15)


def configuration_path(tmp_path, original, partition, snapshot):
    import hashlib
    import json
    from pathlib import Path
    from atm_mlmm.schema import to_json
    from tests.workflow.test_cloud_host_guest import ROOT
    files = {}
    for name, record in (('system-input.json', original), ('partition.json', partition),
                         ('snapshot.json', snapshot)):
        payload = to_json(record).encode()
        (tmp_path / name).write_bytes(payload)
        files[name] = hashlib.sha256(payload).hexdigest()
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'files': files}))
    config = json.loads((ROOT / 'fixtures/cloud_fragment_controls/v1/abfe/config.json').read_text())
    config.update(input_manifest='manifest.json',
                  input_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(config))
    return path


def test_periodic_configuration_uses_existing_declared_convention(tmp_path):
    from atm_mlmm.workflow import load_configuration
    from tests.joint_oracle import joint_input
    original, partition, snapshot = joint_input(periodic=True)
    actual = load_configuration(configuration_path(tmp_path, original, partition, snapshot))
    assert actual.snapshot.box_nm == snapshot.box_nm


def test_periodic_guard_detects_image_clash():
    from atm_mlmm.workflow import _domain
    from atm_mlmm.schema import NumericalDomainError
    from tests.joint_oracle import joint_input, DISPLACEMENT
    original, _, snapshot = joint_input(periodic=True)
    x = np.array(snapshot.positions_nm)
    # A ligand approaches a static solute atom through its periodic image.
    x[26] = x[0] + (6.401, 0., 0.)
    with pytest.raises(NumericalDomainError, match='Bondi ratio'):
        _domain(original.topology, replace(snapshot, positions_nm=x), DISPLACEMENT, 'abfe')


def test_periodic_bulk_guard_checks_full_static_solute_images():
    from atm_mlmm.workflow import _domain
    from atm_mlmm.schema import NumericalDomainError
    from tests.joint_oracle import joint_input, DISPLACEMENT
    original, _, snapshot = joint_input(periodic=True)
    x = np.array(snapshot.positions_nm)
    # Move the complete static fragment to an image of the separated guest.
    x[:26] += x[26] + np.array(DISPLACEMENT) + (6.4, 0., .5) - x[0]
    with pytest.raises(NumericalDomainError):
        _domain(original.topology, replace(snapshot, positions_nm=x), DISPLACEMENT, 'abfe')


def test_rbfe_bulk_guard_clears_the_other_complete_ligand():
    from atm_mlmm.workflow import _domain
    from atm_mlmm.schema import NumericalDomainError
    from tests.joint_oracle import joint_input, DISPLACEMENT
    original, _, snapshot = joint_input(two_ligands=True, periodic=True)
    x = np.array(snapshot.positions_nm)
    x[:26] -= (0., 0., 2.)
    # Neither ligand clashes with the full protein, but the declared bulk
    # ligand reconnects to the other complete ML ligand at map0.
    x[32:] += x[26]+(0., 0., .55)-x[32]
    with pytest.raises(NumericalDomainError, match='other ligand'):
        _domain(original.topology, replace(snapshot, positions_nm=x), DISPLACEMENT, 'rbfe')


def test_live_periodic_box_survives_snapshot_extraction():
    from atm_mlmm.workflow import _snapshot
    from atm_mlmm.atm import PhysicalEvaluator
    from tests.periodic_oracle import periodic_case
    from tests.link_oracle import REFERENCE
    physical, snapshot = periodic_case()
    with PhysicalEvaluator(physical, REFERENCE) as evaluator:
        evaluator.evaluate(snapshot)
        worker = SimpleNamespace(bundle=SimpleNamespace(physical=physical), evaluator=evaluator)
        actual = _snapshot(worker)
        assert actual.box_nm == snapshot.box_nm
        from openmm import unit
        live = evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        np.testing.assert_array_equal(actual.positions_nm, live[list(physical.old_to_new)])


def test_periodic_anchor_is_image_invariant():
    import openmm as mm
    from openmm import unit
    from atm_mlmm.atm import outside_force
    from atm_mlmm.schema import RestraintSpec
    from tests.periodic_oracle import periodic_case
    physical, snapshot = periodic_case()
    center = tuple(np.array(snapshot.positions_nm[0]) + (.02, -.03, .01))
    restraint = RestraintSpec('periodic-anchor', (snapshot.real_atom_ids[0],), 10., center)
    system = mm.System()
    for mass in physical.masses_da:
        system.addParticle(mass)
    system.setDefaultPeriodicBoxVectors(*snapshot.box_nm)
    system.addForce(outside_force(physical, restraint))
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
    try:
        from atm_mlmm.geometry import final_positions
        x = np.array(final_positions(physical, snapshot))
        for image in (np.zeros(3), np.diag(snapshot.box_nm), -np.diag(snapshot.box_nm)):
            context.setPositions(x + image)
            actual = context.getState(getEnergy=True, getForces=True)
            assert actual.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole) == pytest.approx(.007, abs=1e-10)
            force = actual.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer)[physical.real_to_final[snapshot.real_atom_ids[0]]]
            np.testing.assert_allclose(force, (.2, -.3, .1), atol=1e-10, rtol=0)
    finally:
        del context, integrator


@pytest.fixture(scope='module', params=('abfe', 'rbfe'))
def water_run(request, tmp_path_factory):
    import json
    from atm_mlmm.workflow import run_configuration, resume_run
    from atm_mlmm.persistence import read_sample_chunks
    from atm_mlmm.schema import from_json
    kind = request.param
    fixture = FIXTURE / kind
    root = tmp_path_factory.mktemp('water-'+kind)
    config = json.loads((fixture / 'config.json').read_text())
    config['input_manifest'] = str(fixture / 'manifest.json')
    config['settings'].update(frames_per_state=1, steps_per_frame=1, steps_per_phase=1,
                              minimization_iterations=3)
    path = root / 'config.json'
    path.write_text(json.dumps(config))
    output = root / 'run'
    initial = run_configuration(path, output, trusted=True, stop_after_samples=1)
    assert initial['status'] == 'interrupted'
    prefix = {p.relative_to(output): p.read_bytes() for p in (output / 'samples/000000').iterdir()}
    summary = resume_run(output, trusted=True)
    assert summary['status'] == 'complete'
    for name, payload in prefix.items():
        assert (output / name).read_bytes() == payload
    rows = read_sample_chunks(output / 'samples')
    assert len(rows) == 3 and len({r['sample_id'] for r in rows}) == 3
    bundle = from_json((output / 'worker/bundle.json').read_text())
    return kind, fixture, output, summary, bundle, rows


@pytest.mark.model_assets
def test_bulk_site_and_real_cross_forces(water_run):
    import openmm as mm
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.schema import from_json
    from atm_mlmm.model_reference import NativeMACE
    from tests.joint_oracle import RUNTIME, mapped_snapshot, independent_answer
    from tests.periodic_oracle import plain_periodic
    _, fixture, _, _, bundle, _ = water_run
    physical = bundle.physical
    snapshot = from_json((fixture / 'snapshot.json').read_text())
    water_ids = {a for m in physical.topology.molecules if m.role == 'solvent' for a in m.atom_ids}
    ligand_ids = {a for m in physical.topology.molecules if m.role == 'ligand' for a in m.atom_ids}
    water_real = [i for i, a in enumerate(snapshot.real_atom_ids) if a in water_ids]
    retained = mm.XmlSerializer.deserialize(physical.manifest['retained_mm_xml'])
    masked = mm.XmlSerializer.deserialize(physical.manifest['retained_mm_xml'])
    nb = next(f for f in masked.getForces() if isinstance(f, mm.NonbondedForce))
    for atom in ligand_ids:
        i = physical.real_to_final[atom]
        _, sigma, _ = nb.getParticleParameters(i)
        nb.setParticleParameters(i, 0., sigma, 0.)
    # Exceptions involving removed charges must follow the same mask.
    mobile = {physical.real_to_final[a] for a in ligand_ids}
    for i in range(nb.getNumExceptions()):
        a, b, q, sigma, epsilon = nb.getExceptionParameters(i)
        if a in mobile or b in mobile:
            nb.setExceptionParameters(i, a, b, 0., sigma, 0.)
    native = NativeMACE()
    with PhysicalEvaluator(physical, RUNTIME) as direct:
        for mapping in (0, 1):
            frame = mapped_snapshot(physical, snapshot, mapping)
            actual = direct.evaluate(frame)
            expected_energy, expected_force, _ = independent_answer(physical, frame, native)
            assert actual.energy_kj_mol == pytest.approx(expected_energy, abs=1e-4)
            np.testing.assert_allclose(actual.forces_kj_mol_nm, expected_force, atol=5e-3, rtol=0)
            from atm_mlmm.geometry import final_positions
            positions = final_positions(physical, frame)
            _, coupled = plain_periodic(retained, positions, frame.box_nm)
            _, uncoupled = plain_periodic(masked, positions, frame.box_nm)
            indices = [physical.real_to_final[snapshot.real_atom_ids[i]] for i in water_real]
            assert np.max(np.abs(coupled[indices]-uncoupled[indices])) > 1e-3
            # Numerical derivative on real solvent coordinates, not a cap slot.
            for atom in water_real[:2]:
                estimates = []
                for step in (1e-3, 1e-4, 1e-5):
                    energies = []
                    for sign in (1., -1.):
                        x = np.array(frame.positions_nm)
                        x[atom, 1] += sign*step
                        energies.append(direct.evaluate(replace(frame, positions_nm=x)).energy_kj_mol)
                    estimates.append(-(energies[0]-energies[1])/(2*step))
                expected = actual.forces_kj_mol_nm[atom][1]
                assert abs(estimates[-1]-expected) <= 1e-3+1e-4*abs(expected)
                assert abs(estimates[-1]-expected) <= abs(estimates[0]-expected)+1e-4


@pytest.mark.model_assets
def test_same_hamiltonian_in_preparation(water_run):
    import json
    import openmm as mm
    from openmm import unit
    _, _, output, _, bundle, _ = water_run
    preparation = json.loads((output / 'preparation.json').read_text())
    assert preparation['physical_identity'] == bundle.physical.content_identity
    assert all(p['physical_identity'] == bundle.physical.content_identity and p['integration_groups'] == [0]
               and p['timestep_ps'] == .0005 for p in preparation['phases'])
    assert [p['temperature_K'] for p in preparation['phases']] == [10., 100., 300.]
    state = mm.XmlSerializer.deserialize((output / 'prepared-state.xml').read_text())
    positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    for a, b, distance in bundle.physical.constraints:
        actual = np.linalg.norm(positions[a]-positions[b])
        assert actual == pytest.approx(distance, abs=2e-6)


@pytest.mark.model_assets
def test_worker_load_matches_direct_state(water_run):
    import openmm as mm
    from openmm import unit
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.atm import AtmEvaluator
    from atm_mlmm.schema import from_json
    from tests.joint_oracle import RUNTIME
    _, _, output, summary, bundle, _ = water_run
    snapshot = from_json((output / 'prepared-snapshot.json').read_text())
    initial_id = bundle.schedule.states[0].state_id
    with AtmEvaluator(bundle, RUNTIME) as direct:
        expected = direct.evaluate(snapshot, initial_id)
    with load_worker_run(output / 'worker', summary['worker_manifest_sha256'], trusted=True) as worker:
        saved = worker.evaluator.context.getState(getPositions=True, getVelocities=True, getParameters=True)
        exported = mm.XmlSerializer.deserialize((output / 'worker/handover_0.xml').read_text())
        np.testing.assert_allclose(saved.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer), snapshot.box_nm, atol=1e-12, rtol=0)
        np.testing.assert_array_equal(saved.getPositions(asNumpy=True), exported.getPositions(asNumpy=True))
        np.testing.assert_array_equal(saved.getVelocities(asNumpy=True), exported.getVelocities(asNumpy=True))
        assert dict(saved.getParameters()) == dict(exported.getParameters())
        assert worker.evaluator.system.getNumConstraints() == len(bundle.physical.constraints)
        actual = worker.evaluate(snapshot, initial_id)
        assert actual.raw == expected.raw and actual.parameters == expected.parameters
        np.testing.assert_allclose(actual.total.forces_kj_mol_nm, expected.total.forces_kj_mol_nm, atol=1e-7, rtol=0)


@pytest.mark.model_assets
def test_saved_raw_records_reconstruct_states(water_run):
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.schema import from_json, Snapshot
    from atm_mlmm.schedule import reduced_potentials
    _, _, output, summary, bundle, rows = water_run
    records = from_json((output / 'records.json').read_text())
    matrix = reduced_potentials(records)
    assert matrix.shape == (3, 3)
    with load_worker_run(output / 'worker', summary['worker_manifest_sha256'], trusted=True) as worker:
        for i, row in enumerate(rows):
            assert row['box_nm'] == [list(v) for v in bundle.physical.manifest['box_nm']]
            frame = Snapshot(tuple(row['real_atom_ids']), row['positions_nm'], row['box_nm'])
            for j, state in enumerate(bundle.schedule.states):
                actual = worker.evaluate(frame, state.state_id)
                assert actual.total.energy_kj_mol == pytest.approx(matrix[j, i]*.00831446261815324*300., abs=1e-8)
            assert len(row['real_forces_kj_mol_nm']) == len(bundle.physical.topology.atoms)
            assert np.isfinite(row['real_forces_kj_mol_nm']).all()


@pytest.mark.model_assets
def test_both_mapped_geometries_remain_admitted(water_run):
    from atm_mlmm.workflow import _domain
    from atm_mlmm.schema import Snapshot, NumericalDomainError
    kind, _, _, _, bundle, rows = water_run
    edges = tuple((link.ml_parent_id, link.mm_parent_id) for link in bundle.physical.links)
    for row in rows:
        frame = Snapshot(tuple(row['real_atom_ids']), row['positions_nm'], row['box_nm'])
        diagnostics = _domain(bundle.physical.topology, frame, (2.4, 0., 0.), kind, edges)
        assert [d['map'] for d in diagnostics[:2]] == ['map0', 'map1']
        assert all(d['minimum_static_distance_nm'] >= .65 for d in diagnostics[2:])
        # A solvent image in either placement must reject the whole frame.
        for map_index in (0, 1):
            x = np.array(frame.positions_nm)
            x[-3] = x[26]+(6.4+2.4*map_index, 0., 0.)
            with pytest.raises(NumericalDomainError):
                _domain(bundle.physical.topology, replace(frame, positions_nm=x), (2.4, 0., 0.), kind, edges)
