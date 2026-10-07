"""Audit-only, non-simulation characterizations. No production files are changed."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[4]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(case, **result):
    print(json.dumps(dict(case=case, **result), sort_keys=True))


def identities():
    supplied = json.loads((ROOT / 'Worker_Log/Before_HPC/evidence/setup-v1/handoff-identity.json').read_text())
    modules = json.loads((ROOT / 'Worker_Log/Before_HPC/evidence/checkpoint-e-v1/identity.json').read_text())
    for name, rows in [('supplied_files', supplied['files']), ('final_source_modules', modules['source_modules'])]:
        mismatches = [row['path'] for row in rows if sha(ROOT / row['path']) != row['sha256']]
        emit(name, count=len(rows), mismatches=mismatches)
        assert not mismatches


def source_inventory():
    from atm_mlmm.runtime_validation import verify_source_inventory
    with tempfile.TemporaryDirectory(prefix='before-hpc-audit-source-') as temporary:
        bundle = Path(temporary)
        current = ROOT / 'src/atm_mlmm'
        target = bundle / 'runtime/source/atm_mlmm'
        files = {}
        for source in current.rglob('*.py'):
            dest = target / source.relative_to(current)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            files[dest.relative_to(bundle).as_posix()] = sha(dest)
        verify_source_inventory(bundle, files, current_source_root=current)
        extra = target / 'audit_undeclared.py'
        extra.write_text('# inert undeclared Python file; never imported\n')
        verify_source_inventory(bundle, files, current_source_root=current)
        emit('undeclared_bundled_python', actual_python_files=len(list(target.rglob('*.py'))),
             declared_python_files=len(files), observed='accepted')


def hpc_profile():
    from atm_mlmm.hpc import check_profile
    p = dict(schema_version=999, profile_id='audit-invalid-dry-run-only',
        platform=dict(name='Reference', device='CPU', driver='none'),
        software=dict(python='3.11', openmm='8.6', model='analytic'),
        artifacts={key: char * 64 for key, char in zip(
            ['source_sha256', 'wheel_sha256', 'asset_manifest_sha256', 'input_manifest_sha256'], 'abcd')},
        storage=dict(path='/nonexistent/audit-only', filesystem='unverified', lock_rename_fsync_test_required=False),
        allocation=dict(threads=-1, memory_gib=-8, walltime_seconds=0, workers=0, scheduler='none'),
        checkpoint=dict(compatible_with='unknown', portable_state_promises_identical_rng=True))
    r = check_profile(p, bundle_manifest={'format': 'atom-mlmm-release-bundle-v1'})
    emit('contradictory_hpc_profile_and_format_only_bundle', input=p, result=r)
    assert r['status'] == 'ready_for_local_trial_dry_run'


def solvent_owners():
    import importlib.util
    spec = importlib.util.spec_from_file_location('audit_solvent', ROOT / 'tools/validate_solvent_recipe.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifact = ROOT / 'fixtures/two_cut_control/original-mm.xml'
    identity = dict(name='audit-shape-only-artifact', version='1', path=str(artifact), artifact_sha256=sha(artifact))
    # Deliberately artificial recipe: only demonstrates this validator's admission.
    # It is not a chemical input or parameter claim and is never executed.
    recipe = dict(schema='physical-solvent-recipe-v1', schema_version=1, scope='physical_liquid_proposal',
        solute=dict(parameter_identity=identity),
        solvent=dict(parameter_identity=identity, complete_molecules=[dict(molecule_id='audit-water',
            species='audit-only', atom_ids=['audit-atom'], coordinates_nm=[[0., 0., 0.]], formal_charge=0)]),
        ions=dict(decision=dict(kind='none')), box=dict(geometry_nm=[[3., 0., 0.], [0., 3., 0.], [0., 0., 3.]],
            density_definition=dict(target_kg_m3=1000., basis='audit shape probe')),
        nonbonded=dict(cutoff_nm=1., image_convention='orthorhombic'),
        constraints=dict(definition='none'), ensemble=dict(kind='NVT'),
        preparation=dict(active_force_owners=['MM', 'ML', 'outside'], stages=[dict(stage='audit-only',
            ensemble='NVT', steps=1, temperature_K=300., active_force_owners=[])]),
        domain=dict(both_map_checks=dict(maps=['map0', 'map1'], complete_static_host=True, all_atom_contacts=True)),
        outputs=dict(unique_identity=dict(run_id_prefix='audit-only', manifest_identity_rule='explicit')))
    result = module.validate_recipe(recipe, ROOT)
    emit('solvent_empty_stage_owners', declared_owners=recipe['preparation']['active_force_owners'],
         stage_owners=[], result=result)
    assert result['status'] == 'validated_input_definition_only'


if __name__ == '__main__':
    identities()
    source_inventory()
    hpc_profile()
    solvent_owners()
