"""Capture G04 worker numerics, identifying the independent test oracle used."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from tests.link_oracle import cap_answer, REFERENCE
from tests.integration.test_link_geometry import case,model_result
from atm_mlmm.atm import PhysicalEvaluator,AtmEvaluator,build_atm
from atm_mlmm.derivatives import finite_difference_forces
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.protocols.abfe import make_protocol
from atm_mlmm.schema import MobileGroup,RestraintSpec
from atm_mlmm.schedule import linear_schedule

HERE=Path(__file__).resolve().parent
rows=[]
for platform in ('Reference','CPU'):
    for label,options in (
        ('cap',dict(cap_k=7.,ligand_k=0.)),
        ('environment',dict(cap_k=0.,environment_k=10.,ligand_k=0.)),
        ('balance',dict(cap_k=0.,environment_k=10.,pair_k=4.,ligand_k=0.))):
        b,s=case(**options)
        expected=cap_answer(s.positions_nm,**options)
        actual=model_result(b,s,platform)
        errors=[]
        for step in (1e-3,1e-4,1e-5,1e-6):
            fd=finite_difference_forces(lambda s:model_result(b,s,platform)[0],s,step)
            errors.append(dict(step_nm=step,max_component_error=float(np.max(np.abs(fd-expected[1]))),
                               rms_error=float(np.sqrt(np.mean((fd-expected[1])**2)))))
        row=dict(case=label,platform=platform,energy_error=abs(actual[0]-expected[0]),
                 force_error=float(np.max(np.abs(actual[1]-expected[1]))),
                 cap_distance_nm=b.links[0].distance_nm,parent_forces=actual[1][:2].tolist(),
                 environment_force=actual[1][5].tolist(),fd=errors)
        if label=='balance':
            row['net_force']=actual[1].sum(axis=0).tolist()
            row['net_torque']=np.cross(np.asarray(s.positions_nm),actual[1]).sum(axis=0).tolist()
        assert row['energy_error']<=1e-8 and row['force_error']<=1e-7
        assert errors[-1]['max_component_error']<=1e-5
        rows.append(row)
b,s=case(pair_k=4.,environment_k=10.)
protocol=make_protocol((MobileGroup('mobile',tuple(s.real_atom_ids[8:]),('ligand',),'ligand'),),(.3,.1,-.2))
t=resolve_protocol(b,protocol)
schedule=linear_schedule((('initial',0.),('middle',.37),('final',1.)))
r=RestraintSpec('outside',('l8',),3.,(.2,.4,.1))
with AtmEvaluator(build_atm(b,t,schedule,r),REFERENCE) as e:
    for name in ('initial','middle','final'):
        answer=np.asarray(e.evaluate(s,name).total.forces_kj_mol_nm)
        errors=[]
        for step in (1e-3,1e-4,1e-5,1e-6):
            fd=finite_difference_forces(lambda s:e.evaluate(s,name).total.energy_kj_mol,s,step)
            errors.append(dict(step_nm=step,max_component_error=float(np.max(np.abs(fd-answer))),
                               rms_error=float(np.sqrt(np.mean((fd-answer)**2)))))
        assert errors[-1]['max_component_error']<=1e-5
        rows.append(dict(case='full-atm-'+name,platform='Reference',fd=errors))
result=dict(oracle='tests/link_oracle.py hand-derived S04 cap/Jacobian; no production callback/map/mixer oracle',
            numerical_limits=dict(analytic_energy=1e-8,analytic_force=1e-7,atm_energy=1e-4,atm_force=5e-3,final_fd_component=1e-5),cases=rows)
with (HERE/'g04-numerical-results.json').open('x') as out:json.dump(result,out,indent=2)
print(json.dumps(result,indent=2))
