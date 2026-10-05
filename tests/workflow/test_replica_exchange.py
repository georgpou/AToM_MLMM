"""Fresh actual-worker exchange, with independent energy and RNG thresholds."""
from contextlib import ExitStack
from dataclasses import replace
import math

import numpy as np
import pytest

from tests.analytic_oracle import (REFERENCE, mapped_positions, physical_answer,
                                  nonlinear_answer, outside_answer)
from tests.workflow.test_atom_force_routing import atom_case
from tests.workflow.test_solvated_handover import water_run


def multistate_oracle_raw(snapshot,kind,parameters,schedule):
    u0=physical_answer(mapped_positions(snapshot.positions_nm,kind,0),marker=20.)[0]
    u1=physical_answer(mapped_positions(snapshot.positions_nm,kind,1),marker=20.)[0]
    expression=nonlinear_answer(u0,u1,parameters)[0]
    outside=outside_answer(snapshot.positions_nm)[0]
    from atm_mlmm.schedule import softened_perturbation
    return {'u0_raw_kJ_mol':u0,'u1_raw_kJ_mol':u1,'delta_u_raw_kJ_mol':u1-u0,
            'delta_u_softcore_kJ_mol':softened_perturbation(u0,u1,schedule,parameters),
            'atm_expression_energy_kJ_mol':expression,'outside_energy_kJ_mol':outside,
            'system_total_energy_kJ_mol':expression+outside}


def sample_snapshot(sample):
    from atm_mlmm.schema import Snapshot
    positions=tuple(tuple(row) for row in sample['positions_nm'])
    velocities=None if sample['velocities_nm_ps'] is None else tuple(tuple(row) for row in sample['velocities_nm_ps'])
    box=None if sample['box_nm'] is None else tuple(tuple(row) for row in sample['box_nm'])
    return Snapshot(tuple(sample['real_atom_ids']),positions,box,velocities)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('accept', (False, True))
def test_acceptance_uses_actual_reduced_energies(tmp_path, monkeypatch, kind, accept):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run, load_worker_run, attempt_pair_exchange
    from atom_openmm import gibbs_sampling
    physical, transfer, schedule, restraints, snapshot = atom_case(kind, marker=20.)
    x = np.array(snapshot.positions_nm)
    x[2] += (.16, -.12, .04)
    frames = (snapshot, replace(snapshot, positions_nm=x))
    matrix = np.empty((2, 2))
    for k, state in enumerate(schedule.states):
        for w, frame in enumerate(frames):
            u = [physical_answer(mapped_positions(frame.positions_nm, kind, m), marker=20.)[0] for m in (0, 1)]
            matrix[k, w] = (nonlinear_answer(*u, state.parameters)[0] + outside_answer(frame.positions_nm)[0]) / (.00831446261815324 * 300.)
    ids = ('first', 'second')
    delta = matrix[0, 1] + matrix[1, 0] - matrix[0, 0] - matrix[1, 1]
    if delta < 0:
        ids = ids[::-1]
        delta = -delta
    assert delta > 1e-5
    probability = math.exp(-delta)
    draw = probability * .5 if accept else (1. + probability) * .5
    # Only control the random variate; execute the real upstream decision.
    monkeypatch.setattr(gibbs_sampling, '_random', lambda: draw)
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as source:
        manifest, digest = export_worker_run(source, tmp_path / 'export', snapshot, 'first')
    with ExitStack() as stack:
        workers = tuple(stack.enter_context(load_worker_run(manifest.parent, digest, trusted=True)) for _ in range(2))
        # Poison cached reports with unrelated coordinates/state before the call.
        for worker in workers:
            worker.evaluate(frames[1], 'second')
        report = attempt_pair_exchange(workers, frames, ids, ('walker-A', 'walker-B'))
        order = [0 if sid == 'first' else 1 for sid in ids]
        np.testing.assert_allclose(report['reduced_energies'], matrix[order], atol=1e-8, rtol=0)
        assert report['exponent'] == pytest.approx(delta, abs=1e-8)
        assert report['accepted'] is accept
        assert tuple(report['walker_ids']) == ('walker-A', 'walker-B')
        expected = ids[::-1] if accept else ids
        assert tuple(report['state_ids_after']) == expected
        assert tuple(report['state_ids_before']) == ids
        for w, worker in enumerate(workers):
            assert worker.evaluator._state_id == expected[w]
            assert worker.evaluator.context.getParameter('Direction') == next(s for s in schedule.states if s.state_id == expected[w]).parameters['Direction']
            from openmm import unit
            positions = worker.evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            np.testing.assert_array_equal(positions[list(physical.old_to_new)], frames[w].positions_nm)
            current = worker.evaluate(frames[w], expected[w])
            assert report['energies_after_kj_mol'][w] == pytest.approx(current.total.energy_kj_mol, abs=1e-8)
            checkpoint = worker.evaluator.context.createCheckpoint()
            worker.set_state(ids[1-w])
            worker.restore_checkpoint(checkpoint, expected[w])
            assert worker.evaluate(frames[w], expected[w]).raw == current.raw


def test_exchange_rejects_ambiguous_walker_labels_before_evaluation():
    from atm_mlmm.adapters.atom import attempt_pair_exchange
    from atm_mlmm.schema import IdentityError
    with pytest.raises(IdentityError, match='walker'):
        attempt_pair_exchange((None, None), (None, None), ('first', 'second'), ('same', 'same'))


@pytest.mark.model_assets
def test_parameter_update_and_state_history(water_run, monkeypatch):
    import json
    import openmm as mm
    from openmm import unit
    from atm_mlmm.adapters.atom import load_worker_run, attempt_pair_exchange
    from atm_mlmm.schema import Snapshot, from_json
    from atm_mlmm.schedule import reduced_potentials
    from atom_openmm import gibbs_sampling
    _, _, output, summary, bundle, rows = water_run
    records = from_json((output / 'records.json').read_text())
    matrix = reduced_potentials(records)[[0, 2]][:, [0, 2]]
    selected = (rows[0], rows[2])
    snapshots = tuple(Snapshot(tuple(row['real_atom_ids']), row['positions_nm'], row['box_nm']) for row in selected)
    ids = tuple(row['state_id'] for row in selected)
    walkers = tuple(row['walker_id'] for row in selected)
    monkeypatch.setattr(gibbs_sampling, '_random', lambda: 0.)
    with ExitStack() as stack:
        workers = tuple(stack.enter_context(load_worker_run(output / 'worker', summary['worker_manifest_sha256'], trusted=True)) for _ in range(2))
        velocities = []
        for w, worker in enumerate(workers):
            worker.restore_checkpoint((output / 'samples' / f'{2*w:06d}' / 'checkpoint.chk').read_bytes(), ids[w])
            velocities.append(worker.evaluator.context.getState(getVelocities=True).getVelocities(asNumpy=True))
        report = attempt_pair_exchange(workers, snapshots, ids, walkers)
        np.testing.assert_allclose(report['reduced_energies'], matrix, atol=1e-8, rtol=0)
        assert report['accepted'] and report['walker_ids'] == walkers
        assert report['state_ids_after'] == ids[::-1]
        (output / 'exchange-report.json').write_text(json.dumps(report, indent=2)+'\n')
        for w, worker in enumerate(workers):
            state = worker.evaluator.context.getState(getPositions=True, getVelocities=True, getParameters=True)
            np.testing.assert_array_equal(state.getVelocities(asNumpy=True), velocities[w])
            checkpoint = worker.evaluator.context.createCheckpoint()
            portable = mm.XmlSerializer.serialize(state)
            worker.set_state(ids[w])
            worker.restore_checkpoint(checkpoint, report['state_ids_after'][w])
            worker.restore_portable_state(portable, report['state_ids_after'][w])
            actual = worker.evaluate(snapshots[w], report['state_ids_after'][w])
            assert actual.total.energy_kj_mol == pytest.approx(report['energies_after_kj_mol'][w], abs=1e-8)
            assert tuple(actual.total.real_atom_ids) == snapshots[w].real_atom_ids


def test_exchange_rejects_incompatible_hamiltonians_before_sampling(tmp_path, monkeypatch):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run, load_worker_run, attempt_pair_exchange
    from atm_mlmm.schema import IdentityError
    from atom_openmm import gibbs_sampling
    def forbidden(*args):
        raise AssertionError('incompatible workers must not reach a swap decision')
    monkeypatch.setattr(gibbs_sampling, 'pairwise_metropolis_sampling', forbidden)
    exports = []
    for n, kind in enumerate(('abfe', 'rbfe')):
        physical, transfer, schedule, restraints, snapshot = atom_case(kind)
        with build_atom(physical, transfer, schedule, restraints, REFERENCE) as source:
            exports.append((*export_worker_run(source, tmp_path / str(n), snapshot, 'first'), snapshot))
    with ExitStack() as stack:
        workers = tuple(stack.enter_context(load_worker_run(manifest.parent, digest, trusted=True)) for manifest, digest, _ in exports)
        with pytest.raises(IdentityError, match='Hamiltonian'):
            attempt_pair_exchange(workers, tuple(s for _, _, s in exports), ('first', 'second'), ('A', 'B'))


@pytest.mark.parametrize('kind',('abfe','rbfe'))
def test_multistate_decision_uses_fresh_nonlinear_outside_energies(tmp_path,monkeypatch,kind):
    from tests.workflow.test_persistent_exchange import prepare_multistate
    from atm_mlmm.adapters import atom
    from atm_mlmm.exchange import run_multistate_exchange
    from atm_mlmm.exchange_journal import read_multistate_boundaries
    from atm_mlmm.persistence import read_json
    from atm_mlmm.schema import from_json
    from atom_openmm import gibbs_sampling
    prepared=prepare_multistate(tmp_path/'prepared',kind=kind)
    bundle=from_json((prepared/'worker/bundle.json').read_text())
    calls=[]; original=atom.attempt_pair_exchange
    def poison_then_exchange(workers,snapshots,state_ids,walker_ids,**kwargs):
        calls.append((tuple(walker_ids),tuple(state_ids)))
        poison=next(state.state_id for state in bundle.schedule.states if state.state_id not in state_ids)
        for worker,snapshot in zip(workers,snapshots):
            worker.evaluate(snapshot,poison)
        return original(workers,snapshots,state_ids,walker_ids,**kwargs)
    monkeypatch.setattr(atom,'attempt_pair_exchange',poison_then_exchange)
    monkeypatch.setattr(gibbs_sampling,'_random',lambda:0.)
    output=tmp_path/'exchange'
    run_multistate_exchange(prepared,output,state_ids=('first','middle','third'),
        state_pairs=((0,1),(1,2)),boundaries=1,steps_per_boundary=1,seed=73,trusted=True)
    assert len(calls)==2
    boundary=read_multistate_boundaries(output)[0]
    samples={sample['walker_index']:sample for sample in boundary['samples']}
    for index in range(2):
        attempt_dir=output/'boundaries/000000/attempts'/f'{index:04d}'
        attempt=read_json(attempt_dir/'attempt.json')
        evaluated=read_json(attempt_dir/'evaluated.json')
        decision=read_json(attempt_dir/'decision.json')
        refreshed=read_json(attempt_dir/'refreshed.json')
        worker_indices=attempt['worker_indices']
        expected_matrix=[]; expected_raw=[]
        for state_id in attempt['state_ids']:
            state=next(state for state in bundle.schedule.states if state.state_id==state_id)
            row=[]; raw_row=[]
            for worker_index in worker_indices:
                sample=samples[worker_index]
                snapshot=sample_snapshot(sample)
                raw=multistate_oracle_raw(snapshot,kind,state.parameters,bundle.schedule)
                raw_row.append(raw)
                row.append(raw['system_total_energy_kJ_mol']/(.00831446261815324*300.))
            expected_matrix.append(row); expected_raw.append(raw_row)
        np.testing.assert_allclose(evaluated['reduced_energies'],expected_matrix,atol=1e-8,rtol=0)
        for state_index in range(2):
            for walker_index in range(2):
                for name,value in expected_raw[state_index][walker_index].items():
                    assert evaluated['raw_energies'][state_index][walker_index][name]==pytest.approx(value,abs=1e-8)
        assert decision['accepted'] is True
        after=decision['state_ids_after']
        for column,worker_index in enumerate(worker_indices):
            state=next(state for state in bundle.schedule.states if state.state_id==after[column])
            sample=samples[worker_index]
            snapshot=sample_snapshot(sample)
            expected=multistate_oracle_raw(snapshot,kind,state.parameters,bundle.schedule)
            assert refreshed['energies_after_kj_mol'][column]==pytest.approx(
                expected['system_total_energy_kJ_mol'],abs=1e-8)


@pytest.mark.parametrize('kind',('abfe','rbfe'))
@pytest.mark.parametrize('accept',(False,True))
def test_multistate_actual_adapter_accept_and_reject_thresholds(tmp_path,monkeypatch,kind,accept):
    from tests.workflow.test_persistent_exchange import prepare_multistate
    from atm_mlmm.adapters.atom import load_worker_run,attempt_pair_exchange
    from atm_mlmm.persistence import read_json
    from atm_mlmm.schema import from_json
    from atom_openmm import gibbs_sampling
    prepared=prepare_multistate(tmp_path/'prepared',kind=kind)
    manifest=read_json(prepared/'worker/manifest.json')
    bundle=from_json((prepared/'worker/bundle.json').read_text())
    snapshot=from_json((prepared/'worker/snapshot.json').read_text())
    changed=np.array(snapshot.positions_nm,copy=True)
    changed[2]+=(.16,-.12,.04)
    frames=(snapshot,replace(snapshot,positions_nm=changed))
    def independent(state_id,frame):
        state=next(state for state in bundle.schedule.states if state.state_id==state_id)
        raw=multistate_oracle_raw(frame,kind,state.parameters,bundle.schedule)
        return raw['system_total_energy_kJ_mol']
    selected=None
    for first in bundle.schedule.states:
        for second in bundle.schedule.states:
            if first.state_id==second.state_id: continue
            delta=((independent(first.state_id,frames[1])+independent(second.state_id,frames[0])-
                    independent(first.state_id,frames[0])-independent(second.state_id,frames[1]))/
                   (.00831446261815324*300.))
            if delta>1e-5:
                selected=(first.state_id,second.state_id,delta); break
        if selected is not None: break
    assert selected is not None
    state_ids=(selected[0],selected[1]); delta=selected[2]
    probability=math.exp(-delta)
    draw=probability*.5 if accept else (1.+probability)*.5
    monkeypatch.setattr(gibbs_sampling,'_random',lambda:draw)
    with ExitStack() as stack:
        workers=tuple(stack.enter_context(load_worker_run(prepared/'worker',
            read_json(prepared/'metadata.json')['worker_manifest_sha256'],trusted=True,integrator_seed=51+i))
            for i in range(2))
        for worker in workers:
            worker.evaluate(frames[1],bundle.schedule.states[-1].state_id)
        report=attempt_pair_exchange(workers,frames,state_ids,('walker-A','walker-B'))
        expected=[[independent(state_id,frame)/(.00831446261815324*300.) for frame in frames]
                  for state_id in state_ids]
        np.testing.assert_allclose(report['reduced_energies'],expected,atol=1e-8,rtol=0)
        assert report['exponent']==pytest.approx(delta,abs=1e-8)
        assert report['accepted'] is accept
        expected_states=state_ids[::-1] if accept else state_ids
        assert tuple(report['state_ids_after'])==tuple(expected_states)
        for index,worker in enumerate(workers):
            actual=worker.evaluate(frames[index],expected_states[index])
            assert report['energies_after_kj_mol'][index]==pytest.approx(
                actual.total.energy_kj_mol,abs=1e-8)
