"""G07 composition assertions at actual complete-ligand and cap coordinates."""
from dataclasses import replace
import numpy as np
import pytest
from tests.joint_oracle import (joint_case,joint_input,protocol_case,independent_answer,
                               mapped_snapshot,RUNTIME,DISPLACEMENT)


def test_uncut_reference_description_uses_same_builder():
    bundle,snapshot = joint_case(choice='uncut')
    assert not bundle.links
    assert set(bundle.ml_atom_ids) == set(snapshot.real_atom_ids)
    assert len(bundle.masses_da) == len(snapshot.real_atom_ids)


@pytest.mark.model_assets
@pytest.mark.parametrize('two_ligands',(False,))
def test_direct_native_and_atom_agree(two_ligands):
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import PhysicalEvaluator,AtmEvaluator,build_atm
    from atm_mlmm.endpoints import check_reference
    from atm_mlmm.model_reference import NativeMACE
    from tests.analytic_oracle import nonlinear_answer
    bundle,snapshot = joint_case(two_ligands=two_ligands)
    transfer,schedule,restraints = protocol_case(bundle,two_ligands)
    native = NativeMACE()
    answers = [independent_answer(bundle,mapped_snapshot(bundle,snapshot,i),native) for i in (0,1)]
    runtime = RUNTIME
    with PhysicalEvaluator(bundle,runtime) as direct:
        for i in (0,1):
            actual = direct.evaluate(mapped_snapshot(bundle,snapshot,i))
            assert abs(actual.energy_kj_mol-answers[i][0]) <= 1e-4
            np.testing.assert_allclose(actual.forces_kj_mol_nm,answers[i][1],atol=5e-3,rtol=0)
    atm = build_atm(bundle,transfer,schedule,restraints)
    with AtmEvaluator(atm,runtime) as evaluator,build_atom(bundle,transfer,schedule,restraints,runtime) as atom:
        for state in schedule.states:
            expression,weights,_ = nonlinear_answer(answers[0][0],answers[1][0],state.parameters)
            forces = weights[0]*answers[0][1]+weights[1]*answers[1][1]
            for result in (evaluator.evaluate(snapshot,state.state_id),atom.evaluate(snapshot,state.state_id)):
                check_reference(result,u0=answers[0][0],u1=answers[1][0],expression=expression,outside=0.,
                    forces=forces,energy_tolerance=1e-4,force_tolerance=5e-3)
        first = atom.evaluate(snapshot,'map0')
        atom.evaluate(snapshot,'map1')
        again = atom.evaluate(snapshot,'map0')
        assert abs(first.total.energy_kj_mol-again.total.energy_kj_mol) <= 1e-4
        np.testing.assert_allclose(first.total.forces_kj_mol_nm,again.total.forces_kj_mol_nm,atol=5e-3,rtol=0)


@pytest.mark.model_assets
def test_real_model_two_unequal_ligand_single_points():
    # Stable G07-07 node preserves the complete unequal-group comparison.
    test_direct_native_and_atom_agree(True)


@pytest.mark.model_assets
def test_mm_boundary_parent_force():
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.model_reference import NativeMACE
    bundle,snapshot = joint_case()
    native = NativeMACE()
    link, = bundle.links
    parent = snapshot.real_atom_ids.index(link.mm_parent_id)
    with PhysicalEvaluator(bundle,RUNTIME) as evaluator:
        for mapping in (0,1):
            frame = mapped_snapshot(bundle,snapshot,mapping)
            energy,force,_ = independent_answer(bundle,frame,native)
            actual = evaluator.evaluate(frame)
            np.testing.assert_allclose(actual.forces_kj_mol_nm,force,atol=5e-3,rtol=0)
            for axis in range(3):
                estimates = []
                for step in (1e-3,1e-4,1e-5,1e-6):
                    energies = []
                    for sign in (1,-1):
                        x = np.array(frame.positions_nm);x[parent,axis] += step*sign
                        energies.append(evaluator.evaluate(replace(frame,positions_nm=x)).energy_kj_mol)
                    estimates.append(-(energies[0]-energies[1])/(2*step))
                assert abs(estimates[-1]-force[parent,axis]) <= 1e-3+1e-4*abs(force[parent,axis])


@pytest.mark.model_assets
def test_joint_contact_and_disconnected_graph():
    from atm_mlmm.model_reference import NativeMACE
    from tests.model_oracle import derived_input
    bundle,snapshot = joint_case()
    native = NativeMACE()
    membership = tuple(bundle.model_input_ids)
    energies = []
    for mapping in (0,1):
        frame = mapped_snapshot(bundle,snapshot,mapping)
        n,x,_ = derived_input(bundle,frame)
        out = native.evaluate(n,x)
        ligand = {i for i,a in enumerate(membership) if a.startswith('a:')}
        cross = [(i,j) for i,j in out['directed_edges'] if (i in ligand)!=(j in ligand)]
        assert bool(cross) == (mapping==0)
        indices = (sorted(ligand),[i for i in range(len(n)) if i not in ligand])
        parts = [native.evaluate(np.array(n)[part],x[part]) for part in indices]
        energies.append(out['energy_kj_mol'])
        if mapping: assert abs(out['energy_kj_mol']-sum(p['energy_kj_mol'] for p in parts)) <= 1e-4
        else: assert abs(out['energy_kj_mol']-sum(p['energy_kj_mol'] for p in parts)) > 1e-4
        assert bundle.model_input_ids == membership
    assert abs(energies[0]-energies[1]) > 1e-4


@pytest.mark.parametrize('two_ligands',(False,True))
def test_only_mobile_groups_translate(two_ligands):
    bundle,snapshot = joint_case(two_ligands=two_ligands,real_model=False,environment=True)
    transfer,_,_ = protocol_case(bundle,two_ligands)
    for atom in bundle.topology.atoms:
        expected = DISPLACEMENT if atom.atom_id.startswith('a:') else tuple(-v for v in DISPLACEMENT) if atom.atom_id.startswith('b:') else (0.,0.,0.)
        assert transfer.displacement1_nm[bundle.real_to_final[atom.atom_id]] == expected
    for link in bundle.links:
        assert transfer.displacement1_nm[link.final_particle_index] == (0.,0.,0.)
        assert transfer.displacement1_nm[bundle.real_to_final[link.ml_parent_id]] == (0.,0.,0.)
        assert transfer.displacement1_nm[bundle.real_to_final[link.mm_parent_id]] == (0.,0.,0.)
    if two_ligands:
        assert [len(g.atom_ids) for g in transfer.protocol.mobile_groups] == [6,9]


@pytest.mark.model_assets
@pytest.mark.parametrize('two_ligands',(False,True))
def test_joint_periodic_geometry_and_forces(two_ligands):
    from atm_mlmm.model_reference import NativeMACE
    from atm_mlmm.atm import AtmEvaluator,PhysicalEvaluator,build_atm
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.endpoints import check_reference
    from tests.analytic_oracle import nonlinear_answer
    bundle,snapshot = joint_case(two_ligands=two_ligands,periodic=True)
    transfer,schedule,restraints = protocol_case(bundle,two_ligands)
    native = NativeMACE()
    answers = [independent_answer(bundle,mapped_snapshot(bundle,snapshot,i),native) for i in (0,1)]
    with PhysicalEvaluator(bundle,RUNTIME) as direct:
        for i in (0,1):
            frame = mapped_snapshot(bundle,snapshot,i)
            a = direct.evaluate(frame)
            assert abs(a.energy_kj_mol-answers[i][0]) <= 1e-4
            np.testing.assert_allclose(a.forces_kj_mol_nm,answers[i][1],atol=5e-3,rtol=0)
            wrapped = replace(frame,positions_nm=np.mod(frame.positions_nm,np.diag(frame.box_nm)))
            b = direct.evaluate(wrapped)
            assert abs(a.energy_kj_mol-b.energy_kj_mol) <= 1e-4
            np.testing.assert_allclose(a.forces_kj_mol_nm,b.forces_kj_mol_nm,atol=5e-3,rtol=0)
    atm = build_atm(bundle,transfer,schedule,restraints)
    with AtmEvaluator(atm,RUNTIME) as evaluator,build_atom(bundle,transfer,schedule,restraints,RUNTIME) as atom:
        for state in schedule.states:
            expression,weights,_ = nonlinear_answer(answers[0][0],answers[1][0],state.parameters)
            force = weights[0]*answers[0][1]+weights[1]*answers[1][1]
            for result in (evaluator.evaluate(snapshot,state.state_id),atom.evaluate(snapshot,state.state_id)):
                check_reference(result,u0=answers[0][0],u1=answers[1][0],expression=expression,outside=0.,forces=force,
                                energy_tolerance=1e-4,force_tolerance=5e-3)


@pytest.mark.model_assets
def test_periodic_full_real_derivative_step_sweep():
    from atm_mlmm.atm import PhysicalEvaluator
    bundle,snapshot = joint_case(periodic=True)
    ids = snapshot.real_atom_ids
    indices = [ids.index(a) for a in ('p4','p5','p0','a:l0')]
    with PhysicalEvaluator(bundle,RUNTIME) as evaluator:
        for mapping in (0,1):
            frame = mapped_snapshot(bundle,snapshot,mapping)
            actual = evaluator.evaluate(frame)
            errors,reference = [],[]
            for i in indices:
                for axis in range(3):
                    estimates = []
                    for step in (1e-3,1e-4,1e-5,1e-6):
                        values=[]
                        for sign in (1,-1):
                            x=np.array(frame.positions_nm);x[i,axis]+=sign*step
                            values.append(evaluator.evaluate(replace(frame,positions_nm=x)).energy_kj_mol)
                        estimates.append(-(values[0]-values[1])/(2*step))
                    expected=actual.forces_kj_mol_nm[i][axis]
                    error=abs(estimates[-1]-expected)
                    assert error <= 1e-3+1e-4*abs(expected),(ids[i],axis,estimates,expected)
                    assert error <= abs(estimates[0]-expected)+1e-4
                    errors.append(error);reference.append(expected)
            assert np.sqrt(np.mean(np.square(errors))) <= 1e-3+1e-4*np.sqrt(np.mean(np.square(reference)))
