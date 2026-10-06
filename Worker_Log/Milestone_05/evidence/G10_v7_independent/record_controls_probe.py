"""Independent same-attempt arithmetic/history and direct reader symlink control."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

import repair_probe as p
from tests.analytic_oracle import nonlinear_answer

HERE=p.HERE
RESULTS=[]


def record(name,**details):
    RESULTS.append(dict(name=name,status='PASS',**details))
    (HERE/'record-controls-results.json').write_text(json.dumps(dict(probes=RESULTS,
        finished_utc=datetime.now(timezone.utc).isoformat(),exit_status=0),indent=2,sort_keys=True)+'\n')
    print(json.dumps(RESULTS[-1],sort_keys=True),flush=True)


def records(run):
    metadata=p.read_json(run/'metadata.json'); rows=p.j.read_multistate_boundaries(run)
    maximum={name:0. for name in ('complete_total','reduced_total','refresh','exponent')}
    outcomes={True:0,False:0}; entries=outside_entries=sample_count=0; ids=set()
    current=list(range(len(metadata['state_ids'])))
    for row in rows:
        assert current==row['walker_to_state_start']
        for worker,sample in enumerate(row['samples']):
            assert sample['state_id']==metadata['state_ids'][current[worker]]
            assert sample['sample_id'] not in ids
            assert sample['walker_id']==metadata['walker_ids'][worker]
            assert sample['sequence_number']==row['boundary_index']+1
            ids.add(sample['sample_id']); sample_count+=1
        for history in row['attempts']:
            decision=history['decision']; attempt=history['attempt']; index=decision['attempt_index']
            directory=run/f"boundaries/{row['boundary_index']:06d}/attempts/{index:04d}"
            evaluated=p.read_json(directory/'evaluated.json'); refreshed=p.read_json(directory/'refreshed.json')
            i,j=attempt['state_pair_indices']; selected=[current.index(i),current.index(j)]
            assert selected==attempt['worker_indices']
            assert history['resolved_state_to_walker']==[current.index(k) for k in range(len(current))]
            assert current==decision['walker_to_state_before']
            accepted=decision['accepted']; assert type(accepted) is bool; outcomes[accepted]+=1
            for state_index,state in enumerate(decision['state_ids_before']):
                for column,raw in enumerate(evaluated['raw_energies'][state_index]):
                    expr=nonlinear_answer(raw['u0_raw_kJ_mol'],raw['u1_raw_kJ_mol'],metadata['state_parameters'][state])[0]
                    maximum['complete_total']=max(maximum['complete_total'],abs(expr+raw['outside_energy_kJ_mol']-raw['system_total_energy_kJ_mol']))
                    maximum['reduced_total']=max(maximum['reduced_total'],abs(raw['system_total_energy_kJ_mol']/(.00831446261815324*300.)-evaluated['reduced_energies'][state_index][column]))
                    entries+=1; outside_entries+=raw['outside_energy_kJ_mol']!=0.
            matrix=evaluated['reduced_energies']
            maximum['exponent']=max(maximum['exponent'],abs(matrix[0][1]+matrix[1][0]-matrix[0][0]-matrix[1][1]-decision['exponent']))
            if accepted: current[selected[0]],current[selected[1]]=current[selected[1]],current[selected[0]]
            assert current==decision['walker_to_state_after']
            for column,worker in enumerate(selected):
                state=metadata['state_ids'][current[worker]]
                before_row=decision['state_ids_before'].index(state)
                expected=evaluated['raw_energies'][before_row][column]['system_total_energy_kJ_mol']
                maximum['refresh']=max(maximum['refresh'],abs(expected-refreshed['energies_after_kj_mol'][column]))
        assert current==row['walker_to_state_final']
        assert row['state_to_walker_final']==[current.index(k) for k in range(len(current))]
    assert max(maximum.values())<=1e-8
    record('same-attempt-history-'+run.parent.name+'-'+run.name,run=str(run),samples=sample_count,
           accepted=outcomes[True],rejected=outcomes[False],matrix_entries=entries,
           nonzero_outside_entries=outside_entries,max_abs_errors=maximum,
           immutable_capture_labels_unique_ids_and_live_full_inverses=True)
    return outcomes


def symlink():
    run,metadata,boundary=p.clone('cont-reader-symlink')
    link=boundary/'samples/extra-link.json'; link.symlink_to('worker-000.json')
    before=p.tree(run); loader_calls=[]
    def loader(*args,**kwargs):
        loader_calls.append(True); raise RuntimeError('unexpected trusted loader')
    reader=p.error_call(lambda:p.j.read_multistate_boundaries(run))
    with patch.object(p.atom,'load_worker_run',loader):
        resume=p.error_call(lambda:p.c.resume_multistate_exchange(run,trusted=True))
    assert reader and 'symbolic link' in reader and resume and not loader_calls
    assert before==p.tree(run) and link.is_symlink() and link.readlink()==Path('worker-000.json')
    record('direct-inert-symlink-rejection',reader_error=reader,resume_error=resume,
           loader_calls=loader_calls,unchanged_regular_files_and_symlink=True)


total={True:0,False:0}
for run in (p.ART/'reference',Path('/workspace/G10_v7_artifacts/v7-attempt-001/abfe/multistate-run'),
            Path('/workspace/G10_v7_artifacts/v7-attempt-001/rbfe/multistate-run')):
    outcomes=records(run)
    for accepted in total: total[accepted]+=outcomes[accepted]
assert total[True]>0 and total[False]>0, total
symlink()
print(json.dumps({'probes':len(RESULTS),'accepted':total[True],'rejected':total[False],'exit_status':0}))
