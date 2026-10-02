import ast,datetime,gzip,hashlib,json,pathlib,subprocess
R=pathlib.Path.cwd();O=R/'Worker_Log/Milestone_02/evidence/M02_v2_independent';base='a8098a43d46df76b981861aa8dec0522d31be966'
def git(*args): return subprocess.check_output(['git',*args],text=True).strip()
head=git('rev-parse','HEAD');assert head=='6015a652c4a9a9c968ab7933c07ac7bbb4573e12'
paths=git('ls-tree','-r','--name-only',base,'Worker_Log/Milestone_02').splitlines();assert len(paths)==28
rows={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
assert all((R/p).read_bytes()==subprocess.check_output(['git','show',base+':'+p]) for p in paths)
manifest=json.loads((R/'Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json').read_text())
assert len(manifest['sha256'])==127
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in manifest['sha256'].items())
assert not git('diff','--name-only','33daa6bebd91c49ad87f822d48cfa87e600deb6d','HEAD','--','src','tests','fixtures','environment')
old=ast.parse(git('show',base+':src/atm_mlmm/atm.py'));new=ast.parse((R/'src/atm_mlmm/atm.py').read_text())
for name in ('load_bundle','save_bundle','physical_system'):
 a=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name)
 b=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(a)==ast.dump(b),name
strict=pathlib.Path('/workspace/.onboarding/atom-mlmm-m02-v2/logs/validation-20261002T132015Z-17412/results.json')
raw=json.loads(strict.read_text());assert len(raw['results'])==9 and all(x['exit_code']==0 for x in raw['results'])
with gzip.open(O/'strict-validation.json.gz','wt') as f:json.dump(raw,f,indent=2)
worker=R/'Worker_Log/Milestone_02/evidence/M02_v2'
red=[]
for name in ('regressions-red','regressions-red-corrected','r1-additional-red','r2-green','r2-green-source-guard'):
 data=json.load(gzip.open(worker/(name+'.json.gz'),'rt'))
 red.append(dict(name=name,exit_code=data['exit_code'],output_tail=data['output'][-1600:]))
report=dict(head=head,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_input_hash_count=127,all_source_inputs_match=True,all_28_handoff_milestone_files_unchanged=rows,trusted_loader_and_physical_deserialization_functions_unchanged=True,strict_source=str(strict),strict_source_sha256=hashlib.sha256(strict.read_bytes()).hexdigest(),worker_red_evidence_inspected=red)
(O/'final-input-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('127 source/input hashes match; all 28 handoff milestone files unchanged; loader AST unchanged; strict 9/9 output preserved.')
for r in red:print(r['name'],r['exit_code'],r['output_tail'][-180:])
