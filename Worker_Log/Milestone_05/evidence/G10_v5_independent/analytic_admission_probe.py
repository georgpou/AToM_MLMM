"""Fresh independent analytic/full-force controls and resealed admission probes.

Characterization violations exit 1 after saving every result. No reviewed source
or test is edited, and no production probability/evaluation implementation is added.
"""
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import random
import shutil
import sys
from unittest.mock import patch

import numpy as np

ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = ROOT / 'Worker_Log/Milestone_05/evidence/G10_v5_independent'
ARTIFACTS = Path('/workspace/G10_v5_independent_artifacts')
sys.path.insert(0, str(ROOT))
from atm_mlmm import exchange as controller
from atm_mlmm import exchange_journal as journal
from atm_mlmm.adapters import atom
from atm_mlmm.persistence import read_json, write_json
from atm_mlmm.schema import Snapshot, from_json
from atm_mlmm.schedule import reduced_potentials
from tests.analytic_oracle import mapped_positions, nonlinear_answer, outside_answer, physical_answer
from tests.workflow.test_persistent_exchange import prepare_multistate


def snapshot(sample):
    return Snapshot(tuple(sample['real_atom_ids']), sample['positions_nm'],
                    sample['box_nm'], sample['velocities_nm_ps'])


def independent(sample, kind, parameters):
    # Hand-derived endpoint/outside derivatives, no production map/mixer callback.
    u0, f0 = physical_answer(mapped_positions(sample['positions_nm'], kind, 0), marker=20.)
    u1, f1 = physical_answer(mapped_positions(sample['positions_nm'], kind, 1), marker=20.)
    expression, weights, soft = nonlinear_answer(u0, u1, parameters)
    outside, fk = outside_answer(sample['positions_nm'])
    raw = dict(u0_raw_kJ_mol=u0, u1_raw_kJ_mol=u1, delta_u_raw_kJ_mol=u1-u0,
               delta_u_softcore_kJ_mol=soft, atm_expression_energy_kJ_mol=expression,
               outside_energy_kJ_mol=outside, system_total_energy_kJ_mol=expression+outside)
    return raw, fk + weights[0]*f0 + weights[1]*f1


def analytic_case(kind):
    prepared = prepare_multistate(ARTIFACTS / f'{kind}-prepared', kind=kind)
    run = ARTIFACTS / f'{kind}-prefix'
    summary = controller.run_multistate_exchange(prepared, run,
        state_ids=('first', 'middle', 'third'), state_pairs=((0, 1), (1, 2)),
        boundaries=2, steps_per_boundary=1, seed=73, trusted=True, stop_after_boundaries=1)
    rows = journal.read_multistate_boundaries(run)
    metadata = read_json(run / 'metadata.json')
    bundle = from_json((run / 'worker/bundle.json').read_text())
    samples = rows[0]['samples']
    expected_matrix = np.empty((3, 3))
    full_force_error = 0.
    raw_error = 0.
    for w, sample in enumerate(samples):
        for s, state in enumerate(bundle.schedule.states):
            raw, forces = independent(sample, kind, state.parameters)
            expected_matrix[s, w] = raw['system_total_energy_kJ_mol'] * metadata['beta_mol_per_kJ']
            if state.state_id == sample['state_id']:
                raw_error = max(raw_error, max(abs(raw[k]-sample['raw'][k]) for k in raw))
                full_force_error = max(full_force_error, float(np.max(np.abs(
                    forces - np.asarray(sample['real_forces_kj_mol_nm'])))))
    reconstructed = reduced_potentials(from_json((run / 'records.json').read_text()))
    reconstruction_error = float(np.max(np.abs(reconstructed - expected_matrix)))
    matrix_error = 0.
    exponent_error = 0.
    outside_count = 0
    for q in range(2):
        attempt = read_json(run / f'boundaries/000000/attempts/{q:04d}/attempt.json')
        evaluated = read_json(run / f'boundaries/000000/attempts/{q:04d}/evaluated.json')
        indices = [metadata['state_ids'].index(s) for s in attempt['state_ids']]
        expected = expected_matrix[np.ix_(indices, attempt['worker_indices'])]
        matrix_error = max(matrix_error, float(np.max(np.abs(expected - evaluated['reduced_energies']))))
        exponent = expected[0, 1]+expected[1, 0]-expected[0, 0]-expected[1, 1]
        exponent_error = max(exponent_error, abs(exponent-evaluated['exponent']))
        for state_raw in evaluated['raw_energies']:
            outside_count += sum(abs(raw['outside_energy_kJ_mol']) > 1e-10 for raw in state_raw)
    assert raw_error <= 1e-8 and full_force_error <= 1e-8
    assert max(reconstruction_error, matrix_error, exponent_error) <= 1e-8
    assert outside_count == 8 and summary['binding_result'] == 'not_evaluated'
    return {'kind': kind, 'run': str(run), 'samples': 3, 'attempts': 2,
            'raw_max_abs_error_kJ_mol': raw_error, 'all_real_force_max_abs_error_kJ_mol_nm': full_force_error,
            'reduced_matrix_max_abs_error': matrix_error, 'exponent_max_abs_error': exponent_error,
            'raw_reconstruction_max_abs_error': reconstruction_error, 'nonzero_outside_entries': outside_count,
            'initial_start_permutation': rows[0]['walker_to_state_start'],
            'final_permutation': rows[0]['walker_to_state_final'], 'status': 'PASS'}


class LoadObserved(RuntimeError):
    pass


def reseal_metadata(run, metadata):
    write_json(run / 'metadata.json', metadata)
    (run / 'metadata.sha256').write_text(journal.sha(run / 'metadata.json') + '\n')


def challenge(name, change):
    run = ARTIFACTS / f'admission-{name}'
    shutil.copytree(ARTIFACTS / 'rbfe-prefix', run)
    metadata = read_json(run / 'metadata.json')
    boundary = run / 'boundaries/000000'
    change(run, metadata, boundary)
    reseal_metadata(run, metadata)
    journal.seal_tree(boundary, index=0)
    reader_error = None
    try:
        rows = journal.read_multistate_boundaries(run)
        reader_admitted = len(rows) == 1
    except Exception as error:
        reader_admitted = False
        reader_error = f'{type(error).__name__}: {error}'
    loaded = []
    def forbidden(*args, **kwargs):
        loaded.append(kwargs.get('integrator_seed'))
        raise LoadObserved('trusted worker loader reached')
    resume_error = None
    with patch.object(atom, 'load_worker_run', forbidden):
        try:
            controller.resume_multistate_exchange(run, trusted=True)
        except Exception as error:
            resume_error = f'{type(error).__name__}: {error}'
    status = 'VIOLATION' if reader_admitted or loaded else 'PASS'
    return {'name': name, 'expected': 'inert rejection before trusted worker loading',
            'reader_admitted': reader_admitted, 'reader_error': reader_error,
            'loader_calls': loaded, 'resume_error': resume_error, 'status': status,
            'metadata_sha256': journal.sha(run / 'metadata.json'),
            'boundary_manifest_sha256': journal.sha(boundary / 'manifest.json')}


def edit_json(path, edit):
    document = read_json(path)
    edit(document)
    write_json(path, document)


def stationary_composition():
    permutations = list(itertools.permutations(range(3)))
    q = [[Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)],
         [Fraction(1, 7), Fraction(1, 2), Fraction(1, 3)],
         [Fraction(1, 3), Fraction(1, 5), Fraction(1, 2)]]
    weights = [math.prod(q[w][p[w]] for w in range(3)) for p in permutations]
    target = [x / sum(weights) for x in weights]
    kernels = []
    for left, right in ((0, 1), (1, 2)):
        kernel = [[Fraction(0) for _ in permutations] for _ in permutations]
        for i, p in enumerate(permutations):
            after = list(p)
            a, b = p.index(left), p.index(right)
            after[a], after[b] = after[b], after[a]
            j = permutations.index(tuple(after))
            probability = min(Fraction(1), weights[j]/weights[i])
            kernel[i][j] = probability
            kernel[i][i] = 1-probability
        assert all(target[i]*kernel[i][j] == target[j]*kernel[j][i]
                   for i in range(6) for j in range(6))
        kernels.append(kernel)
    composition = [[sum(kernels[0][i][k]*kernels[1][k][j] for k in range(6))
                    for j in range(6)] for i in range(6)]
    assert all(sum(target[i]*composition[i][j] for i in range(6)) == target[j] for j in range(6))
    nonreversible = sum(target[i]*composition[i][j] != target[j]*composition[j][i]
                        for i in range(6) for j in range(6))
    assert nonreversible > 0
    py, nu = random.Random(31), np.random.RandomState(33)
    py.gauss(0., 1.); nu.normal()
    restored_py, restored_nu = controller._rng_from_document(json.loads(json.dumps(controller._rng_document(py, nu))))
    assert py.gauss(0., 1.) == restored_py.gauss(0., 1.)
    assert nu.normal() == restored_nu.normal()
    assert [(py.choice(range(3)), nu.random_sample()) for _ in range(9)] == [
        (restored_py.choice(range(3)), restored_nu.random_sample()) for _ in range(9)]
    return {'stationarity': 'exact Fraction equality on six permutations',
            'whole_composition_detailed_balance_violations': nonreversible,
            'both_rng_cache_and_draw_roundtrip': 'PASS', 'status': 'PASS'}


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    result = {'analytic_controls': [analytic_case(k) for k in ('abfe', 'rbfe')],
              'mathematical_control': stationary_composition(), 'challenges': []}
    probes = [
        ('steps-at-api-exclusive-limit', lambda r, m, b: m.update(steps_per_boundary=1000000)),
        ('worker-seed-overflows-later-walkers', lambda r, m, b: m.update(integrator_seed_base=2**31-1)),
        ('host-seed-boolean', lambda r, m, b: m.update(host_rng_seed=True)),
        ('python-gaussian-cache-string', lambda r, m, b: edit_json(b/'rng.json', lambda d: d['python'].__setitem__(2, 'invalid-cache'))),
        ('inverse-index-boolean', lambda r, m, b: edit_json(b/'walker-to-state.json', lambda d: d['state_to_walker'].__setitem__(d['state_to_walker'].index(1), True))),
        ('sample-sequence-boolean', lambda r, m, b: edit_json(b/'samples/worker-000.json', lambda d: d.update(sequence_number=True))),
        ('refreshed-energy-arithmetic', lambda r, m, b: edit_json(b/'attempts/0000/refreshed.json', lambda d: d['energies_after_kj_mol'].__setitem__(0, d['energies_after_kj_mol'][0]+123.))),
        ('nonfinite-force-control', lambda r, m, b: edit_json(b/'samples/worker-000.json', lambda d: d['real_forces_kj_mol_nm'][0].__setitem__(0, 'nan'))),
        ('invalid-permutation-control', lambda r, m, b: edit_json(b/'walker-to-state.json', lambda d: d.update(walker_to_state=[0,0,2]))),
    ]
    for name, change in probes:
        row = challenge(name, change)
        result['challenges'].append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    result['violation_count'] = sum(r['status'] == 'VIOLATION' for r in result['challenges'])
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    result['exit_status'] = 1 if result['violation_count'] else 0
    (HERE/'analytic-admission-results.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'analytic_cases': 2, 'challenges': len(result['challenges']),
                      'violation_count': result['violation_count'], 'exit_status': result['exit_status'],
                      'finished_utc': result['finished_utc']}, sort_keys=True))
    return result['exit_status']


if __name__ == '__main__':
    sys.exit(main())
