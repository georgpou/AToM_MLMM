from pathlib import Path
import json,hashlib,subprocess,datetime,re,os,math
root=Path.cwd(); e=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def git(*a):return subprocess.check_output(['git',*a])
base=root/'Worker_Log/Milestone_03/evidence/G05_v4'; plan=root/'fixtures/chemical_reference_v3'
full=read(base/'snapshot-file-manifest.json');source=read(base/'calculation-source-input-manifest.json')
checks={}
for label,manifest in [('snapshot_files',full),('calculation_source_inputs',source),('frozen_inputs',read(plan/'input-manifest.json'))]:
 prefix=plan if label=='frozen_inputs' else root
 mismatch=[path for path,digest in manifest['files'].items() if sha(prefix/path)!=digest]
 assert not mismatch,mismatch
 checks[label]={'count':len(manifest['files']),'mismatches':mismatch}
assert sha(base/'snapshot-file-manifest.json')==read(base/'audit-snapshot.json')['snapshot_file_manifest_sha256']
reviewed=read(plan/'quantum/manifest.json')['approval']['reviewed_commit']
for path in read(plan/'input-manifest.json')['files']:
 rel=str((plan/path).relative_to(root)); assert git('show',reviewed+':'+rel)==(root/rel).read_bytes(),rel
checks['approved_input_files_match_reviewed_commit']=reviewed
for path in source['files']:assert git('show',source['source_commit']+':'+path)==(root/path).read_bytes(),path
hist=root/'Worker_Log/Milestone_00/evidence/M00_reference_v3';attempt=hist/'quantum-attempt-v2'
oldpaths=git('ls-tree','-r','--name-only','4bb2547684cb9a40de1d65819dfe0cbcae145249','--',str((hist/'quantum-attempt-v1').relative_to(root))).decode().splitlines()
for rel in oldpaths:assert git('show','4bb2547684cb9a40de1d65819dfe0cbcae145249:'+rel)==(root/rel).read_bytes(),rel
checks['unchanged_v1_files']=len(oldpaths)
qmanifest=read(plan/'quantum/manifest.json');generation=read(attempt/'manifest.json');progress=read(attempt/'progress.json')
assert qmanifest['generation_manifest_sha256']==sha(attempt/'manifest.json')
assert qmanifest['numerical_control_report_sha256']==sha(base/'quantum-numerical-validation/quantum-numerical-controls-prebundle.json')
assert qmanifest['files']==generation['files']
assert len(qmanifest['files'])==46
job_details=[]
for rel,digest in qmanifest['files'].items():
 assert sha(plan/'quantum'/rel)==digest==sha(attempt/rel)
 name=Path(rel).stem;record=read(plan/'quantum'/rel)
 assert record['status']=='computed' and record['threads']==2
 assert all(math.isfinite(float(v)) for row in record['gradient_hartree_bohr'] for v in row)
 v=record['quantum_energy_variables']; scf=v.get('DFT FUNCTIONAL TOTAL ENERGY')
 if scf is not None:assert abs(record['energy_hartree']-scf-v['DISPERSION CORRECTION ENERGY'])<1e-10
 assert abs(v.get('DFT VV10 ENERGY',0))<1e-15
 provenance=progress['provenance'][name];record_path=Path(provenance['source'])
 assert record_path.read_bytes()==(plan/'quantum'/rel).read_bytes()
 log=record_path.with_suffix('.psi4.txt').read_text()
 assert 'Energy and wave function converged.' in log or 'Energy and wavefunction converged.' in log or re.search(r'Energy and wave.?function converged',log),name
 assert 'LibXC Version 7.0.0' in log or 'Libxc Version 7.0.0' in log or re.search(r'Lib[Xx][Cc].*?7\.0\.0',log,re.S),name
 assert 'WB97M' in log.upper() and 'D3BJ' in log.upper(),name
 gradient_text=log.rsplit('-Total Gradient:',1)[1]
 parsed=re.findall(r'^\s+\d+\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)',gradient_text,re.M)
 assert len(parsed)==len(record['atomic_numbers']),name
 assert max(abs(float(a)-float(b)) for text,row in zip(parsed,record['gradient_hartree_bohr']) for a,b in zip(text,row))<5.1e-13,name
 detail={'name':name,'record_sha256':digest,'reused':provenance['recovered'],'converged_log':str(record_path.with_suffix('.psi4.txt').relative_to(root))}
 if not provenance['recovered']:
  receipt=read(Path(provenance['receipt']));assert receipt['exit']==0 and receipt['reason'] is None
  order=read(record_path.parent/'order.json'); assert order['runtime_memory']=='3 GiB'
  assert record['memory']=='3 GiB'
  samples=[json.loads(line) for line in (record_path.parent/'resources.jsonl').read_text().splitlines()]
  for sample in samples:
   events=dict(line.split() for line in sample.get('memory.events','').splitlines());assert int(events.get('oom',0))==int(events.get('oom_kill',0))==0
  detail.update(worker_exit=receipt['exit'],worker_peak_rss_bytes=record['peak_rss_bytes'],sampled_peak_rss_bytes=receipt['sampled_rss_peak_bytes'],resource_sample_count=len(samples))
 else:detail['coordinator_exit']=provenance['coordinator_exit']
 job_details.append(detail)
assert sum(d['reused'] for d in job_details)==8
assert not list(attempt.glob('jobs/*/attempt-*/scratch'))
start=datetime.datetime.fromisoformat(read(hist/'launch-v1.json')['recorded_utc']);stop=datetime.datetime.fromisoformat(read(hist/'stop-state-20261003.json')['recorded_utc'])
prior=(stop-start).total_seconds();debit=prior+sum(s['wall_seconds'] for s in progress['sessions'])
assert abs(debit-progress['wall_seconds_debited'])<1e-9 and debit<=43200
assert abs(debit/3600-read(base/'results-summary.json')['charged_wall_hours'])<1e-12
peak=max(d.get('worker_peak_rss_bytes',0) for d in job_details)
assert peak/2**30==read(base/'results-summary.json')['peak_new_worker_rss_gib']
ref=Path('/workspace/atom-mlmm-reference-pilot-v2/env');installed={}
for file in (ref/'conda-meta').glob('*.json'):
 data=read(file);installed[data.get('url','').rsplit('/',1)[-1]]=data.get('sha256')
expected={line.rsplit('#',1)[0].rsplit('/',1)[-1]:line.rsplit('#',1)[1] for line in (plan/'reference-explicit.lock').read_text().splitlines() if line.startswith('https://')}
assert installed==expected and len(expected)==105
active=[]
for proc in Path('/proc').iterdir():
 if proc.name.isdigit():
  try:cmd=(proc/'cmdline').read_bytes().split(b'\0')
  except (OSError,PermissionError):continue
  if any(x.endswith((b'/generate_neutral_quantum.py',b'/resume_neutral_quantum.py')) for x in cmd):active.append({'pid':proc.name,'command':[x.decode(errors='replace') for x in cmd if x]})
assert not active,active
checks.update(reference_locked_packages=len(expected),quantum_records=46,reused_records=8,new_zero_exit_workers=38,all_logs_converged=True,prior_debit_seconds=prior,cumulative_debit_hours=debit/3600,peak_worker_rss_gib=peak/2**30,private_scratch_count=0,active_qm_processes=active)
out={'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'job_details':job_details}
with (e/'integrity-results.json').open('x') as stream:json.dump(out,stream,indent=2);stream.write('\n')
print(json.dumps(checks,indent=2))
