"""Check that the main Python environment can call the separate AmberTools."""
from openff.toolkit import Molecule
from openmmforcefields.generators import GAFFTemplateGenerator
from openmm import app, unit
import openmm as mm
import numpy as np

molecule = Molecule.from_smiles("C")
molecule.generate_conformers(n_conformers=1)
generator = GAFFTemplateGenerator(molecules=[molecule], forcefield="gaff-2.2.20")
forcefield = app.ForceField()
forcefield.registerTemplateGenerator(generator.generator)
system = forcefield.createSystem(molecule.to_topology().to_openmm(), nonbondedMethod=app.NoCutoff)
context = mm.Context(system, mm.VerletIntegrator(.001), mm.Platform.getPlatformByName("CPU"))
context.setPositions(molecule.conformers[0].m_as("nanometer"))
state = context.getState(getEnergy=True, getForces=True)
energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
assert system.getNumParticles() == 5
assert np.isfinite(energy) and np.isfinite(forces).all()
print("OpenFF/openmmforcefields in main environment -> separate AmberTools -> finite CPU energy and forces:", energy)
