"""Quantum-only methane feasibility under frozen settings; no target molecules or model."""
import hashlib, json, os, pathlib, socket, sys, time
ROOT=pathlib.Path('/workspace/AToM_MLMM-m00-review-v2')
OUT=pathlib.Path('/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2')
def deny(*a,**k):raise RuntimeError('independent audit is offline')
socket.socket.connect=deny;socket.create_connection=deny;socket.getaddrinfo=deny
import numpy as np
import psi4
ref=json.loads((ROOT/'fixtures/chemical_reference/reference-settings.json').read_text())
psi4.set_num_threads(2);psi4.set_memory('5 GiB');psi4.core.IOManager.shared_object().set_default_path(str(OUT));psi4.set_output_file(str(OUT/'independent-methane.dat'),False)
psi4.set_options(ref['settings'])
checks=[]
def check(k,v,d=None):checks.append({'check':k,'passed':bool(v),'details':d})
# Inspect actual package metadata, not only the worker's report.
actual={x['name']:x for p in pathlib.Path(sys.prefix,'conda-meta').glob('*.json') for x in [json.loads(p.read_text())]}
records=json.loads((ROOT/'Worker_Log/Milestone_00/evidence/M00_reference_v2/working-libxc-7.0.0/installed-packages.json').read_text())
lock=[x.strip() for x in (ROOT/'fixtures/chemical_reference/reference-explicit.lock').read_text().splitlines() if x.startswith('https://')]
check('105 packages',len(lock)==len(records)==len(actual)==105,[len(lock),len(records),len(actual)])
for r in records:
    a=actual[r['name']]
    check('installed '+r['name'], all(a.get(k)==r[k] for k in ['name','version','build','sha256']) and r['url']+'#'+r['sha256'] in lock)
for f,digest in ref['basis_file_sha256'].items():check('basis hash '+f,hashlib.sha256(pathlib.Path(psi4.core.get_datadir(),'basis',f).read_bytes()).hexdigest()==digest)
check('versions',psi4.__version__=='1.10.2' and actual['libxc-c']['version']=='7.0.0' and actual['dftd3-python']['version']=='1.6.0')
x=1.09/np.sqrt(3);coords=np.array([[0,0,0],[x,x,x],[x,-x,-x],[-x,x,-x],[-x,-x,x]])
def molecule(r):
    return psi4.geometry('\n'.join(['0 1']+[z+' '+' '.join(format(v,'.17g') for v in xyz) for z,xyz in zip(['C','H','H','H','H'],r)]+ref['molecular_options']))
t=time.monotonic();g,w=psi4.gradient(ref['method'],molecule=molecule(coords),return_wfn=True);grad=np.asarray(g).copy();energy=float(w.energy());vs={k:float(v) for k,v in psi4.core.variables().items() if isinstance(v,(int,float)) and ('ENERGY' in k or 'DISPERSION' in k)}
force=-grad*ref['hartree_to_kJ_mol']/ref['bohr_to_nm'];fds=[]
for h in [1e-3,1e-4]:
    p=coords.copy();m=coords.copy();p[1,0]+=h;m[1,0]-=h
    ep=psi4.energy(ref['method'],molecule=molecule(p));em=psi4.energy(ref['method'],molecule=molecule(m));fd=-(ep-em)*ref['hartree_to_kJ_mol']/(2*h*.1)
    fds.append({'h_angstrom':h,'fd_kJ_mol_nm':fd,'analytic_kJ_mol_nm':float(force[1,0]),'absolute_error_kJ_mol_nm':abs(fd-force[1,0])})
check('finite methane energy and gradient',np.isfinite(energy) and np.isfinite(grad).all())
check('D3 and no VV10',vs['DISPERSION CORRECTION ENERGY']!=0 and vs['DFT VV10 ENERGY']==0)
check('energy includes D3',abs(energy-vs['DFT FUNCTIONAL TOTAL ENERGY']-vs['DISPERSION CORRECTION ENERGY'])<1e-12)
check('FD is beneath convergence force budget',max(x['absolute_error_kJ_mol_nm'] for x in fds)<0.002*964.8533288249877)
r={'scope':'independent quantum-only methane; frozen settings including wcombine=false; no target comparisons','python':sys.executable,'psi4_version':psi4.__version__,'network_denied':True,'wall_seconds':time.monotonic()-t,'settings':ref['settings'],'energy_hartree':energy,'gradient_hartree_bohr':grad.tolist(),'variables':vs,'finite_differences':fds,'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),'failed':[c for c in checks if not c['passed']]}
(OUT/'quantum-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['checks','gradient_hartree_bohr']},indent=2));psi4.core.clean()
