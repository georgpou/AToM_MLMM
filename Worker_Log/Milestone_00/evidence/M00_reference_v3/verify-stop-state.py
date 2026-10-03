"""Read-only verification of the user-requested G05 calculation checkpoint.

Run from the repository root with the activated core Python. This checks saved
data/provenance only; it launches no quantum calculation or model comparison.
"""
import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


root = Path.cwd()
evidence = root / 'Worker_Log/Milestone_00/evidence/M00_reference_v3'
attempt = evidence / 'quantum-attempt-v1'
plan = root / 'fixtures/chemical_reference_v3'
snapshot = json.loads((evidence / 'stop-state-20261003.json').read_text())
source_manifest = json.loads((root / 'Worker_Log/Milestone_03/evidence/G05_v2/source-input-manifest.json').read_text())
source_mismatches = [name for name, sha in source_manifest['files'].items()
                     if not (root / name).is_file() or digest(root / name) != sha]
assert not source_mismatches, source_mismatches
approval_path = root / 'Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json'
approval = json.loads(approval_path.read_text())
launch = json.loads((evidence / 'launch-v1.json').read_text())
assert digest(approval_path) == launch['approval_sha256']
assert approval['user_agreed'] is True
assert approval['design_verdict'] == 'accepted_for_scope'
assert approval['reviewer_model'] == 'gpt-6-astra'
assert approval['reasoning_effort'] == 'high' and approval['fresh_context'] is True
assert digest(root / approval['design_audit_path']) == approval['design_audit_sha256']
assert digest(plan / 'input-manifest.json') == approval['input_manifest_sha256']
assert digest(root / 'tools/generate_neutral_quantum.py') == launch['program_sha256']
manifest = json.loads((plan / 'input-manifest.json').read_text())
assert all(digest(plan / name) == sha for name, sha in manifest['files'].items())
settings = json.loads((plan / 'reference-settings.json').read_text())
prefix = Path(launch['reference_prefix'])
installed = {}
for path in (prefix / 'conda-meta').glob('*.json'):
    package = json.loads(path.read_text())
    installed[package.get('url', '').rsplit('/', 1)[-1]] = package.get('sha256')
expected_packages = {line.rsplit('#', 1)[0].rsplit('/', 1)[-1]: line.rsplit('#', 1)[1]
                     for line in (plan / 'reference-explicit.lock').read_text().splitlines()[1:]}
assert installed == expected_packages
queue = sorted(path.stem for path in (plan / 'structures').glob('*.json'))
queue += sorted(path.stem for path in (plan / 'quadrature_controls').glob('*.json'))
queue += [name + '-fine-grid' for name in settings['convergence_checks']['rows']]
assert len(queue) == len(set(queue)) == 46
completed = []
for path in sorted((attempt / 'records').glob('*.json')):
    record = json.loads(path.read_text())
    name = path.stem
    assert name in queue and record['name'] == name and record['status'] == 'computed'
    input_path = plan / 'structures' / (name + '.json')
    assert input_path.is_file(), 'The saved eight are ordinary target rows'
    structure = json.loads(input_path.read_text())
    order = json.loads((attempt / 'orders' / (name + '.json')).read_text())
    assert order['structure'] == structure
    assert record['source_input_sha256'] == order['source_input_sha256'] == digest(input_path)
    assert record['settings'] == order['settings'] == settings['settings']
    assert record['basis_file_sha256'] == order['basis_file_sha256'] == settings['basis_file_sha256']
    assert record['positions_angstrom'] == structure['positions_angstrom']
    assert record['atomic_numbers'] == structure['atomic_numbers']
    assert record['formal_charge'] == 0 and record['multiplicity'] == 1
    assert record['method'] == 'wb97m-d3bj/def2-tzvppd' and record['psi4_version'] == '1.10.2'
    assert record['network_denied'] is True and record['threads'] == 2 and record['memory'] == '5 GiB'
    assert math.isfinite(record['energy_hartree'])
    gradient = record['gradient_hartree_bohr']
    assert len(gradient) == len(record['atomic_numbers'])
    assert all(len(row) == 3 and all(math.isfinite(value) for value in row) for row in gradient)
    assert math.isfinite(record['wall_seconds']) and record['wall_seconds'] > 0
    assert abs(record['quantum_energy_variables'].get('DFT VV10 ENERGY', 0)) <= 1e-15
    assert 'DISPERSION CORRECTION ENERGY' in record['quantum_energy_variables']
    for suffix in ('.psi4.txt', '.psi4.log'):
        assert path.with_suffix(suffix).stat().st_size > 0
    launcher = attempt / (name + '.launcher.txt')
    receipts = [json.loads(line) for line in launcher.read_text().splitlines() if line.startswith('{')]
    assert any(item.get('name') == name and item.get('status') == 'computed' for item in receipts)
    completed.append({'name': name, 'sha256': digest(path), 'wall_seconds': record['wall_seconds'],
                      'atom_count': len(record['atomic_numbers']), 'record_provenance_verified': True})
assert [(item['name'], item['sha256']) for item in completed] == [
    (item['name'], item['sha256']) for item in snapshot['completed']]
remaining = sorted(set(queue) - {item['name'] for item in completed})
assert remaining == snapshot['remaining'] and len(completed) == 8 and len(remaining) == 38
assert not (attempt / 'manifest.json').exists()
processes = []
for path in Path('/proc').iterdir():
    if not path.name.isdigit():
        continue
    try:
        argv = path.joinpath('cmdline').read_bytes().decode().split('\0')
        if len(argv) > 1 and argv[1].endswith('generate_neutral_quantum.py'):
            processes.append({'pid': int(path.name), 'argv': argv})
    except (OSError, UnicodeError):
        pass
assert not processes, processes
disk = shutil.disk_usage(root)
memory = {name: (Path('/sys/fs/cgroup') / name).read_text().strip()
          for name in ('memory.max', 'memory.current', 'memory.peak', 'memory.events')}
output = {
    'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'read-only checkpoint verification; no quantum/model execution or chemical acceptance',
    'HEAD_before_checkpoint_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'source_input_hashes_matched': len(source_manifest['files']),
    'frozen_plan_hashes_matched': len(manifest['files']),
    'reference_lock_packages_matched': len(expected_packages),
    'completed': completed, 'remaining': remaining,
    'saved_worker_wall_seconds_sum': sum(item['wall_seconds'] for item in completed),
    'coordinator_manifest_exists': False, 'visible_quantum_processes': processes,
    'workspace_disk_bytes': dict(zip(('total', 'used', 'free'), disk)),
    'container_memory': memory,
    'interpretation': 'Eight valid saved target records; full 46-row batch and chemical comparison remain pending.'
}
(evidence / 'checkpoint-verification.json').write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
print(json.dumps({key: value for key, value in output.items() if key not in ('completed', 'remaining')}, indent=2))
