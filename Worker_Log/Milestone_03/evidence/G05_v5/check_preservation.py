"""Read-only reference/history checks; never executes a quantum worker."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools'))
from resume_neutral_quantum import queue, validate_record, validate_environment


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((ROOT / 'Worker_Log/Milestone_03/evidence/G05_v4/snapshot-file-manifest.json').read_text())
allowed = {'docs/project-0/STATUS.md', 'tools/generate_neutral_quantum.py',
           'tools/resume_neutral_quantum.py', 'tests/unit/test_quantum_recovery.py'}
changed = {name for name, expected in manifest['files'].items() if sha(ROOT / name) != expected}
assert changed == allowed, changed
plan = ROOT / 'fixtures/chemical_reference_v3'
settings = json.loads((plan / 'reference-settings.json').read_text())
orders = queue(plan, settings)
bundle = json.loads((plan / 'quantum/manifest.json').read_text())
assert bundle['ready_for_comparison'] is True
assert bundle['numerical_controls_passed'] is True
assert len(bundle['files']) == len(orders) == 46
for name, expected in bundle['files'].items():
    path = plan / 'quantum' / name
    validate_record(path, orders[path.stem], expected)
validate_environment('/workspace/atom-mlmm-reference-pilot-v2/env/bin/python', plan)
result = dict(snapshot_files=len(manifest['files']),
              unchanged_snapshot_files=len(manifest['files']) - len(changed),
              expected_changed_files=sorted(changed), quantum_records_verified=46,
              numerical_controls_prebundle_passed=True,
              input_manifest_sha256=sha(plan / 'input-manifest.json'),
              quantum_manifest_sha256=sha(plan / 'quantum/manifest.json'),
              quantum_and_history_bytes_unchanged=True, reference_lock_matches=True,
              qm_reexecuted=False)
destination = Path(sys.argv[1])
with destination.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result, indent=2))
