import copy
from dataclasses import replace
import hashlib
import logging
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import openmm as mm
import pytest

from tests.analytic_oracle import (REFERENCE, case, check, mapped_positions, nonlinear_answer,
                                   outside_answer, physical_answer, production_parameters)


def atom_case(kind='abfe', **kwargs):
    from atm_mlmm.schedule import production_schedule
    physical, transfer, _, restraints, snapshot = case(kind, **kwargs)
    schedule = production_schedule((('first', production_parameters()),
                                    ('second', production_parameters(Lambda1=.3, Lambda2=.7, W0=.9, Direction=-1.))))
    return physical, transfer, schedule, restraints, snapshot


def replace_system(bundle, system):
    from atm_mlmm.schema import ForceRecord
    xml = mm.XmlSerializer.serialize(system)
    ledger = tuple(ForceRecord(i, type(f).__name__, f.getName(), f.getForceGroup(),
                               f.usesPeriodicBoundaryConditions(),
                               {'force_sha256': hashlib.sha256(mm.XmlSerializer.serialize(f).encode()).hexdigest()})
                   for i, f in enumerate(system.getForces()))
    return replace(bundle, system_xml=xml, system_sha256=hashlib.sha256(xml.encode()).hexdigest(), ledger=ledger)


def test_pythonforce_explicit_group_route():
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import outside_force
    from atm_mlmm.routing import export_physical, validate_routing
    from atom_openmm.ommsystem import OMMSystemABFE
    physical, transfer, schedule, restraints, snapshot = atom_case()
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
        report = validate_routing(run.upstream.system, physical, restraints)
        physical_rows = [r for r in report if r.disposition == 'physical_child']
        assert len(physical_rows) == len(physical.ledger)
        assert all(r.class_name == 'PythonForce' for r in physical_rows)
        assert len({r.force_id for r in physical_rows}) == len(physical.ledger)
        assert all(len(r.path) == 2 for r in physical_rows)
        assert all(not isinstance(f, mm.PythonForce) for f in run.upstream.system.getForces())
        assert run.keywords['VARIABLE_FORCE_GROUP'] == 1
        # Reproduce the real pinned upstream default selection with the same
        # honestly named forces. It selects no PythonForce and leaves originals.
        defaults = dict(run.keywords)
        defaults.pop('VARIABLE_FORCE_GROUP')
        stock = OMMSystemABFE('default-route', defaults, None, None, logging.getLogger('m02-default-route'))
        stock.system = export_physical(physical).system
        stock.system.addForce(outside_force(physical, restraints))
        stock.topology = run.upstream.topology
        stock.set_ligand_atoms()
        stock.set_displacement()
        stock.set_atmforce()
        assert stock.atmforce.getNumForces() == 0
        assert sum(isinstance(f, mm.PythonForce) for f in stock.system.getForces()) == len(physical.ledger)
        from atm_mlmm.schema import IdentityError
        with pytest.raises(IdentityError, match='ownership|physical|child'):
            validate_routing(stock.system, physical, restraints)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('environment', (False, True))
@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_both_protocols_match_native_oracle(kind, environment, platform):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import build_atm, evaluate_atm
    physical, transfer, schedule, restraints, snapshot = atom_case(kind, environment=environment)
    runtime = replace(REFERENCE, platform=platform)
    native = build_atm(physical, transfer, schedule, restraints)
    with build_atom(physical, transfer, schedule, restraints, runtime) as run:
        for state in schedule.states:
            actual = run.evaluate(snapshot, state.state_id)
            baseline = evaluate_atm(native, snapshot, state.state_id, runtime)
            assert actual.raw == baseline.raw
            np.testing.assert_allclose(actual.total.forces_kj_mol_nm, baseline.total.forces_kj_mol_nm, atol=1e-7, rtol=0)
            u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 0), environment=environment)
            u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 1), environment=environment)
            expression, weights, soft = nonlinear_answer(u0, u1, state.parameters)
            outside, fk = outside_answer(snapshot.positions_nm)
            check(actual, (u0, u1, expression, outside, weights[0]*f0+weights[1]*f1+fk))
            assert actual.parameters == state.parameters


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_upstream_unit_and_key_conversion(kind):
    from atm_mlmm.adapters.atom import atom_keywords, build_atom
    physical, transfer, schedule, restraints, snapshot = atom_case(kind, old_to_new=(6,2,4,0,5,1,3))
    keywords = atom_keywords(physical, transfer, schedule, REFERENCE)
    assert keywords['TIME_STEP'] == .0005
    assert keywords['INTEGRATOR'] == 'langevinmiddle'
    np.testing.assert_array_equal(keywords['DISPLACEMENT'], [1., -2., 3.])
    assert keywords['UMAX'] == pytest.approx(10./4.184, abs=1e-14, rel=0)
    if kind == 'abfe':
        assert keywords['LIGAND_ATOMS'] == [4, 6]
        assert 'LIGAND1_ATOMS' not in keywords and 'LIGAND2_ATOMS' not in keywords
    else:
        assert keywords['LIGAND1_ATOMS'] == [4, 6]
        assert keywords['LIGAND2_ATOMS'] == [0, 3, 1]
        assert 'LIGAND_ATOMS' not in keywords
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
        result = run.evaluate(snapshot, 'first')
        u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 0))
        u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, kind, 1))
        expression, weights, _ = nonlinear_answer(u0, u1, schedule.states[0].parameters)
        outside, fk = outside_answer(snapshot.positions_nm)
        check(result, (u0, u1, expression, outside, weights[0]*f0+weights[1]*f1+fk))


@pytest.mark.parametrize('fault', ('occupied', 'nested-root', 'nested-cv', 'duplicated-input', 'left-outside'))
def test_duplicate_and_nested_atm_rejected(fault):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import physical_system
    from atm_mlmm.routing import export_physical, validate_routing
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, _ = atom_case()
    if fault == 'left-outside':
        with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
            run.upstream.system.addForce(copy.copy(run.upstream.atmforce.getForce(0)))
            with pytest.raises(IdentityError, match='duplicate|outside|ownership'):
                validate_routing(run.upstream.system, physical, restraints)
        return
    system = physical_system(physical)
    if fault == 'occupied':
        system.getForce(0).setForceGroup(1)
    elif fault == 'duplicated-input':
        system.addForce(copy.copy(system.getForce(0)))
    else:
        nested = mm.ATMForce('u0')
        for _ in range(7):
            nested.addParticle(mm.Vec3(0,0,0))
        nested.addForce(copy.copy(system.getForce(0)))
        if fault == 'nested-cv':
            container = mm.CustomCVForce('child')
            container.addCollectiveVariable('child', nested)
            nested = container
        system.addForce(nested)
    with pytest.raises(IdentityError, match='occupied|nested|ATM|duplicate'):
        export_physical(replace_system(physical, system))


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_fixed_map_guard_after_construction(tmp_path, kind, platform):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import AtmEvaluator, build_atm, load_bundle, save_bundle
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, snapshot = atom_case(kind)
    runtime = replace(REFERENCE, platform=platform)
    native = build_atm(physical, transfer, schedule, restraints)
    with build_atom(physical, transfer, schedule, restraints, runtime) as run:
        run.evaluate(snapshot, 'first')
        run.set_state('second')
        run.evaluator._check_maps()
        state_path, digest = run.save_initial_state(tmp_path, snapshot, 'first')
        assert state_path.name == 'analytic_0.xml'
        run.set_state('second')
        run.load_initial_state(state_path, digest, 'second')
        np.testing.assert_array_equal(run.evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(mm.unit.nanometer), snapshot.positions_nm)
        assert dict(run.evaluator.context.getParameters())['Lambda1'] == .3
        assert run.evaluate(snapshot, 'second').parameters == schedule.states[1].parameters
        # Reload the exact upstream-constructed artifact in a new evaluator.
        target = tmp_path/'upstream.json'
        bundle_digest = save_bundle(target, run.bundle)
        reloaded = load_bundle(target, bundle_digest, trusted=True)
        with AtmEvaluator(reloaded, runtime) as fresh:
            fresh.evaluate(snapshot, 'second')
            fresh._check_maps()
        run.evaluator.context.setParameter('Lambda1', .123)
        with pytest.raises(IdentityError, match='parameter'):
            run.evaluate(snapshot, 'first')
    with AtmEvaluator(native, runtime) as evaluator:
        evaluator.evaluate(snapshot, 'first')
        evaluator.atm_force.setParticleParameters(1, mm.Vec3(.1,0,0), mm.Vec3(0,0,0))
        with pytest.raises(IdentityError, match='map|mutation'):
            evaluator.evaluate(snapshot, 'first')
    with build_atom(physical, transfer, schedule, restraints, runtime) as run:
        run.upstream.atmforce.setParticleParameters(4, mm.Vec3(.2,0,0), mm.Vec3(0,0,0))
        with pytest.raises(IdentityError, match='map|mutation'):
            run.evaluate(snapshot, 'first')


def test_upstream_state_updates_reuse_worker_and_reject_bad_handover(tmp_path):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, snapshot = atom_case('rbfe')
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
        run.set_state('second')
        assert run.worker.par['lambda1'] == .3
        assert run.worker.par['uh'].value_in_unit(mm.unit.kilojoules_per_mole) == 2.
        path, digest = run.save_initial_state(tmp_path, snapshot, 'first')
        path.write_text(path.read_text()+' ')
        with pytest.raises(IdentityError, match='digest'):
            run.load_initial_state(path, digest, 'second')


def test_loaded_routing_report_is_verified_before_context():
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, _ = atom_case()
    correct = build_atm(physical, transfer, schedule, restraints)
    bogus = replace(correct, routing_report=(replace(correct.routing_report[0], force_group=17),)+correct.routing_report[1:])
    with pytest.raises(IdentityError, match='routing|ownership'):
        with AtmEvaluator(bogus, REFERENCE):
            pass


def test_femtosecond_conversion_at_upstream_boundary():
    from atm_mlmm.adapters.atom import timestep_fs_to_ps
    from atm_mlmm.schema import MalformedInput
    assert timestep_fs_to_ps(.5) == .0005
    assert timestep_fs_to_ps(.1) == .0001
    for value in (float('nan'), float('inf'), 0., -.5, True):
        with pytest.raises(MalformedInput):
            timestep_fs_to_ps(value)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_upstream_artifact_fresh_offline_reload(tmp_path, kind):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import save_bundle
    physical, transfer, schedule, restraints, snapshot = atom_case(kind)
    target = tmp_path/'upstream.json'
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
        digest = save_bundle(target, run.bundle)
    code = '''
import socket, sys
def deny(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket.connect = deny
socket.create_connection = deny
socket.getaddrinfo = deny
from atm_mlmm.atm import load_bundle, AtmEvaluator, build_atm, evaluate_atm
from tests.analytic_oracle import REFERENCE
from tests.workflow.test_atom_force_routing import atom_case
import numpy as np
p,t,s,r,x = atom_case(sys.argv[3])
reference = evaluate_atm(build_atm(p,t,s,r), x, 'second', REFERENCE)
bundle = load_bundle(sys.argv[1], sys.argv[2], trusted=True)
with AtmEvaluator(bundle, REFERENCE) as evaluator:
    actual = evaluator.evaluate(x, 'second')
    assert actual.raw == reference.raw
    assert actual.parameters == reference.parameters
    np.testing.assert_allclose(actual.total.forces_kj_mol_nm, reference.total.forces_kj_mol_nm, atol=1e-7, rtol=0)
    evaluator._check_maps()
print('fresh upstream artifact reload: passed')
'''
    root = Path(__file__).resolve().parents[2]
    run = subprocess.run([sys.executable, '-c', code, str(target), digest, kind],
                         env=dict(os.environ, PYTHONPATH=str(root/'src')+os.pathsep+str(root),
                                  XDG_CACHE_HOME=str(tmp_path/'empty-cache')), text=True, capture_output=True, timeout=60)
    assert run.returncode == 0, run.stdout+run.stderr
    assert 'fresh upstream artifact reload: passed' in run.stdout
