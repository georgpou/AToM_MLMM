"""Exercise the actual pinned worker constructor and sealed file contract."""
import hashlib
import json
from dataclasses import replace
import shutil
import numpy as np
import pytest
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE


@pytest.fixture
def exported_worker(tmp_path):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run
    physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        manifest,digest=export_worker_run(source,tmp_path/'export',snapshot,'first')
    return manifest.parent,digest


def _rebind_manifest(root, manifest):
    from atm_mlmm.persistence import write_json
    path=root/'manifest.json'
    write_json(path,manifest)
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


@pytest.mark.parametrize('mutation', ('extra-source', 'changed-source'))
def test_worker_source_inventory_is_complete_before_executable_loading(
        exported_worker,monkeypatch,mutation):
    from atm_mlmm import atm
    from atm_mlmm.adapters import atom
    from atm_mlmm.persistence import read_json
    from atm_mlmm.schema import IdentityError

    root,digest=exported_worker
    manifest=read_json(root/'manifest.json')
    prefix='runtime/source/atm_mlmm/'
    if mutation=='extra-source':
        name=prefix+'extra_untracked.py'
        path=root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('EXTRA_SOURCE = True\n')
        manifest['files'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        name=next(name for name in manifest['files'] if name.startswith(prefix) and name.endswith('/chemical_reference.py'))
        path=root/name
        path.write_bytes(path.read_bytes()+b'\n# coherently rehashed mutation\n')
        manifest['files'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    digest=_rebind_manifest(root,manifest)

    attempted=[]
    def forbidden(*args,**kwargs):
        attempted.append(True)
        raise AssertionError('worker executable bundle was deserialized before source admission')
    monkeypatch.setattr(atm,'load_bundle',forbidden)
    monkeypatch.setattr(atom.WorkerRun,'__init__',forbidden)
    with pytest.raises(IdentityError,match='source|inventory|identity'):
        atom.load_worker_run(root,digest,trusted=True)
    assert attempted==[]


def test_byte_identical_worker_bundle_can_be_relocated(exported_worker,tmp_path):
    from atm_mlmm.adapters.atom import load_worker_run

    root,digest=exported_worker
    relocated=tmp_path/'relocated-worker'
    shutil.copytree(root,relocated)
    with load_worker_run(relocated,digest,trusted=True) as worker:
        assert worker.bundle.content_identity
