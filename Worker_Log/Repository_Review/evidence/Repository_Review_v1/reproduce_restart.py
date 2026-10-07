"""Four preselected admission diagnostics; no changes to reviewed code."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import traceback
from unittest.mock import patch
import uuid

import numpy as np
import openmm as mm
from openmm import unit

from atm_mlmm.adapters.atom import load_worker_run
from atm_mlmm.exchange import run_exchange, resume_exchange, read_exchange_rounds
from atm_mlmm.persistence import read_json, write_json, read_sample_chunks
from atm_mlmm.workflow import _execute, _domain, _snapshot, resume_run
from tests.workflow.test_persistent_exchange import prepare_multistate

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'restart-attempt-001'
ROOT.mkdir(exist_ok=False)
RESULTS = []


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata_write(root, metadata):
    write_json(root / 'metadata.json', metadata)
    (root / 'metadata.sha256').write_text(digest(root / 'metadata.json') + '\n')


def fresh(name, *, fixed=False):
    root = ROOT / name
    prepare_multistate(root)
    metadata = read_json(root / 'metadata.json')
    if fixed:
        metadata['run_id'] = uuid.uuid4().hex
        metadata['settings'].update(frames_per_state=2, steps_per_frame=1)
        metadata_write(root, metadata)
        result = _execute(root, metadata, stop_after_samples=1)
        assert result['status'] == 'interrupted' and result['samples'] == 1
    return root, metadata


def alter_clock(root, metadata, checkpoint, state_id):
    checkpoint.with_name(checkpoint.name + '.original').write_bytes(checkpoint.read_bytes())
    with load_worker_run(root / 'worker', metadata['worker_manifest_sha256'], trusted=True) as worker:
        worker.restore_checkpoint(checkpoint.read_bytes(), state_id)
        context = worker.evaluator.context
        before = context.getState(getPositions=True, getVelocities=True, getParameters=True)
        original_time = before.getTime().value_in_unit(unit.picosecond)
        context.setTime((original_time + 1.) * unit.picosecond)
        after = context.getState(getPositions=True, getVelocities=True, getParameters=True)
        assert before.getStepCount() == after.getStepCount()
        assert dict(before.getParameters()) == dict(after.getParameters())
        for method, units in (('getPositions', unit.nanometer), ('getVelocities', unit.nanometer / unit.picosecond)):
            np.testing.assert_array_equal(getattr(before, method)(asNumpy=True).value_in_unit(units),
                                          getattr(after, method)(asNumpy=True).value_in_unit(units))
        payload = context.createCheckpoint()
    checkpoint.write_bytes(payload)
    return {'original_time_ps': original_time, 'altered_time_ps': original_time + 1.,
            'step': before.getStepCount(), 'other_observables_unchanged': True,
            'original_checkpoint_sha256': digest(checkpoint.with_name(checkpoint.name + '.original')),
            'altered_checkpoint_sha256': digest(checkpoint)}


def rehash_checkpoint(directory, name):
    manifest = directory / 'manifest.json'
    # Original bytes are outside the journal so its exact file inventory stays valid.
    (ROOT / (directory.parent.parent.name + '-' + directory.name + '-manifest.original.json')).write_bytes(manifest.read_bytes())
    document = read_json(manifest)
    document['files'][name] = digest(directory / name)
    write_json(manifest, document)


def fixed_clock():
    root, metadata = fresh('fixed-clock', fixed=True)
    chunk = root / 'samples/000000'
    saved = read_json(chunk / 'record.json')
    mutation = alter_clock(root, metadata, chunk / 'checkpoint.chk', saved['state_id'])
    # Move the preserved copy outside the committed chunk's inventory.
    (chunk / 'checkpoint.chk.original').rename(ROOT / 'fixed-clock-checkpoint.original.chk')
    rehash_checkpoint(chunk, 'checkpoint.chk')
    result = resume_run(root, trusted=True)
    rows = read_sample_chunks(root / 'samples')
    actual = rows[1]['time_ps'] - rows[0]['time_ps']
    expected = (rows[1]['step'] - rows[0]['step']) * .0005
    return {'case': 'fixed_clock', 'expected': 'reject before stepping: checkpoint time disagrees with saved sample and State',
            'actual': result['status'], 'mutation': mutation, 'saved_time_ps': saved['time_ps'],
            'next_time_ps': rows[1]['time_ps'], 'expected_elapsed_ps': expected, 'actual_elapsed_ps': actual,
            'defect_reproduced': result['status'] == 'complete' and abs(actual - expected) > .9}


def source_omission():
    root, metadata = fresh('fixed-source-omission', fixed=True)
    path = root / 'worker/manifest.json'
    (ROOT / 'source-manifest.original.json').write_bytes(path.read_bytes())
    manifest = read_json(path)
    omitted = 'runtime/source/atm_mlmm/chemical_reference.py'
    assert omitted in manifest['files']
    del manifest['files'][omitted]
    write_json(path, manifest)
    metadata['worker_manifest_sha256'] = digest(path)
    metadata_write(root, metadata)
    sentinel = {'execution_reached': True}
    with patch('atm_mlmm.workflow._execute', return_value=sentinel):
        result = resume_run(root, trusted=True)
    return {'case': 'fixed_source_omission', 'expected': 'reject incomplete bundled source inventory before execution',
            'actual': result, 'omitted': omitted, 'remaining_source_entries': sum(
                name.startswith('runtime/source/atm_mlmm/') for name in manifest['files']),
            'proof_kind': 'admission control-flow sentinel; no continuation or numerical claim',
            'defect_reproduced': result is sentinel}


def geometry_before_step():
    root, metadata = fresh('fixed-invalid-geometry', fixed=True)
    chunk = root / 'samples/000000'
    row = read_json(chunk / 'record.json')
    (ROOT / 'geometry-checkpoint.original.chk').write_bytes((chunk / 'checkpoint.chk').read_bytes())
    with load_worker_run(root / 'worker', metadata['worker_manifest_sha256'], trusted=True) as worker:
        worker.restore_checkpoint((chunk / 'checkpoint.chk').read_bytes(), row['state_id'])
        snapshot = _snapshot(worker)
        x = np.array(snapshot.positions_nm)
        # Put one atom of bulk ligand B on the stationary protein atom.
        x[snapshot.real_atom_ids.index('b1')] = x[snapshot.real_atom_ids.index('protein')]
        changed = replace(snapshot, positions_nm=x)
        positions = np.array(worker.evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer))
        positions[list(worker.bundle.physical.old_to_new)] = x
        worker.evaluator.context.setPositions(positions * unit.nanometer)
        try:
            _domain(worker.bundle.physical.topology, changed, metadata['settings']['displacement_nm'], 'rbfe')
        except Exception as error:
            oracle_rejection = str(error)
        else:
            raise AssertionError('selected invalid geometry was not rejected by the declared guard')
        (chunk / 'checkpoint.chk').write_bytes(worker.evaluator.context.createCheckpoint())
    rehash_checkpoint(chunk, 'checkpoint.chk')
    entered = []
    class StepSentinel(RuntimeError):
        pass
    def forbid_step(integrator, count):
        entered.append(count)
        raise StepSentinel('integration reached before restored geometry admission')
    rejection = None
    with patch.object(mm.LangevinMiddleIntegrator, 'step', forbid_step):
        try:
            resume_run(root, trusted=True)
        except Exception as error:
            rejection = {'type': type(error).__name__, 'message': str(error)}
    return {'case': 'fixed_geometry_before_step', 'expected': 'geometry guard rejects before integration',
            'oracle_rejection': oracle_rejection, 'actual_exception': rejection,
            'integration_calls': entered, 'invalid_geometry_steps_executed': 0,
            'defect_reproduced': entered == [1] and rejection['type'] == 'StepSentinel'}


def pair_clock():
    prepared, _ = fresh('pair-preparation')
    root = ROOT / 'pair-clock'
    result = run_exchange(prepared, root, rounds=2, steps_per_round=1, seed=73, trusted=True, stop_after_rounds=1)
    assert result['status'] == 'interrupted'
    metadata = read_json(root / 'metadata.json')
    boundary = root / 'rounds/000000'
    rows = read_exchange_rounds(root)
    mutation = alter_clock(root, metadata, boundary / 'worker-0.chk', rows[-1]['state_ids_after'][0])
    (boundary / 'worker-0.chk.original').rename(ROOT / 'pair-clock-checkpoint.original.chk')
    rehash_checkpoint(boundary, 'worker-0.chk')
    # This inert journal check still accepts the altered boundary.
    assert len(read_exchange_rounds(root)) == 1
    result = resume_exchange(root, trusted=True)
    rows = read_exchange_rounds(root)
    first, second = rows[0]['samples'][0], rows[1]['samples'][0]
    expected = (second['step'] - first['step']) * .0005
    actual = second['time_ps'] - first['time_ps']
    return {'case': 'pair_clock', 'expected': 'reject checkpoint time inconsistent with prior sample/portable State before stepping',
            'actual': result['status'], 'mutation': mutation, 'expected_elapsed_ps': expected,
            'actual_elapsed_ps': actual, 'defect_reproduced': result['status'] == 'complete' and abs(actual - expected) > .9}


for diagnostic in (fixed_clock, source_omission, geometry_before_step, pair_clock):
    try:
        result = diagnostic()
    except Exception as error:
        result = {'case': diagnostic.__name__, 'blocked': type(error).__name__ + ': ' + str(error),
                  'traceback': traceback.format_exc(), 'defect_reproduced': False}
    RESULTS.append(result)
    write_json(HERE / 'restart-results.json', RESULTS)
    print(json.dumps(result, indent=2), flush=True)

# Zero means the preselected diagnostic completed; confirmed defects are findings.
raise SystemExit(0 if all(result['defect_reproduced'] for result in RESULTS) else 2)
