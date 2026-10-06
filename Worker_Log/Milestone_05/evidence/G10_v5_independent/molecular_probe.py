"""Reevaluate the exact successful v2 molecular records without more sampling."""
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import resource
import shutil
import sys
import time
from unittest.mock import patch

import numpy as np

ROOT=Path('/workspace/AToM_MLMM-g10')
HERE=ROOT/'Worker_Log/Milestone_05/evidence/G10_v5_independent'
ARTIFACTS=Path('/workspace/G10_v5_independent_artifacts')
sys.path.insert(0,str(ROOT))
from atm_mlmm import exchange as controller
from atm_mlmm import exchange_journal as journal
from atm_mlmm.adapters import atom
from atm_mlmm.persistence import read_json
from atm_mlmm.schema import Snapshot,from_json
from atm_mlmm.schedule import reduced_potentials
from atm_mlmm.workflow import _snapshot
from tests.analytic_oracle import nonlinear_answer


def digest_tree(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def snap(sample):
    return Snapshot(tuple(sample['real_atom_ids']),sample['positions_nm'],sample['box_nm'],sample['velocities_nm_ps'])


def check_case(kind,count):
    started=time.perf_counter()
    case=Path('/workspace/G10_v5_artifacts/probe-fix1')/kind
    run=case/'multistate-run'
    rows=journal.read_multistate_boundaries(run)
    metadata=read_json(run/'metadata.json')
    bundle=from_json((run/'worker/bundle.json').read_text())
    runtime=from_json((run/'worker/runtime.json').read_text())
    assert len(bundle.physical.topology.atoms)==count
    assert len(rows)==2 and len(metadata['state_ids'])==3
    assert metadata['steps_per_boundary']==1 and runtime.temperature_K==300.
    # Fixture config differs only by the four explicitly admitted preparation counts.
    original=read_json(ROOT/f'fixtures/solvated_fragment/v2/{kind}/config.json')
    used=read_json(case/'fixture-input/config.json')
    for key,value in {'frames_per_state':1,'steps_per_frame':1,'steps_per_phase':1,'minimization_iterations':3}.items():
        original['settings'][key]=value
    assert used==original
    for file in ('manifest.json','system-input.json','partition.json','snapshot.json'):
        assert (case/'fixture-input'/file).read_bytes()==(ROOT/f'fixtures/solvated_fragment/v2/{kind}'/file).read_bytes()
    atoms=[a.atom_id for a in bundle.physical.topology.atoms]
    ligands=[m for m in bundle.physical.topology.molecules if m.role=='ligand']
    mobiles={a for g in bundle.transfer.protocol.mobile_groups for a in g.atom_ids}
    assert len(ligands)==(1 if kind=='abfe' else 2)
    assert all(set(m.atom_ids)<=mobiles for m in ligands)
    parents=sorted({p for link in bundle.physical.links for p in (link.ml_parent_id,link.mm_parent_id)})
    assert parents
    for link in bundle.physical.links:
        particle=bundle.physical.real_to_final[link.ml_parent_id]
        assert bundle.transfer.displacement0_nm[particle]==bundle.transfer.displacement1_nm[particle]==(0.,0.,0.)
    samples=[s for row in rows for s in row['samples']]
    assert len(samples)==6 and len({s['sample_id'] for s in samples})==6
    assert all([s['sequence_number'] for s in samples if s['walker_id']==walker]==[1,2]
               for walker in metadata['walker_ids'])
    for w in range(3):
        assert samples[3+w]['step']-samples[w]['step']==1
    before_bytes={name:digest_tree(run/name) for name in ('initial','boundaries/000000','boundaries/000001')}
    replay=case/'identical-prefix-replay'
    assert all(before_bytes[name]==digest_tree(replay/name) for name in before_bytes)
    reconstructed=reduced_potentials(from_json((run/'records.json').read_text()))
    actual=np.empty_like(reconstructed)
    numerical_formula_max=0.; force_max=0.; raw_max=0.; outside_count=0
    position_roundtrip_max=0.; identities=[]; complete_raw={}
    with ExitStack() as stack:
        workers=[stack.enter_context(atom.load_worker_run(run/'worker',metadata['worker_manifest_sha256'],
            trusted=True,integrator_seed=metadata['integrator_seed_base']+w)) for w in range(3)]
        final_boundary=run/'boundaries/000001'
        final_reports=read_json(final_boundary/'final-state-reports.json')['workers']
        final_perm=rows[-1]['walker_to_state_final']
        for w,worker in enumerate(workers):
            state_id=metadata['state_ids'][final_perm[w]]
            controller._fresh_multistate_check(worker,w,metadata['walker_ids'][w],state_id,
                final_boundary,final_reports[w],metadata,rows[-1]['samples'][w])
            restored=_snapshot(worker)
            captured=snap(rows[-1]['samples'][w])
            position_roundtrip_max=max(position_roundtrip_max,float(np.max(np.abs(
                np.asarray(restored.positions_nm)-np.asarray(captured.positions_nm)))))
            assert final_reports[w]['total']['snapshot_identity']==captured.content_identity
            evaluated=worker.evaluate(restored,state_id)
            assert evaluated.total.snapshot_identity==restored.content_identity
            identities.append({'walker':w,'saved_snapshot_identity':captured.content_identity,
                               'fresh_snapshot_identity':restored.content_identity,
                               'each_identity_matches_its_own_snapshot':True})
        for b,row in enumerate(rows):
            for w,sample in enumerate(row['samples']):
                frame=snap(sample)
                assert sample['real_atom_ids']==atoms
                assert np.asarray(sample['real_forces_kj_mol_nm']).shape==(count,3)
                assert [d['map'] for d in sample['domain'] if 'map' in d]==['map0','map1']
                controller._geometry(workers[w],frame,metadata['settings'])
                for s,state in enumerate(bundle.schedule.states):
                    evaluated=workers[w].evaluate(frame,state.state_id)
                    raw=asdict(evaluated.raw)
                    complete_raw[(b,state.state_id,w)]=raw
                    actual[s,3*b+w]=evaluated.total.energy_kj_mol*metadata['beta_mol_per_kJ']
                    expression=nonlinear_answer(raw['u0_raw_kJ_mol'],raw['u1_raw_kJ_mol'],state.parameters)[0]
                    numerical_formula_max=max(numerical_formula_max,abs(
                        expression+raw['outside_energy_kJ_mol']-raw['system_total_energy_kJ_mol']))
                    outside_count+=abs(raw['outside_energy_kJ_mol'])>1e-10
                    if state.state_id==sample['state_id']:
                        raw_max=max(raw_max,max(abs(raw[k]-sample['raw'][k]) for k in raw))
                        force_max=max(force_max,float(np.max(np.abs(
                            np.asarray(evaluated.total.forces_kj_mol_nm)-sample['real_forces_kj_mol_nm']))))
    matrix_max=0.; exponent_max=0.; refresh_max=0.; pair_matrices=[]
    for b,row in enumerate(rows):
        for q in range(2):
            path=run/f'boundaries/{b:06d}/attempts/{q:04d}'
            attempt=read_json(path/'attempt.json')
            evaluated=read_json(path/'evaluated.json')
            refreshed=read_json(path/'refreshed.json')
            expected=[[complete_raw[(b,s,w)]['system_total_energy_kJ_mol']*metadata['beta_mol_per_kJ']
                       for w in attempt['worker_indices']] for s in attempt['state_ids']]
            delta=expected[0][1]+expected[1][0]-expected[0][0]-expected[1][1]
            matrix_max=max(matrix_max,float(np.max(np.abs(np.asarray(expected)-evaluated['reduced_energies']))))
            exponent_max=max(exponent_max,abs(delta-evaluated['exponent']))
            expected_after=[complete_raw[(b,s,w)]['system_total_energy_kJ_mol']
                            for s,w in zip(refreshed['state_ids_after'],attempt['worker_indices'])]
            refresh_max=max(refresh_max,float(np.max(np.abs(np.asarray(expected_after)-refreshed['energies_after_kj_mol']))))
            pair_matrices.append({'boundary':b,'attempt':q,'worker_indices':attempt['worker_indices'],
                                  'state_ids':attempt['state_ids'],'actual_reduced_matrix':expected,
                                  'actual_exponent':delta,'accepted':refreshed['accepted']})
    reconstruction_max=float(np.max(np.abs(actual-reconstructed)))
    assert max(numerical_formula_max,force_max,raw_max,matrix_max,exponent_max,refresh_max,reconstruction_max)<=1e-8
    assert outside_count==18
    # The retained resealed stale probe is copied before exercising the runtime.
    # Its exact current-source bundle already records the requested 2e-12 nm fault.
    stale=ARTIFACTS/f'{kind}-molecular-stale-copy'
    shutil.copytree(case/'stale-coordinate-probe',stale)
    assert len(journal.read_multistate_boundaries(stale))==2
    evaluation_calls=[]
    def forbidden_evaluation(*args,**kwargs):
        evaluation_calls.append(True)
        raise AssertionError('stale coordinate reached scientific evaluation')
    rejection=None
    with patch.object(atom.WorkerRun,'evaluate',forbidden_evaluation):
        try:
            controller.resume_multistate_exchange(stale,trusted=True)
        except Exception as error:
            rejection=f'{type(error).__name__}: {error}'
    assert rejection and 'beyond unit-conversion roundoff' in rejection
    assert not evaluation_calls and not (stale/'pending').exists()
    assert all(before_bytes[name]==digest_tree(run/name) for name in before_bytes)
    return {'kind':kind,'status':'PASS','real_atoms':count,'ligand_atom_counts':[len(m.atom_ids) for m in ligands],
            'cap_parent_ids':parents,'samples':6,'attempts':4,'schedule_evaluations':18,
            'outside_nonzero_entries':outside_count,'actual_schedule_reduced_matrix':actual.tolist(),
            'pair_matrices':pair_matrices,'reconstruction_max_abs_error':reconstruction_max,
            'matrix_max_abs_error':matrix_max,'exponent_max_abs_error':exponent_max,
            'refresh_max_abs_error_kJ_mol':refresh_max,'raw_max_abs_error_kJ_mol':raw_max,
            'full_force_max_abs_error_kJ_mol_nm':force_max,'independent_mixing_formula_max_abs_error_kJ_mol':numerical_formula_max,
            'checkpoint_sample_position_roundtrip_max_nm':position_roundtrip_max,'snapshot_identities':identities,
            'stale_coordinate_rejection':rejection,'stale_coordinate_evaluate_calls':len(evaluation_calls),
            'stale_pending_created':False,'identical_prefix_replay_hashes_equal':True,
            'retained_artifacts_unchanged':True,'binding_result':'not_evaluated',
            'runtime_identity':runtime.content_identity,'physical_identity':bundle.physical.content_identity,
            'alchemical_identity':bundle.content_identity,'manifest_hashes':{n:journal.sha(run/n/'manifest.json') for n in before_bytes},
            'elapsed_seconds':time.perf_counter()-started,
            'process_high_water_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}


def main():
    result={'cases':[],'integration_steps_run':0,'new_preparation_frames':0}
    for kind,count in (('abfe',224),('rbfe',233)):
        row=check_case(kind,count)
        result['cases'].append(row)
        print(json.dumps({'case':kind,'status':row['status'],'raw_max':row['raw_max_abs_error_kJ_mol'],
                          'force_max':row['full_force_max_abs_error_kJ_mol_nm'],'elapsed_seconds':row['elapsed_seconds']},sort_keys=True),flush=True)
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    result['exit_status']=0
    (HERE/'molecular-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'cases':2,'exit_status':0,'finished_utc':result['finished_utc']},sort_keys=True))


if __name__=='__main__':
    main()
