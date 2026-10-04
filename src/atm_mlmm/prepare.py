"""Project-owned physical preparation, separate from reserved-group exports."""
from dataclasses import replace
import math

import numpy as np
import openmm as mm
from openmm import unit

from .atm import PhysicalEvaluator, make_integrator, physical_system, validate_runtime
from .schema import MalformedInput, PhysicalBundle, Snapshot, UnsupportedCapability


class PhysicalPreparation(PhysicalEvaluator):
    def __init__(self, physical, runtime, *, random_seed=None):
        if not isinstance(physical, PhysicalBundle):
            raise UnsupportedCapability('preparation requires a physical bundle, not a production export')
        validate_runtime(runtime)
        if runtime.integrator != 'LangevinMiddle':
            raise UnsupportedCapability('preparation qualifies LangevinMiddle explicitly')
        self.bundle = physical
        system = physical_system(physical)
        for force in system.getForces():
            force.setForceGroup(0)
        integrator = make_integrator(runtime)
        if random_seed is not None:
            if isinstance(random_seed,bool) or not isinstance(random_seed,int) or not 0 < random_seed < 2**31:
                raise MalformedInput('random_seed must be a positive bounded integer')
            integrator.setRandomNumberSeed(random_seed)
        self._open(system, runtime, integrator)
        self.integrator.setIntegrationForceGroups({0})


def build_preparation(physical, runtime, *, random_seed=None):
    return PhysicalPreparation(physical, runtime, random_seed=random_seed)


def prepare_phases(physical, snapshot, runtime, *, temperatures_K=(10., 100., 300.),
                   steps_per_phase=2, minimization_iterations=10, seed=41):
    """Bounded all-active minimization and explicit gradual NVT phases.

    Each thermostat phase has its own admitted RuntimeSpec/context. This is
    workflow preparation, with no claim of density or equilibrium convergence.
    """
    validate_runtime(runtime)
    temperatures = tuple(temperatures_K)
    if (not temperatures or any(isinstance(t, bool) or not isinstance(t, (int, float))
            or not math.isfinite(t) or t <= 0 for t in temperatures)
            or any(a >= b for a, b in zip(temperatures, temperatures[1:]))
            or temperatures[-1] != runtime.temperature_K):
        raise MalformedInput('preparation temperatures must increase to declared runtime temperature')
    for name, value in (('steps_per_phase', steps_per_phase),
                        ('minimization_iterations', minimization_iterations), ('seed', seed)):
        if isinstance(value, bool) or not isinstance(value, int) or not 0 < value < 2**31:
            raise MalformedInput(f'{name} must be a positive bounded integer')
    phases, saved, previous_temperature = [], None, None
    current = snapshot
    for index, temperature in enumerate(temperatures):
        phase_runtime = replace(runtime, temperature_K=float(temperature))
        if seed+index >= 2**31:
            raise MalformedInput('phase seed exceeds admitted integer range')
        with build_preparation(physical, phase_runtime, random_seed=seed+index) as preparation:
            preparation.evaluate(current)
            if saved is None:
                preparation.context.applyConstraints(1.e-8)
                initial_energy = preparation.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                mm.LocalEnergyMinimizer.minimize(preparation.context, 10., minimization_iterations)
                preparation.context.setVelocitiesToTemperature(temperature, seed)
            else:
                preparation.context.setState(saved)
                velocities = saved.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond)
                preparation.context.setVelocities(velocities*np.sqrt(temperature/previous_temperature))
            preparation._guard_system()
            preparation.integrator.step(steps_per_phase)
            preparation._guard_system()
            preparation.context.computeVirtualSites()
            saved = preparation.context.getState(getPositions=True, getVelocities=True,
                                                  getParameters=True, getEnergy=True, getForces=True)
            x = saved.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            forces = saved.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer)
            energy = saved.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
            if not np.isfinite(x).all() or not np.isfinite(forces).all() or not math.isfinite(energy):
                from .schema import NumericalDomainError
                raise NumericalDomainError('nonfinite preparation; preserve the failed attempt')
            ids = tuple(a.atom_id for a in physical.topology.atoms)
            positions = tuple(tuple(x[physical.real_to_final[a]]) for a in ids)
            current = Snapshot(ids, positions, snapshot.box_nm)
            phases.append(dict(temperature_K=float(temperature), timestep_ps=runtime.timestep_ps,
                               steps=steps_per_phase, seed=seed+index, integration_groups=[0],
                               constraint_tolerance=preparation.integrator.getConstraintTolerance(),
                               energy_kj_mol=energy, max_real_force_kj_mol_nm=float(np.max(np.abs(forces[list(physical.old_to_new)]))),
                               physical_identity=physical.content_identity, snapshot_identity=current.content_identity))
            previous_temperature = temperature
    return dict(physical_identity=physical.content_identity, snapshot=current,
                state_xml=mm.XmlSerializer.serialize(saved), phases=phases,
                initial_energy_kj_mol=initial_energy, minimization_iterations=minimization_iterations)
