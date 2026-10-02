import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path('/workspace/AToM_MLMM-m00-review-v3');OUT=pathlib.Path(__file__).resolve().parent
F=ROOT/'fixtures/chemical_reference_v3';prefix=pathlib.Path('/workspace/atom-mlmm-reference-pilot-v2/env');checks=[]
def ck(k,v,d=None):checks.append({'check':k,'passed':bool(v),'details':d})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ref=json.loads((F/'reference-settings.json').read_text());actual={x['name']:x for p in (prefix/'conda-meta').glob('*.json') for x in [json.loads(p.read_text())]}
records=json.loads((ROOT/'Worker_Log/Milestone_00/evidence/M00_reference_v2/working-libxc-7.0.0/installed-packages.json').read_text());lock=[x for x in (F/'reference-explicit.lock').read_text().splitlines() if x.startswith('https://')]
ck('105 actual locked packages',len(actual)==len(records)==len(lock)==105)
for r in records:
 a=actual[r['name']];ck('package:'+r['name'],all(a.get(k)==r[k] for k in ['name','version','build','sha256']) and r['url']+'#'+r['sha256'] in lock)
for name,digest in ref['basis_file_sha256'].items():ck('basis:'+name,sha(prefix/'share/psi4/basis'/name)==digest)
for relative in ['fixtures/chemical_reference','tools/prepare_neutral_references.py','docs/project-0/reference/M00-neutral-reference-plan-v2.md']:
 diff=subprocess.check_output(['git','diff','321d7e3764a46eb5359a8d96bcab9124dccbc5f5','HEAD','--',relative],cwd=ROOT,text=True);ck('v2 preserved:'+relative,diff=='')
prov=ROOT/'Worker_Log/Milestone_00/evidence/M00_reference_v2/provenance'
for record in json.loads((prov/'manifest.json').read_text()):
 if 'sha256' in record:ck('provenance:'+record['path'],sha(prov/record['path'])==record['sha256'])
prior=ROOT/'Worker_Log/Milestone_00/evidence/M00_review_v2';em=json.loads((prior/'evidence-manifest.json').read_text())
for name,d in em['files'].items():ck('prior independent evidence:'+name,sha(prior/name)==d)
qr=json.loads((prior/'quantum-results.json').read_text());ck('prior methane exact settings',qr['settings']==ref['settings'] and qr['passed']==qr['total']==113 and not qr['failed'])
ck('prior methane no VV10',qr['variables']['DFT VV10 ENERGY']==0 and qr['variables']['DISPERSION CORRECTION ENERGY']!=0)
ck('resource caps',ref['wall_cap_hours']==12 and ref['threads']==2 and ref['memory']=='5 GiB')
ck('snapshot unchanged',subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True)=='')
r={'reviewed_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'target_calculations_run':0,'total':len(checks),'passed':sum(x['passed'] for x in checks),'failed':[x for x in checks if not x['passed']],'checks':checks};(OUT/'provenance-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2));sys.exit(bool(r['failed']))
