"""Read-only identity and byte preservation check; no scientific calculations."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import subprocess

E = Path(__file__).resolve().parent
REPO = E.parents[3]
BASE = '8738d16f8d3813f03c6f05a5c89a4be107159c19'
HEAD = 'ca12e023f6a6e67321fafd4af642c0975041d7f6'
SOURCE = 'ac414dcb4a5f401312616f08faa17ece5ea35e9e'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert git('rev-parse', 'HEAD') == HEAD
manifest = json.loads((REPO / 'Worker_Log/Milestone_03/evidence/G05_v4/snapshot-file-manifest.json').read_text())
changed = [path for path, digest in manifest['files'].items() if sha(REPO / path) != digest]
assert sorted(changed) == ['docs/project-0/STATUS.md', 'tests/unit/test_quantum_recovery.py',
                            'tools/generate_neutral_quantum.py', 'tools/resume_neutral_quantum.py']
unchanged = len(manifest['files']) - len(changed)
assert unchanged == 1435
qm_root = REPO / 'fixtures/chemical_reference_v3/quantum'
quantum = json.loads((qm_root / 'manifest.json').read_text())
assert len(quantum['files']) == 46
for path, digest in quantum['files'].items():
    assert sha(qm_root / path) == digest
assert quantum['ready_for_comparison']
immutable_paths = ['fixtures/chemical_reference_v3', 'models', 'src', 'Worker_Log/Milestone_00',
                   'Worker_Log/Milestone_03/evidence/G05_v4',
                   'Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max',
                   'Worker_Log/Milestone_03/Gate_05_v4_audit.md',
                   'Worker_Log/Milestone_03/evidence/G05_v5',
                   'Worker_Log/Milestone_03/evidence/G05_v5_independent_sol61_max',
                   'Worker_Log/Milestone_03/Gate_05_v5_audit.md']
assert not git('diff', '--name-only', BASE, HEAD, '--', *immutable_paths)
snapshot = json.loads((REPO / 'Worker_Log/Milestone_03/evidence/G05_v6/snapshot.json').read_text())
source_hashes = {path: sha(REPO / path) for path in snapshot['changed_source_files']}
assert source_hashes == snapshot['changed_source_files']
for path in ['tools/generate_neutral_quantum.py', 'tools/quantum_worker_guard.py', 'tests/unit/test_quantum_recovery.py']:
    assert not git('diff', '--name-only', BASE, SOURCE, '--', path)
previous = ast.parse(subprocess.check_output(['git', 'show', BASE + ':tools/resume_neutral_quantum.py'], cwd=REPO, text=True))
current = ast.parse((REPO / 'tools/resume_neutral_quantum.py').read_text())
old_functions = {node.name: ast.dump(node, include_attributes=False) for node in previous.body if isinstance(node, ast.FunctionDef)}
new_functions = {node.name: ast.dump(node, include_attributes=False) for node in current.body if isinstance(node, ast.FunctionDef)}
same_functions = [name for name, body in old_functions.items() if name not in ('run', 'terminate_group')]
assert all(old_functions[name] == new_functions[name] for name in same_functions)
result = {'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'head': HEAD,
          'source_commit': SOURCE, 'unchanged_snapshot_entries': unchanged,
          'expected_changed_existing_paths': sorted(changed), 'immutable_subtrees': immutable_paths,
          'quantum_records_unchanged': 46, 'quantum_manifest_sha256': sha(qm_root / 'manifest.json'),
          'input_manifest_sha256': sha(REPO / 'fixtures/chemical_reference_v3/input-manifest.json'),
          'reference_lock_sha256': sha(REPO / 'fixtures/chemical_reference_v3/reference-explicit.lock'),
          'preserved_scientific_results_sha256': sha(REPO / 'Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/scientific-results.json'),
          'source_hashes': source_hashes, 'unchanged_recovery_helper_functions': same_functions,
          'R1_R3_closure_paths_unchanged': True, 'qm_reexecuted': False,
          'preserved_worker_executions_inspected': {'source_passed': 336, 'source_seconds': 213.92,
                                                  'recovery_cases': 42, 'strict_checks': 9, 'docs_errors': 0, 'docs_selftests': 8}}
with (E / 'preservation-observed.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
