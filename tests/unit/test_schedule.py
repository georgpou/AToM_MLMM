"""Exact saved-raw reconstruction and deliberately unequal directional midpoints."""
from dataclasses import replace
import math

import numpy as np
import pytest
from scipy.integrate import quad

from tests.analytic_oracle import REFERENCE, case, production_parameters

RT = .00831446261815324*300.


def records_for(schedule, state_ids, raw, *, sampling_mode='independent'):
    from atm_mlmm.schema import EvaluationRecords
    return EvaluationRecords(schedule, tuple(f'fixture-{i}' for i in range(len(raw))), tuple(state_ids),
                             tuple(f'walker-{s}' for s in state_ids), tuple(range(len(raw))),
                             tuple(r[0] for r in raw), tuple(r[1] for r in raw), tuple(r[2] for r in raw),
                             tuple(r[3] for r in raw), 'physical-fixture', 'transfer-fixture', 'restraint-fixture',
                             {'fixture': 'independent explicit test values'}, sampling_mode)


def test_reduced_energies_match_context():
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.schedule import production_schedule, reduced_potentials
    physical, transfer, _, restraints, snapshot = case('rbfe')
    states = tuple((f's{i}', production_parameters(Direction=direction, Lambda1=l1, Lambda2=l2,
                                                    W0=offset, UOffset=.8))
                   for i, (direction, l1, l2, offset) in enumerate(((1., 0., 0., .3), (1., .1, .8, -.4),
                                                                   (1., .5, .5, .2), (-1., .1, .8, .6),
                                                                   (-1., .5, .5, -.1), (-1., 0., 0., .9))))
    schedule = production_schedule(states)
    frames = [replace(snapshot, positions_nm=np.array(snapshot.positions_nm)+shift) for shift in (0., .11, -.23)]
    observed = []
    with AtmEvaluator(build_atm(physical, transfer, schedule, restraints), REFERENCE) as evaluator:
        for frame in frames:
            observed.append([evaluator.evaluate(frame, state.state_id) for state in schedule.states])
    raw = [(row[0].raw.u0_raw_kJ_mol, row[0].raw.u1_raw_kJ_mol, row[0].raw.outside_energy_kJ_mol,
            row[0].raw.system_total_energy_kJ_mol) for row in observed]
    records = records_for(schedule, (states[0][0],)*len(raw), raw)
    actual = reduced_potentials(records)*RT
    expected = np.array([[row[i].total.energy_kj_mol for row in observed] for i in range(len(states))])
    np.testing.assert_allclose(actual, expected, atol=1.e-8, rtol=0)
    # A saved scope/unit defect must be rejected, not compensated by an estimator.
    with pytest.raises(ValueError, match='observed'):
        reduced_potentials(replace(records, outside_energy_kJ_mol=tuple(2*x for x in records.outside_energy_kJ_mol)))


def test_active_midpoint_difference_requires_bridge(tmp_path):
    from atm_mlmm.analysis import directional_difference
    from atm_mlmm.schedule import production_schedule, reduced_potentials
    # The common fixed soft-core parameters still produce unequal directional middles.
    # The endpoint states have lambda=0 in their respective directions.
    pars = [production_parameters(Direction=direction, Lambda1=lam, Lambda2=lam, W0=0., UOffset=0.,
                                  Ubcore=1., Umax=10., Acore=.25)
            for direction, lam in ((1., 0.), (1., .5), (-1., .5), (-1., 0.))]
    schedule = production_schedule(tuple(zip(('e0', 'm+', 'm-', 'e1'), pars)))

    def independent_energy(x, p):
        u0, u1, outside = 50*x*x, 50*(x+.3)**2, 25*x*x
        delta = p['Direction']*(u1-u0)
        if delta > 1.:
            y = (delta-1.)/9.
            power = (1+2*y/.25+2*(y/.25)**2)**.25
            delta = 1.+9.*(power-1.)/(power+1.)
        return outside+(u0 if p['Direction'] > 0 else u1)+p['Lambda2']*delta

    xs = np.array([-.8, -.2, .1, .7])
    raw = [(50*x*x, 50*(x+.3)**2, 25*x*x, 75*x*x) for x in xs]
    actual = reduced_potentials(records_for(schedule, ('e0',)*len(raw), raw))*RT
    expected = np.array([[independent_energy(x, p) for x in xs] for p in pars])
    np.testing.assert_allclose(actual, expected, atol=1.e-10, rtol=0)
    assert np.max(np.abs(actual[1]-actual[2])) > .1
    partition = [quad(lambda x: math.exp(-independent_energy(x, p)/RT), -np.inf, np.inf,
                      epsabs=1.e-11, epsrel=1.e-11, limit=200)[0] for p in pars]
    free = -RT*np.log(partition)
    d0, d1, bridge = free[1]-free[0], free[2]-free[3], free[2]-free[1]
    assert abs(bridge) > .01
    assert abs(d1-d0+1.5) > .01
    assert abs(d1-d0+bridge+1.5) > .01
    value, error = directional_difference(d0, d1, bridge, np.array([[.09, .08, .01], [.08, .16, .02], [.01, .02, .04]]))
    assert value == pytest.approx(-1.5, abs=1.e-8)
    assert error == pytest.approx(math.sqrt(.11))
    with pytest.raises(ValueError, match='bridge'):
        directional_difference(d0, d1, None, np.eye(3))
    # Independent numerical inverse-CDF samples of all four potentials include
    # both midpoint ensembles. Cross-evaluate both expressions on both ensembles.
    from scipy.integrate import cumulative_trapezoid
    from atm_mlmm.analysis import analyze, estimate_free_energies
    from atm_mlmm.schema import to_json
    from tests.unit.test_restraint_volume import thermodynamics
    grid = np.linspace(-2., 2., 40001)
    rng = np.random.default_rng(20261004)
    raw, state_ids, sampled_x = [], [], []
    for state, p in zip(schedule.states, pars):
        density = np.exp(-np.array([independent_energy(x, p) for x in grid])/RT)
        cumulative = cumulative_trapezoid(density, grid, initial=0.)
        xs = np.interp(rng.uniform(size=5000), cumulative/cumulative[-1], grid)
        sampled_x.extend(xs)
        state_ids.extend((state.state_id,)*len(xs))
        raw.extend((50*x*x, 50*(x+.3)**2, 25*x*x, independent_energy(x, p)) for x in xs)
    sampled = records_for(schedule, state_ids, raw)
    (tmp_path/'unequal-midpoint-records.json').write_text(to_json(sampled)+'\n')
    np.savez_compressed(tmp_path/'unequal-midpoint-frames.npz', x_nm=sampled_x,
                        midpoint_cross_reduced=reduced_potentials(sampled)[1:3, 5000:15000])
    spec = replace(thermodynamics(), endpoint_weights={'e0': 1., 'e1': -1.},
                   endpoint_descriptions={'e0': 'physical endpoint zero', 'e1': 'physical endpoint one'},
                   state_connections=(('e0', 'm+'), ('m+', 'm-'), ('m-', 'e1')))
    result = analyze(sampled, spec)
    assert abs(result.restrained_kj_mol+1.5) <= .1
    assert abs(result.restrained_kj_mol+1.5) <= 3*result.restrained_standard_error_kj_mol
    assert min(result.diagnostics['effective_samples']) > 100
    fit = estimate_free_energies(reduced_potentials(sampled), (5000,)*4)
    bridge_weights = np.array((0., -1., 1., 0.))
    estimated_bridge = float(bridge_weights@fit['free_energies_dimensionless'])*RT
    bridge_error = math.sqrt(float(bridge_weights@fit['covariance_dimensionless']@bridge_weights))*RT
    assert abs(estimated_bridge-bridge) <= 3*bridge_error


def test_raw_records_reject_lost_identity_duplicate_samples_and_nonfinite():
    from atm_mlmm.schedule import linear_schedule, reduced_potentials
    schedule = linear_schedule((('a', 0.), ('b', 1.)))
    records = records_for(schedule, ('a', 'b'), ((1., 2., 3., 4.), (2., 3., 4., 7.)))
    for change in ({'sample_ids': ('duplicate', 'duplicate')}, {'sampled_state_ids': ('a', 'unknown')},
                   {'physical_identity': ''}, {'u0_raw_kJ_mol': (float('nan'), 2.)},
                   {'sequence_numbers': (-1, 1)}, {'sampling_mode': 'unspecified'}):
        with pytest.raises(ValueError):
            replace(records, **change)
    np.testing.assert_allclose(reduced_potentials(records)*RT, ((4., 6.), (5., 7.)), atol=1.e-12)
