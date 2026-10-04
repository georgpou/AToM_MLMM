"""One explicit configuration drives bounded preparation and actual workers."""
from pathlib import Path
import json
import pytest
from tests.workflow.test_cloud_host_guest import FIXTURE


def test_configuration_rejects_unsupported_settings_before_execution(tmp_path):
    from atm_mlmm.workflow import load_configuration
    from atm_mlmm.schema import MalformedInput, UnsupportedCapability
    base = json.loads((FIXTURE/'config.json').read_text())
    base['input_manifest'] = str(FIXTURE/'manifest.json')
    for change in ({'timestep_ps':.002}, {'platform':'CUDA'}, {'implicit_solvent':'GB'},
                   {'frames_per_state':0}, {'temperatures_K':[300.,10.]}):
        document = {**base,'settings':{**base['settings'],**change}}
        path=tmp_path/'config.json'
        path.write_text(json.dumps(document))
        with pytest.raises((MalformedInput,UnsupportedCapability)):
            load_configuration(path)


def test_common_runner_preserves_raw_states_and_all_real_forces(tmp_path):
    from atm_mlmm.workflow import run_configuration
    from atm_mlmm.schema import from_json
    from atm_mlmm.schedule import reduced_potentials
    base = json.loads((FIXTURE/'config.json').read_text())
    base['input_manifest'] = str(FIXTURE/'manifest.json')
    base['settings'].update(frames_per_state=1,steps_per_frame=1,minimization_iterations=3)
    path=tmp_path/'config.json'
    path.write_text(json.dumps(base))
    out=tmp_path/'run'
    summary=run_configuration(path,out,trusted=True)
    assert summary['scope']=='bounded engine preflight; no equilibrium or physical-accuracy claim'
    records=from_json((out/'records.json').read_text())
    assert len(records.sample_ids)==3 and len(set(records.sample_ids))==3
    assert set(records.sampled_state_ids)=={'contact','middle','separated'}
    assert reduced_potentials(records).shape==(3,3)
    rows=json.loads((out/'observations.json').read_text())
    assert all(len(row['real_forces_kj_mol_nm'])==48 for row in rows)
    assert all(row['parameters']['Direction']==1 for row in rows)
    assert summary['binding_result']=='not_evaluated'
    assert all((out/'samples'/f'{i:06d}'/'checkpoint.chk').is_file() for i in range(3))
    # Independent fresh state evaluations of all saved configurations check the
    # entire reconstructed matrix, including unsampled counterfactual states.
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.schema import Snapshot
    matrix = reduced_potentials(records)
    with load_worker_run(out/'worker',summary['worker_manifest_sha256'],trusted=True) as worker:
        for i,row in enumerate(rows):
            snapshot = Snapshot(tuple(row['real_atom_ids']),row['positions_nm'],row['box_nm'])
            for j,state in enumerate(worker.bundle.schedule.states):
                actual = worker.evaluate(snapshot,state.state_id)
                assert actual.total.energy_kj_mol == pytest.approx(matrix[j,i]*.00831446261815324*300.,abs=1.e-8)
    with pytest.raises(FileExistsError):
        run_configuration(path,out,trusted=True)


def test_original_clashing_pose_rejects_before_model_startup_and_is_preserved(tmp_path,monkeypatch):
    from atm_mlmm.workflow import run_configuration
    from atm_mlmm.schema import NumericalDomainError
    import atm_mlmm.hybrid
    import hashlib
    manifest = FIXTURE.parent/'v1/manifest.json'
    base = json.loads((FIXTURE/'config.json').read_text())
    base.update(input_manifest=str(manifest),input_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    path = tmp_path/'config.json'
    path.write_text(json.dumps(base))
    def forbidden(*args,**kwargs):
        raise AssertionError('a known geometric clash must not start a model')
    monkeypatch.setattr(atm_mlmm.hybrid,'build_physical',forbidden)
    out=tmp_path/'rejected'
    with pytest.raises(NumericalDomainError,match='Bondi ratio'):
        run_configuration(path,out,trusted=True)
    assert (out/'snapshot.json').exists() and (out/'configuration.json').exists()


@pytest.mark.parametrize('kind,atoms,ml_atoms',[('abfe',32,14),('rbfe',41,23)])
def test_same_runner_preserves_caps_and_multiple_complete_mobile_groups(tmp_path,kind,atoms,ml_atoms):
    from atm_mlmm.workflow import run_configuration
    from atm_mlmm.schema import from_json
    from tests.workflow.test_cloud_host_guest import ROOT
    fixture=ROOT/'fixtures/cloud_fragment_controls/v1'/kind
    base=json.loads((fixture/'config.json').read_text())
    base['input_manifest']=str(fixture/'manifest.json')
    base['settings'].update(frames_per_state=1,steps_per_frame=1,minimization_iterations=3)
    config=tmp_path/'config.json'
    config.write_text(json.dumps(base))
    out=tmp_path/'control'
    result=run_configuration(config,out,trusted=True)
    assert result['status']=='complete' and result['all_real_atoms']==atoms
    bundle=from_json((out/'worker/bundle.json').read_text())
    assert len(bundle.physical.ml_atom_ids)==ml_atoms
    assert len(bundle.physical.links)==1
    assert len(bundle.transfer.protocol.mobile_groups)==(1 if kind=='abfe' else 2)
    link=bundle.physical.links[0]
    assert bundle.transfer.displacement1_nm[link.final_particle_index]==(0.,0.,0.)
    for parent in (link.ml_parent_id,link.mm_parent_id):
        assert bundle.transfer.displacement1_nm[bundle.physical.real_to_final[parent]]==(0.,0.,0.)
    rows=json.loads((out/'observations.json').read_text())
    assert all(len(row['real_forces_kj_mol_nm'])==atoms for row in rows)
