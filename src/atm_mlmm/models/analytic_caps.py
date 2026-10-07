"""Weight-free analytic probe for zero/one/many-cap collection contracts.

This module is a derivative oracle fixture, not an admitted chemical model.
Each cap owns its cap-local and cap/environment terms; ligand and direct
environment terms live once at collection scope.
"""
from dataclasses import dataclass
import math

import numpy as np
import openmm as mm
from openmm import unit

from ..schema import IdentityError, MalformedInput, NumericalDomainError


def _identity(value, name):
    if not isinstance(value, str) or not value.strip():
        raise MalformedInput(f'{name} must be a nonempty identity')
    return value


def _vector(value, name):
    result = tuple(float(x) for x in value)
    if len(result) != 3 or not np.isfinite(result).all():
        raise MalformedInput(f'{name} must be a finite 3-vector')
    return result


def _constant(value, name):
    result = float(value)
    if not math.isfinite(result) or result < 0.:
        raise NumericalDomainError(f'{name} must be finite and nonnegative')
    return result


@dataclass(frozen=True)
class CapParameters:
    ml_parent_id: str
    mm_parent_id: str
    cap_k: float
    cap_center_nm: tuple[float, float, float]
    environment_id: str | None = None
    environment_k: float = 0.

    def __post_init__(self):
        _identity(self.ml_parent_id, 'ML cap parent')
        _identity(self.mm_parent_id, 'MM cap parent')
        if self.ml_parent_id == self.mm_parent_id:
            raise IdentityError('cap parents must be distinct')
        object.__setattr__(self, 'cap_k', _constant(self.cap_k, 'cap_k'))
        object.__setattr__(self, 'cap_center_nm', _vector(self.cap_center_nm, 'cap_center_nm'))
        object.__setattr__(self, 'environment_k', _constant(self.environment_k, 'environment_k'))
        if self.environment_id is not None:
            _identity(self.environment_id, 'cap environment')
        if self.environment_k and self.environment_id is None:
            raise MalformedInput('a cap environment identity is required for a nonzero environment_k')


@dataclass(frozen=True)
class LigandTerm:
    atom_id: str
    k: float
    center_nm: tuple[float, float, float]

    def __post_init__(self):
        _identity(self.atom_id, 'ligand term atom')
        object.__setattr__(self, 'k', _constant(self.k, 'ligand k'))
        object.__setattr__(self, 'center_nm', _vector(self.center_nm, 'ligand center'))


@dataclass(frozen=True)
class EnvironmentTerm:
    model_id: str
    environment_id: str
    k: float

    def __post_init__(self):
        _identity(self.model_id, 'environment term model atom')
        _identity(self.environment_id, 'environment term MM atom')
        if self.model_id == self.environment_id:
            raise IdentityError('environment term atoms must be distinct')
        object.__setattr__(self, 'k', _constant(self.k, 'environment term k'))
        if self.k == 0.:
            raise NumericalDomainError('environment term k must be positive')


@dataclass(frozen=True)
class CapCollectionProbe:
    """Explicit collection input for the analytic weight-free provider.

    Signature: ``CapCollectionProbe(cap_parameters, environment_terms=(),
    ligand_terms=())``.  All parameter records are per term, never broadcast
    implicitly over caps.
    """
    cap_parameters: tuple[CapParameters, ...]
    environment_terms: tuple[EnvironmentTerm, ...] = ()
    ligand_terms: tuple[LigandTerm, ...] = ()

    def __post_init__(self):
        caps = tuple(self.cap_parameters)
        environments = tuple(self.environment_terms)
        ligands = tuple(self.ligand_terms)
        if any(not isinstance(term, CapParameters) for term in caps):
            raise MalformedInput('cap_parameters must contain CapParameters records')
        if any(not isinstance(term, EnvironmentTerm) for term in environments):
            raise MalformedInput('environment_terms must contain EnvironmentTerm records')
        if any(not isinstance(term, LigandTerm) for term in ligands):
            raise MalformedInput('ligand_terms must contain LigandTerm records')
        edges = tuple((term.ml_parent_id, term.mm_parent_id) for term in caps)
        if len(set(edges)) != len(edges):
            raise IdentityError('duplicate per-edge cap parameters')
        if len({term.atom_id for term in ligands}) != len(ligands):
            raise IdentityError('duplicate collection ligand term owner')
        pairs = tuple((term.model_id, term.environment_id) for term in environments)
        if len(set(pairs)) != len(pairs):
            raise IdentityError('duplicate collection environment term owner')
        if not caps and not environments and not ligands:
            raise MalformedInput('collection probe needs at least one owned energy term')
        object.__setattr__(self, 'cap_parameters', caps)
        object.__setattr__(self, 'environment_terms', environments)
        object.__setattr__(self, 'ligand_terms', ligands)

    @property
    def environment_dependent(self):
        return any(term.environment_k for term in self.cap_parameters) or bool(self.environment_terms)


@dataclass(frozen=True)
class CapCollectionCallback:
    probe: CapCollectionProbe
    cap_indices: tuple[int, ...]
    cap_environment_indices: tuple[int | None, ...]
    environment_indices: tuple[tuple[int, int], ...]
    ligand_indices: tuple[int, ...]

    def __call__(self, state):
        positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        forces = np.zeros_like(positions, dtype=np.float64)
        energy = 0.
        for term, cap, environment in zip(
                self.probe.cap_parameters, self.cap_indices, self.cap_environment_indices):
            delta = positions[cap] - term.cap_center_nm
            energy += .5 * term.cap_k * float(np.dot(delta, delta))
            forces[cap] -= term.cap_k * delta
            if term.environment_k:
                delta = positions[cap] - positions[environment]
                energy += .5 * term.environment_k * float(np.dot(delta, delta))
                forces[cap] -= term.environment_k * delta
                forces[environment] += term.environment_k * delta
        for term, (model, environment) in zip(self.probe.environment_terms, self.environment_indices):
            delta = positions[model] - positions[environment]
            energy += .5 * term.k * float(np.dot(delta, delta))
            forces[model] -= term.k * delta
            forces[environment] += term.k * delta
        for term, atom in zip(self.probe.ligand_terms, self.ligand_indices):
            delta = positions[atom] - term.center_nm
            energy += .5 * term.k * float(np.dot(delta, delta))
            forces[atom] -= term.k * delta
        if not np.isfinite(energy) or not np.isfinite(forces).all():
            raise NumericalDomainError('nonfinite cap-collection model result')
        # Return raw cap forces. Native LocalCoordinatesSite projection owns
        # the parent transfer exactly once.
        return energy, forces


def collection_callback(probe, selected, system, particle_indices):
    """Resolve declared edges against actual sites by mapped parent identity."""
    selected = list(selected)
    inverse = {particle: atom_id for atom_id, particle in particle_indices.items()}
    actual = {}
    for cap in selected:
        if not system.isVirtualSite(cap):
            continue
        site = system.getVirtualSite(cap)
        if not isinstance(site, mm.LocalCoordinatesSite) or site.getNumParticles() != 2:
            raise IdentityError('collection probe received an unsupported native cap type')
        try:
            edge = tuple(inverse[site.getParticle(i)] for i in range(2))
        except KeyError as exc:
            raise IdentityError('collection cap parent is not a selected real identity') from exc
        if edge in actual:
            raise IdentityError(f'duplicate actual cap for parent edge {edge}')
        actual[edge] = cap
    declared = {(term.ml_parent_id, term.mm_parent_id) for term in probe.cap_parameters}
    if set(actual) != declared:
        raise IdentityError(f'analytic collection edge/site mismatch: {set(actual)} vs {declared}')
    cap_indices = tuple(selected.index(actual[(term.ml_parent_id, term.mm_parent_id)])
                        for term in probe.cap_parameters)
    required_environment_ids = [term.environment_id for term in probe.cap_parameters if term.environment_k]
    required_environment_ids.extend(term.environment_id for term in probe.environment_terms)
    for atom_id in required_environment_ids:
        if atom_id not in particle_indices:
            raise IdentityError(f'unknown MM environment atom in collection probe: {atom_id}')
        particle = particle_indices[atom_id]
        if particle not in selected:
            selected.append(particle)
    cap_environment_indices = tuple(
        selected.index(particle_indices[term.environment_id]) if term.environment_k else None
        for term in probe.cap_parameters
    )
    environment_indices = tuple((selected.index(particle_indices[term.model_id]),
                                  selected.index(particle_indices[term.environment_id]))
                                 for term in probe.environment_terms)
    ligand_indices = tuple(selected.index(particle_indices[term.atom_id])
                           for term in probe.ligand_terms)
    return CapCollectionCallback(probe, cap_indices, cap_environment_indices,
                                 environment_indices, ligand_indices), selected


def registered_potential(probe, *, particle_indices):
    from openmmml import MLPotential
    from openmmml.mlpotential import MLPotentialImpl, MLPotentialImplFactory

    class Impl(MLPotentialImpl):
        def getMLLongRange(self):
            return False

        def addForces(self, topology, system, atoms, forceGroup, **args):
            callback, selected = collection_callback(probe, atoms, system, particle_indices)
            force = mm.PythonForce(callback)
            force.setParticles(selected)
            force.setForceGroup(forceGroup)
            force.setName('analytic:cap-collection-probe-v2')
            system.addForce(force)

    class Factory(MLPotentialImplFactory):
        def createImpl(self, name, **args):
            return Impl()

    MLPotential.registerImplFactory('atm-mlmm-cap-collection-v2', Factory())
    return MLPotential('atm-mlmm-cap-collection-v2')
