"""Explicit recursive physical ownership and actual integration-mask checks."""
import copy
from dataclasses import dataclass

import numpy as np
import openmm as mm
from openmm import unit

from .atm import force_digest, outside_force, physical_system, xml_digest
from .schema import ForceOwnership, IdentityError, PhysicalBundle, UnsupportedCapability


def walk_forces(system):
    def descend(force, path):
        yield path, force
        if isinstance(force, mm.ATMForce):
            children = (force.getForce(i) for i in range(force.getNumForces()))
        elif isinstance(force, mm.CustomCVForce):
            children = (force.getCollectiveVariable(i) for i in range(force.getNumCollectiveVariables()))
        else:
            children = ()
        for i, child in enumerate(children):
            yield from descend(child, path+(i,))
    for i, force in enumerate(system.getForces()):
        yield from descend(force, (i,))


def _reject_duplicates(rows):
    seen = {}
    for path, force in rows:
        if isinstance(force, mm.ATMForce):
            continue
        # Names and groups are labels. Preserve them in ownership/report hashes,
        # but exclude both when deciding whether physical content is duplicated.
        content = copy.copy(force)
        content.setName('')
        content.setForceGroup(0)
        digest = xml_digest(mm.XmlSerializer.serialize(content))
        if digest in seen:
            raise IdentityError(f'duplicate force ownership/content at {seen[digest]} and {path}: {force.getName()}')
        seen[digest] = path


@dataclass
class ProductionExport:
    """A distinct mutable handover copy, never an ordinary preparation input."""
    physical: PhysicalBundle
    system: object
    reserved_group: int
    system_sha256: str

    def check(self):
        if xml_digest(mm.XmlSerializer.serialize(self.system)) != self.system_sha256:
            raise IdentityError('production export System mutation')


def export_physical(physical, *, reserved_group=1):
    if not isinstance(physical, PhysicalBundle):
        raise UnsupportedCapability('production export requires a sealed PhysicalBundle')
    if isinstance(reserved_group, bool) or not isinstance(reserved_group, int) or not 1 <= reserved_group <= 31:
        raise UnsupportedCapability('reserved production force group must be an integer in [1,31]')
    system = physical_system(physical)
    rows = tuple(walk_forces(system))
    if any(isinstance(force, mm.ATMForce) for _, force in rows):
        raise IdentityError('already nested ATM physical input is forbidden')
    if any(force.getForceGroup() == reserved_group for _, force in rows):
        raise IdentityError(f'reserved force group {reserved_group} is occupied')
    _reject_duplicates(rows)
    for force in system.getForces():
        force.setForceGroup(reserved_group)
    return ProductionExport(physical, system, reserved_group, xml_digest(mm.XmlSerializer.serialize(system)))


def validate_routing(system, physical, restraints):
    rows = tuple(walk_forces(system))
    atms = [(path, force) for path, force in rows if isinstance(force, mm.ATMForce)]
    if len(atms) != 1 or len(atms[0][0]) != 1:
        raise IdentityError('exactly one top-level ATM required; nested ATM is forbidden')
    _reject_duplicates(rows)
    source = physical_system(physical)
    _reject_duplicates(tuple(walk_forces(source)))
    expected = {force_digest(f): (f'physical:{i}', type(f).__name__)
                for i, f in enumerate(source.getForces())}
    outside_digest = force_digest(outside_force(physical, restraints))
    parent_path, parent = atms[0]
    report, found, outside_count = [], set(), 0
    for path, force in rows:
        if isinstance(force, mm.ATMForce):
            continue
        digest = force_digest(force)
        if path[:1] == parent_path:
            if len(path) != 2 or digest not in expected:
                raise IdentityError(f'unowned physical child force at {path}: {force.getName()}')
            force_id, class_name = expected[digest]
            found.add(digest)
            disposition = 'physical_child'
        else:
            if len(path) != 1 or digest != outside_digest:
                raise IdentityError(f'physical force left outside or unowned outside contribution at {path}')
            force_id, class_name = restraints.restraint_id, type(force).__name__
            disposition = 'outside'
            outside_count += 1
            if force.getForceGroup() == parent.getForceGroup():
                raise IdentityError('outside and ATM expression energy require separate force groups')
        report.append(ForceOwnership(force_id, class_name, force.getName(), disposition,
                                     force.getForceGroup(), path, digest))
    if found != set(expected) or parent.getNumForces() != len(expected) or outside_count != 1:
        raise IdentityError('physical child/outside force ownership is incomplete')
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles()))
    constraints = tuple((int(a), int(b), d.value_in_unit(unit.nanometer))
                        for a, b, d in (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    if masses != physical.masses_da or constraints != physical.constraints:
        raise IdentityError('production changes physical masses/constraints')
    return tuple(report)


def check_active_forces(context, integrator, *, force_tolerance=1e-7):
    mask = integrator.getIntegrationForceGroups()
    required_groups = sorted({f.getForceGroup() for f in context.getSystem().getForces()})
    required_mask = sum(1 << group for group in required_groups)
    full = context.getState(getForces=True).getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer)
    active = context.getState(getForces=True, groups=mask).getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer)
    error = float(np.max(np.abs(full-active)))
    if mask & required_mask != required_mask or not np.isfinite(error) or error > force_tolerance:
        raise IdentityError(f'integration force-group mask {mask} omits forces: required groups {required_groups}, max component error {error}')
    return dict(integration_mask=mask, required_groups=required_groups,
                max_force_error_kJ_mol_nm=error, full_force_norm=float(np.linalg.norm(full)),
                integrated_force_norm=float(np.linalg.norm(active)))
