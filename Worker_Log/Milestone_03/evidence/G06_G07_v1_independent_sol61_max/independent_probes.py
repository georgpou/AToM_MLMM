"""Additional bounded G06/G07 audit probes; no source or QM changes.

The PME reference is a vectorized lattice Ewald sum plus explicit exceptions.
The joint probe exercises the alternative isoleucine cap, two unequal ligands,
whole-molecule face seams, a changed box and total ATM directional derivatives.
"""
from dataclasses import replace
import itertools
import json
from math import erfc
from pathlib import Path

import numpy as np
import openmm as mm
from openmm import unit

HERE = Path(__file__).resolve().parent
COULOMB = 138.93545764438198


def ewald(q, x, box, alpha):
    lengths = np.diag(box); volume = float(np.prod(lengths))
    real = 0.
    for i, j in itertools.product(range(len(q)), repeat=2):
        for s in itertools.product(range(-2,3), repeat=3):
            if i == j and s == (0,0,0):
                continue
            r = np.linalg.norm(x[j]-x[i]+np.array(s)*lengths)
            real += .5*q[i]*q[j]*erfc(alpha*r)/r
    n = np.array(list(itertools.product(range(-25,26),repeat=3)))
    n = n[np.any(n,axis=1)]
    k = 2*np.pi*n/lengths
    k2 = (k*k).sum(axis=1)
    s = np.exp(1j*(k@x.T))@q
    reciprocal = 2*np.pi/volume*np.sum(np.exp(-k2/(4*alpha**2))*abs(s)**2/k2)
    return COULOMB*(real+reciprocal-alpha/np.sqrt(np.pi)*np.dot(q,q)-np.pi*q.sum()**2/(2*alpha**2*volume))


def image(d, box):
    lengths = np.diag(box)
    center = -np.floor(d/lengths).astype(int)
    alternatives = [d+(center+np.array(s))*lengths for s in itertools.product((-1,0,1),repeat=3)]
    return min(alternatives,key=lambda v:np.dot(v,v))


def exception_probe():
    from atm_mlmm.ledger import charge_mask_diagnostic, lj_mask_diagnostic
    box = np.diag((3.2,3.4,3.6))
    x = np.array(((.10,.3,.5),(3.09,.34,.52),(.63,.48,.41),(1.37,.81,.71)))
    q = np.array((.23,-.17,.11,.07)); alpha = 4.4
    system = mm.System()
    nb = mm.NonbondedForce()
    nb.setNonbondedMethod(nb.PME);nb.setCutoffDistance(.9)
    nb.setUseSwitchingFunction(True);nb.setSwitchingDistance(.75)
    nb.setUseDispersionCorrection(False);nb.setPMEParameters(alpha,64,64,64)
    for charge,sigma,eps in zip(q,(.25,.29,.33,.24),(.20,.15,.12,.08)):
        system.addParticle(12.);nb.addParticle(charge,sigma,eps)
    nb.addException(0,1,.4*q[0]*q[1],.27,.05)
    system.addForce(nb);system.setDefaultPeriodicBoxVectors(*box)
    first, second = (0,2), (1,3)
    records = []
    for periodic in (True,False):
        nb.setExceptionsUsePeriodicBoundaryConditions(periodic)
        report = charge_mask_diagnostic(system,x,box,first,second)
        # PME's real-space exclusion is the minimum-image pair; its reciprocal
        # exclusion/explicit exception uses the selected exception convention.
        electrostatic = {}
        for name,selected in (('union',first+second),('cavity',first),('ligand',second),('empty',())):
            masked = np.zeros(4);masked[list(selected)] = q[list(selected)]
            explicit_product = .4*q[0]*q[1] if 0 in selected and 1 in selected else 0.
            rmin = np.linalg.norm(image(x[1]-x[0],box))
            rex = rmin if periodic else np.linalg.norm(x[1]-x[0])
            base = ewald(masked,x,box,alpha)
            # Excluded pairs have no direct erfc term. Reciprocal subtraction
            # uses the exception distance; this expression is tested below.
            base += COULOMB*(-masked[0]*masked[1]*(erfc(alpha*rmin)/rmin+(1-erfc(alpha*rex))/rex)+explicit_product/rex)
            electrostatic[name] = base
        charge_errors = {name:abs(report['energies_kj_mol'][name]-expected) for name,expected in electrostatic.items()}
        # Preserve measurements before asserting so an oracle/convention issue
        # is distinguishable from an implementation defect.
        actual_lj = lj_mask_diagnostic(system,x,box,first,second)['cross_kj_mol']
        expected_lj = 0.
        for a,b in itertools.product(first,second):
            exceptional = {a,b} == {0,1}
            r = np.linalg.norm(x[b]-x[a] if exceptional and not periodic else image(x[b]-x[a],box))
            if exceptional:
                sigma,eps,switch = .27,.05,1.
            else:
                _,sa,ea = nb.getParticleParameters(a);_,sb,eb = nb.getParticleParameters(b)
                sigma = .5*(sa+sb).value_in_unit(unit.nanometer)
                eps = np.sqrt((ea*eb).value_in_unit(unit.kilojoule_per_mole**2))
                if r >= .9:
                    continue
                t = max(0.,(r-.75)/(.9-.75))
                switch = 1-10*t**3+15*t**4-6*t**5
            expected_lj += 4*eps*((sigma/r)**12-(sigma/r)**6)*switch
        row = dict(exceptions_periodic=periodic,masked=report,ewald_expected_kj_mol=electrostatic,
                   charge_errors_kj_mol=charge_errors,lj_actual_kj_mol=actual_lj,lj_expected_kj_mol=expected_lj,
                   lj_error_kj_mol=abs(actual_lj-expected_lj))
        records.append(row)
    with (HERE/'exception-probe-observed.json').open('x') as stream:
        json.dump(records,stream,indent=2);stream.write('\n')
    assert all(max(r['charge_errors_kj_mol'].values()) <= 1e-4 for r in records), records
    assert all(r['lj_error_kj_mol'] <= 1e-4 for r in records), records
    return records


def joint_probe():
    from atm_mlmm.adapters.atom import build_atom
    from atm_mlmm.atm import AtmEvaluator,PhysicalEvaluator,build_atm
    from atm_mlmm.endpoints import check_reference
    from atm_mlmm.model_reference import NativeMACE
    from atm_mlmm.schema import IdentityError,QualificationError
    from tests.analytic_oracle import nonlinear_answer
    from tests.joint_oracle import joint_case,protocol_case,mapped_snapshot,independent_answer,RUNTIME
    bundle,snapshot = joint_case(two_ligands=True,periodic=True,choice='alternative-ethane',row_name='butane-methanol-d3.4-r0')
    transfer,schedule,restraints = protocol_case(bundle,True)
    native = NativeMACE(); ids = snapshot.real_atom_ids
    x = np.array(snapshot.positions_nm)
    x += (snapshot.box_nm[0][0]-x[0,0]+1e-5,.11,.09)
    frame = replace(snapshot,positions_nm=np.mod(x,np.diag(snapshot.box_nm)))
    frames = [frame,replace(frame,box_nm=tuple(tuple(1.03*v for v in row) for row in frame.box_nm)),frame]
    alchemical = build_atm(bundle,transfer,schedule,restraints)
    route_records = []; fd = []; fault_checks = []
    with PhysicalEvaluator(bundle,RUNTIME) as direct,AtmEvaluator(alchemical,RUNTIME) as atm,build_atom(bundle,transfer,schedule,restraints,RUNTIME) as atom:
        for number,case in enumerate(frames):
            answers = [independent_answer(bundle,mapped_snapshot(bundle,case,i),native) for i in (0,1)]
            for mapping in (0,1):
                actual = direct.evaluate(mapped_snapshot(bundle,case,mapping))
                energy_error = abs(actual.energy_kj_mol-answers[mapping][0])
                force_error = float(np.max(abs(np.array(actual.forces_kj_mol_nm)-answers[mapping][1])))
                assert energy_error <= 1e-4 and force_error <= 5e-3
                route_records.append(dict(frame=number,route='physical',map=mapping,energy_error_kj_mol=energy_error,force_component_error_kj_mol_nm=force_error))
            for state in schedule.states:
                expression,weights,_ = nonlinear_answer(answers[0][0],answers[1][0],state.parameters)
                forces = weights[0]*answers[0][1]+weights[1]*answers[1][1]
                for route,evaluator in (('native-atm',atm),('atom',atom)):
                    result = evaluator.evaluate(case,state.state_id)
                    check_reference(result,u0=answers[0][0],u1=answers[1][0],expression=expression,outside=0.,forces=forces,energy_tolerance=1e-4,force_tolerance=5e-3)
                    route_records.append(dict(frame=number,route=route,state=state.state_id,
                        energy_error_kj_mol=abs(result.total.energy_kj_mol-expression),
                        force_component_error_kj_mol_nm=float(np.max(abs(np.array(result.total.forces_kj_mol_nm)-forces)))))
                    if number == 0 and state.state_id == 'middle':
                        for mode,badforce in (('factor-ten',forces*10),('omit-mm-parent',forces.copy())):
                            if mode == 'omit-mm-parent':badforce[ids.index(bundle.links[0].mm_parent_id)]=0
                            try:
                                check_reference(result,u0=answers[0][0],u1=answers[1][0],expression=expression,outside=0.,forces=badforce,energy_tolerance=1e-4,force_tolerance=5e-3)
                            except QualificationError as exc:
                                fault_checks.append(dict(route=route,mode=mode,caught=str(exc)))
                            else:
                                raise AssertionError('fault was not detected: '+mode)
        case = frame
        total = atm.evaluate(case,'middle').total
        direction = np.array((.31,-.47,.826));direction /= np.linalg.norm(direction)
        atoms = tuple(dict.fromkeys((bundle.links[0].ml_parent_id,bundle.links[0].mm_parent_id,ids[0],'a:l0','b:l0')))
        for a in atoms:
            i = ids.index(a);expected = float(np.dot(total.forces_kj_mol_nm[i],direction))
            estimates = []
            for h in (1e-3,1e-4,1e-5,1e-6):
                energies = []
                for sign in (1,-1):
                    moved = np.array(case.positions_nm);moved[i] += sign*h*direction
                    energies.append(atm.evaluate(replace(case,positions_nm=moved),'middle').total.energy_kj_mol)
                estimates.append(-(energies[0]-energies[1])/(2*h))
            errors = [abs(v-expected) for v in estimates]
            assert errors[-1] <= 1e-3+1e-4*abs(expected), (a,expected,estimates)
            assert errors[-1] <= errors[0]+1e-4
            fd.append(dict(atom_id=a,direction=direction.tolist(),steps_nm=[1e-3,1e-4,1e-5,1e-6],
                reference_force_kj_mol_nm=expected,finite_difference_forces_kj_mol_nm=estimates,errors_kj_mol_nm=errors))
    wrong_maps = list(transfer.displacement1_nm)
    for i,a in enumerate(ids):
        if a.startswith('b:'):
            wrong_maps[bundle.real_to_final[a]] = tuple(-v for v in wrong_maps[bundle.real_to_final[a]])
    try:
        build_atm(bundle,replace(transfer,displacement1_nm=wrong_maps),schedule,restraints)
    except IdentityError as exc:
        fault_checks.append(dict(mode='wrong-second-ligand-sign',caught=str(exc)))
    else:
        raise AssertionError('wrong second-ligand map admitted')
    return dict(fixture='isoleucine alternative C-beta-C-gamma1 cap, two unequal complete ligands',
        reviewed_physical_identity=bundle.content_identity,stationary_links=[l.cap_id for l in bundle.links],
        cap_distance_nm=bundle.links[0].distance_nm,ligand_sizes=[len(m.atom_ids) for m in bundle.topology.molecules if m.role=='ligand'],
        original_snapshot=json.loads(__import__('atm_mlmm.schema',fromlist=['to_json']).to_json(snapshot)),
        preserved_wrapped_snapshot=json.loads(__import__('atm_mlmm.schema',fromlist=['to_json']).to_json(frame)),
        changed_box_nm=frames[1].box_nm,route_comparisons=route_records,directional_derivatives=fd,
        deliberate_fault_rejections=fault_checks)


def geometry_negatives():
    from atm_mlmm.geometry import unwrap_molecules,validate_bulk_clearance
    from atm_mlmm.schema import AtomIdentity,Bond,MoleculeState,TopologyView,NumericalDomainError
    atoms = tuple(AtomIdentity(a,'C','A','1','',a) for a in ('x','y','z'))
    topology = TopologyView(atoms,(Bond('x','y'),Bond('y','z'),Bond('z','x')),
                            (MoleculeState('cycle',('x','y','z'),'protein',0,1),))
    box = np.diag((3.,3.,3.)); rejections = []
    try:
        unwrap_molecules(topology,((0.,0.,0.),(1.,0.,0.),(2.,0.,0.)),box)
    except NumericalDomainError as exc:
        rejections.append(dict(mode='winding-cycle',caught=str(exc)))
    else:
        raise AssertionError('winding cycle admitted')
    try:
        validate_bulk_clearance([[1.,1.,1.]],[[2.3,2.3,2.3]],[],box,cutoff_nm=.45,other_ligands_nm=[[1.1,1.,1.]])
    except NumericalDomainError as exc:
        rejections.append(dict(mode='second-ligand-reconnection',caught=str(exc)))
    else:
        raise AssertionError('other-ligand contact admitted')
    return rejections


def main():
    result = dict(exception_probe=exception_probe(),geometry_rejections=geometry_negatives(),joint=joint_probe(),new_quantum_runs=0)
    with (HERE/'independent-probes.json').open('x') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print('Two periodic/nonperiodic-exception mask and switched-LJ checks passed.')
    print('24 alternative-cap periodic direct/native/AToM route comparisons passed; five directional derivative sweeps passed.')
    print('Geometry rejections and five deliberate force/map faults detected.')


if __name__ == '__main__':
    main()
