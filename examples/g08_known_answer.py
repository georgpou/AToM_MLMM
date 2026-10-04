"""Bounded reproducible G08 harmonic MD; this is not a molecular binding run.

Activate the locked environment and set PYTHONPATH to the repository's src:
python examples/g08_known_answer.py --output /absolute/path/to/new-attempt
"""
import argparse
import json
from pathlib import Path


def sample_harmonic_md(seed, *, frames, stride, output):
    import numpy as np
    import openmm as mm
    from openmm import unit
    from atm_mlmm.analytic import seal_physical
    from atm_mlmm.atm import AtmEvaluator, build_atm, make_integrator, save_bundle
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import (AtomIdentity, EvaluationRecords, MobileGroup, MoleculeState,
                                 RestraintSpec, RuntimeSpec, Snapshot, TopologyView, to_json)
    from atm_mlmm.schedule import linear_schedule

    target = Path(output)
    target.mkdir(parents=True, exist_ok=False)  # immutable attempt, never overwrite
    topology = TopologyView((AtomIdentity('x', 'C', 'L', '1', '', 'C'),), (),
                            (MoleculeState('analytic-coordinate', ('x',), 'ligand', 0, 1),))
    system = mm.System()
    system.addParticle(12.)
    child = mm.CustomExternalForce('50*(x*x+y*y+z*z)')
    child.addParticle(0, [])
    child.setName('G08:analytic-physical-harmonic')
    system.addForce(child)
    physical = seal_physical(system, topology, ml_atom_ids=('x',), old_to_new=(0,),
                             manifest={'fixture_kind': 'G08-harmonic', 'periodicity': 'nonperiodic',
                                       'k_kj_mol_nm2': 100., 'mass_da': 12.})
    group = MobileGroup('mobile', ('x',), ('ligand',), 'analytic-coordinate')
    transfer = resolve_protocol(physical, make_protocol((group,), (.3, 0., 0.)))
    names = ('zero', 'q1', 'q2', 'q3', 'one')
    lambdas = np.linspace(0., 1., 5)
    schedule = linear_schedule(tuple(zip(names, lambdas)))
    restraint = RestraintSpec('outside-kr50', ('x',), 50., (0., 0., 0.))
    runtime = RuntimeSpec('Reference', 'double', (), .0005, 300., 'NVT')
    bundle = build_atm(physical, transfer, schedule, restraint)
    bundle_digest = save_bundle(target/'bundle.json', bundle)
    rng = np.random.default_rng(seed)
    positions, forces, raw, state_ids, sample_ids, walkers, steps = [], [], [], [], [], [], []
    rt = .00831446261815324*300.
    for j, (state_id, lam) in enumerate(zip(names, lambdas)):
        integrator = make_integrator(runtime)
        integrator.setRandomNumberSeed(seed+1009*j)
        with AtmEvaluator(bundle, runtime, integrator=integrator) as evaluator:
            initial = rng.normal(0., np.sqrt(rt/150.), (1, 3))
            initial[0, 0] -= lam*.2
            evaluator.evaluate(Snapshot(('x',), initial, None), state_id)
            evaluator.context.setVelocitiesToTemperature(300.*unit.kelvin, seed+1013*j)
            evaluator.integrator.step(10000)  # 5 ps, recorded explicitly
            for i in range(frames):
                evaluator.integrator.step(stride)
                observed = evaluator.context.getState(getPositions=True, getEnergy=True, getForces=True)
                xyz = np.asarray(observed.getPositions(asNumpy=True).value_in_unit(unit.nanometer))
                force = np.asarray(observed.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))
                u1, u0, expression = evaluator.atm_force.getPerturbationEnergy(evaluator.context)
                u0, u1 = (v.value_in_unit(unit.kilojoules_per_mole) for v in (u0, u1))
                outside = evaluator.context.getState(getEnergy=True, groups=evaluator.outside_groups).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                total = observed.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                positions.append(xyz)
                forces.append(force)
                raw.append((u0, u1, outside, total))
                sample_ids.append(f'seed-{seed}:{state_id}:{i}')
                state_ids.append(state_id)
                walkers.append(f'seed-{seed}:{state_id}')
                steps.append(10000+(i+1)*stride)
            # Re-enter the guarded shared evaluator at the end of each pilot.
            evaluator.evaluate(Snapshot(('x',), xyz, None), state_id)
    # Preserve complete observations before numerical/analysis admission.
    np.savez_compressed(target/'frames.npz', positions_nm=positions,
                        full_real_forces_kj_mol_nm=forces, raw_kj_mol=raw)
    records = EvaluationRecords(schedule, sample_ids, state_ids, walkers, steps,
                                 *(tuple(row[j] for row in raw) for j in range(4)),
                                 physical.content_identity, transfer.content_identity, restraint.content_identity,
                                 {'seed': str(seed), 'runtime_identity': runtime.content_identity,
                                  'bundle_sha256': bundle_digest, 'warmup_steps_per_state': '10000',
                                  'sample_stride_steps': str(stride), 'frames_per_state': str(frames),
                                  'profile': 'native-analytic OpenMM Reference double NVT'}, 'correlated')
    (target/'records.json').write_text(to_json(records)+'\n')
    xyz = np.array(positions)
    lam = np.repeat(lambdas, frames)
    expected_force = -150.*xyz
    expected_force[:, 0, 0] -= 30.*lam
    np.testing.assert_allclose(forces, expected_force, atol=1.e-7, rtol=0)
    return records


def main():
    from atm_mlmm.analysis import analyze
    from atm_mlmm.schema import ThermodynamicSpec, to_json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--frames', type=int, default=4000)
    parser.add_argument('--stride', type=int, default=200)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    spec = ThermodynamicSpec('restrained_free_energy', {'zero': -1., 'one': 1.}, 'endpoint_difference',
                             (('zero', 'q1'), ('q1', 'q2'), ('q2', 'q3'), ('q3', 'one')),
                             {'zero': 'u0+outside', 'one': 'u1+outside'}, (), (), None,
                             'Unbounded analytic Gaussian coordinates', 'Outside kr=50 harmonic',
                             'No orientation in this analytic coordinate test', 'One analytic state per endpoint')
    (args.output/'thermodynamics.json').write_text(to_json(spec)+'\n')
    results = []
    for seed in (41, 73, 109):
        records = sample_harmonic_md(seed, frames=args.frames, stride=args.stride, output=args.output/f'seed-{seed}')
        result = analyze(records, spec)
        (args.output/f'seed-{seed}'/'result.json').write_text(to_json(result)+'\n')
        passed = abs(result.restrained_kj_mol-1.5) <= .1 and abs(result.restrained_kj_mol-1.5) <= 3*result.restrained_standard_error_kj_mol
        results.append({'seed': seed, 'value_kj_mol': result.restrained_kj_mol,
                        'standard_error_kj_mol': result.restrained_standard_error_kj_mol,
                        'minimum_effective_contributions': min(result.diagnostics['effective_samples']),
                        'known_answer_passed': passed})
    (args.output/'summary.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps(results, indent=2))
    if not all(row['known_answer_passed'] for row in results):
        raise SystemExit('Known-answer sampling criterion failed; all attempts were preserved')


if __name__ == '__main__':
    main()
