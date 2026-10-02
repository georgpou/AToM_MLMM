"""Independent read-only audit of frozen chemistry, geometry and preparation."""
import collections, contextlib, hashlib, importlib.util, io, json, math, pathlib, subprocess, sys
import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import rdMolDescriptors, rdMolTransforms
ROOT=pathlib.Path('/workspace/AToM_MLMM-m00-review-v2')
F=ROOT/'fixtures/chemical_reference'
checks=[]
rows=[]
def check(label, okay, details=None):
    checks.append({'check':label,'passed':bool(okay),'details':details})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((F/'input-manifest.json').read_text())
for name,digest in manifest['files'].items():check('hash:'+name,sha(F/name)==digest)
check('preparation script hash',sha(ROOT/'tools/prepare_neutral_references.py')==manifest['preparation_script_sha256'])
structures={p.stem:json.loads(p.read_text()) for p in (F/'structures').glob('*.json')}
check('34 structures',len(structures)==34)
expected={'ethanol':'C2H6O','butane':'C4H10','methanol':'CH4O','acetamide':'C2H5NO'}
def mol(record):
    rw=Chem.RWMol()
    for z in record['atomic_numbers']:rw.AddAtom(Chem.Atom(z))
    for i,j,o in record['bonds']:rw.AddBond(i,j,{1:Chem.BondType.SINGLE,2:Chem.BondType.DOUBLE}[o])
    m=rw.GetMol();Chem.SanitizeMol(m)
    c=Chem.Conformer(m.GetNumAtoms())
    for i,xyz in enumerate(record['positions_angstrom']):c.SetAtomPosition(i,xyz)
    m.AddConformer(c);Chem.AssignAtomChiralTagsFromStructure(m,replaceExistingTags=True)
    Chem.AssignStereochemistry(m,cleanIt=True,force=True)
    return m
parents={}
def inspect_mol(s,label,formula=None):
    m=mol(s);f=rdMolDescriptors.CalcMolFormula(m)
    check(label+':formula',formula is None or f==formula,f)
    check(label+':explicit saturated valence',all(a.GetNumImplicitHs()==0 for a in m.GetAtoms()))
    check(label+':neutral singlet',Chem.GetFormalCharge(m)==0 and s['formal_charge']==0 and s['multiplicity']==1 and sum(s['atomic_numbers'])%2==0)
    check(label+':unique ids',len(set(s['atom_ids']))==len(s['atom_ids']))
    check(label+':atom array order',len(s['atom_ids'])==len(s['positions_angstrom'])==len(s['elements'])==len(s['atomic_numbers']) and all(Chem.GetPeriodicTable().GetElementSymbol(z)==e for z,e in zip(s['atomic_numbers'],s['elements'])))
    r=np.array(s['positions_angstrom']);check(label+':finite angstrom',s['units']=='angstrom' and np.isfinite(r).all())
    if 'stereocenters' in s:
        cip=[list(x) for x in Chem.FindMolChiralCenters(m,includeUnassigned=True)]
        check(label+':3D vs declared chirality',cip==s['stereocenters'],cip)
    return m

def cap_check(s,label):
    parent=s['parent'];cap=s['cap'];p=np.array(parent['positions_angstrom']);r=np.array(s['positions_angstrom'])
    a=parent['atom_ids'].index(cap['ml_parent_id']);b=parent['atom_ids'].index(cap['mm_parent_id']);sel=cap['real_source_indices']
    h=p[a]+cap['distance_angstrom']*(p[b]-p[a])/np.linalg.norm(p[b]-p[a])
    check(label+':derived cap',np.max(np.abs(r[-1]-h))<2e-14 and cap['raw_index']==len(r)-1)
    check(label+':retained exact real identity',np.array_equal(r[:-1],p[sel]) and s['atom_ids'][:-1]==[parent['atom_ids'][i] for i in sel])
    check(label+':cap convention',cap['distance_angstrom']==1.09 and cap['mass_da']==cap['classical_charge']==cap['classical_lj_epsilon']==0)
    return parent

for name,s in sorted(structures.items()):
    if 'fragment_count' not in s:
        m=inspect_mol(s,name,expected[s['family']])
        if s['cap']:
            parent=cap_check(s,name);pm=inspect_mol(parent,name+':parent',{'ethanol':'C7H14N2O3','butane':'C9H18N2O2'}[s['family']])
            parents[s['family']]=parent
            observed=rdMolTransforms.GetDihedralDeg(pm.GetConformer(),*s['torsion_parent_indices'])
            check(name+':torsion',abs((observed-s['torsion_degrees']+180)%360-180)<1e-10,observed)
        continue
    rf=np.array(structures[s['fragment_baseline']]['positions_angstrom']);rl=np.array(structures[s['ligand_baseline']]['positions_angstrom']);r=np.array(s['positions_angstrom']);n=s['fragment_count']
    transforms=[s['fragment_transform'],s['ligand_transform']]
    for label,orig,target,t in [('fragment',rf,r[:n],transforms[0]),('ligand',rl,r[n:],transforms[1])]:
        q=np.array(t['rotation']);trans=np.array(t.get('translation_angstrom',[0,0,0]));out=(orig-np.array(t['source_anchor_angstrom']))@q.T+trans
        check(name+':exact '+label+' rigid transform',np.max(np.abs(out-target))<1e-14)
        check(name+':proper '+label+' rotation',np.max(np.abs(q@q.T-np.eye(3)))<1e-14 and abs(np.linalg.det(q)-1)<1e-14)
    check(name+':identities',s['atom_ids']==['f:'+x for x in structures[s['fragment_baseline']]['atom_ids']]+['l:'+x for x in structures[s['ligand_baseline']]['atom_ids']])
    check(name+':neutral singlet',s['formal_charge']==0 and s['multiplicity']==1)
    d=np.linalg.norm(r[:n,None,:]-r[None,n:,:],axis=2)
    check(name+':min distance',abs(d.min()-s['minimum_intercomponent_distance_angstrom'])<1e-14)
    check(name+':anchor distance',abs(np.linalg.norm(r[s['anchor_indices'][0]]-r[s['anchor_indices'][1]])-s['anchor_distance_angstrom'])<1e-14)
    g=s['g07_controls'];p=g['parent'];pm=inspect_mol(p,name+':g07-parent', 'C7H14N2O3' if name.startswith('ethanol') else 'C9H18N2O2');pr=np.array(p['positions_angstrom'])
    full_d=np.linalg.norm(pr[:,None,:]-r[None,n:,:],axis=2)
    a=p['atom_ids'].index(s['fragment_cap']['ml_parent_id']);b=p['atom_ids'].index(s['fragment_cap']['mm_parent_id']);h=pr[a]+1.09*(pr[b]-pr[a])/np.linalg.norm(pr[b]-pr[a])
    check(name+':transformed parent cap',np.max(np.abs(h-r[n-1]))<2e-14)
    check(name+':same complete g07 ligand',np.array_equal(g['ligand_positions_angstrom'],r[n:]))
    choices={x['name']:x for x in g['choices']}
    check(name+':all g07 choices',set(choices)==({'baseline','uncut'} if name.startswith('ethanol') else {'baseline','uncut','alternative-ethane'}))
    check(name+':uncut identities',choices['uncut']['protein_ml_ids']==p['atom_ids'])
    if 'alternative-ethane' in choices:
        alt=choices['alternative-ethane']['exact_model_fragment'];inspect_mol(alt,name+':alternative','C2H6');cap_check(alt,name+':alternative')
    if s['kind']=='separated':check(name+':15A both full and capped separation',d.min()>=15 and full_d.min()>=15)
    ii,jj=np.unravel_index(full_d.argmin(),full_d.shape)
    rows.append({'name':name,'capped_min_A':float(d.min()),'full_parent_min_A':float(full_d.min()),'full_parent_closest_pair':[p['atom_ids'][ii],s['atom_ids'][n+jj]],'choices':list(choices)})
# Regenerate only in memory, intercept every writer, disallow pycache.
spec=importlib.util.spec_from_file_location('reference_preparation',ROOT/'tools/prepare_neutral_references.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
generated={};module.write=lambda name,data: generated.setdefault(name,data)
with contextlib.redirect_stdout(io.StringIO()):module.main()
for name,s in structures.items():
    blob=(json.dumps(generated['structures/'+name+'.json'],indent=2,allow_nan=False)+'\n').encode()
    check(name+':regeneration exact bytes',hashlib.sha256(blob).hexdigest()==manifest['files']['structures/'+name+'.json'])
# Recorded source digests and checkpoint are read as bytes, never imported.
prov=ROOT/'Worker_Log/Milestone_00/evidence/M00_reference_v2/provenance'
for record in json.loads((prov/'manifest.json').read_text()):
    if 'sha256' in record:check('provenance:'+record['path'],sha(prov/record['path'])==record['sha256'])
model=ROOT/'models/mace-off23-small';mm=json.loads((model/'manifest.json').read_text())
for path,record in mm['files'].items():check('model asset:'+path,sha(model/path)==record['sha256'])
result={'reviewed_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':sys.executable,'rdkit':rdBase.rdkitVersion,'numpy':np.__version__,'total_checks':len(checks),'passed':sum(x['passed'] for x in checks),'failed':[x for x in checks if not x['passed']],'contacts':rows,'checks':checks}
print(json.dumps(result,indent=2))
