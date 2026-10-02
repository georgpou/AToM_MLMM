"""Independent frozen-v3 review; geometry and integrity only, no target scores."""
import ast, contextlib, hashlib, importlib.util, io, json, pathlib, subprocess, sys
import numpy as np
from rdkit import Chem
ROOT=pathlib.Path('/workspace/AToM_MLMM-m00-review-v3')
OUT=pathlib.Path(__file__).resolve().parent
F=ROOT/'fixtures/chemical_reference_v3'
OLD=ROOT/'fixtures/chemical_reference'
# Re-run inherited independently authored molecular checks on new records.
source=(ROOT/'Worker_Log/Milestone_00/evidence/M00_review_v2/structural_audit.py').read_text()
source=source.replace("ROOT=pathlib.Path('/workspace/AToM_MLMM-m00-review-v2')",'ROOT=pathlib.Path('+repr(str(ROOT))+')')
source=source.replace("F=ROOT/'fixtures/chemical_reference'","F=ROOT/'fixtures/chemical_reference_v3'")
source=source.replace("check('preparation script hash',sha(ROOT/'tools/prepare_neutral_references.py')==manifest['preparation_script_sha256'])", "check('repair script hash',sha(ROOT/'tools/repair_neutral_reference_controls.py')==manifest['repair_script_sha256'])")
source=source[:source.index('# Regenerate only in memory')]
exec(compile(source,'inherited_structural_checks','exec'),globals())
# Independently recompute steric distances, graph exclusions and rotations.
radii={'H':1.2,'C':1.7,'N':1.55,'O':1.52}
geometry=[]
def minpairs(p,l,le,ids=None):
    indices=list(range(len(p['atom_ids']))) if ids is None else [i for i,a in enumerate(p['atom_ids']) if a in ids]
    rr=np.asarray(p['positions_angstrom'])[indices];ll=np.asarray(l)
    d=np.linalg.norm(rr[:,None,:]-ll[None,:,:],axis=-1)
    rad=np.array([radii[p['elements'][i]] for i in indices])[:,None]+np.array([radii[e] for e in le])[None,:]
    k,j=np.unravel_index((d/rad).argmin(),d.shape)
    return {'min_distance_A':float(d.min()),'min_Bondi_ratio':float((d/rad).min()),'ratio_pair':[p['atom_ids'][indices[k]],int(j)]}
def internal(p):
    d=np.linalg.norm(np.asarray(p['positions_angstrom'])[:,None,:]-np.asarray(p['positions_angstrom'])[None,:,:],axis=-1)
    n=len(d);adj=np.zeros((n,n),dtype=int)
    for i,j,_ in p['bonds']:adj[i,j]=adj[j,i]=1
    eligible=(adj==0)&((adj@adj)==0)&~np.eye(n,dtype=bool)
    radi=np.array([radii[e] for e in p['elements']]);ratio=d/(radi[:,None]+radi[None,:])
    return float(np.min(ratio[eligible]))
def rotate(p,ids,angle):
    import copy
    q=copy.deepcopy(p);r=np.asarray(p['positions_angstrom']);a=r[p['atom_ids'].index('p5')];b=r[p['atom_ids'].index('p4')]
    axis=(b-a)/np.linalg.norm(b-a);v=r-a;t=np.deg2rad(angle)
    rotated=a+v*np.cos(t)+np.cross(axis,v)*np.sin(t)+np.outer(v@axis,axis)*(1-np.cos(t))
    mask=np.array([x not in ids for x in p['atom_ids']]);r=r.copy();r[mask]=rotated[mask];r[p['atom_ids'].index('p4')]=b
    q['positions_angstrom']=r.tolist();return q
raw_fields=('positions_angstrom','atomic_numbers','atom_ids','elements','bonds','formal_charge','multiplicity','cap','fragment_cap','fragment_transform','ligand_transform')
for name,s in sorted(structures.items()):
    old=json.loads((OLD/'structures'/(name+'.json')).read_text())
    check(name+':all G05 fields identical',all(s.get(k)==old.get(k) for k in raw_fields))
    if not name.startswith('ethanol'):
        check(name+':non-Thr entire bytes identical',(F/'structures'/(name+'.json')).read_bytes()==(OLD/'structures'/(name+'.json')).read_bytes())
    parent=s.get('parent') or s.get('g07_controls',{}).get('parent')
    if parent and name.startswith('ethanol'):
        oldp=old.get('parent') or old['g07_controls']['parent'];ids=s['atom_ids'][:-1] if 'fragment_count' not in s else s['g07_controls']['choices'][0]['protein_ml_ids']
        predicted=rotate(oldp,ids,120)
        check(name+':independent Rodrigues rotation',np.max(np.abs(np.array(parent['positions_angstrom'])-predicted['positions_angstrom']))<3e-14)
        check(name+':topology unchanged',all(parent[k]==v for k,v in oldp.items() if k!='positions_angstrom'))
        pr=np.array(parent['positions_angstrom']);op=np.array(oldp['positions_angstrom'])
        check(name+':bond lengths unchanged',max(abs(np.linalg.norm(pr[i]-pr[j])-np.linalg.norm(op[i]-op[j])) for i,j,_ in parent['bonds'])<1e-14)
        check(name+':internal nonbonded ratio',internal(parent)>=.65,internal(parent))
    if 'g07_controls' not in s:continue
    g=s['g07_controls'];p=g['parent'];n=s['fragment_count'];le=s['elements'][n:];lig=g['ligand_positions_angstrom']
    result={'name':name,'full_parent':minpairs(p,lig,le),'internal_nonbonded_ratio':internal(p),'choices':{}}
    for ch in g['choices']:
        retained=set(p['atom_ids'])-set(ch['protein_ml_ids'])
        item={'retained':minpairs(p,lig,le,retained)} if retained else {'retained':None}
        if 'exact_model_fragment' in ch:item['capped_fragment']=minpairs(ch['exact_model_fragment'],lig,le)
        result['choices'][ch['name']]=item
        if retained:check(name+':'+ch['name']+':retained ligand ratio >= .70',item['retained']['min_Bondi_ratio']>=.70,item['retained'])
    check(name+':full-parent nonbonded ratio >= .65',internal(p)>=.65,internal(p))
    if s['kind']=='separated':check(name+':full separation',result['full_parent']['min_distance_A']>=15)
    geometry.append(result)
attempts=[]
for angle in range(0,360,30):
    inter=[];intra=[]
    for name,s in structures.items():
        if not name.startswith('ethanol-') or 'g07_controls' not in s:continue
        old=json.loads((OLD/'structures'/(name+'.json')).read_text());g=old['g07_controls'];ids=g['choices'][0]['protein_ml_ids'];p=rotate(g['parent'],ids,angle)
        inter.append(minpairs(p,g['ligand_positions_angstrom'],old['elements'][old['fragment_count']:],set(p['atom_ids'])-set(ids))['min_Bondi_ratio']);intra.append(internal(p))
    attempts.append({'angle_degrees':angle,'worst_retained_ligand_ratio':min(inter),'worst_internal_nonbonded_ratio':min(intra),'eligible':min(intra)>=.65})
for got,want in zip(attempts,manifest['repair_attempts']):
    check('angle '+str(got['angle_degrees'])+':independent selection metric',got['eligible']==want['eligible'] and all(abs(got[k]-want[k])<2e-14 for k in ('worst_retained_ligand_ratio','worst_internal_nonbonded_ratio')))
selected=max((a for a in attempts if a['eligible']),key=lambda a:(a['worst_retained_ligand_ratio'],-a['angle_degrees']))
check('maximin selection = 120',selected['angle_degrees']==manifest['selected_angle']==120)
# Every actual monomer frame represented; coordinates, proper rotations and budgets.
controls=[json.loads(p.read_text()) for p in sorted((F/'quadrature_controls').glob('*.json'))]
frames={}
for name,s in structures.items():
    if 'fragment_count' not in s:continue
    n=s['fragment_count']
    for part,start,stop in [('fragment',0,n),('ligand',n,len(s['atom_ids']))]:
        q=np.array(s[part+'_transform']['rotation']);key=(s[part+'_baseline'],tuple(q.flat));positions=np.array(s['positions_angstrom'])[start:stop];positions=positions-positions[0]
        frames[key]=positions
check('ten distinct frames and controls',len(frames)==len(controls)==10)
for c in controls:
    q=np.array(c['rotation']);key=(c['baseline'],tuple(q.flat));b=structures[c['baseline']];r=np.array(b['positions_angstrom']);expected=(r-r[0])@q.T
    check(c['name']+':frame covered',key in frames and np.max(np.abs(frames[key]-c['positions_angstrom']))<1e-13)
    check(c['name']+':baseline rotated exactly',np.max(np.abs(expected-c['positions_angstrom']))<1e-13)
    check(c['name']+':atom order and state',c['atomic_numbers']==b['atomic_numbers'] and c['formal_charge']==0 and c['multiplicity']==1 and c['units']=='angstrom')
    check(c['name']+':fixed budgets',c['energy_difference_max_kcal_mol']==.02 and c['force_component_rms_difference_max_eV_angstrom']==.002 and c['force_atom_vector_difference_max_eV_angstrom']==.005)
# Regenerate repaired bundle only inside reviewer evidence and compare every byte.
sys.path.insert(0,str(ROOT/'tools'))
import repair_neutral_reference_controls as repair
repair.TARGET=OUT/'regenerated-r2'
with contextlib.redirect_stdout(io.StringIO()) as captured:repair.main()
for rel in ['input-manifest.json']+list(manifest['files']):check('regenerated exact bytes:'+rel,(F/rel).read_bytes()==(repair.TARGET/rel).read_bytes())
for name in ('reference-settings.json','reference-explicit.lock'):check(name+':unchanged v2',(F/name).read_bytes()==(OLD/name).read_bytes())
for script in ('prepare_neutral_references.py','repair_neutral_reference_controls.py'):
    tree=ast.parse((ROOT/'tools'/script).read_text());imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]+[a.name for node in ast.walk(tree) if isinstance(node,ast.Import) for a in node.names]
    check(script+':score-free imports',not any(any(x in (m or '').lower() for x in ['mace','psi4','torch','quantum','model']) for m in imports),imports)
result={'reviewed_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'reviewer':'/root/m00_reference_design_v3; gpt-6-astra/high fresh context per dispatch','python':sys.executable,'numpy':np.__version__,'total_checks':len(checks),'passed':sum(x['passed'] for x in checks),'failed':[x for x in checks if not x['passed']],'geometry':geometry,'independent_attempts':attempts,'checks':checks}
(OUT/'review-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','geometry','independent_attempts']},indent=2))
sys.exit(bool(result['failed']))
