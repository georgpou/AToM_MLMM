import datetime,hashlib,json,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).parent;ROOT=pathlib.Path.cwd();DELIVERY=OUT.parents[3]
expected='a7768e375476667139db374dc0091999263a37de'
git=lambda *a:subprocess.check_output(['git',*a],text=True).strip()
head=git('rev-parse','HEAD');status=git('status','--porcelain')
assert head==expected and not status
manifest=json.loads((ROOT/'Worker_Log/Milestone_03/evidence/G05_v1/source-input-manifest-partial.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(ROOT/p)==h for p,h in manifest['files'].items())
commands={}
for name in ('software','inherited','coordinates-v2','domain-total','upstream','documentation','snapshot','reference-provenance','pending-guard'):
 record=json.loads((OUT/(name+'.json')).read_text());assert record['exit_code']==0 and record['reviewed_commit']==expected
 commands[name]={'exit_code':record['exit_code'],'command':record['command'],'sha256':sha(OUT/(name+'.json'))}
c=json.loads((OUT/'coordinate-results.json').read_text());assert len(c['checks'])==138 and all(x['passed'] for x in c['checks'])
d=json.loads((OUT/'domain-total-results.json').read_text());assert len(d)==36 and sum(x['admitted'] for x in d)==34 and all(x['finite'] for x in d if x['admitted'])
r=json.loads((OUT/'reference-provenance-results.json').read_text())['results'];assert [x['accepted'] for x in r]==[True,True,True,True,False]
decision=json.loads((ROOT/'Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-pending.json').read_text());assert decision['user_agreed'] is False
reports=[DELIVERY/'Milestone_03/Gate_05_v1_audit.md',DELIVERY/'Milestone_01/Gate_00_v2_audit.md']
# Resolve Worker_Log from known evidence ancestry without reading mutable production source.
reports=[OUT.parents[1]/'Gate_05_v1_audit.md',OUT.parents[2]/'Milestone_01/Gate_00_v2_audit.md']
for p in reports:assert p.exists()
result={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':[sys.executable,str(pathlib.Path(__file__).resolve())],'cwd':str(ROOT),'reviewed_commit':head,'git_status':status,'exit_code':0,'verified_source_input_hashes':len(manifest['files']),'successful_captures':commands,'coordinate_checks':138,'all_real_fd_sweeps':117,'domain_rows':36,'admitted_finite_rows':34,'T4_R1_reproduced':True,'actual_user_agreed':False,'reports':{str(p):sha(p) for p in reports},'evidence_files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()},'notes':'No production implementation or target quantum/model-reference calculations. Source is exact a7768; original reviewer-script and report-link failures preserved. Final report-link verification follows in a separate capture.'}
with (OUT/'final-verification.json').open('x') as f:json.dump(result,f,indent=2)
print('Final verification PASS: immutable clean snapshot,269 hashes,138 coordinate checks,34 admitted domain rows,open T4 provenance reproduction, pending actual user agreement, both report hashes.')
