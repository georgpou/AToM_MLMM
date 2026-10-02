from dataclasses import replace
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.analytic_oracle import (REFERENCE, case, check, expected_linear, mapped_positions,
                                   nonlinear_answer, outside_answer, physical_answer,
                                   production_parameters)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('state_id,lam', (('initial', 0.), ('middle', .37), ('final', 1.)))
def test_linear_endpoint_and_force_identity(kind, state_id, lam):
    from atm_mlmm.atm import build_atm, evaluate_atm, evaluate_physical
    physical, transfer, schedule, restraints, snapshot = case(kind)
    expected = expected_linear(snapshot, kind, lam)
    for endpoint in (0, 1):
        direct_snapshot = replace(snapshot, positions_nm=mapped_positions(snapshot.positions_nm, kind, endpoint))
        direct = evaluate_physical(physical, direct_snapshot, REFERENCE)
        energy, forces = physical_answer(direct_snapshot.positions_nm)
        assert direct.energy_kj_mol == pytest.approx(energy, abs=1e-8, rel=0)
        np.testing.assert_allclose(direct.forces_kj_mol_nm, forces, atol=1e-7, rtol=0)
    check(evaluate_atm(build_atm(physical, transfer, schedule, restraints), snapshot, state_id, REFERENCE), expected)


def test_permuted_subset_and_units():
    from atm_mlmm.atm import evaluate_physical
    physical, _, _, _, snapshot = case(environment=False)
    result = evaluate_physical(physical, snapshot, REFERENCE)
    energy, force = physical_answer(snapshot.positions_nm, environment=False)
    assert result.energy_kj_mol == pytest.approx(energy, abs=1e-8, rel=0)
    np.testing.assert_allclose(result.forces_kj_mol_nm, force, atol=1e-7, rtol=0)
    # Different stiffness/centres make the [2,0] scatter independently visible.
    np.testing.assert_allclose(result.forces_kj_mol_nm[2], (-1.8, -2.4, .6), atol=1e-7, rtol=0)
    np.testing.assert_allclose(result.forces_kj_mol_nm[0], (-5.6, 1.4, 1.4), atol=1e-7, rtol=0)
    assert result.units.forces == 'kJ/mol/nm'
    assert not np.allclose(np.asarray(result.forces_kj_mol_nm)*10., force, atol=1e-7, rtol=0)


def test_nonzero_outside_term_and_tuple_order():
    from atm_mlmm.atm import AtmEvaluator, build_atm
    physical, transfer, schedule, restraints, snapshot = case()
    with AtmEvaluator(build_atm(physical, transfer, schedule, restraints), REFERENCE) as evaluator:
        result = evaluator.evaluate(snapshot, 'middle')
        u1, u0, expression = evaluator.atm_force.getPerturbationEnergy(evaluator.context)
        from openmm import unit
        assert u1.value_in_unit(unit.kilojoules_per_mole) == result.raw.u1_raw_kJ_mol
        assert u0.value_in_unit(unit.kilojoules_per_mole) == result.raw.u0_raw_kJ_mol
        assert expression.value_in_unit(unit.kilojoules_per_mole) == result.raw.atm_expression_energy_kJ_mol
    expected = expected_linear(snapshot, 'abfe', .37)
    check(result, expected)
    assert expected[0] != expected[1]
    assert result.raw.outside_energy_kJ_mol > .1
    assert result.total.energy_kj_mol == pytest.approx(expected[2]+expected[3], abs=1e-8, rel=0)


def test_independent_harmonic_forces():
    from atm_mlmm.atm import build_atm, evaluate_atm
    physical, transfer, schedule, restraints, snapshot = case(environment=False)
    check(evaluate_atm(build_atm(physical, transfer, schedule, restraints), snapshot, 'middle', REFERENCE),
          expected_linear(snapshot, 'abfe', .37, environment=False))


@pytest.mark.parametrize('direction', (1., -1.))
@pytest.mark.parametrize('target', (.99, 1., 1.01, 2., 8.))
def test_nonlinear_mixing_force_chain_rule(direction, target):
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.derivatives import finite_difference_forces
    from atm_mlmm.schedule import production_schedule
    physical, transfer, _, restraints, snapshot = case('rbfe')
    u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 0))
    u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 1))
    p = production_parameters(Direction=direction, UOffset=u1-u0-direction*target)
    expression, weights, soft = nonlinear_answer(u0, u1, p)
    outside, fk = outside_answer(snapshot.positions_nm)
    expected_force = weights[0]*f0+weights[1]*f1+fk
    schedule = production_schedule((('transition', p),))
    with AtmEvaluator(build_atm(physical, transfer, schedule, restraints), REFERENCE) as evaluator:
        result = evaluator.evaluate(snapshot, 'transition')
        check(result, (u0, u1, expression, outside, expected_force))
        assert result.raw.delta_u_softcore_kJ_mol == pytest.approx(soft, abs=1e-8, rel=0)
        errors = []
        for h in (1e-3, 1e-4, 1e-5):
            fd = finite_difference_forces(lambda s: evaluator.evaluate(s, 'transition').total.energy_kj_mol, snapshot, h)
            errors.append(float(np.max(np.abs(fd-expected_force))))
        assert errors[-1] <= 1e-5, errors
        assert errors[-1] <= errors[0]+1e-8, errors
    # Nonlinear weights are not the generic linear lambda weights.
    assert abs(weights[1]-.37) > 1e-3


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_fresh_process_serialization_offline(tmp_path, kind):
    from atm_mlmm.atm import build_atm, save_bundle, load_bundle
    from atm_mlmm.schema import IdentityError, UnsupportedCapability
    physical, transfer, schedule, restraints, snapshot = case(kind)
    target = tmp_path/'trusted.json'
    digest = save_bundle(target, build_atm(physical, transfer, schedule, restraints))
    assert digest == hashlib.sha256(target.read_bytes()).hexdigest()
    with pytest.raises(UnsupportedCapability, match='trusted'):
        load_bundle(target, digest)
    with pytest.raises(IdentityError, match='digest'):
        load_bundle(target, '0'*64, trusted=True)
    code = '''
import socket, sys
def deny(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket.connect = deny
socket.create_connection = deny
socket.getaddrinfo = deny
from atm_mlmm.atm import load_bundle, evaluate_atm
from tests.analytic_oracle import case, check, expected_linear, REFERENCE
bundle = load_bundle(sys.argv[1], sys.argv[2], trusted=True)
snapshot = case(sys.argv[3])[-1]
check(evaluate_atm(bundle, snapshot, 'middle', REFERENCE), expected_linear(snapshot, sys.argv[3], .37))
print('fresh offline reload: passed')
'''
    root = Path(__file__).resolve().parents[2]
    run = subprocess.run([sys.executable, '-c', code, str(target), digest, kind],
                         env=dict(os.environ, PYTHONPATH=str(root/'src')+os.pathsep+str(root),
                                  XDG_CACHE_HOME=str(tmp_path/'empty-cache')),
                         text=True, capture_output=True, timeout=60)
    assert run.returncode == 0, run.stdout+run.stderr
    assert 'fresh offline reload: passed' in run.stdout


@pytest.mark.parametrize('changes', ({'Alpha': 0.}, {'Direction': 0.}, {'Umax': 1.},
                                  {'Acore': -.1}, {'Lambda1': float('nan')}, {'unknown': 1.}))
def test_invalid_production_parameter_domains(changes):
    from atm_mlmm.schedule import production_schedule
    from atm_mlmm.schema import MalformedInput, UnsupportedCapability
    with pytest.raises((MalformedInput, UnsupportedCapability)):
        production_schedule((('bad', production_parameters(**changes)),))


@pytest.mark.parametrize('lam', (0., .37, 1.))
@pytest.mark.parametrize('direction', (1., -1.))
def test_production_linear_limits_and_offsets(lam, direction):
    from atm_mlmm.atm import build_atm, evaluate_atm
    from atm_mlmm.schedule import production_schedule
    physical, transfer, _, restraints, snapshot = case('rbfe')
    u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 0))
    u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 1))
    parameters = production_parameters(Lambda1=lam, Lambda2=lam, Alpha=0., Acore=0., Direction=direction,
                                       UOffset=.8, W0=.6)
    expression, weights, soft = nonlinear_answer(u0, u1, parameters)
    outside, fk = outside_answer(snapshot.positions_nm)
    schedule = production_schedule((('limit', parameters),))
    result = evaluate_atm(build_atm(physical, transfer, schedule, restraints), snapshot, 'limit', REFERENCE)
    check(result, (u0, u1, expression, outside, weights[0]*f0+weights[1]*f1+fk))
    assert result.raw.delta_u_softcore_kJ_mol == pytest.approx(soft, abs=1e-8, rel=0)
