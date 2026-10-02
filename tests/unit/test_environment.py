"""G00-T1: missing APIs or changed software identities must fail explicitly."""
import copy
import functools
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
# The maintained installer supports a custom prefix. Keep all exact inventory
# and source checks, but inspect the installation running this interpreter.
SETUP = Path(sys.prefix).resolve().parent


def test_required_apis_and_versions():
    from atm_mlmm.environment import check_required_apis
    report = check_required_apis()
    assert report['openmm_version'] == '8.6.1'
    assert report['openmmml_version'] == '1.8'
    assert report['atom_package_version'] == '8.5.0b0'
    assert report['checks'] == {
        'native_atm': True, 'selected_particle_python_force': True,
        'mixed_system_info': True, 'serialization': True,
    }


def test_environment_manifest_complete():
    from atm_mlmm.environment import characterize_environment, validate_environment_manifest
    report = characterize_environment(ROOT, SETUP)
    validate_environment_manifest(report)
    assert report['profile'] == 'core-analytic-cpu'
    assert report['python_version'] == '3.11.16'
    assert report['platform']['system'] == 'Linux'
    assert report['platform']['machine'] == 'x86_64'
    assert all(check['exit_code'] == 0 for check in report['dependency_checks'])
    assert {check['name'] for check in report['dependency_checks']} == {
        'core_exact_versions', 'amber_exact_versions', 'core_pip_check',
        'amber_pip_check', 'openmm_installation',
    }
    assert len(report['conda_builds']['core']) > 100
    assert len(report['python_distributions']['core']) > 50
    atom = next(s for s in report['sources'] if s['directory'] == 'AToM-OpenMM')
    assert atom['tag'] == 'v8.5.0'
    assert atom['distribution_version'] == '8.5.0b0'
    assert atom['commit'] == '9e26c5a3811038be1c98e3be6af4c78cd0dd57a7'
    assert len(atom['archive_sha256']) == 64
    assert report['deferred_profiles'] == {'model_assets': 'not_run', 'gpu': 'not_run'}
    for section in ('sources', 'conda_builds', 'dependency_checks', 'python_version', 'locks'):
        malformed = copy.deepcopy(report)
        malformed.pop(section)
        with pytest.raises(ValueError, match=section):
            validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['dependency_checks'][0]['exit_code'] = 1
    with pytest.raises(ValueError, match='dependency'):
        validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['sources'][0]['commit'] = 'main'
    with pytest.raises(ValueError, match='commit'):
        validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['sources'][0]['archive_sha256'] = 'not-a-digest'
    with pytest.raises(ValueError, match='digest'):
        validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['sources'][0]['distribution_version'] = '99.0'
    with pytest.raises(ValueError, match='version'):
        validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['api_checks']['checks']['serialization'] = False
    with pytest.raises(ValueError, match='API'):
        validate_environment_manifest(malformed)
    malformed = copy.deepcopy(report)
    malformed['locks'].pop('pip-wheels.lock')
    with pytest.raises(ValueError, match='locks'):
        validate_environment_manifest(malformed)
    # The tested manifest itself is preserved by the worker, not synthesized by tests.
    assert json.loads(json.dumps(report)) == report


def test_missing_required_api_fails_clearly():
    from atm_mlmm.environment import require_api
    with pytest.raises(ValueError, match='PythonForce'):
        require_api(object(), 'PythonForce')


def test_mixed_system_info_is_exercised_and_missing_mapping_fails(monkeypatch):
    from atm_mlmm.environment import check_required_apis
    from openmmml import MLPotential
    original = MLPotential.createMixedSystem
    @functools.wraps(original)
    def missing_mapping(*args, **kwargs):
        result = original(*args, **kwargs)
        result.pop('oldToNew')
        return result
    monkeypatch.setattr(MLPotential, 'createMixedSystem', missing_mapping)
    with pytest.raises(ValueError, match='oldToNew'):
        check_required_apis()


def test_version_drift_fails_before_numerical_probes(monkeypatch):
    from atm_mlmm.environment import check_required_apis
    import importlib.metadata as metadata
    version = metadata.version
    monkeypatch.setattr(metadata, 'version', lambda name: '8.1' if name == 'OpenMM' else version(name))
    with pytest.raises(ValueError, match='versions inconsistent'):
        check_required_apis()


def test_atomic_json_rejects_nonfinite_and_preserves_previous_file(tmp_path):
    from atm_mlmm.persistence import read_json, write_json
    target = tmp_path / 'manifest.json'
    write_json(target, {'energy': 1.5})
    with pytest.raises(ValueError):
        write_json(target, {'energy': float('nan')})
    assert read_json(target) == {'energy': 1.5}
