"""Independent offline reload and mapped parent/environment FD using saved oracle."""
import hashlib,json,os,pathlib,subprocess,sys
OUT=pathlib.Path(__file__).resolve().parent
if len(sys.argv)==1:
 from tests.integration.test_link_geometry import case
 from atm_mlmm.atm import build_atm,save_bundle
 from atm_mlmm.geometry import resolve_protocol
 from atm_mlmm.protocols.abfe import make_protocol
 from atm_mlmm.schedule import linear_schedule
 from atm_mlmm.schema import MobileGroup,RestraintSpec
 b,s=case(pair_k=4.,environment_k=10.)
 protocol=make_protocol((MobileGroup('mobile',tuple(s.real_atom_ids[8:]),('ligand',),'ligand'),),(.3,.1,-.2))
 a=build_atm(b,resolve_protocol(b,protocol),linear_schedule((('initial',0.),('middle',.37),('final',1.))),RestraintSpec('outside',('l8',),3.,(.2,.4,.1)))
 artifact=OUT/'trusted-cap-artifact.json';assert not artifact.exists();digest=save_bundle(artifact,a)
 cache=OUT/'cap-empty-cache';cache.mkdir();assert not list(cache.iterdir())
 env=dict(os.environ,XDG_CACHE_HOME=str(cache))
 command=[sys.executable,str(pathlib.Path(__file__).resolve()),str(artifact),digest]
 result=subprocess.run(command,env=env,text=True,capture_output=True)
 with (OUT/'offline-cap-child.json').open('x') as f:json.dump(dict(argv=command,cwd=str(pathlib.Path.cwd()),cache=str(cache),sha256=digest,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr),f,indent=2)
 print(result.stdout);print(result.stderr);sys.exit(result.returncode)
import socket
def deny(*args,**kwargs):raise AssertionError('network and DNS forbidden')
socket.socket.connect=deny;socket.socket.connect_ex=deny;socket.create_connection=deny;socket.getaddrinfo=deny
assert not list(pathlib.Path(os.environ['XDG_CACHE_HOME']).iterdir())
from dataclasses import replace
import numpy as np
import openmm as mm
from openmm import unit
from atm_mlmm.atm import load_bundle,AtmEvaluator
from atm_mlmm.schema import RuntimeSpec,Snapshot,IdentityError,UnsupportedCapability
artifact,digest=sys.argv[1:]
for trusted,wanted,exc in ((False,digest,UnsupportedCapability),(True,'0'*64,IdentityError)):
 try:load_bundle(artifact,wanted,trusted=trusted)
 except exc:pass
 else:raise AssertionError('trust/digest guard absent')
b=load_bundle(artifact,digest,trusted=True)
reference=json.loads((OUT/'cap-independent-results.json').read_text())
expected={r['case'].removeprefix('full-'):r for r in reference['rows'] if r['case'].startswith('full-')}
x=np.asarray(next(r for r in reference['fd'] if r['case']=='full-initial')['coordinates'])
s=Snapshot(tuple(a.atom_id for a in b.physical.topology.atoms),x,None)
results=[];runtime=RuntimeSpec('Reference','double',(),.0005,300.,'NVT','Verlet')
with AtmEvaluator(b,runtime) as ev:
 ev.context.setTime(.583);ev.context.setVelocities(np.full((14,3),.009))
 for name in ('initial','middle','final'):
  actual=ev.evaluate(s,name);f=np.asarray(actual.total.forces_kj_mol_nm)
  assert np.max(np.abs(f-expected[name]['expected_force']))<=5e-3
  positions=ev.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
  cap=x[0]+.117*(x[1]-x[0])/np.linalg.norm(x[1]-x[0]);assert np.max(np.abs(positions[13]-cap))<=1e-12
  saved=ev.context.getState(getPositions=True,getVelocities=True,getParameters=True)
  samples=[]
  try:
   for h in (1e-3,1e-4,1e-5,1e-6):
    estimates=[];values=[]
    for atom in (0,1,5):
     for axis in range(3):
      p=x.copy();m=x.copy();p[atom,axis]+=h;m[atom,axis]-=h
      ep=ev.evaluate(replace(s,positions_nm=p),name).total.energy_kj_mol
      em=ev.evaluate(replace(s,positions_nm=m),name).total.energy_kj_mol
      estimates.append(-(ep-em)/(2*h));values.append([atom,axis,ep,em])
    error=np.asarray(estimates)-f[[0,1,5]].ravel()
    samples.append(dict(h=h,max_error=float(np.max(np.abs(error))),values=values,estimates=estimates))
  finally:ev.context.setState(saved)
  assert mm.XmlSerializer.serialize(saved)==mm.XmlSerializer.serialize(ev.context.getState(getPositions=True,getVelocities=True,getParameters=True))
  assert samples[-1]['max_error']<1e-5
  results.append(dict(state=name,actual_forces=f.tolist(),cap_position=positions[13].tolist(),samples=samples))
 first=ev.evaluate(s,'initial');ev.evaluate(replace(s,positions_nm=x+.023),'final');assert ev.evaluate(s,'initial')==first
with (OUT/'offline-cap-results.json').open('x') as f:json.dump(results,f,indent=2,allow_nan=False)
print('Trusted fresh process: guards, empty cache, denied sockets/DNS, all states, both parents/MM environment FD, complete state restoration and A-B-A pass')
print('Final parent/environment FD errors:',[r['samples'][-1]['max_error'] for r in results])
