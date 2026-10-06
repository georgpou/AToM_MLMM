"""Current v2 saved-record validation, zero integration/preparation.

Reuse the protected accepted derivative/probability proofs. Fresh checks bind
this source's final checkpoints and all 12 saved full-force molecular samples.
"""
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np

ROOT=Path('/workspace/AToM_MLMM-g10')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atm_mlmm import exchange as c, exchange_journal as j
from atm_mlmm.adapters import atom
from atm_mlmm.persistence import read_json
from atm_mlmm.schema import Snapshot,from_json
from atm_mlmm.schedule import reduced_potentials
from tests.analytic_oracle import nonlinear_answer

def tree(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}
def snap(s):
    return Snapshot(tuple(s['real_atom_ids']),s['positions_nm'],s['box_nm'],s['velocities_nm_ps'])
def check(kind,count):
    started=time.perf_counter()
    case=Path('/workspace/G10_v7_artifacts/v7-attempt-001')/kind
    run=case/'multistate-run'; before=tree(run)
    rows=j.read_multistate_boundaries(run); m=read_json(run/'metadata.json')
    bundle=from_json((run/'worker/bundle.json').read_text())
    runtime=from_json((run/'worker/runtime.json').read_text())
    assert len(bundle.physical.topology.atoms)==count and len(rows)==2
    original=read_json(ROOT/f'fixtures/solvated_fragment/v2/{kind}/config.json')
    original['settings'].update(frames_per_state=1,steps_per_frame=1,steps_per_phase=1,minimization_iterations=3)
    assert read_json(case/'fixture-input/config.json')==original
    for name in ('manifest.json','system-input.json','partition.json','snapshot.json'):
        assert (case/'fixture-input'/name).read_bytes()==(ROOT/f'fixtures/solvated_fragment/v2/{kind}'/name).read_bytes()
    ligands=[mol for mol in bundle.physical.topology.molecules if mol.role=='ligand']
    mobile={a for group in bundle.transfer.protocol.mobile_groups for a in group.atom_ids}
    assert all(set(mol.atom_ids)<=mobile for mol in ligands)
    parents=sorted({p for link in bundle.physical.links for p in (link.ml_parent_id,link.mm_parent_id)})
    assert parents
    for link in bundle.physical.links:
        particle=bundle.physical.real_to_final[link.ml_parent_id]
        assert bundle.transfer.displacement0_nm[particle]==bundle.transfer.displacement1_nm[particle]==(0.,0.,0.)
    samples=[s for row in rows for s in row['samples']]
    assert len(samples)==6 and len({s['sample_id'] for s in samples})==6
    reconstructed=reduced_potentials(from_json((run/'records.json').read_text()))
    formula=np.zeros((3,6)); force_max=raw_max=final_force_max=position_max=0.
    identities=[]; fresh_evaluations=0
    with ExitStack() as stack:
        workers=[stack.enter_context(atom.load_worker_run(run/'worker',m['worker_manifest_sha256'],trusted=True,
            integrator_seed=m['integrator_seed_base']+w)) for w in range(3)]
        final=run/'boundaries/000001'; reports=read_json(final/'final-state-reports.json')['workers']
        restored=[]
        for w,worker in enumerate(workers):
            state=m['state_ids'][rows[-1]['walker_to_state_final'][w]]
            frames=c._fresh_multistate_check(worker,w,m['walker_ids'][w],state,final,reports[w],m,rows[-1]['samples'][w])
            restored.append(frames)
        for worker,(frame,_) in zip(workers,restored): c._geometry(worker,frame,m['settings'])
        for w,worker in enumerate(workers):
            frame,captured=restored[w]; state=m['state_ids'][rows[-1]['walker_to_state_final'][w]]
            c._fresh_multistate_energy_check(worker,state,reports[w],frame,captured); fresh_evaluations+=1
            position_max=max(position_max,float(np.max(np.abs(np.asarray(frame.positions_nm)-captured.positions_nm))))
            assert reports[w]['total']['snapshot_identity']==captured.content_identity
            identities.append(dict(walker=w,captured_snapshot_identity=captured.content_identity,
                                   restored_snapshot_identity=frame.content_identity,own_snapshot_binding=True))
        for column,s in enumerate(samples):
            w=s['walker_index']; frame=snap(s)
            c._geometry(workers[w],frame,m['settings'])
            result=workers[w].evaluate(frame,s['state_id']); fresh_evaluations+=1
            assert result.total.snapshot_identity==frame.content_identity
            assert np.asarray(s['real_forces_kj_mol_nm']).shape==(count,3)
            force_max=max(force_max,float(np.max(np.abs(np.asarray(result.total.forces_kj_mol_nm)-s['real_forces_kj_mol_nm']))))
            raw=asdict(result.raw); raw_max=max(raw_max,max(abs(raw[k]-s['raw'][k]) for k in raw))
            for row,state in enumerate(bundle.schedule.states):
                expression=nonlinear_answer(s['raw']['u0_raw_kJ_mol'],s['raw']['u1_raw_kJ_mol'],state.parameters)[0]
                formula[row,column]=(expression+s['raw']['outside_energy_kJ_mol'])*m['beta_mol_per_kJ']
    matrix_error=float(np.max(np.abs(formula-reconstructed)))
    pair_formula_max=refresh_max=exponent_max=0.; pair_count=0; outside_count=0
    for row in rows:
        for attempt in row['attempts']:
            decision=attempt['decision']; indices=attempt['attempt']['worker_indices']
            phase=read_json(run/f"boundaries/{row['boundary_index']:06d}/attempts/{decision['attempt_index']:04d}/refreshed.json")
            pair_count+=1; matrix=decision['reduced_energies']
            expected_delta=matrix[0][1]+matrix[1][0]-matrix[0][0]-matrix[1][1]
            exponent_max=max(exponent_max,abs(expected_delta-decision['exponent']))
            for i,state in enumerate(decision['state_ids_before']):
                for col,raw in enumerate(decision['raw_energies'][i]):
                    expr=nonlinear_answer(raw['u0_raw_kJ_mol'],raw['u1_raw_kJ_mol'],m['state_parameters'][state])[0]
                    pair_formula_max=max(pair_formula_max,abs(expr+raw['outside_energy_kJ_mol']-raw['system_total_energy_kJ_mol']))
                    outside_count+=abs(raw['outside_energy_kJ_mol'])>1e-10
            for col,state in enumerate(phase['state_ids_after']):
                index=decision['state_ids_before'].index(state)
                refresh_max=max(refresh_max,abs(phase['energies_after_kj_mol'][col]-decision['raw_energies'][index][col]['system_total_energy_kJ_mol']))
    assert max(force_max,raw_max,matrix_error,pair_formula_max,refresh_max,exponent_max)<=1e-8
    assert position_max<=1e-15 and pair_count==4 and outside_count==16
    assert before==tree(run)
    replay=case/'identical-prefix-replay'
    assert all(tree(run/name)==tree(replay/name) for name in ('initial','boundaries/000000','boundaries/000001'))
    return dict(kind=kind,status='PASS',real_atoms=count,ligand_atom_counts=[len(l.atom_ids) for l in ligands],
        cap_parent_ids=parents,samples=6,attempts=4,actual_evaluations=fresh_evaluations,
        raw_max_abs_error_kJ_mol=raw_max,full_force_max_abs_error_kJ_mol_nm=force_max,
        reconstructed_matrix_shape=list(reconstructed.shape),reconstruction_max_abs_error=matrix_error,
        pair_nonlinear_formula_max_abs_error_kJ_mol=pair_formula_max,
        refreshed_matrix_total_max_abs_error_kJ_mol=refresh_max,exponent_max_abs_error=exponent_max,
        nonzero_pair_outside_entries=outside_count,position_roundtrip_max_nm=position_max,
        own_snapshot_identities=identities,prefix_replay_byte_equal=True,artifacts_unchanged=True,
        binding_result=read_json(run/'summary.json')['binding_result'],runtime_identity=runtime.content_identity,
        elapsed_s=time.perf_counter()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)

result={'cases':[], 'integration_steps_run':0,'preparation_frames_run':0,
        'profile':{p:importlib.metadata.version(p) for p in ('openmm','atom-openmm','mace-torch','numpy','torch')},
        'python_version':sys.version}
for kind,count in (('abfe',224),('rbfe',233)):
    result['cases'].append(check(kind,count))
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    (HERE/'molecular-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result['cases'][-1],sort_keys=True),flush=True)
result['exit_status']=0
(HERE/'molecular-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'cases':2,'actual_evaluations':18,'integration_steps':0,'exit_status':0}))
