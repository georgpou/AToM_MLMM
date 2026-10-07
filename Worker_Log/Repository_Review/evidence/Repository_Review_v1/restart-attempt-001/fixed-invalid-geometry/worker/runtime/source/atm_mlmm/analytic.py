"""Importable, deterministic analytic substitutes; no molecular qualification."""
from dataclasses import dataclass
import hashlib

import numpy as np
import openmm as mm
from openmm import unit

from .schema import (ForceRecord, IdentityError, MalformedInput, NumericalDomainError,
                     PhysicalBundle, UnsupportedCapability)


@dataclass(frozen=True)
class SelectedHarmonic:
    spring_constants: tuple
    centers_nm: tuple

    def __call__(self, state):
        positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        difference = positions - np.asarray(self.centers_nm, dtype=np.float64)
        k = np.asarray(self.spring_constants, dtype=np.float64)[:, None]
        energy = float(.5*np.sum(k*difference*difference))
        forces = -k*difference
        if not np.isfinite(energy) or not np.isfinite(forces).all():
            raise NumericalDomainError('nonfinite selected harmonic result')
        return energy, forces


@dataclass(frozen=True)
class EnvironmentSpring:
    k: float

    def __call__(self, state):
        # Recompute from the mapped coordinates on every invocation.
        positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        difference = positions[0]-positions[1]
        energy = float(.5*self.k*np.dot(difference, difference))
        force = -self.k*difference
        forces = np.asarray((force, -force), dtype=np.float64)
        if not np.isfinite(energy) or not np.isfinite(forces).all():
            raise NumericalDomainError('nonfinite environment spring result')
        return energy, forces


def seal_physical(system, topology, *, ml_atom_ids, old_to_new, manifest):
    """Seal a caller-owned trusted System, consuming its explicit source map."""
    if len(old_to_new) != len(topology.atoms):
        raise IdentityError('oldToNew must cover every original real atom')
    if system.getNumParticles() != len(topology.atoms) or any(system.isVirtualSite(i) for i in range(system.getNumParticles())):
        raise UnsupportedCapability('analytic factory admits real particles only; caps require G04')
    if system.usesPeriodicBoundaryConditions():
        raise UnsupportedCapability('analytic factory is nonperiodic')
    ledger = []
    for i, force in enumerate(system.getForces()):
        if not isinstance(force, (mm.PythonForce, mm.CustomExternalForce)):
            raise UnsupportedCapability(f'unadmitted analytic physical force: {type(force).__name__}')
        xml = mm.XmlSerializer.serialize(force)
        ledger.append(ForceRecord(i, type(force).__name__, force.getName(), force.getForceGroup(),
                                 force.usesPeriodicBoundaryConditions(),
                                 {'force_sha256': hashlib.sha256(xml.encode()).hexdigest()}))
    ids = tuple(a.atom_id for a in topology.atoms)
    real_to_final = dict(zip(ids, old_to_new))
    xml = mm.XmlSerializer.serialize(system)
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles()))
    constraints = tuple((int(a), int(b), d.value_in_unit(unit.nanometer))
                        for a, b, d in (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    return PhysicalBundle(xml, hashlib.sha256(xml.encode()).hexdigest(), topology, real_to_final,
                          {a: real_to_final[a] for a in ml_atom_ids}, tuple(old_to_new), tuple(ml_atom_ids),
                          masses, constraints, tuple(ledger), manifest)


def make_analytic_bundle(topology, *, ml_atom_ids, masses_da, selected_particles,
                         spring_constants, centers_nm, environment_pairs=(), marker_k=0., old_to_new,
                         additional_harmonics=()):
    count = len(topology.atoms)
    if len(old_to_new) != count or set(old_to_new) != set(range(count)):
        raise IdentityError('oldToNew must be a complete final particle permutation')
    selected = tuple(selected_particles)
    constants = tuple(float(k) for k in spring_constants)
    centers = tuple(tuple(float(x) for x in row) for row in centers_nm)
    if not selected or len(set(selected)) != len(selected) or any(i not in range(count) for i in selected):
        raise IdentityError('invalid selected particle order/index')
    if len(constants) != len(selected) or len(centers) != len(selected) or any(len(row) != 3 for row in centers):
        raise MalformedInput('harmonic constants/centres must cover selected particles')
    values = (*constants, *(x for row in centers for x in row), marker_k, *masses_da)
    if not all(np.isfinite(v) for v in values) or any(k < 0 for k in constants) or marker_k < 0:
        raise NumericalDomainError('invalid analytic harmonic parameters')
    if len(masses_da) != count or any(m <= 0 for m in masses_da):
        raise MalformedInput('positive masses required for every real atom')
    system = mm.System()
    final_masses = [None]*count
    for old, new in enumerate(old_to_new):
        final_masses[new] = masses_da[old]
    for mass in final_masses:
        system.addParticle(mass)
    harmonic_terms = ((selected, constants, centers),) + tuple(
        (tuple(indices), tuple(float(k) for k in ks), tuple(tuple(float(x) for x in row) for row in cs))
        for indices, ks, cs in additional_harmonics)
    for number, (indices, ks, cs) in enumerate(harmonic_terms):
        if not indices or len(set(indices)) != len(indices) or any(i not in range(count) for i in indices):
            raise IdentityError('invalid harmonic particle index/order')
        if len(indices) != len(ks) or len(indices) != len(cs) or any(len(row) != 3 for row in cs):
            raise MalformedInput('harmonic constants/centres must cover selected particles')
        if any(not np.isfinite(k) or k < 0 for k in ks) or any(not np.isfinite(x) for row in cs for x in row):
            raise NumericalDomainError('invalid harmonic parameters')
        force = mm.PythonForce(SelectedHarmonic(ks, cs))
        force.setParticles([old_to_new[i] for i in indices])
        force.setName('analytic:selected-harmonic' if number == 0 else f'analytic:harmonic:{number}')
        system.addForce(force)
    real_index = {a.atom_id: i for i, a in enumerate(topology.atoms)}
    pairs = tuple(tuple(p) for p in environment_pairs)
    for model_id, environment_id, k in pairs:
        if model_id not in ml_atom_ids or environment_id in ml_atom_ids or environment_id not in real_index:
            raise IdentityError('environment spring must join a real ML atom and a real MM atom')
        if not np.isfinite(k) or k <= 0:
            raise NumericalDomainError('environment spring requires positive finite k')
        coupling = mm.PythonForce(EnvironmentSpring(float(k)))
        coupling.setParticles([old_to_new[real_index[a]] for a in (model_id, environment_id)])
        coupling.setName(f'analytic:environment:{model_id}:{environment_id}')
        system.addForce(coupling)
    if marker_k:
        protein = next((a for m in topology.molecules if m.role == 'protein' for a in m.atom_ids), None)
        if protein is None:
            raise IdentityError('marker requires a real protein coordinate')
        marker = mm.CustomExternalForce('0.5*k*((x+0.3)^2+(y-0.2)^2+(z-0.1)^2)')
        marker.addPerParticleParameter('k')
        marker.addParticle(old_to_new[real_index[protein]], [marker_k])
        marker.setName('analytic:large-marker')
        system.addForce(marker)
    manifest = dict(contract_version=1, fixture_kind='analytic_substitute',
                    selected_particles=selected, spring_constants=constants, centers_nm=centers,
                    additional_harmonics=harmonic_terms[1:],
                    environment_pairs=pairs, marker_k=marker_k, periodicity='nonperiodic',
                    derivative_scope='all_real', model_dtype='float64')
    return seal_physical(system, topology, ml_atom_ids=ml_atom_ids, old_to_new=old_to_new, manifest=manifest)
