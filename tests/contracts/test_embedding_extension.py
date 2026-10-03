"""G07-05: swap only physical provider; both protocols/engines keep full forces."""
from dataclasses import dataclass,replace
import pickle
import xml.etree.ElementTree as ET
import numpy as np
import openmm as mm
from openmm import unit
import pytest
from tests.joint_oracle import (joint_case,protocol_case,independent_answer,mapped_snapshot,RUNTIME)


@dataclass
class FaultyFullCap:
    normal: object
    selected: tuple
    parents: tuple
    cap_final: int
    distance: float
    mode: str

    def __call__(self,state):
        x = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        selected = x[list(self.selected)]
        class Positions:
            def getPositions(self,asNumpy=False): return selected*unit.nanometer
        energy,raw = self.normal(Positions())
        f = np.zeros_like(x);f[list(self.selected)] = raw
        if self.mode == 'omit-cap': f[self.cap_final] = 0.
        elif self.mode == 'omit-environment': f[self.selected[self.normal.environment_index]] = 0.
        elif self.mode == 'double-parent':
            a,b = self.parents;v = x[b]-x[a];length=np.linalg.norm(v);n=v/length
            jac = self.distance/length*(np.eye(3)-np.outer(n,n))
            cap = f[self.cap_final].copy()
            f[a] += (np.eye(3)-jac).T@cap;f[b] += jac.T@cap
        return energy,f


@pytest.mark.parametrize('two_ligands',(False,True))
@pytest.mark.parametrize('environment',(False,True))
def test_environment_provider_reuses_atm_and_protocols(two_ligands,environment):
    from atm_mlmm.atm import AtmEvaluator,build_atm
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.endpoints import check_reference
    from tests.analytic_oracle import nonlinear_answer
    bundle,snapshot = joint_case(two_ligands=two_ligands,environment=environment,real_model=False)
    transfer,schedule,restraints = protocol_case(bundle,two_ligands)
    answers = [independent_answer(bundle,mapped_snapshot(bundle,snapshot,i),probe=environment) for i in (0,1)]
    atm = build_atm(bundle,transfer,schedule,restraints)
    with AtmEvaluator(atm,RUNTIME) as native,build_atom(bundle,transfer,schedule,restraints,RUNTIME) as atom:
        for state in schedule.states:
            energy,weights,_ = nonlinear_answer(answers[0][0],answers[1][0],state.parameters)
            f = weights[0]*answers[0][1]+weights[1]*answers[1][1]
            for evaluator in (native,atom):
                check_reference(evaluator.evaluate(snapshot,state.state_id),u0=answers[0][0],u1=answers[1][0],
                    expression=energy,outside=0.,forces=f,energy_tolerance=1e-4,force_tolerance=5e-3)
        # Move the real MM environment without moving the cap's parents/ligands.
        x = np.asarray(snapshot.positions_nm).copy();x[0]+=(.07,-.03,.02)
        moved = replace(snapshot,positions_nm=x)
        for evaluator in (native,atom):
            a = evaluator.evaluate(snapshot,'map0')
            b = evaluator.evaluate(moved,'map0')
            c = evaluator.evaluate(snapshot,'map0')
            assert abs(b.total.energy_kj_mol-a.total.energy_kj_mol) > 1e-4
            assert abs(c.total.energy_kj_mol-a.total.energy_kj_mol) <= 1e-4
            np.testing.assert_allclose(c.total.forces_kj_mol_nm,a.total.forces_kj_mol_nm,atol=5e-3,rtol=0)


@pytest.mark.parametrize('mode',('omit-cap','omit-environment','double-parent'))
@pytest.mark.parametrize('two_ligands',(False,True))
def test_joint_checker_detects_cap_and_environment_faults(mode,two_ligands):
    from atm_mlmm.atm import physical_system,AtmEvaluator,build_atm
    from atm_mlmm.endpoints import check_reference
    from atm_mlmm.schema import QualificationError
    from tests.workflow.test_atom_force_routing import replace_system
    from tests.analytic_oracle import nonlinear_answer
    bundle,snapshot = joint_case(two_ligands=two_ligands,environment=True,real_model=False)
    system = physical_system(bundle)
    index = next(i for i,f in enumerate(system.getForces()) if isinstance(f,mm.PythonForce))
    original = system.getForce(index)
    # This is our own ledger-verified trusted callback, never an external pickle.
    normal = pickle.loads(bytes.fromhex(ET.fromstring(mm.XmlSerializer.serialize(original)).get('function')))
    link, = bundle.links
    faulty = mm.PythonForce(FaultyFullCap(normal,tuple(original.getParticles()),
        (bundle.real_to_final[link.ml_parent_id],bundle.real_to_final[link.mm_parent_id]),
        link.final_particle_index,link.distance_nm,mode))
    faulty.setForceGroup(original.getForceGroup());faulty.setName(original.getName())
    system.removeForce(index);system.addForce(faulty)
    bad = replace_system(bundle,system)
    transfer,schedule,restraints = protocol_case(bad,two_ligands)
    answers = [independent_answer(bundle,mapped_snapshot(bundle,snapshot,i),probe=True) for i in (0,1)]
    atm = build_atm(bad,transfer,schedule,restraints)
    with AtmEvaluator(atm,RUNTIME) as evaluator:
        for state in schedule.states:
            energy,weights,_ = nonlinear_answer(answers[0][0],answers[1][0],state.parameters)
            f = weights[0]*answers[0][1]+weights[1]*answers[1][1]
            with pytest.raises(QualificationError,match='force mismatch'):
                check_reference(evaluator.evaluate(snapshot,state.state_id),u0=answers[0][0],u1=answers[1][0],
                    expression=energy,outside=0.,forces=f,energy_tolerance=1e-4,force_tolerance=5e-3)
