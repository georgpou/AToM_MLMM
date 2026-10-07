"""Registered weight-free OpenMM-ML substitute returning raw model derivatives."""
from dataclasses import dataclass
import numpy as np
import openmm as mm
from openmm import unit

from ..schema import IdentityError, MalformedInput, NumericalDomainError


@dataclass(frozen=True)
class BoundaryProbe:
    cap_k: float = 7.
    cap_center_nm: tuple = (.13, -.08, .11)
    pair_k: float = 0.
    partner_id: str = 'l8'
    environment_k: float = 0.
    environment_id: str = 'p5'
    ligand_k: float = 5.
    ligand_center_nm: tuple = (.02, .3, -.07)

    def __post_init__(self):
        for name in ('cap_center_nm', 'ligand_center_nm'):
            value = tuple(float(x) for x in getattr(self, name))
            if len(value) != 3 or not np.isfinite(value).all():
                raise MalformedInput('probe centers must be finite 3-vectors')
            object.__setattr__(self, name, value)
        if any(not np.isfinite(k) or k < 0 for k in (self.cap_k, self.pair_k, self.environment_k, self.ligand_k)):
            raise NumericalDomainError('invalid boundary spring constant')


@dataclass(frozen=True)
class BoundaryCallback:
    probe: BoundaryProbe
    cap_index: int
    partner_index: int | None
    environment_index: int | None

    def __call__(self, state):
        r = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        p = self.probe
        f = np.zeros_like(r, dtype=np.float64)
        delta = r[self.cap_index]-p.cap_center_nm
        energy = float(.5*p.cap_k*np.dot(delta, delta))
        f[self.cap_index] -= p.cap_k*delta
        for partner, k in ((self.partner_index, p.pair_k), (self.environment_index, p.environment_k)):
            if k:
                delta = r[self.cap_index]-r[partner]
                energy += float(.5*k*np.dot(delta, delta))
                f[self.cap_index] -= k*delta
                f[partner] += k*delta
        if p.ligand_k:
            delta = r[self.partner_index]-p.ligand_center_nm
            energy += float(.5*p.ligand_k*np.dot(delta, delta))
            f[self.partner_index] -= p.ligand_k*delta
        if not np.isfinite(energy) or not np.isfinite(f).all():
            raise NumericalDomainError('nonfinite cap model result')
        # Return the raw cap slot. Native virtual-site machinery projects once.
        return energy, f


def registered_potential(probe, *, partner_particle, environment_particle):
    from openmmml.mlpotential import MLPotential, MLPotentialImpl, MLPotentialImplFactory

    class Impl(MLPotentialImpl):
        def getMLLongRange(self):
            return False

        def addForces(self, topology, system, atoms, forceGroup, **args):
            selected = list(atoms)
            caps = [i for i in selected if system.isVirtualSite(i)]
            if len(caps) != 1:
                raise IdentityError('analytic boundary probe requires exactly one cap')
            partner = None
            if probe.pair_k or probe.ligand_k:
                if partner_particle not in selected:
                    raise IdentityError('cap pair/ligand spring requires a model partner')
                partner = selected.index(partner_particle)
            environment = None
            if probe.environment_k:
                if environment_particle in selected or environment_particle is None:
                    raise IdentityError('environment spring requires a real MM coordinate')
                selected.append(environment_particle)
                environment = len(selected)-1
            callback = BoundaryCallback(probe, selected.index(caps[0]), partner, environment)
            force = mm.PythonForce(callback)
            force.setParticles(selected)
            force.setForceGroup(forceGroup)
            force.setName('analytic:boundary-probe')
            system.addForce(force)

    class Factory(MLPotentialImplFactory):
        def createImpl(self, name, **args):
            return Impl()

    # The factory is immediately consumed. Serialized callbacks are importable
    # module-level objects and never depend on this transient registration.
    MLPotential.registerImplFactory('atm-mlmm-boundary-analytic-v1', Factory())
    return MLPotential('atm-mlmm-boundary-analytic-v1')
