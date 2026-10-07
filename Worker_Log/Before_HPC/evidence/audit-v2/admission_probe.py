"""Inert F1 regression characterization: intercept all estimator work."""
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tests.sampling.test_exchange_uncertainty import make_synthetic_history, restrained_spec
from atm_mlmm.exchange_analysis import _validate_window, analyze_exchange
from atm_mlmm.schema import ExchangeResamplingSpec, IdentityError


class EstimationReached(Exception):
    pass


with tempfile.TemporaryDirectory(prefix='audit-v2-inert-') as directory:
    root = Path(directory)
    first = make_synthetic_history(root, 0, seed=254347, frames=32)
    duplicate = make_synthetic_history(root, 1, seed=254347, frames=32)
    distinct = make_synthetic_history(root, 2, seed=278933, frames=32)
    assert first.records.u0_raw_kJ_mol == duplicate.records.u0_raw_kJ_mol
    assert first.records.u1_raw_kJ_mol == duplicate.records.u1_raw_kJ_mol
    assert first.records.sample_ids != duplicate.records.sample_ids
    assert _validate_window(first)['initialization_identity'] == _validate_window(duplicate)['initialization_identity']
    outcomes = {}
    for method, pair, name in (
            ('independent_runs', (first, duplicate), 'duplicate_independent_runs'),
            ('synchronized_blocks', (first, duplicate), 'duplicate_synchronized_blocks'),
            ('synchronized_blocks', (first, distinct), 'distinct_synchronized_blocks')):
        spec = ExchangeResamplingSpec(method, 8 if method == 'synchronized_blocks' else None,
                                      8, 99, 'audit-only inert admission control')
        with patch('atm_mlmm.exchange_analysis._fit_pairs', side_effect=EstimationReached):
            try:
                analyze_exchange(pair, restrained_spec(), resampling=spec)
            except EstimationReached:
                outcomes[name] = 'estimation_reached'
            except IdentityError as exc:
                outcomes[name] = str(exc)
    assert 'initialization' in outcomes['duplicate_independent_runs']
    assert outcomes['duplicate_synchronized_blocks'] == 'estimation_reached'
    assert outcomes['distinct_synchronized_blocks'] == 'estimation_reached'
    print(json.dumps(outcomes, indent=2, sort_keys=True))
    print('CHARACTERIZATION CONFIRMED; no estimator, model, dynamics or production executed')
