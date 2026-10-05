"""Independent G09-R2 closure challenges on actual one-step workers."""
from pathlib import Path
import json
import sys

import openmm as mm
import pytest

from atm_mlmm.schema import NumericalDomainError, from_json
from tests.workflow.test_failure_archive_errors import failing_attempt

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT/'Worker_Log/Milestone_05/evidence/G09_v4_independent'


def setup(tmp_path,monkeypatch):
    out,primary,execute = failing_attempt(tmp_path,monkeypatch,'independent')
    fired = {'value':False}
    original_step = mm.LangevinMiddleIntegrator.step
    def step(integrator,*args):
        try:
            return original_step(integrator,*args)
        finally:
            fired['value'] = True
    monkeypatch.setattr(mm.LangevinMiddleIntegrator,'step',step)
    return out,primary,execute,fired


def assert_metadata(out,primary):
    metadata = json.loads((out/'failure-000000/error.json').read_text())
    assert metadata['error_type'] == type(primary).__name__ == 'NumericalDomainError'
    assert metadata['message'] == str(primary) == 'original scientific trigger'
    assert metadata['state_id'] == 'first'
    assert metadata['walker_id'] == 'R2:first'
    assert metadata['attempted_sample_id'] == 'R2:first:1'
    assert metadata['sequence_number'] == 1 and metadata['journal_index'] == 0
    bundle = from_json((out/'worker/bundle.json').read_text())
    assert metadata['transfer_identity'] == bundle.transfer.content_identity
    assert not (out/'samples').exists()
    return metadata


def catch_original(execute,primary):
    with pytest.raises(NumericalDomainError) as caught:
        execute()
    assert caught.value is primary
    assert str(primary) == 'original scientific trigger'
    traceback_names = []
    trace = caught.value.__traceback__
    while trace is not None:
        traceback_names.append(trace.tb_frame.f_code.co_name)
        trace = trace.tb_next
    assert '_execute' in traceback_names and 'step' in traceback_names


@pytest.mark.parametrize('fault',('unavailable_both','multiple_writes','primary_metadata','metadata_update'))
def test_combined_and_metadata_failures_keep_primary_and_available_artifacts(tmp_path,monkeypatch,fault):
    import atm_mlmm.workflow as workflow
    from atm_mlmm.__main__ import main
    out,primary,execute,fired = setup(tmp_path,monkeypatch)
    state = mm.Context.getState
    checkpoint = mm.Context.createCheckpoint
    write_text = Path.write_text
    write_bytes = Path.write_bytes
    write_json = workflow.write_json
    calls = {'metadata':0}
    def get_state(context,*args,**kwargs):
        if fired['value']:
            assert not (kwargs.get('getEnergy') or kwargs.get('getForces'))
            if fault == 'unavailable_both':
                raise OSError('independent State unavailable')
        return state(context,*args,**kwargs)
    def get_checkpoint(context):
        if fired['value'] and fault == 'unavailable_both':
            raise RuntimeError('independent checkpoint unavailable')
        return checkpoint(context)
    def text(path,*args,**kwargs):
        if fired['value'] and fault == 'multiple_writes' and path.name in ('state.xml','map0-state.xml'):
            raise OSError(f'independent write unavailable: {path.name}')
        return write_text(path,*args,**kwargs)
    def binary(path,*args,**kwargs):
        if fired['value'] and fault == 'multiple_writes' and path.name == 'checkpoint.chk':
            raise OSError('independent write unavailable: checkpoint.chk')
        return write_bytes(path,*args,**kwargs)
    def metadata(path,*args,**kwargs):
        if fired['value'] and path.name == 'error.json':
            calls['metadata'] += 1
            if (fault == 'primary_metadata' and calls['metadata'] == 1) or (fault == 'metadata_update' and calls['metadata'] == 2):
                raise OSError(f'independent {fault} write unavailable')
        return write_json(path,*args,**kwargs)
    monkeypatch.setattr(mm.Context,'getState',get_state)
    monkeypatch.setattr(mm.Context,'createCheckpoint',get_checkpoint)
    monkeypatch.setattr(Path,'write_text',text)
    monkeypatch.setattr(Path,'write_bytes',binary)
    monkeypatch.setattr(workflow,'write_json',metadata)
    def resume(*args,**kwargs):
        try:
            execute()
        except Exception as caught:
            assert caught is primary
            assert '_execute' in [entry.name for entry in __import__('traceback').extract_tb(caught.__traceback__)]
            raise
    monkeypatch.setattr(workflow,'resume_run',resume)
    monkeypatch.setattr(sys,'argv',['atm_mlmm','resume',str(out),'--trusted'])
    from io import StringIO
    from contextlib import redirect_stderr, redirect_stdout
    stderr,stdout = StringIO(),StringIO()
    with redirect_stderr(stderr),redirect_stdout(stdout):
        assert main() == 2
    assert stdout.getvalue() == ''
    assert stderr.getvalue().startswith('NumericalDomainError: original scientific trigger\n')
    count = 2 if fault == 'unavailable_both' else (3 if fault == 'multiple_writes' else 1)
    assert len(primary.__notes__) == count
    assert stderr.getvalue().count('Failure archive (') == count
    report = assert_metadata(out,primary)
    names = set(p.name for p in (out/'failure-000000').iterdir())
    if fault == 'unavailable_both':
        assert names == {'error.json'}
        assert report['actual_step'] == 1 and report['actual_time_ps'] is None
        assert {e['error_type'] for e in report['archive_errors']} == {'OSError','RuntimeError'}
    elif fault == 'multiple_writes':
        assert names == {'error.json','map1-state.xml'}
        assert report['actual_step'] == 1 and report['actual_time_ps'] == .0005
        assert {e['operation'] for e in report['archive_errors']} == {'write state.xml','write checkpoint.chk','write map0-state.xml'}
    else:
        assert names == {'error.json','state.xml','checkpoint.chk','map0-state.xml','map1-state.xml'}
        if fault == 'primary_metadata':
            assert report['actual_step'] == 1 and report['actual_time_ps'] == .0005
            assert report['archive_errors'][0]['operation'] == 'write primary error.json'
        else:
            assert report['actual_step'] is None and report['actual_time_ps'] is None
            assert report['archive_errors'] == []  # primary record survives failed atomic update
            assert 'Failure archive (update error.json)' in stderr.getvalue()
    (EVIDENCE/f'{fault}.json').write_text(json.dumps({'cli_stderr':stderr.getvalue(),'metadata':report,'surviving_files':sorted(names)},indent=2)+'\n')


def test_existing_failure_directory_is_preserved_without_archive_reads(tmp_path,monkeypatch):
    out,primary,execute,fired = setup(tmp_path,monkeypatch)
    failed = out/'failure-000000'
    failed.mkdir()
    for name in ('error.json','state.xml','checkpoint.chk','map0-state.xml','map1-state.xml','unrelated.txt'):
        (failed/name).write_bytes(b'pre-existing evidence: '+name.encode())
    original = {p.name:p.read_bytes() for p in failed.iterdir()}
    state = mm.Context.getState
    checkpoint = mm.Context.createCheckpoint
    def no_state(context,*args,**kwargs):
        assert not fired['value'], 'archive must not touch a conflicting directory or request State'
        return state(context,*args,**kwargs)
    def no_checkpoint(context):
        assert not fired['value'], 'archive must not request checkpoint after directory conflict'
        return checkpoint(context)
    monkeypatch.setattr(mm.Context,'getState',no_state)
    monkeypatch.setattr(mm.Context,'createCheckpoint',no_checkpoint)
    catch_original(execute,primary)
    assert {p.name:p.read_bytes() for p in failed.iterdir()} == original
    assert len(primary.__notes__) == 1 and 'FileExistsError' in primary.__notes__[0]
    assert 'create failure directory' in primary.__notes__[0]
    assert not (out/'samples').exists()


def test_nonfinite_cached_time_is_explicit_and_other_artifacts_survive(tmp_path,monkeypatch):
    import atm_mlmm.workflow as workflow
    out,primary,execute,_ = setup(tmp_path,monkeypatch)
    archive = workflow._archive_failure
    def invalid_time(directory,worker,error,identifiers):
        worker.evaluator.context.setTime(float('nan'))
        return archive(directory,worker,error,identifiers)
    monkeypatch.setattr(workflow,'_archive_failure',invalid_time)
    catch_original(execute,primary)
    report = assert_metadata(out,primary)
    assert report['actual_step'] == 1 and report['actual_time_ps'] is None
    assert report['archive_errors'] == [{'operation':'read cached State time','error_type':'NumericalDomainError','message':'nonfinite cached State time'}]
    assert {p.name for p in (out/'failure-000000').iterdir()} == {'error.json','state.xml','checkpoint.chk','map0-state.xml','map1-state.xml'}
