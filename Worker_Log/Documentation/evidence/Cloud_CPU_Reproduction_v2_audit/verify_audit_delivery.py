"""Check the audit's evidence/claim boundaries and preservation before delivery."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
initial = json.loads((out/'inherited-files.json').read_text())
allowed = {'AGENTS.md','AGENT_HANDOFF.md','README.md','docs/project-0/STATUS.md'}
changed = {p for p,digest in initial.items() if hashlib.sha256((root/p).read_bytes()).hexdigest() != digest}
assert changed == allowed, changed
for p in out.glob('*.py'): ast.parse(p.read_text(), filename=str(p))
subprocess.run(['bash','-n',str(out/'activation_probe.sh')],check=True)
baseline = json.loads((out/'docs-inherited-output.json').read_text())
final = json.loads((out/'final-docs-v3-output.json').read_text())
assert final['errors'] == baseline['errors'] and len(final['errors']) == 2
assert len(final['self_tests']) == 8 and all(final['self_tests'].values())
assert json.loads((out/'final-docs-v3.json').read_text())['exit_code'] == 1
for label in ['fresh','strict','replay','cloud']:
    data = json.loads((out/(label+'-validation.json')).read_text())
    assert data['environment_ok'] and not data['documentation_ok']
    assert len(data['results']) == 9
    assert [r['exit_code'] for r in data['results']] == [0]*8+[1]
    assert data['environment_only_exit'] == (label != 'strict')
    assert '1 passed' in next(r['output'] for r in data['results'] if r['name']=='atom_uwham')
for label in ['AToM-OpenMM','openmm-ml','openmmforcefields']:
    data = json.loads((out/('upstream-'+label+'-comparison.json')).read_text())
    assert data['fetched_commit'] == data['commit']
    assert data['all_names_types_modes_links_and_file_hashes_match'] and data['uncompressed_bytes_match']
failures = json.loads((out/'failure-probe-summary.json').read_text())
assert len(failures['checks']) == 5 and failures['all_five_negative_checks_passed']
assert all(r['exit_code']==1 and not r['main_env_created'] and not r['amber_env_created'] and not r['bootstrap_installed'] for r in failures['checks'])
assert failures['fallback_before'] == failures['fallback_after']
assert json.loads((out/'loading-policy-original.json').read_text())['exit_code'] == 1
assert json.loads((out/'loading-policy-scratch-candidate.json').read_text())['exit_code'] == 0
assert not json.loads((out/'runtime-identities.json').read_text())['unsafe_override_cleared']
assert json.loads((out/'activation-switching.json').read_text())['exit_code'] == 0
for label in ['fresh-install-v1b','installer-replay','cloud-fallback-success']:
    assert json.loads((out/(label+'.json')).read_text())['exit_code'] == 0
missing = json.loads((out/'amendment-delivery-history.json').read_text())
assert len(missing['missing_deliveries']) == 18
assert not any(p['claimed_after_found_in_reachable_path_history'] for p in missing['missing_deliveries'])
status = (root/'docs/project-0/STATUS.md').read_text()
audit = (root/'Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md').read_text()
for finding in ['A01','A02','A03','A04','A05','A06']:
    assert finding in status and finding in audit
for p in ['AGENTS.md','README.md','AGENT_HANDOFF.md','docs/project-0/STATUS.md']:
    assert 'NEXT_AGENT_REPAIR_HANDOUT.md' in (root/p).read_text()
assert 'changes_required' in audit and 'scratch-only' in audit
commands = [
 ['git','diff','--check'],
 ['git','diff','--exit-code','28f89cb23bdb7081c3723b9794fbde7d9bb50dca','--','environment','docs/project-0/specs','docs/project-0/gates','ATM_MLMM_environment.yml','Worker_Log/Milestone_00'],
 ['git','merge-base','--is-ancestor','28f89cb23bdb7081c3723b9794fbde7d9bb50dca','HEAD'],
 ['git','rev-parse','refs/remotes/origin/main'],
 ['git','branch','--show-current']]
recorded = []
for cmd in commands:
    p = subprocess.run(cmd,capture_output=True,text=True)
    assert p.returncode == 0, (cmd,p.stderr,p.stdout)
    recorded.append(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
assert recorded[-2]['stdout'].strip() == '2d7bcc94f901738e39f536f16de84699d4e8d631'
assert recorded[-1]['stdout'].strip() == 'm01-g00-environment-audit-v1'
result = dict(checked=datetime.datetime.now(datetime.timezone.utc).isoformat(), inherited_files=len(initial),
    allowed_reporting_changes=sorted(changed), other_inherited_files_preserved=len(initial)-len(changed),
    new_documentation_errors=0, remaining_documentation_errors=final['errors'], checker_self_tests=8,
    preserved_validation_runs=4, environment_checks_per_run=8, controlled_failure_cases=5,
    production_loading_policy_finding_still_open=True, gate_or_model_or_gpu_acceptance=False,
    source_comparisons=3, commands=recorded)
(out/'final-delivery-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
