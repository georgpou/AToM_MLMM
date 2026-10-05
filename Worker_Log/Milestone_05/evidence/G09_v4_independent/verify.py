"""Verify exact repair hashes and carry-forward scientific identity."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT/'Worker_Log/Milestone_05/evidence'
BASE = 'b11c16750ad111a2fcafcda7a2d51c6690254e97'
TESTED = '027f8173babc13606afb24d96f58148704e38b1b'
HEAD = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert HEAD == '09a85d979fe9fce2ceca23da74509846254df9b1'
manifest = json.loads((EVIDENCE/'G09_v4/scientific-source-input-manifest.json').read_text())
assert len(manifest) == 49
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest,name
    assert hashlib.sha256(subprocess.check_output(['git','show',f'{TESTED}:{name}'],cwd=ROOT)).hexdigest() == digest,name
old = json.loads((EVIDENCE/'G09_v3/scientific-source-input-manifest.json').read_text())
assert set(manifest)-set(old) == {'tests/workflow/test_failure_archive_errors.py'}
assert {name for name in old if old[name] != manifest[name]} == {'src/atm_mlmm/workflow.py','src/atm_mlmm/__main__.py'}
lines = (EVIDENCE/'G09_v4/file-manifest.sha256').read_text().splitlines()
for row in lines:
    digest,name = row.split('  ',1)
    assert hashlib.sha256((EVIDENCE/'G09_v4'/name).read_bytes()).hexdigest() == digest,name
changed = subprocess.check_output(['git','diff','--name-only',BASE,'HEAD','--','src','tests','fixtures','models','environment'],cwd=ROOT,text=True).splitlines()
assert set(changed) == {'src/atm_mlmm/workflow.py','src/atm_mlmm/__main__.py','tests/workflow/test_failure_archive_errors.py'}
amendment = 'docs/project-0/specs/cloud-solvent-control-amendment.md'
old_amendment = subprocess.check_output(['git','show',f'{BASE}:{amendment}'],cwd=ROOT,text=True)
current_amendment = (ROOT/amendment).read_text()
def scientific_body(text):
    return text.split('## Scientific definition and rationale',1)[1].split('## Reviewer decision',1)[0]
assert scientific_body(old_amendment) == scientific_body(current_amendment)
prior = subprocess.check_output(['git','diff','--name-only',BASE,'HEAD','--','Worker_Log/Milestone_03','Worker_Log/Milestone_04','Worker_Log/Milestone_05/evidence/G09_v3','Worker_Log/Milestone_05/evidence/G10_v1'],cwd=ROOT,text=True)
assert not prior
result = {'reviewed_head':HEAD,'tested_repair':TESTED,'source_input_regression_hashes':len(manifest),
          'capture_hashes':len(lines),'changed_scientific_or_code_paths':changed,
          'physical_inputs_builder_routing_adapter_tolerances_amendment_definition_unchanged':True,
          'amendment_review_status_and_decision_updated':old_amendment != current_amendment,
          'earlier_evidence_models_locks_unchanged':True}
(EVIDENCE/'G09_v4_independent/verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
