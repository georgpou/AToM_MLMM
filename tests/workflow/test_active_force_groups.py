from dataclasses import replace

import numpy as np
import openmm as mm
import pytest

from tests.analytic_oracle import REFERENCE, case
from tests.workflow.test_atom_force_routing import atom_case


@pytest.mark.parametrize('stage', ('preparation', 'abfe', 'rbfe'))
@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_all_physical_groups_integrated(stage, platform):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.prepare import build_preparation
    from atm_mlmm.routing import check_active_forces
    from atm_mlmm.schema import IdentityError
    runtime = replace(REFERENCE, platform=platform)
    if stage == 'preparation':
        physical, _, _, _, snapshot = case(marker=2000.)
        holder = build_preparation(physical, runtime)
        holder.evaluate(snapshot)
        evaluator = holder
    else:
        physical, transfer, schedule, restraints, snapshot = atom_case(stage, marker=2000.)
        holder = build_atom(physical, transfer, schedule, restraints, runtime)
        holder.evaluate(snapshot, 'first')
        evaluator = holder.evaluator
    with holder:
        measurements = check_active_forces(evaluator.context, evaluator.integrator)
        assert measurements['max_force_error_kJ_mol_nm'] <= 1e-7
        force = evaluator.context.getState(getForces=True).getForces(asNumpy=True).value_in_unit(mm.unit.kilojoules_per_mole/mm.unit.nanometer)
        assert np.linalg.norm(force[4]) > 500.
        assert isinstance(evaluator.integrator, mm.LangevinMiddleIntegrator)
        assert evaluator.integrator.getStepSize().value_in_unit(mm.unit.picosecond) == .0005
        evaluator.context.setVelocities(np.zeros((7,3)))
        evaluator.integrator.setRandomNumberSeed(2026)
        evaluator.integrator.step(2)
        stepped = evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(mm.unit.nanometer)
        assert np.isfinite(stepped).all()
        assert np.linalg.norm(stepped[4]-snapshot.positions_nm[4]) > 1e-12
        # A stable-looking trajectory is insufficient: this actual integrator's
        # altered mask must reject the omitted marker/container immediately.
        evaluator.integrator.setIntegrationForceGroups(0)
        with pytest.raises(IdentityError, match='group|mask|force'):
            check_active_forces(evaluator.context, evaluator.integrator)


def test_preparation_and_export_copies():
    from atm_mlmm.atm import physical_system
    from atm_mlmm.prepare import build_preparation
    from atm_mlmm.routing import check_active_forces, export_physical
    from atm_mlmm.schema import IdentityError, UnsupportedCapability
    physical, _, _, _, snapshot = case(marker=2000.)
    original = physical.system_xml
    export = export_physical(physical)
    assert all(f.getForceGroup() == 1 for f in export.system.getForces())
    with build_preparation(physical, REFERENCE) as preparation:
        preparation.evaluate(snapshot)
        assert all(f.getForceGroup() == 0 for f in preparation.system.getForces())
        assert preparation.integrator.getIntegrationForceGroups() & 1
        assert physical.system_xml == original
        # OpenMM child proxies require their owning System to stay alive.
        original_system = physical_system(physical)
        assert all(f.getForceGroup() == 0 for f in original_system.getForces())
    with pytest.raises(UnsupportedCapability, match='physical|export'):
        build_preparation(export, REFERENCE)
    # Reproduce omission if a reserved-group copy is fed to a stock group-0 path.
    integrator = mm.LangevinMiddleIntegrator(300., 1., .0005)
    integrator.setIntegrationForceGroups({0})
    context = mm.Context(export.system, integrator, mm.Platform.getPlatformByName('Reference'))
    context.setPositions(snapshot.positions_nm)
    with pytest.raises(IdentityError, match='group|mask|force'):
        check_active_forces(context, integrator)


def test_integrator_mutation_rejected_before_production_evaluation():
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, snapshot = atom_case()
    with build_atom(physical, transfer, schedule, restraints, REFERENCE) as run:
        run.evaluator.integrator.setIntegrationForceGroups({0})
        with pytest.raises(IdentityError, match='group|mask|integrator'):
            run.evaluate(snapshot, 'first')


def test_native_integrator_mask_guard():
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.schema import IdentityError
    physical, transfer, schedule, restraints, snapshot = atom_case()
    with AtmEvaluator(build_atm(physical, transfer, schedule, restraints), REFERENCE) as evaluator:
        evaluator.integrator.setIntegrationForceGroups({0})
        with pytest.raises(IdentityError, match='group|mask|integrator'):
            evaluator.evaluate(snapshot, 'first')
