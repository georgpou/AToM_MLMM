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
