"""Opt-in exchange analysis preserves synchronized walker/state bundles."""

from dataclasses import replace
import json
import math
from pathlib import Path

import numpy as np
import pytest


def make_synthetic_history(tmp_path, run_number, *, seed, frames=32, rho=.5,
                           shared_fraction=.5, restraint_k=50., sampling_mode='correlated',
                           run_prefix='synthetic'):
    """Generate explicit synthetic frame groups; this is not a scheduler trace."""
    from atm_mlmm.schedule import linear_schedule
    from atm_mlmm.schema import EvaluationRecords

    state_ids = ('endpoint-A-id', 'endpoint-B-id')
    schedule = linear_schedule(((state_ids[0], 0.), (state_ids[1], 1.)))
    rng = np.random.default_rng(seed)
    common = rng.normal(size=frames)
    independent = rng.normal(size=(frames, 2))
    residual = np.empty((frames, 2))
    if frames:
        residual[0] = np.sqrt(1.-shared_fraction)*independent[0] + np.sqrt(shared_fraction)*common[0]
    innovation_scale = np.sqrt(1.-rho*rho)
    for frame in range(1, frames):
        innovation = (np.sqrt(1.-shared_fraction)*independent[frame]
                      + np.sqrt(shared_fraction)*common[frame])
        residual[frame] = rho*residual[frame-1] + innovation_scale*innovation

    run_id = f'{run_prefix}-run-{run_number}'
    sigma = np.sqrt(.00831446261815324*300./(100.+restraint_k))
    sample_ids, sampled_states, walkers, sequences = [], [], [], []
    u0s, u1s, outs, totals = [], [], [], []
    grouped_ids = []
    for frame in range(frames):
        frame_ids = []
        for walker in range(2):
            state_index = (walker+frame) % 2
            lam = float(state_index)
            mean = -lam*100.*.3/(100.+restraint_k)
            x = mean + sigma*residual[frame, walker]
            u0, u1 = .5*100.*x*x, .5*100.*(x+.3)**2
            outside = .5*restraint_k*x*x
            total = (u0+lam*(u1-u0))+outside
            sample_id = f'{run_id}:walker-{walker}:boundary-{frame+1}'
            sample_ids.append(sample_id)
            sampled_states.append(state_ids[state_index])
            walkers.append(f'walker-{walker}')
            sequences.append(frame+1)
            u0s.append(u0)
            u1s.append(u1)
            outs.append(outside)
            totals.append(total)
            frame_ids.append(sample_id)
        grouped_ids.append(tuple(frame_ids))

    records = EvaluationRecords(
        schedule, tuple(sample_ids), tuple(sampled_states), tuple(walkers), tuple(sequences),
        tuple(u0s), tuple(u1s), tuple(outs), tuple(totals),
        f'analytic-harmonic-k{restraint_k:g}', 'fixed-whole-coordinate-transfer',
        f'harmonic-outside-k{restraint_k:g}',
        {'run_id': run_id, 'profile': 'synthetic analytic control', 'seed': str(seed)},
        sampling_mode)
    evidence = Path(tmp_path)/f'{run_id}-retained-window.json'
    document = {
        'format': 'exchange-retained-window-v1', 'version': 1,
        'source_kind': 'synthetic', 'run_id': run_id,
        'records_identity': records.content_identity,
        'schedule_identity': schedule.content_identity,
        'physical_identity': records.physical_identity,
        'transfer_identity': records.transfer_identity,
        'restraint_identity': records.restraint_identity,
        'source_frames': [list(row) for row in grouped_ids],
        'retained_frames': [list(row) for row in grouped_ids],
        'excluded_frames': [],
        'selection_evidence': 'synthetic fixture predeclares every generated synchronized frame',
        'independent_initialization_evidence': f'numpy.default_rng independent seed {seed}',
        'synthetic_warning': 'not a persistent journal, scheduler mixing, or convergence evidence'
    }
    evidence.write_text(json.dumps(document, sort_keys=True)+'\n')
    from atm_mlmm.schema import ExchangeAnalysisInput
    return ExchangeAnalysisInput(records, tuple(grouped_ids), run_id, str(evidence))


def sampled_harmonic_statistics(histories, *, restraint_k=50.):
    rt = .00831446261815324*300.
    expected_variance = rt/(100.+restraint_k)
    expected_means = {'endpoint-A-id': 0.,
                      'endpoint-B-id': -.3*100./(100.+restraint_k)}
    state_values = {state: [] for state in expected_means}
    lag_pairs = []
    cross_pairs = []
    for history in histories:
        records = history.records
        # u1-u0=30*x+4.5 for the independently specified S05 harmonic model.
        x = (np.asarray(records.u1_raw_kJ_mol)-np.asarray(records.u0_raw_kJ_mol)-4.5)/30.
        residual = np.empty(len(x))
        for i, state in enumerate(records.sampled_state_ids):
            state_values[state].append(float(x[i]))
            residual[i] = (x[i]-expected_means[state])/np.sqrt(expected_variance)
        for walker in dict.fromkeys(records.walker_ids):
            indices = sorted((i for i, value in enumerate(records.walker_ids) if value == walker),
                             key=lambda i: records.sequence_numbers[i])
            lag_pairs.extend(zip(residual[np.asarray(indices[:-1])], residual[np.asarray(indices[1:])]))
        by_sequence = {}
        for i, sequence in enumerate(records.sequence_numbers):
            by_sequence.setdefault(sequence, {})[records.walker_ids[i]] = residual[i]
        cross_pairs.extend((row['walker-0'], row['walker-1']) for row in by_sequence.values())
    moments = {state: {'mean_nm': float(np.mean(values)),
                       'variance_nm2': float(np.var(values, ddof=1))}
               for state, values in state_values.items()}
    lag = float(np.corrcoef(np.asarray(lag_pairs).T)[0, 1])
    cross = float(np.corrcoef(np.asarray(cross_pairs).T)[0, 1])
    return moments, lag, cross, expected_variance, expected_means


def restrained_spec():
    from atm_mlmm.schema import ThermodynamicSpec
    return ThermodynamicSpec(
        'restrained_free_energy',
        {'endpoint-B-id': 1., 'endpoint-A-id': -1.},
        'endpoint_difference', (('endpoint-A-id', 'endpoint-B-id'),),
        {'endpoint-A-id': 'harmonic endpoint lambda zero',
         'endpoint-B-id': 'harmonic endpoint lambda one'},
        (), (), None, 'one-dimensional analytic harmonic domain',
        'outside harmonic restraint retained in every state',
        'translation only', 'single Gaussian state per endpoint')


def test_exchange_analysis_api_is_explicit_and_opt_in(tmp_path):
    from atm_mlmm.exchange_analysis import (ExchangeAnalysisInput,
                                            ExchangeResamplingSpec,
                                            analyze_exchange)
    from atm_mlmm.schema import from_json, to_json

    assert ExchangeAnalysisInput is not None
    assert ExchangeResamplingSpec is not None
    assert analyze_exchange.__name__ == 'analyze_exchange'
    history = make_synthetic_history(tmp_path, 0, seed=104729, frames=8)
    assert from_json(to_json(history)) == history


def test_synchronized_bootstrap_keeps_frame_bundles_and_reports_information_scopes(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange

    history = make_synthetic_history(tmp_path, 0, seed=104729, frames=32)
    design = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 91,
                                    'fixtures/analytic/exchange-analysis-v1/design.json')
    result = analyze_exchange((history,), restrained_spec(), resampling=design)
    diagnostics = result.diagnostics
    assert diagnostics['resampling_method'] == 'synchronized_blocks'
    assert diagnostics['block_length_frames'] == 8
    assert diagnostics['bootstrap_replicates'] == 8
    assert len(diagnostics['raw_sample_ids']) == 64
    assert diagnostics['retained_sample_ids'] == diagnostics['raw_sample_ids']
    assert diagnostics['excluded_sample_ids'] == ()
    assert len(diagnostics['bootstrap_draws'][0]['selected_block_indices_by_run']['synthetic-run-0']) == 4
    assert diagnostics['iid_weight_effective_contributions']
    assert diagnostics['correlation_adjusted_information']['units'] == 'resampled time blocks'
    assert diagnostics['sampling_standard_error_kj_mol'] == pytest.approx(
        result.restrained_standard_error_kj_mol)
    assert 'across_run_estimate_spread_kj_mol' in diagnostics
    assert diagnostics['last_half_estimate_kj_mol'] is not None
    assert 'not independent' in diagnostics['full_last_half_warning']


def test_excluded_frames_remain_in_raw_provenance_but_not_retained_window(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import ExchangeAnalysisInput

    history = make_synthetic_history(tmp_path, 0, seed=303091, frames=64)
    evidence_path = Path(history.retained_window_evidence)
    document = json.loads(evidence_path.read_text())
    source = document['source_frames']
    document['retained_frames'] = source[16:48]
    document['excluded_frames'] = source[:16]+source[48:]
    evidence_path.write_text(json.dumps(document, sort_keys=True)+'\n')
    selected = ExchangeAnalysisInput(history.records,
        tuple(tuple(frame) for frame in document['retained_frames']), history.run_id,
        history.retained_window_evidence)
    spec = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 98,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    result = analyze_exchange((selected,), restrained_spec(), resampling=spec)
    assert len(result.diagnostics['raw_sample_ids']) == 128
    assert len(result.diagnostics['retained_sample_ids']) == 64
    assert len(result.diagnostics['excluded_sample_ids']) == 64


def test_mislabeled_iid_histories_and_reused_initializations_are_rejected(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import IdentityError, QualificationError

    iid = make_synthetic_history(tmp_path, 0, seed=327673, frames=32,
                                 rho=0., shared_fraction=0., sampling_mode='independent')
    spec = ExchangeResamplingSpec('independent_runs', None, 8, 99,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    with pytest.raises(QualificationError, match='correlated'):
        analyze_exchange((iid, make_synthetic_history(tmp_path, 1, seed=352057, frames=32)),
                         restrained_spec(), resampling=spec)

    first = make_synthetic_history(tmp_path, 2, seed=254347, frames=32)
    second = make_synthetic_history(tmp_path, 3, seed=278933, frames=32)
    first_doc = json.loads(Path(first.retained_window_evidence).read_text())
    second_doc = json.loads(Path(second.retained_window_evidence).read_text())
    second_doc['independent_initialization_evidence'] = first_doc['independent_initialization_evidence']
    Path(second.retained_window_evidence).write_text(json.dumps(second_doc, sort_keys=True)+'\n')
    with pytest.raises(IdentityError, match='initialization'):
        analyze_exchange((first, second), restrained_spec(), resampling=spec)


def test_synchronized_input_must_match_verified_frame_order(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import ExchangeAnalysisInput, IdentityError

    history = make_synthetic_history(tmp_path, 0, seed=130363, frames=32)
    detached = tuple(tuple(reversed(frame)) for frame in history.synchronized_frames)
    corrupted = ExchangeAnalysisInput(history.records, detached, history.run_id,
                                      history.retained_window_evidence)
    spec = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 92,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    with pytest.raises(IdentityError, match='frame|provenance|bundle'):
        analyze_exchange((corrupted,), restrained_spec(), resampling=spec)


def test_raw_outside_energy_is_validated_before_window_selection(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import IdentityError

    history = make_synthetic_history(tmp_path, 0, seed=155921, frames=32)
    # Keep the observed total from the complete source while dropping its
    # nonzero outside term. Reconstruction must fail before resampling.
    corrupted = replace(history.records,
                        outside_energy_kJ_mol=(0.,)*len(history.records.sample_ids))
    from atm_mlmm.schema import ExchangeAnalysisInput
    bad = ExchangeAnalysisInput(corrupted, history.synchronized_frames,
                                history.run_id, history.retained_window_evidence)
    spec = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 93,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    with pytest.raises(IdentityError, match='observed|reconstruction'):
        analyze_exchange((bad,), restrained_spec(), resampling=spec)


def test_partial_block_tail_is_rejected_instead_of_dropped(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import QualificationError

    history = make_synthetic_history(tmp_path, 0, seed=181081, frames=30)
    spec = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 94,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    with pytest.raises(QualificationError, match='divisible|partial|block'):
        analyze_exchange((history,), restrained_spec(), resampling=spec)


def test_independent_run_resampling_keeps_complete_runs_without_nested_blocks(tmp_path):
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schema import QualificationError

    first = make_synthetic_history(tmp_path, 0, seed=205759, frames=32)
    second = make_synthetic_history(tmp_path, 1, seed=230003, frames=32)
    spec = ExchangeResamplingSpec('independent_runs', None, 8, 95,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    result = analyze_exchange((first, second), restrained_spec(), resampling=spec)
    diagnostics = result.diagnostics
    assert diagnostics['resampling_method'] == 'independent_runs'
    assert diagnostics['block_length_frames'] is None
    assert diagnostics['correlation_adjusted_information']['units'] == 'complete independent runs'
    assert diagnostics['correlation_adjusted_information']['count'] == 2
    assert len(diagnostics['bootstrap_draws'][0]['selected_run_ids']) == 2
    with pytest.raises(QualificationError, match='independent runs|two|run'):
        analyze_exchange((first,), restrained_spec(), resampling=spec)


def test_failed_bootstrap_draw_is_preserved_and_withholds_covariance(tmp_path, monkeypatch):
    import atm_mlmm.exchange_analysis as module
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec
    from atm_mlmm.schema import QualificationError

    first = make_synthetic_history(tmp_path, 0, seed=254347, frames=32)
    second = make_synthetic_history(tmp_path, 1, seed=278933, frames=32)
    original = module.estimate_free_energies
    calls = {'n': 0}

    def fail_second_draw(reduced, counts, *, estimator='pymbar'):
        calls['n'] += 1
        if calls['n'] == 5:  # pooled fit, two run fits, then draw 1 and draw 2
            raise QualificationError('injected disconnected synthetic draw')
        return original(reduced, counts, estimator=estimator)

    monkeypatch.setattr(module, 'estimate_free_energies', fail_second_draw)
    spec = ExchangeResamplingSpec('synchronized_blocks', 8, 8, 96,
                                  'fixtures/analytic/exchange-analysis-v1/design.json')
    with pytest.raises(QualificationError, match='bootstrap draw') as caught:
        module.analyze_exchange((first, second), restrained_spec(), resampling=spec)
    failures = caught.value.failed_draws
    assert failures and failures[0]['draw_index'] == 1
    assert failures[0]['reason'] == 'injected disconnected synthetic draw'
    assert failures[0]['selected_sample_ids_sha256']
    assert failures[0]['selected_block_indices_by_run']


@pytest.mark.slow
def test_frozen_analytic_seed_design_qualifies_known_answer_and_covariance(tmp_path):
    """Bounded 12-seed synthetic control; never evidence of molecular mixing."""
    from atm_mlmm.analysis import estimate_free_energies
    from atm_mlmm.exchange_analysis import ExchangeResamplingSpec, analyze_exchange
    from atm_mlmm.schedule import reduced_potentials

    fixture = Path(__file__).resolve().parents[2]/'fixtures/analytic/exchange-analysis-v1'
    design = json.loads((fixture/'design.json').read_text())
    seeds = json.loads((fixture/'seeds.json').read_text())['seeds']
    assert len(seeds) == design['runs'] == 12
    assert design['synchronized_frames_per_run'] == 4096
    assert design['resampling']['synchronized_blocks_length_frames'] == 32
    assert design['resampling']['bootstrap_replicates'] == 64
    correlated = tuple(make_synthetic_history(
        tmp_path, index, seed=seed, frames=design['synchronized_frames_per_run'],
        rho=design['correlated_gaussian_control']['temporal_ar1_rho'],
        shared_fraction=design['correlated_gaussian_control']['shared_innovation_variance_fraction'],
        run_prefix='correlated')
        for index, seed in enumerate(seeds))
    independent = tuple(make_synthetic_history(
        tmp_path, index, seed=seed, frames=design['synchronized_frames_per_run'],
        rho=design['independent_analytic_baseline']['temporal_ar1_rho'],
        shared_fraction=design['independent_analytic_baseline']['shared_innovation_variance_fraction'],
        run_prefix='independent')
        for index, seed in enumerate(seeds))
    first = correlated[0].records
    first_frame, second_frame = correlated[0].synchronized_frames[:2]
    frame_index = {sample_id: index for index, sample_id in enumerate(first.sample_ids)}
    assert first.sampled_state_ids[frame_index[first_frame[0]]] == 'endpoint-A-id'
    assert first.sampled_state_ids[frame_index[second_frame[0]]] == 'endpoint-B-id'
    assert first.sampled_state_ids[frame_index[first_frame[1]]] == 'endpoint-B-id'
    assert first.sampled_state_ids[frame_index[second_frame[1]]] == 'endpoint-A-id'
    resampling = ExchangeResamplingSpec(
        'synchronized_blocks', 32, 64, design['resampling']['bootstrap_seed'],
        'fixtures/analytic/exchange-analysis-v1/design.json#frozen')
    results = {}
    for estimator in ('pymbar', 'atom_uwham'):
        results[estimator] = analyze_exchange(
            correlated, restrained_spec(), resampling=resampling, estimator=estimator)
        value = results[estimator].restrained_kj_mol
        error = results[estimator].restrained_standard_error_kj_mol
        criteria = design['predeclared_qualification_criteria']
        assert abs(value-1.5) <= criteria['known_answer_absolute_tolerance_kJ_mol']
        assert abs(value-1.5) <= criteria['known_answer_standard_error_multiplier']*error

    agreement = abs(results['pymbar'].restrained_kj_mol-results['atom_uwham'].restrained_kj_mol)
    criteria = design['predeclared_qualification_criteria']
    assert agreement <= criteria['identical_input_estimator_agreement_limit_kJ_mol']

    run_estimates = []
    for history in correlated:
        reduced = reduced_potentials(history.records)
        fit = estimate_free_energies(reduced, (4096, 4096), estimator='pymbar')
        run_estimates.append(float(fit['free_energies_dimensionless'][1]-fit['free_energies_dimensionless'][0])
                             *design['rt_kJ_mol'])
    across_run_mean_variance = float(np.var(run_estimates, ddof=1)/len(run_estimates))
    bootstrap_variance = results['pymbar'].restrained_standard_error_kj_mol**2
    ratio = bootstrap_variance/across_run_mean_variance
    low, high = criteria['bootstrap_to_independent_run_mean_variance_ratio']
    assert low <= ratio <= high

    independent_result = analyze_exchange(independent, restrained_spec(),
        resampling=resampling, estimator='pymbar')
    criteria = design['predeclared_qualification_criteria']
    assert abs(independent_result.restrained_kj_mol-1.5) <= criteria['known_answer_absolute_tolerance_kJ_mol']
    assert abs(independent_result.restrained_kj_mol-1.5) <= (
        criteria['known_answer_standard_error_multiplier']*
        independent_result.restrained_standard_error_kj_mol)

    run_resampling = ExchangeResamplingSpec(
        'independent_runs', None, 64, design['resampling']['bootstrap_seed'],
        'fixtures/analytic/exchange-analysis-v1/design.json#frozen')
    run_result = analyze_exchange(correlated, restrained_spec(),
        resampling=run_resampling, estimator='pymbar')
    assert abs(run_result.restrained_kj_mol-1.5) <= criteria['known_answer_absolute_tolerance_kJ_mol']
    assert abs(run_result.restrained_kj_mol-1.5) <= (
        criteria['known_answer_standard_error_multiplier']*
        run_result.restrained_standard_error_kj_mol)
    run_ratio = run_result.restrained_standard_error_kj_mol**2/across_run_mean_variance
    assert low <= run_ratio <= high

    from atm_mlmm.analysis import combine_free_energies
    reverse_spec = replace(restrained_spec(),
        endpoint_weights={'endpoint-A-id': 1., 'endpoint-B-id': -1.})
    diagnostic = results['pymbar'].diagnostics
    reverse = combine_free_energies(
        diagnostic['state_ids'], diagnostic['state_free_energies_kj_mol'],
        diagnostic['bootstrap_covariance_kj2_mol2'], reverse_spec)
    assert reverse.restrained_kj_mol == pytest.approx(-results['pymbar'].restrained_kj_mol)
    assert reverse.restrained_standard_error_kj_mol == pytest.approx(
        results['pymbar'].restrained_standard_error_kj_mol)

    correlated_moments, lag_rho, cross_rho, expected_variance, expected_means = sampled_harmonic_statistics(correlated)
    independent_moments, iid_lag, iid_cross, _, _ = sampled_harmonic_statistics(independent)
    mean_tolerance = criteria['state_marginal_mean_absolute_tolerance_nm']
    variance_tolerance = criteria['state_marginal_variance_relative_tolerance']
    correlation_tolerance = criteria['correlation_absolute_tolerance']
    for moments in (correlated_moments, independent_moments):
        for state, expected_mean in expected_means.items():
            assert abs(moments[state]['mean_nm']-expected_mean) <= mean_tolerance
            assert abs(moments[state]['variance_nm2']/expected_variance-1.) <= variance_tolerance
    assert abs(lag_rho-.5) <= correlation_tolerance
    assert abs(cross_rho-.5) <= correlation_tolerance
    assert abs(iid_lag) <= correlation_tolerance
    assert abs(iid_cross) <= correlation_tolerance

    from scipy.integrate import quad
    rt = design['rt_kJ_mol']
    k, displacement = 100., .3
    def partition(lam, spring):
        return quad(lambda x: math.exp(-(.5*k*(x+lam*displacement)**2+.5*spring*x*x)/rt),
                    -np.inf, np.inf, epsabs=1.e-11, epsrel=1.e-11)[0]
    restrained_exact = -rt*np.log(partition(1., 50.)/partition(0., 50.))
    zero_restraint_exact = -rt*np.log(partition(1., 0.)/partition(0., 0.))
    assert abs(restrained_exact-1.5) <= 1.e-12
    assert abs(-restrained_exact+1.5) <= 1.e-12
    assert abs(zero_restraint_exact) <= 1.e-12

    assert results['pymbar'].diagnostics['state_walker_visits']
    assert results['pymbar'].diagnostics['overlap_matrix']
    assert results['pymbar'].diagnostics['last_half_estimate_kj_mol'] is not None

    print(json.dumps({
        'scope': 'synthetic analytic control only',
        'design_id': design['design_id'], 'seeds': seeds,
        'pymbar': {'estimate_kJ_mol': results['pymbar'].restrained_kj_mol,
                   'bootstrap_se_kJ_mol': results['pymbar'].restrained_standard_error_kj_mol},
        'atom_uwham': {'estimate_kJ_mol': results['atom_uwham'].restrained_kj_mol,
                       'bootstrap_se_kJ_mol': results['atom_uwham'].restrained_standard_error_kj_mol},
        'estimator_difference_kJ_mol': agreement,
        'bootstrap_variance_kJ2_mol2': bootstrap_variance,
        'independent_run_mean_variance_kJ2_mol2': across_run_mean_variance,
        'covariance_ratio': ratio,
        'independent_runs_bootstrap_se_kJ_mol': run_result.restrained_standard_error_kj_mol,
        'independent_runs_covariance_ratio': run_ratio,
        'independent_baseline_estimate_kJ_mol': independent_result.restrained_kj_mol,
        'correlated_state_marginals': correlated_moments,
        'independent_state_marginals': independent_moments,
        'correlated_lag1': lag_rho, 'correlated_cross_walker': cross_rho,
        'iid_lag1': iid_lag, 'iid_cross_walker': iid_cross,
        'restrained_independent_quadrature_kJ_mol': restrained_exact,
        'reverse_quadrature_kJ_mol': -restrained_exact,
        'zero_restraint_quadrature_kJ_mol': zero_restraint_exact,
        'criterion_covariance_ratio': [low, high]
    }, sort_keys=True))
