"""Secondary archive faults must preserve the primary actual-worker failure."""
import json
import os
from pathlib import Path
import sys

import openmm as mm
import pytest

from atm_mlmm.schema import NumericalDomainError
from tests.analytic_oracle import REFERENCE
from tests.workflow.test_atom_force_routing import atom_case


def failing_attempt(tmp_path, monkeypatch, boundary):
    import atm_mlmm.adapters.atom as adapter
    import atm_mlmm.workflow as workflow
    physical, transfer, schedule, restraints, snapshot = atom_case('abfe')
    out = tmp_path / 'attempt'
    with adapter.build_atom(physical, transfer, schedule, restraints, REFERENCE) as source:
        _, digest = adapter.export_worker_run(source, out/'worker', snapshot, 'first')
    primary = NumericalDomainError('original scientific trigger')
    fired = {'value': False}
    normal_step = mm.LangevinMiddleIntegrator.step
    normal_state = mm.Context.getState
    normal_checkpoint = mm.Context.createCheckpoint
    normal_count = mm.Context.getStepCount
    normal_serialize = mm.XmlSerializer.serialize
    normal_write_text = Path.write_text
    normal_write_bytes = Path.write_bytes
    normal_mkdir = Path.mkdir
    normal_replace = os.replace

    def fault():
        raise OSError(f'archive trigger: {boundary}')

    def step(integrator, steps):
        normal_step(integrator, steps)
        fired['value'] = True
        raise primary

    def state(context, *args, **kwargs):
        if fired['value']:
            assert not (kwargs.get('getEnergy') or kwargs.get('getForces')), 'scientific evaluation reentry'
            if boundary == 'cached_state':
                fault()
        return normal_state(context, *args, **kwargs)

    def checkpoint(context):
        if fired['value'] and boundary == 'checkpoint_capture':
            fault()
        return normal_checkpoint(context)

    def count(context):
        if fired['value'] and boundary == 'step_count':
            fault()
        return normal_count(context)

    def serialize(value):
        if fired['value'] and boundary == 'serialization':
            fault()
        return normal_serialize(value)

    def write_text(path, *args, **kwargs):
        if fired['value'] and path.name == boundary:
            fault()
        return normal_write_text(path, *args, **kwargs)

    def write_bytes(path, *args, **kwargs):
        if fired['value'] and path.name == boundary:
            fault()
        return normal_write_bytes(path, *args, **kwargs)

    def mkdir(path, *args, **kwargs):
        if fired['value'] and boundary == 'mkdir' and path.name == 'failure-000000':
            fault()
        return normal_mkdir(path, *args, **kwargs)

    def replace(source, destination):
        if fired['value'] and Path(destination).name == boundary:
            fault()
        return normal_replace(source, destination)

    monkeypatch.setattr(mm.LangevinMiddleIntegrator, 'step', step)
    monkeypatch.setattr(mm.Context, 'getState', state)
    monkeypatch.setattr(mm.Context, 'createCheckpoint', checkpoint)
    monkeypatch.setattr(mm.Context, 'getStepCount', count)
    monkeypatch.setattr(mm.XmlSerializer, 'serialize', serialize)
    monkeypatch.setattr(Path, 'write_text', write_text)
    monkeypatch.setattr(Path, 'write_bytes', write_bytes)
    monkeypatch.setattr(Path, 'mkdir', mkdir)
    monkeypatch.setattr(os, 'replace', replace)
    monkeypatch.setattr(workflow, '_domain', lambda *args: [])
    metadata = {'settings': {'frames_per_state': 1, 'steps_per_frame': 1, 'seed': 41,
                            'displacement_nm': [.3, 0., 0.], 'protocol_kind': 'abfe'},
                'worker_manifest_sha256': digest, 'run_id': 'R2',
                'runtime_identity': REFERENCE.content_identity, 'profile': {}}
    return out, primary, lambda: workflow._execute(out, metadata)


@pytest.mark.parametrize('boundary', (
    'mkdir', 'step_count', 'cached_state', 'serialization', 'state.xml',
    'checkpoint_capture', 'checkpoint.chk', 'map0-state.xml', 'map1-state.xml', 'error.json',
))
def test_secondary_archive_error_keeps_primary_and_available_artifacts(tmp_path, monkeypatch, boundary):
    out, primary, execute = failing_attempt(tmp_path, monkeypatch, boundary)
    with pytest.raises(NumericalDomainError) as caught:
        execute()
    assert caught.value is primary
    assert str(primary) == 'original scientific trigger'
    assert any(f'OSError: archive trigger: {boundary}' in note for note in primary.__notes__)
    assert not (out/'samples').exists()
    failed = out/'failure-000000'
    if boundary == 'mkdir':
        assert not failed.exists()
        return
    state_available = boundary not in ('cached_state', 'serialization')
    for name in ('state.xml', 'map0-state.xml', 'map1-state.xml'):
        assert (failed/name).exists() == (state_available and boundary != name)
    assert (failed/'checkpoint.chk').exists() == (boundary not in ('checkpoint_capture', 'checkpoint.chk'))
    if boundary == 'error.json':
        assert not (failed/'error.json').exists()
        return
    error = json.loads((failed/'error.json').read_text())
    assert error['error_type'] == 'NumericalDomainError'
    assert error['message'] == 'original scientific trigger'
    assert error['attempted_sample_id'] == 'R2:first:1'
    assert error['walker_id'] == 'R2:first' and error['state_id'] == 'first'
    assert error['actual_step'] == (None if boundary == 'step_count' else 1)
    assert error['actual_time_ps'] == (None if boundary == 'cached_state' else .0005)
    assert any(item['error_type'] == 'OSError' and item['message'] == f'archive trigger: {boundary}'
               for item in error['archive_errors'])


@pytest.mark.parametrize('boundary', ('map1-state.xml', 'error.json'))
def test_normal_cli_surfaces_primary_and_secondary_archive_errors(tmp_path, monkeypatch, capsys, boundary):
    import atm_mlmm.workflow as workflow
    from atm_mlmm.__main__ import main
    out, primary, execute = failing_attempt(tmp_path, monkeypatch, boundary)

    def resume(*args, **kwargs):
        try:
            execute()
        except Exception as error:
            assert error is primary
            raise

    monkeypatch.setattr(workflow, 'resume_run', resume)
    monkeypatch.setattr(sys, 'argv', ['atm_mlmm', 'resume', str(out), '--trusted'])
    assert main() == 2
    output = capsys.readouterr()
    assert output.out == ''
    assert 'NumericalDomainError: original scientific trigger' in output.err
    assert f'OSError: archive trigger: {boundary}' in output.err
    assert not (out/'samples').exists()
