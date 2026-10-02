"""All G04 geometric/derivative assertions, with independent Cartesian oracles."""
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import openmm as mm
from openmm import unit
import pytest

from tests.link_oracle import DATA, IDS, REFERENCE, cap_answer, input_case, upstream_info


def case(*, cap_k=7., pair_k=0., environment_k=0., ligand_k=5.):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.analytic_boundary import BoundaryProbe
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec, ModelSpec
    original,spec,snapshot=input_case()
    model=ModelSpec('analytic-environment' if environment_k else 'analytic-local',None,
                    'declared_relative_energy',('H','C'),'neutral_singlet',
                    'environment_dependent' if environment_k else 'local','float64')
    probe=BoundaryProbe(cap_k, (.13,-.08,.11), pair_k, 'l8', environment_k, 'p5',
                        ligand_k, (.02,.3,-.07))
    bundle=build_physical(original,resolve_partition(original.topology,spec),model,
                          EmbeddingSpec('mechanical','1','protein_c_c','nonperiodic'),
                          probe=probe,cap_distance_nm=.117)
    return bundle,snapshot


def model_result(bundle, snapshot, platform='Reference', *, system=None):
    """Isolate the actual model child without changing its site machinery."""
    from atm_mlmm.atm import physical_system
    from atm_mlmm.geometry import final_positions
    system=physical_system(bundle) if system is None else system
    integrator=mm.VerletIntegrator(.0005)
    context=mm.Context(system,integrator,mm.Platform.getPlatformByName(platform))
    try:
        context.setPositions(final_positions(bundle,snapshot))
        context.computeVirtualSites()
        state=context.getState(getEnergy=True,getForces=True,getPositions=True,groups=1<<2)
        forces=state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
        return (float(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),
                forces[list(bundle.old_to_new)],
                state.getPositions(asNumpy=True).value_in_unit(unit.nanometer))
    finally:
        del context,integrator


def assert_components(actual, expected, tolerance=1e-7):
    np.testing.assert_allclose(actual,expected,rtol=0,atol=tolerance)


def fd_sweep(energy,snapshot,expected):
    from atm_mlmm.derivatives import finite_difference_forces
    expected=np.asarray(expected)
    errors=[]
    # Keep the three required steps. The retained GAFF Lennard-Jones term
    # needs one additional step to reach the stricter 1e-5 component target.
    for h in (1e-3,1e-4,1e-5,1e-6):
        estimate=finite_difference_forces(energy,snapshot,h)
        errors.append(float(np.max(np.abs(estimate-expected))))
    assert errors[-1]<1e-5, errors
    assert errors[-1]<=errors[0]+1e-8, errors
    rms=np.sqrt(np.mean((estimate-expected)**2))
    assert rms<=1e-3+1e-4*np.sqrt(np.mean(expected**2))
    return errors


def test_fd_restores_snapshot_on_success_and_failure():
    from atm_mlmm.derivatives import finite_difference_forces
    _,_,snapshot=input_case()
    for fail in (False,True):
        positioned=[]
        def energy(s):
            positioned.append(s)
            if fail and len(positioned)==2:raise ValueError('preserved failed perturbation')
            return float(np.sum(np.asarray(s.positions_nm)**2))
        if fail:
            with pytest.raises(ValueError,match='preserved failed'):finite_difference_forces(energy,snapshot,1e-4)
        else:finite_difference_forces(energy,snapshot,1e-4)
        assert positioned[-1]==snapshot


def test_cap_position_and_zero_mass():
    from atm_mlmm.atm import PhysicalEvaluator, physical_system
    bundle,snapshot=case()
    system=physical_system(bundle)
    link,=bundle.links
    assert system.getNumParticles()==14
    assert link.ml_parent_id=='p0' and link.mm_parent_id=='p1'
    assert link.virtual_site_type=='LocalCoordinatesSite'
    assert link.distance_nm==.117 and link.final_particle_index==13
    assert bundle.masses_da[13]==0.
    site=system.getVirtualSite(13)
    assert tuple(site.getParticle(i) for i in range(2))==(0,1)
    assert tuple(site.getOriginWeights())==(1.,0.)
    assert tuple(site.getXWeights())==(-1.,1.) and tuple(site.getYWeights())==(0.,0.)
    assert tuple(site.getLocalPosition().value_in_unit(unit.nanometer))==(.117,0.,0.)
    nb=next(f for f in system.getForces() if isinstance(f,mm.NonbondedForce))
    q,sigma,epsilon=nb.getParticleParameters(13)
    assert q.value_in_unit(unit.elementary_charge)==0.
    assert epsilon.value_in_unit(unit.kilojoule_per_mole)==0.
    with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
        evaluator.evaluate(snapshot)
        pos=evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        assert_components(pos[13],cap_answer(snapshot.positions_nm)[2],1e-12)
    # Unknown record version and inconsistent site metadata must reject.
    from atm_mlmm.schema import IdentityError, UnsupportedCapability, from_json, to_json
    assert from_json(to_json(bundle))==bundle
    with pytest.raises((IdentityError,UnsupportedCapability)):
        physical_system(replace(bundle,links=(replace(link,distance_nm=.118),)))


@pytest.mark.parametrize('platform',('Reference','CPU'))
def test_cap_parent_chain_rule(platform):
    bundle,snapshot=case(ligand_k=0.)
    energy,forces,h,raw=cap_answer(snapshot.positions_nm,ligand_k=0.)
    actual=model_result(bundle,snapshot,platform)
    assert abs(actual[0]-energy)<=1e-8
    assert_components(actual[1],forces)
    assert np.linalg.norm(forces[1])>.1 and np.linalg.norm(forces[0])>.1
    assert_components(forces[0]+forces[1],raw)
    fd_sweep(lambda s:model_result(bundle,s,platform)[0],snapshot,forces)
    # Axial and both perpendicular directions on each parent, off constraints.
    n=(np.asarray(snapshot.positions_nm)[1]-snapshot.positions_nm[0]); n/=np.linalg.norm(n)
    t=np.cross(n,(0.,0.,1.)); t/=np.linalg.norm(t)
    for parent in (0,1):
        for direction in (n,t,np.cross(n,t)):
            estimates=[]
            for step in (1e-3,1e-4,1e-5):
                r=np.array(snapshot.positions_nm)
                plus,minus=r.copy(),r.copy()
                plus[parent]+=step*direction; minus[parent]-=step*direction
                estimates.append(-(model_result(bundle,replace(snapshot,positions_nm=plus),platform)[0]-
                                    model_result(bundle,replace(snapshot,positions_nm=minus),platform)[0])/(2*step))
            assert abs(estimates[-1]-np.dot(forces[parent],direction))<1e-5
    assert_components(model_result(bundle,snapshot,platform)[1],forces)


def test_actual_and_nonidentity_index_maps():
    from atm_mlmm.embeddings.mechanical import seal_boundary_result
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup
    from tests.link_permutation import permute_info
    actual,snapshot=case(ligand_k=0.)
    original,spec,_=input_case()
    from atm_mlmm.partition import resolve_partition
    info=upstream_info()
    info=permute_info(info,(9,4,1,12,8,0,11,3,7,2,13,6,10,5))
    bundle=seal_boundary_result(original,resolve_partition(original.topology,spec),info,
                                manifest={'fixture_kind':'analytic_substitute','boundary_builder_version':1})
    assert actual.old_to_new==tuple(range(13))
    assert bundle.old_to_new==(9,4,1,12,8,0,11,3,7,2,13,6,10)
    link,=bundle.links
    assert link.final_particle_index==5
    assert bundle.model_to_final[link.cap_id]==5
    assert bundle.model_input_ids[link.model_input_index]==link.cap_id
    assert_components(model_result(bundle,snapshot)[1],cap_answer(snapshot.positions_nm,ligand_k=0.)[1])
    protocol=make_protocol((MobileGroup('mobile',IDS[8:],('ligand',),'ligand'),),(.3,.1,-.2))
    transfer=resolve_protocol(bundle,protocol)
    assert len(transfer.displacement1_nm)==14
    assert transfer.displacement1_nm[5]==(0.,0.,0.)
    assert all(transfer.displacement1_nm[bundle.real_to_final[a]]==(.3,.1,-.2) for a in IDS[8:])


@pytest.mark.parametrize('platform',('Reference','CPU'))
@pytest.mark.parametrize('environment_k',(0.,10.))
def test_stationary_cap_force_under_atm(platform,environment_k):
    from atm_mlmm.atm import AtmEvaluator, PhysicalEvaluator, build_atm
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup,RestraintSpec
    from atm_mlmm.schedule import linear_schedule
    bundle,snapshot=case(pair_k=4.,environment_k=environment_k)
    transfer=resolve_protocol(bundle,make_protocol((MobileGroup('mobile',IDS[8:],('ligand',),'ligand'),),(.3,.1,-.2)))
    schedule=linear_schedule((('initial',0.),('middle',.37),('final',1.)))
    restraints=RestraintSpec('outside',('l8',),3.,(.2,.4,.1))
    atm=build_atm(bundle,transfer,schedule,restraints)
    runtime=replace(REFERENCE,platform=platform)
    endpoints=[]
    with PhysicalEvaluator(bundle,runtime) as physical,AtmEvaluator(atm,runtime) as evaluator:
        for state in (0,1):
            r=np.array(snapshot.positions_nm)
            if state: r[8:]+=np.array((.3,.1,-.2))
            endpoints.append(physical.evaluate(replace(snapshot,positions_nm=r)))
        for name,lam in (('initial',0.),('middle',.37),('final',1.)):
            out=evaluator.evaluate(snapshot,name)
            outside=1.5*np.sum((np.array(snapshot.positions_nm)[8]-(.2,.4,.1))**2)
            fk=np.zeros((13,3)); fk[8]=-3.*(np.array(snapshot.positions_nm)[8]-(.2,.4,.1))
            expected=(1-lam)*np.array(endpoints[0].forces_kj_mol_nm)+lam*np.array(endpoints[1].forces_kj_mol_nm)+fk
            assert abs(out.raw.u0_raw_kJ_mol-endpoints[0].energy_kj_mol)<=1e-4
            assert abs(out.raw.u1_raw_kJ_mol-endpoints[1].energy_kj_mol)<=1e-4
            assert abs(out.total.energy_kj_mol-((1-lam)*endpoints[0].energy_kj_mol+lam*endpoints[1].energy_kj_mol+outside))<=1e-4
            assert_components(out.total.forces_kj_mol_nm,expected,5e-3)
            # Compare model-only ATM parents to the independent Jacobian, not just direct agreement.
            from tests.link_oracle import cap_answer
            model_expected=[]
            for state in (0,1):
                r=np.array(snapshot.positions_nm)
                if state:r[8:]+=(.3,.1,-.2)
                model_expected.append(cap_answer(r,pair_k=4.,environment_k=environment_k)[1])
            retained=mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
            # Parent contributions in the complete Hamiltonian also receive retained MM forces.
            from tests.link_permutation import plain_result
            rf=plain_result(retained,snapshot.positions_nm)[1]
            # Retained ML-MM terms change when the ligand maps, so evaluate both explicitly.
            r=np.array(snapshot.positions_nm);r[8:]+=(.3,.1,-.2)
            rf1=plain_result(retained,r)[1]
            oracle=(1-lam)*(rf+model_expected[0])+lam*(rf1+model_expected[1])+fk
            assert_components(out.total.forces_kj_mol_nm,oracle,5e-3)
        if platform=='Reference':
            expected=evaluator.evaluate(snapshot,'middle').total.forces_kj_mol_nm
            fd_sweep(lambda s:evaluator.evaluate(s,'middle').total.energy_kj_mol,snapshot,expected)
        first=evaluator.evaluate(snapshot,'initial')
        evaluator.evaluate(replace(snapshot,positions_nm=np.asarray(snapshot.positions_nm)+.023),'final')
        assert evaluator.evaluate(snapshot,'initial')==first
        positions=evaluator.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        assert_components(positions[bundle.links[0].final_particle_index],cap_answer(snapshot.positions_nm)[2],1e-12)


@pytest.mark.parametrize('platform',('Reference','CPU'))
def test_cap_environment_cross_derivative(platform):
    bundle,snapshot=case(cap_k=0.,ligand_k=0.,environment_k=10.)
    energy,forces,_,_=cap_answer(snapshot.positions_nm,cap_k=0.,ligand_k=0.,environment_k=10.)
    actual=model_result(bundle,snapshot,platform)
    assert abs(actual[0]-energy)<=1e-8
    assert_components(actual[1],forces)
    fd_sweep(lambda s:model_result(bundle,s,platform)[0],snapshot,forces)
    r=np.array(snapshot.positions_nm);r[5]+=(.07,-.04,.03)
    moved=replace(snapshot,positions_nm=r)
    assert abs(model_result(bundle,moved,platform)[0]-energy)>.001
    assert_components(model_result(bundle,moved,platform)[1],cap_answer(r,cap_k=0.,ligand_k=0.,environment_k=10.)[1])


@pytest.mark.parametrize('platform',('Reference','CPU'))
def test_cap_projected_force_and_torque_balance(platform):
    bundle,snapshot=case(cap_k=0.,ligand_k=0.,pair_k=4.,environment_k=10.)
    for r in (np.asarray(snapshot.positions_nm),np.asarray(snapshot.positions_nm)@np.array(((0,1,0),(-1,0,0),(0,0,1)))+(.3,.2,-.1)):
        s=replace(snapshot,positions_nm=r)
        forces=model_result(bundle,s,platform)[1]
        assert_components(forces,cap_answer(r,cap_k=0.,ligand_k=0.,pair_k=4.,environment_k=10.)[1])
        assert_components(forces.sum(axis=0),np.zeros(3))
        assert_components(np.cross(r,forces).sum(axis=0),np.zeros(3))
        fd_sweep(lambda s:model_result(bundle,s,platform)[0],s,forces)


def test_trusted_fresh_process_reload(tmp_path):
    from atm_mlmm.atm import build_atm,save_bundle,load_bundle
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup,RestraintSpec,IdentityError,UnsupportedCapability
    from atm_mlmm.schedule import linear_schedule
    bundle,snapshot=case(pair_k=4.,environment_k=10.)
    transfer=resolve_protocol(bundle,make_protocol((MobileGroup('mobile',IDS[8:],('ligand',),'ligand'),),(.3,.1,-.2)))
    atm=build_atm(bundle,transfer,linear_schedule((('initial',0.),('middle',.37),('final',1.))),RestraintSpec('outside',('l8',),3.,(.2,.4,.1)))
    target=tmp_path/'trusted.json';digest=save_bundle(target,atm)
    with pytest.raises(UnsupportedCapability,match='trusted'):load_bundle(target,digest)
    with pytest.raises(IdentityError,match='digest'):load_bundle(target,'0'*64,trusted=True)
    code='''
import socket,sys
def deny(*a,**k):raise AssertionError('network forbidden')
socket.socket.connect=deny;socket.create_connection=deny;socket.getaddrinfo=deny
from atm_mlmm.atm import load_bundle,AtmEvaluator
from tests.link_oracle import input_case,REFERENCE
from tests.integration.test_link_geometry import fd_sweep
b=load_bundle(sys.argv[1],sys.argv[2],trusted=True)
s=input_case()[-1]
with AtmEvaluator(b,REFERENCE) as e:
    for name in ('initial','middle','final'):
        result=e.evaluate(s,name)
        fd_sweep(lambda s:e.evaluate(s,name).total.energy_kj_mol,s,result.total.forces_kj_mol_nm)
    first=e.evaluate(s,'initial');e.evaluate(s,'final');assert e.evaluate(s,'initial')==first
print('fresh offline cap reload passed')
'''
    run=subprocess.run([sys.executable,'-c',code,str(target),digest],text=True,capture_output=True,timeout=60,
                       env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]/'src')+os.pathsep+str(Path(__file__).resolve().parents[2]),XDG_CACHE_HOME=str(tmp_path/'empty-cache')))
    assert run.returncode==0,run.stdout+run.stderr


@pytest.mark.parametrize('fault',('omit-parent','double-parent','omit-environment','stale-cap'))
def test_deliberate_derivative_faults(fault):
    from atm_mlmm.atm import physical_system
    from atm_mlmm.models.analytic_boundary import BoundaryCallback,BoundaryProbe
    from tests.link_oracle import FaultyBoundaryCallback
    bundle,snapshot=case(environment_k=10.,ligand_k=0.)
    good=model_result(bundle,snapshot)
    expected=cap_answer(snapshot.positions_nm,environment_k=10.,ligand_k=0.)[1]
    assert_components(good[1],expected)
    system=physical_system(bundle)
    normal=BoundaryCallback(BoundaryProbe(environment_k=10.,ligand_k=0.),13,8,5)
    broken=mm.PythonForce(FaultyBoundaryCallback(normal,fault,cap_answer(snapshot.positions_nm)[2]))
    broken.setParticles(list(range(14)));broken.setForceGroup(2)
    system.removeForce(system.getNumForces()-1);system.addForce(broken)
    if fault=='stale-cap':
        r=np.array(snapshot.positions_nm);r[1]+=(.01,.05,-.03)
        snapshot=replace(snapshot,positions_nm=r)
        expected=cap_answer(r,environment_k=10.,ligand_k=0.)[1]
    actual=model_result(bundle,snapshot,system=system)[1]
    with pytest.raises(AssertionError):assert_components(actual,expected)


def test_link_ids_cannot_alias_real_mm_ids():
    from atm_mlmm.schema import IdentityError
    bundle,_=case()
    link=replace(bundle.links[0],cap_id='p5')
    model=dict(bundle.model_to_final);model.pop(bundle.links[0].cap_id);model['p5']=13
    with pytest.raises(IdentityError,match='cap identity'):
        replace(bundle,links=(link,),model_to_final=model)


def test_complete_runtime_state_restored_after_cartesian_fd():
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.derivatives import finite_difference_forces
    bundle,snapshot=case(environment_k=10.)
    with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
        evaluator.context.setTime(.123)
        evaluator.context.setVelocities(np.full((14,3),.007))
        evaluator.evaluate(snapshot)
        before=evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        finite_difference_forces(lambda s:evaluator.evaluate(s).energy_kj_mol,snapshot,1e-5)
        after=evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
        assert before.getTime()==after.getTime()
        assert dict(before.getParameters())==dict(after.getParameters())
        assert_components(before.getPositions(asNumpy=True).value_in_unit(unit.nanometer),after.getPositions(asNumpy=True).value_in_unit(unit.nanometer),1e-12)
        assert_components(before.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond),after.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond),1e-12)


def test_legacy_real_only_encoding_and_future_cap_version():
    import json
    from atm_mlmm.schema import IdentityError,UnsupportedCapability,from_json,to_json
    from tests.analytic_oracle import case as legacy_case
    legacy=legacy_case()[0]
    document=json.loads(to_json(legacy))
    assert 'links' not in document['data']
    assert from_json(json.dumps(document)).content_identity==legacy.content_identity
    bundle,_=case()
    with pytest.raises(UnsupportedCapability,match='version'):
        replace(bundle,manifest={**bundle.manifest,'boundary_builder_version':2})
    with pytest.raises(IdentityError,match='model'):
        replace(bundle,model_to_final={a:i for a,i in bundle.model_to_final.items() if a!=bundle.links[0].cap_id})


def test_nonidentity_capped_atm_matches_identity_case():
    from tests.link_permutation import permute_info
    from tests.link_oracle import openmm_topology
    from atm_mlmm.atm import physical_system,build_atm,AtmEvaluator
    from atm_mlmm.embeddings.mechanical import seal_boundary_result
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup,RestraintSpec
    from atm_mlmm.schedule import linear_schedule
    bundle,snapshot=case(pair_k=4.,environment_k=10.)
    topology=openmm_topology(bundle.topology)
    topology.addAtom('cap-with-arbitrary-label',mm.app.element.hydrogen,topology.addResidue('X',topology.addChain()))
    info=permute_info(dict(system=physical_system(bundle),topology=topology,oldToNew=list(range(13))),
                      (9,4,1,12,8,0,11,3,7,2,13,6,10,5))
    original,spec,_=input_case()
    remapped=seal_boundary_result(original,resolve_partition(original.topology,spec),info,manifest=bundle.manifest)
    protocol=make_protocol((MobileGroup('mobile',IDS[8:],('ligand',),'ligand'),),(.3,.1,-.2))
    schedule=linear_schedule((('initial',0.),('middle',.37),('final',1.)))
    restraints=RestraintSpec('outside',('l8',),3.,(.2,.4,.1))
    a=build_atm(bundle,resolve_protocol(bundle,protocol),schedule,restraints)
    b=build_atm(remapped,resolve_protocol(remapped,protocol),schedule,restraints)
    with AtmEvaluator(a,REFERENCE) as e0,AtmEvaluator(b,REFERENCE) as e1:
        for state in ('initial','middle','final'):
            x,y=e0.evaluate(snapshot,state),e1.evaluate(snapshot,state)
            assert abs(x.total.energy_kj_mol-y.total.energy_kj_mol)<=1e-8
            assert_components(x.total.forces_kj_mol_nm,y.total.forces_kj_mol_nm)
        middle=e1.evaluate(snapshot,'middle')
        fd_sweep(lambda s:e1.evaluate(s,'middle').total.energy_kj_mol,snapshot,middle.total.forces_kj_mol_nm)
