"""Validate actual completed references and controls before packaging the fixture.

Run after main activation with repository root and src on PYTHONPATH. This
uses the maintained importer and stable numerical-control check, never a model.
"""
import datetime
import hashlib
import json
from pathlib import Path
import os
import shutil

from atm_mlmm.chemical_reference import load_references
from tests.integration.test_chemical_reference import quantum_numerics

evidence = Path(__file__).resolve().parent
repo = evidence.parents[3]
plan = repo / 'fixtures/chemical_reference_v3'
attempt = repo / 'Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
generation = json.loads((attempt / 'manifest.json').read_text())
assert generation['ready_for_comparison'] is True
source = json.loads((evidence / 'calculation-source-input-manifest.json').read_text())
assert all(sha(repo / p) == digest for p, digest in source['files'].items())

validation = Path('/workspace/g05-reference-validation')
validation.mkdir(exist_ok=False)
for child in plan.iterdir():
    if child.name != 'quantum':
        (validation / child.name).symlink_to(child, target_is_directory=child.is_dir())
(validation / 'quantum').symlink_to(attempt, target_is_directory=True)
settings, references = load_references(validation)
assert len(references) == 46
capture = evidence / 'quantum-numerical-validation'
os.environ['ATOM_G05_CAPTURE_DIR'] = str(capture)
quantum_numerics(settings, references, {}, 'prebundle')
controls = capture / 'quantum-numerical-controls-prebundle.json'
assert len(json.loads(controls.read_text())['records']) == 12

target = plan / 'quantum'
target.mkdir(exist_ok=False)
(target / 'records').mkdir()
for name, digest in generation['files'].items():
    path = (attempt / name).resolve()
    assert path.is_relative_to(attempt.resolve()) and sha(path) == digest
    shutil.copyfile(path, target / name)
manifest = dict(generation, numerical_controls_passed=True,
                numerical_control_report_sha256=sha(controls),
                generation_manifest_sha256=sha(attempt / 'manifest.json'),
                calculation_source_commit=source['source_commit'])
with (target / 'manifest.json').open('x') as stream:
    json.dump(manifest, stream, indent=2, allow_nan=False)
    stream.write('\n')
_, actual = load_references(plan)
assert set(actual) == set(references)
report = dict(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              status='passed', actual_records=46, numerical_controls=12,
              input_manifest_sha256=sha(plan / 'input-manifest.json'),
              quantum_fixture_manifest_sha256=sha(target / 'manifest.json'),
              numerical_control_report_sha256=sha(controls),
              calculation_source_commit=source['source_commit'],
              model_evaluated=False, independent_audit_performed=False)
with (evidence / 'quantum-bundle-validation.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps(report))
