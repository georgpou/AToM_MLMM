"""Numerical smoke for the installed wheel, run outside the source checkout."""
import json
import os
from pathlib import Path
import sys

import openmm as mm
from openmm import unit

import atm_mlmm
from atm_mlmm.analytic import SelectedHarmonic

system = mm.System()
system.addParticle(12.0 * unit.dalton)
force = mm.PythonForce(SelectedHarmonic((2.0,), ((0.0, 0.0, 0.0),)))
force.setParticles([0])
system.addForce(force)
integrator = mm.VerletIntegrator(0.0005 * unit.picoseconds)
context = mm.Context(system, integrator, mm.Platform.getPlatformByName("Reference"))
context.setPositions([[0.2, 0.0, 0.0]] * unit.nanometer)
state = context.getState(getEnergy=True, getForces=True)
energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole / unit.nanometer)
assert abs(energy - 0.04) < 1e-12
assert abs(float(forces[0][0]) + 0.4) < 1e-12
package_path = Path(atm_mlmm.__file__).resolve()
source_root = Path(os.environ["ATOM_MLMM_SOURCE_ROOT"]).resolve()
assert not package_path.is_relative_to(source_root)
assert package_path.is_relative_to(Path(sys.prefix).resolve())
print(json.dumps({"scope": "installed analytic one-particle harmonic energy/force",
                  "energy_kj_mol": energy,
                  "force_kj_mol_nm": forces.tolist(),
                  "package_location": str(package_path),
                  "project_install_prefix": sys.prefix,
                  "source_checkout_excluded": True}, sort_keys=True))
