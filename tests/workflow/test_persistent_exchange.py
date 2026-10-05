"""Whole-round commits preserve both worker and host RNG continuation."""
from contextlib import ExitStack
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil

import numpy as np
import pytest


def api():
    assert importlib.util.find_spec('atm_mlmm.exchange'), 'persistent exchange controller is missing'
    from atm_mlmm.exchange import run_exchange,resume_exchange,read_exchange_rounds
    return run_exchange,resume_exchange,read_exchange_rounds


@pytest.fixture
def prepared(tmp_path):
    from atm_mlmm.adapters.atom import build_atom,export_worker_run
    from atm_mlmm.persistence import write_json
    from atm_mlmm.workflow import _profile
    from tests.workflow.test_atom_force_routing import atom_case
    from tests.analytic_oracle import REFERENCE
    physical,transfer,schedule,restraints,snapshot=atom_case('rbfe',marker=20.)
    # The inherited force oracle was designed for algebra, not bulk clearance.
    # Give its complete second ligand/protein safe placements without relaxing
    # the molecular guard; retain the oracle's exact declared maps.
    x=np.array(snapshot.positions_nm)
    x[[snapshot.real_atom_ids.index(a) for a in ('b1','b2','b3')]]-=np.array((1.5,0.,0.))
    x[snapshot.real_atom_ids.index('protein')]+=np.array((0.,2.,0.))
    x[snapshot.real_atom_ids.index('env')]-=np.array((0.,2.,0.))
    snapshot=replace(snapshot,positions_nm=x)
    root=tmp_path/'prepared'
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        _,digest=export_worker_run(source,root/'worker',snapshot,'first')
    metadata={'version':1,'worker_manifest_sha256':digest,'runtime_identity':REFERENCE.content_identity,
              'profile':_profile(),'settings':{'seed':41,'displacement_nm':[.1,-.2,.3],'protocol_kind':'rbfe'}}
    write_json(root/'metadata.json',metadata)
    (root/'metadata.sha256').write_text(hashlib.sha256((root/'metadata.json').read_bytes()).hexdigest()+'\n')
    return root


def without_timings(rows):
    return rows  # Scientific transaction contains no elapsed-time fields.


def test_round_prefix_resume_preserves_rng_samples_states_and_analysis(prepared,tmp_path):
    run,resume,read=api()
    caller_python=random.getstate(); caller_numpy=np.random.get_state()
    interrupted=tmp_path/'interrupted'
    first=run(prepared,interrupted,rounds=4,steps_per_round=2,seed=73,trusted=True,stop_after_rounds=1)
    assert first['status']=='interrupted' and first['samples']==2
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    prefix={p.relative_to(interrupted):p.read_bytes() for p in (interrupted/'rounds/000000').iterdir()}
    # Both branches start from the exact same prepared/checkpoint/RNG boundary.
    assert resume(reference,trusted=True)['samples']==8
    assert resume(interrupted,trusted=True,stop_after_rounds=1)['samples']==4
    assert resume(interrupted,trusted=True)['samples']==8
    assert read(reference)==read(interrupted)
    for name,payload in prefix.items(): assert (interrupted/name).read_bytes()==payload
    samples=[s for r in read(interrupted) for s in r['samples']]
    assert len({s['sample_id'] for s in samples})==8
    assert len({s['walker_id'] for s in samples})==2
    for walker in {s['walker_id'] for s in samples}:
        assert [s['sequence_number'] for s in samples if s['walker_id']==walker]==[1,2,3,4]
    from atm_mlmm.schema import from_json
    from atm_mlmm.schedule import reduced_potentials
    records=from_json((interrupted/'records.json').read_text())
    assert records.sampling_mode=='correlated'
    assert reduced_potentials(records).shape==(2,8)
    assert random.getstate()==caller_python
    after=np.random.get_state()
    assert after[0]==caller_numpy[0] and after[2:]==caller_numpy[2:]
    np.testing.assert_array_equal(after[1],caller_numpy[1])
    assert resume(interrupted,trusted=True)['samples']==8


@pytest.mark.parametrize('phase', ('evaluated','decision','refreshed'))
def test_phase_failure_preserves_pending_and_explicit_rollback_replays(prepared,tmp_path,monkeypatch,phase):
    run,resume,read=api()
    import atm_mlmm.exchange as controller
    interrupted=tmp_path/'interrupted'
    run(prepared,interrupted,rounds=3,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    resume(reference,trusted=True)
    original=controller._record_phase
    def fail(pending,name,report):
        original(pending,name,report)
        if name==phase: raise OSError('phase persistence failure')
    monkeypatch.setattr(controller,'_record_phase',fail)
    with pytest.raises(OSError,match='phase persistence'):
        resume(interrupted,trusted=True)
    pending=list((interrupted/'rounds').glob('.pending-*'))
    assert len(pending)==1
    assert (pending[0]/(phase+'.json')).is_file()
    for w in (0,1):
        assert (pending[0]/f'worker-{w}/map0-state.xml').is_file()
        assert (pending[0]/f'worker-{w}/map1-state.xml').is_file()
    preserved={p.relative_to(pending[0]):p.read_bytes() for p in pending[0].rglob('*') if p.is_file()}
    with pytest.raises(ValueError,match='incomplete'):
        resume(interrupted,trusted=True)
    monkeypatch.setattr(controller,'_record_phase',original)
    assert resume(interrupted,trusted=True,recover_pending=True)['samples']==6
    assert read(reference)==read(interrupted)
    failures=list((interrupted/'failures').glob('rollback-*'))
    assert len(failures)==1
    for name,payload in preserved.items(): assert (failures[0]/name).read_bytes()==payload


def test_round_journal_tamper_and_concurrent_controller_reject(prepared,tmp_path):
    run,resume,read=api()
    import fcntl
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    with (output/'.controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='controller'):
            resume(output,trusted=True)
    (output/'rounds/000000/worker-0.chk').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='mismatch'):
        read(output)
    with pytest.raises(ValueError,match='mismatch'):
        resume(output,trusted=True)


def test_journal_failure_before_publish_never_commits_half_a_pair(prepared,tmp_path,monkeypatch):
    run,resume,read=api()
    import atm_mlmm.exchange as controller
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    original=controller._publish_round
    def fail(*args): raise OSError('round commit failed')
    monkeypatch.setattr(controller,'_publish_round',fail)
    with pytest.raises(OSError,match='round commit'): resume(output,trusted=True)
    assert not (output/'rounds/000001').exists()
    assert list((output/'rounds').glob('.pending-*'))
    monkeypatch.setattr(controller,'_publish_round',original)
    assert resume(output,trusted=True,recover_pending=True)['samples']==4


def test_postpublish_reporting_failure_leaves_committed_round_authoritative(prepared,tmp_path,monkeypatch):
    run,resume,read=api()
    import atm_mlmm.exchange as controller
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    original=controller.write_json
    def fail(path,data):
        if Path(path).name=='summary.json': raise OSError('summary unavailable')
        return original(path,data)
    monkeypatch.setattr(controller,'write_json',fail)
    with pytest.raises(OSError,match='summary'): resume(output,trusted=True)
    assert len(read(output))==2
    monkeypatch.setattr(controller,'write_json',original)
    assert resume(output,trusted=True)['samples']==4


def test_postrename_sync_failure_keeps_published_pair(prepared,tmp_path,monkeypatch):
    run,resume,read=api()
    import atm_mlmm.exchange as controller
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    original=controller._publish_round
    def fail_after_rename(*args):
        original(*args)
        raise OSError('parent fsync failed after rename')
    monkeypatch.setattr(controller,'_publish_round',fail_after_rename)
    with pytest.raises(OSError,match='fsync'): resume(output,trusted=True)
    assert len(read(output))==2 and not list((output/'rounds').glob('.pending-*'))
    monkeypatch.setattr(controller,'_publish_round',original)
    assert resume(output,trusted=True)['samples']==4


def test_refresh_failure_keeps_decision_and_does_not_reenter_energy(prepared,tmp_path,monkeypatch):
    run,resume,read=api()
    import atm_mlmm.exchange as controller
    from atm_mlmm.adapters.atom import WorkerRun
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    decided=[False]; original_phase=controller._record_phase; original_evaluate=WorkerRun.evaluate
    def record(*args):
        original_phase(*args)
        if args[1]=='decision': decided[0]=True
    def fail_after_decision(self,*args):
        if decided[0]: raise RuntimeError('actual postdecision refresh failed')
        return original_evaluate(self,*args)
    monkeypatch.setattr(controller,'_record_phase',record)
    monkeypatch.setattr(WorkerRun,'evaluate',fail_after_decision)
    with pytest.raises(RuntimeError,match='postdecision'): resume(output,trusted=True)
    pending=next((output/'rounds').glob('.pending-*'))
    assert (pending/'decision.json').is_file() and not (pending/'refreshed.json').exists()
    for w in (0,1):
        assert (pending/f'worker-{w}/map0-state.xml').exists()
        assert (pending/f'worker-{w}/map1-state.xml').exists()
    assert not (output/'rounds/000001').exists()


def test_stale_saved_energy_is_rejected_on_checkpoint_refresh(prepared,tmp_path):
    run,resume,_=api()
    from atm_mlmm.persistence import read_json,write_json
    from atm_mlmm.exchange_journal import sha
    output=tmp_path/'exchange'
    run(prepared,output,rounds=2,steps_per_round=1,seed=73,trusted=True,stop_after_rounds=1)
    chunk=output/'rounds/000000'
    record=read_json(chunk/'record.json')
    record['exchange']['energies_after_kj_mol'][0]+=10.
    write_json(chunk/'record.json',record)
    write_json(chunk/'refreshed.json',record['exchange'])
    manifest=read_json(chunk/'manifest.json')
    for name in ('record.json','refreshed.json'): manifest['files'][name]=sha(chunk/name)
    write_json(chunk/'manifest.json',manifest)
    with pytest.raises(ValueError,match='fresh|stale'): resume(output,trusted=True)


def test_guard_settings_must_describe_actual_sealed_maps(prepared,tmp_path):
    run,_,_=api()
    from atm_mlmm.persistence import read_json,write_json
    from atm_mlmm.exchange_journal import sha
    data=read_json(prepared/'metadata.json')
    data['settings']['displacement_nm']=[3.,0.,0.]
    write_json(prepared/'metadata.json',data)
    (prepared/'metadata.sha256').write_text(sha(prepared/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='map|displacement'):
        run(prepared,tmp_path/'exchange',rounds=2,steps_per_round=1,seed=73,trusted=True)
