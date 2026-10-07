#!/usr/bin/env python
"""Check explicit physical-solvent definitions without inventing defaults."""
import argparse
import hashlib
import json
import math
from pathlib import Path


_REQUIRED = (
    'solute.parameter_identity', 'solvent.complete_molecules',
    'solvent.parameter_identity', 'ions.decision', 'box.geometry_nm',
    'box.density_definition', 'nonbonded.cutoff_nm', 'nonbonded.image_convention',
    'constraints.definition', 'ensemble.kind', 'preparation.stages',
    'preparation.active_force_owners', 'domain.both_map_checks',
    'outputs.unique_identity',
)
_FORBIDDEN = ('npt', 'pressure', 'virial', 'hmr', 'mts')


def _lookup(document, dotted):
    value = document
    for part in dotted.split('.'):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_recipe(document, base_dir):
    if document.get('schema') != 'physical-solvent-recipe-v1':
        raise ValueError('unsupported solvent recipe schema')
    if type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('solvent recipe schema_version must be the supported integer 1')
    base_dir = Path(base_dir).resolve()
    scope = document.get('scope')
    if scope == 'synthetic_plumbing_reference':
        fixture = document.get('fixture')
        if not fixture:
            return {'status': 'blocked', 'missing_fields': ['fixture'],
                    'physical_liquid': False, 'binding_result': 'not_evaluated'}
        fixture_root = (base_dir / fixture).resolve()
        repository_root = Path(__file__).resolve().parents[1]
        if repository_root not in fixture_root.parents:
            raise ValueError('reference fixture escapes the repository workspace')
        manifest_path = fixture_root / document.get('manifest', 'manifest.json')
        manifest = json.loads(manifest_path.read_text())
        verified = 0
        for name, digest in manifest.get('files', {}).items():
            target = (fixture_root / name).resolve()
            if fixture_root not in target.parents or _sha(target) != digest:
                raise ValueError(f'reference fixture digest mismatch: {name}')
            verified += 1
        if verified == 0:
            raise ValueError('reference fixture has no integrity-bound source files')
        return {'status': 'validated_plumbing_only', 'scope': scope,
                'physical_liquid': False, 'binding_result': 'not_evaluated',
                'source_files_verified': verified,
                'physical_scope': manifest.get('physical_scope', 'unqualified synthetic fixture')}
    if scope != 'physical_liquid_proposal':
        raise ValueError('scope must be physical_liquid_proposal or synthetic_plumbing_reference')
    missing = [key for key in _REQUIRED if _lookup(document, key) in (None, '', [])]
    ensemble = _lookup(document, 'ensemble.kind')
    if ensemble not in (None, 'NVT'):
        raise ValueError('only explicit NVT is admitted; NPT/pressure/virial is not implicit')
    forbidden_present = []
    def walk(value, prefix=''):
        if isinstance(value, dict):
            for key, child in value.items():
                name = f'{prefix}.{key}' if prefix else key
                if any(term in name.lower() for term in _FORBIDDEN):
                    forbidden_present.append(name)
                walk(child, name)
        elif isinstance(value, list):
            for child in value:
                walk(child, prefix)
        elif isinstance(value, str):
            if value.lower() in {'npt', 'hmr', 'mts', 'pressure', 'virial'}:
                forbidden_present.append(prefix)
    walk(document)
    if forbidden_present:
        raise ValueError(f'unsupported undeclared extension in solvent recipe: {sorted(set(forbidden_present))}')
    if not missing:
        _validate_complete_physical_definition(document, base_dir)
    return {'status': 'blocked' if missing else 'validated_input_definition_only',
            'scope': scope, 'missing_fields': missing,
            'physical_liquid': False, 'binding_result': 'not_evaluated',
            'implicit_npt': False, 'hmr': False, 'mts': False,
            'message': 'recipe validation does not perform a liquid calculation or qualify a production solvent state'}


def _validate_complete_physical_definition(document, base_dir):
    """Check declared shapes and named artifacts; this does not qualify parameters."""
    def need(condition, message):
        if not condition:
            raise ValueError(message)

    for label in ('solute', 'solvent'):
        identity = document[label]['parameter_identity']
        need(isinstance(identity, dict) and all(
            isinstance(identity.get(key), str) and identity[key]
            for key in ('name', 'version', 'path', 'artifact_sha256')),
            f'{label}.parameter_identity must name a versioned path and SHA-256 artifact')
        need(len(identity['artifact_sha256']) == 64 and
             all(ch in '0123456789abcdef' for ch in identity['artifact_sha256']),
             f'{label}.parameter_identity.artifact_sha256 must be lowercase SHA-256')
        artifact = (base_dir / identity['path']).resolve()
        repository_root = Path(__file__).resolve().parents[1]
        need(repository_root in artifact.parents and artifact.is_file(),
             f'{label}.parameter_identity.path must resolve to a repository artifact')
        need(_sha(artifact) == identity['artifact_sha256'],
             f'{label}.parameter_identity SHA-256 mismatch')

    molecules = document['solvent']['complete_molecules']
    need(isinstance(molecules, list) and molecules,
         'solvent.complete_molecules must enumerate every molecule')
    seen_atoms, seen_molecules = set(), set()
    for molecule in molecules:
        need(isinstance(molecule, dict) and all(
            isinstance(molecule.get(key), str) and molecule[key]
            for key in ('molecule_id', 'species')),
            'each solvent molecule needs stable molecule_id and species')
        atom_ids, coordinates = molecule.get('atom_ids'), molecule.get('coordinates_nm')
        need(isinstance(atom_ids, list) and atom_ids and
             all(isinstance(atom_id, str) and atom_id for atom_id in atom_ids),
             'each solvent molecule needs complete stable atom_ids')
        need(len(atom_ids) == len(set(atom_ids)) and not (seen_atoms & set(atom_ids)),
             'solvent atom IDs must be globally unique')
        need(isinstance(coordinates, list) and len(coordinates) == len(atom_ids) and
             all(isinstance(row, list) and len(row) == 3 and
                 all(type(v) in (int, float) and math.isfinite(v) for v in row)
                 for row in coordinates),
             'each solvent molecule needs finite coordinates for every complete atom')
        need(type(molecule.get('formal_charge')) is int,
             'each solvent molecule needs an explicit integer formal_charge')
        seen_atoms.update(atom_ids)
        seen_molecules.add(molecule['molecule_id'])
    need(len(seen_molecules) == len(molecules), 'solvent molecule IDs must be unique')

    ion_decision = document['ions']['decision']
    need(isinstance(ion_decision, dict) and ion_decision.get('kind') in ('none', 'explicit'),
         'ions.decision must explicitly say none or enumerate explicit ions')
    if ion_decision['kind'] == 'explicit':
        need(isinstance(ion_decision.get('molecules'), list) and ion_decision['molecules'],
             'explicit ion decision must enumerate ion molecules')

    box = document['box']['geometry_nm']
    need(isinstance(box, list) and len(box) == 3 and
         all(isinstance(row, list) and len(row) == 3 and
             all(type(v) in (int, float) and math.isfinite(v) for v in row)
             for row in box), 'box.geometry_nm must be a finite 3-by-3 matrix')
    a, b, c = box
    volume = (a[0]*(b[1]*c[2]-b[2]*c[1]) -
              a[1]*(b[0]*c[2]-b[2]*c[0]) +
              a[2]*(b[0]*c[1]-b[1]*c[0]))
    need(volume > 0., 'box.geometry_nm must have positive volume')
    density = document['box']['density_definition']
    need(isinstance(density, dict) and
         type(density.get('target_kg_m3')) in (int, float) and
         math.isfinite(density['target_kg_m3']) and density['target_kg_m3'] > 0 and
         isinstance(density.get('basis'), str) and density['basis'],
         'box.density_definition must state a positive target and explicit basis')
    cutoff = document['nonbonded']['cutoff_nm']
    need(type(cutoff) in (int, float) and math.isfinite(cutoff) and cutoff > 0,
         'nonbonded.cutoff_nm must be a positive finite number')
    need(isinstance(document['nonbonded']['image_convention'], str) and
         document['nonbonded']['image_convention'],
         'nonbonded.image_convention must be explicit')
    constraints = document['constraints']['definition']
    need((isinstance(constraints, str) and constraints.strip()) or
         (isinstance(constraints, dict) and constraints),
         'constraints.definition must explicitly define the constraint policy')

    preparation = document['preparation']
    stages, owners = preparation['stages'], preparation['active_force_owners']
    need(isinstance(stages, list) and stages and
         all(isinstance(row, dict) and row.get('stage') and
             row.get('ensemble') == 'NVT' and
             type(row.get('steps')) is int and row['steps'] > 0 and
             type(row.get('temperature_K')) in (int, float) and
             math.isfinite(row['temperature_K']) and row['temperature_K'] > 0
             for row in stages),
         'preparation.stages must declare positive NVT steps and temperature for every stage')
    need(isinstance(owners, list) and owners and
         all(isinstance(owner, str) and owner for owner in owners) and
         len(owners) == len(set(owners)),
         'preparation.active_force_owners must enumerate unique force owners')
    need(all(isinstance(row.get('active_force_owners'), list) and
             all(isinstance(owner, str) and owner for owner in row['active_force_owners']) and
             len(row['active_force_owners']) == len(set(row['active_force_owners'])) and
             set(row['active_force_owners']) == set(owners) for row in stages),
         'every preparation stage must retain every declared active force owner')
    checks = document['domain']['both_map_checks']
    need(isinstance(checks, dict) and checks.get('maps') == ['map0', 'map1'] and
         checks.get('complete_static_host') is True and
         checks.get('all_atom_contacts') is True,
         'domain.both_map_checks must cover both complete all-atom maps')
    output = document['outputs']['unique_identity']
    need(isinstance(output, dict) and all(
        isinstance(output.get(key), str) and output[key]
        for key in ('run_id_prefix', 'manifest_identity_rule')),
        'outputs.unique_identity must state a run-ID prefix and manifest identity rule')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe')
    args = parser.parse_args()
    path = Path(args.recipe).resolve()
    print(json.dumps(validate_recipe(json.loads(path.read_text()), path.parent),
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
