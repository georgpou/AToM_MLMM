"""Known answers from independent quadrature and independent Gaussian draws."""
from dataclasses import replace
import math

import numpy as np
import pytest
from scipy.integrate import quad

from tests.unit.test_restraint_volume import thermodynamics
from tests.unit.test_schedule import records_for

RT = .00831446261815324*300.


def harmonic_records(seed=20261004, *, count=5000, repeats=1, common_offset=0., state_offsets=None):
    from atm_mlmm.schedule import production_schedule
    from tests.analytic_oracle import production_parameters
    lambdas = np.linspace(0., 1., 5)
    names = ('zero', 'q1', 'q2', 'q3', 'one')
    shifts = np.zeros(5) if state_offsets is None else np.array(state_offsets)
    schedule = production_schedule(tuple((name, production_parameters(
        Lambda1=lam, Lambda2=lam, Acore=0., Alpha=0., UOffset=0., W0=offset))
        for name, lam, offset in zip(names, lambdas, shifts)))
    rng = np.random.default_rng(seed)
    raw, states = [], []
    for name, lam, offset in zip(names, lambdas, shifts):
        xs = np.repeat(rng.normal(-lam*.2, math.sqrt(RT/150.), count), repeats)
        raw.extend((50*x*x+common_offset, 50*(x+.3)**2+common_offset, 25*x*x,
                    50*((1-lam)*x*x+lam*(x+.3)**2)+25*x*x+common_offset+offset) for x in xs)
        states.extend((name,)*len(xs))
    return records_for(schedule, states, raw, sampling_mode='correlated' if repeats > 1 else 'independent')


def test_estimators_covariance_and_offsets():
    from atm_mlmm.analysis import analyze, estimate_free_energies
    from atm_mlmm.schedule import reduced_potentials
    data = harmonic_records()
    reduced = reduced_potentials(data)
    counts = np.full(5, 5000)
    mbar = estimate_free_energies(reduced, counts, estimator='pymbar')
    uwham = estimate_free_energies(reduced, counts, estimator='atom_uwham')
    # The adapter refines the exact pinned UWHAM objective independently.
    np.testing.assert_allclose(uwham['free_energies_dimensionless'], mbar['free_energies_dimensionless'], atol=1.e-8, rtol=0)
    weights = np.array((-1., 0., 0., 0., 1.))
    mv = weights@mbar['covariance_dimensionless']@weights
    uv = weights@uwham['covariance_dimensionless']@weights
    assert uv == pytest.approx(mv, rel=1.e-7, abs=1.e-10)
    assert mbar['effective_samples'].min() > 100
    result = analyze(data, thermodynamics())
    assert abs(result.restrained_kj_mol-1.5) <= .1
    assert abs(result.restrained_kj_mol-1.5) <= 3*result.restrained_standard_error_kj_mol
    common = analyze(harmonic_records(common_offset=713.), thermodynamics())
    assert common.restrained_kj_mol == pytest.approx(result.restrained_kj_mol, abs=1.e-9)
    assert common.restrained_standard_error_kj_mol == pytest.approx(result.restrained_standard_error_kj_mol, abs=1.e-9)
    shifts = (.4, -.7, .2, 1.1, -.3)
    shifted = analyze(harmonic_records(state_offsets=shifts), thermodynamics())
    assert shifted.restrained_kj_mol == pytest.approx(result.restrained_kj_mol+shifts[-1]-shifts[0], abs=1.e-9)
    assert shifted.restrained_standard_error_kj_mol == pytest.approx(result.restrained_standard_error_kj_mol, abs=1.e-9)
    correlated = analyze(harmonic_records(count=2500, repeats=8), thermodynamics())
    assert correlated.diagnostics['retained_samples'] < correlated.diagnostics['input_samples']/2
    assert min(correlated.diagnostics['statistical_inefficiency'].values()) > 2.
    assert 'mean_error_is_not_replicate_spread' in correlated.diagnostics['limitations']
    naive = analyze(replace(harmonic_records(count=2500, repeats=8), sampling_mode='independent'), thermodynamics())
    assert correlated.restrained_standard_error_kj_mol > 1.5*naive.restrained_standard_error_kj_mol


def test_uwham_large_constant_state_offsets_are_a_gauge():
    from atm_mlmm.analysis import analyze
    original = analyze(harmonic_records(count=1000), thermodynamics(), estimator='atom_uwham')
    offsets = (2000., -1800., 713., -910., 1400.)
    shifted = analyze(harmonic_records(count=1000, state_offsets=offsets), thermodynamics(), estimator='atom_uwham')
    assert shifted.restrained_kj_mol == pytest.approx(original.restrained_kj_mol+offsets[-1]-offsets[0], abs=1.e-7)
    assert shifted.restrained_standard_error_kj_mol == pytest.approx(original.restrained_standard_error_kj_mol, abs=1.e-8)


def test_repeated_seed_harmonic_md(tmp_path):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('g08_known_answer', Path(__file__).resolve().parents[2]/'examples/g08_known_answer.py')
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    sample_harmonic_md = example.sample_harmonic_md
    from atm_mlmm.analysis import analyze
    values, errors = [], []
    for seed in (41, 73, 109):
        records = sample_harmonic_md(seed, frames=4000, stride=200, output=tmp_path/f'seed-{seed}')
        result = analyze(records, thermodynamics())
        values.append(result.restrained_kj_mol)
        errors.append(result.restrained_standard_error_kj_mol)
        assert abs(values[-1]-1.5) <= .1
        assert abs(values[-1]-1.5) <= 3*errors[-1]
        assert min(result.diagnostics['effective_samples']) >= 100
        assert (tmp_path/f'seed-{seed}'/'records.json').exists()
        # Same source history, last half retained separately; covariance is
        # conservatively bounded by sigma_full+sigma_half for this comparison.
        walker = np.asarray(records.walker_ids)
        retain = np.concatenate([np.flatnonzero(walker == w)[2000:] for w in dict.fromkeys(records.walker_ids)])
        names = ('sample_ids', 'sampled_state_ids', 'walker_ids', 'sequence_numbers',
                 'u0_raw_kJ_mol', 'u1_raw_kJ_mol', 'outside_energy_kJ_mol', 'observed_total_kJ_mol')
        last = replace(records, **{name: tuple(getattr(records, name)[i] for i in retain) for name in names})
        half = analyze(last, thermodynamics())
        assert abs(half.restrained_kj_mol-result.restrained_kj_mol) <= 3*(half.restrained_standard_error_kj_mol+errors[-1])
    # Independent-run mean uncertainty and replicate spread are distinct.
    mean_error = math.sqrt(sum(e*e for e in errors))/len(errors)
    spread = np.std(values, ddof=1)
    assert abs(np.mean(values)-1.5) <= .1
    assert abs(np.mean(values)-1.5) <= 3*mean_error
    assert spread < .2


def test_estimator_rejects_disconnected_support_and_missing_counts():
    from atm_mlmm.analysis import estimate_free_energies
    from atm_mlmm.schema import QualificationError
    for estimator in ('pymbar', 'atom_uwham'):
        with pytest.raises(QualificationError, match='sampled'):
            estimate_free_energies(np.zeros((2, 10)), (10, 0), estimator=estimator)
        reduced = np.array([[0.]*100+[10000.]*100, [10000.]*100+[0.]*100])
        with pytest.raises(QualificationError, match='support'):
            estimate_free_energies(reduced, (100, 100), estimator=estimator)


def test_harmonic_known_difference():
    from pymbar import MBAR
    from atm_mlmm.analysis import combine_free_energies
    for kr, expected in ((50., 1.5), (0., 0.)):
        k, d = 100., .3
        lambdas = np.linspace(0., 1., 11)
        curve = .5*lambdas*k*d*d-lambdas*lambdas*k*k*d*d/(2*(k+kr))
        partition = [quad(lambda x: math.exp(-(.5*k*((1-lam)*x*x+lam*(x+d)**2)+.5*kr*x*x)/RT),
                          -np.inf, np.inf, epsabs=1.e-12, epsrel=1.e-12)[0] for lam in lambdas]
        np.testing.assert_allclose(-RT*np.log(np.array(partition)/partition[0]), curve, atol=1.e-10, rtol=0)
        assert curve[-1] == pytest.approx(expected, abs=1.e-12)
        rng = np.random.default_rng(20261004)
        # Complete the square independently: precision k+kr, mean -lambda*k*d/(k+kr).
        samples = np.concatenate([rng.normal(-lam*k*d/(k+kr), math.sqrt(RT/(k+kr)), 4000) for lam in lambdas])
        potentials = np.array([(.5*k*((1-lam)*samples**2+lam*(samples+d)**2)+.5*kr*samples**2)/RT for lam in lambdas])
        mbar = MBAR(potentials, np.full(len(lambdas), 4000), relative_tolerance=1.e-12)
        stats = mbar.compute_free_energy_differences(return_theta=True)
        estimates = RT*stats['Delta_f'][0]
        errors = RT*stats['dDelta_f'][0]
        np.testing.assert_array_less(np.abs(estimates-curve), .1000000001)
        assert np.all(np.abs(estimates[1:]-curve[1:]) <= 3*errors[1:])
        spec = replace(thermodynamics(), endpoint_weights={'s0': -1., 's10': 1.},
                       endpoint_descriptions={'s0': 'unshifted', 's10': 'shifted'},
                       state_connections=tuple((f's{i}', f's{i+1}') for i in range(10)))
        ids = tuple(f's{i}' for i in range(11))
        covariance = RT**2*stats['Theta']
        result = combine_free_energies(ids, mbar.f_k*RT, covariance, spec)
        assert abs(result.restrained_kj_mol-expected) <= .1
        assert abs(result.restrained_kj_mol-expected) <= 3*result.restrained_standard_error_kj_mol
        reverse = combine_free_energies(ids, mbar.f_k*RT, covariance,
                                       replace(spec, endpoint_weights={'s0': 1., 's10': -1.}))
        assert reverse.restrained_kj_mol == -result.restrained_kj_mol
