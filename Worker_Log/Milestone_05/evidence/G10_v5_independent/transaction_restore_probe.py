"""Independent restart-domain/timeline and crash-durability characterizations."""
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

import numpy as np
import openmm as mm
from openmm import unit

ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = ROOT/'Worker_Log/Milestone_05/evidence/G10_v5_independent'
ARTIFACTS = Path('/workspace/G10_v5_independent_artifacts')
sys.path.insert(0, str(ROOT))
from atm_mlmm import exchange as controller
from atm_mlmm import exchange_journal as journal
from atm_mlmm.adapters import atom
from atm_mlmm.persistence import read_json, write_json
from atm_mlmm.workflow import _snapshot


def clone(name):
    run = ARTIFACTS/name
    shutil.copytree(ARTIFACTS/'rbfe-prefix', run)
    return run, read_json(run/'metadata.json'), run/'boundaries/000000'


def cached_capture(worker, boundary):
    context = worker.evaluator.context
    (boundary/'workers/worker-000.chk').write_bytes(context.createCheckpoint())
    portable = context.getState(getPositions=True, getVelocities=True, getParameters=True)
    (boundary/'workers/worker-000-state.xml').write_text(mm.XmlSerializer.serialize(portable))


def timeline_probe():
    run, metadata, boundary = clone('restored-timeline')
    state = metadata['state_ids'][read_json(boundary/'record.json')['walker_to_state_final'][0]]
    with atom.load_worker_run(run/'worker', metadata['worker_manifest_sha256'], trusted=True,
                             integrator_seed=metadata['integrator_seed_base']) as worker:
        worker.restore_checkpoint((boundary/'workers/worker-000.chk').read_bytes(), state)
        before = _snapshot(worker)
        worker.evaluator.context.setStepCount(99)
        worker.evaluator.context.setTime(9.99*unit.picosecond)
        after = _snapshot(worker)
        assert before == after  # Positions, velocities, parameters and physical data unchanged.
        cached_capture(worker, boundary)
    journal.seal_tree(boundary, index=0)
    assert len(journal.read_multistate_boundaries(run)) == 1
    summary = controller.resume_multistate_exchange(run, trusted=True)
    rows = journal.read_multistate_boundaries(run)
    old, new = rows[0]['samples'][0], rows[1]['samples'][0]
    report = read_json(boundary/'final-state-reports.json')['workers'][0]
    violated = new['step']-old['step'] != metadata['steps_per_boundary']
    assert violated
    return {'name': 'restored-checkpoint-timeline', 'status': 'VIOLATION',
            'reader_admitted': True, 'resume_completed': summary['status'],
            'saved_step': old['step'], 'saved_time_ps': old['time_ps'],
            'saved_final_report_step': report['step'], 'saved_final_report_time_ps': report['time_ps'],
            'altered_checkpoint_step': 99, 'altered_checkpoint_time_ps': 9.99,
            'next_committed_step': new['step'], 'next_committed_time_ps': new['time_ps'],
            'expected_step_increment': metadata['steps_per_boundary'],
            'actual_step_increment': new['step']-old['step'],
            'positions_velocities_and_snapshot_identity_unchanged': True,
            'final_manifest_sha256': journal.sha(run/'boundaries/000001/manifest.json')}


def geometry_probe():
    run, metadata, boundary = clone('restored-invalid-domain')
    sample = read_json(boundary/'samples/worker-000.json')
    final_state = metadata['state_ids'][read_json(boundary/'record.json')['walker_to_state_final'][0]]
    expected_domain_error = None
    with atom.load_worker_run(run/'worker', metadata['worker_manifest_sha256'], trusted=True,
                             integrator_seed=metadata['integrator_seed_base']) as worker:
        worker.restore_checkpoint((boundary/'workers/worker-000.chk').read_bytes(), final_state)
        original = _snapshot(worker)
        positions = np.asarray(original.positions_nm, dtype=float).copy()
        # A complete environmental molecule (one atom) now overlaps a ligand atom.
        # Maps, fixed ML membership, ligand composition and Hamiltonian are unchanged.
        env = original.real_atom_ids.index('env')
        ligand = original.real_atom_ids.index('a1')
        positions[env] = positions[ligand]
        moved = replace(original, positions_nm=positions)
        try:
            controller._geometry(worker, moved, metadata['settings'])
        except Exception as error:
            expected_domain_error = f'{type(error).__name__}: {error}'
        assert expected_domain_error is not None
        sample_result = worker.evaluate(moved, sample['state_id'])
        saved = worker.evaluator.context.getState(getPositions=True, getVelocities=True, getParameters=True)
        sample.update(positions_nm=moved.positions_nm, velocities_nm_ps=moved.velocities_nm_ps,
                      real_forces_kj_mol_nm=sample_result.total.forces_kj_mol_nm,
                      total_energy_kJ_mol=sample_result.total.energy_kj_mol,
                      raw=asdict(sample_result.raw), parameters=dict(sample_result.parameters))
        write_json(boundary/'samples/worker-000.json', sample)
        (boundary/'samples/worker-000-state.xml').write_text(mm.XmlSerializer.serialize(saved))
        (boundary/'samples/worker-000.chk').write_bytes(worker.evaluator.context.createCheckpoint())
        # Recompute the affected pair-phase entries to retain complete internally
        # consistent four-entry matrices at the modified boundary coordinates.
        for q in range(2):
            attempt_dir = boundary/'attempts'/f'{q:04d}'
            attempt = read_json(attempt_dir/'attempt.json')
            if 0 not in attempt['worker_indices']:
                continue
            column = attempt['worker_indices'].index(0)
            docs = {name:read_json(attempt_dir/(name+'.json')) for name in ('evaluated','decision','refreshed','history')}
            new_raw = [asdict(worker.evaluate(moved, state_id).raw) for state_id in attempt['state_ids']]
            for name in ('evaluated','decision','refreshed'):
                doc = docs[name]
                for s in range(2):
                    doc['raw_energies'][s][column] = new_raw[s]
                    doc['reduced_energies'][s][column] = new_raw[s]['system_total_energy_kJ_mol']*metadata['beta_mol_per_kJ']
                matrix = doc['reduced_energies']
                doc['exponent'] = matrix[0][1]+matrix[1][0]-matrix[0][0]-matrix[1][1]
            selected_state = docs['decision']['state_ids_after'][column]
            docs['refreshed']['energies_after_kj_mol'][column] = worker.evaluate(moved, selected_state).total.energy_kj_mol
            docs['history']['decision'] = docs['decision']
            for name, document in docs.items():
                write_json(attempt_dir/(name+'.json'), document)
        final_result = worker.evaluate(moved, final_state)
        saved = worker.evaluator.context.getState(getPositions=True, getVelocities=True, getParameters=True)
        reports = read_json(boundary/'final-state-reports.json')
        reports['workers'][0] = controller._multistate_report(worker, 0, metadata['walker_ids'][0],
                                                          final_state, moved, final_result, saved)
        write_json(boundary/'final-state-reports.json', reports)
        cached_capture(worker, boundary)
    journal.seal_tree(boundary, index=0)
    assert len(journal.read_multistate_boundaries(run)) == 1
    evaluations = []
    geometry_calls = []
    old_evaluate, old_geometry = atom.WorkerRun.evaluate, controller._geometry
    def evaluate(self, frame, state_id):
        evaluations.append({'seed': self.integrator_seed, 'step': self.evaluator.context.getStepCount()})
        return old_evaluate(self, frame, state_id)
    def geometry(worker, frame, settings):
        geometry_calls.append({'seed': worker.integrator_seed, 'step': worker.evaluator.context.getStepCount(),
                               'environment_position': frame.positions_nm[frame.real_atom_ids.index('env')]})
        return old_geometry(worker, frame, settings)
    resume_error = None
    with patch.object(atom.WorkerRun, 'evaluate', evaluate), patch.object(controller, '_geometry', geometry):
        try:
            controller.resume_multistate_exchange(run, trusted=True)
        except Exception as error:
            resume_error = f'{type(error).__name__}: {error}'
    failure = read_json(run/'pending/failures/worker-000/error.json')
    assert failure['actual_step'] == 2  # Unsafe restore advanced before geometry admission.
    return {'name': 'restored-both-map-domain', 'status': 'VIOLATION', 'reader_admitted': True,
            'independent_preintegration_domain_rejection': expected_domain_error,
            'resume_error': resume_error, 'fresh_evaluations_before_domain_rejection': evaluations,
            'geometry_calls': geometry_calls, 'saved_step': 1,
            'failed_worker_actual_step': failure['actual_step'], 'pending_created': True,
            'final_report_and_all_affected_pair_matrix_values_freshly_recomputed': True,
            'pending_failure_sha256': journal.sha(run/'pending/failure.json')}


def publication_failure(name, kind):
    run, metadata, boundary = clone(name)
    committed_hash_before = journal.sha(boundary/'manifest.json')
    error_text = None
    if kind == 'parent-fsync':
        old_sync = controller.sync_directory
        def fail_sync(path):
            if Path(path) == run/'boundaries' and (run/'boundaries/000001').exists():
                raise OSError('independent parent-fsync failure after actual rename')
            return old_sync(path)
        manager = patch.object(controller, 'sync_directory', fail_sync)
    else:
        def fail_derived(*args, **kwargs):
            raise OSError('independent derived-record failure after commit')
        manager = patch.object(controller, 'to_json', fail_derived)
    with manager:
        try:
            controller.resume_multistate_exchange(run, trusted=True)
        except Exception as error:
            error_text = f'{type(error).__name__}: {error}'
    assert error_text is not None
    assert len(journal.read_multistate_boundaries(run)) == 2
    assert committed_hash_before == journal.sha(boundary/'manifest.json')
    archives = list((run/'failures').rglob('*')) if (run/'failures').exists() else []
    assert not (run/'pending').exists()
    assert not archives
    return {'name': name, 'status': 'VIOLATION', 'primary_exception': error_text,
            'committed_boundaries': 2, 'authoritative_commit_preserved': True,
            'prior_manifest_unchanged': True, 'archived_primary_or_worker_artifacts': [],
            'final_manifest_sha256': journal.sha(run/'boundaries/000001/manifest.json')}


def fsync_trace():
    root = ARTIFACTS/'fsync-order'
    root.mkdir()
    pending = root/'pending'
    pending.mkdir()
    (root/'boundaries').mkdir()
    (pending/'payload').write_text('frozen transaction payload\n')
    events = []
    old_sync, old_rename = journal.os.fsync, journal.os.rename
    def observed_fsync(fd):
        events.append({'operation':'fsync', 'path':os.readlink(f'/proc/self/fd/{fd}')})
        return old_sync(fd)
    def observed_rename(source, target):
        events.append({'operation':'rename','source':str(source),'target':str(target)})
        return old_rename(source, target)
    with patch.object(journal.os, 'fsync', observed_fsync), patch.object(journal.os, 'rename', observed_rename):
        controller._publish_multistate_boundary(pending, root/'boundaries/000000', 0)
    after = events[next(i for i, e in enumerate(events) if e['operation'] == 'rename')+1:]
    parents = [e['path'] for e in after if e['operation'] == 'fsync']
    assert str(root/'boundaries') in parents and str(root) not in parents
    # Rollback can include failure capture files that have never had file fsync.
    rollback = ARTIFACTS/'rollback-fsync'
    (rollback/'pending/failures').mkdir(parents=True)
    (rollback/'pending/failures/state.xml').write_text('<State/>\n')
    rollback_events = []
    def rollback_fsync(fd):
        rollback_events.append({'operation':'fsync','path':os.readlink(f'/proc/self/fd/{fd}')})
        return old_sync(fd)
    with patch.object(journal.os, 'fsync', rollback_fsync):
        archived = journal.preserve_multistate_pending(rollback)
    assert not any(e['path'].endswith('state.xml') for e in rollback_events)
    return {'name':'publication-and-rollback-fsync-order', 'status':'VIOLATION',
            'publication_events':events, 'postrename_fsynced_parents':parents,
            'missing_postrename_source_parent':str(root), 'rollback_events':rollback_events,
            'rollback_archive':str(archived), 'preserved_failure_file_fsynced':False,
            'scope':'observed syscall ordering; no power-loss experiment or crash reproduction claimed'}


def main():
    rows = [timeline_probe(), geometry_probe(),
            publication_failure('postrename-parent-fsync', 'parent-fsync'),
            publication_failure('postrename-derived-report', 'derived'), fsync_trace()]
    for row in rows:
        print(json.dumps(row, sort_keys=True), flush=True)
    result = {'probes':rows, 'violation_count':len(rows), 'exit_status':1,
              'finished_utc':datetime.now(timezone.utc).isoformat()}
    (HERE/'transaction-restore-results.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'probes':len(rows),'violation_count':len(rows),'exit_status':1,
                      'finished_utc':result['finished_utc']},sort_keys=True))
    return 1


if __name__ == '__main__':
    sys.exit(main())
