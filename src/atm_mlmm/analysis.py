"""Protocol-supplied observables and covariance-aware thermodynamic accounting."""
import math

import numpy as np

from .schema import BindingResult, IdentityError, MalformedInput, NumericalDomainError, QualificationError


def _connected_support(overlap):
    graph = (overlap+overlap.T) > 1.e-10
    reached, queue = set(), [0]
    while queue:
        i = queue.pop()
        if i not in reached:
            reached.add(i)
            queue.extend(j for j in np.flatnonzero(graph[i]) if j not in reached)
    if len(reached) != len(overlap):
        raise QualificationError('estimator support is disconnected at overlap threshold 1e-10')


def estimate_free_energies(reduced, sample_counts, *, estimator='pymbar'):
    """Identical dimensionless states/counts for independently implemented solvers."""
    import importlib.metadata
    from .schema import UnsupportedCapability
    potentials = np.asarray(reduced, dtype=float)
    counts = np.asarray(sample_counts)
    if potentials.ndim != 2 or potentials.shape[0] < 2 or counts.shape != (potentials.shape[0],):
        raise MalformedInput('two or more reduced states and complete counts required')
    if counts.dtype.kind not in 'iu' or np.any(counts < 0) or counts.sum() != potentials.shape[1]:
        raise MalformedInput('integer sample counts must sum to observation count')
    if np.any(counts == 0):
        raise QualificationError('this estimator profile requires every declared state sampled')
    if not np.isfinite(potentials).all():
        raise NumericalDomainError('nonfinite reduced observations must be retained as failures')
    if estimator == 'pymbar':
        if importlib.metadata.version('pymbar') != '4.0.3':
            raise UnsupportedCapability('analysis requires pinned PyMBAR 4.0.3')
        from pymbar import MBAR
        model = MBAR(potentials, counts, relative_tolerance=1.e-12, maximum_iterations=10000)
        overlap = np.asarray(model.compute_overlap()['matrix'])
        _connected_support(overlap)
        output = dict(free_energies_dimensionless=np.asarray(model.f_k)-model.f_k[0],
                      covariance_dimensionless=model.compute_free_energy_differences(return_theta=True)['Theta'],
                      normalized_weights=model.weights(),
                      solver_residual=float(np.max(np.abs(model.weights().sum(axis=0)-1.))))
    elif estimator == 'atom_uwham':
        from .adapters.atom import estimate_uwham
        output = estimate_uwham(potentials, counts)
        weights = output['normalized_weights']
        overlap = (weights.T@weights)*counts
        _connected_support(overlap)
    else:
        raise UnsupportedCapability(f'unknown estimator: {estimator}')
    weights = output['normalized_weights']
    if not np.isfinite(weights).all() or not np.allclose(weights.sum(axis=0), 1., rtol=0, atol=1.e-4):
        raise QualificationError('estimator weights failed normalization')
    output['covariance_dimensionless'] = _covariance(output['covariance_dimensionless'], len(counts))
    output['overlap_matrix'] = overlap
    output['effective_samples'] = 1/np.sum(weights*weights, axis=0)
    output['estimator'] = estimator
    return output


def _uncorrelated_indices(records):
    """Conservative thinning by walker, preserving every original raw record.

    The analysis does not infer equilibration or omit nonfinite frames. Input
    must already define its scientifically retained window with provenance.
    Histories with state changes require a later block/resampling qualification.
    """
    if records.sampling_mode == 'independent':
        return np.arange(len(records.sample_ids)), {walker: 1. for walker in records.walker_ids}
    from pymbar import timeseries
    walkers = np.asarray(records.walker_ids)
    states = np.asarray(records.sampled_state_ids)
    u0, u1, outside = map(np.asarray, (records.u0_raw_kJ_mol, records.u1_raw_kJ_mol, records.outside_energy_kJ_mol))
    retained, inefficiency = [], {}
    for walker in dict.fromkeys(records.walker_ids):
        indices = np.flatnonzero(walkers == walker)
        if len(set(states[indices])) != 1:
            from .schema import UnsupportedCapability
            raise UnsupportedCapability('correlated exchanging-walker history requires qualified block/resampling analysis')
        if len(indices) < 4:
            raise QualificationError('correlated walker history is too short for correlation assessment')
        signals = (u0[indices], u1[indices], (u1-u0)[indices], outside[indices])
        estimates = [float(timeseries.statistical_inefficiency(signal)) for signal in signals if np.var(signal) > 0]
        if not estimates:
            raise QualificationError('constant correlated walker observables cannot establish independence')
        g = max(1., *estimates)
        inefficiency[walker] = g
        selected = timeseries.subsample_correlated_data(signals[0], g=g, conservative=True)
        retained.extend(indices[selected])
    return np.asarray(sorted(retained)), inefficiency


def analyze(records, thermodynamics, *, estimator='pymbar', joint_covariance_kj2_mol2=None):
    """Analyze raw NVT records under an explicit protocol thermodynamic spec."""
    from .schedule import reduced_potentials
    from .restraints import MOLAR_GAS_CONSTANT_KJ_MOL_K
    reduced = reduced_potentials(records)  # validate all original observations first
    retained, inefficiency = _uncorrelated_indices(records)
    state_ids = tuple(state.state_id for state in records.schedule.states)
    sampled = np.asarray(records.sampled_state_ids)
    # Both estimator inputs use the same state-contiguous ordering and counts.
    ordered = np.concatenate([retained[sampled[retained] == state] for state in state_ids])
    counts = np.array([np.count_nonzero(sampled[ordered] == state) for state in state_ids])
    fit = estimate_free_energies(reduced[:, ordered], counts, estimator=estimator)
    rt = MOLAR_GAS_CONSTANT_KJ_MOL_K*records.schedule.temperature_K
    diagnostics = dict(estimator=estimator, input_samples=len(records.sample_ids), retained_samples=len(ordered),
                       retained_sample_ids=tuple(records.sample_ids[i] for i in ordered),
                       statistical_inefficiency=inefficiency, sampled_counts=tuple(int(n) for n in counts),
                       state_ids=state_ids, overlap_matrix=fit['overlap_matrix'].tolist(),
                       effective_samples=fit['effective_samples'].tolist(), solver_residual=fit['solver_residual'],
                       records_identity=records.content_identity,
                       quality_flags=('fewer_than_100_effective_contributions',) if np.min(fit['effective_samples']) < 100 else (),
                       limitations=('finite_state_overlap_does_not_prove_conformational_convergence',
                                    'mean_error_is_not_replicate_spread', 'fixed_state_walker_correlation_profile'))
    return combine_free_energies(state_ids, fit['free_energies_dimensionless']*rt,
                                 fit['covariance_dimensionless']*rt**2, thermodynamics,
                                 joint_covariance_kj2_mol2=joint_covariance_kj2_mol2, diagnostics=diagnostics)


def _covariance(value, count):
    array = np.asarray(value, dtype=float)
    if array.shape != (count, count) or not np.isfinite(array).all():
        raise MalformedInput('complete finite covariance matrix required')
    if not np.allclose(array, array.T, rtol=0, atol=1.e-10):
        raise MalformedInput('covariance matrix must be symmetric')
    if np.linalg.eigvalsh(array).min() < -1.e-10*max(1., float(np.max(np.abs(array)))):
        raise MalformedInput('covariance matrix must be positive semidefinite')
    return array


def directional_difference(leg0, leg1, bridge, covariance_kj2_mol2):
    """F0-F1 = D1-D0-deltaFm, with all three covariances retained."""
    if bridge is None:
        raise QualificationError('directional bridge must be computed or demonstrated zero')
    values = np.array((leg0, leg1, bridge), dtype=float)
    if not np.isfinite(values).all():
        raise NumericalDomainError('nonfinite directional leg/bridge')
    weights = np.array((-1., 1., -1.))
    covariance = _covariance(covariance_kj2_mol2, 3)
    return float(weights@values), math.sqrt(max(0., float(weights@covariance@weights)))


def combine_free_energies(state_ids, free_energies_kj_mol, covariance_kj2_mol2, thermodynamics,
                          *, joint_covariance_kj2_mol2=None, diagnostics=None):
    """Apply explicit state weights, then only complete correction obligations.

    Joint covariance orders all supplied states then every resolved correction
    in the spec's correction order; it includes cross-covariance with sampling.
    No independent-corrections assumption is silently made.
    """
    ids = tuple(state_ids)
    if not ids or len(set(ids)) != len(ids) or not set(thermodynamics.endpoint_weights) <= set(ids):
        raise IdentityError('unique states must cover all endpoint weights')
    energies = np.asarray(free_energies_kj_mol, dtype=float)
    if energies.shape != (len(ids),) or not np.isfinite(energies).all():
        raise NumericalDomainError('finite free energy required for every state')
    graph = {state: set() for state in ids}
    for a, b in thermodynamics.state_connections:
        if a not in graph or b not in graph:
            raise IdentityError('thermodynamic graph references unknown state')
        graph[a].add(b)
        graph[b].add(a)
    weighted = {s for s, w in thermodynamics.endpoint_weights.items() if w != 0}
    reached, queue = set(), [next(iter(weighted))]
    while queue:
        state = queue.pop()
        if state not in reached:
            reached.add(state)
            queue.extend(graph[state]-reached)
    if not weighted <= reached:
        raise QualificationError('declared endpoint graph is disconnected')
    covariance = _covariance(covariance_kj2_mol2, len(ids))
    weights = np.array([thermodynamics.endpoint_weights.get(s, 0.) for s in ids])
    raw = float(weights@energies)
    error = math.sqrt(max(0., float(weights@covariance@weights)))
    corrections = thermodynamics.corrections
    by_id = {c.correction_id: c for c in corrections}
    unresolved = [name for name in thermodynamics.correction_obligations
                  if name not in by_id or by_id[name].status == 'required_uncomputed']
    final = final_error = None
    if thermodynamics.observable == 'standard_binding_free_energy' and not unresolved:
        resolved = [c for c in corrections if c.status != 'required_uncomputed']
        if joint_covariance_kj2_mol2 is None and any(c.standard_error_kj_mol != 0 for c in resolved):
            unresolved.append('correction_covariance')
        else:
            final = raw+sum(c.value_kj_mol for c in resolved)
            final_error = error
            if joint_covariance_kj2_mol2 is not None:
                joint = _covariance(joint_covariance_kj2_mol2, len(ids)+len(resolved))
                if not np.allclose(joint[:len(ids), :len(ids)], covariance, atol=1.e-10, rtol=1.e-10):
                    raise IdentityError('joint covariance must retain state covariance')
                if not np.allclose(np.diag(joint)[len(ids):], [c.standard_error_kj_mol**2 for c in resolved], atol=1.e-10, rtol=1.e-10):
                    raise IdentityError('joint covariance disagrees with correction errors')
                combined_weights = np.r_[weights, np.ones(len(resolved))]
                final_error = math.sqrt(max(0., float(combined_weights@joint@combined_weights)))
    return BindingResult(raw, error, corrections, tuple(unresolved), final, final_error,
                         thermodynamics.content_identity, diagnostics or {})
