"""Protein input admission and solvent recipe rejection contracts."""
import hashlib
import json
from pathlib import Path
import shutil

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
