"""Exact same-profile continuation and conservative raw-journal failures."""
import json
from pathlib import Path
import shutil
import numpy as np
import pytest
from tests.workflow.test_cloud_host_guest import FIXTURE


def test_interrupted_actual_workers_resume_without_duplicate_or_lost_samples(tmp_path):
    from atm_mlmm.workflow import run_configuration, resume_run, _execute
    from atm_mlmm.persistence import read_sample_chunks
    base = json.loads((FIXTURE/'config.json').read_text())
    base['input_manifest'] = str(FIXTURE/'manifest.json')
    base['settings'].update(frames_per_state=2,steps_per_frame=1,minimization_iterations=3)
    path = tmp_path/'config.json'
    path.write_text(json.dumps(base))
    complete, interrupted = tmp_path/'complete', tmp_path/'interrupted'
    first = run_configuration(path,interrupted,trusted=True,stop_after_samples=1)
    assert first['status'] == 'interrupted'
    assert len(read_sample_chunks(interrupted/'samples')) == 1
    # Independent minimizations may differ at floating-point roundoff, including
    # the resulting anchor center. Compare continuation from the same exact
    # prepared System/State and seed, not two independently assembled bundles.
    complete.mkdir()
    shutil.copytree(interrupted/'worker',complete/'worker')
    metadata=json.loads((interrupted/'metadata.json').read_text())
    reference_metadata={**metadata,'run_id':metadata['run_id']+':reference'}
    _execute(complete,reference_metadata)
    final = resume_run(interrupted,trusted=True)
    assert final['status'] == 'complete'
    a,b = (read_sample_chunks(p/'samples') for p in (complete,interrupted))
    assert len(a) == len(b) == 6
    for original,resumed in zip(a,b):
        for key in ('state_id','sequence_number','step','time_ps','parameters','raw'):
            assert resumed[key] == original[key]
        np.testing.assert_array_equal(original['positions_nm'],resumed['positions_nm'])
        np.testing.assert_array_equal(original['velocities_nm_ps'],resumed['velocities_nm_ps'])
        np.testing.assert_array_equal(original['real_forces_kj_mol_nm'],resumed['real_forces_kj_mol_nm'])
    # A repeated resume is a read/verification of the completed prefix.
    assert resume_run(interrupted,trusted=True)['samples'] == 6


def test_journal_rejects_tampering_and_preserves_incomplete_transactions(tmp_path):
    from atm_mlmm.persistence import commit_sample_chunk, read_sample_chunks
    from atm_mlmm.schema import IdentityError
    record = {'sample_id':'sample-0','walker_id':'walker','sequence_number':1}
    chunk = commit_sample_chunk(tmp_path,0,record,'<State/>',b'checkpoint')
    assert read_sample_chunks(tmp_path) == [record]
    with pytest.raises(FileExistsError):
        commit_sample_chunk(tmp_path,0,record,'<State/>',b'checkpoint')
    (chunk/'checkpoint.chk').write_bytes(b'changed')
    with pytest.raises(IdentityError,match='mismatch'):
        read_sample_chunks(tmp_path)
    pending = tmp_path/'.pending-000001-failure'
    pending.mkdir()
    (pending/'raw.json').write_text('{"failure":"preserved"}')
    with pytest.raises(IdentityError,match='incomplete'):
        read_sample_chunks(tmp_path)
    assert (pending/'raw.json').exists()


def test_failed_counterfactual_is_saved_without_retriggering_failed_energy(tmp_path,monkeypatch):
    from atm_mlmm.adapters.atom import build_atom,export_worker_run
    from atm_mlmm.workflow import _execute
    import atm_mlmm.workflow as workflow
    from atm_mlmm.schema import NumericalDomainError
    from tests.workflow.test_atom_force_routing import atom_case
    from tests.analytic_oracle import REFERENCE
    import openmm as mm
    physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
    out=tmp_path/'failed'
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        _,digest=export_worker_run(source,out/'worker',snapshot,'first')
    failed=[False]
    def reject_domain(*args,**kwargs):
        failed[0]=True
        raise NumericalDomainError('alternate geometry rejected')
    original=mm.Context.getState
    def guarded_state(context,*args,**kwargs):
        if failed[0] and (kwargs.get('getEnergy') or kwargs.get('getForces')):
            raise RuntimeError('failed energy must not run again during preservation')
        return original(context,*args,**kwargs)
    monkeypatch.setattr(workflow,'_domain',reject_domain)
    monkeypatch.setattr(mm.Context,'getState',guarded_state)
    settings={'frames_per_state':1,'steps_per_frame':1,'seed':41,
              'displacement_nm':[.3,0.,0.],'protocol_kind':'abfe'}
    metadata={'settings':settings,'worker_manifest_sha256':digest,'run_id':'failure',
              'runtime_identity':REFERENCE.content_identity,'profile':{}}
    with pytest.raises(NumericalDomainError,match='alternate geometry'):
        _execute(out,metadata)
    failure=out/'failure-000000'
    assert (failure/'state.xml').is_file() and (failure/'checkpoint.chk').is_file()
    assert json.loads((failure/'error.json').read_text())['error_type']=='NumericalDomainError'
