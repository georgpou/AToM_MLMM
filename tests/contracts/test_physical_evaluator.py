from dataclasses import replace
import numpy as np
import pytest

from tests.analytic_oracle import REFERENCE, case, check, expected_linear, physical_answer


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_environment_force_and_recomputed_mapping(kind):
    from atm_mlmm.atm import build_atm, evaluate_atm, evaluate_physical
    physical, transfer, schedule, restraints, snapshot = case(kind)
    # Isolate the numerical S04 example by subtracting the independently
    # derived local spring contribution, never by calling its callback.
    positions = np.array(snapshot.positions_nm)
    positions[2] = (.2, 0., 0.)
    positions[1] = (.5, 0., 0.)
    a = replace(snapshot, positions_nm=positions)
    result = evaluate_physical(physical, a, REFERENCE)
    local_energy, local_force = physical_answer(positions, environment=False)
    assert result.energy_kj_mol-local_energy == pytest.approx(.45, abs=1e-8, rel=0)
    np.testing.assert_allclose(np.asarray(result.forces_kj_mol_nm)-local_force,
                               [[0,0,0],[-3,0,0],[3,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]], atol=1e-7, rtol=0)
    positions[1,0] = .6
    b = replace(snapshot, positions_nm=positions)
    moved = evaluate_physical(physical, b, REFERENCE)
    local_energy, local_force = physical_answer(positions, environment=False)
    assert moved.energy_kj_mol-local_energy == pytest.approx(.80, abs=1e-8, rel=0)
    assert moved.forces_kj_mol_nm[1][0] == pytest.approx(-4., abs=1e-7, rel=0)
    alchemical = build_atm(physical, transfer, schedule, restraints)
    result = evaluate_atm(alchemical, a, 'middle', REFERENCE)
    check(result, expected_linear(a, kind, .37))
    assert not np.allclose(result.total.forces_kj_mol_nm[1],
                           evaluate_atm(alchemical, a, 'initial', REFERENCE).total.forces_kj_mol_nm[1], atol=1e-7, rtol=0)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_evaluation_history_independence(kind):
    from atm_mlmm.atm import AtmEvaluator, PhysicalEvaluator, build_atm
    physical, transfer, schedule, restraints, a = case(kind)
    positions = np.array(a.positions_nm)
    positions[1] += (.17, -.11, .09)
    b = replace(a, positions_nm=positions)
    for evaluator in (PhysicalEvaluator(physical, REFERENCE),
                      AtmEvaluator(build_atm(physical, transfer, schedule, restraints), REFERENCE)):
        with evaluator:
            evaluate = (lambda s: evaluator.evaluate(s, 'middle')) if isinstance(evaluator, AtmEvaluator) else evaluator.evaluate
            first, middle, last = evaluate(a), evaluate(b), evaluate(a)
            assert first == last
            assert first != middle


def test_force_order_box_and_runtime_rejection():
    from atm_mlmm.atm import evaluate_physical
    from atm_mlmm.schema import IdentityError, UnsupportedCapability
    physical, _, _, _, snapshot = case()
    with pytest.raises(IdentityError, match='order'):
        evaluate_physical(physical, replace(snapshot, real_atom_ids=tuple(reversed(snapshot.real_atom_ids))), REFERENCE)
    with pytest.raises(UnsupportedCapability, match='periodic'):
        evaluate_physical(physical, replace(snapshot, box_nm=((2.,0,0),(0,2.,0),(0,0,2.))), REFERENCE)
    for runtime in (replace(REFERENCE, timestep_ps=.001), replace(REFERENCE, platform='CUDA'),
                    replace(REFERENCE, precision='single'), replace(REFERENCE, ensemble='NPT')):
        with pytest.raises(UnsupportedCapability):
            evaluate_physical(physical, snapshot, runtime)
