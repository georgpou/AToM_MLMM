from dataclasses import replace
import copy
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.analytic_oracle import BrokenEnvironmentSpring, REFERENCE, case, check, expected_linear


@pytest.mark.parametrize('fault', ('wrong-index', 'omitted-force', 'environment-force',
                                  'reversed-tuple', 'stale-environment', 'factor-ten', 'double-count'))
def test_known_transfer_errors_are_detected(fault):
    from atm_mlmm.atm import build_atm, evaluate_atm
    from atm_mlmm.schema import QualificationError
    physical, transfer, schedule, restraints, snapshot = case('rbfe')
    result = evaluate_atm(build_atm(physical, transfer, schedule, restraints), snapshot, 'middle', REFERENCE)
    expected = expected_linear(snapshot, 'rbfe', .37)
    check(result, expected)
    forces = np.array(result.total.forces_kj_mol_nm)
    raw = result.raw
    if fault == 'wrong-index':
        forces[[0,2]] = forces[[2,0]]
    elif fault == 'omitted-force':
        forces[:] = 0.
    elif fault == 'environment-force':
        forces[1] = 0.
    elif fault == 'reversed-tuple':
        raw = replace(raw, u0_raw_kJ_mol=raw.u1_raw_kJ_mol, u1_raw_kJ_mol=raw.u0_raw_kJ_mol,
                      delta_u_raw_kJ_mol=-raw.delta_u_raw_kJ_mol)
    elif fault == 'stale-environment':
        initial = evaluate_atm(build_atm(physical, transfer, schedule, restraints), snapshot, 'initial', REFERENCE)
        forces[1] = initial.total.forces_kj_mol_nm[1]
    elif fault == 'factor-ten':
        forces *= 10.
    else:
        forces *= 2.
    bad = replace(result, raw=raw, total=replace(result.total, forces_kj_mol_nm=forces))
    with pytest.raises(QualificationError, match='u0|u1|force'):
        check(bad, expected)


@pytest.mark.parametrize('fault', ('omitted-child', 'omitted-coupling', 'double-child'))
def test_actual_physical_force_faults_are_detected(fault):
    from atm_mlmm.analytic import seal_physical
    from atm_mlmm.atm import build_atm, evaluate_atm, physical_system
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.schema import IdentityError, QualificationError
    physical, transfer, schedule, restraints, snapshot = case('rbfe')
    system = physical_system(physical)
    if fault == 'double-child':
        system.addForce(copy.copy(system.getForce(0)))
    else:
        names = [f.getName() for f in system.getForces()]
        index = 0 if fault == 'omitted-child' else names.index('analytic:environment:a1:env')
        system.removeForce(index)
    faulty = seal_physical(system, physical.topology, ml_atom_ids=physical.ml_atom_ids,
                          old_to_new=physical.old_to_new, manifest=physical.manifest)
    with pytest.raises((IdentityError, QualificationError), match='u0|u1|duplicate'):
        result = evaluate_atm(build_atm(faulty, resolve_protocol(faulty, transfer.protocol), schedule, restraints),
                              snapshot, 'middle', REFERENCE)
        check(result, expected_linear(snapshot, 'rbfe', .37))


@pytest.mark.parametrize('fault', ('zero-MM-gradient', 'stale-input', 'factor-ten'))
def test_executable_environment_callback_faults_are_detected(fault):
    import openmm as mm
    from atm_mlmm.analytic import seal_physical
    from atm_mlmm.atm import build_atm, evaluate_atm, physical_system
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.schema import QualificationError
    physical, transfer, schedule, restraints, snapshot = case('rbfe')
    system = physical_system(physical)
    index = next(i for i, f in enumerate(system.getForces()) if f.getName() == 'analytic:environment:a1:env')
    broken = mm.PythonForce(BrokenEnvironmentSpring(fault, (snapshot.positions_nm[2], snapshot.positions_nm[1])))
    broken.setParticles([physical.real_to_final[a] for a in ('a1', 'env')])
    broken.setName('analytic:environment:a1:env')
    system.removeForce(index)
    system.addForce(broken)
    faulty = seal_physical(system, physical.topology, ml_atom_ids=physical.ml_atom_ids,
                          old_to_new=physical.old_to_new, manifest=physical.manifest)
    result = evaluate_atm(build_atm(faulty, resolve_protocol(faulty, transfer.protocol), schedule, restraints),
                          snapshot, 'middle', REFERENCE)
    with pytest.raises(QualificationError, match='u1|force'):
        check(result, expected_linear(snapshot, 'rbfe', .37))


def test_smallest_stale_callback_reproducer_after_fresh_reload(tmp_path):
    import openmm as mm
    from atm_mlmm.analytic import seal_physical
    from atm_mlmm.atm import build_atm, physical_system, save_bundle
    from atm_mlmm.geometry import resolve_protocol
    physical, transfer, schedule, restraints, snapshot = case('rbfe')
    system = physical_system(physical)
    index = next(i for i, f in enumerate(system.getForces()) if f.getName() == 'analytic:environment:a1:env')
    broken = mm.PythonForce(BrokenEnvironmentSpring('stale-input', (snapshot.positions_nm[2], snapshot.positions_nm[1])))
    broken.setParticles([2,1])
    broken.setName('analytic:environment:a1:env')
    system.removeForce(index)
    system.addForce(broken)
    faulty = seal_physical(system, physical.topology, ml_atom_ids=physical.ml_atom_ids,
                          old_to_new=physical.old_to_new, manifest=physical.manifest)
    target = tmp_path/'stale-reproducer.json'
    digest = save_bundle(target, build_atm(faulty, resolve_protocol(faulty, transfer.protocol), schedule, restraints))
    code = '''
import socket, sys
def deny(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket.connect = deny
socket.create_connection = deny
from atm_mlmm.atm import load_bundle, evaluate_atm
from atm_mlmm.schema import QualificationError
from tests.analytic_oracle import case, check, expected_linear, REFERENCE
snapshot = case('rbfe')[-1]
result = evaluate_atm(load_bundle(sys.argv[1], sys.argv[2], trusted=True), snapshot, 'middle', REFERENCE)
try:
    check(result, expected_linear(snapshot, 'rbfe', .37))
except QualificationError as error:
    assert 'u1' in str(error), str(error)
    print('stale descriptor detected after fresh reload: ' + str(error))
else:
    raise AssertionError('fault went undetected')
'''
    root = Path(__file__).resolve().parents[2]
    run = subprocess.run([sys.executable, '-c', code, str(target), digest],
                         env=dict(os.environ, PYTHONPATH=str(root/'src')+os.pathsep+str(root),
                                  XDG_CACHE_HOME=str(tmp_path/'empty-cache')), text=True, capture_output=True, timeout=60)
    assert run.returncode == 0, run.stdout+run.stderr
    assert 'stale descriptor detected after fresh reload' in run.stdout
