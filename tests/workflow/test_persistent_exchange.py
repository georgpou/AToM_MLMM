"""Whole-round commits preserve both worker and host RNG continuation."""
from contextlib import ExitStack
from dataclasses import asdict,replace
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


def multistate_api():
    from atm_mlmm.exchange import run_multistate_exchange,resume_multistate_exchange
    from atm_mlmm.exchange_journal import read_multistate_boundaries
    return run_multistate_exchange,resume_multistate_exchange,read_multistate_boundaries


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


def prepare_multistate(root, *, kind='rbfe', temperature_K=300.):
    from dataclasses import replace
    from atm_mlmm.adapters.atom import build_atom,export_worker_run
    from atm_mlmm.persistence import write_json
    from atm_mlmm.schedule import production_schedule
    from atm_mlmm.workflow import _profile
    from tests.workflow.test_atom_force_routing import atom_case
    from tests.analytic_oracle import REFERENCE,production_parameters
    physical,transfer,_,restraints,snapshot=atom_case(kind,marker=20.)
    if kind=='rbfe':
        x=np.array(snapshot.positions_nm)
        x[[snapshot.real_atom_ids.index(a) for a in ('b1','b2','b3')]]-=np.array((1.5,0.,0.))
        x[snapshot.real_atom_ids.index('protein')]+=np.array((0.,2.,0.))
        x[snapshot.real_atom_ids.index('env')]-=np.array((0.,2.,0.))
        snapshot=replace(snapshot,positions_nm=x)
    elif kind=='abfe':
        x=np.array(snapshot.positions_nm)
        x[[snapshot.real_atom_ids.index(a) for a in ('b1','b2','b3')]]-=np.array((1.5,0.,0.))
        x[snapshot.real_atom_ids.index('protein')]-=np.array((0.,2.,0.))
        x[snapshot.real_atom_ids.index('env')]+=np.array((0.,2.,0.))
        snapshot=replace(snapshot,positions_nm=x)
    schedule=production_schedule((
        ('first',production_parameters()),
        ('middle',production_parameters(Lambda1=.2,Lambda2=.7,W0=.6)),
        ('third',production_parameters(Lambda1=.3,Lambda2=.7,W0=.9,Direction=-1.)),
    ),temperature_K=temperature_K)
    runtime=replace(REFERENCE,temperature_K=temperature_K)
    root=Path(root)
    with build_atom(physical,transfer,schedule,restraints,runtime) as source:
        _,digest=export_worker_run(source,root/'worker',snapshot,'first')
    metadata={'version':1,'worker_manifest_sha256':digest,'runtime_identity':runtime.content_identity,
              'profile':_profile(),'settings':{'seed':41,'displacement_nm':[.1,-.2,.3],'protocol_kind':kind}}
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


def test_multistate_admission_requires_connected_three_to_eight_schedule_states(tmp_path,monkeypatch):
    run,_,_=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    def forbidden(*args,**kwargs):
        raise AssertionError('trusted worker loader ran before multistate admission')
    monkeypatch.setattr(atom,'load_worker_run',forbidden)
    invalid=(
        (('first','middle'),((0,1),)),
        (tuple(f'state-{i}' for i in range(9)),tuple((i,i+1) for i in range(8))),
        (('first','middle','first'),((0,1),(1,2))),
        (('first','middle','third'),((0,3),(1,2))),
        (('first','middle','third'),((0,1),)),
        (('first','middle','third'),((0,1),(1,0))),
        (('first','middle','absent'),((0,1),(1,2))),
    )
    for index,(state_ids,state_pairs) in enumerate(invalid):
        with pytest.raises(ValueError):
            run(prepared,tmp_path/f'invalid-{index}',state_ids=state_ids,state_pairs=state_pairs,
                boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
        assert not (tmp_path/f'invalid-{index}').exists()
    non_300=prepare_multistate(tmp_path/'non-300',temperature_K=310.)
    with pytest.raises(ValueError,match='300|temperature|runtime'):
        run(non_300,tmp_path/'invalid-temperature',state_ids=('first','middle','third'),
            state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    assert not (tmp_path/'invalid-temperature').exists()


def test_multistate_runtime_and_geometry_are_admitted_before_worker_load(tmp_path,monkeypatch):
    run,_,_=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json,write_json
    loaded=[]
    def forbidden(*args,**kwargs):
        loaded.append(True)
        raise AssertionError('trusted worker loader ran before exact runtime/geometry admission')
    monkeypatch.setattr(atom,'load_worker_run',forbidden)
    from dataclasses import replace
    from atm_mlmm.schema import from_json,to_json
    unsupported=prepare_multistate(tmp_path/'unsupported-runtime')
    runtime_path=unsupported/'worker/runtime.json'
    runtime=replace(from_json(runtime_path.read_text()),integrator='Verlet')
    runtime_path.write_text(to_json(runtime)+'\n')
    manifest_path=unsupported/'worker/manifest.json'
    manifest=read_json(manifest_path)
    manifest['files']['runtime.json']=sha(runtime_path)
    manifest['runtime_identity']=runtime.content_identity
    write_json(manifest_path,manifest)
    metadata=read_json(unsupported/'metadata.json')
    metadata['runtime_identity']=runtime.content_identity
    metadata['worker_manifest_sha256']=sha(manifest_path)
    write_json(unsupported/'metadata.json',metadata)
    (unsupported/'metadata.sha256').write_text(sha(unsupported/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='LangevinMiddle|runtime'):
        run(unsupported,tmp_path/'runtime-output',state_ids=('first','middle','third'),
            state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    assert loaded==[] and not (tmp_path/'runtime-output').exists()
    wrong_geometry=prepare_multistate(tmp_path/'wrong-geometry')
    metadata=read_json(wrong_geometry/'metadata.json')
    metadata['settings']['displacement_nm']=[3.,0.,0.]
    write_json(wrong_geometry/'metadata.json',metadata)
    (wrong_geometry/'metadata.sha256').write_text(sha(wrong_geometry/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='geometry|displacement|maps'):
        run(wrong_geometry,tmp_path/'geometry-output',state_ids=('first','middle','third'),
            state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    assert loaded==[] and not (tmp_path/'geometry-output').exists()


def test_pair_and_multistate_modes_cannot_resume_each_other(prepared,tmp_path):
    pair_run,pair_resume,_=api()
    _,multi_resume,read_multi=multistate_api()
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json,write_json
    output=tmp_path/'pair'
    pair_run(prepared,output,rounds=1,steps_per_round=1,seed=73,trusted=True)
    with pytest.raises(ValueError,match='mode'):
        read_multi(output)
    with pytest.raises(ValueError,match='mode'):
        multi_resume(output,trusted=True)
    metadata=read_json(output/'metadata.json')
    metadata['mode']='persistent-multistate-exchange-v1'
    write_json(output/'metadata.json',metadata)
    (output/'metadata.sha256').write_text(sha(output/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='mode'):
        pair_resume(output,trusted=True)


@pytest.mark.parametrize('fault',('missing-source-path','changed-source-digest'))
def test_multistate_source_inventory_must_match_before_trusted_load(tmp_path,monkeypatch,fault):
    run,_,_=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    manifest_path=prepared/'worker/manifest.json'
    manifest=read_json(manifest_path)
    source_paths=sorted(name for name in manifest['files'] if name.startswith('runtime/source/atm_mlmm/') and name.endswith('.py'))
    assert source_paths
    if fault=='missing-source-path':
        del manifest['files'][source_paths[-1]]
    else:
        manifest['files'][source_paths[-1]]='0'*64
    write_json(manifest_path,manifest)
    metadata=read_json(prepared/'metadata.json')
    metadata['worker_manifest_sha256']=sha(manifest_path)
    write_json(prepared/'metadata.json',metadata)
    (prepared/'metadata.sha256').write_text(sha(prepared/'metadata.json')+'\n')
    def forbidden(*args,**kwargs):
        raise AssertionError('trusted worker loader ran before source admission')
    monkeypatch.setattr(atom,'load_worker_run',forbidden)
    with pytest.raises(ValueError,match='source|artifact|manifest'):
        run(prepared,tmp_path/'exchange',state_ids=('first','middle','third'),
            state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)


def test_pair_source_inventory_rejects_a_missing_bundled_module_before_load(prepared,tmp_path,monkeypatch):
    run,resume,_=api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import sha
    from atm_mlmm.persistence import read_json,write_json
    output=tmp_path/'pair'
    run(prepared,output,rounds=1,steps_per_round=1,seed=73,trusted=True)
    manifest_path=output/'worker/manifest.json'
    manifest=read_json(manifest_path)
    source_paths=sorted(name for name in manifest['files']
        if name.startswith('runtime/source/atm_mlmm/') and name.endswith('.py'))
    assert source_paths
    del manifest['files'][source_paths[-1]]
    write_json(manifest_path,manifest)
    metadata=read_json(output/'metadata.json')
    metadata['worker_manifest_sha256']=sha(manifest_path)
    write_json(output/'metadata.json',metadata)
    (output/'metadata.sha256').write_text(sha(output/'metadata.json')+'\n')
    def forbidden(*args,**kwargs):
        raise AssertionError('trusted worker loader ran before pair source admission')
    monkeypatch.setattr(atom,'load_worker_run',forbidden)
    with pytest.raises(ValueError,match='source inventory'):
        resume(output,trusted=True)


def test_multistate_inert_admission_binds_runtime_and_initial_assignment(tmp_path):
    run,_,read=multistate_api()
    from atm_mlmm.exchange_journal import seal_tree,sha
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=1,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)

    metadata=read_json(output/'metadata.json')
    metadata['runtime_identity']='0'*64
    write_json(output/'metadata.json',metadata)
    (output/'metadata.sha256').write_text(sha(output/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='runtime.*identity'):
        read(output)

    # Restore a valid metadata identity, then make the immutable initial report
    # claim a different schedule state while retaining a valid recursive seal.
    metadata['runtime_identity']=read_json(prepared/'metadata.json')['runtime_identity']
    initial=output/'initial'
    reports=read_json(initial/'final-state-reports.json')
    reports['workers'][0]['state_id']='middle'
    reports['workers'][0]['parameters']=metadata['state_parameters']['middle']
    write_json(initial/'final-state-reports.json',reports)
    metadata['initial_manifest_sha256']=seal_tree(initial,index=-1)
    boundary=output/'boundaries/000000'
    record=read_json(boundary/'record.json')
    record['previous_manifest_sha256']=metadata['initial_manifest_sha256']
    write_json(boundary/'record.json',record)
    seal_tree(boundary,index=0)
    write_json(output/'metadata.json',metadata)
    (output/'metadata.sha256').write_text(sha(output/'metadata.json')+'\n')
    with pytest.raises(ValueError,match='assignment|permutation|initial'):
        read(output)


def test_multistate_controller_preserves_caller_global_rng(tmp_path):
    run,_,_=multistate_api()
    python_state=random.getstate()
    numpy_state=np.random.get_state()
    prepared=prepare_multistate(tmp_path/'prepared')
    run(prepared,tmp_path/'exchange',state_ids=('first','middle','third'),
        state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,
        trusted=True,stop_after_boundaries=1)
    assert random.getstate()==python_state
    after=np.random.get_state()
    assert after[0]==numpy_state[0] and after[2:]==numpy_state[2:]
    np.testing.assert_array_equal(after[1],numpy_state[1])


def test_multistate_sweep_resolves_overlapping_pairs_after_each_accept(tmp_path,monkeypatch):
    run,_,read=multistate_api()
    from atm_mlmm.adapters import atom
    from atom_openmm import gibbs_sampling
    prepared=prepare_multistate(tmp_path/'prepared')
    calls=[]; original=atom.attempt_pair_exchange
    def observe(workers,snapshots,state_ids,walker_ids,**kwargs):
        calls.append((tuple(walker_ids),tuple(state_ids)))
        return original(workers,snapshots,state_ids,walker_ids,**kwargs)
    monkeypatch.setattr(atom,'attempt_pair_exchange',observe)
    monkeypatch.setattr(gibbs_sampling,'_random',lambda:0.)
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    assert len(calls)==2
    assert tuple(value.rsplit(':',1)[-1] for value in calls[0][0])==('walker-0','walker-1')
    assert tuple(value.rsplit(':',1)[-1] for value in calls[1][0])==('walker-0','walker-2')
    assert [call[1] for call in calls]==[('first','middle'),('middle','third')]
    boundary=read(output)[0]
    assert boundary['walker_to_state_start']==[0,1,2]
    assert [attempt['walker_to_state_after'] for attempt in boundary['attempts']]==[[1,0,2],[2,0,1]]
    assert boundary['walker_to_state_final']==[2,0,1]


def test_multistate_sample_state_is_distinct_from_final_assignment(tmp_path,monkeypatch):
    run,_,read=multistate_api()
    from atom_openmm import gibbs_sampling
    prepared=prepare_multistate(tmp_path/'prepared')
    monkeypatch.setattr(gibbs_sampling,'_random',lambda:0.)
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    boundary=read(output)[0]
    samples=sorted(boundary['samples'],key=lambda sample:sample['walker_index'])
    assert [sample['state_id'] for sample in samples]==['first','middle','third']
    assert [sample['sequence_number'] for sample in samples]==[1,1,1]
    assert boundary['walker_to_state_final']==[2,0,1]


def test_partial_integration_stages_worker_zero_and_replays_entire_boundary(tmp_path,monkeypatch):
    run,resume,read=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    interrupted=tmp_path/'interrupted'
    run(prepared,interrupted,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    expected=resume(reference,trusted=True)
    original=atom.WorkerRun.evaluate
    def fail_worker_one_after_integration(self,snapshot,state_id):
        if self.integrator_seed==42 and self.evaluator.context.getStepCount()>=2:
            raise RuntimeError('worker one failed after integration')
        return original(self,snapshot,state_id)
    monkeypatch.setattr(atom.WorkerRun,'evaluate',fail_worker_one_after_integration)
    with pytest.raises(RuntimeError,match='worker one failed after integration'):
        resume(interrupted,trusted=True)
    pending=interrupted/'pending'
    staged=pending/'samples/worker-000.json'
    assert staged.is_file()
    sample=read_json(staged)
    assert sample['sample_id'].endswith(':walker-0:boundary-2')
    assert len(sample['real_forces_kj_mol_nm'])==len(sample['real_atom_ids'])
    assert set(sample['raw'])=={'u0_raw_kJ_mol','u1_raw_kJ_mol','delta_u_raw_kJ_mol',
        'delta_u_softcore_kJ_mol','atm_expression_energy_kJ_mol','outside_energy_kJ_mol',
        'system_total_energy_kJ_mol'}
    for name in ('worker-000-state.xml','worker-000.chk'):
        assert (pending/'samples'/name).is_file()
    for worker in range(3):
        archive=pending/'failures'/f'worker-{worker:03d}'
        assert (archive/'error.json').is_file()
        assert (archive/'checkpoint.chk').is_file()
        assert (archive/'map0-state.xml').is_file() and (archive/'map1-state.xml').is_file()
    preserved={path.relative_to(pending).as_posix():path.read_bytes() for path in pending.rglob('*') if path.is_file()}
    with pytest.raises(ValueError,match='incomplete'):
        resume(interrupted,trusted=True)
    assert preserved=={path.relative_to(pending).as_posix():path.read_bytes() for path in pending.rglob('*') if path.is_file()}
    monkeypatch.setattr(atom.WorkerRun,'evaluate',original)
    resumed=resume(interrupted,trusted=True,recover_pending=True)
    assert resumed['samples']==expected['samples']==6
    assert read(reference)==read(interrupted)
    rollback=next((interrupted/'failures').glob('rollback-*'))
    rollback_record=read_json(rollback/'rollback.json')
    assert set(rollback_record['preserved_file_hashes'])==set(preserved)
    for name,payload in preserved.items():
        assert (rollback/name).read_bytes()==payload
    for boundary in ('initial','boundaries/000000','boundaries/000001'):
        left=interrupted/boundary; right=reference/boundary
        left_files={p.relative_to(left):p.read_bytes() for p in left.rglob('*') if p.is_file()}
        right_files={p.relative_to(right):p.read_bytes() for p in right.rglob('*') if p.is_file()}
        assert left_files==right_files
    samples=[sample for row in read(interrupted) for sample in row['samples']]
    assert len({sample['sample_id'] for sample in samples})==6
    assert all([sample['sequence_number'] for sample in samples if sample['walker_id']==walker]==[1,2]
               for walker in {sample['walker_id'] for sample in samples})


@pytest.mark.parametrize('phase',('evaluated','decision','refreshed'))
@pytest.mark.parametrize('attempt_index',(0,1))
def test_multistate_phase_persistence_failure_rolls_back_whole_sweep(
        tmp_path,monkeypatch,phase,attempt_index):
    run,resume,read=multistate_api()
    import atm_mlmm.exchange as controller
    from atm_mlmm.persistence import read_json
    prepared=prepare_multistate(tmp_path/'prepared')
    interrupted=tmp_path/'interrupted'
    run(prepared,interrupted,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    resume(reference,trusted=True)
    original=controller._write_multistate_phase
    def fail_after_durable_write(directory,name,document):
        original(directory,name,document)
        if directory.name==f'{attempt_index:04d}' and name==phase:
            raise OSError(f'{phase} persistence failure')
    monkeypatch.setattr(controller,'_write_multistate_phase',fail_after_durable_write)
    with pytest.raises(OSError,match=f'{phase} persistence'):
        resume(interrupted,trusted=True)
    pending=interrupted/'pending'
    attempts=pending/'attempts'
    attempt_dir=attempts/f'{attempt_index:04d}'
    assert (attempt_dir/'attempt.json').is_file()
    assert (attempt_dir/f'{phase}.json').is_file()
    attempt=read_json(attempt_dir/'attempt.json')
    assert len(attempt['walker_to_state_before'])==3
    if attempt_index:
        prior=read_json(attempts/'0000/history.json')
        assert attempt['walker_to_state_before']==prior['walker_to_state_after']
        assert all((attempts/'0000'/f'{name}.json').is_file()
                   for name in ('attempt','evaluated','decision','refreshed','history'))
    if phase=='decision':
        decision=read_json(attempt_dir/'decision.json')
        assert len(decision['walker_to_state_before'])==len(decision['walker_to_state_after'])==3
    assert not (interrupted/'boundaries/000001').exists()
    monkeypatch.setattr(controller,'_write_multistate_phase',original)
    resume(interrupted,trusted=True,recover_pending=True)
    assert read(reference)==read(interrupted)
    left=interrupted/'boundaries/000001'; right=reference/'boundaries/000001'
    assert {p.relative_to(left):p.read_bytes() for p in left.rglob('*') if p.is_file()}=={
        p.relative_to(right):p.read_bytes() for p in right.rglob('*') if p.is_file()}


@pytest.mark.parametrize('failure',('capture','seal','rename'))
def test_multistate_capture_seal_and_precommit_failures_do_not_publish(
        tmp_path,monkeypatch,failure):
    run,resume,read=multistate_api()
    import atm_mlmm.exchange as controller
    import atm_mlmm.exchange_journal as journal
    from atm_mlmm.adapters import atom
    prepared=prepare_multistate(tmp_path/'prepared')
    interrupted=tmp_path/'interrupted'
    run(prepared,interrupted,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    resume(reference,trusted=True)
    if failure=='capture':
        original=controller._capture_multistate
        def fail_capture(worker,state_path,checkpoint_path):
            result=original(worker,state_path,checkpoint_path)
            if Path(state_path).name=='worker-001-state.xml' and Path(state_path).parent.name=='workers':
                raise OSError('final capture failed')
            return result
        monkeypatch.setattr(controller,'_capture_multistate',fail_capture)
        expected='capture'
    elif failure=='seal':
        original=journal.seal_tree
        def fail_seal(directory,*,index):
            if index==1: raise OSError('boundary seal failed')
            return original(directory,index=index)
        monkeypatch.setattr(journal,'seal_tree',fail_seal)
        expected='seal'
    else:
        import os
        original=os.rename
        def fail_rename(source,target):
            if Path(source).name=='pending' and Path(target).name=='000001':
                raise OSError('precommit rename failed')
            return original(source,target)
        monkeypatch.setattr(os,'rename',fail_rename)
        expected='precommit rename'
    with pytest.raises(OSError,match=expected):
        resume(interrupted,trusted=True)
    assert not (interrupted/'boundaries/000001').exists()
    assert (interrupted/'pending').is_dir()
    with pytest.raises(ValueError,match='incomplete'):
        read(interrupted)
    monkeypatch.undo()
    resume(interrupted,trusted=True,recover_pending=True)
    assert read(reference)==read(interrupted)
    left=interrupted/'boundaries/000001'; right=reference/'boundaries/000001'
    assert {p.relative_to(left):p.read_bytes() for p in left.rglob('*') if p.is_file()}=={
        p.relative_to(right):p.read_bytes() for p in right.rglob('*') if p.is_file()}


@pytest.mark.parametrize('failure',('parent-fsync','records','observations.json','summary.json'))
def test_multistate_postrename_failure_keeps_boundary_authoritative(tmp_path,monkeypatch,failure):
    run,resume,read=multistate_api()
    import atm_mlmm.exchange as controller
    prepared=prepare_multistate(tmp_path/'prepared')
    interrupted=tmp_path/'interrupted'
    run(prepared,interrupted,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    reference=tmp_path/'reference'; shutil.copytree(interrupted,reference)
    resume(reference,trusted=True)
    if failure=='parent-fsync':
        original=controller._publish_multistate_boundary
        def fail_after_rename(pending,target,index):
            original(pending,target,index)
            if index==1: raise OSError('parent fsync failed after rename')
        monkeypatch.setattr(controller,'_publish_multistate_boundary',fail_after_rename)
        expected='parent fsync'
    elif failure=='records':
        def fail_records(record): raise OSError('records rebuild failed')
        monkeypatch.setattr(controller,'to_json',fail_records)
        expected='records rebuild'
    else:
        original=controller.write_json
        def fail_report(path,document):
            if Path(path).name==failure: raise OSError(f'{failure} rebuild failed')
            return original(path,document)
        monkeypatch.setattr(controller,'write_json',fail_report)
        expected=f'{failure} rebuild'
    with pytest.raises(OSError,match=expected):
        resume(interrupted,trusted=True)
    assert not (interrupted/'pending').exists()
    assert len(read(interrupted))==2
    committed=interrupted/'boundaries/000001'
    before={p.relative_to(committed):p.read_bytes() for p in committed.rglob('*') if p.is_file()}
    monkeypatch.undo()
    summary=resume(interrupted,trusted=True)
    assert summary['samples']==6 and len(read(interrupted))==2
    assert before=={p.relative_to(committed):p.read_bytes() for p in committed.rglob('*') if p.is_file()}
    left=interrupted/'boundaries/000001'; right=reference/'boundaries/000001'
    assert {p.relative_to(left):p.read_bytes() for p in left.rglob('*') if p.is_file()}=={
        p.relative_to(right):p.read_bytes() for p in right.rglob('*') if p.is_file()}


@pytest.mark.parametrize('fault',('permutation','sample-id','sample-sequence','rng','phase',
                                 'rng-before-chain','history-assignment','checkpoint'))
def test_multistate_inert_admission_rejects_tampered_artifacts_before_load(
        tmp_path,monkeypatch,fault):
    run,resume,read=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange_journal import seal_tree
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    boundary=output/'boundaries/000000'
    if fault=='permutation':
        path=boundary/'walker-to-state.json'; document=read_json(path)
        document['walker_to_state']=[1,0,2]; write_json(path,document)
    elif fault in ('sample-id','sample-sequence'):
        path=boundary/'samples/worker-000.json'; document=read_json(path)
        if fault=='sample-id': document['sample_id']='tampered-id'
        else: document['sequence_number']=99
        write_json(path,document)
    elif fault=='rng':
        path=boundary/'rng.json'; document=read_json(path)
        document['numpy'][2]=(document['numpy'][2]+1)%625; write_json(path,document)
    elif fault=='phase':
        path=boundary/'attempts/0000/evaluated.json'; document=read_json(path)
        document['reduced_energies'][0][0]+=1.; write_json(path,document)
    elif fault=='rng-before-chain':
        path=boundary/'record.json'; document=read_json(path)
        document['rng_before_sha256']='0'*64; write_json(path,document)
        seal_tree(boundary,index=0)
    elif fault=='history-assignment':
        path=boundary/'attempts/0000/history.json'; document=read_json(path)
        document['resolved_state_to_walker']=[2,1,0]; write_json(path,document)
        seal_tree(boundary,index=0)
    else:
        path=boundary/'workers/worker-000.chk'; path.write_bytes(b'unrehashed checkpoint tamper')
    loaded=[]
    def forbidden(*args,**kwargs):
        loaded.append(True)
        raise AssertionError('trusted worker loader ran before inert journal admission')
    monkeypatch.setattr(atom,'load_worker_run',forbidden)
    with pytest.raises(ValueError,match='mismatch|identity|hash|arithmetic|permutation|history'):
        read(output)
    with pytest.raises(ValueError,match='mismatch|identity|hash|arithmetic|permutation|history'):
        resume(output,trusted=True)
    assert loaded==[]


def test_multistate_lock_rejects_concurrent_controller(tmp_path):
    run,resume,_=multistate_api()
    import fcntl
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    with (output/'.controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='controller'):
            resume(output,trusted=True)


def test_multistate_checkpoint_energy_is_refreshed_after_restore_before_integration(
        tmp_path,monkeypatch):
    run,resume,read=multistate_api()
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange import _coordinate_digest
    from atm_mlmm.exchange_journal import seal_tree
    from atm_mlmm.persistence import read_json,write_json
    from atm_mlmm.workflow import _snapshot
    import openmm as mm
    import numpy as np
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    boundary=output/'boundaries/000000'
    metadata=read_json(output/'metadata.json')
    record=read_json(boundary/'record.json')
    worker_path=output/'worker'
    from atm_mlmm.adapters.atom import load_worker_run
    with load_worker_run(worker_path,metadata['worker_manifest_sha256'],trusted=True,
                         integrator_seed=metadata['integrator_seed_base']) as worker:
        final_state=metadata['state_ids'][record['walker_to_state_final'][0]]
        sample_state=metadata['state_ids'][record['walker_to_state_start'][0]]
        worker.restore_checkpoint((boundary/'workers/worker-000.chk').read_bytes(),final_state)
        original_snapshot=_snapshot(worker)
        positions=np.array(original_snapshot.positions_nm,copy=True)
        positions[0,0]+=.03
        moved=replace(original_snapshot,positions_nm=positions)
        sample_result=worker.evaluate(moved,sample_state)
        sample_saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        sample_checkpoint=worker.evaluator.context.createCheckpoint()
        sample_path=boundary/'samples/worker-000.json'
        sample=read_json(sample_path)
        sample.update(positions_nm=moved.positions_nm,velocities_nm_ps=moved.velocities_nm_ps,
            raw=asdict(sample_result.raw),total_energy_kJ_mol=sample_result.total.energy_kj_mol,
            real_forces_kj_mol_nm=sample_result.total.forces_kj_mol_nm,
            parameters=dict(sample_result.parameters))
        write_json(sample_path,sample)
        (boundary/'samples/worker-000-state.xml').write_text(mm.XmlSerializer.serialize(sample_saved))
        (boundary/'samples/worker-000.chk').write_bytes(sample_checkpoint)
        final_result=worker.evaluate(moved,final_state)
        final_saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        final_checkpoint=worker.evaluator.context.createCheckpoint()
        (boundary/'workers/worker-000-state.xml').write_text(mm.XmlSerializer.serialize(final_saved))
        (boundary/'workers/worker-000.chk').write_bytes(final_checkpoint)
        reports=read_json(boundary/'final-state-reports.json')
        reports['workers'][0]['coordinate_sha256']=_coordinate_digest(moved.positions_nm)
        # Keep the hash-consistent prior raw/total report so trusted restore must
        # discover its physical staleness by a fresh actual-context evaluation.
        write_json(boundary/'final-state-reports.json',reports)
    seal_tree(boundary,index=0)
    assert len(read(output))==1
    evaluated=[]; original_evaluate=atom.WorkerRun.evaluate
    def count_fresh(self,snapshot,state_id):
        evaluated.append((self.integrator_seed,self.evaluator.context.getStepCount()))
        return original_evaluate(self,snapshot,state_id)
    monkeypatch.setattr(atom.WorkerRun,'evaluate',count_fresh)
    with pytest.raises(ValueError,match='fresh actual-context'):
        resume(output,trusted=True)
    assert evaluated==[(metadata['integrator_seed_base'],1)]
    assert not (output/'pending').exists()


def test_multistate_fresh_restore_compares_complete_total_before_next_integration(
        tmp_path,monkeypatch):
    run,resume,read=multistate_api()
    import atm_mlmm.exchange as controller
    from atm_mlmm.exchange_journal import seal_tree
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    boundary=output/'boundaries/000000'
    reports=read_json(boundary/'final-state-reports.json')
    reports['workers'][0]['total']['diagnostics']['platform']='CPU'
    write_json(boundary/'final-state-reports.json',reports)
    seal_tree(boundary,index=0)
    assert len(read(output))==1
    captured=[]
    original=controller._multistate_sample
    def capture(*args,**kwargs):
        captured.append(True)
        return original(*args,**kwargs)
    monkeypatch.setattr(controller,'_multistate_sample',capture)
    with pytest.raises(ValueError,match='fresh actual-context'):
        resume(output,trusted=True)
    assert captured==[]
    assert len(read(output))==1


def test_multistate_restore_rejects_portable_parameter_disagreement_before_integration(
        tmp_path,monkeypatch):
    run,resume,read=multistate_api()
    import openmm as mm
    import atm_mlmm.exchange as controller
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.exchange_journal import seal_tree
    from atm_mlmm.persistence import read_json,write_json
    prepared=prepare_multistate(tmp_path/'prepared')
    output=tmp_path/'exchange'
    run(prepared,output,state_ids=('first','middle','third'),state_pairs=((0,1),(1,2)),
        boundaries=2,steps_per_boundary=1,seed=73,trusted=True,stop_after_boundaries=1)
    boundary=output/'boundaries/000000'
    metadata=read_json(output/'metadata.json')
    with load_worker_run(output/'worker',metadata['worker_manifest_sha256'],trusted=True,
                         integrator_seed=metadata['integrator_seed_base']) as worker:
        final_state=metadata['state_ids'][read_json(boundary/'record.json')['walker_to_state_final'][0]]
        worker.restore_checkpoint((boundary/'workers/worker-000.chk').read_bytes(),final_state)
        context=worker.evaluator.context
        current=context.getParameters()['Lambda1']
        context.setParameter('Lambda1',current+.01)
        portable=context.getState(getPositions=True,getVelocities=True,getParameters=True)
        state_xml=mm.XmlSerializer.serialize(portable)
    (boundary/'workers/worker-000-state.xml').write_text(state_xml)
    seal_tree(boundary,index=0)
    assert len(read(output))==1
    captured=[]
    original=controller._multistate_sample
    def capture(*args,**kwargs):
        captured.append(True)
        return original(*args,**kwargs)
    monkeypatch.setattr(controller,'_multistate_sample',capture)
    with pytest.raises(ValueError,match='portable State'):
        resume(output,trusted=True)
    assert captured==[]
    assert len(read(output))==1
