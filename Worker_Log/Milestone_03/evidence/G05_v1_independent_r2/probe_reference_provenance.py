"""Synthetic loader negatives only; no real approval, quantum or model evaluation."""
import copy,hashlib,json,pathlib,sys
from atm_mlmm.chemical_reference import load_references
from atm_mlmm.schema import IdentityError
OUT=pathlib.Path(__file__).parent
root=OUT/'synthetic-loader-fixture';(root/'structures').mkdir(parents=True);(root/'quantum/records').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
settings=json.loads(pathlib.Path('fixtures/chemical_reference_v3/reference-settings.json').read_text());settings['convergence_checks']['rows']=[]
settings['state']='SYNTHETIC SOFTWARE NEGATIVE ONLY; not the reviewed plan'
geometry={'name':'synthetic-h2','atomic_numbers':[1,1],'positions_angstrom':[[0.,0.,0.],[1.,0.,0.]]}
write(root/'structures/synthetic-h2.json',geometry);write(root/'reference-settings.json',settings)
inputs={'files':{n:sha(root/n) for n in ('structures/synthetic-h2.json','reference-settings.json')}}
write(root/'input-manifest.json',inputs)
record={'status':'computed','network_denied':True,'source_input_sha256':sha(root/'structures/synthetic-h2.json'),**geometry,
 'formal_charge':0,'multiplicity':1,'method':'wb97m-d3bj/def2-tzvppd','psi4_version':'1.10.2','basis_file_sha256':settings['basis_file_sha256'],
 'settings':settings['settings'],'energy_hartree':0.,'gradient_hartree_bohr':[[0.,0.,0.],[0.,0.,0.]],
 'notice':'SYNTHETIC ZERO ARRAYS; NO QUANTUM CALCULATION; NOT REFERENCE DATA'}
write(root/'quantum/records/synthetic-h2.json',record)
approval={'user_agreed':True,'design_verdict':'accepted_for_scope','reviewer_model':'gpt-6-astra','reasoning_effort':'high','fresh_context':True,
 'reviewed_commit':'0'*40,'input_manifest_sha256':sha(root/'input-manifest.json'),
 'notice':'SYNTHETIC BOOLEAN TEST DATA; NO ACTUAL USER AGREEMENT OR DESIGN APPROVAL'}
manifest={'ready_for_comparison':True,'approval':approval,'approval_sha256':'0'*64,'input_manifest_sha256':sha(root/'input-manifest.json'),
 'reference_settings_sha256':sha(root/'reference-settings.json'),'files':{'records/synthetic-h2.json':sha(root/'quantum/records/synthetic-h2.json')}}
results=[]
for label,mutate in [('matched-synthetic-control',lambda a:None),('wrong-approval-plan-hash',lambda a:a.update(input_manifest_sha256='f'*64)),
 ('missing-reviewed-commit',lambda a:a.pop('reviewed_commit')),('missing-approval-plan-hash',lambda a:a.pop('input_manifest_sha256')),
 ('unagreed-negative-control',lambda a:a.update(user_agreed=False))]:
 current=copy.deepcopy(manifest);mutate(current['approval']);write(root/'quantum/manifest.json',current)
 try:
  _,records=load_references(root);result={'case':label,'accepted':True,'rows':list(records)}
 except Exception as e:result={'case':label,'accepted':False,'exception':repr(e)}
 results.append(result)
# Leave only visibly unagreed sentinel manifest in the fixture.
write(OUT/'reference-provenance-results.json',{'scope':'synthetic loader software negatives only','results':results})
print(json.dumps(results,indent=2))
assert results[0]['accepted'] and not results[-1]['accepted']
