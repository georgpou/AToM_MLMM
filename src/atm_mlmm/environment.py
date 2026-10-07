"""G00 analytic CPU API probes and exact installed-source provenance."""
import hashlib
import importlib.metadata as metadata
import inspect
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile


def require_api(owner, name):
    if not hasattr(owner, name):
        raise ValueError(f'required API missing: {name}')
    return getattr(owner, name)


def _selected_harmonic(state):
    import numpy as np
    from openmm import unit
    positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    return 2.0 * np.sum(positions * positions), -4.0 * positions


def check_required_apis():
    import numpy as np
    import openmm as mm
    from openmm import unit
    from openmmml import MLPotential
    for name in ('ATMForce', 'PythonForce', 'XmlSerializer'):
        require_api(mm, name)
    require_api(mm.PythonForce, 'setParticles')
    if 'returnInfo' not in inspect.signature(MLPotential.createMixedSystem).parameters:
        raise ValueError('required mixed-system returnInfo API missing')
    versions = {'openmm_version': metadata.version('OpenMM'),
                'openmmml_version': metadata.version('openmmml'),
                'atom_package_version': metadata.version('atom-openmm')}
    expected = {'openmm_version': '8.6.1', 'openmmml_version': '1.8',
                'atom_package_version': '8.5.0b0'}
    if versions != expected:
        raise ValueError(f'locked API versions inconsistent: {versions}, expected {expected}')
    from openmm import app
    from ase.calculators.calculator import Calculator
    topology = app.Topology()
    chain = topology.addChain('api')
    residue = topology.addResidue('API', chain)
    topology.addAtom('H', app.element.hydrogen, residue)
    original = mm.System()
    original.addParticle(1.0)
    info = MLPotential('ase').createMixedSystem(topology, original, [0],
                                              calculator=Calculator(), returnInfo=True)
    if not isinstance(info, dict) or not {'system', 'topology', 'oldToNew'} <= info.keys():
        raise ValueError('mixed-system info missing system/topology/oldToNew')
    if info['oldToNew'] != [0] or info['system'].getNumParticles() != 1 or info['topology'].getNumAtoms() != 1:
        raise ValueError('mixed-system oldToNew/particle identity mismatch')
    system = mm.System()
    system.addParticle(12.0)
    system.addParticle(1.0)
    force = mm.PythonForce(_selected_harmonic)
    force.setParticles([1])
    system.addForce(force)
    integrator = mm.VerletIntegrator(0.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
    context.setPositions([[0.9, 0, 0], [0.2, 0, 0]])
    state = context.getState(getEnergy=True, getForces=True)
    energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
    if abs(energy - 0.08) > 1e-8 or not np.allclose(forces, [[0, 0, 0], [-0.8, 0, 0]], rtol=0, atol=1e-7):
        raise ValueError('PythonForce selected-particle energy/force mismatch')
    del context, integrator
    # Only serialize objects constructed here. Never deserialize a supplied PythonForce.
    native = mm.ATMForce('u0')
    native.addParticle(mm.Vec3(0, 0, 0))
    child = mm.CustomExternalForce('x*x')
    child.addParticle(0, [])
    native.addForce(child)
    plain = mm.System()
    plain.addParticle(12.0)
    plain.addForce(native)
    rebuilt = mm.XmlSerializer.deserialize(mm.XmlSerializer.serialize(plain))
    if rebuilt.getNumParticles() != 1 or not isinstance(rebuilt.getForce(0), mm.ATMForce):
        raise ValueError('native ATM System serialization mismatch')
    return dict(versions, checks=dict(native_atm=True, selected_particle_python_force=True,
                                     mixed_system_info=True, serialization=True))


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def characterize_environment(repository, setup_root):
    repository, root = Path(repository).resolve(), Path(setup_root).resolve()
    if Path(sys.prefix).resolve() != root / 'env':
        raise ValueError(f'activate the locked main environment: {root / "env"}')
    bundle = repository / 'environment/cloud-cpu'
    checks = []
    builds, inventories, locks = {}, {}, {}
    # Validate the named installation's locked inventory, not metadata from
    # whichever source checkout happened to invoke this function.
    check_env = os.environ.copy()
    check_env.pop('PYTHONPATH', None)
    for label, prefix in (('core', root/'env'), ('amber', root/'amber-env')):
        builds[label] = []
        for path in sorted((prefix/'conda-meta').glob('*.json')):
            installed = json.loads(path.read_text())
            # Build identities and dependencies suffice; thousands of per-package
            # file entries are reproducible from the hashed artifact, not new evidence.
            keys = ('name', 'version', 'build', 'build_number', 'subdir', 'url', 'sha256', 'depends')
            builds[label].append({key: installed[key] for key in keys if key in installed})
        if not builds[label]:
            raise ValueError(f'missing {label} Conda builds')
        command = [str(prefix/'bin/python'), '-c',
                   'import importlib.metadata as m,json; print(json.dumps({d.metadata["Name"]:d.version for d in m.distributions()}))']
        inventories[label] = json.loads(subprocess.check_output(command, text=True, env=check_env))
        for kind, command in (
            ('exact_versions', [str(prefix/'bin/python'), str(bundle/'check_versions.py'), str(root), label]),
            ('pip_check', [str(prefix/'bin/python'), '-m', 'pip', 'check']),
        ):
            run = subprocess.run(command, text=True, capture_output=True, env=check_env)
            checks.append(dict(name=f'{label}_{kind}', command=command, exit_code=run.returncode,
                               output=run.stdout+run.stderr))
        name = f'{label}-conda-linux-64.lock'
        locks[name] = _digest(bundle/name)
        if _digest(root/name) != locks[name]:
            raise ValueError(f'installed {name} differs from repository lock')
    for name in ('pip-wheels.lock', 'wheels.sha256', 'core-pip-inventory.txt', 'amber-pip-inventory.txt', 'bundle.sha256'):
        locks[name] = _digest(bundle/name)
        if _digest(root/name) != locks[name]:
            raise ValueError(f'installed {name} differs from repository lock')
    run = subprocess.run([sys.executable, '-m', 'openmm.testInstallation'], text=True, capture_output=True)
    checks.append(dict(name='openmm_installation', command=[sys.executable, '-m', 'openmm.testInstallation'],
                       exit_code=run.returncode, output=run.stdout+run.stderr))
    sources = json.loads((bundle/'upstream-sources.json').read_text())
    approved = dict(line.split('  ', 1)[::-1] for line in (bundle/'bundle.sha256').read_text().splitlines())
    for source in sources:
        archive = bundle / source['archive']
        source['archive_sha256'] = _digest(archive)
        if approved.get(source['archive']) != source['archive_sha256']:
            raise ValueError(f'archive digest mismatch: {source["directory"]}')
        with tarfile.open(archive) as packed:
            for member in packed.getmembers():
                if member.isfile():
                    extracted = root/'sources'/source['directory']/member.name
                    if not extracted.is_file() or _digest(extracted) != hashlib.sha256(packed.extractfile(member).read()).hexdigest():
                        raise ValueError(f'installed source differs: {source["directory"]}/{member.name}')
    report = dict(schema_version='1.0', profile='core-analytic-cpu', setup_root=str(root),
                  python_version=platform.python_version(),
                  platform=dict(system=platform.system(), machine=platform.machine()),
                  locks=locks, conda_builds=builds, python_distributions=inventories,
                  sources=sources, dependency_checks=checks, api_checks=check_required_apis(),
                  deferred_profiles=dict(model_assets='not_run', gpu='not_run'))
    validate_environment_manifest(report)
    return report


def validate_environment_manifest(report):
    for field in ('schema_version', 'profile', 'setup_root', 'python_version', 'platform', 'locks',
                  'conda_builds', 'python_distributions', 'sources', 'dependency_checks', 'api_checks', 'deferred_profiles'):
        if not report.get(field):
            raise ValueError(f'environment manifest missing {field}')
    if report['schema_version'] != '1.0' or report['profile'] != 'core-analytic-cpu':
        raise ValueError('unsupported environment schema/profile')
    if report['python_version'] != '3.11.16':
        raise ValueError('python_version differs from locked patch version')
    if report['platform'] != dict(system='Linux', machine='x86_64'):
        raise ValueError('platform differs from locked Linux x86_64 profile')
    required_locks = {'core-conda-linux-64.lock', 'amber-conda-linux-64.lock', 'pip-wheels.lock',
                      'wheels.sha256', 'core-pip-inventory.txt', 'amber-pip-inventory.txt', 'bundle.sha256'}
    if set(report['locks']) != required_locks:
        raise ValueError('locks incomplete or inconsistent with the CPU profile')
    for name, digest in report['locks'].items():
        if not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError(f'invalid lock digest: {name}')
    if {s['directory'] for s in report['sources']} != {'AToM-OpenMM', 'openmm-ml', 'openmmforcefields'}:
        raise ValueError('sources incomplete')
    for source in report['sources']:
        if not re.fullmatch('[0-9a-f]{40}', source.get('commit', '')):
            raise ValueError('source commit must be a full immutable SHA')
        if source['commit'] not in source.get('archive', ''):
            raise ValueError('source commit differs from its pinned archive identity')
        for field in ('tag', 'distribution_version', 'archive_sha256'):
            if not source.get(field):
                raise ValueError(f'source missing {field}')
        if not re.fullmatch('[0-9a-f]{64}', source['archive_sha256']):
            raise ValueError('source archive digest must be SHA-256')
        distribution = {'AToM-OpenMM': 'atom-openmm', 'openmm-ml': 'openmmml', 'openmmforcefields': 'openmmforcefields'}[source['directory']]
        installed = {re.sub('[-_.]+', '-', name).lower(): version for name, version in report['python_distributions']['core'].items()}
        if installed.get(distribution) != source['distribution_version']:
            raise ValueError(f'source/package version mismatch: {source["directory"]}')
    expected = {'core_exact_versions', 'amber_exact_versions', 'core_pip_check', 'amber_pip_check', 'openmm_installation'}
    if {c['name'] for c in report['dependency_checks']} != expected or any(c['exit_code'] != 0 for c in report['dependency_checks']):
        raise ValueError('dependency checks missing or failed')
    for label in ('core', 'amber'):
        if not report['conda_builds'].get(label) or not report['python_distributions'].get(label):
            raise ValueError(f'conda_builds/python_distributions missing {label}')
        for build in report['conda_builds'][label]:
            for field in ('name', 'version', 'build', 'url', 'sha256'):
                if not build.get(field):
                    raise ValueError(f'conda_builds missing {field}')
            if not re.fullmatch('[0-9a-f]{64}', build['sha256']):
                raise ValueError('conda_builds artifact digest must be SHA-256')
    api = report['api_checks']
    if api.get('checks') != dict(native_atm=True, selected_particle_python_force=True,
                                  mixed_system_info=True, serialization=True):
        raise ValueError('API checks incomplete or failed')
    if (api.get('openmm_version'), api.get('openmmml_version'), api.get('atom_package_version')) != ('8.6.1', '1.8', '8.5.0b0'):
        raise ValueError('API/package versions inconsistent')
    if report['deferred_profiles'] != dict(model_assets='not_run', gpu='not_run'):
        raise ValueError('deferred profiles cannot be qualified by analytic CPU evidence')
    return None
