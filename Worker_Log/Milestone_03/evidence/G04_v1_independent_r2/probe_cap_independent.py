"""Reviewer-authored numerical oracle. Reuse fixture construction only.

Expected cap pullback uses axial/transverse raw-force decomposition. No test or
production callback, map, mixer, FD helper, or cap oracle computes expectations.
All required h values, full force arrays and perturbed energies are retained.
"""
import copy,json,pathlib
from dataclasses import replace
import numpy as np
import openmm as mm
from openmm import unit
from tests.integration.test_link_geometry import case
from atm_mlmm.atm import physical_system,build_atm,AtmEvaluator
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.protocols.abfe import make_protocol
from atm_mlmm.schedule import linear_schedule
from atm_mlmm.schema import MobileGroup,RestraintSpec,RuntimeSpec
OUT=pathlib.Path(__file__).parent
H=(1e-3,1e-4,1e-5,1e-6)
SHIFT=np.array((.3,.1,-.2)); rows=[]; fd=[]; decomposition=[]

def oracle(x,ks):
 kc,kp,ke,kl=ks
 x=np.asarray(x); bond=x[1]-x[0]; length=np.linalg.norm(bond); direction=bond/length
 cap=x[0]+.117*direction
 energy=0.;force=np.zeros((13,3));raw=np.zeros(3)
 for point,k,partner in ((np.array((.13,-.08,.11)),kc,None),(x[8],kp,8),(x[5],ke,5)):
  delta=cap-point; energy+=k*float(delta@delta)/2; contribution=-k*delta;raw+=contribution
  if partner is not None:force[partner]-=contribution
 delta=x[8]-np.array((.02,.3,-.07));energy+=kl*float(delta@delta)/2;force[8]-=kl*delta
 transverse=raw-direction*float(direction@raw)
 force[1]+=(.117/length)*transverse;force[0]+=raw-(.117/length)*transverse
 return energy,force,cap,raw

def context(system,platform):
 integ=mm.VerletIntegrator(.0005);c=mm.Context(system,integ,mm.Platform.getPlatformByName(platform))
 c.setTime(.231);c.setVelocities(np.full((system.getNumParticles(),3),.007))
 return c,integ

def raw(c,x):
 positions=np.zeros((14,3));positions[:13]=x
 c.setPositions(positions);c.computeVirtualSites()
 s=c.getState(getEnergy=True,getForces=True,getPositions=True)
 return float(s.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),np.asarray(s.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer))[:13],np.asarray(s.getPositions(asNumpy=True).value_in_unit(unit.nanometer))

def sweep(label,energy,x,force,restore):
 samples=[]
 try:
  for h in H:
   estimate=np.empty((13,3)); energies=[]
   for atom in range(13):
    for axis in range(3):
     plus=x.copy();minus=x.copy();plus[atom,axis]+=h;minus[atom,axis]-=h
     ep=energy(plus);em=energy(minus);estimate[atom,axis]=-(ep-em)/(2*h)
     energies.append([atom,axis,ep,em])
   error=estimate-force
   samples.append(dict(h_nm=h,max_error=float(np.max(np.abs(error))),rms_error=float(np.sqrt(np.mean(error**2))),estimate=estimate.tolist(),energies=energies))
 finally:restore()
 row=dict(case=label,coordinates=x.tolist(),forces=force.tolist(),s06_rms_limit=float(1e-3+1e-4*np.sqrt(np.mean(force**2))),samples=samples)
 fd.append(row)
 assert samples[-1]['max_error']<1e-5,row
 assert samples[2]['rms_error']<=row['s06_rms_limit'],row
 assert samples[2]['max_error']<samples[0]['max_error'],row
 return row

configs={'cap':(7.,0.,0.,0.),'environment':(0.,0.,10.,0.),'invariant':(0.,4.,10.,0.),'mixed':(7.,4.,10.,5.)}
for name,ks in configs.items():
 bundle,snapshot=case(cap_k=ks[0],pair_k=ks[1],environment_k=ks[2],ligand_k=ks[3])
 base=np.asarray(snapshot.positions_nm)
 actual_system=physical_system(bundle)
 isolated=copy.deepcopy(actual_system)
 for i in reversed(range(isolated.getNumForces())):
  if not isinstance(isolated.getForce(i),mm.PythonForce):isolated.removeForce(i)
 assert isolated.getNumForces()==1
 for platform in ('Reference','CPU'):
  for nested in (False,True):
   system=copy.deepcopy(isolated)
   if nested:
    atm=mm.ATMForce('(1-lambda)*u0+lambda*u1');atm.addGlobalParameter('lambda',0.)
    for i in range(14):atm.addParticle(mm.Vec3(*SHIFT) if 8<=i<13 else mm.Vec3(0,0,0))
    atm.addForce(copy.deepcopy(system.getForce(0)));system.removeForce(0);system.addForce(atm)
   c,integ=context(system,platform)
   try:
    for lam in ((0.,.37,1.) if nested else (0.,)):
     if nested:c.setParameter('lambda',lam)
     for frame,x in [('original',base)]+([('rotated',base@np.array(((0,1,0),(-1,0,0),(0,0,1)))+(.3,.2,-.1))] if name=='invariant' and not nested else []):
      mapped=x.copy();mapped[8:13]+=SHIFT
      a,b=oracle(x,ks),oracle(mapped,ks)
      expected_e=(1-lam)*a[0]+lam*b[0];expected_f=(1-lam)*a[1]+lam*b[1]
      e,f,p=raw(c,x)
      row=dict(case=name,platform=platform,nested=nested,lambda_value=lam,frame=frame,energy=e,expected_energy=expected_e,force=f.tolist(),expected_force=expected_f.tolist(),max_force_error=float(np.max(np.abs(f-expected_f))),energy_error=abs(e-expected_e),cap_position=p[13].tolist(),expected_cap=a[2].tolist())
      rows.append(row)
      assert abs(e-expected_e)<=1e-8 and row['max_force_error']<=1e-7,row
      assert np.max(np.abs(p[13]-a[2]))<1e-12
      if name=='invariant' and not nested:
       row['net_force']=f.sum(axis=0).tolist();row['net_torque']=np.cross(x,f).sum(axis=0).tolist()
       assert np.max(np.abs(row['net_force']))<1e-7 and np.max(np.abs(row['net_torque']))<1e-7
      if platform=='Reference':
       saved=c.getState(getPositions=True,getVelocities=True,getParameters=True)
       sweep(f'{name}-{nested}-{lam}-{frame}',lambda y:raw(c,y)[0],x,expected_f,lambda:c.setState(saved))
       after=c.getState(getPositions=True,getVelocities=True,getParameters=True)
       assert mm.XmlSerializer.serialize(saved)==mm.XmlSerializer.serialize(after)
   finally:del c,integ
# Full retained-MM plus analytic model, production-native ATM; manual endpoint
# maps and analytic model oracle are independent of production geometry helpers.
bundle,snapshot=case(pair_k=4.,environment_k=10.);x=np.asarray(snapshot.positions_nm)
protocol=make_protocol((MobileGroup('mobile',tuple(snapshot.real_atom_ids[8:13]),('ligand',),'ligand'),),tuple(SHIFT))
schedule=linear_schedule((('initial',0.),('middle',.37),('final',1.)))
restraint=RestraintSpec('outside',('l8',),3.,(.2,.4,.1))
atm_bundle=build_atm(bundle,resolve_protocol(bundle,protocol),schedule,restraint)
retained=mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
rc,ri=context(retained,'Reference')
runtime=RuntimeSpec('Reference','double',(),.0005,300.,'NVT','Verlet')
try:
 with AtmEvaluator(atm_bundle,runtime) as ev:
  for state,lam in (('initial',0.),('middle',.37),('final',1.)):
   x1=x.copy();x1[8:13]+=SHIFT
   e0,f0,_=raw(rc,x);e1,f1,_=raw(rc,x1)
   a,b=oracle(x,configs['mixed']),oracle(x1,configs['mixed'])
   d=x[8]-np.array((.2,.4,.1));outside=np.zeros((13,3));outside[8]=-3*d
   expected_e=(1-lam)*(e0+a[0])+lam*(e1+b[0])+1.5*float(d@d)
   expected_f=(1-lam)*(f0+a[1])+lam*(f1+b[1])+outside
   actual=ev.evaluate(snapshot,state)
   row=dict(case='full-'+state,energy_error=abs(actual.total.energy_kj_mol-expected_e),max_force_error=float(np.max(np.abs(np.asarray(actual.total.forces_kj_mol_nm)-expected_f))),expected_force=expected_f.tolist(),actual_force=actual.total.forces_kj_mol_nm)
   rows.append(row);assert row['energy_error']<=1e-4 and row['max_force_error']<=5e-3,row
   saved=ev.context.getState(getPositions=True,getVelocities=True,getParameters=True)
   sweep('full-'+state,lambda y:ev.evaluate(replace(snapshot,positions_nm=y),state).total.energy_kj_mol,x,np.asarray(actual.total.forces_kj_mol_nm),lambda:ev.context.setState(saved))
finally:del rc,ri
# Attribute truncation to actual retained force classes; do not assume LJ.
for index in range(retained.getNumForces()):
 system=copy.deepcopy(retained);kind=type(system.getForce(index)).__name__
 for j in reversed(range(system.getNumForces())):
  if j!=index:system.removeForce(j)
 c,integ=context(system,'Reference')
 try:
  _,f,_=raw(c,x);saved=c.getState(getPositions=True,getVelocities=True,getParameters=True)
  result=sweep('retained-'+kind,lambda y:raw(c,y)[0],x,f,lambda:c.setState(saved))
  decomposition.append({'force_index':index,'class':kind,'max_errors':[s['max_error'] for s in result['samples']]})
 finally:del c,integ
report=dict(oracle='reviewer-authored axial/transverse S04 pullback, explicit real ligand indices 8:13 and independently written Cartesian central differences',rows=rows,fd=fd,decomposition=decomposition,summary={'comparisons':len(rows),'fd_sweeps':len(fd),'max_energy_error':max(r['energy_error'] for r in rows),'max_force_error':max(r['max_force_error'] for r in rows),'max_final_fd_error':max(r['samples'][-1]['max_error'] for r in fd)})
with (OUT/'cap-independent-results.json').open('x') as f:json.dump(report,f,indent=2,allow_nan=False)
print(json.dumps(report['summary']));print(json.dumps(decomposition))
