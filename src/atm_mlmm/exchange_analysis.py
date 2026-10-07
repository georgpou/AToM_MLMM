"""Opt-in dependence-aware analysis for verified exchanging-walker histories.

This module consumes the existing raw energy records and pinned estimators. It
does not implement exchange decisions or a new thermodynamic estimator.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .analysis import combine_free_energies, estimate_free_energies
from .schema import (ExchangeAnalysisInput, ExchangeResamplingSpec, IdentityError,
                     MalformedInput, NumericalDomainError, QualificationError)


_WINDOW_FORMAT = 'exchange-retained-window-v1'


def _read_window_manifest(history):
    path = Path(history.retained_window_evidence)
    if path.is_symlink() or not path.is_file():
        raise IdentityError('retained-window evidence must name a regular JSON file')
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityError(f'cannot read retained-window evidence: {exc}') from exc
    if (not isinstance(document, dict) or document.get('format') != _WINDOW_FORMAT or
            type(document.get('version')) is not int or document['version'] != 1):
        raise IdentityError('unsupported retained-window evidence format/version')
    if document.get('run_id') != history.run_id:
        raise IdentityError('retained-window evidence run_id differs from analysis input')
    for name in ('selection_evidence', 'independent_initialization_evidence'):
        if not isinstance(document.get(name), str) or not document[name].strip():
            raise QualificationError(f'retained-window evidence lacks {name}')
    return document


def _groups(document, key):
    value = document.get(key)
    if not isinstance(value, list) or any(not isinstance(frame, list) or not frame for frame in value):
        raise IdentityError(f'retained-window {key} must be a nonempty list of complete frames')
    groups = []
    seen = set()
    for frame in value:
        if any(not isinstance(sample_id, str) or not sample_id for sample_id in frame):
            raise IdentityError(f'retained-window {key} contains an invalid sample ID')
        if len(frame) != len(set(frame)) or seen.intersection(frame):
            raise IdentityError(f'retained-window {key} repeats a sample ID')
        seen.update(frame)
        groups.append(tuple(frame))
    if not groups:
        raise IdentityError(f'retained-window {key} is empty')
    return tuple(groups)


def _journal_frames(document, history):
    source = Path(document.get('boundary_source', ''))
    if source.is_symlink() or not source.is_dir():
        raise IdentityError('persistent retained-window source must be a journal directory')
    from .exchange_journal import read_multistate_boundaries
    from .persistence import read_json

    rows = read_multistate_boundaries(source)
    metadata = read_json(source/'metadata.json')
    if metadata.get('run_id') != history.run_id:
        raise IdentityError('persistent journal run_id differs from analysis input')
    expected_identities = {
        'physical_identity': history.records.physical_identity,
        'transfer_identity': history.records.transfer_identity,
        'restraints_identity': history.records.restraint_identity,
        'schedule_identity': history.records.schedule.content_identity,
    }
    for field, actual in expected_identities.items():
        if metadata.get(field) != actual:
            raise IdentityError(f'persistent journal {field} differs from raw records')
    sample_rows = [sample for row in rows for sample in row['samples']]
    if len(sample_rows) != len(history.records.sample_ids):
        raise IdentityError('persistent journal sample inventory differs from raw records')
    records = history.records
    identity_fields = (
        ('sample_id', records.sample_ids), ('state_id', records.sampled_state_ids),
        ('walker_id', records.walker_ids), ('sequence_number', records.sequence_numbers),
    )
    for field, values in identity_fields:
        if tuple(sample[field] for sample in sample_rows) != tuple(values):
            raise IdentityError(f'persistent journal {field} order differs from raw records')
    raw_fields = (
        ('u0_raw_kJ_mol', records.u0_raw_kJ_mol),
        ('u1_raw_kJ_mol', records.u1_raw_kJ_mol),
        ('outside_energy_kJ_mol', records.outside_energy_kJ_mol),
        ('system_total_energy_kJ_mol', records.observed_total_kJ_mol),
    )
    for raw_name, values in raw_fields:
        journal_values = tuple(sample['raw'][raw_name] for sample in sample_rows)
        if not np.array_equal(np.asarray(journal_values), np.asarray(values)):
            raise IdentityError(f'persistent journal {raw_name} differs from raw records')
    frames = tuple(tuple(sample['sample_id'] for sample in row['samples']) for row in rows)
    initial_identity = hashlib.sha256((source/'initial'/'manifest.json').read_bytes()).hexdigest()
    return frames, initial_identity


def _validate_window(history):
    document = _read_window_manifest(history)
    records = history.records
    if document.get('source_kind') == 'synthetic':
        required = ('records_identity', 'schedule_identity', 'physical_identity',
                    'transfer_identity', 'restraint_identity', 'source_frames',
                    'retained_frames', 'excluded_frames', 'synthetic_warning')
        if any(name not in document for name in required):
            raise IdentityError('synthetic retained-window evidence is incomplete')
        if not str(document['synthetic_warning']).strip():
            raise QualificationError('synthetic histories require an explicit non-molecular limitation')
        identities = (
            ('records_identity', records.content_identity),
            ('schedule_identity', records.schedule.content_identity),
            ('physical_identity', records.physical_identity),
            ('transfer_identity', records.transfer_identity),
            ('restraint_identity', records.restraint_identity),
        )
        for field, expected in identities:
            if document[field] != expected:
                raise IdentityError(f'synthetic window {field} differs from raw records')
        source_frames = _groups(document, 'source_frames')
        initialization_identity = document['independent_initialization_evidence']
    elif document.get('source_kind') == 'persistent_multistate_journal':
        if 'boundary_source' not in document or 'retained_frames' not in document or 'excluded_frames' not in document:
            raise IdentityError('persistent retained-window evidence is incomplete')
        source_frames, initialization_identity = _journal_frames(document, history)
    else:
        raise IdentityError('unknown retained-window source kind')

    retained = _groups(document, 'retained_frames')
    excluded_value = document.get('excluded_frames')
    if not isinstance(excluded_value, list):
        raise IdentityError('retained-window excluded_frames must be a list')
    excluded = () if not excluded_value else _groups(document, 'excluded_frames')
    all_ids = tuple(sample_id for frame in source_frames for sample_id in frame)
    if all_ids != records.sample_ids:
        raise IdentityError('verified source frame order does not cover every original raw record')
    source_set = set(source_frames)
    retained_set, excluded_set = set(retained), set(excluded)
    if (len(retained_set) != len(retained) or len(excluded_set) != len(excluded) or
            retained_set & excluded_set or retained_set | excluded_set != source_set):
        raise IdentityError('retained and excluded windows must partition complete source frames')
    ordered_retained = tuple(frame for frame in source_frames if frame in retained_set)
    ordered_excluded = tuple(frame for frame in source_frames if frame in excluded_set)
    if retained != ordered_retained or excluded != ordered_excluded:
        raise IdentityError('retained/excluded frames must preserve source chronology')
    positions = [i for i, frame in enumerate(source_frames) if frame in retained_set]
    if positions != list(range(positions[0], positions[-1]+1)):
        raise IdentityError('retained frames must form one explicit contiguous time window')
    if history.synchronized_frames != retained:
        raise IdentityError('synchronized frame groups differ from verified retained-window provenance')

    sample_index = {sample_id: i for i, sample_id in enumerate(records.sample_ids)}
    if len(sample_index) != len(records.sample_ids):
        raise IdentityError('original raw sample IDs are not unique')
    state_ids = tuple(state.state_id for state in records.schedule.states)
    walker_ids = tuple(dict.fromkeys(records.walker_ids))
    if len(walker_ids) != len(state_ids):
        raise QualificationError('exchange analysis requires one stable walker per declared state')
    expected_states = set(state_ids)
    for frame in source_frames:
        if len(frame) != len(walker_ids):
            raise IdentityError('verified frame does not contain exactly one sample per walker')
        indices = [sample_index[sample_id] for sample_id in frame]
        frame_walkers = tuple(records.walker_ids[i] for i in indices)
        frame_states = tuple(records.sampled_state_ids[i] for i in indices)
        frame_sequences = tuple(records.sequence_numbers[i] for i in indices)
        if (set(frame_walkers) != set(walker_ids) or len(set(frame_walkers)) != len(walker_ids) or
                set(frame_states) != expected_states or len(set(frame_states)) != len(state_ids) or
                len(set(frame_sequences)) != 1):
            raise IdentityError('synchronized frame must contain one complete declared walker/state permutation')
    for run_id in walker_ids:
        numbers = [records.sequence_numbers[i] for i, walker in enumerate(records.walker_ids)
                   if walker == run_id]
        if len(numbers) != len(set(numbers)) or numbers != sorted(numbers):
            raise IdentityError('walker boundary sequence must be unique and monotone')
    if records.sampling_mode != 'correlated':
        raise QualificationError('exchange analysis requires explicitly correlated histories')
    return dict(document=document, source_frames=source_frames, retained_frames=retained,
                excluded_frames=excluded, retained_frame_positions=tuple(positions),
                sample_index=sample_index, walker_ids=walker_ids,
                initialization_identity=initialization_identity)


def _fit_pairs(histories, matrices, state_ids, pairs, estimator):
    records_by_history = [history.records for history in histories]
    state_by_pair = [records_by_history[h].sampled_state_ids[index] for h, index in pairs]
    ordered = [(h, index) for state in state_ids for (h, index), sampled in zip(pairs, state_by_pair)
               if sampled == state]
    counts = np.array([sum(sampled == state for sampled in state_by_pair) for state in state_ids], dtype=int)
    if any(count == 0 for count in counts):
        raise QualificationError('resampled draw is missing a declared sampled state')
    reduced = np.column_stack([matrices[h][:, index] for h, index in ordered])
    fit = estimate_free_energies(reduced, counts, estimator=estimator)
    free = np.asarray(fit['free_energies_dimensionless'], dtype=float)
    if free.shape != (len(state_ids),) or not np.isfinite(free).all():
        raise NumericalDomainError('resampled draw returned nonfinite state free energies')
    return fit, counts, free


def _indices_for_frames(validation, records, frame_positions):
    sample_index = validation['sample_index']
    return tuple(sample_index[sample_id]
                 for position in frame_positions
                 for sample_id in validation['source_frames'][position])


def _frame_selection(rng, histories, validations, resampling):
    frame_positions_by_run = {}
    if resampling.method == 'synchronized_blocks':
        length = resampling.block_length_frames
        block_indices_by_run = {}
        for history, validation in zip(histories, validations):
            retained = validation['retained_frame_positions']
            if len(retained) < 2*length or len(retained) % length:
                raise QualificationError('retained window needs at least two full blocks and exact divisibility')
            block_count = len(retained)//length
            selected_blocks = rng.integers(0, block_count, size=block_count)
            block_indices_by_run[history.run_id] = tuple(int(i) for i in selected_blocks)
            selected_frames = tuple(retained[int(block)*length+offset]
                                    for block in selected_blocks for offset in range(length))
            frame_positions_by_run[history.run_id] = tuple(int(i) for i in selected_frames)
        pairs = []
        for history_index, (history, validation) in enumerate(zip(histories, validations)):
            for record_index in _indices_for_frames(validation, history.records,
                                                    frame_positions_by_run[history.run_id]):
                pairs.append((history_index, record_index))
        return pairs, dict(selected_block_indices_by_run=block_indices_by_run,
                           selected_run_ids=()), sum(
            len(validation['retained_frame_positions'])//resampling.block_length_frames
            for validation in validations)

    run_indices = rng.integers(0, len(histories), size=len(histories))
    selected_run_ids = tuple(histories[int(index)].run_id for index in run_indices)
    pairs = []
    for index in run_indices:
        history_index = int(index)
        history, validation = histories[history_index], validations[history_index]
        selected_frames = validation['retained_frame_positions']
        frame_positions_by_run.setdefault(history.run_id, tuple())
        frame_positions_by_run[history.run_id] += tuple(selected_frames)
        pairs.extend((history_index, record_index)
                     for record_index in _indices_for_frames(validation, history.records, selected_frames))
    return pairs, dict(selected_block_indices_by_run={},
                       selected_run_ids=selected_run_ids), len(selected_run_ids)


def _selection_record(histories, selection, pairs):
    sample_ids = tuple(histories[h].records.sample_ids[index] for h, index in pairs)
    digest = hashlib.sha256()
    for sample_id in sample_ids:
        digest.update(sample_id.encode())
        digest.update(b'\0')
    return dict(selected_block_indices_by_run=selection['selected_block_indices_by_run'],
                selected_run_ids=tuple(selection['selected_run_ids']),
                selected_sample_count=len(sample_ids),
                selected_sample_ids_sha256=digest.hexdigest(),
                # The source ID inventory plus this repeated frame-index stream
                # reconstructs every sample ID and bootstrap multiplicity.
                sample_id_source='raw_sample_ids + selected_frame_indices_by_run')


def analyze_exchange(histories, thermodynamics, *, resampling, estimator='pymbar',
                     joint_covariance_kj2_mol2=None):
    """Analyze verified correlated exchange histories with declared resampling.

    Raw reduced-potential reconstruction is performed on every original record
    before retained-window selection. Bootstrap repeats are index multiplicities;
    they do not acquire fabricated physical sample IDs.
    """
    if not isinstance(histories, tuple) or not histories:
        raise MalformedInput('exchange histories must be a nonempty tuple')
    if not isinstance(resampling, ExchangeResamplingSpec):
        raise MalformedInput('explicit ExchangeResamplingSpec is required')
    if any(not isinstance(history, ExchangeAnalysisInput) for history in histories):
        raise MalformedInput('exchange input must contain ExchangeAnalysisInput records')

    # Reconstruct every original raw observation before any window selection.
    from .schedule import reduced_potentials
    matrices = [reduced_potentials(history.records) for history in histories]
    validations = [_validate_window(history) for history in histories]
    run_ids = tuple(history.run_id for history in histories)
    if len(set(run_ids)) != len(run_ids):
        raise IdentityError('exchange run IDs must be distinct')
    initialization = [validation['initialization_identity'] for validation in validations]
    if len(set(initialization)) != len(initialization):
        raise IdentityError('independent histories repeat their initialization identity')
    first = histories[0].records
    if any(history.records.schedule.content_identity != first.schedule.content_identity or
           history.records.physical_identity != first.physical_identity or
           history.records.transfer_identity != first.transfer_identity or
           history.records.restraint_identity != first.restraint_identity
           for history in histories[1:]):
        raise IdentityError('exchange runs do not share the same schedule and physical identities')
    if resampling.method == 'independent_runs' and len(histories) < 2:
        raise QualificationError('independent_runs resampling requires at least two independent runs')

    state_ids = tuple(state.state_id for state in first.schedule.states)
    rt = .00831446261815324*first.schedule.temperature_K
    raw_sample_ids = tuple(sample_id for history in histories for sample_id in history.records.sample_ids)
    if len(raw_sample_ids) != len(set(raw_sample_ids)):
        raise IdentityError('raw sample IDs collide across exchange histories')
    retained_sample_ids = tuple(sample_id for history, validation in zip(histories, validations)
                                for frame in validation['retained_frames'] for sample_id in frame)
    excluded_sample_ids = tuple(sample_id for history, validation in zip(histories, validations)
                                for frame in validation['excluded_frames'] for sample_id in frame)

    point_pairs = []
    for history_index, validation in enumerate(validations):
        point_pairs.extend((history_index, record_index)
                           for record_index in _indices_for_frames(
                               validation, histories[history_index].records,
                               validation['retained_frame_positions']))
    point_fit, point_counts, point_free = _fit_pairs(histories, matrices, state_ids, point_pairs, estimator)

    run_free = []
    for history_index, history in enumerate(histories):
        validation = validations[history_index]
        run_pairs = [(history_index, index) for index in _indices_for_frames(
            validation, history.records, validation['retained_frame_positions'])]
        _, _, free = _fit_pairs((history,), (matrices[history_index],), state_ids,
                                [(0, index) for _, index in run_pairs], estimator)
        run_free.append(free*rt)

    visits = {}
    for history, validation in zip(histories, validations):
        per_walker = {walker: {state: 0 for state in state_ids}
                      for walker in validation['walker_ids']}
        for frame in validation['retained_frames']:
            for sample_id in frame:
                index = validation['sample_index'][sample_id]
                per_walker[history.records.walker_ids[index]][history.records.sampled_state_ids[index]] += 1
        visits[history.run_id] = per_walker

    rng = np.random.default_rng(resampling.seed)
    free_draws, draw_records, failed_draws = [], [], []
    for draw_index in range(resampling.bootstrap_replicates):
        pairs, selection, information_count = _frame_selection(
            rng, histories, validations, resampling)
        selection_record = _selection_record(histories, selection, pairs)
        try:
            fit, counts, free = _fit_pairs(histories, matrices, state_ids, pairs, estimator)
            free_draws.append(free*rt)
            draw_records.append(dict(draw_index=draw_index, status='passed',
                                     state_counts=tuple(int(value) for value in counts),
                                     free_energies_kj_mol=tuple(float(value*rt) for value in free),
                                     solver_residual=float(fit['solver_residual']),
                                     information_units=information_count, **selection_record))
        except Exception as exc:
            failed_draws.append(dict(draw_index=draw_index, status='failed',
                                     exception_type=type(exc).__name__, reason=str(exc), **selection_record))
            draw_records.append(failed_draws[-1])
    if failed_draws:
        error = QualificationError(
            f'{len(failed_draws)} of {resampling.bootstrap_replicates} exchange bootstrap draws failed; '
            'sampling covariance is withheld')
        error.failed_draws = tuple(failed_draws)
        error.bootstrap_draws = tuple(draw_records)
        error.raw_sample_ids = raw_sample_ids
        error.resampling_seed = resampling.seed
        error.design_evidence = resampling.design_evidence
        raise error
    if not np.isfinite(np.asarray(free_draws)).all():
        raise NumericalDomainError('nonfinite bootstrap free-energy vectors; covariance is withheld')
    covariance = np.asarray(np.cov(np.asarray(free_draws), rowvar=False, ddof=1), dtype=float)
    if covariance.shape != (len(state_ids), len(state_ids)):
        raise NumericalDomainError('bootstrap free-energy covariance has the wrong shape')

    endpoint_weights = np.array([thermodynamics.endpoint_weights.get(state, 0.) for state in state_ids])
    run_contrasts = np.asarray([endpoint_weights@free for free in run_free], dtype=float)
    if len(run_contrasts) > 1:
        run_spread = float(np.std(run_contrasts, ddof=1))
        run_mean_se = run_spread/math.sqrt(len(run_contrasts))
    else:
        run_spread = run_mean_se = None

    retained_indices_by_run = [validation['retained_frame_positions'] for validation in validations]
    last_half_pairs = []
    last_half_failures = []
    for history_index, (history, validation) in enumerate(zip(histories, validations)):
        positions = validation['retained_frame_positions']
        if len(positions) < 2:
            last_half_failures.append(f'{history.run_id}: fewer than two retained frames')
            continue
        split = len(positions)//2
        last_half_pairs.extend((history_index, index) for index in _indices_for_frames(
            validation, history.records, positions[split:]))
    last_half_estimate = None
    if not last_half_failures:
        try:
            _, _, last_half_free = _fit_pairs(histories, matrices, state_ids, last_half_pairs, estimator)
            last_half_estimate = float(endpoint_weights@(last_half_free*rt))
        except Exception as exc:
            last_half_failures.append(f'{type(exc).__name__}: {exc}')

    full_estimate = float(endpoint_weights@(point_free*rt))
    quality_flags = []
    if np.min(point_fit['effective_samples']) < 100:
        quality_flags.append('fewer_than_100_iid_weight_effective_contributions')
    limitations = [
        'synthetic_histories_are_not_scheduler_mixing_or_convergence_evidence',
        'connected_overlap_does_not_prove_conformational_convergence',
        'effective_weight_counts_are_iid_contribution_diagnostics_not_correlation_adjusted_information',
        'full_and_last_half_share_trajectory_samples_and_are_not_independent',
        'linked_corrections_require_joint_covariance_from_the_same_linked_observables',
    ]
    correlation_information = dict(
        units=('resampled time blocks' if resampling.method == 'synchronized_blocks'
               else 'complete independent runs'),
        count=(sum(len(validation['retained_frame_positions'])//resampling.block_length_frames
                   for validation in validations) if resampling.method == 'synchronized_blocks'
               else len(histories)),
        interpretation='resampling units; not an effective independent molecular sample count')
    diagnostics = dict(
        analysis_format='exchange-analysis-v1', estimator=estimator,
        resampling_method=resampling.method,
        block_length_frames=resampling.block_length_frames,
        run_count=len(histories), bootstrap_replicates=resampling.bootstrap_replicates,
        bootstrap_seed=resampling.seed, design_evidence=resampling.design_evidence,
        run_ids=run_ids, retained_window_evidence=tuple(history.retained_window_evidence for history in histories),
        raw_sample_ids=raw_sample_ids, retained_sample_ids=retained_sample_ids,
        excluded_sample_ids=excluded_sample_ids,
        raw_sample_count=len(raw_sample_ids), retained_sample_count=len(retained_sample_ids),
        state_ids=state_ids, sampled_counts=tuple(int(value) for value in point_counts),
        state_free_energies_kj_mol=tuple(float(value*rt) for value in point_free),
        state_walker_visits=visits,
        overlap_matrix=point_fit['overlap_matrix'].tolist(),
        iid_weight_effective_contributions=point_fit['effective_samples'].tolist(),
        solver_residual=float(point_fit['solver_residual']), quality_flags=tuple(quality_flags),
        correlation_adjusted_information=correlation_information,
        bootstrap_covariance_kj2_mol2=covariance.tolist(),
        bootstrap_draws=tuple(draw_records),
        sampling_standard_error_kj_mol=math.sqrt(max(0., float(endpoint_weights@covariance@endpoint_weights))),
        across_run_estimate_spread_kj_mol=run_spread,
        across_run_mean_standard_error_kj_mol=run_mean_se,
        run_endpoint_estimates_kj_mol=tuple(float(value) for value in run_contrasts),
        full_estimate_kj_mol=full_estimate,
        last_half_estimate_kj_mol=last_half_estimate,
        full_minus_last_half_kj_mol=(None if last_half_estimate is None else full_estimate-last_half_estimate),
        full_last_half_warning=('halves are dependent diagnostics, not independent convergence evidence'),
        last_half_failures=tuple(last_half_failures),
        limitations=tuple(limitations))
    return combine_free_energies(state_ids, point_free*rt, covariance, thermodynamics,
                                 joint_covariance_kj2_mol2=joint_covariance_kj2_mol2,
                                 diagnostics=diagnostics)


__all__ = ('ExchangeAnalysisInput', 'ExchangeResamplingSpec', 'analyze_exchange')
