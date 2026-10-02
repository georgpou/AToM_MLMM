"""Hand-derived expectations. Never call a production callback/map/mixer here."""
import json
import math
from pathlib import Path

import numpy as np

from atm_mlmm.schema import (AtomIdentity, Bond, MobileGroup, MoleculeState,
                             RuntimeSpec, Snapshot, TopologyView)

FIXTURE = json.loads((Path(__file__).resolve().parents[1] /
                     'fixtures/analytic/transfer-v1.json').read_text())
REFERENCE = RuntimeSpec('Reference', 'double', (), .0005, 300., 'NVT')


def case(kind='abfe', *, environment=True, marker=0., old_to_new=None):
    from atm_mlmm.analytic import make_analytic_bundle
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols import abfe, rbfe
    from atm_mlmm.schema import RestraintSpec
    from atm_mlmm.schedule import linear_schedule
    ids = tuple(FIXTURE['real_ids'])
    topology = TopologyView(
        tuple(AtomIdentity(a, 'C', str(i), '1', '', a) for i, a in enumerate(ids)),
        (Bond('a1', 'a2'), Bond('b1', 'b2'), Bond('b1', 'b3')),
        (MoleculeState('A', ('a1', 'a2'), 'ligand', 0, 1),
         MoleculeState('B', ('b1', 'b2', 'b3'), 'ligand', 0, 1),
         MoleculeState('P', ('protein',), 'protein', 0, 1),
         MoleculeState('E', ('env',), 'environment', 0, 1)))
    groups = (MobileGroup('A-mobile', ('a1', 'a2'), ('ligand',), 'A'),)
    if kind == 'rbfe':
        groups += (MobileGroup('B-mobile', ('b1', 'b2', 'b3'), ('ligand',), 'B'),)
    protocol = (abfe if kind == 'abfe' else rbfe).make_protocol(groups, FIXTURE['displacement_nm'])
    physical = make_analytic_bundle(
        topology, ml_atom_ids=tuple(a for a in ids if a != 'env'),
        masses_da=FIXTURE['masses_da'], selected_particles=FIXTURE['selected_particles'],
        spring_constants=FIXTURE['spring_constants_kj_mol_nm2'], centers_nm=FIXTURE['centers_nm'],
        environment_pairs=(tuple(FIXTURE['environment_pair']),) if environment else (),
        additional_harmonics=(((3,6,5), (3.,5.,7.), ((.05,-.15,.2),(.2,.1,0.),(-.2,0.,.1))),),
        marker_k=marker, old_to_new=tuple(range(7)) if old_to_new is None else old_to_new)
    transfer = resolve_protocol(physical, protocol)
    schedule = linear_schedule((('initial', 0.), ('middle', .37), ('final', 1.)))
    restraints = RestraintSpec('outside-harmonic', ('env', 'protein'), 9., (.1, 0., 0.))
    snapshot = Snapshot(ids, FIXTURE['positions_nm'], None)
    return physical, transfer, schedule, restraints, snapshot


def mapped_positions(positions, kind, endpoint):
    # Explicit final maps from the fixture, not the resolver or real_to_final.
    result = np.array(positions, dtype=float, copy=True)
    if endpoint == 1:
        result += np.array(FIXTURE[kind + '_map1_nm'])
    return result


def physical_answer(positions, *, environment=True, marker=0.):
    positions = np.asarray(positions)
    forces = np.zeros((7, 3))
    energy = 0.
    for particle, k, center in ((2, 6., (.1, -.1, .2)), (0, 14., (-.2, .2, 0.)),
                                (3, 3., (.05,-.15,.2)), (6, 5., (.2,.1,0.)), (5, 7., (-.2,0.,.1))):
        for axis in range(3):
            difference = positions[particle, axis] - center[axis]
            energy += .5 * k * difference**2
            forces[particle, axis] -= k * difference
    if environment:
        for axis in range(3):
            difference = positions[2, axis] - positions[1, axis]
            energy += 5. * difference**2
            forces[2, axis] -= 10. * difference
            forces[1, axis] += 10. * difference
    if marker:
        for axis in range(3):
            difference = positions[4, axis] - (-.3, .2, .1)[axis]
            energy += .5 * marker * difference**2
            forces[4, axis] -= marker * difference
    return energy, forces


def outside_answer(positions):
    positions = np.asarray(positions)
    forces = np.zeros((7, 3))
    energy = 0.
    for particle in (1, 4):
        for axis in range(3):
            difference = positions[particle, axis] - (.1, 0., 0.)[axis]
            energy += 4.5 * difference**2
            forces[particle, axis] -= 9. * difference
    return energy, forces


def production_parameters(**changes):
    parameters = dict(Lambda1=.1, Lambda2=.8, Alpha=.7, Uh=2., W0=.3,
                      Umax=10., Ubcore=1., Acore=.25, Direction=1., UOffset=.2)
    parameters.update(changes)
    return parameters


def nonlinear_answer(u0, u1, parameters):
    p = parameters
    direction = p['Direction']
    raw = direction * (u1 - u0 - p['UOffset'])
    soft, derivative = raw, 1.
    if p['Acore'] != 0. and raw > p['Ubcore']:
        span = p['Umax'] - p['Ubcore']
        a = p['Acore']
        y = (raw - p['Ubcore']) / span
        z = 1. + 2.*y/a + 2.*(y/a)**2
        power = z**a
        soft = span*(power-1.)/(power+1.) + p['Ubcore']
        derivative = 2.*a*z**(a-1.)*(2./a + 4.*y/a**2)/(power+1.)**2
    diff = p['Lambda2'] - p['Lambda1']
    t = p['Alpha'] * (soft - p['Uh'])
    # Stable independently differentiated log(1+exp(-t)).
    logterm = max(0., -t) + math.log1p(math.exp(-abs(t)))
    sigmoid_minus = (1./(1.+math.exp(t)) if t >= 0 else
                     1. - 1./(1.+math.exp(-t)))
    bias = p['Lambda2']*soft + p['W0']
    if diff:
        bias += diff*logterm/p['Alpha']
    weight = (p['Lambda2'] - diff*sigmoid_minus) * derivative
    if direction > 0:
        return u0 + bias, (1.-weight, weight), soft
    return u1 + bias, (weight, 1.-weight), soft


def expected_linear(snapshot, kind, lam, *, environment=True, marker=0.):
    u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 0), environment=environment, marker=marker)
    u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 1), environment=environment, marker=marker)
    outside, fk = outside_answer(snapshot.positions_nm)
    return u0, u1, (1.-lam)*u0+lam*u1, outside, (1.-lam)*f0+lam*f1+fk


def check(evaluation, expected):
    from atm_mlmm.endpoints import check_reference
    return check_reference(evaluation, u0=expected[0], u1=expected[1],
                           expression=expected[2], outside=expected[3], forces=expected[4])


class BrokenEnvironmentSpring:
    """Isolated executable faults, never used by production builders."""
    def __init__(self, mode, frozen_nm):
        self.mode = mode
        self.frozen_nm = tuple(tuple(row) for row in frozen_nm)

    def __call__(self, state):
        from openmm import unit
        positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        if self.mode == 'stale-input':
            positions = np.asarray(self.frozen_nm)
        difference = positions[0]-positions[1]
        force = -10.*difference
        forces = np.array((force, -force))
        if self.mode == 'zero-MM-gradient':
            forces[1] = 0.
        if self.mode == 'factor-ten':
            forces *= 10.
        return 5.*float(np.dot(difference, difference)), forces
