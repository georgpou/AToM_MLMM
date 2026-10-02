"""Measure native nested-site behavior before any production repair."""
import copy
import json
import sys
import numpy as np
import openmm as mm
from openmm import unit
from tests.link_oracle import upstream_info, DATA, cap_answer

info=upstream_info()
direct=info['system']
for i in reversed(range(direct.getNumForces())):
    if direct.getForce(i).getName()!='diagnostic:raw-cap':
        direct.removeForce(i)
_,expected,h,_=cap_answer(DATA['positions_nm'],ligand_k=0.)
result={}
for platform in ('Reference','CPU'):
    for nested in (False,True):
        system=copy.deepcopy(direct)
        if nested:
            force=mm.ATMForce('u0')
            for i in range(system.getNumParticles()):
                force.addParticle(mm.Vec3(0,0,0))
            force.addForce(copy.deepcopy(system.getForce(0)))
            system.removeForce(0)
            system.addForce(force)
        integrator=mm.VerletIntegrator(.0005)
        context=mm.Context(system,integrator,mm.Platform.getPlatformByName(platform))
        context.setPositions([*DATA['positions_nm'],[99.,88.,77.]])
        context.computeVirtualSites()
        s=context.getState(getPositions=True,getEnergy=True,getForces=True)
        forces=s.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
        result[f'{platform}-{nested}']=dict(energy=float(s.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),
            parent_forces=forces[:2].tolist(),cap_force=forces[13].tolist(),
            max_parent_error=float(np.max(np.abs(forces[:2]-expected[:2]))),
            cap_position=s.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[13].tolist())
        del context,integrator
print(json.dumps(result,indent=2))
assert all(r['max_parent_error']<=1e-7 for r in result.values()), 'nested redistribution mismatch'
