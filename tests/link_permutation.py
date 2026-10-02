"""Independent remapped fixture construction using public OpenMM APIs."""
import copy
import numpy as np
import openmm as mm
from openmm import app,unit


def permute_info(info,old_to_new):
    old=info['system'];new=mm.System()
    inverse=np.argsort(old_to_new)
    for i in inverse:new.addParticle(old.getParticleMass(int(i)))
    for i in range(old.getNumParticles()):
        if old.isVirtualSite(i):
            site=old.getVirtualSite(i)
            new.setVirtualSite(old_to_new[i],mm.LocalCoordinatesSite(
                [old_to_new[site.getParticle(j)] for j in range(site.getNumParticles())],
                site.getOriginWeights(),site.getXWeights(),site.getYWeights(),site.getLocalPosition()))
    for i in range(old.getNumConstraints()):
        a,b,d=old.getConstraintParameters(i);new.addConstraint(old_to_new[a],old_to_new[b],d)
    for original in old.getForces():
        force=copy.deepcopy(original)
        if isinstance(force,mm.HarmonicBondForce):
            for i in range(force.getNumBonds()):
                a,b,d,k=force.getBondParameters(i);force.setBondParameters(i,old_to_new[a],old_to_new[b],d,k)
        elif isinstance(force,mm.HarmonicAngleForce):
            for i in range(force.getNumAngles()):
                a,b,c,t,k=force.getAngleParameters(i);force.setAngleParameters(i,old_to_new[a],old_to_new[b],old_to_new[c],t,k)
        elif isinstance(force,mm.PeriodicTorsionForce):
            for i in range(force.getNumTorsions()):
                a,b,c,d,n,p,k=force.getTorsionParameters(i);force.setTorsionParameters(i,*(old_to_new[j] for j in (a,b,c,d)),n,p,k)
        elif isinstance(force,mm.NonbondedForce):
            particles=[force.getParticleParameters(int(i)) for i in inverse]
            for i,p in enumerate(particles):force.setParticleParameters(i,*p)
            for i in range(force.getNumExceptions()):
                a,b,q,s,e=force.getExceptionParameters(i);force.setExceptionParameters(i,old_to_new[a],old_to_new[b],q,s,e)
        elif isinstance(force,mm.PythonForce):
            force.setParticles([old_to_new[i] for i in force.getParticles()])
        else:raise AssertionError(type(force))
        new.addForce(force)
    topology=app.Topology();residue=topology.addResidue('deliberately-unhelpful',topology.addChain())
    original_atoms=list(info['topology'].atoms())
    atoms=[topology.addAtom(original_atoms[int(i)].name,original_atoms[int(i)].element,residue) for i in inverse]
    for b in info['topology'].bonds():
        topology.addBond(atoms[old_to_new[b.atom1.index]],atoms[old_to_new[b.atom2.index]])
    return dict(system=new,topology=topology,oldToNew=[old_to_new[i] for i in info['oldToNew']])


def plain_result(system,positions):
    """Evaluate retained MM on independently laid-out positions, computing sites."""
    integrator=mm.VerletIntegrator(.0005)
    context=mm.Context(system,integrator,mm.Platform.getPlatformByName('Reference'))
    try:
        r=np.zeros((system.getNumParticles(),3));r[:len(positions)]=positions
        context.setPositions(r);context.computeVirtualSites()
        s=context.getState(getEnergy=True,getForces=True)
        return (float(s.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),
                s.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)[:len(positions)])
    finally:del context,integrator
