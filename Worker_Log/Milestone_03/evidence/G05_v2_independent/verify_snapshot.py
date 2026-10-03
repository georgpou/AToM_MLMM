"""Read-only source/input preservation and actual approval binding review."""
import gzip, hashlib, json, subprocess
from pathlib import Path
ROOT=Path.cwd(); BASE='a7768e375476667139db374dc0091999263a37de'; HEAD='3124c6d275bf19a32ce364dfdb83b11115828ac5'; PLAN='a825f5f1c2d8cf4146133c2049ef1c4eca550e93'
OUT=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args])
def unchanged(commit,paths):
 result={}
 for name in paths:
  old=git('show',commit+':'+name); current=(ROOT/name).read_bytes()
  result[name]={'snapshot_sha256':sha(current),'baseline_sha256':sha(old),'equal':old==current}
 assert all(r['equal'] for r in result.values())
 return result
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert git('status','--porcelain')==b''
manpath=ROOT/'Worker_Log/Milestone_03/evidence/G05_v2/source-input-manifest.json'
man=json.loads(manpath.read_text()); hashes={n:{'expected':h,'actual':sha((ROOT/n).read_bytes())} for n,h in man['files'].items()}
assert len(hashes)==270 and all(r['expected']==r['actual'] for r in hashes.values())
changed=git('diff','--name-only',BASE,HEAD,'--','src','tests','tools','fixtures','models','environment','docs/project-0/specs','docs/project-0/reference').decode().splitlines()
assert changed==['src/atm_mlmm/chemical_reference.py','tests/unit/test_reference_provenance.py'],changed
protected=git('ls-tree','-r','--name-only',BASE,'--','fixtures','models','environment','docs/project-0/specs','docs/project-0/reference','tools').decode().splitlines()
protected_result=unchanged(BASE,protected)
base_source=git('ls-tree','-r','--name-only',BASE,'--','src','tests').decode().splitlines()
source_result=unchanged(BASE,[p for p in base_source if p!='src/atm_mlmm/chemical_reference.py'])
plan_paths=git('ls-tree','-r','--name-only',PLAN,'--','fixtures/chemical_reference_v3','docs/project-0/reference/M00-neutral-reference-plan-v3.md').decode().splitlines()
plan_result=unchanged(PLAN,plan_paths)
decision_path='Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json'
decision=json.loads((ROOT/decision_path).read_text())
assert decision['reviewed_commit']==PLAN and decision['user_agreed'] is True
assert decision['input_manifest_sha256']==sha((ROOT/'fixtures/chemical_reference_v3/input-manifest.json').read_bytes())
assert decision['design_audit_sha256']==sha((ROOT/decision['design_audit_path']).read_bytes())
pending_path='Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-pending.json'
pending_result=unchanged(BASE,[pending_path]);assert json.loads((ROOT/pending_path).read_text())['user_agreed'] is False
captures={}
for name in ['red-reference-approval-binding','green-reference-approval-binding','full-after-provenance-repair','analytic-after-provenance-repair']:
 path=ROOT/'Worker_Log/Milestone_03/evidence/G05_v2'/(name+'.json.gz');d=json.loads(gzip.decompress(path.read_bytes()))
 captures[name]={'sha256':sha(path.read_bytes()),'command':d['command'],'cwd':d['cwd'],'head':d['head'],'exit_code':d['exit_code'],'summary':d['output'].splitlines()[-1]}
result=dict(head=HEAD,base=BASE,plan_commit=PLAN,source_input_manifest_sha256=sha(manpath.read_bytes()),manifest_files=hashes,production_and_test_changes=changed,protected_unchanged=protected_result,inherited_source_tests_unchanged=source_result,exact_M00_v3_unchanged=plan_result,actual_approval={'path':decision_path,'sha256':sha((ROOT/decision_path).read_bytes()),'input_manifest_binding':True,'audit_binding':True,'reviewed_commit':PLAN,'approved_resource_cap':decision['approved_resource_cap']},historical_pending_unchanged=pending_result,retained_worker_captures=captures,status=git('status','--porcelain').decode())
with (OUT/'snapshot-results.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'source_input_hashes':len(hashes),'protected_files_unchanged':len(protected_result),'inherited_source_tests_unchanged':len(source_result),'exact_M00_v3_unchanged':len(plan_result),'actual_approval_bindings':True,'retained_worker_capture_summaries':captures,'status':result['status']},indent=2))
