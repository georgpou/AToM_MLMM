"""Focused regressions for the G10 v6 inert admission repair batch."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
from unittest.mock import patch

import pytest

from tests.workflow.test_persistent_exchange import prepare_multistate


STATES = ('first', 'middle', 'third')
PAIRS = ((0, 1), (1, 2))
_RESULTS = []


@pytest.fixture(scope='module')
def valid_prefix(tmp_path_factory):
    from atm_mlmm.exchange import run_multistate_exchange
    from atom_openmm import gibbs_sampling

    root = tmp_path_factory.mktemp('g10-v6-source-current')
    prepared = prepare_multistate(root / 'prepared')
    output = root / 'prefix'
    with patch.object(gibbs_sampling, '_random', lambda: 0.0):
        run_multistate_exchange(prepared, output, state_ids=STATES, state_pairs=PAIRS,
            boundaries=1, steps_per_boundary=1, seed=73, trusted=True)
    return prepared, output


def _edit_json(path, edit):
    from atm_mlmm.persistence import read_json, write_json
    document = read_json(path)
    edit(document)
    write_json(path, document)


def _write_metadata(run, edit):
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json, write_json
    path = run / 'metadata.json'
    metadata = read_json(path)
    edit(metadata)
    write_json(path, metadata)
    (run / 'metadata.sha256').write_text(sha(path) + '\n')


def _reseal_initial_and_boundary(run, *, initial_changed=False, boundary_changed=True):
    from atm_mlmm.exchange_journal import seal_tree, sha
    from atm_mlmm.persistence import read_json, write_json

    metadata = read_json(run / 'metadata.json')
    if initial_changed:
        metadata['initial_manifest_sha256'] = seal_tree(run / 'initial', index=-1)
        boundary_changed = True
        record_path = run / 'boundaries/000000/record.json'
        record = read_json(record_path)
        record['previous_manifest_sha256'] = metadata['initial_manifest_sha256']
        write_json(record_path, record)
    if boundary_changed:
        seal_tree(run / 'boundaries/000000', index=0)
    if initial_changed:
        path = run / 'metadata.json'
        write_json(path, metadata)
        (run / 'metadata.sha256').write_text(sha(path) + '\n')


def _clone_prefix(valid_prefix, destination):
    _, prefix = valid_prefix
    return shutil.copytree(prefix, destination)


def _tree_digest(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(8, 'big'))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, 'big'))
        digest.update(content)
    return digest.hexdigest()


def _file_digest(path):
    if not path.exists():
        return None
    return _tree_digest(path) if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()


def _write_results():
    path = os.environ.get('G10_V6_RESULTS_PATH')
    if not path:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parents[2] / 'src/atm_mlmm/exchange_journal.py'
    result = {
        'worker_model': 'gpt-6-luna',
        'worker_effort': 'max',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'challenges': _RESULTS,
        'challenge_count': len(_RESULTS),
        'violation_count': sum(row.get('status') == 'VIOLATION' for row in _RESULTS),
    }
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


@pytest.fixture(scope='module', autouse=True)
def _persist_results_after_module():
    yield
    _write_results()


def _challenge(run, name):
    from atm_mlmm import exchange as controller
    from atm_mlmm import exchange_journal as journal
    from atm_mlmm.adapters import atom
    from atm_mlmm.schema import IdentityError

    loader_calls = []

    def forbidden(*args, **kwargs):
        loader_calls.append(kwargs.get('integrator_seed'))
        raise RuntimeError('trusted worker loader reached')

    before = _tree_digest(run)
    pending_before = _file_digest(run / 'pending')
    reader_error = None
    resume_error = None
    with patch.object(atom, 'load_worker_run', forbidden):
        try:
            journal.read_multistate_boundaries(run)
        except Exception as error:
            reader_error = f'{type(error).__name__}: {error}'
        try:
            controller.resume_multistate_exchange(run, trusted=True)
        except Exception as error:
            resume_error = f'{type(error).__name__}: {error}'
    after = _tree_digest(run)
    pending_after = _file_digest(run / 'pending')
    result = {
        'name': name,
        'reader_error': reader_error,
        'resume_error': resume_error,
        'reader_rejected_with_identity_error': bool(reader_error and reader_error.startswith('IdentityError:')),
        'loader_calls': loader_calls,
        'run_tree_sha256_before': before,
        'run_tree_sha256_after': after,
        'pending_sha256_before': pending_before,
        'pending_sha256_after': pending_after,
        'metadata_sha256': journal.sha(run / 'metadata.json'),
        'boundary_manifest_sha256': journal.sha(run / 'boundaries/000000/manifest.json'),
        'status': 'PASS' if reader_error and not loader_calls and before == after and pending_before == pending_after else 'VIOLATION',
    }
    _RESULTS.append(result)
    _write_results()
    assert result['reader_rejected_with_identity_error'], f'{name}: reader admitted challenge; result={result}'
    assert not loader_calls, f'{name}: trusted worker loader ran; result={result}'
    assert before == after, f'{name}: resume mutated output/evidence; result={result}'
    assert pending_before == pending_after, f'{name}: pending evidence changed; result={result}'


@pytest.mark.parametrize('challenge', (
    'steps-exclusive-limit',
    'boundaries-boolean',
    'steps-boolean',
    'worker-seed-overflows-later-walkers',
    'worker-seed-base-boolean',
    'host-seed-boolean',
    'host-seed-api-exclusive-limit',
    'python-gaussian-cache-string',
    'python-gaussian-cache-boolean',
    'python-gaussian-cache-overflow',
    'python-internal-word-boolean',
    'python-index-boolean',
    'initial-record-inverse-boolean',
    'initial-inverse-document-boolean',
    'boundary-inverse-document-boolean',
    'attempt-inverse-boolean',
    'history-inverse-boolean',
    'record-final-inverse-conflict',
    'attempt-index-boolean',
    'attempt-pair-index-booleans',
    'attempt-worker-index-booleans',
    'sample-sequence-boolean',
    'sample-identity-zero-hashes',
    'sample-walker-index-boolean',
    'sample-integrator-seed-boolean',
    'boundary-record-index-boolean',
    'boundary-report-clock-types',
    'boundary-report-clock-disagrees-with-sample',
    'boundary-report-clock-overflow',
    'boundary-report-walker-index-boolean',
    'initial-report-clock-types',
))
def test_multistate_r1_challenges_reject_inertly(valid_prefix, tmp_path, challenge):
    from atm_mlmm.persistence import read_json, write_json

    run = _clone_prefix(valid_prefix, tmp_path / challenge)
    initial = run / 'initial'
    boundary = run / 'boundaries/000000'
    initial_changed = False
    boundary_changed = False

    if challenge == 'steps-exclusive-limit':
        _write_metadata(run, lambda metadata: metadata.update(steps_per_boundary=1_000_000))
    elif challenge == 'boundaries-boolean':
        _write_metadata(run, lambda metadata: metadata.update(boundaries=True))
    elif challenge == 'steps-boolean':
        _write_metadata(run, lambda metadata: metadata.update(steps_per_boundary=True))
    elif challenge == 'worker-seed-overflows-later-walkers':
        _write_metadata(run, lambda metadata: metadata.update(integrator_seed_base=2**31 - 2))
    elif challenge == 'worker-seed-base-boolean':
        _write_metadata(run, lambda metadata: metadata.update(integrator_seed_base=True))
    elif challenge == 'host-seed-boolean':
        _write_metadata(run, lambda metadata: metadata.update(host_rng_seed=True))
    elif challenge == 'host-seed-api-exclusive-limit':
        _write_metadata(run, lambda metadata: metadata.update(host_rng_seed=2**31 - 10_000))
    elif challenge.startswith('python-gaussian-cache-'):
        rng_path = boundary / 'rng.json'
        _edit_json(rng_path, lambda document: document['python'].__setitem__(
            2, 'invalid-cache' if challenge.endswith('string') else (True if challenge.endswith('boolean') else 0.987654321)))
        if challenge.endswith('overflow'):
            rng_path.write_text(rng_path.read_text().replace('0.987654321', '1e309'))
        boundary_changed = True
    elif challenge == 'python-internal-word-boolean':
        _edit_json(boundary / 'rng.json', lambda document: document['python'][1].__setitem__(0, True))
        boundary_changed = True
    elif challenge == 'python-index-boolean':
        _edit_json(boundary / 'rng.json', lambda document: document['python'][1].__setitem__(-1, True))
        boundary_changed = True
    elif challenge == 'initial-record-inverse-boolean':
        _edit_json(initial / 'record.json', lambda document: document['state_to_walker'].__setitem__(1, True))
        initial_changed = True
    elif challenge == 'initial-inverse-document-boolean':
        _edit_json(initial / 'walker-to-state.json', lambda document: document['state_to_walker'].__setitem__(1, True))
        initial_changed = True
    elif challenge == 'boundary-inverse-document-boolean':
        _edit_json(boundary / 'walker-to-state.json', lambda document: document['state_to_walker'].__setitem__(0, True))
        boundary_changed = True
    elif challenge == 'attempt-inverse-boolean':
        _edit_json(boundary / 'attempts/0000/attempt.json',
            lambda document: document['state_to_walker_before'].__setitem__(1, True))
        boundary_changed = True
    elif challenge == 'history-inverse-boolean':
        _edit_json(boundary / 'attempts/0000/history.json',
            lambda document: document['resolved_state_to_walker'].__setitem__(1, True))
        boundary_changed = True
    elif challenge == 'record-final-inverse-conflict':
        _edit_json(boundary / 'record.json', lambda document: document.update(state_to_walker_final=[0, 1, 2]))
        boundary_changed = True
    elif challenge == 'attempt-index-boolean':
        _edit_json(boundary / 'attempts/0001/attempt.json', lambda document: document.update(attempt_index=True))
        boundary_changed = True
    elif challenge == 'attempt-pair-index-booleans':
        _edit_json(boundary / 'attempts/0000/attempt.json', lambda document: document.update(state_pair_indices=[False, True]))
        boundary_changed = True
    elif challenge == 'attempt-worker-index-booleans':
        _edit_json(boundary / 'attempts/0000/attempt.json', lambda document: document.update(worker_indices=[False, True]))
        boundary_changed = True
    elif challenge == 'sample-sequence-boolean':
        _edit_json(boundary / 'samples/worker-000.json', lambda document: document.update(sequence_number=True))
        boundary_changed = True
    elif challenge == 'sample-identity-zero-hashes':
        _edit_json(boundary / 'samples/worker-000.json', lambda document: document.update(
            physical_identity='0' * 64, transfer_identity='0' * 64))
        boundary_changed = True
    elif challenge == 'sample-walker-index-boolean':
        _edit_json(boundary / 'samples/worker-001.json', lambda document: document.update(walker_index=True))
        boundary_changed = True
    elif challenge == 'sample-integrator-seed-boolean':
        _edit_json(boundary / 'samples/worker-001.json', lambda document: document.update(integrator_seed=True))
        boundary_changed = True
    elif challenge == 'boundary-record-index-boolean':
        _edit_json(boundary / 'record.json', lambda document: document.update(boundary_index=False))
        boundary_changed = True
    elif challenge == 'boundary-report-clock-types':
        _edit_json(boundary / 'final-state-reports.json', lambda document: document['workers'][0].update(
            step=True, time_ps='invalid-time'))
        boundary_changed = True
    elif challenge == 'boundary-report-clock-disagrees-with-sample':
        _edit_json(boundary / 'final-state-reports.json', lambda document: document['workers'][0].update(
            time_ps=document['workers'][0]['time_ps'] + 0.25))
        boundary_changed = True
    elif challenge == 'boundary-report-clock-overflow':
        reports_path = boundary / 'final-state-reports.json'
        _edit_json(reports_path, lambda document: document['workers'][0].update(time_ps=0.987654321))
        reports_path.write_text(reports_path.read_text().replace('0.987654321', '1e309'))
        boundary_changed = True
    elif challenge == 'boundary-report-walker-index-boolean':
        _edit_json(boundary / 'final-state-reports.json', lambda document: document['workers'][1].update(
            walker_index=True))
        boundary_changed = True
    elif challenge == 'initial-report-clock-types':
        _edit_json(initial / 'final-state-reports.json', lambda document: document['workers'][1].update(
            step=True, time_ps='invalid-time'))
        initial_changed = True
    else:
        raise AssertionError(challenge)

    _reseal_initial_and_boundary(run, initial_changed=initial_changed, boundary_changed=boundary_changed)
    _challenge(run, challenge)


def test_multistate_public_run_rejects_unusable_worker_seed_before_output(valid_prefix, tmp_path, monkeypatch):
    from atm_mlmm import exchange as controller
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json, write_json
    from atm_mlmm.schema import MalformedInput

    prepared, _ = valid_prefix
    changed = tmp_path / 'prepared-invalid-seed'
    shutil.copytree(prepared, changed)
    metadata_path = changed / 'metadata.json'
    metadata = read_json(metadata_path)
    metadata['settings']['seed'] = 2**31 - 2
    write_json(metadata_path, metadata)
    (changed / 'metadata.sha256').write_text(sha(metadata_path) + '\n')
    output = tmp_path / 'must-remain-absent'
    loaded = []

    def forbidden(*args, **kwargs):
        loaded.append(kwargs.get('integrator_seed'))
        raise RuntimeError('worker loader called before seed range admission')

    monkeypatch.setattr(atom, 'load_worker_run', forbidden)
    caught = None
    try:
        controller.run_multistate_exchange(changed, output, state_ids=STATES, state_pairs=PAIRS,
            boundaries=1, steps_per_boundary=1, seed=73, trusted=True)
    except Exception as error:
        caught = error
    result = {
        'name': 'public-run-seed-base-overflows-worker-count',
        'error': None if caught is None else f'{type(caught).__name__}: {caught}',
        'loader_calls': loaded,
        'output_exists': output.exists(),
        'status': 'PASS' if isinstance(caught, MalformedInput) and not loaded and not output.exists() else 'VIOLATION',
    }
    _RESULTS.append(result)
    _write_results()
    assert isinstance(caught, MalformedInput), result
    assert loaded == [], result
    assert not output.exists(), result


@pytest.mark.parametrize('accepted', (False, True))
def test_multistate_r4_refreshed_total_must_match_matrix_on_both_decisions(
        valid_prefix, tmp_path, monkeypatch, accepted):
    from atm_mlmm import exchange_journal as journal
    from atm_mlmm.persistence import read_json, write_json
    from atom_openmm import gibbs_sampling

    prepared, _ = valid_prefix
    output = tmp_path / f'r4-accepted-{accepted}'
    draw = 0.0 if accepted else 1.0 - 1e-12
    with patch.object(gibbs_sampling, '_random', lambda: draw):
        from atm_mlmm.exchange import run_multistate_exchange
        run_multistate_exchange(prepared, output, state_ids=STATES, state_pairs=PAIRS,
            boundaries=1, steps_per_boundary=1, seed=73, trusted=True)
    boundary = output / 'boundaries/000000'
    decision = read_json(boundary / 'attempts/0000/decision.json')
    assert decision['accepted'] is accepted
    refreshed_path = boundary / 'attempts/0000/refreshed.json'
    _edit_json(refreshed_path, lambda document: document['energies_after_kj_mol'].__setitem__(
        0, document['energies_after_kj_mol'][0] + 123.0))
    journal.seal_tree(boundary, index=0)
    _challenge(output, f'refreshed-plus-123-decision-accepted-{accepted}')


@pytest.mark.parametrize('tamper', ('added', 'modified-after-seal'))
def test_multistate_r7_nested_attempt_manifest_is_rejected(valid_prefix, tmp_path, tamper):
    from atm_mlmm import exchange_journal as journal

    run = _clone_prefix(valid_prefix, tmp_path / f'nested-manifest-{tamper}')
    boundary = run / 'boundaries/000000'
    nested = boundary / 'attempts/0000/manifest.json'
    nested.write_text('{"attempt_manifest":"nested bytes"}\n')
    journal.seal_tree(boundary, index=0)
    if tamper == 'modified-after-seal':
        nested.write_text('{"attempt_manifest":"modified nested bytes"}\n')
    _challenge(run, f'nested-manifest-{tamper}')


def test_valid_eight_state_selection_and_finite_gaussian_cache_roundtrip(valid_prefix, tmp_path):
    from atm_mlmm import exchange as controller
    from atm_mlmm import exchange_journal as journal
    from atm_mlmm.persistence import read_json, write_json

    states = tuple(f's-{index}' for index in range(8))
    pairs = tuple((left, right) for left in range(8) for right in range(left + 1, 8))
    assert controller._multistate_selection(states, pairs) == (states, pairs)

    run = _clone_prefix(valid_prefix, tmp_path / 'finite-gaussian-cache')
    path = run / 'boundaries/000000/rng.json'
    document = read_json(path)
    source = random.Random(31)
    source.gauss(0.0, 1.0)
    document['python'] = json.loads(json.dumps(source.getstate()))
    write_json(path, document)
    journal.seal_tree(run / 'boundaries/000000', index=0)
    rows = journal.read_multistate_boundaries(run)
    restored, _ = controller._rng_from_document(document)
    assert len(rows) == 1
    assert source.gauss(0.0, 1.0) == restored.gauss(0.0, 1.0)
