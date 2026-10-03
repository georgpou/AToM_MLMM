"""Read-only final audit/evidence checks."""
import hashlib,json,re,subprocess
from pathlib import Path
out=Path(__file__).parent;root=Path.cwd();audit=out.parent.parent/'Gate_05_v2_audit.md'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();status=subprocess.check_output(['git','status','--porcelain'],text=True)
assert head=='3124c6d275bf19a32ce364dfdb83b11115828ac5' and not status
manifest=json.loads((root/'Worker_Log/Milestone_03/evidence/G05_v2/source-input-manifest.json').read_text())
assert len(manifest['files'])==270
assert all(sha(root/p)==h for p,h in manifest['files'].items())
for name in ['focused.json','snapshot.json','binding.json']:
 c=json.loads((out/name).read_text());assert c['head']==head and c['exit_code']==0 and not c['status_before'] and not c['status_after']
b=json.loads((out/'binding-results.json').read_text());assert b['passed']==30 and b['positive']==1 and b['rejections']==29 and b['all_invalid_rejected_before_record_access']
for doc in [audit,out/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if not target.startswith(('http:','https:')):assert (doc.parent/target.split('#')[0]).exists(),target
text=audit.read_text();assert 'accepted_for_scope' in text and 'remain pending' in text and '3124c6d275bf19a32ce364dfdb83b11115828ac5' in text
files={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()};files['../../Gate_05_v2_audit.md']=sha(audit)
print(json.dumps({'head':head,'status':status,'verified_source_input_hashes':270,'independent_captures_verified':3,'synthetic_results_verified':True,'audit_links_resolve':True,'reviewer_artifact_sha256':files},indent=2))
