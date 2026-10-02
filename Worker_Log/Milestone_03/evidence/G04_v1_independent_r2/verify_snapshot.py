import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path.cwd(); out=pathlib.Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git',*args])
head=git('rev-parse','HEAD').decode().strip()
assert head=='35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a'
m=json.loads((root/'Worker_Log/Milestone_03/evidence/G04_v1/source-input-manifest.json').read_text())
p=json.loads((root/'Worker_Log/Milestone_03/evidence/G04_v1/preservation.json').read_text())
rows=[]
for kind,items,commit in [('inputs',m['sha256'],m['source_commit']),('inherited',p['unchanged_inherited_files'],p['base'])]:
 for path,expected in items.items():
  actual=sha((root/path).read_bytes()); committed=sha(git('show',commit+':'+path))
  rows.append(dict(kind=kind,path=path,expected=expected,actual=actual,commit=commit,committed=committed,match=actual==expected==committed))
report={'head':head,'rows':rows,'input_count':len(m['sha256']),'inherited_count':len(p['unchanged_inherited_files']),'all_match':all(r['match'] for r in rows),'source_diff':git('diff',m['source_commit'],head,'--','src','tests','fixtures','environment').decode(),'tracked_diff':git('diff','HEAD','--').decode(),'git_status':git('status','--short').decode()}
with (out/(sys.argv[1]+'.json')).open('x') as f:json.dump(report,f,indent=2)
print({k:v for k,v in report.items() if k!='rows'})
assert report['all_match'] and not report['source_diff'] and not report['tracked_diff']
