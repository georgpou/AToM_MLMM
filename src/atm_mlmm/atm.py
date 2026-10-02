"""Shared native transfer assembly and full-real-coordinate evaluation.

Systems sealed by the project are trusted executable artifacts. External JSON
must enter through load_bundle with explicit trust and an expected digest;
neither XML nor PythonForce pickle is a safe untrusted interchange format.
"""
import copy
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import openmm as mm
from openmm import unit

from .geometry import final_positions, validate_sites, validate_transfer
from .persistence import write_json
from .schedule import schedule_state, softened_perturbation, validate_schedule
from .schema import (AlchemicalBundle, AtmEvaluation, EnergyForces,
                     IdentityError, PhysicalBundle, RawAtmEnergies,
                     UnsupportedCapability, from_json, to_json)


def xml_digest(xml):
    return hashlib.sha256(xml.encode()).hexdigest()


def force_digest(force):
    """Name-preserving ownership fingerprint independent of routing group."""
    force = copy.copy(force)
    force.setForceGroup(0)
    return xml_digest(mm.XmlSerializer.serialize(force))


def physical_system(bundle):
    if xml_digest(bundle.system_xml) != bundle.system_sha256:
        raise IdentityError('physical System digest mismatch before deserialization')
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    if system.getNumParticles() != len(bundle.masses_da):
        raise IdentityError('physical final-particle count mismatch')
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles()))
    constraints = tuple((int(a), int(b), d.value_in_unit(unit.nanometer))
                        for a, b, d in (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    if masses != bundle.masses_da or constraints != bundle.constraints:
        raise IdentityError('physical masses/constraints mismatch')
    validate_sites(system,bundle)
    if system.getNumForces() != len(bundle.ledger):
        raise IdentityError('physical force ledger count mismatch')
    for row, force in zip(bundle.ledger, system.getForces()):
        if xml_digest(mm.XmlSerializer.serialize(force)) != row.parameters['force_sha256']:
            raise IdentityError(f'physical force ledger mismatch: {row.index}')
    return system


def outside_force(physical, restraints):
    if not set(restraints.atom_ids) <= set(physical.real_to_final):
        raise IdentityError('outside restraint references unknown real atoms')
    force = mm.CustomExternalForce('0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)')
    for parameter in ('k', 'x0', 'y0', 'z0'):
        force.addPerParticleParameter(parameter)
    for atom_id in restraints.atom_ids:
        force.addParticle(physical.real_to_final[atom_id], [restraints.spring_kj_mol_nm2, *restraints.center_nm])
    force.setName('restraint:'+restraints.restraint_id)
    force.setForceGroup(0)
    return force


def validate_atm_schedule(force, schedule):
    """Bind executed ATM semantics to the declared schedule before admission."""
    # Ignore whitespace between tokens, including the pinned upstream's extra
    # space before a comma. Whitespace inside a name/number changes its tokens.
    token = r'[A-Za-z_]\w*|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[^\s]'
    if re.findall(token, force.getEnergyFunction()) != re.findall(token, schedule.expression):
        raise IdentityError('actual ATM expression differs from declared schedule')
    names = [force.getGlobalParameterName(i) for i in range(force.getNumGlobalParameters())]
    if len(names) != len(set(names)):
        raise IdentityError('ATM schedule/global parameter names must be unique')
    missing = set(schedule.parameter_units) - set(names)
    if missing:
        raise IdentityError(f'ATM lacks required schedule global parameters: {sorted(missing)}')


def validate_physical_parameter_ownership(system, schedule):
    """Schedule globals may not also control an admitted physical System."""
    from .routing import walk_forces
    for path, force in walk_forces(system):
        if isinstance(force, mm.ATMForce) or not hasattr(force, 'getNumGlobalParameters'):
            continue
        names = {force.getGlobalParameterName(i) for i in range(force.getNumGlobalParameters())}
        collisions = names & set(schedule.parameter_units)
        if collisions:
            raise IdentityError(f'physical/schedule global parameter collision at {path}: {sorted(collisions)}')


def seal_alchemical(system, physical, transfer, schedule, restraints, *, construction='native'):
    from .routing import validate_routing
    validate_transfer(physical, transfer)
    validate_schedule(schedule)
    report = validate_routing(system, physical, restraints)
    force = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    validate_atm_schedule(force, schedule)
    # Routing already proves the actual children match this physical source.
    # ATMForce.getForce returns base Force wrappers without parameter accessors.
    validate_physical_parameter_ownership(physical_system(physical), schedule)
    xml = mm.XmlSerializer.serialize(system)
    return AlchemicalBundle(physical, transfer, schedule, restraints, xml, xml_digest(xml), tuple(report), construction)


def build_atm(bundle, transfer, schedule, restraints):
    validate_transfer(bundle, transfer)
    validate_schedule(schedule)
    system = physical_system(bundle)
    validate_physical_parameter_ownership(system, schedule)
    force = mm.ATMForce(schedule.expression)
    for name, value in schedule.states[0].parameters.items():
        force.addGlobalParameter(name, value)
    for map0, map1 in zip(transfer.displacement0_nm, transfer.displacement1_nm):
        force.addParticle(mm.Vec3(*map1), mm.Vec3(*map0))
    for original in system.getForces():
        force.addForce(copy.copy(original))
    for i in reversed(range(system.getNumForces())):
        system.removeForce(i)
    force.setForceGroup(31)
    system.addForce(force)
    system.addForce(outside_force(bundle, restraints))
    return seal_alchemical(system, bundle, transfer, schedule, restraints)


def validate_runtime(runtime):
    if runtime.platform not in ('Reference', 'CPU') or runtime.device_allocation:
        raise UnsupportedCapability('analytic runtime requires Reference/CPU without GPU allocation')
    if runtime.precision != 'double' or runtime.ensemble != 'NVT':
        raise UnsupportedCapability('analytic runtime requires double reference precision and NVT')
    if runtime.integrator not in ('LangevinMiddle', 'Verlet') or runtime.timestep_ps > .0005:
        raise UnsupportedCapability('analytic runtime requires an admitted integrator and timestep <=0.0005 ps')


def make_integrator(runtime):
    validate_runtime(runtime)
    if runtime.integrator == 'Verlet':
        return mm.VerletIntegrator(runtime.timestep_ps*unit.picosecond)
    return mm.LangevinMiddleIntegrator(runtime.temperature_K*unit.kelvin,
                                       1./unit.picosecond, runtime.timestep_ps*unit.picosecond)


class _Evaluator:
    def _open(self, system, runtime, integrator=None, *, varying_parameters=()):
        validate_runtime(runtime)
        self.system = system
        self.runtime = runtime
        self.integrator = make_integrator(runtime) if integrator is None else integrator
        expected_type = mm.LangevinMiddleIntegrator if runtime.integrator == 'LangevinMiddle' else mm.VerletIntegrator
        if not isinstance(self.integrator, expected_type) or self.integrator.getStepSize().value_in_unit(unit.picosecond) != runtime.timestep_ps:
            raise UnsupportedCapability('actual integrator differs from declared runtime')
        if runtime.integrator == 'LangevinMiddle' and self.integrator.getTemperature().value_in_unit(unit.kelvin) != runtime.temperature_K:
            raise IdentityError('actual integrator temperature differs from runtime')
        platform = mm.Platform.getPlatformByName(runtime.platform)
        properties = {'Threads': '2'} if runtime.platform == 'CPU' else {}
        self.context = mm.Context(system, self.integrator, platform, properties)
        self._fixed_parameters = {name: value for name, value in self.context.getParameters().items()
                                  if name not in varying_parameters}
        self._system_digest = xml_digest(mm.XmlSerializer.serialize(system))
        self._bundle_identity = self.bundle.content_identity
        self._runtime_identity = runtime.content_identity

    def _guard_system(self):
        if self.context is None:
            raise IdentityError('runtime evaluator is closed')
        if self.bundle.content_identity != self._bundle_identity:
            raise IdentityError('runtime bundle identity/fixed membership replacement requires a new context')
        if self.runtime.content_identity != self._runtime_identity:
            raise IdentityError('runtime profile identity replacement requires a new context')
        if xml_digest(mm.XmlSerializer.serialize(self.system)) != self._system_digest:
            raise IdentityError('runtime System/force/map mutation invalidates sealed identity')
        actual = self.context.getParameters()
        for name, value in self._fixed_parameters.items():
            if actual[name] != value:
                raise IdentityError(f'fixed runtime parameter mutation before evaluation: {name}')
        groups = {force.getForceGroup() for force in self.system.getForces()}
        required = sum(1 << group for group in groups)
        if self.integrator.getIntegrationForceGroups() & required != required:
            raise IdentityError('actual integrator mask omits a physical/outside force group')
        if self.integrator.getStepSize().value_in_unit(unit.picosecond) != self.runtime.timestep_ps:
            raise IdentityError('actual integrator timestep mutation')
        if self.runtime.integrator == 'LangevinMiddle' and self.integrator.getTemperature().value_in_unit(unit.kelvin) != self.runtime.temperature_K:
            raise IdentityError('actual integrator temperature mutation')

    def _position(self, physical, snapshot):
        self.context.setPositions(final_positions(physical, snapshot)*unit.nanometer)
        self.context.computeVirtualSites()

    def _result(self, physical, snapshot, state):
        forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer)
        ids = tuple(a.atom_id for a in physical.topology.atoms)
        return EnergyForces(state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole), ids,
                            tuple(tuple(forces[physical.real_to_final[a]]) for a in ids),
                            physical.content_identity, snapshot.content_identity,
                            {'platform': self.runtime.platform, 'model_dtype': 'float64',
                             'openmm_precision': 'double' if self.runtime.platform == 'Reference' else 'CPU_default'})

    def close(self):
        self.context = None
        self.integrator = None
        self.system = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class PhysicalEvaluator(_Evaluator):
    def __init__(self, bundle, runtime):
        validate_runtime(runtime)
        self.bundle = bundle
        self._open(physical_system(bundle), runtime)

    def evaluate(self, snapshot):
        self._guard_system()
        self._position(self.bundle, snapshot)
        return self._result(self.bundle, snapshot, self.context.getState(getEnergy=True, getForces=True))


class AtmEvaluator(_Evaluator):
    def __init__(self, bundle, runtime, *, system=None, integrator=None):
        from .routing import validate_routing
        validate_runtime(runtime)
        validate_schedule(bundle.schedule)
        validate_transfer(bundle.physical, bundle.transfer)
        if runtime.temperature_K != bundle.schedule.temperature_K:
            raise IdentityError('schedule/runtime temperature mismatch')
        if xml_digest(bundle.system_xml) != bundle.system_sha256:
            raise IdentityError('ATM System digest mismatch before deserialization')
        declared = mm.XmlSerializer.deserialize(bundle.system_xml)
        if system is None:
            system = declared
        elif mm.XmlSerializer.serialize(system) != mm.XmlSerializer.serialize(declared):
            raise IdentityError('provided runtime System differs from sealed ATM artifact')
        if validate_routing(system, bundle.physical, bundle.restraints) != bundle.routing_report:
            raise IdentityError('saved routing report differs from actual recursive ownership')
        self.bundle = bundle
        self.atm_force = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
        validate_atm_schedule(self.atm_force, bundle.schedule)
        validate_physical_parameter_ownership(physical_system(bundle.physical), bundle.schedule)
        self.outside_groups = {r.force_group for r in bundle.routing_report if r.disposition == 'outside'}
        if self.atm_force.getForceGroup() in self.outside_groups:
            raise IdentityError('ATM and outside energies require separate groups')
        self._open(system, runtime, integrator, varying_parameters=bundle.schedule.parameter_units)
        self._state_id = bundle.schedule.states[0].state_id
        self._expected_parameters = dict(bundle.schedule.states[0].parameters)
        self._auxiliary_parameters = self._fixed_parameters
        self._check_maps()
        # Artifact defaults may differ in upstream construction: explicitly
        # restore the complete first schedule state before admitting evaluation.
        for name, value in self._expected_parameters.items():
            self.context.setParameter(name, value)
        self._guard()

    def _check_maps(self):
        transfer = self.bundle.transfer
        if self.atm_force.getNumParticles() != transfer.final_particle_count:
            raise IdentityError('fixed full-particle map count mismatch')
        for i, (map0, map1) in enumerate(zip(transfer.displacement0_nm, transfer.displacement1_nm)):
            transform = self.atm_force.getParticleTransformation(i)
            if not isinstance(transform, mm.FixedDisplacement):
                raise IdentityError(f'non-fixed runtime particle transformation: {i}')
            actual0 = tuple(transform.getFixedDisplacement0().value_in_unit(unit.nanometer))
            actual1 = tuple(transform.getFixedDisplacement1().value_in_unit(unit.nanometer))
            if actual0 != map0 or actual1 != map1:
                raise IdentityError(f'fixed full-particle map mutation at particle {i}')

    def _guard(self):
        self._guard_system()
        self._check_maps()
        actual = self.context.getParameters()
        for name, value in self._expected_parameters.items():
            if actual[name] != value:
                raise IdentityError(f'runtime parameter mutation before evaluation: {name}')

    def set_state(self, state_id, *, setter=None):
        self._guard()
        state = schedule_state(self.bundle.schedule, state_id)
        if setter is None:
            for name, value in state.parameters.items():
                self.context.setParameter(name, value)
        else:
            setter(state.parameters)
        self._expected_parameters = dict(state.parameters)
        self._state_id = state_id
        self._guard()

    def restore_state(self, state, state_id):
        self._guard()
        requested = schedule_state(self.bundle.schedule, state_id)
        self.context.setState(state)
        # A portable State overwrites parameters; reinstate every declared one.
        for name, value in {**self._auxiliary_parameters, **requested.parameters}.items():
            self.context.setParameter(name, value)
        self._state_id = state_id
        self._expected_parameters = dict(requested.parameters)
        self._guard()

    def evaluate(self, snapshot, state_id):
        self.set_state(state_id)
        self._position(self.bundle.physical, snapshot)
        state = self.context.getState(getEnergy=True, getForces=True)
        total = self._result(self.bundle.physical, snapshot, state)
        u1, u0, expression = self.atm_force.getPerturbationEnergy(self.context)
        u0, u1, expression = (v.value_in_unit(unit.kilojoules_per_mole) for v in (u0, u1, expression))
        outside = self.context.getState(getEnergy=True, groups=self.outside_groups).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        raw = RawAtmEnergies(u0, u1, u1-u0,
                             softened_perturbation(u0, u1, self.bundle.schedule, self._expected_parameters),
                             expression, outside, total.energy_kj_mol)
        return AtmEvaluation(total, raw, state_id, self.bundle.transfer.content_identity,
                             self.bundle.schedule.content_identity, self.bundle.restraints.content_identity,
                             self._expected_parameters)


def evaluate_physical(bundle, snapshot, runtime):
    with PhysicalEvaluator(bundle, runtime) as evaluator:
        return evaluator.evaluate(snapshot)


def evaluate_atm(bundle, snapshot, state_id, runtime):
    with AtmEvaluator(bundle, runtime) as evaluator:
        return evaluator.evaluate(snapshot, state_id)


def save_bundle(path, bundle):
    if not isinstance(bundle, (PhysicalBundle, AlchemicalBundle)):
        raise UnsupportedCapability('only sealed physical/alchemical bundles can be saved')
    write_json(path, json.loads(to_json(bundle)))
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_bundle(path, expected_sha256, *, trusted=False):
    if trusted is not True:
        raise UnsupportedCapability('PythonForce artifacts require explicitly trusted loading')
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise IdentityError('bundle digest mismatch before executable deserialization')
    result = from_json(payload.decode())
    if not isinstance(result, (PhysicalBundle, AlchemicalBundle)):
        raise UnsupportedCapability('not a physical/alchemical artifact')
    return result
