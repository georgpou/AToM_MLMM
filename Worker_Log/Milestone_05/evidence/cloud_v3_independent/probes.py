"""Independent frozen-snapshot review probes; never imported by production."""
from contextlib import ExitStack
from dataclasses import replace
from itertools import product
from pathlib import Path
import json

import numpy as np
import openmm as mm
from openmm import app, unit
import pytest

from atm_mlmm.schema import NumericalDomainError, IdentityError, Snapshot, from_json
from tests.analytic_oracle import REFERENCE
from tests.workflow.test_atom_force_routing import atom_case

ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_preliminary_pdb_box_and_enumerated_image_oracle(kind):
    """Enumerate 27 physical images independently of minimum_image()."""
    from atm_mlmm.workflow import _domain
    attempt = Path('/workspace/cloud-engine-pilots/water-v3') / kind
    bundle = from_json((attempt / 'worker/bundle.json').read_text())
    physical = bundle.physical
    pdb = app.PDBFile(str(attempt / 'worker/handover.pdb'))
    box = pdb.topology.getPeriodicBoxVectors().value_in_unit(unit.nanometer)
    np.testing.assert_array_equal(box, np.eye(3)*6.4)
    real = [physical.real_to_final[a.atom_id] for a in physical.topology.atoms]
    x = np.asarray(pdb.positions.value_in_unit(unit.nanometer))[real]
    ids = tuple(a.atom_id for a in physical.topology.atoms)
    index = {a:i for i,a in enumerate(ids)}
    images = np.array(tuple(product((-1., 0., 1.), repeat=3))) * 6.4
    def nearest(a, b):
        delta = a[:,None,None,:] - b[None,:,None,:] + images[None,None,:,:]
        return np.min(np.linalg.norm(delta, axis=-1), axis=-1)
    caps = []
    for link in physical.links:
        a,b = x[index[link.ml_parent_id]], x[index[link.mm_parent_id]]
        bond = b-a
        bond = (bond+images)[np.argmin(np.linalg.norm(bond+images, axis=1))]
        caps.append(a+.109*bond/np.linalg.norm(bond))
    radii = {'H':.12, 'C':.17, 'N':.155, 'O':.152}
    ligands = [m for m in physical.topology.molecules if m.role == 'ligand']
    mapped = x.copy()
    for sign, molecule in zip((1.,-1.), ligands):
        mapped[[index[a] for a in molecule.atom_ids]] += (sign*2.4,0.,0.)
    diagnostics = _domain(physical.topology, Snapshot(ids,x,box), (2.4,0.,0.), kind,
                         tuple((l.ml_parent_id,l.mm_parent_id) for l in physical.links))
    for mapping, positions in enumerate((x,mapped)):
        minimum = float('inf')
        for i,molecule in enumerate(physical.topology.molecules):
            for other in physical.topology.molecules[i+1:]:
                a,b = [index[v] for v in molecule.atom_ids], [index[v] for v in other.atom_ids]
                scales = np.array([radii[physical.topology.atoms[j].element] for j in a])[:,None] + np.array([radii[physical.topology.atoms[j].element] for j in b])[None,:]
                minimum = min(minimum, float(np.min(nearest(positions[a],positions[b])/scales)))
        assert minimum >= .65
        assert diagnostics[mapping]['minimum_intermolecular_Bondi_ratio'] == pytest.approx(minimum, abs=1e-13)
    obstacles = [index[a] for m in physical.topology.molecules if m.role in ('host','protein') for a in m.atom_ids]
    for j,ligand in enumerate(ligands):
        positions = mapped if j == 0 else x
        static = np.vstack((positions[obstacles],caps))
        minimum = float(np.min(nearest(positions[[index[a] for a in ligand.atom_ids]], static)))
        assert minimum >= .65
        assert diagnostics[2+j]['minimum_static_distance_nm'] == pytest.approx(minimum, abs=1e-13)


def analytic_export(tmp_path):
    from atm_mlmm.adapters.atom import build_atom, export_worker_run
    physical,transfer,schedule,restraints,snapshot = atom_case('abfe', marker=20.)
    with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        manifest,digest = export_worker_run(source,tmp_path/'worker',snapshot,'first')
    return manifest,digest,snapshot


def test_exchange_evaluation_failures_propagate_without_report(tmp_path, monkeypatch):
    """All four evaluations, both restorations and postdecision refreshes."""
    from atm_mlmm.adapters.atom import load_worker_run, attempt_pair_exchange
    from atom_openmm import gibbs_sampling
    manifest,digest,snapshot = analytic_export(tmp_path)
    frames = (snapshot, replace(snapshot,positions_nm=np.array(snapshot.positions_nm)+(.03,.02,-.01)))
    normal_decision = gibbs_sampling.pairwise_metropolis_sampling
    with ExitStack() as stack:
        workers = tuple(stack.enter_context(load_worker_run(manifest.parent,digest,trusted=True)) for _ in range(2))
        for failure_call in range(1,9):
            for w,worker in enumerate(workers):
                worker.evaluate(frames[w], ('first','second')[w])
            count = {'evaluations':0, 'decisions':0}
            normal_evaluate = [w.evaluate for w in workers]
            with monkeypatch.context() as patch:
                def decision(*args):
                    count['decisions'] += 1
                    return normal_decision(*args)
                patch.setattr(gibbs_sampling,'pairwise_metropolis_sampling',decision)
                patch.setattr(gibbs_sampling,'_random',lambda:0.)
                for w,worker in enumerate(workers):
                    def evaluate(*args, w=w):
                        count['evaluations'] += 1
                        if count['evaluations'] == failure_call:
                            raise NumericalDomainError(f'independent refresh failure {failure_call}')
                        return normal_evaluate[w](*args)
                    patch.setattr(worker,'evaluate',evaluate)
                with pytest.raises(NumericalDomainError,match=f'independent refresh failure {failure_call}'):
                    attempt_pair_exchange(workers,frames,('first','second'),('A','B'))
                assert count['decisions'] == (0 if failure_call <= 6 else 1)


def test_exchange_actual_nonfinite_and_outside_mutation_rejected(tmp_path,monkeypatch):
    from atm_mlmm.adapters.atom import load_worker_run, attempt_pair_exchange
    from atom_openmm import gibbs_sampling
    manifest,digest,snapshot = analytic_export(tmp_path)
    def forbidden(*args):
        raise AssertionError('rejected exchange must never reach Metropolis')
    monkeypatch.setattr(gibbs_sampling,'pairwise_metropolis_sampling',forbidden)
    with ExitStack() as stack:
        workers = tuple(stack.enter_context(load_worker_run(manifest.parent,digest,trusted=True)) for _ in range(2))
        huge = np.array(snapshot.positions_nm)
        huge[2,0] = 1e200  # finite input, genuinely nonfinite actual child energy
        with pytest.raises((NumericalDomainError,mm.OpenMMException),match='nonfinite'):
            attempt_pair_exchange(workers,(replace(snapshot,positions_nm=huge),snapshot),('first','second'),('A','B'))
        outside = next(f for f in workers[0].evaluator.system.getForces() if isinstance(f,mm.CustomExternalForce))
        outside.setEnergyFunction('('+outside.getEnergyFunction()+')*Lambda1')
        outside.addGlobalParameter('Lambda1',.2)
        with pytest.raises(IdentityError,match='mutation'):
            attempt_pair_exchange(workers,(snapshot,snapshot),('first','second'),('A','B'))


def test_live_box_and_checkpoint_portable_state_preservation():
    """Perturb the Context cell to prove extraction reads its live State."""
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.workflow import _snapshot
    attempt = Path('/workspace/cloud-engine-pilots/water-v3/abfe')
    summary = json.loads((attempt/'summary.json').read_text())
    box = np.diag((6.6,6.7,6.8))  # diagnostic injection, not new profile evidence
    with load_worker_run(attempt/'worker',summary['worker_manifest_sha256'],trusted=True) as worker:
        context = worker.evaluator.context
        context.setPeriodicBoxVectors(*(mm.Vec3(*v) for v in box))
        worker.set_state('separated')
        original = context.getState(getPositions=True,getVelocities=True,getParameters=True)
        snapshot = _snapshot(worker)
        np.testing.assert_array_equal(snapshot.box_nm,box)
        real = list(worker.bundle.physical.old_to_new)
        np.testing.assert_array_equal(snapshot.positions_nm,original.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[real])
        np.testing.assert_array_equal(snapshot.velocities_nm_ps,original.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond)[real])
        checkpoint = context.createCheckpoint()
        portable = mm.XmlSerializer.serialize(original)
        for restore in (lambda:worker.restore_checkpoint(checkpoint,'separated'),
                        lambda:worker.restore_portable_state(portable,'separated')):
            context.setPeriodicBoxVectors(*(mm.Vec3(*v) for v in np.eye(3)*7.))
            worker.set_state('contact')
            restore()
            actual = context.getState(getPositions=True,getVelocities=True,getParameters=True)
            np.testing.assert_array_equal(actual.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer),box)
            np.testing.assert_array_equal(actual.getPositions(asNumpy=True),original.getPositions(asNumpy=True))
            np.testing.assert_array_equal(actual.getVelocities(asNumpy=True),original.getVelocities(asNumpy=True))
            assert dict(actual.getParameters()) == dict(original.getParameters())


def failure_attempt(tmp_path,monkeypatch,*,nonfinite=False,map_write_failure=False):
    import atm_mlmm.adapters.atom as adapter
    import atm_mlmm.workflow as workflow
    manifest,digest,snapshot = analytic_export(tmp_path)
    out = manifest.parent.parent
    original_step = mm.LangevinMiddleIntegrator.step
    original_state = mm.Context.getState
    original_write = Path.write_text
    original_load = adapter.load_worker_run
    owners = {}
    fired = {'value':False}
    def load(*args,**kwargs):
        worker = original_load(*args,**kwargs)
        owners[id(worker.evaluator.integrator)] = worker
        return worker
    def step(integrator,steps):
        original_step(integrator,steps)
        if nonfinite:
            context = owners[id(integrator)].evaluator.context
            positions = original_state(context,getPositions=True).getPositions(asNumpy=True)
            positions[0,0] = float('nan')*unit.nanometer
            context.setPositions(positions)
        fired['value'] = True
        raise NumericalDomainError('independent original scientific trigger')
    def state(context,*args,**kwargs):
        if fired['value'] and (kwargs.get('getEnergy') or kwargs.get('getForces')):
            raise AssertionError('failure archive reentered scientific evaluation')
        return original_state(context,*args,**kwargs)
    def write(path,*args,**kwargs):
        if map_write_failure and path.name == 'map1-state.xml':
            raise OSError('independent mapped State archive trigger')
        return original_write(path,*args,**kwargs)
    monkeypatch.setattr(adapter,'load_worker_run',load)
    monkeypatch.setattr(mm.LangevinMiddleIntegrator,'step',step)
    monkeypatch.setattr(mm.Context,'getState',state)
    monkeypatch.setattr(Path,'write_text',write)
    monkeypatch.setattr(workflow,'_domain',lambda *args:[])
    metadata = {'settings':{'frames_per_state':1,'steps_per_frame':1,'seed':41,
                           'displacement_nm':[.3,0.,0.],'protocol_kind':'abfe'},
                'worker_manifest_sha256':digest,'run_id':'independent',
                'runtime_identity':REFERENCE.content_identity,'profile':{}}
    return out, lambda:workflow._execute(out,metadata)


def test_nonfinite_failure_states_preserved_without_reentry(tmp_path,monkeypatch):
    out,execute = failure_attempt(tmp_path,monkeypatch,nonfinite=True)
    with pytest.raises(NumericalDomainError,match='independent original scientific trigger'):
        execute()
    failed = out/'failure-000000'
    for name in ('state.xml','map0-state.xml','map1-state.xml'):
        state = mm.XmlSerializer.deserialize((failed/name).read_text())
        assert np.isnan(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[0,0])
    error = json.loads((failed/'error.json').read_text())
    assert error['error_type'] == 'NumericalDomainError'
    assert not (out/'samples').exists()


def test_map_archive_failure_does_not_hide_original_scientific_error(tmp_path,monkeypatch):
    """Expected safety contract; frozen HEAD is allowed to fail this audit probe."""
    out,execute = failure_attempt(tmp_path,monkeypatch,map_write_failure=True)
    with pytest.raises(NumericalDomainError,match='independent original scientific trigger'):
        execute()
    failed = out/'failure-000000'
    error = json.loads((failed/'error.json').read_text())
    assert error['error_type'] == 'NumericalDomainError'
    assert error['message'] == 'independent original scientific trigger'
    assert not (out/'samples').exists()


def test_characterize_archive_failure_normal_cli_output(tmp_path,monkeypatch,capsys):
    """Capture actual user-visible behavior, separately from the failing contract."""
    import shutil
    import sys
    import atm_mlmm.workflow as workflow
    from atm_mlmm.__main__ import main
    out,execute = failure_attempt(tmp_path,monkeypatch,map_write_failure=True)
    monkeypatch.setattr(workflow,'resume_run',lambda *args,**kwargs:execute())
    monkeypatch.setattr(sys,'argv',['atm_mlmm','resume',str(out),'--trusted'])
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err == 'OSError: independent mapped State archive trigger\n'
    assert 'independent original scientific trigger' not in captured.err
    failed = out/'failure-000000'
    assert not (failed/'error.json').exists()
    assert not (out/'samples').exists()
    target = ROOT/'Worker_Log/Milestone_05/evidence/cloud_v3_independent/archive-failure'
    target.mkdir(exist_ok=True)
    for name in ('state.xml','checkpoint.chk','map0-state.xml'):
        shutil.copyfile(failed/name,target/name)
    characterization = dict(exit_code=exit_code,stderr=captured.err,
                            failure_files=sorted(p.name for p in failed.iterdir()),
                            samples_exist=(out/'samples').exists(),
                            original_error='NumericalDomainError: independent original scientific trigger',
                            injected_archive_error='OSError: independent mapped State archive trigger')
    (target/'cli-characterization.json').write_text(json.dumps(characterization,indent=2)+'\n')
