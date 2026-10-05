"""Six-atom stock TIP3P reproducer; no project/ML/cap imports or custom physics.

Run in the unchanged pinned environment. Outputs distinguish actual raw and
canonical-coordinate behavior; this diagnostic is not a new backend profile.
"""
import json
from pathlib import Path
import sys

import numpy as np
import openmm as mm
from openmm import app,unit

POSITIONS=np.array(((.4415733928415964,.000009999999999988898,6.08),
    (.5372933928415964,-1.1102907872609369e-17,6.08),
    (.417574672000693,.09266272064859948,6.08),
    (.4415733928415964,.32,1.6653345369377347e-17),
    (.5372933928415964,.32,1.6653345369377347e-17),
    (.417574672000693,.4126627206485995,1.6653345369377347e-17)))


def probe():
    topology=app.Topology(); chain=topology.addChain()
    for _ in range(2):
        residue=topology.addResidue('HOH',chain)
        atoms=[topology.addAtom(name,app.Element.getBySymbol(element),residue)
               for name,element in (('O','O'),('H1','H'),('H2','H'))]
        topology.addBond(atoms[0],atoms[1]); topology.addBond(atoms[0],atoms[2])
    topology.setPeriodicBoxVectors((mm.Vec3(6.4,0.,0.),mm.Vec3(0.,6.4,0.),mm.Vec3(0.,0.,6.4))*unit.nanometer)
    system=app.ForceField('tip3p.xml').createSystem(topology,nonbondedMethod=app.PME,
        nonbondedCutoff=.9*unit.nanometer,rigidWater=True,removeCMMotion=False)
    nb=next(f for f in system.getForces() if isinstance(f,mm.NonbondedForce))
    nb.setPMEParameters(4.4,64,64,64); nb.setEwaldErrorTolerance(1e-7)
    nb.setUseSwitchingFunction(True); nb.setSwitchingDistance(.75); nb.setUseDispersionCorrection(False)
    nb.setReciprocalSpaceForceGroup(1)
    integrator=mm.VerletIntegrator(.0005)
    context=mm.Context(system,integrator,mm.Platform.getPlatformByName('Reference'))
    try:
        rows=[]
        for mode in ('raw','one-hydrogen-exact-zero','canonical-faces'):
            x=POSITIONS.copy()
            if mode=='one-hydrogen-exact-zero': x[1,1]=0.
            if mode=='canonical-faces':
                boundary=np.rint(x/6.4)*6.4
                x=np.where(np.abs(x-boundary)<=8*np.spacing(6.4),boundary,x)
            context.setPositions(x*unit.nanometer)
            saved=context.getState(getEnergy=True,getForces=True)
            rows.append({'mode':mode,'positions_nm':x.tolist(),
                'energy_kj_mol':saved.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),
                'real_space_energy_kj_mol':context.getState(getEnergy=True,groups=1).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),
                'reciprocal_energy_kj_mol':context.getState(getEnergy=True,groups=2).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),
                'forces_kj_mol_nm':saved.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer).tolist()})
        return {'openmm_version':mm.version.full_version,'platform':'Reference',
            'construction':'stock OpenMM ForceField tip3p.xml; no project builder, ML or caps',
            'system_xml':mm.XmlSerializer.serialize(system),'rows':rows}
    finally:
        del context,integrator


if __name__=='__main__':
    output=Path(sys.argv[1]); output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as handle: json.dump(probe(),handle,indent=2); handle.write('\n')
