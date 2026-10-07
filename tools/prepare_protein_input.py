#!/usr/bin/env python
"""Validate prepared-target choices without selecting or repairing a target."""
import argparse
from collections.abc import Mapping
import hashlib
import json
from pathlib import Path


_TARGET_FIELDS = (
    'target_id', 'source_structure.path', 'source_structure.sha256',
    'protein.selection', 'protein.protonation', 'protein.stereochemistry',
    'protein.alternate_conformers', 'protein.missing_atoms', 'protein.missing_residues',
    'ligand.chemistry', 'ligand.atom_ids', 'waters.decision', 'ions.decision',
    'force_field.identity', 'system.masses_da', 'system.constraints',
    'system.periodic_box_nm', 'system.nonbonded_conventions',
    'model.neutral_components', 'model.permitted_c_c_cuts',
    'artifacts.configuration', 'artifacts.system_input', 'artifacts.partition',
    'artifacts.snapshot',
)
_EXPLICIT_NONE_FIELDS = frozenset({'system.periodic_box_nm'})
_EXPLICIT_EMPTY_LIST_FIELDS = frozenset({'system.constraints', 'model.permitted_c_c_cuts'})


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _missing(document, paths):
    missing = []
    for dotted in paths:
        value = document
        present = True
        for part in dotted.split('.'):
            if not isinstance(value, dict) or part not in value:
                present = False
                break
            value = value[part]
        if (not present or value == '' or value == {} or
                (value is None and dotted not in _EXPLICIT_NONE_FIELDS) or
                (isinstance(value, list) and not value and
                 dotted not in _EXPLICIT_EMPTY_LIST_FIELDS)):
            missing.append(dotted)
    return missing


def _load_control(base, manifest):
    from atm_mlmm.embeddings.mechanical import original_system
    from atm_mlmm.workflow import load_configuration
    configuration = (base / manifest['artifacts']['configuration']).resolve()
    if base not in configuration.parents:
        raise ValueError('configuration path escapes the admission manifest directory')
    config = load_configuration(configuration)
    original_system(config.original, require_inventory_identity=True)
    input_manifest = (configuration.parent / config.document['input_manifest']).resolve()
    if configuration.parent not in input_manifest.parents:
        raise ValueError('configuration input manifest escapes its directory')
    return config, input_manifest


def _json_equal(left, right):
    def plain(value):
        if isinstance(value, Mapping):
            return {key: plain(child) for key, child in value.items()}
        if isinstance(value, (list, tuple)):
            return [plain(child) for child in value]
        return value

    return json.dumps(plain(left), sort_keys=True, separators=(',', ':'), allow_nan=False) == \
        json.dumps(plain(right), sort_keys=True, separators=(',', ':'), allow_nan=False)


def _validate_complete_target(base, document, config, input_manifest):
    """Cross-check declarations against the hash-bound prepared artifacts."""
    file_manifest = json.loads(input_manifest.read_text())
    artifacts = document['artifacts']
    names = {'system_input': 'system-input.json', 'partition': 'partition.json',
             'snapshot': 'snapshot.json'}
    for key, filename in names.items():
        declared = (base / artifacts[key]).resolve()
        actual = (input_manifest.parent / filename).resolve()
        if base not in declared.parents or declared != actual:
            raise ValueError(f'artifacts.{key} does not name the configuration input artifact')
        if filename not in file_manifest.get('files', {}):
            raise ValueError(f'configuration manifest does not bind {filename}')

    original = config.original
    molecules = original.topology.molecules
    ligands = [m for m in molecules if m.role == 'ligand']
    if len(ligands) != 1:
        raise ValueError('complete protein target requires exactly one whole ligand')
    ligand = ligands[0]
    ligand_ids = document['ligand']['atom_ids']
    if ligand_ids != list(ligand.atom_ids):
        raise ValueError('declared ligand atom_ids differ from the complete prepared ligand')
    chemistry = document['ligand']['chemistry']
    if not isinstance(chemistry, dict) or not all(
            isinstance(chemistry.get(key), str) and chemistry[key]
            for key in ('canonical_smiles', 'source')):
        raise ValueError('ligand.chemistry must identify canonical chemistry and its source')
    if (chemistry.get('formal_charge'), chemistry.get('multiplicity')) != (
            ligand.formal_charge, ligand.multiplicity):
        raise ValueError('declared ligand charge/multiplicity differs from prepared topology')

    membership = {atom_id: molecule for molecule in molecules for atom_id in molecule.atom_ids}
    protein_ids = sorted(a.atom_id for a in original.topology.atoms
                         if membership[a.atom_id].role == 'protein')
    selection = document['protein']['selection']
    if not isinstance(selection, dict) or selection.get('atom_ids') != protein_ids:
        raise ValueError('protein.selection atom_ids differ from the complete prepared protein topology')
    for section in ('waters', 'ions'):
        decision = document[section]['decision']
        if not isinstance(decision, dict) or not isinstance(decision.get('molecule_ids'), list):
            raise ValueError(f'{section}.decision must explicitly enumerate molecule_ids')
        roles = ('water', 'solvent') if section == 'waters' else ('ion',)
        observed = sorted(m.molecule_id for m in molecules if m.role in roles)
        if decision['molecule_ids'] != observed:
            raise ValueError(f'{section}.decision molecule_ids differ from prepared topology')

    force_field = document['force_field']['identity']
    if not _json_equal(force_field, original.force_field_provenance):
        raise ValueError('force_field.identity differs from SystemInput provenance')
    system = document['system']
    if not _json_equal(system['masses_da'], list(original.masses_da)):
        raise ValueError('system.masses_da differs from SystemInput')
    if not _json_equal(system['constraints'], [list(row) for row in original.constraints]):
        raise ValueError('system.constraints differs from SystemInput')
    if not _json_equal(system['periodic_box_nm'], original.box_nm):
        raise ValueError('system.periodic_box_nm differs from SystemInput')
    conventions = original.force_field_provenance.get('nonbonded_conventions')
    if conventions is None or not _json_equal(system['nonbonded_conventions'], conventions):
        raise ValueError('system.nonbonded_conventions is not bound by force-field provenance')

    expected_states = {
        (tuple(sorted(row.atom_ids)), row.formal_charge, row.multiplicity)
        for row in config.partition.component_states
    }
    declared_states = document['model']['neutral_components']
    if not isinstance(declared_states, list):
        raise ValueError('model.neutral_components must enumerate every selected component')
    observed_states = set()
    for row in declared_states:
        if not isinstance(row, dict) or not isinstance(row.get('atom_ids'), list):
            raise ValueError('each model component needs atom_ids, formal_charge, and multiplicity')
        observed_states.add((tuple(sorted(row['atom_ids'])), row.get('formal_charge'),
                             row.get('multiplicity')))
        if row.get('formal_charge') != 0 or row.get('multiplicity') != 1:
            raise ValueError('model components must be explicit neutral singlets')
    if observed_states != expected_states:
        raise ValueError('model.neutral_components differ from prepared component states')
    declared_cuts = {frozenset(edge) for edge in document['model']['permitted_c_c_cuts']}
    actual_cuts = {frozenset(edge) for edge in config.partition.permitted_cuts}
    if declared_cuts != actual_cuts:
        raise ValueError('model.permitted_c_c_cuts differ from prepared partition')
    from atm_mlmm.schema import PartitionSpec
    if not isinstance(config.partition, PartitionSpec):
        raise ValueError('partition artifact is not a typed PartitionSpec')
    return input_manifest


def validate_manifest(path):
    """Return a readable rejection or a narrow input-only validation record."""
    path = Path(path).resolve()
    document = json.loads(path.read_text())
    if document.get('schema') != 'prepared-protein-input-v1':
        raise ValueError('unsupported prepared-protein manifest schema')
    scope = document.get('scope')
    if scope == 'complete_prepared_target':
        missing = _missing(document, _TARGET_FIELDS)
        if missing:
            return {
                'status': 'blocked', 'scope': scope, 'missing_fields': missing,
                'binding_result': 'not_evaluated', 'complete_target_selected': False,
                'message': 'Choose and hash a complete target, ligand, protonation/repair/ion/parameter definition, then provide loadable artifacts. No structure has been repaired or selected.',
            }
    elif scope != 'structural_control':
        raise ValueError('scope must be complete_prepared_target or structural_control')

    source = document.get('source_control') if scope == 'structural_control' else document.get('source_structure')
    if not isinstance(source, dict) or not source.get('path') or not source.get('sha256'):
        key = 'source_control' if scope == 'structural_control' else 'source_structure'
        return {'status': 'blocked', 'scope': scope,
                'missing_fields': [f'{key}.path', f'{key}.sha256'],
                'binding_result': 'not_evaluated', 'complete_target_selected': False}
    source_path = (path.parent / source['path']).resolve()
    if path.parent not in source_path.parents or not source_path.is_file():
        raise ValueError('source structure/control path is missing or escapes its admission directory')
    if _sha(source_path) != source['sha256']:
        raise ValueError('source structure/control SHA-256 mismatch')

    config, input_manifest = _load_control(path.parent, document)
    if scope == 'structural_control':
        return {
            'status': 'validated_structural_control', 'scope': scope,
            'classification': document.get('classification', 'structural control only'),
            'cuts': [list(edge) for edge in config.partition.permitted_cuts],
            'complete_protein_target': False, 'binding_result': 'not_evaluated',
        }
    # Complete-target records are checked but never silently repaired or accepted as production.
    _validate_complete_target(path.parent, document, config, input_manifest)
    return {
        'status': 'validated_prepared_input_only', 'scope': scope,
        'complete_target_selected': True, 'production_acceptance': False,
        'binding_result': 'not_evaluated', 'cuts': [list(edge) for edge in config.partition.permitted_cuts],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    print(json.dumps(validate_manifest(args.manifest), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
