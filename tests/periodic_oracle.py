"""Tiny fixed charged PME fixture and independent image/pair oracles."""
from dataclasses import replace
import hashlib
import itertools
import numpy as np
import openmm as mm
from openmm import unit

from tests.link_oracle import input_case, REFERENCE

BOX = ((3.2, 0., 0.), (0., 3.4, 0.), (0., 0., 3.6))
CAVITY = (0, 2, 3, 4)
LIGAND = (8, 9, 10, 11, 12)
ENVIRONMENT = (1, 5, 6, 7)
COULOMB = 138.93545764438198


def periodic_input():
    original, spec, snapshot = input_case()
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    system.setDefaultPeriodicBoxVectors(*BOX)
    nb = next(f for f in system.getForces() if isinstance(f, mm.NonbondedForce))
    nb.setNonbondedMethod(mm.NonbondedForce.PME)
    nb.setCutoffDistance(.9)
    nb.setUseSwitchingFunction(True)
    nb.setSwitchingDistance(.75)
    nb.setUseDispersionCorrection(False)
    nb.setEwaldErrorTolerance(1e-7)
    nb.setPMEParameters(4.4, 64, 64, 64)
    # Fixed nonneutral subsets, while keeping actual inherited bonded/exception
    # topology. Partial charges here are diagnostic data, not formal states.
    for i in range(13):
        _, sigma, epsilon = nb.getParticleParameters(i)
        nb.setParticleParameters(i, (i + 1) * .007, sigma, epsilon)
    for i in range(nb.getNumExceptions()):
        a, b, q, sigma, epsilon = nb.getExceptionParameters(i)
        if q.value_in_unit(unit.elementary_charge**2) != 0:
            q = .5 * (a + 1) * (b + 1) * .007**2
        if frozenset((a,b)) == frozenset((2,3)):
            q, epsilon = .0004, .025
        nb.setExceptionParameters(i, a, b, q, sigma, epsilon)
    xml = mm.XmlSerializer.serialize(system)
    return (replace(original, prepared_mm_artifact=xml,
                    prepared_mm_sha256=hashlib.sha256(xml.encode()).hexdigest(), box_nm=BOX),
            spec, replace(snapshot, box_nm=BOX))


def periodic_case(real_model=False):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.analytic_boundary import BoundaryProbe
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec, ModelSpec
    original, spec, snapshot = periodic_input()
    if real_model:
        from atm_mlmm.models.mace import model_spec
        model, probe = model_spec(), None
    else:
        model = ModelSpec('analytic-local', None, 'declared_relative_energy',
                          ('H', 'C'), 'neutral_singlet', 'local', 'float64')
        probe = BoundaryProbe(cap_k=0., ligand_k=0.)
    bundle = build_physical(original, resolve_partition(original.topology, spec), model,
                            EmbeddingSpec('mechanical', '1', 'protein_c_c', 'orthorhombic-pme-v1'),
                            probe=probe, cap_distance_nm=.117)
    return bundle, snapshot


def plain_periodic(system, positions, box=BOX):
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
    try:
        context.setPeriodicBoxVectors(*box)
        context.setPositions(positions)
        context.computeVirtualSites()
        state = context.getState(getEnergy=True, getForces=True)
        return (float(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),
                state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole / unit.nanometer))
    finally:
        del context, integrator


def enumerated_displacement(delta, box=BOX):
    # Exhaustive image answer; never calls the production minimum-image helper.
    d = np.asarray(delta)
    lengths = np.diag(box)
    center = -np.floor(d / lengths).astype(int)
    candidates = [(d + (center + shift) * lengths, center + shift)
                  for shift in itertools.product((-1, 0, 1), repeat=3)]
    return min(candidates, key=lambda p: np.dot(p[0], p[0]))


def direct_lj_cross(nb, positions, first, second, box=BOX):
    exceptions = {frozenset((a, b)): (float(s.value_in_unit(unit.nanometer)),
                                    float(e.value_in_unit(unit.kilojoule_per_mole)))
                  for a, b, _, s, e in (nb.getExceptionParameters(i) for i in range(nb.getNumExceptions()))}
    value = 0.
    for a in first:
        for b in second:
            d = enumerated_displacement(np.asarray(positions)[b] - positions[a], box)[0]
            r = np.linalg.norm(d)
            key = frozenset((a, b))
            if key in exceptions:
                sigma, epsilon = exceptions[key]
                switch = 1.
            else:
                _, s1, e1 = nb.getParticleParameters(a)
                _, s2, e2 = nb.getParticleParameters(b)
                sigma = .5 * (s1 + s2).value_in_unit(unit.nanometer)
                epsilon = np.sqrt((e1 * e2).value_in_unit(unit.kilojoule_per_mole**2))
                if r >= nb.getCutoffDistance().value_in_unit(unit.nanometer):
                    continue
                switch = 1.
                if nb.getUseSwitchingFunction():
                    rs = nb.getSwitchingDistance().value_in_unit(unit.nanometer)
                    if r > rs:
                        t = (r-rs)/(nb.getCutoffDistance().value_in_unit(unit.nanometer)-rs)
                        switch = 1 - 10*t**3 + 15*t**4 - 6*t**5
            value += switch * 4 * epsilon * ((sigma/r)**12 - (sigma/r)**6)
    return value


def ewald_energy(charges, positions, box, alpha, *, background=True):
    """Independent converged lattice Ewald with self/background; no PME APIs."""
    from math import erfc
    q, x, lengths = np.asarray(charges), np.asarray(positions), np.diag(box)
    volume = np.prod(lengths)
    real = 0.
    for i in range(len(q)):
        for j in range(len(q)):
            for shift in itertools.product(range(-2, 3), repeat=3):
                if i == j and shift == (0, 0, 0):
                    continue
                r = np.linalg.norm(x[j] - x[i] + lengths*np.asarray(shift))
                real += .5*q[i]*q[j]*erfc(alpha*r)/r
    ns = np.asarray(list(itertools.product(range(-25, 26), repeat=3)))
    ns = ns[np.any(ns != 0, axis=1)]
    k = 2*np.pi*ns/lengths
    k2 = np.sum(k*k, axis=1)
    structure = np.exp(1j * (k @ x.T)) @ q
    reciprocal = 2*np.pi/volume*np.sum(np.exp(-k2/(4*alpha**2))/k2*np.abs(structure)**2)
    self_term = -alpha/np.sqrt(np.pi)*np.dot(q, q)
    bg = -np.pi*np.sum(q)**2/(2*alpha**2*volume) if background else 0.
    return COULOMB*(real + reciprocal + self_term + bg)
