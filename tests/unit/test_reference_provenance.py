"""Synthetic importer integrity checks; no quantum calculation or real approval.

These records test file/decision binding only. They are never chemical evidence
and never enter the frozen chemical-reference fixture directory.
"""
import hashlib
import json

import pytest

from atm_mlmm.chemical_reference import load_references
from atm_mlmm.schema import IdentityError


@pytest.fixture
def synthetic_references(tmp_path):
    def write(path, data):
        path.write_text(json.dumps(data, indent=2) + '\n')

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    (tmp_path / 'structures').mkdir()
    (tmp_path / 'quantum' / 'records').mkdir(parents=True)
    notice = 'SYNTHETIC SOFTWARE TEST ONLY; no quantum data or actual approval'
    geometry = dict(name='synthetic-h2', atomic_numbers=[1, 1],
                    positions_angstrom=[[0., 0., 0.], [1., 0., 0.]], notice=notice)
    settings = dict(settings={'basis': 'def2-tzvppd'},
                    basis_file_sha256={'def2-tzvppd.gbs': 'a' * 64},
                    convergence_checks={'rows': []},
                    hartree_to_kJ_mol=2625.4996382852164,
                    bohr_to_nm=0.052917721067, notice=notice)
    structure = tmp_path / 'structures' / 'synthetic-h2.json'
    settings_path = tmp_path / 'reference-settings.json'
    write(structure, geometry)
    write(settings_path, settings)
    inputs = {'files': {'structures/synthetic-h2.json': sha(structure),
                        'reference-settings.json': sha(settings_path)}}
    input_path = tmp_path / 'input-manifest.json'
    write(input_path, inputs)
    record = dict(geometry, status='computed', network_denied=True,
                  source_input_sha256=sha(structure), formal_charge=0,
                  multiplicity=1, method='wb97m-d3bj/def2-tzvppd',
                  psi4_version='1.10.2', basis_file_sha256=settings['basis_file_sha256'],
                  settings=settings['settings'], energy_hartree=0.,
                  gradient_hartree_bohr=[[0., 0., 0.], [0., 0., 0.]])
    record_path = tmp_path / 'quantum' / 'records' / 'synthetic-h2.json'
    write(record_path, record)
    approval = dict(user_agreed=True, design_verdict='accepted_for_scope',
                    reviewer_model='gpt-6-astra', reasoning_effort='high',
                    fresh_context=True, reviewed_commit='1' * 40,
                    input_manifest_sha256=sha(input_path), notice=notice)
    manifest = dict(ready_for_comparison=True, approval=approval,
                    input_manifest_sha256=sha(input_path),
                    reference_settings_sha256=sha(settings_path),
                    files={'records/synthetic-h2.json': sha(record_path)})
    manifest_path = tmp_path / 'quantum' / 'manifest.json'
    write(manifest_path, manifest)
    return tmp_path, manifest, manifest_path


def test_matching_synthetic_plan_binding_is_readable(synthetic_references):
    root, _, _ = synthetic_references
    _, records = load_references(root)
    assert set(records) == {'synthetic-h2'}
    assert records['synthetic-h2']['notice'].startswith('SYNTHETIC SOFTWARE TEST')


@pytest.mark.parametrize('field,value', [
    ('input_manifest_sha256', 'f' * 64),
    ('input_manifest_sha256', None),
    ('reviewed_commit', None),
    ('reviewed_commit', 'a' * 39),
    ('reviewed_commit', 'x' * 40),
    ('reviewed_commit', 123),
])
def test_reference_approval_requires_exact_plan_and_commit(synthetic_references, field, value):
    root, manifest, path = synthetic_references
    if value is None:
        manifest['approval'].pop(field)
    else:
        manifest['approval'][field] = value
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    with pytest.raises(IdentityError, match='approval'):
        load_references(root)
