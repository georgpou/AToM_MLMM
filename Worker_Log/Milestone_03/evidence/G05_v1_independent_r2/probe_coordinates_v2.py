"""Reviewer-only software probe. No target quantum/model-reference chemistry."""
import json,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
import openmm as mm
from openmm import app,unit
sys.path.insert(0,str(Path.cwd()))
from atm_mlmm.schema import IdentityError
from atm_mlmm.atm import PhysicalEvaluator,physical_system
from atm_mlmm.model_reference import NativeMACE
from atm_mlmm.models.mace import EV_TO_KJ_MOL,EV_A_TO_KJ_MOL_NM
from tests.integration.test_model_adapter import real_case
from tests.link_oracle import REFERENCE,input_case
from tests.link_permutation import plain_result,permute_info
from atm_mlmm.embeddings.mechanical import seal_boundary_result,openmm_topology
from atm_mlmm.partition import resolve_partition
import ase.units
OUT=Path(__file__).parent
bundle,snapshot=real_case();native=NativeMACE();ids=tuple(a.atom_id for a in bundle.topology.atoms)
retained=mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
checks=[];records=[]
def check(name,ok,**detail):
 checks.append(dict(name=name,passed=bool(ok),**detail))
 if not ok:print('FAILED',name,detail,flush=True)
check('measured-ASE-energy-factor',abs(1/(ase.units.kJ/ase.units.mol)-EV_TO_KJ_MOL)<1e-13,actual=1/(ase.units.kJ/ase.units.mol))
check('measured-ASE-force-factor',abs(10/(ase.units.kJ/ase.units.mol)-EV_A_TO_KJ_MOL_NM)<1e-12,actual=10/(ase.units.kJ/ase.units.mol))

def oracle(r):
 # Direct identity lookup and cap formula, without production geometry or test cap helpers.
 link=bundle.links[0];a=ids.index(link.ml_parent_id);b=ids.index(link.mm_parent_id)
 v=r[b]-r[a];length=np.linalg.norm(v);n=v/length
 cap=r[a]+link.distance_nm*n
 elements={a.atom_id:a.element for a in bundle.topology.atoms};z={'H':1,'C':6,'N':7,'O':8}
 x=np.array([cap if k==link.cap_id else r[ids.index(k)] for k in bundle.model_input_ids])
 numbers=[1 if k==link.cap_id else z[elements[k]] for k in bundle.model_input_ids]
 raw=native.evaluate(numbers,x);f=np.zeros_like(r)
 B=link.distance_nm/length*(np.eye(3)-np.outer(n,n))
 for k,force in zip(bundle.model_input_ids,np.asarray(raw['forces_kj_mol_nm'])):
  if k==link.cap_id:f[a]+=(np.eye(3)-B).T@force;f[b]+=B.T@force
  else:f[ids.index(k)]+=force
 e_mm,f_mm=plain_result(retained,r)
 return raw['energy_kj_mol']+e_mm,f+f_mm,dict(raw=raw,projected_ml_forces=f.tolist(),retained_energy=e_mm,retained_forces=f_mm.tolist())

axis=np.array([1.,2.,-3.]);axis/=np.linalg.norm(axis);theta=.913
K=np.array([[0.,-axis[2],axis[1]],[axis[2],0.,-axis[0]],[-axis[1],axis[0],0.]])
Q=np.eye(3)+np.sin(theta)*K+(1-np.cos(theta))*(K@K)
r=np.array(snapshot.positions_nm);counter=r.copy();counter[8:]+=(.3,.1,-.2)
frames=[('baseline',r),('general-rotation-translation',r@Q.T+[.217,-.531,.093]),('counterfactual',counter)]
with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
 for name,positions in frames:
  s=replace(snapshot,positions_nm=positions);e,f,details=oracle(positions);actual=evaluator.evaluate(s)
  check(name+'-energy',abs(actual.energy_kj_mol-e)<=1e-4,error=abs(actual.energy_kj_mol-e))
  check(name+'-all-real-forces',np.max(np.abs(np.array(actual.forces_kj_mol_nm)-f))<=5e-3,max_error=float(np.max(np.abs(np.array(actual.forces_kj_mol_nm)-f))))
  check(name+'-net-force',np.linalg.norm(np.sum(f,axis=0))<=5e-3,norm=float(np.linalg.norm(np.sum(f,axis=0))))
  check(name+'-net-torque',np.linalg.norm(np.sum(np.cross(positions,f),axis=0))<=5e-3,norm=float(np.linalg.norm(np.sum(np.cross(positions,f),axis=0))))
  order=np.array([12,2,10,0,4,7,1,8,3,9,5,11,6])
  try:
   evaluator.evaluate(replace(s,real_atom_ids=tuple(ids[i] for i in order),positions_nm=positions[order]))
   rejected=False
  except IdentityError:
   rejected=True
  check(name+'-reject-snapshot-order-inconsistent-with-topology',rejected)
  fd=[]
  # All 39 real components, both parents and all retained-MM coordinates.
  for i in range(len(ids)):
   for a in range(3):
    estimates=[]
    for h in (1e-3,1e-4,1e-5,1e-6):
     ep=[]
     for sign in (1,-1):
      displaced=positions.copy();displaced[i,a]+=sign*h
      ep.append(evaluator.evaluate(replace(s,positions_nm=displaced)).energy_kj_mol)
     estimates.append(-(ep[0]-ep[1])/(2*h))
    errors=np.abs(np.array(estimates)-f[i,a]);limit=1e-3+1e-4*abs(f[i,a])
    check(name+'-fd-'+ids[i]+'-'+str(a),errors[-1]<=limit and errors[-1]<=errors[0]+1e-5,errors=errors.tolist(),limit=limit)
    fd.append(dict(atom=ids[i],axis=a,steps_nm=[1e-3,1e-4,1e-5,1e-6],estimates=estimates,reference=f[i,a],errors=errors.tolist()))
  records.append(dict(name=name,positions_nm=positions.tolist(),oracle=details,expected_energy=e,expected_forces=f.tolist(),actual_energy=actual.energy_kj_mol,actual_forces=actual.forces_kj_mol_nm,fd=fd))
base,rot=records[:2]
check('full-total-rotation-energy',abs(base['actual_energy']-rot['actual_energy'])<=1e-4)
check('full-total-rotation-forces',np.max(np.abs(np.asarray(base['actual_forces'])@Q.T-np.asarray(rot['actual_forces'])))<=5e-3)
# Full physical force check with nonidentity final particle layout.
original,spec,_=input_case();top=openmm_topology(original.topology)
top.addAtom('cap',app.Element.getBySymbol('H'),top.addResidue('cap',top.addChain()))
order=(9,4,1,12,8,0,11,3,7,2,13,6,10,5)
info=permute_info(dict(system=physical_system(bundle),topology=top,oldToNew=list(range(13))),order)
remapped=seal_boundary_result(original,resolve_partition(original.topology,spec),info,manifest={'fixture_kind':'pinned_mace_candidate'})
with PhysicalEvaluator(remapped,REFERENCE) as evaluator:actual=evaluator.evaluate(snapshot)
check('nonidentity-full-energy',abs(actual.energy_kj_mol-base['expected_energy'])<=1e-4)
check('nonidentity-full-forces',np.max(np.abs(np.asarray(actual.forces_kj_mol_nm)-base['expected_forces']))<=5e-3)
result={'scope':'software only; inherited CH4/one-cut fixture, no chemical target calculations','checks':checks,'rotation':Q.tolist(),'records':records,'nonidentity':{'real_to_final':dict(remapped.real_to_final),'energy':actual.energy_kj_mol,'forces':actual.forces_kj_mol_nm}}
with (OUT/'coordinate-results.json').open('x') as out:json.dump(result,out,indent=2,allow_nan=False)
print(sum(c['passed'] for c in checks),'/',len(checks),'checks passed')
sys.exit(0 if all(c['passed'] for c in checks) else 1)
