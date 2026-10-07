"""Small host–guest RBFE input and mechanism controls; not binding evidence."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'fixtures/host_guest_rbfe/v1'


def test_host_guest_rbfe_fixture_is_complete_unequal_and_loadable():
    import openmm as mm
    from openmm import unit
    from atm_mlmm.ledger import inventory_system
    from atm_mlmm.schema import from_json
    from atm_mlmm.workflow import load_configuration

    manifest = json.loads((FIXTURE / 'manifest.json').read_text())
    assert manifest['fixture_kind'] == 'development_host_guest_rbfe'
    assert manifest['status'] == 'preflight_only'
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == digest
    original, partition, snapshot = (
        from_json((FIXTURE / name).read_text())
        for name in ('system-input.json', 'partition.json', 'snapshot.json')
    )
    molecules = original.topology.molecules
    assert [(m.molecule_id, m.role, len(m.atom_ids), m.formal_charge, m.multiplicity)
            for m in molecules] == [
        ('host-18-crown-6', 'host', 42, 0, 1),
        ('ligand-methanol-A', 'ligand', 6, 0, 1),
        ('ligand-ethanol-B', 'ligand', 9, 0, 1),
    ]
    assert len(set(a.atom_id for a in original.topology.atoms)) == 57
    expected_states = {frozenset(m.atom_ids) for m in molecules}
    assert {frozenset(row.atom_ids) for row in partition.component_states} == expected_states
    assert all((row.formal_charge, row.multiplicity) == (0, 1)
               for row in partition.component_states)
    assert set(partition.ml_ids) == set(snapshot.real_atom_ids)
    assert not partition.permitted_cuts and snapshot.box_nm is None
    assert original.prepared_mm_inventory_identity
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    assert inventory_system(system).content_identity == original.prepared_mm_inventory_identity
    nonbonded = next(force for force in system.getForces()
                     if isinstance(force, mm.NonbondedForce))
    assert all(nonbonded.getParticleParameters(i)[0].value_in_unit(unit.elementary_charge) == 0.
               and nonbonded.getParticleParameters(i)[2].value_in_unit(unit.kilojoule_per_mole) == 0.
               for i in range(nonbonded.getNumParticles()))
    assert manifest['parameter_route']['status'] == 'blocked_missing_host_parameters'
    assert manifest['physical_scope'] == 'all-ML vacuum plumbing only'
    assert manifest['preparation']['parameter_route_source']['sha256'] == \
        'b956f580c233ca84cf1c88c855f13bb060e14f4178a479177ba535d153b81c08'
    config = load_configuration(FIXTURE / 'config.json')
    assert config.settings['protocol_kind'] == 'rbfe'
    assert config.document['input_manifest_sha256'] == hashlib.sha256(
        (FIXTURE / 'manifest.json').read_bytes()).hexdigest()
    run_definitions = json.loads((FIXTURE / 'run-definitions.json').read_text())
    assert {row['run_id'] for row in run_definitions['runs']} >= {
        'A_to_A_identity', 'forward_A_to_B', 'independent_reverse_B_to_A'}
    assert run_definitions['cross_protocol_closure_definition']['status'].startswith('blocked_')
    assert run_definitions['cross_protocol_closure_definition']['closure_expression'] is None
    assert run_definitions['S06_uncertainty_needs']['investigation_triggers_only'] == [
        'fewer than 100 effectively contributing samples',
        'incompatible full/last-half estimates']


def test_host_guest_opposite_maps_clear_the_entire_host_and_each_other():
    from atm_mlmm.schema import from_json
    from atm_mlmm.workflow import _domain

    original = from_json((FIXTURE / 'system-input.json').read_text())
    partition = from_json((FIXTURE / 'partition.json').read_text())
    snapshot = from_json((FIXTURE / 'snapshot.json').read_text())
    config = json.loads((FIXTURE / 'config.json').read_text())
    displacement = np.asarray(config['settings']['displacement_nm'])
    ids = {atom_id: i for i, atom_id in enumerate(snapshot.real_atom_ids)}
    groups = {m.molecule_id: [ids[a] for a in m.atom_ids]
              for m in original.topology.molecules}
    host0 = np.asarray(snapshot.positions_nm)[groups['host-18-crown-6']]
    x0 = np.asarray(snapshot.positions_nm)
    x1 = x0.copy()
    x1[groups['ligand-methanol-A']] += displacement
    x1[groups['ligand-ethanol-B']] -= displacement
    np.testing.assert_array_equal(x0[groups['host-18-crown-6']], host0)
    np.testing.assert_allclose(
        x1[groups['ligand-methanol-A']] - x0[groups['ligand-methanol-A']],
        np.broadcast_to(displacement, (len(groups['ligand-methanol-A']), 3)))
    np.testing.assert_allclose(
        x1[groups['ligand-ethanol-B']] - x0[groups['ligand-ethanol-B']],
        np.broadcast_to(-displacement, (len(groups['ligand-ethanol-B']), 3)))
    diagnostics = _domain(
        original.topology, snapshot, tuple(displacement), 'rbfe', partition.permitted_cuts
    )
    assert [row['map'] for row in diagnostics[:2]] == ['map0', 'map1']
    assert all(row['minimum_intermolecular_Bondi_ratio'] >= .65 for row in diagnostics[:2])
    assert all(row['minimum_static_distance_nm'] >= .65 for row in diagnostics[2:])
    domain = json.loads((FIXTURE / 'geometry-admission.json').read_text())
    assert domain['maps'] == ['map0', 'map1']
    assert domain['geometry_only'] is True
    assert domain['periodic_images'] == 'not_applicable_nonperiodic_input'
    assert domain['guest_guest_contact_check'] == 'complete_all_atom_pairs_both_maps'


def test_host_guest_generator_reproduces_the_frozen_preflight_input(tmp_path):
    from tools.prepare_host_guest_rbfe import prepare

    output = tmp_path / 'generated'
    prepare(output)
    for name in ('system-input.json', 'partition.json', 'snapshot.json',
                 'manifest.json', 'config.json', 'geometry-admission.json',
                 'run-definitions.json', 'thermodynamic-ledger.json'):
        assert (output / name).read_bytes() == (FIXTURE / name).read_bytes()


@pytest.mark.model_assets
def test_host_guest_direct_native_and_fresh_worker_restart_are_mechanism_checks(tmp_path):
    import os
    import subprocess
    import sys
    from dataclasses import replace
    from atm_mlmm.atm import AtmEvaluator, PhysicalEvaluator, build_atm
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.protocols.rbfe import make_protocol
    from atm_mlmm.schema import EmbeddingSpec, MobileGroup, RestraintSpec, from_json
    from atm_mlmm.workflow import load_configuration

    config = load_configuration(FIXTURE / 'config.json')
    groups = tuple(MobileGroup(m.molecule_id, m.atom_ids, ('ligand',), m.molecule_id)
                   for m in config.original.topology.molecules if m.role == 'ligand')
    physical = build_physical(config.original, resolve_partition(
        config.original.topology, config.partition), model_spec(),
        EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'),
        cap_distance_nm=.109)
    transfer = resolve_protocol(physical, make_protocol(
        groups, tuple(config.settings['displacement_nm'])))
    anchor = next(a.atom_id for a in config.original.topology.atoms
                  if a.atom_id.startswith('h'))
    restraint = RestraintSpec('static-host-anchor', (anchor,), 10.,
                              config.snapshot.positions_nm[
                                  config.snapshot.real_atom_ids.index(anchor)])
    bundle = build_atm(physical, transfer, config.schedule, restraint)
    mapped = np.array(config.snapshot.positions_nm)
    for group in groups:
        for atom_id in group.atom_ids:
            real_index = config.snapshot.real_atom_ids.index(atom_id)
            mapped[real_index] += np.asarray(
                transfer.displacement1_nm[physical.real_to_final[atom_id]])
    first = config.snapshot
    second = replace(config.snapshot, positions_nm=tuple(tuple(row) for row in mapped))
    with PhysicalEvaluator(physical, config.runtime) as direct:
        direct0, direct1 = direct.evaluate(first), direct.evaluate(second)
    with AtmEvaluator(bundle, config.runtime) as native:
        results = [native.evaluate(first, state.state_id) for state in config.schedule.states]
    for result in results:
        assert result.raw.u0_raw_kJ_mol == pytest.approx(direct0.energy_kj_mol, abs=1e-6)
        assert result.raw.u1_raw_kJ_mol == pytest.approx(direct1.energy_kj_mol, abs=1e-6)
        assert result.total.real_atom_ids == first.real_atom_ids
        assert np.isfinite(result.total.forces_kj_mol_nm).all()
        lam = result.parameters['Lambda1']
        expected = ((1. - lam) * np.asarray(direct0.forces_kj_mol_nm)
                    + lam * np.asarray(direct1.forces_kj_mol_nm))
        np.testing.assert_allclose(result.total.forces_kj_mol_nm, expected,
                                   atol=5e-3, rtol=0.)

    tiny = json.loads((FIXTURE / 'config.json').read_text())
    tiny['input_manifest'] = str(FIXTURE / 'manifest.json')
    tiny['settings'].update(frames_per_state=1, steps_per_frame=1,
                            steps_per_phase=1, minimization_iterations=3)
    config_path = tmp_path / 'tiny-config.json'
    config_path.write_text(json.dumps(tiny))
    output = tmp_path / 'run'
    from atm_mlmm.workflow import run_configuration
    initial = run_configuration(config_path, output, trusted=True, stop_after_samples=1)
    assert initial['status'] == 'interrupted'
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'src') + os.pathsep + str(ROOT)
    child = subprocess.run([
        sys.executable, '-c',
        'import json,sys; from atm_mlmm.workflow import resume_run; '
        'print(json.dumps(resume_run(sys.argv[1], trusted=True)))', str(output),
    ], cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    assert json.loads(child.stdout.splitlines()[-1])['status'] == 'complete'
    assert (output / 'handover-parity.json').is_file()
    assert (output / 'worker' / 'manifest.json').is_file()
