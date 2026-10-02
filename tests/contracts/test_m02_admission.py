"""Scientific admission regressions for independent findings M02-R1/R2/R3."""
import copy
from dataclasses import replace

import numpy as np
import openmm as mm
import pytest

from atm_mlmm.adapters.atom import build_atom
from atm_mlmm.analytic import seal_physical
from atm_mlmm.atm import (AtmEvaluator, PhysicalEvaluator, build_atm, physical_system,
                         seal_alchemical, xml_digest)
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.prepare import build_preparation
from atm_mlmm.routing import export_physical, validate_routing
from atm_mlmm.schedule import linear_schedule, production_schedule
from atm_mlmm.schema import IdentityError
from tests.analytic_oracle import (REFERENCE, check, mapped_positions, nonlinear_answer,
                                   outside_answer, physical_answer, production_parameters)
from tests.workflow.test_atom_force_routing import atom_case


def reseal_physical(physical, system):
    return seal_physical(system, physical.topology, ml_atom_ids=physical.ml_atom_ids,
                         old_to_new=physical.old_to_new, manifest=physical.manifest)


def holder(stage, physical, transfer, schedule, restraints, runtime=REFERENCE):
    if stage == 'physical':
        return PhysicalEvaluator(physical, runtime)
    if stage == 'preparation':
        return build_preparation(physical, runtime)
    if stage == 'native':
        return AtmEvaluator(build_atm(physical, transfer, schedule, restraints), runtime)
    return build_atom(physical, transfer, schedule, restraints, runtime)


def evaluator_of(run):
    return run.evaluator if hasattr(run, 'evaluator') else run


def global_case(kind='rbfe', *, name='physical_k', value=2., **kwargs):
    physical, transfer, schedule, restraints, snapshot = atom_case(kind, **kwargs)
    system = physical_system(physical)
    force = mm.CustomExternalForce('.5*'+name+'*(x*x+y*y+z*z)')
    force.addGlobalParameter(name, value)
    force.addParticle(physical.real_to_final['a1'], [])
    force.setName('regression:fixed-global')
    system.addForce(force)
    physical = reseal_physical(physical, system)
    return physical, resolve_protocol(physical, transfer.protocol), schedule, restraints, snapshot


def admit_system(bundle, system, admission):
    if admission == 'sealer':
        return seal_alchemical(system, bundle.physical, bundle.transfer, bundle.schedule,
                               bundle.restraints, construction=bundle.construction)
    # Correctly hash forged trusted bytes, bypassing the sealer deliberately.
    xml = mm.XmlSerializer.serialize(system)
    altered = replace(bundle, system_xml=xml, system_sha256=xml_digest(xml))
    with AtmEvaluator(altered, REFERENCE):
        return altered


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('stage', ('native', 'upstream'))
@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
def test_actual_expression_must_match_schedule(kind, stage, admission):
    physical, transfer, schedule, restraints, _ = atom_case(kind)
    with holder(stage, physical, transfer, schedule, restraints) as run:
        bundle = run.bundle
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    atm.setEnergyFunction('u0')
    with pytest.raises(IdentityError, match='expression|schedule'):
        admit_system(bundle, system, admission)


@pytest.mark.parametrize('stage', ('native', 'upstream'))
@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
@pytest.mark.parametrize('name', ('Lambda1', 'UOffset'))
def test_atm_itself_must_own_required_schedule_globals(stage, admission, name):
    physical, transfer, schedule, restraints, _ = atom_case()
    with holder(stage, physical, transfer, schedule, restraints) as run:
        bundle = run.bundle
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    index = next(i for i in range(atm.getNumGlobalParameters()) if atm.getGlobalParameterName(i) == name)
    atm.setGlobalParameterName(index, 'unowned_parameter')
    with pytest.raises(IdentityError, match='parameter|global|schedule'):
        admit_system(bundle, system, admission)


@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
@pytest.mark.parametrize('fault', ('expression', 'global'))
def test_linear_schedule_expression_and_globals_are_bound(admission, fault):
    physical, transfer, _, restraints, _ = atom_case()
    schedule = linear_schedule((('first', 0.), ('second', .37)))
    bundle = build_atm(physical, transfer, schedule, restraints)
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    if fault == 'expression':
        atm.setEnergyFunction('u0')
    else:
        atm.setGlobalParameterName(0, 'unowned_parameter')
    with pytest.raises(IdentityError, match='expression|parameter|global|schedule'):
        admit_system(bundle, system, admission)


@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
def test_required_atm_global_cannot_have_ambiguous_duplicate_ownership(admission):
    physical, transfer, schedule, restraints, _ = atom_case()
    bundle = build_atm(physical, transfer, schedule, restraints)
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    atm.addGlobalParameter('Lambda1', schedule.states[0].parameters['Lambda1'])
    with pytest.raises(IdentityError, match='parameter|global|schedule'):
        admit_system(bundle, system, admission)


@pytest.mark.parametrize('stage', ('native', 'upstream'))
def test_harmless_expression_whitespace_preserves_numerics(stage):
    physical, transfer, schedule, restraints, snapshot = atom_case('rbfe')
    with holder(stage, physical, transfer, schedule, restraints) as run:
        bundle = run.bundle
        expected = evaluator_of(run).evaluate(snapshot, 'second')
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    atm.setEnergyFunction('\n'+atm.getEnergyFunction().replace(';', ';\n')+'\n')
    admitted = admit_system(bundle, system, 'sealer')
    with AtmEvaluator(admitted, REFERENCE) as evaluator:
        assert evaluator.evaluate(snapshot, 'second') == expected


@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
def test_whitespace_cannot_join_different_expression_tokens(admission):
    physical, transfer, schedule, restraints, _ = atom_case()
    bundle = build_atm(physical, transfer, schedule, restraints)
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    atm.setEnergyFunction(atm.getEnergyFunction().replace('Lambda1', 'Lam bda1'))
    with pytest.raises(IdentityError, match='expression|schedule'):
        admit_system(bundle, system, admission)


@pytest.mark.parametrize('stage', ('physical', 'preparation', 'native', 'upstream'))
@pytest.mark.parametrize('restored', (False, True))
def test_fixed_physical_globals_reject_context_or_state_mutation(stage, restored):
    physical, transfer, schedule, restraints, snapshot = global_case()
    with holder(stage, physical, transfer, schedule, restraints) as run:
        evaluator = evaluator_of(run)
        args = (snapshot,) if stage in ('physical', 'preparation') else (snapshot, 'first')
        evaluator.evaluate(*args)
        evaluator.context.setParameter('physical_k', 200.)
        if restored:
            state = evaluator.context.getState(getPositions=True, getParameters=True)
            evaluator.context.setParameter('physical_k', 2.)
            evaluator.context.setState(state)
        with pytest.raises(IdentityError, match='physical_k|parameter'):
            evaluator.evaluate(*args)


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
@pytest.mark.parametrize('stage', ('native', 'upstream'))
def test_schedule_parameter_cannot_control_physical_child(kind, stage):
    physical, transfer, _, restraints, _ = global_case(kind, name='Lambda1', value=0.)
    schedule = production_schedule((('first', production_parameters(Lambda1=0.)),
                                    ('second', production_parameters(Lambda1=.3))))
    with pytest.raises(IdentityError, match='collision|physical|parameter|schedule'):
        with holder(stage, physical, transfer, schedule, restraints):
            pass


@pytest.mark.parametrize('name', ('Lambda1', 'UOffset'))
@pytest.mark.parametrize('admission', ('sealer', 'artifact'))
def test_collision_is_rejected_even_when_constructors_are_bypassed(name, admission):
    physical, transfer, schedule, restraints, _ = atom_case()
    bundle = build_atm(physical, transfer, schedule, restraints)
    new_physical, new_transfer, _, _, _ = global_case('abfe', name=name, value=schedule.states[0].parameters[name])
    system = mm.XmlSerializer.deserialize(bundle.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    new_source = physical_system(new_physical)
    atm.addForce(copy.copy(new_source.getForces()[-1]))
    bundle = replace(bundle, physical=new_physical, transfer=new_transfer,
                     routing_report=validate_routing(system, new_physical, restraints))
    with pytest.raises(IdentityError, match='collision|physical|parameter|schedule'):
        admit_system(bundle, system, admission)


def test_linear_schedule_parameter_collision_is_rejected():
    physical, transfer, _, restraints, _ = global_case(name='Lambda', value=0.)
    schedule = linear_schedule((('first', 0.), ('second', .37)))
    with pytest.raises(IdentityError, match='collision|physical|parameter|schedule'):
        build_atm(physical, transfer, schedule, restraints)


@pytest.mark.parametrize('stage', ('physical', 'preparation', 'native', 'upstream'))
@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_fixed_global_positive_control_full_forces_and_state_changes(stage, platform):
    physical, transfer, schedule, restraints, snapshot = global_case(old_to_new=(6,2,4,0,5,1,3))
    runtime = replace(REFERENCE, platform=platform)

    def expected_physical(positions):
        energy, forces = physical_answer(positions)
        # Independent negative gradient for k=2 on real a1 (index 2).
        forces[2] -= 2.*positions[2]
        return energy+float(np.dot(positions[2], positions[2])), forces

    with holder(stage, physical, transfer, schedule, restraints, runtime) as run:
        evaluator = evaluator_of(run)
        if stage in ('physical', 'preparation'):
            energy, forces = expected_physical(np.asarray(snapshot.positions_nm))
            actual = evaluator.evaluate(snapshot)
            assert actual.energy_kj_mol == pytest.approx(energy, abs=1e-8, rel=0)
            np.testing.assert_allclose(actual.forces_kj_mol_nm, forces, atol=1e-7, rtol=0)
        else:
            for state in schedule.states:
                u0, f0 = expected_physical(mapped_positions(snapshot.positions_nm, 'rbfe', 0))
                u1, f1 = expected_physical(mapped_positions(snapshot.positions_nm, 'rbfe', 1))
                expression, weights, _ = nonlinear_answer(u0, u1, state.parameters)
                outside, fk = outside_answer(snapshot.positions_nm)
                actual = evaluator.evaluate(snapshot, state.state_id)
                check(actual, (u0, u1, expression, outside, weights[0]*f0+weights[1]*f1+fk))
                assert actual.parameters == state.parameters
        assert evaluator.context.getParameter('physical_k') == 2.


@pytest.mark.parametrize('stage', ('native', 'upstream'))
def test_explicit_state_restoration_resets_physical_and_schedule_globals(stage):
    physical, transfer, schedule, restraints, snapshot = global_case()
    with holder(stage, physical, transfer, schedule, restraints) as run:
        evaluator = evaluator_of(run)
        expected = evaluator.evaluate(snapshot, 'second')
        evaluator.set_state('first')
        evaluator.context.setParameter('physical_k', 200.)
        state = evaluator.context.getState(getPositions=True, getParameters=True)
        evaluator.context.setParameter('physical_k', 2.)
        evaluator.restore_state(state, 'second')
        assert evaluator.context.getParameter('physical_k') == 2.
        assert evaluator.context.getParameter('Lambda1') == .3
        assert evaluator.evaluate(snapshot, 'second') == expected


@pytest.mark.parametrize('stage', ('export', 'native', 'upstream'))
@pytest.mark.parametrize('force_type', ('python', 'external'))
@pytest.mark.parametrize('change', ('rename', 'regroup', 'both'))
def test_duplicate_physical_content_cannot_be_hidden_by_labels(stage, force_type, change):
    physical, transfer, schedule, restraints, _ = atom_case('rbfe', marker=2.)
    system = physical_system(physical)
    force = system.getForce(0) if force_type == 'python' else system.getForces()[-1]
    duplicate = copy.copy(force)
    if change in ('rename', 'both'):
        duplicate.setName('regression:renamed-duplicate')
    if change in ('regroup', 'both'):
        duplicate.setForceGroup(7)
    system.addForce(duplicate)
    physical = reseal_physical(physical, system)
    transfer = resolve_protocol(physical, transfer.protocol)
    with pytest.raises(IdentityError, match='duplicate'):
        if stage == 'export':
            export_physical(physical)
        else:
            with holder(stage, physical, transfer, schedule, restraints):
                pass


@pytest.mark.parametrize('stage', ('export', 'native', 'upstream'))
def test_distinct_physical_parameters_with_same_label_are_admitted(stage):
    physical, transfer, schedule, restraints, snapshot = atom_case('rbfe', marker=2.)
    system = physical_system(physical)
    distinct = copy.copy(system.getForces()[-1])
    particle, _ = distinct.getParticleParameters(0)
    distinct.setParticleParameters(0, particle, [3.])
    distinct.setForceGroup(7)
    system.addForce(distinct)
    physical = reseal_physical(physical, system)
    transfer = resolve_protocol(physical, transfer.protocol)
    if stage == 'export':
        assert export_physical(physical).system.getNumForces() == 5
        return
    with holder(stage, physical, transfer, schedule, restraints) as run:
        for state in schedule.states:
            u0, f0 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 0), marker=5.)
            u1, f1 = physical_answer(mapped_positions(snapshot.positions_nm, 'rbfe', 1), marker=5.)
            expression, weights, _ = nonlinear_answer(u0, u1, state.parameters)
            outside, fk = outside_answer(snapshot.positions_nm)
            check(evaluator_of(run).evaluate(snapshot, state.state_id),
                  (u0, u1, expression, outside, weights[0]*f0+weights[1]*f1+fk))
