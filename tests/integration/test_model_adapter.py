"""G05 independent native/adapter and derived-cap contracts."""
from dataclasses import replace

import numpy as np
import pytest

from tests.link_oracle import IDS, REFERENCE, input_case
from tests.model_oracle import derived_input, project, raw_adapter

pytestmark = pytest.mark.model_assets


def real_case():
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec
    original, spec, snapshot = input_case()
    bundle = build_physical(original, resolve_partition(original.topology, spec),
                            model_spec(), EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'),
                            probe=None, cap_distance_nm=.117)
    return bundle, snapshot


@pytest.fixture(scope='module')
def real_fixture():
    return real_case()


@pytest.fixture(scope='module')
def native():
    from atm_mlmm.model_reference import NativeMACE
    return NativeMACE()


def assert_agree(energy, forces, expected_energy, expected_forces):
    assert abs(energy - expected_energy) <= 1e-4
    np.testing.assert_allclose(forces, expected_forces, atol=5e-3, rtol=0)


def capture(name, record):
    import json, os
    from pathlib import Path
    if root := os.environ.get('ATOM_G05_CAPTURE_DIR'):
        path = Path(root) / (name + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as stream:
            json.dump(record, stream, indent=2, allow_nan=False)


@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_native_and_openmm_energy_forces(native, real_fixture, platform):
    bundle, snapshot = real_fixture
    numbers, coordinates, _ = derived_input(bundle, snapshot)
    expected = native.evaluate(numbers, coordinates)
    energy, forces = raw_adapter(numbers, coordinates, platform)
    assert_agree(energy, forces, expected['energy_kj_mol'], expected['forces_kj_mol_nm'])
    capture('raw-' + platform, {'native': expected, 'adapter_energy_kj_mol': energy,
                               'adapter_forces_kj_mol_nm': forces.tolist()})


@pytest.mark.parametrize('platform', ('Reference', 'CPU'))
def test_real_parent_forces_with_model_caps(native, real_fixture, platform):
    from atm_mlmm.atm import PhysicalEvaluator
    from tests.integration.test_link_geometry import model_result
    from tests.link_permutation import plain_result
    import openmm as mm
    bundle, snapshot = real_fixture
    numbers, coordinates, jacobians = derived_input(bundle, snapshot)
    expected = native.evaluate(numbers, coordinates)
    projected = project(expected['forces_kj_mol_nm'], jacobians)
    # Both parent contributions must be nonzero, including the MM parent.
    assert np.linalg.norm(projected[0]) > .1
    assert np.linalg.norm(projected[1]) > .1
    model_energy, model_forces, final = model_result(bundle, snapshot, platform)
    assert_agree(model_energy, model_forces, expected['energy_kj_mol'], projected)
    retained_e, retained_f = plain_result(mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml']),
                                         snapshot.positions_nm)
    with PhysicalEvaluator(bundle, replace(REFERENCE, platform=platform)) as evaluator:
        actual = evaluator.evaluate(snapshot)
    assert actual.real_atom_ids == IDS
    assert_agree(actual.energy_kj_mol, actual.forces_kj_mol_nm,
                 expected['energy_kj_mol'] + retained_e, projected + retained_f)
    np.testing.assert_allclose(final[bundle.links[0].final_particle_index], coordinates[-1], atol=1e-14)
    capture('projected-' + platform, {'native': expected, 'independent_jacobians': jacobians.tolist(),
            'expected_model_real_forces': projected.tolist(), 'model_real_forces': model_forces.tolist(),
            'retained_mm_energy': retained_e, 'retained_mm_forces': retained_f.tolist(),
            'total_energy': actual.energy_kj_mol, 'total_real_forces': actual.forces_kj_mol_nm})


def test_consistent_translation_rotation_and_permutation(native, real_fixture):
    bundle, snapshot = real_fixture
    numbers, coordinates, _ = derived_input(bundle, snapshot)
    baseline = native.evaluate(numbers, coordinates)
    angle = .731
    rotation = np.array([[np.cos(angle), -np.sin(angle), 0.],
                         [np.sin(angle), np.cos(angle), 0.], [0., 0., 1.]])
    shifted = coordinates @ rotation.T + (.37, -.82, .21)
    permutation = np.array([7, 2, 9, 0, 5, 8, 1, 6, 4, 3])
    changed = native.evaluate(np.array(numbers)[permutation], shifted[permutation])
    expected_f = np.asarray(baseline['forces_kj_mol_nm']) @ rotation.T
    assert_agree(changed['energy_kj_mol'], changed['forces_kj_mol_nm'],
                 baseline['energy_kj_mol'], expected_f[permutation])
    energy, forces = raw_adapter(np.array(numbers)[permutation], shifted[permutation])
    assert_agree(energy, forces, baseline['energy_kj_mol'], expected_f[permutation])
    capture('transformed', {'permutation': permutation.tolist(), 'rotation': rotation.tolist(),
            'baseline': baseline, 'transformed': changed, 'adapter_energy': energy,
            'adapter_forces': forces.tolist()})


def test_nonidentity_final_map(native, real_fixture):
    import openmm as mm
    from atm_mlmm.atm import physical_system
    from atm_mlmm.embeddings.mechanical import seal_boundary_result, openmm_topology
    from atm_mlmm.partition import resolve_partition
    from tests.link_permutation import permute_info
    from tests.integration.test_link_geometry import model_result
    bundle, snapshot = real_fixture
    original, spec, _ = input_case()
    topology = openmm_topology(original.topology)
    residue = topology.addResidue('cap', topology.addChain())
    from openmm import app
    cap = topology.addAtom('cap', app.Element.getBySymbol('H'), residue)
    info = permute_info(dict(system=physical_system(bundle), topology=topology, oldToNew=list(range(13))),
                        (9, 4, 1, 12, 8, 0, 11, 3, 7, 2, 13, 6, 10, 5))
    remapped = seal_boundary_result(original, resolve_partition(original.topology, spec), info,
                                    manifest={'fixture_kind': 'pinned_mace_candidate'})
    assert remapped.links[0].final_particle_index == 5
    numbers, coordinates, jacobians = derived_input(remapped, snapshot)
    expected = native.evaluate(numbers, coordinates)
    energy, forces, _ = model_result(remapped, snapshot)
    assert_agree(energy, forces, expected['energy_kj_mol'], project(expected['forces_kj_mol_nm'], jacobians))


def test_component_finite_difference_sweep(native, real_fixture):
    from atm_mlmm.atm import PhysicalEvaluator
    bundle, snapshot = real_fixture
    numbers, coordinates, jacobians = derived_input(bundle, snapshot)
    expected = project(native.evaluate(numbers, coordinates)['forces_kj_mol_nm'], jacobians)
    samples = []
    # Independently rebuild cap geometry for every real-coordinate perturbation.
    for index in (0, 1, 2, 5, 8, 10):
        for axis in range(3):
            estimates = []
            for step in (1e-3, 1e-4, 1e-5):
                energies = []
                for sign in (1, -1):
                    r = np.array(snapshot.positions_nm)
                    r[index, axis] += sign * step
                    n, x, _ = derived_input(bundle, replace(snapshot, positions_nm=r))
                    energies.append(native.evaluate(n, x)['energy_kj_mol'])
                estimates.append(-(energies[0] - energies[1]) / (2 * step))
            errors = np.abs(np.array(estimates) - expected[index, axis])
            assert errors[-1] <= errors[0] + 1e-5, (index, axis, errors)
            samples.append({'real_id': IDS[index], 'axis': axis, 'estimates': estimates,
                            'reference': expected[index, axis], 'errors': errors.tolist()})
    rms = np.sqrt(np.mean([s['errors'][-1]**2 for s in samples]))
    reference_rms = np.sqrt(np.mean([s['reference']**2 for s in samples]))
    assert rms <= 1e-3 + 1e-4 * reference_rms
    # The complete physical force also differentiates retained classical terms.
    with PhysicalEvaluator(bundle, REFERENCE) as evaluator:
        physical = evaluator.evaluate(snapshot)
        full_samples = []
        for i in (0, 1, 5, 8):
            for axis in range(3):
                estimates = []
                for step in (1e-3, 1e-4, 1e-5, 1e-6):
                    energies = []
                    for sign in (1, -1):
                        r = np.array(snapshot.positions_nm); r[i, axis] += sign * step
                        energies.append(evaluator.evaluate(replace(snapshot, positions_nm=r)).energy_kj_mol)
                    estimates.append(-(energies[0] - energies[1]) / (2 * step))
                error = abs(estimates[-1] - physical.forces_kj_mol_nm[i][axis])
                assert error <= 1e-3 + 1e-4 * abs(physical.forces_kj_mol_nm[i][axis])
                full_samples.append({'real_id': IDS[i], 'axis': axis, 'estimates': estimates,
                                     'reference': physical.forces_kj_mol_nm[i][axis], 'error': error})
    capture('finite-differences', {'model_samples': samples, 'model_rms_error': rms,
                                 'full_physical_samples': full_samples})


@pytest.mark.parametrize('fault', ('omit-parent', 'force-times-ten', 'wrong-order', 'stale-cap'))
def test_deliberate_numeric_faults(native, real_fixture, fault):
    bundle, snapshot = real_fixture
    n, x, jac = derived_input(bundle, snapshot)
    expected = native.evaluate(n, x)
    projected = project(expected['forces_kj_mol_nm'], jac)
    faulty = projected.copy()
    if fault == 'omit-parent':
        faulty[1] = 0.
    elif fault == 'force-times-ten':
        faulty *= 10.
    elif fault == 'wrong-order':
        faulty[[0, 8]] = faulty[[8, 0]]
    else:
        moved = np.array(snapshot.positions_nm); moved[1] += (.01, .02, -.01)
        n, _, new_jac = derived_input(bundle, replace(snapshot, positions_nm=moved))
        new_n, new_x, _ = derived_input(bundle, replace(snapshot, positions_nm=moved))
        projected = project(native.evaluate(new_n, new_x)['forces_kj_mol_nm'], new_jac)
        faulty = project(expected['forces_kj_mol_nm'], new_jac)
    with pytest.raises(AssertionError):
        assert_agree(0., faulty, 0., projected)
    capture('fault-' + fault, {'expected': projected.tolist(), 'faulty': faulty.tolist(),
                               'max_force_error': float(np.max(np.abs(faulty - projected)))})


def test_mace_nested_atm_real_force_oracle(native, real_fixture):
    from atm_mlmm.atm import AtmEvaluator, build_atm
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schedule import linear_schedule
    from atm_mlmm.schema import MobileGroup, RestraintSpec
    from tests.link_permutation import plain_result
    import openmm as mm
    bundle, snapshot = real_fixture
    protocol = make_protocol((MobileGroup('mobile', IDS[8:], ('ligand',), 'ligand'),), (.3, .1, -.2))
    transfer = resolve_protocol(bundle, protocol)
    atm = build_atm(bundle, transfer, linear_schedule((('initial',0.),('middle',.37),('final',1.))),
                    RestraintSpec('outside', ('l8',), 0., (.2,.4,.1)))
    endpoints = []
    for mapping in (0,1):
        r=np.array(snapshot.positions_nm)
        if mapping:r[8:] += (.3,.1,-.2)
        frame=replace(snapshot,positions_nm=r)
        numbers,x,jac=derived_input(bundle,frame)
        raw=native.evaluate(numbers,x)
        mm_e,mm_f=plain_result(mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml']),r)
        endpoints.append((raw['energy_kj_mol']+mm_e,project(raw['forces_kj_mol_nm'],jac)+mm_f))
    records=[]
    with AtmEvaluator(atm,REFERENCE) as evaluator:
        for name,lam in (('initial',0.),('middle',.37),('final',1.)):
            actual=evaluator.evaluate(snapshot,name)
            energy=(1-lam)*endpoints[0][0]+lam*endpoints[1][0]
            forces=(1-lam)*endpoints[0][1]+lam*endpoints[1][1]
            assert abs(actual.raw.u0_raw_kJ_mol-endpoints[0][0])<=1e-4
            assert abs(actual.raw.u1_raw_kJ_mol-endpoints[1][0])<=1e-4
            assert_agree(actual.total.energy_kj_mol,actual.total.forces_kj_mol_nm,energy,forces)
            records.append({'state':name,'raw0':actual.raw.u0_raw_kJ_mol,'raw1':actual.raw.u1_raw_kJ_mol,
                            'energy':actual.total.energy_kj_mol,'forces':actual.total.forces_kj_mol_nm})
    capture('nested-atm', {'endpoint_oracles':[{'energy':e,'forces':f.tolist()} for e,f in endpoints],
                           'actual_states':records,'full_particle_maps':len(transfer.displacement1_nm)})


def test_local_asset_fresh_process_reload(real_fixture, tmp_path):
    import hashlib, json, os, shutil, subprocess, sys
    from pathlib import Path
    from atm_mlmm.atm import PhysicalEvaluator, save_bundle
    from atm_mlmm.schema import to_json
    bundle,snapshot=real_fixture
    with PhysicalEvaluator(bundle,REFERENCE) as evaluator:expected=evaluator.evaluate(snapshot)
    path=tmp_path/'physical.json';digest=save_bundle(path,bundle)
    (tmp_path/'snapshot.json').write_text(to_json(snapshot))
    # Move source and approved asset together to a fresh installation root.
    # Old absolute asset paths must never become an undeclared cache dependency.
    repo=Path(__file__).resolve().parents[2];relocated=tmp_path/'relocated'
    shutil.copytree(repo/'src',relocated/'src',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(repo/'models',relocated/'models')
    code = '''import json,socket,sys,builtins,io
def denied(*args,**kwargs): raise RuntimeError("offline reload forbids network")
socket.socket.connect=denied
socket.create_connection=denied
socket.getaddrinfo=denied
old_root=sys.argv[4]
normal_open=builtins.open
def guarded_open(file,*args,**kwargs):
    if str(file).startswith(old_root):raise RuntimeError("old checkout is unavailable")
    return normal_open(file,*args,**kwargs)
builtins.open=guarded_open
io.open=guarded_open
from atm_mlmm.atm import load_bundle,PhysicalEvaluator
from atm_mlmm.schema import from_json,RuntimeSpec
bundle=load_bundle(sys.argv[1],sys.argv[2],trusted=True)
snapshot=from_json(normal_open(sys.argv[3]).read())
runtime=RuntimeSpec('Reference','double',(),.0005,300.,'NVT','Verlet')
with PhysicalEvaluator(bundle,runtime) as evaluator:out=evaluator.evaluate(snapshot)
print(json.dumps({'energy':out.energy_kj_mol,'forces':out.forces_kj_mol_nm,
 'physical_identity':bundle.content_identity,'model_input_ids':bundle.model_input_ids,
 'links':len(bundle.links),'network_denied':True,'old_checkout_denied':True}))
'''
    env={**os.environ,'PYTHONPATH':str(relocated/'src'),'XDG_CACHE_HOME':str(tmp_path/'empty-xdg'),
         'TORCH_HOME':str(tmp_path/'empty-torch'),'MACE_CACHE_DIR':str(tmp_path/'empty-mace')}
    result=subprocess.run([sys.executable,'-c',code,str(path),digest,str(tmp_path/'snapshot.json'),str(repo)],
                          cwd=tmp_path,env=env,text=True,capture_output=True)
    assert result.returncode==0,result.stdout+result.stderr
    data=json.loads(result.stdout.splitlines()[-1])
    assert data['physical_identity']==bundle.content_identity
    assert data['links']==1 and data['network_denied'] and data['old_checkout_denied']
    assert_agree(data['energy'],data['forces'],expected.energy_kj_mol,expected.forces_kj_mol_nm)
    capture('offline-serialized-reload',{'bundle_sha256':digest,'result':data,'child_stderr':result.stderr})
