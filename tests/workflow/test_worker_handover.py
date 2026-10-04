"""Exercise the actual pinned worker constructor and sealed file contract."""
import hashlib
from dataclasses import replace
import numpy as np
import pytest
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE


def test_real_worker_constructor_preserves_high_precision_state(tmp_path):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run, load_worker_run
    from atom_openmm.ommworker import OMMWorkerATMSync
    physical, transfer, schedule, restraints, snapshot = atom_case('abfe', marker=20.)
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        answer = source.evaluate(snapshot,'second')
        manifest, digest = export_worker_run(source,tmp_path/'export',snapshot,'second')
    with load_worker_run(manifest.parent,digest,trusted=True) as loaded:
        assert type(loaded.worker) is OMMWorkerATMSync
        assert loaded.worker.simulation.context is loaded.evaluator.context
        from openmm import unit
        positions = loaded.evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        np.testing.assert_array_equal(positions[list(physical.old_to_new)],snapshot.positions_nm)
        result = loaded.evaluate(snapshot,'second')
        assert result.total.energy_kj_mol == pytest.approx(answer.total.energy_kj_mol,abs=1.e-8)
        assert np.allclose(result.total.forces_kj_mol_nm,answer.total.forces_kj_mol_nm,atol=1.e-7,rtol=1.e-7)
        assert result.parameters == answer.parameters and result.raw == answer.raw
        assert loaded.evaluator.integrator.getStepSize().value_in_unit(__import__('openmm').unit.picosecond)==.0005


def test_worker_artifact_trust_and_identity_are_checked_before_loading(tmp_path):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run, load_worker_run
    from atm_mlmm.schema import IdentityError, UnsupportedCapability
    physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        manifest,digest=export_worker_run(source,tmp_path/'export',snapshot,'first')
    with pytest.raises(UnsupportedCapability,match='trusted'):
        load_worker_run(manifest.parent,digest)
    with pytest.raises(IdentityError,match='digest'):
        load_worker_run(manifest.parent,'0'*64,trusted=True)
    path=manifest.parent/'handover_sys.xml'
    path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(IdentityError,match='file'):
        load_worker_run(manifest.parent,digest,trusted=True)


def test_checkpoint_continuity_and_portable_state_have_distinct_guarantees(tmp_path):
    from atm_mlmm.adapters.atom import build_atom,export_worker_run,load_worker_run
    import openmm as mm
    from openmm import unit
    physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        manifest,digest=export_worker_run(source,tmp_path/'export',snapshot,'first')
    with load_worker_run(manifest.parent,digest,trusted=True) as worker:
        worker.set_state('second')
        worker.evaluator.context.setVelocitiesToTemperature(300.,617)
        worker.evaluator.integrator.step(4)
        state=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        checkpoint=worker.evaluator.context.createCheckpoint()
        portable=mm.XmlSerializer.serialize(state)
        x=state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        fixed=replace(snapshot,positions_nm=x[list(physical.old_to_new)])
        reference=worker.evaluate(fixed,'second')
        worker.evaluator.integrator.step(2)
        expected=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
    with load_worker_run(manifest.parent,digest,trusted=True) as worker:
        worker.restore_checkpoint(checkpoint,'second')
        worker.evaluator.integrator.step(2)
        actual=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        np.testing.assert_array_equal(actual.getPositions(asNumpy=True),expected.getPositions(asNumpy=True))
        np.testing.assert_array_equal(actual.getVelocities(asNumpy=True),expected.getVelocities(asNumpy=True))
        assert actual.getTime()==expected.getTime()
    with load_worker_run(manifest.parent,digest,trusted=True,integrator_seed=73) as worker:
        worker.restore_portable_state(portable,'second')
        actual=worker.evaluate(fixed,'second')
        assert actual.raw==reference.raw and actual.parameters==reference.parameters
        np.testing.assert_array_equal(actual.total.forces_kj_mol_nm,reference.total.forces_kj_mol_nm)
        # State restores position/velocity/parameters, while RNG is independently seeded.
        assert worker.integrator_seed==73
