"""Independent Cartesian spring/mixing oracle and full-coordinate FD sweeps.

Inputs come from the frozen fixture; expected energies/maps/negative gradients
do not call production callbacks, mapping helpers, mixers or test oracles.
"""
from dataclasses import replace
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import openmm as mm
from openmm import unit

from atm_mlmm.adapters.atom import build_atom
from atm_mlmm.analytic import make_analytic_bundle
from atm_mlmm.atm import AtmEvaluator, PhysicalEvaluator, build_atm
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.protocols import abfe, rbfe
from atm_mlmm.routing import check_active_forces
from atm_mlmm.schema import (AtomIdentity, Bond, MobileGroup, MoleculeState,
                             RestraintSpec, RuntimeSpec, Snapshot, TopologyView)
from atm_mlmm.schedule import linear_schedule, production_schedule

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
data = json.loads((ROOT/'fixtures/analytic/transfer-v1.json').read_text())
ids = tuple(data['real_ids'])
topology = TopologyView(tuple(AtomIdentity(a, 'C', str(i), '1', '', a) for i,a in enumerate(ids)),
                        (Bond('a1','a2'), Bond('b1','b2'), Bond('b1','b3')),
                        (MoleculeState('A',('a1','a2'),'ligand',0,1),
                         MoleculeState('B',('b1','b2','b3'),'ligand',0,1),
                         MoleculeState('P',('protein',),'protein',0,1),
                         MoleculeState('E',('env',),'environment',0,1)))
position = np.asarray(data['positions_nm'], dtype=float)
position += np.array([[.017,-.022,.013],[-.081,.036,-.027],[.012,.031,-.018],
                     [-.013,.027,.019],[.033,-.041,.012],[.017,.009,-.016],[-.009,.013,.022]])
snapshot = Snapshot(ids, position, None)
permutation = (6,2,4,0,5,1,3)
restraints = RestraintSpec('independent:outside', ('env','protein'),9.,(.1,0.,0.))
base_parameters = dict(Lambda1=.17,Lambda2=.83,Alpha=.9,Uh=1.7,W0=-.4,Umax=9.,Ubcore=1.,
                       Acore=.3,Direction=1.,UOffset=.35)
linear = linear_schedule((('zero',0.),('middle',.37),('one',1.)))
production = production_schedule((('forward',base_parameters),
                                  ('reverse',{**base_parameters,'Direction':-1.,'W0':.7})))
records = []
fd_rows = []
history = []


def spring_answer(coordinates, environment):
    energy, force = 0., np.zeros((7,3))
    for i,k,center in ((2,6.,(.1,-.1,.2)),(0,14.,(-.2,.2,0.)),(3,3.,(.05,-.15,.2)),
                       (6,5.,(.2,.1,0.)),(5,7.,(-.2,0.,.1)),(4,2000.,(-.3,.2,.1))):
        for axis in range(3):
            delta = coordinates[i,axis]-center[axis]
            energy += k*delta*delta/2
            force[i,axis] -= k*delta
    if environment:
        delta = coordinates[2]-coordinates[1]
        energy += 5.*sum(delta*delta)
        force[2] -= 10.*delta
        force[1] += 10.*delta
    return energy, force


def outside_answer(coordinates):
    energy, force = 0., np.zeros((7,3))
    for i in (1,4):
        delta = coordinates[i]-(.1,0.,0.)
        energy += 4.5*sum(delta*delta)
        force[i] -= 9.*delta
    return energy, force


def mixer(u0,u1,p):
    directed = p['Direction']*(u1-u0-p['UOffset'])
    soft, derivative = directed, 1.
    if p['Acore'] and directed > p['Ubcore']:
        span = p['Umax']-p['Ubcore']
        q = (directed-p['Ubcore'])/(span*p['Acore'])
        z = 1+2*q+2*q*q
        tangent = math.tanh(.5*p['Acore']*math.log(z))
        soft = p['Ubcore']+span*tangent
        derivative = (1+2*q)*(1-tangent*tangent)/z
    alpha, difference = p['Alpha'], p['Lambda2']-p['Lambda1']
    arg = alpha*(soft-p['Uh'])
    bias = p['Lambda2']*soft+p['W0']
    weight = p['Lambda2']
    if difference:
        bias += difference*np.logaddexp(0.,-arg)/alpha
        weight -= difference*np.exp(-np.logaddexp(0.,arg))
    weight *= derivative
    return ((u0+bias,(1-weight,weight),soft) if p['Direction']>0 else
            (u1+bias,(weight,1-weight),soft))


def expected(kind,environment,schedule,state,coords):
    mapped = coords+np.asarray(data[kind+'_map1_nm'])
    u0,f0 = spring_answer(coords,environment)
    u1,f1 = spring_answer(mapped,environment)
    outside,fk = outside_answer(coords)
    if schedule.kind == 'linear':
        lam = state.parameters['Lambda']
        expression, weights, soft = u0+lam*(u1-u0),(1-lam,lam),u1-u0
    else:
        expression,weights,soft = mixer(u0,u1,state.parameters)
    return np.array((u0,u1,expression,outside,expression+outside,soft)), weights[0]*f0+weights[1]*f1+fk


def verify(actual,values,forces):
    observed = np.array((actual.raw.u0_raw_kJ_mol,actual.raw.u1_raw_kJ_mol,
                         actual.raw.atm_expression_energy_kJ_mol,actual.raw.outside_energy_kJ_mol,
                         actual.total.energy_kj_mol,actual.raw.delta_u_softcore_kJ_mol))
    ee = float(max(abs(observed-values)))
    fe = float(np.max(np.abs(np.asarray(actual.total.forces_kj_mol_nm)-forces)))
    assert ee<=1e-8 and fe<=1e-7,(ee,fe)
    assert actual.total.real_atom_ids==ids and actual.total.units.forces=='kJ/mol/nm'
    return dict(max_energy_error=ee,max_force_component_error=fe,outside=values[3],
                u0=observed[0],u1=observed[1])


for platform in ('Reference','CPU'):
    runtime = RuntimeSpec(platform,'double',(),.0005,300.,'NVT')
    for environment in (False,True):
        physical = make_analytic_bundle(topology,ml_atom_ids=tuple(a for a in ids if a!='env'),
            masses_da=data['masses_da'],selected_particles=(2,0),spring_constants=(6.,14.),
            centers_nm=((.1,-.1,.2),(-.2,.2,0.)),environment_pairs=(('a1','env',10.),) if environment else (),
            additional_harmonics=(((3,6,5),(3.,5.,7.),((.05,-.15,.2),(.2,.1,0.),(-.2,0.,.1))),),
            marker_k=2000.,old_to_new=permutation)
        for kind in ('abfe','rbfe'):
            groups = (MobileGroup('A-mobile',('a1','a2'),('ligand',),'A'),)
            if kind=='rbfe':
                groups += (MobileGroup('B-mobile',('b1','b2','b3'),('ligand',),'B'),)
            protocol = (abfe if kind=='abfe' else rbfe).make_protocol(groups,data['displacement_nm'])
            transfer = resolve_protocol(physical,protocol)
            for old,new in enumerate(permutation):
                assert transfer.displacement1_nm[new]==tuple(data[kind+'_map1_nm'][old])
            with PhysicalEvaluator(physical,runtime) as direct:
                for endpoint in (0,1):
                    mapped = position+(np.asarray(data[kind+'_map1_nm']) if endpoint else 0.)
                    expected_energy, expected_force = spring_answer(mapped,environment)
                    actual = direct.evaluate(replace(snapshot,positions_nm=mapped))
                    assert abs(actual.energy_kj_mol-expected_energy)<=1e-8
                    assert np.max(abs(np.asarray(actual.forces_kj_mol_nm)-expected_force))<=1e-7
            for schedule in (linear,production):
                native = build_atm(physical,transfer,schedule,restraints)
                with AtmEvaluator(native,runtime) as evaluator:
                    for state in schedule.states:
                        values,forces = expected(kind,environment,schedule,state,position)
                        records.append(dict(platform=platform,environment=environment,kind=kind,
                            physical_identity=physical.content_identity,schedule=schedule.kind,state=state.state_id,
                            route='native',**verify(evaluator.evaluate(snapshot,state.state_id),values,forces)))
            with build_atom(physical,transfer,production,restraints,runtime) as run:
                for state in production.states:
                    values,forces = expected(kind,environment,production,state,position)
                    actual = run.evaluate(snapshot,state.state_id)
                    records.append(dict(platform=platform,environment=environment,kind=kind,
                        physical_identity=physical.content_identity,schedule='softplus',state=state.state_id,
                        route='upstream',**verify(actual,values,forces),mask=check_active_forces(run.evaluator.context,run.evaluator.integrator)))
                bcoords = position.copy(); bcoords[1]+=(.071,-.047,.039)
                first = run.evaluate(snapshot,'forward')
                middle = run.evaluate(replace(snapshot,positions_nm=bcoords),'forward')
                last = run.evaluate(snapshot,'forward')
                assert first==last and first!=middle
                history.append(dict(platform=platform,environment=environment,kind=kind,aba=True,mm_energy_change=middle.total.energy_kj_mol-first.total.energy_kj_mol))
                # All 21 real components at each admitted initial FD step.
                values,forces = expected(kind,environment,production,production.states[0],position)
                errors=[]
                for h in (1e-3,1e-4,1e-5):
                    fd=np.empty((7,3))
                    for i in range(7):
                        for axis in range(3):
                            a,b=position.copy(),position.copy();a[i,axis]+=h;b[i,axis]-=h
                            ep=run.evaluate(replace(snapshot,positions_nm=a),'forward').total.energy_kj_mol
                            em=run.evaluate(replace(snapshot,positions_nm=b),'forward').total.energy_kj_mol
                            fd[i,axis]=-(ep-em)/(2*h)
                    errors.append(float(np.max(abs(fd-forces))))
                assert errors[-1]<=1e-5 and errors[-1]<=errors[0]+1e-8,errors
                fd_rows.append(dict(platform=platform,environment=environment,kind=kind,steps_nm=[1e-3,1e-4,1e-5],max_component_errors=errors))

# Independently vary only the offset to straddle the soft-core transition and
# place the softened perturbation directly at the softplus transition.
for direction in (1.,-1.):
    for target in (.999,1.,1.001,1.7,6.):
        u0,f0=spring_answer(position,True)
        u1,f1=spring_answer(position+np.asarray(data['rbfe_map1_nm']),True)
        params={**base_parameters,'Direction':direction,'UOffset':u1-u0-direction*target}
        schedule=production_schedule((('transition',params),))
        _,_,soft=mixer(u0,u1,params)
        params['Uh']=soft
        schedule=production_schedule((('transition',params),))
        transfer=resolve_protocol(physical,rbfe.make_protocol(groups,data['displacement_nm']))
        with AtmEvaluator(build_atm(physical,transfer,schedule,restraints),runtime) as evaluator:
            values,forces=expected('rbfe',True,schedule,schedule.states[0],position)
            records.append(dict(platform=platform,environment=True,kind='rbfe',schedule='transition',state=str((direction,target)),route='native',**verify(evaluator.evaluate(snapshot,'transition'),values,forces)))

report=dict(review_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    fixture='transfer-v1; independent perturbed geometry and nonidentity final map',
    oracle='Cartesian negative gradients plus tanh/logaddexp soft-core/softplus differentiation; no test-oracle imports',
    cases=records,fd=fd_rows,upstream_history=history,
    maximum_energy_error=max(row['max_energy_error'] for row in records),
    maximum_force_error=max(row['max_force_component_error'] for row in records),
    maximum_final_fd_error=max(row['max_component_errors'][-1] for row in fd_rows))
(OUT/'independent-numerics.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:report[k] for k in ('maximum_energy_error','maximum_force_error','maximum_final_fd_error')}))
print('cases',len(records),'full-coordinate FD sweeps',len(fd_rows),'upstream A-B-A',len(history))
