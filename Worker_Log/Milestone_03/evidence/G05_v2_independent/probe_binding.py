"""Independent synthetic-only binding probe. No real approval, Q, or model evaluation."""
import copy, hashlib, json, tempfile
from pathlib import Path
from unittest.mock import patch
from atm_mlmm.chemical_reference import load_references
from atm_mlmm.schema import IdentityError
OUT=Path(__file__).parent
NOTICE='SYNTHETIC SOFTWARE PROBE ONLY: fabricated approval and arrays; NOT quantum or chemical evidence'
def put(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,sort_keys=True)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
rows=[]
with tempfile.TemporaryDirectory(prefix='synthetic-binding-',dir=OUT) as td:
 root=Path(td);record_path=root/'quantum/records/probe-h2.json'
 geometry=dict(atomic_numbers=[1,1],positions_angstrom=[[0.,0.,0.],[0.9,0.2,0.1]],notice=NOTICE)
 settings=dict(settings={'basis':'def2-tzvppd'},basis_file_sha256={'def2-tzvppd.gbs':'b'*64},convergence_checks={'rows':[]},hartree_to_kJ_mol=2625.4996382852164,bohr_to_nm=0.052917721067,notice=NOTICE)
 put(root/'structures/probe-h2.json',geometry);put(root/'reference-settings.json',settings)
 inputs={'notice':NOTICE,'files':{'structures/probe-h2.json':digest(root/'structures/probe-h2.json'),'reference-settings.json':digest(root/'reference-settings.json')}}
 put(root/'input-manifest.json',inputs)
 record=dict(geometry,status='computed',network_denied=True,source_input_sha256=digest(root/'structures/probe-h2.json'),formal_charge=0,multiplicity=1,method='wb97m-d3bj/def2-tzvppd',psi4_version='1.10.2',basis_file_sha256=settings['basis_file_sha256'],settings=settings['settings'],energy_hartree=0.,gradient_hartree_bohr=[[0.,0.,0.],[0.,0.,0.]])
 put(record_path,record)
 approval=dict(user_agreed=True,design_verdict='accepted_for_scope',reviewer_model='gpt-6-astra',reasoning_effort='high',fresh_context=True,reviewed_commit='0123456789abcdef'*2+'01234567',input_manifest_sha256=digest(root/'input-manifest.json'),notice=NOTICE)
 original=dict(ready_for_comparison=True,approval=approval,input_manifest_sha256=digest(root/'input-manifest.json'),reference_settings_sha256=digest(root/'reference-settings.json'),files={'records/probe-h2.json':digest(record_path)},notice=NOTICE)
 cases=[('matched',None,None,False)]
 for field,values in [('input_manifest_sha256',['MISSING',None,'f'*64,'',123,True,[],{}]),('reviewed_commit',['MISSING',None,'','a'*39,'a'*41,'g'*40,'A'*40,'a'*40+'\n',' '+'a'*40,123,True,[],{}]),('user_agreed',[False,'MISSING',1]),('fresh_context',[False]),('design_verdict',['changes_required'])]:
  for i,value in enumerate(values):cases.append((field+'-'+str(i),field,value,True))
 cases.extend([('copied-approval-and-outer-wrong-digest','BOTH_HASH','f'*64,True),('changed-plan-self-consistent-outer','PLAN',None,True),('outer-plan-hash-mismatch','OUTER_HASH','f'*64,True)])
 for name,field,value,reject in cases:
  put(root/'input-manifest.json',inputs);m=copy.deepcopy(original)
  if field=='BOTH_HASH':m['approval']['input_manifest_sha256']=value;m['input_manifest_sha256']=value
  elif field=='PLAN':
   altered=copy.deepcopy(inputs);altered['notice']+='; different plan bytes';put(root/'input-manifest.json',altered);m['input_manifest_sha256']=digest(root/'input-manifest.json')
  elif field=='OUTER_HASH':m['input_manifest_sha256']=value
  elif field:
   if value=='MISSING':m['approval'].pop(field)
   else:m['approval'][field]=value
  put(root/'quantum/manifest.json',m)
  opened=[];real_open=Path.open
  def observed_open(path,*args,**kwargs):
   if path==record_path:opened.append(str(path.relative_to(root)))
   return real_open(path,*args,**kwargs)
  message=None;loaded=None
  try:
   with patch.object(Path,'open',observed_open):_,loaded=load_references(root)
  except IdentityError as exc:message=str(exc)
  assert (message is not None)==reject,(name,message)
  if reject:assert not opened,(name,opened)
  else:assert set(loaded)=={'probe-h2'} and opened
  rows.append(dict(case=name,field=field,value=value,expected_rejection=reject,rejected=message is not None,message=message,record_opens=opened))
 result=dict(notice=NOTICE,baseline_fixture={'geometry':geometry,'settings':settings,'inputs':inputs,'record':record,'manifest':original},cases=rows,passed=len(rows),positive=sum(not r['expected_rejection'] for r in rows),rejections=sum(r['expected_rejection'] for r in rows),all_invalid_rejected_before_record_access=True)
 with (OUT/'binding-results.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['baseline_fixture','cases']},indent=2))
