"""Restored fixed-window state is admitted before energy evaluation or stepping."""
import hashlib
import json

import numpy as np
import pytest

from tests.workflow.test_engine_restart import _analytic_fixed_window


def _mutate_checkpoint(output, mutate, *, align_saved_record=False):
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.persistence import read_json, write_json
    from atm_mlmm.workflow import _snapshot
    import openmm as mm

    output = output
    metadata = read_json(output/'metadata.json')
    chunk = output/'samples/000000'
    row = read_json(chunk/'record.json')
    checkpoint = chunk/'checkpoint.chk'
    with load_worker_run(output/'worker', metadata['worker_manifest_sha256'], trusted=True,
                         integrator_seed=row['integrator_seed']) as worker:
        worker.restore_checkpoint(checkpoint.read_bytes(), row['state_id'])
        mutate(worker, row)
        portable_payload = None
        if align_saved_record:
            saved = worker.evaluator.context.getState(
                getPositions=True, getVelocities=True, getParameters=True)
            snapshot = _snapshot(worker)
            row['positions_nm'] = tuple(tuple(float(value) for value in vector)
                                        for vector in snapshot.positions_nm)
            row['velocities_nm_ps'] = tuple(tuple(float(value) for value in vector)
                                            for vector in snapshot.velocities_nm_ps)
            row['box_nm'] = (None if snapshot.box_nm is None else
                             tuple(tuple(float(value) for value in vector) for vector in snapshot.box_nm))
            portable_payload = mm.XmlSerializer.serialize(saved)
        payload = worker.evaluator.context.createCheckpoint()
    checkpoint.write_bytes(payload)
    manifest_path = chunk/'manifest.json'
    manifest = read_json(manifest_path)
    manifest['files']['checkpoint.chk'] = hashlib.sha256(payload).hexdigest()
    if portable_payload is not None:
        state_path = chunk/'state.xml'
        state_path.write_text(portable_payload)
        write_json(chunk/'record.json', row)
        manifest['files']['record.json'] = hashlib.sha256((chunk/'record.json').read_bytes()).hexdigest()
        manifest['files']['state.xml'] = hashlib.sha256(state_path.read_bytes()).hexdigest()
    write_json(manifest_path, manifest)
    return row


def _watch_admission_calls(monkeypatch):
    import openmm as mm
    from atm_mlmm.adapters import atom

    calls = {'energy': 0, 'steps': []}
    original_evaluate = atom.WorkerRun.evaluate
    original_step = mm.LangevinMiddleIntegrator.step

    def evaluate(self, *args, **kwargs):
        calls['energy'] += 1
        return original_evaluate(self, *args, **kwargs)

    def step(self, count):
        calls['steps'].append(count)
        return original_step(self, count)

    monkeypatch.setattr(atom.WorkerRun, 'evaluate', evaluate)
    monkeypatch.setattr(mm.LangevinMiddleIntegrator, 'step', step)
    return calls


@pytest.mark.parametrize('map_index', (0, 1))
def test_invalid_restored_geometry_rejects_before_step(tmp_path, monkeypatch, map_index):
    import openmm as mm
    from openmm import unit
    from atm_mlmm.schema import NumericalDomainError
    from atm_mlmm.workflow import resume_run

    output = _analytic_fixed_window(tmp_path/'fixed')

    def overlap(worker, _row):
        physical = worker.bundle.physical
        context = worker.evaluator.context
        state = context.getState(getPositions=True)
        positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        ligand_index = physical.real_to_final['b1']
        protein_index = physical.real_to_final['protein']
        if map_index == 0:
            positions[protein_index] = positions[ligand_index]
        else:
            displacement = np.asarray(worker.bundle.transfer.protocol.geometry_requests['displacement_nm'])
            positions[protein_index] = positions[ligand_index] - displacement
        context.setPositions(positions*unit.nanometer)
        context.computeVirtualSites()

    row = _mutate_checkpoint(output, overlap, align_saved_record=True)
    assert row['state_id'] == 'first'
    calls = _watch_admission_calls(monkeypatch)
    with pytest.raises(NumericalDomainError, match=f'map{map_index} intermolecular Bondi ratio'):
        resume_run(output, trusted=True)
    assert calls == {'energy': 0, 'steps': []}
    failure = output/'failure-000001'
    assert (failure/'state.xml').is_file() and (failure/'checkpoint.chk').is_file()
    assert json.loads((failure/'error.json').read_text())['error_type'] == 'NumericalDomainError'


def test_restored_checkpoint_time_must_match_saved_state(tmp_path, monkeypatch):
    import openmm as mm
    from openmm import unit
    from atm_mlmm.schema import IdentityError
    from atm_mlmm.workflow import resume_run

    output = _analytic_fixed_window(tmp_path/'fixed')

    def move_time(worker, _row):
        worker.evaluator.context.setTime(1.0005*unit.picosecond)

    row = _mutate_checkpoint(output, move_time)
    assert row['step'] == 1 and row['time_ps'] == .0005
    calls = _watch_admission_calls(monkeypatch)
    with pytest.raises(IdentityError, match='clock|time'):
        resume_run(output, trusted=True)
    assert calls == {'energy': 0, 'steps': []}


@pytest.mark.parametrize('field', ('positions_nm', 'velocities_nm_ps', 'box_nm', 'parameters'))
def test_saved_row_must_match_actual_restored_state(tmp_path, monkeypatch, field):
    from atm_mlmm.persistence import read_json, write_json
    from atm_mlmm.schema import IdentityError
    from atm_mlmm.workflow import resume_run

    output = _analytic_fixed_window(tmp_path/'fixed')
    chunk = output/'samples/000000'
    row_path = chunk/'record.json'
    row = read_json(row_path)
    if field == 'positions_nm':
        row[field][0][0] += .001
    elif field == 'velocities_nm_ps':
        row[field][0][0] += .1
    elif field == 'box_nm':
        row[field] = [[3.2, 0., 0.], [0., 3.2, 0.], [0., 0., 3.2]]
    else:
        row[field]['Lambda1'] += .01
    write_json(row_path, row)
    manifest_path = chunk/'manifest.json'
    manifest = read_json(manifest_path)
    manifest['files']['record.json'] = hashlib.sha256(row_path.read_bytes()).hexdigest()
    write_json(manifest_path, manifest)

    calls = _watch_admission_calls(monkeypatch)
    with pytest.raises(IdentityError, match='saved|sample|coordinates|velocities|box|parameters'):
        resume_run(output, trusted=True)
    assert calls == {'energy': 0, 'steps': []}


def test_fresh_valid_prefix_continues_with_exact_saved_history(tmp_path):
    from atm_mlmm.persistence import read_sample_chunks
    from atm_mlmm.workflow import resume_run

    output = _analytic_fixed_window(tmp_path/'fixed')
    summary = resume_run(output, trusted=True)
    rows = read_sample_chunks(output/'samples')
    assert summary['status'] == 'complete'
    assert len(rows) == 4
    assert [(row['state_id'], row['sequence_number'], row['step'], row['time_ps']) for row in rows] == [
        ('first', 1, 1, .0005), ('first', 2, 2, .001),
        ('second', 1, 1, .0005), ('second', 2, 2, .001),
    ]
