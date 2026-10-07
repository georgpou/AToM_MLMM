"""Protein input admission and solvent recipe rejection contracts."""
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import shutil

import pytest

from atm_mlmm.schema import to_json

ROOT = Path(__file__).resolve().parents[2]


def test_unselected_complete_protein_target_is_rejected_with_missing_choices():
    from tools.prepare_protein_input import validate_manifest

    proposal = ROOT / 'fixtures/protein_abfe/target-proposal-v1.json'
    result = validate_manifest(proposal)
    assert result['status'] == 'blocked'
    assert result['scope'] == 'complete_prepared_target'
    missing = set(result['missing_fields'])
    assert {
        'target_id', 'source_structure.path', 'source_structure.sha256',
        'protein.selection', 'protein.protonation', 'protein.stereochemistry',
        'protein.alternate_conformers', 'protein.missing_atoms',
        'protein.missing_residues', 'ligand.chemistry', 'ligand.atom_ids',
        'waters.decision', 'ions.decision', 'force_field.identity',
        'system.masses_da', 'system.constraints', 'system.periodic_box_nm',
        'system.nonbonded_conventions', 'model.neutral_components',
        'model.permitted_c_c_cuts', 'artifacts.configuration',
        'artifacts.system_input', 'artifacts.partition', 'artifacts.snapshot',
    } <= missing
    assert result['binding_result'] == 'not_evaluated'


def test_two_cut_structural_control_imports_without_becoming_a_protein_target(tmp_path):
    from tools.prepare_protein_input import validate_manifest
    from tests.cap_collection_oracle import input_case, FIXTURE

    original, partition, snapshot = input_case()
    source = tmp_path / 'source'
    source.mkdir()
    shutil.copyfile(FIXTURE / 'input.json', source / 'input.json')
    shutil.copyfile(FIXTURE / 'original-mm.xml', source / 'original-mm.xml')
    records = {
        'system-input.json': original,
        'partition.json': partition,
        'snapshot.json': snapshot,
    }
    file_hashes = {}
    for name, record in records.items():
        payload = (to_json(record) + '\n').encode()
        (tmp_path / name).write_bytes(payload)
        file_hashes[name] = hashlib.sha256(payload).hexdigest()
    input_manifest = tmp_path / 'input-manifest.json'
    input_manifest.write_text(json.dumps({'files': file_hashes}, indent=2) + '\n')
    input_digest = hashlib.sha256(input_manifest.read_bytes()).hexdigest()
    config = json.loads((ROOT / 'fixtures/cloud_fragment_controls/v1/rbfe/config.json').read_text())
    config['input_manifest'] = 'input-manifest.json'
    config['input_manifest_sha256'] = input_digest
    config['settings']['protocol_kind'] = 'rbfe'
    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(config, indent=2) + '\n')
    source_digest = hashlib.sha256((source / 'input.json').read_bytes()).hexdigest()
    manifest = {
        'schema': 'prepared-protein-input-v1',
        'scope': 'structural_control',
        'classification': 'synthetic two-cut control; not a complete protein target',
        'source_control': {'path': 'source/input.json', 'sha256': source_digest},
        'artifacts': {'configuration': 'config.json'},
        'binding_result': 'not_evaluated',
    }
    path = tmp_path / 'target-manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    result = validate_manifest(path)
    assert result['status'] == 'validated_structural_control'
    assert result['cuts'] == [list(edge) for edge in partition.permitted_cuts]
    assert result['complete_protein_target'] is False
    assert result['binding_result'] == 'not_evaluated'


def test_solvent_recipe_checker_blocks_missing_physical_liquid_definitions():
    from tools.validate_solvent_recipe import validate_recipe

    recipe_path = ROOT / 'fixtures/solvent_recipe/v1/physical-solvent-proposal.json'
    recipe = json.loads(recipe_path.read_text())
    result = validate_recipe(recipe, recipe_path.parent)
    assert result['status'] == 'blocked'
    assert {
        'solute.parameter_identity', 'solvent.complete_molecules',
        'solvent.parameter_identity', 'ions.decision', 'box.geometry_nm',
        'box.density_definition', 'nonbonded.cutoff_nm',
        'nonbonded.image_convention', 'constraints.definition',
        'ensemble.kind', 'preparation.stages', 'preparation.active_force_owners',
        'domain.both_map_checks', 'outputs.unique_identity',
    } <= set(result['missing_fields'])
    assert result['binding_result'] == 'not_evaluated'
    assert result['implicit_npt'] is False
    assert result['hmr'] is False


def _shape_only_solvent_recipe(stage_owners):
    artifact = ROOT / 'fixtures/two_cut_control/original-mm.xml'
    identity = {'name': 'input-only-shape-control', 'version': '1', 'path': str(artifact),
                'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
    return {
        'schema': 'physical-solvent-recipe-v1', 'schema_version': 1,
        'scope': 'physical_liquid_proposal',
        'solute': {'parameter_identity': identity},
        'solvent': {'parameter_identity': identity,
                    'complete_molecules': [{'molecule_id': 'control-water', 'species': 'control',
                                            'atom_ids': ['control-atom'],
                                            'coordinates_nm': [[0., 0., 0.]], 'formal_charge': 0}]},
        'ions': {'decision': {'kind': 'none'}},
        'box': {'geometry_nm': [[3., 0., 0.], [0., 3., 0.], [0., 0., 3.]],
                'density_definition': {'target_kg_m3': 1000., 'basis': 'shape-only control'}},
        'nonbonded': {'cutoff_nm': 1., 'image_convention': 'orthorhombic'},
        'constraints': {'definition': 'none'}, 'ensemble': {'kind': 'NVT'},
        'preparation': {'active_force_owners': ['MM', 'ML', 'outside'],
                        'stages': [{'stage': 'shape-only', 'ensemble': 'NVT', 'steps': 1,
                                    'temperature_K': 300., 'active_force_owners': stage_owners}]},
        'domain': {'both_map_checks': {'maps': ['map0', 'map1'],
                                       'complete_static_host': True, 'all_atom_contacts': True}},
        'outputs': {'unique_identity': {'run_id_prefix': 'shape-only',
                                        'manifest_identity_rule': 'explicit'}},
    }


@pytest.mark.parametrize('stage_owners', ([], ['MM', 'outside']))
def test_physical_solvent_preparation_requires_every_declared_force_owner(stage_owners):
    from tools.validate_solvent_recipe import validate_recipe

    with pytest.raises(ValueError, match='every preparation stage'):
        validate_recipe(_shape_only_solvent_recipe(stage_owners), ROOT)


def test_physical_solvent_preparation_accepts_complete_owner_declaration_only():
    from tools.validate_solvent_recipe import validate_recipe

    result = validate_recipe(_shape_only_solvent_recipe(['MM', 'ML', 'outside']), ROOT)
    assert result['status'] == 'validated_input_definition_only'
    assert result['physical_liquid'] is False
    assert result['binding_result'] == 'not_evaluated'


def test_solvent_recipe_rejects_implicit_npt_and_unknown_schema_versions():
    import pytest
    from tools.validate_solvent_recipe import validate_recipe

    recipe_path = ROOT / 'fixtures/solvent_recipe/v1/physical-solvent-proposal.json'
    recipe = json.loads(recipe_path.read_text())
    recipe['ensemble']['kind'] = 'NPT'
    with pytest.raises(ValueError, match='only explicit NVT'):
        validate_recipe(recipe, recipe_path.parent)
    recipe['schema_version'] = 2
    recipe['ensemble']['kind'] = None
    with pytest.raises(ValueError, match='schema_version'):
        validate_recipe(recipe, recipe_path.parent)


def test_existing_sixty_four_water_control_stays_a_synthetic_plumbing_fixture():
    from tools.validate_solvent_recipe import validate_recipe

    recipe_path = ROOT / 'fixtures/solvent_recipe/v1/synthetic-64-water-reference.json'
    recipe = json.loads(recipe_path.read_text())
    result = validate_recipe(recipe, recipe_path.parent)
    assert result['status'] == 'validated_plumbing_only'
    assert result['physical_liquid'] is False
    assert result['binding_result'] == 'not_evaluated'
    assert result['source_files_verified'] > 0


def _complete_input_only_fixture(tmp_path):
    from atm_mlmm.schema import to_json
    from atm_mlmm.workflow import load_configuration
    from atm_mlmm.ledger import inventory_system
    import openmm as mm

    prepared = tmp_path / 'prepared-input-only'
    shutil.copytree(ROOT / 'fixtures/cloud_fragment_controls/v1/abfe', prepared)
    config_path = prepared / 'config.json'
    config = load_configuration(config_path)
    ligand = next(molecule for molecule in config.original.topology.molecules
                  if molecule.role == 'ligand')
    ligand_state = next(state for state in config.partition.component_states
                        if set(state.atom_ids) == set(ligand.atom_ids))
    partition = replace(config.partition, ml_ids=tuple(ligand.atom_ids), protein_ml_ids=(),
                        permitted_cuts=(), component_states=(ligand_state,))

    system = mm.XmlSerializer.deserialize(config.original.prepared_mm_artifact)
    nonbonded = [force for force in system.getForces() if isinstance(force, mm.NonbondedForce)]
    assert len(nonbonded) == 1
    method_names = {mm.NonbondedForce.NoCutoff: 'NoCutoff',
                    mm.NonbondedForce.CutoffNonPeriodic: 'CutoffNonPeriodic',
                    mm.NonbondedForce.CutoffPeriodic: 'CutoffPeriodic',
                    mm.NonbondedForce.Ewald: 'Ewald', mm.NonbondedForce.PME: 'PME',
                    mm.NonbondedForce.LJPME: 'LJPME'}
    conventions = {'method': method_names[nonbonded[0].getNonbondedMethod()]}
    provenance = {**config.original.force_field_provenance,
                  'nonbonded_conventions': conventions}
    original = replace(config.original, force_field_provenance=provenance,
                       prepared_mm_inventory_identity=inventory_system(system).content_identity)
    records = {'system-input.json': original, 'partition.json': partition,
               'snapshot.json': config.snapshot}
    for name, record in records.items():
        (prepared / name).write_text(to_json(record) + '\n')

    input_manifest_path = prepared / 'manifest.json'
    input_manifest = json.loads(input_manifest_path.read_text())
    input_manifest['files'] = {
        name: hashlib.sha256((prepared / name).read_bytes()).hexdigest()
        for name in records
    }
    input_manifest_path.write_text(json.dumps(input_manifest, indent=2, sort_keys=True) + '\n')
    config_document = json.loads(config_path.read_text())
    config_document['input_manifest_sha256'] = hashlib.sha256(
        input_manifest_path.read_bytes()).hexdigest()
    config_path.write_text(json.dumps(config_document, indent=2, sort_keys=True) + '\n')

    protein_ids = sorted(atom.atom_id for atom in original.topology.atoms
                         if next(molecule for molecule in original.topology.molecules
                                 if atom.atom_id in molecule.atom_ids).role == 'protein')
    manifest = {
        'schema': 'prepared-protein-input-v1', 'scope': 'complete_prepared_target',
        'target_id': 'fixture-only-input-admission',
        'source_structure': {'path': 'system-input.json',
                             'sha256': hashlib.sha256((prepared / 'system-input.json').read_bytes()).hexdigest()},
        'protein': {
            'selection': {'atom_ids': protein_ids},
            'protonation': {'source': 'prepared fixture as supplied'},
            'stereochemistry': {'source': 'prepared fixture as supplied'},
            'alternate_conformers': {'source': 'prepared fixture as supplied'},
            'missing_atoms': {'source': 'prepared fixture as supplied'},
            'missing_residues': {'source': 'prepared fixture as supplied'},
        },
        'ligand': {'chemistry': {'canonical_smiles': 'CO',
                                 'source': 'existing fixture identity: neutral methanol',
                                 'formal_charge': ligand.formal_charge,
                                 'multiplicity': ligand.multiplicity},
                   'atom_ids': list(ligand.atom_ids)},
        'waters': {'decision': {'molecule_ids': []}},
        'ions': {'decision': {'molecule_ids': []}},
        'force_field': {'identity': provenance},
        'system': {'masses_da': list(original.masses_da),
                   'constraints': [list(row) for row in original.constraints],
                   'periodic_box_nm': original.box_nm,
                   'nonbonded_conventions': conventions},
        'model': {'neutral_components': [
            {'atom_ids': list(ligand_state.atom_ids),
             'formal_charge': ligand_state.formal_charge,
             'multiplicity': ligand_state.multiplicity}],
            'permitted_c_c_cuts': []},
        'artifacts': {'configuration': 'config.json', 'system_input': 'system-input.json',
                      'partition': 'partition.json', 'snapshot': 'snapshot.json'},
    }
    manifest_path = prepared / 'target-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest_path


def test_complete_input_only_manifest_accepts_explicit_none_and_empty_values(tmp_path):
    from tools.prepare_protein_input import validate_manifest

    manifest = _complete_input_only_fixture(tmp_path)
    result = validate_manifest(manifest)
    assert result['status'] == 'validated_prepared_input_only'
    assert result['cuts'] == []
    assert result['production_acceptance'] is False
    assert result['binding_result'] == 'not_evaluated'
