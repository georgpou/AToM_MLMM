"""Independent G08 audit probes; no worker test helper or arithmetic imported."""
from dataclasses import replace
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import traceback

import numpy as np
from scipy.integrate import quad, cumulative_trapezoid

from atm_mlmm.analysis import analyze, combine_free_energies, directional_difference, estimate_free_energies
from atm_mlmm.restraints import finite_wall_volume_nm3, translational_standard_state_correction
from atm_mlmm.schedule import linear_schedule, production_schedule, reduced_potentials
from atm_mlmm.schema import (BindingResult, CorrectionRecord, EvaluationRecords, ThermodynamicSpec,
                             STANDARD_CORRECTION_OBLIGATIONS, from_json, to_json)

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RT = .00831446261815324*300.
REPORT = {'positives': [], 'required_rejections': [], 'findings': [], 'failures': [], 'metrics': {}}

def check(name, action):
    try:
        value = action()
        REPORT['positives'].append(name)
        if value is not None:
            REPORT['metrics'][name] = value
        print('PASS', name, flush=True)
    except Exception as exc:
        REPORT['failures'].append({'name': name, 'type': type(exc).__name__, 'error': str(exc), 'traceback': traceback.format_exc()})
        print('FAIL', name, type(exc).__name__, str(exc), flush=True)

def reject(name, action):
    try:
        result = action()
    except (ValueError, ArithmeticError) as exc:
        REPORT['required_rejections'].append({'name': name, 'type': type(exc).__name__, 'error': str(exc)})
        return
    REPORT['findings'].append({'name': name, 'result': repr(result), 'problem': 'required rejection was admitted'})
    print('ADMITTED', name, flush=True)
    return result

def spec(ids, *, standard=False, corrections=()):
    return ThermodynamicSpec('standard_binding_free_energy' if standard else 'restrained_free_energy',
                             {ids[0]: -1., ids[-1]: 1.}, 'bound_minus_bulk' if standard else 'endpoint_difference',
                             tuple(zip(ids[:-1], ids[1:])), {ids[0]: 'bulk/first', ids[-1]: 'bound/last'},
                             STANDARD_CORRECTION_OBLIGATIONS if standard else (), corrections,
                             1.6605390671738466 if standard else None,
                             'Separable infinite-space bulk translation; explicit bound domain',
                             'Independent analytic restraints', 'No orientation factor for one coordinate',
                             'One pose, unit symmetry, explicit state-counting proof')

def records(schedule, sampled, raw, *, mode='independent', prefix='oracle'):
    counters, seq = {}, []
    for state in sampled:
        seq.append(counters.get(state, 0))
        counters[state] = counters.get(state, 0)+1
    raw = np.asarray(raw)
    return EvaluationRecords(schedule, tuple(f'{prefix}-{i}' for i in range(len(sampled))), tuple(sampled),
                             tuple(prefix+'-walker-'+s for s in sampled), tuple(seq),
                             *(tuple(raw[:,j]) for j in range(4)),
                             'independent-physical-oracle', 'independent-fixed-translation', 'independent-restraint',
                             {'source': str(Path(__file__).resolve()), 'seed': prefix}, mode)

def parameters(**changes):
    p = dict(Lambda1=.13, Lambda2=.79, Alpha=.63, Uh=1.1, W0=.37,
             Umax=19., Ubcore=2.5, Acore=.42, Direction=1., UOffset=-1.7)
    p.update(changes)
    return p

def independent_expression(u0, u1, outside, p):
    delta = p['Direction']*(u1-u0-p['UOffset'])
    if p['Acore'] != 0 and delta > p['Ubcore']:
        ratio = (delta-p['Ubcore'])/(p['Umax']-p['Ubcore'])/p['Acore']
        power = (1+2*ratio+2*ratio*ratio)**p['Acore']
        delta = p['Ubcore']+(p['Umax']-p['Ubcore'])*(power-1)/(power+1)
    result = (u0 if p['Direction'] > 0 else u1)+outside+p['Lambda2']*delta+p['W0']
    if p['Lambda2'] != p['Lambda1']:
        t = -p['Alpha']*(delta-p['Uh'])
        softplus = max(t, 0)+math.log1p(math.exp(-abs(t)))
        result += (p['Lambda2']-p['Lambda1'])*softplus/p['Alpha']
    return result

def harmonic_data(k=100., kr=50., d=.3, temperature=300., count=5000, seed=424242, mode='independent'):
    rt = .00831446261815324*temperature
    lambdas = np.linspace(0., 1., 9)
    names = tuple(f'h{i}' for i in range(len(lambdas)))
    schedule = linear_schedule(tuple(zip(names, lambdas)), temperature_K=temperature)
    rng = np.random.default_rng(seed)
    raw, sampled = [], []
    for name, lam in zip(names, lambdas):
        mean, sigma = -lam*k*d/(k+kr), math.sqrt(rt/(k+kr))
        if mode == 'correlated':
            xs = np.empty(count)
            xs[0] = rng.normal(mean, sigma)
            for i in range(1, count):
                xs[i] = mean+.88*(xs[i-1]-mean)+math.sqrt(1-.88**2)*sigma*rng.normal()
        else:
            xs = rng.normal(mean, sigma, count)
        for x in xs:
            u0, u1, outside = .5*k*x*x, .5*k*(x+d)**2, .5*kr*x*x
            raw.append((u0, u1, outside, (1-lam)*u0+lam*u1+outside))
            sampled.append(name)
    return records(schedule, sampled, raw, mode=mode, prefix=str(seed)), names, lambdas

def known_answer():
    output = []
    for kr, temperature in ((50.,300.), (0.,300.), (23.,317.)):
        data, names, lambdas = harmonic_data(kr=kr, temperature=temperature, seed=9100+int(kr))
        rt = .00831446261815324*temperature
        integrals = np.array([quad(lambda x: math.exp(-(.5*100*((1-lam)*x*x+lam*(x+.3)**2)+.5*kr*x*x)/rt),
                                  -np.inf, np.inf, epsabs=1.e-13, epsrel=1.e-12)[0] for lam in lambdas])
        curve = .5*lambdas*100*.3**2-.5*lambdas**2*(100*.3)**2/(100+kr)
        reference = -rt*np.log(integrals/integrals[0])
        np.testing.assert_allclose(reference, curve, atol=1.e-10, rtol=0)
        fit = estimate_free_energies(reduced_potentials(data), np.full(len(names), 5000))
        sampled_curve = fit['free_energies_dimensionless']*rt
        theta = fit['covariance_dimensionless']*rt**2
        errors = np.sqrt(np.maximum(0,np.diag(theta)+theta[0,0]-2*theta[0]))
        assert np.max(np.abs(sampled_curve-curve)) <= .1
        assert np.all(np.abs(sampled_curve[1:]-curve[1:]) <= 3*errors[1:])
        reverse = combine_free_energies(names, sampled_curve, theta, replace(spec(names), endpoint_weights={names[0]:1.,names[-1]:-1.}))
        assert abs(reverse.restrained_kj_mol+curve[-1]) <= .1
        output.append(dict(kr=kr, temperature=temperature, endpoint=float(sampled_curve[-1]),
                           exact=float(curve[-1]), error=float(errors[-1]), max_curve_error=float(np.max(np.abs(sampled_curve-curve)))))
    return output

def nonlinear_contexts():
    import openmm as mm
    from openmm import unit
    psets = [parameters(Direction=s, Lambda1=a, Lambda2=b, W0=w, Uh=h, Alpha=alpha)
             for s,a,b,w,h,alpha in ((1.,0.,0.,-.9,2.,0.), (1.,.13,.79,.37,1.1,.63),
                                    (1.,.5,.5,1.7,-3.,0.), (-1.,.13,.79,-.43,2.7,.21),
                                    (-1.,.9,.15,.8,-2.,.51), (-1.,0.,0.,1.3,0.,0.))]
    names = tuple('c'+str(i) for i in range(len(psets)))
    schedule = production_schedule(tuple(zip(names,psets)))
    system = mm.System()
    system.addParticle(17.)
    atm = mm.ATMForce(schedule.expression)
    for key,value in psets[0].items():
        atm.addGlobalParameter(key,value)
    child = mm.CustomExternalForce('18.5*((x-0.07)^2+(y+0.04)^2+(z-0.02)^2)+1.23')
    child.addParticle(0,[])
    atm.addForce(child)
    displacement = np.array((.41,-.23,.17))
    atm.addParticle(mm.Vec3(*displacement),mm.Vec3(0,0,0))
    atm.setForceGroup(1)
    system.addForce(atm)
    outside_force = mm.CustomExternalForce('11*(x+0.12)^2+7*(y-0.03)^2+5*(z+0.01)^2-0.71')
    outside_force.addParticle(0,[])
    outside_force.setForceGroup(2)
    system.addForce(outside_force)
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
    xyz = np.random.default_rng(18231).uniform(-.95,.95,(83,3))
    u0 = 18.5*np.sum((xyz-np.array((.07,-.04,.02)))**2,axis=1)+1.23
    u1 = 18.5*np.sum((xyz+displacement-np.array((.07,-.04,.02)))**2,axis=1)+1.23
    outside = 11*(xyz[:,0]+.12)**2+7*(xyz[:,1]-.03)**2+5*(xyz[:,2]+.01)**2-.71
    actual, expected = np.empty((len(names),len(xyz))), np.empty((len(names),len(xyz)))
    raw_endpoint_errors = []
    try:
        for j,p in enumerate(psets):
            for key,value in p.items():
                context.setParameter(key,value)
            for i,position in enumerate(xyz):
                context.setPositions([position])
                actual[j,i] = context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
                expected[j,i] = independent_expression(u0[i],u1[i],outside[i],p)
                raw1,raw0,expr = atm.getPerturbationEnergy(context)
                raw_endpoint_errors.extend((abs(raw0.value_in_unit(unit.kilojoules_per_mole)-u0[i]),
                                            abs(raw1.value_in_unit(unit.kilojoules_per_mole)-u1[i])))
    finally:
        del context,integrator
    sampled = tuple(names[i%len(names)] for i in range(len(xyz)))
    raw = np.c_[u0,u1,outside,actual[np.arange(len(xyz))%len(names),np.arange(len(xyz))]]
    data = records(schedule,sampled,raw,prefix='native-context')
    reconstructed = reduced_potentials(data)*RT
    np.testing.assert_allclose(actual,expected,rtol=0,atol=1.e-8)
    np.testing.assert_allclose(reconstructed,actual,rtol=0,atol=1.e-8)
    assert max(raw_endpoint_errors) < 1.e-8
    (OUT/'native-context-records.json').write_text(to_json(data)+'\n')
    np.savez_compressed(OUT/'native-context-frames.npz',positions_nm=xyz,independent_energy_kj_mol=expected,
                        actual_energy_kj_mol=actual,reconstructed_energy_kj_mol=reconstructed)
    return dict(state_frame_comparisons=int(actual.size),directions=[-1,1],UOffset=-1.7,Acore=.42,
                max_energy_error=float(np.max(np.abs(actual-expected))),max_raw_error=float(max(raw_endpoint_errors)))

def finite_volumes():
    rng = np.random.default_rng(98021)
    max_rel = 0.
    for i in range(18):
        radius = 0. if i==0 else 10**rng.uniform(-3.,.3)
        spring,temperature = 10**rng.uniform(-3.,8.),rng.uniform(220.,450.)
        rt = .00831446261815324*temperature
        width = math.sqrt(2*rt/spring)
        ref = 4*math.pi*(radius**3/3+quad(lambda t: (radius+width*t)**2*width*math.exp(-t*t),0.,np.inf,
                                         epsabs=1.e-13,epsrel=1.e-12)[0])
        value = finite_wall_volume_nm3(radius,spring,temperature,domain='infinite_space')
        np.testing.assert_allclose(value,ref,rtol=1.e-10,atol=1.e-13)
        max_rel=max(max_rel,abs(value-ref)/ref)
    assert abs(finite_wall_volume_nm3(.6,1.e20,300.,domain='infinite_space')/(4*math.pi*.6**3/3)-1) < 1.e-8
    assert translational_standard_state_correction(3.,300.,1.5) < 0
    assert translational_standard_state_correction(.75,300.,1.5) > 0
    for domain in ('periodic_box','coupled_orientation_position','finite_box','',None):
        reject('unsupported_volume_domain_'+str(domain),lambda domain=domain: finite_wall_volume_nm3(.2,40.,300.,domain=domain))
    return dict(cases=18,max_relative_error=max_rel)

def generic_estimators():
    rng = np.random.default_rng(27731)
    results = []
    for nstates in (2,3,6):
        centers=np.linspace(-.6,.8,nstates)
        springs=np.linspace(1.1,3.8,nstates)
        constants=rng.normal(0.,1.2,nstates)
        counts=np.array([350+137*j for j in range(nstates)])
        xs=np.concatenate([rng.normal(mu,1/math.sqrt(k),int(n)) for mu,k,n in zip(centers,springs,counts)])
        reduced=np.array([.5*k*(xs-mu)**2+c for mu,k,c in zip(centers,springs,constants)])
        mbar=estimate_free_energies(reduced,counts,estimator='pymbar')
        uwham=estimate_free_energies(reduced,counts,estimator='atom_uwham')
        delta=np.max(np.abs(mbar['free_energies_dimensionless']-uwham['free_energies_dimensionless']))
        assert delta < 1.e-8
        exact=constants+.5*np.log(springs)
        exact-=exact[0]
        estimate=mbar['free_energies_dimensionless']
        for i in range(1,nstates):
            w=np.zeros(nstates);w[0]=-1;w[i]=1
            vm=float(w@mbar['covariance_dimensionless']@w)
            vu=float(w@uwham['covariance_dimensionless']@w)
            np.testing.assert_allclose(vm,vu,atol=1.e-10,rtol=1.e-7)
            assert abs(estimate[i]-exact[i]) <= 3*math.sqrt(vm)
        offsets=rng.uniform(-1800.,1800.,nstates)
        column_gauge=rng.uniform(-500.,500.,len(xs))
        shifted=estimate_free_energies(reduced+offsets[:,None]+column_gauge[None,:],counts,estimator='atom_uwham')
        np.testing.assert_allclose(shifted['free_energies_dimensionless'],uwham['free_energies_dimensionless']+offsets-offsets[0],atol=1.e-8,rtol=0)
        # Compare weighted covariances because the algorithms use different covariance gauges.
        w=np.zeros(nstates);w[0]=-1;w[-1]=1
        np.testing.assert_allclose(w@shifted['covariance_dimensionless']@w,w@uwham['covariance_dimensionless']@w,rtol=1.e-7,atol=1.e-10)
        results.append(dict(states=nstates,counts=counts.tolist(),max_solver_difference=float(delta),
                            max_known_difference=float(np.max(np.abs(estimate-exact))),uwham_residual=uwham['solver_residual']))
    return results

def admissions_and_reordering():
    data,names,_=harmonic_data(count=1200,seed=3201)
    thermo=spec(names)
    assert from_json(to_json(data)) == data
    baseline=analyze(data,thermo)
    reverse_schedule=replace(data.schedule,states=tuple(reversed(data.schedule.states)))
    reordered=replace(data,schedule=reverse_schedule)
    np.testing.assert_allclose(reduced_potentials(reordered),reduced_potentials(data)[::-1],rtol=0,atol=1.e-12)
    result=analyze(reordered,thermo)
    np.testing.assert_allclose([result.restrained_kj_mol,result.restrained_standard_error_kj_mol],
                               [baseline.restrained_kj_mol,baseline.restrained_standard_error_kj_mol],rtol=0,atol=1.e-9)
    fields=('sample_ids','sampled_state_ids','walker_ids','sequence_numbers','u0_raw_kJ_mol','u1_raw_kJ_mol','outside_energy_kJ_mol','observed_total_kJ_mol')
    order=np.array([j*1200+i for i in range(1200) for j in range(len(names))])
    interleaved=replace(data,**{name:tuple(getattr(data,name)[i] for i in order) for name in fields})
    same=analyze(interleaved,thermo)
    np.testing.assert_allclose([same.restrained_kj_mol,same.restrained_standard_error_kj_mol],
                               [baseline.restrained_kj_mol,baseline.restrained_standard_error_kj_mol],rtol=0,atol=1.e-9)
    mutations={
        'duplicate_sample':dict(sample_ids=('dup',)*len(data.sample_ids)),
        'unknown_sampled_state':dict(sampled_state_ids=('unknown',)+data.sampled_state_ids[1:]),
        'empty_physical_identity':dict(physical_identity=''),
        'empty_transfer_identity':dict(transfer_identity=''),
        'empty_restraint_identity':dict(restraint_identity=''),
        'empty_provenance':dict(provenance={}),
        'empty_provenance_value':dict(provenance={'source':' '}),
        'sequence_duplicate':dict(sequence_numbers=(0,0)+data.sequence_numbers[2:]),
        'lost_raw_observation':dict(u0_raw_kJ_mol=data.u0_raw_kJ_mol[:-1]),
        'nonfinite_raw':dict(u1_raw_kJ_mol=(float('inf'),)+data.u1_raw_kJ_mol[1:]),
        'unknown_sampling_mode':dict(sampling_mode='auto')}
    for name,changes in mutations.items():
        reject(name,lambda changes=changes:replace(data,**changes))
    reject('wrong_raw_outside_scope',lambda: reduced_potentials(replace(data,outside_energy_kJ_mol=tuple(x+.1 for x in data.outside_energy_kJ_mol))))
    reject('unknown_endpoint_state',lambda:analyze(data,replace(thermo,endpoint_weights={'missing':-1.,names[-1]:1.},endpoint_descriptions={'missing':'unknown',names[-1]:'last'})))
    reject('unknown_graph_state',lambda:analyze(data,replace(thermo,state_connections=(('missing',names[-1]),))))
    reject('disconnected_endpoint_graph',lambda:analyze(data,replace(thermo,state_connections=((names[0],names[1]),(names[-2],names[-1])))))
    for estimator in ('pymbar','atom_uwham'):
        reject('unsampled_state_'+estimator,lambda estimator=estimator:estimate_free_energies(np.zeros((2,20)),(20,0),estimator=estimator))
        # Disconnected support within the UWHAM +/-600 input-range check.
        disconnected=np.array([[0.]*100+[140.]*100,[140.]*100+[0.]*100])
        reject('disconnected_finite_range_'+estimator,lambda estimator=estimator:estimate_free_energies(disconnected,(100,100),estimator=estimator))
    reject('uwham_range_over_600',lambda:estimate_free_energies(np.array([[0.,0.],[0.,601.]]),(1,1),estimator='atom_uwham'))
    return dict(reordering_and_interleaving_preserve_value=True)

def corrections_and_covariance():
    ids=('bulk','bound')
    standard=spec(ids,standard=True)
    covariance=np.array([[.13,.09],[.09,.22]])
    ledger=tuple(CorrectionRecord(name,'zero_demonstrated',0.,0.,'Independent analytic cancellation: '+name)
                 for name in STANDARD_CORRECTION_OBLIGATIONS)
    for n in range(7):
        partial=replace(standard,corrections=ledger[:n])
        result=combine_free_energies(ids,(71.,72.5),covariance,partial)
        if n < 6:
            assert result.final_kj_mol is None
            assert set(result.unresolved_corrections)==set(STANDARD_CORRECTION_OBLIGATIONS[n:])
        else:
            assert result.final_kj_mol==1.5
    reject('empty_standard_obligations',lambda:replace(standard,correction_obligations=()))
    reject('computed_without_evidence',lambda:CorrectionRecord('orientation','computed',.2,.1,''))
    reject('uncomputed_with_zero',lambda:CorrectionRecord('orientation','required_uncomputed',0.,0.,'unknown'))
    reject('false_zero_nonzero_value',lambda:CorrectionRecord('orientation','zero_demonstrated',.1,0.,'claim'))
    rng=np.random.default_rng(27114)
    A=rng.normal(0.,.04,(8,5))
    joint=A@A.T
    corrections=tuple(CorrectionRecord(name,'computed',float(.11*(i-2)),float(math.sqrt(joint[i+2,i+2])),
                                        'Joint linear oracle '+str(i)) for i,name in enumerate(STANDARD_CORRECTION_OBLIGATIONS))
    thermo=replace(standard,corrections=corrections)
    without=combine_free_energies(ids,(71.,72.5),joint[:2,:2],thermo)
    assert without.final_kj_mol is None and 'correction_covariance' in without.unresolved_corrections
    with_cov=combine_free_energies(ids,(71.,72.5),joint[:2,:2],thermo,joint_covariance_kj2_mol2=joint)
    w=np.r_[-1.,1.,np.ones(6)]
    assert abs(with_cov.final_kj_mol-(1.5+sum(c.value_kj_mol for c in corrections))) < 1.e-12
    assert abs(with_cov.final_standard_error_kj_mol-math.sqrt(float(w@joint@w))) < 1.e-12
    wrong=joint.copy();wrong[0,0]+=.001
    reject('joint_wrong_state_block',lambda:combine_free_energies(ids,(71.,72.5),joint[:2,:2],thermo,joint_covariance_kj2_mol2=wrong))
    wrong=joint.copy();wrong[4,4]+=.001
    reject('joint_wrong_correction_diagonal',lambda:combine_free_energies(ids,(71.,72.5),joint[:2,:2],thermo,joint_covariance_kj2_mol2=wrong))
    # A common record or serialized reader must not admit contradictory final results.
    uncomputed=CorrectionRecord('orientation','required_uncomputed',None,None,'not yet available')
    fabricated=reject('BindingResult_final_with_uncomputed_correction',lambda:BindingResult(1.5,.2,(uncomputed,),(),1.5,.2,standard.content_identity,{}))
    empty=reject('BindingResult_final_with_empty_correction_ledger',lambda:BindingResult(1.5,.2,(),(),1.5,.2,standard.content_identity,{}))
    if fabricated is not None:
        payload=to_json(fabricated)
        (OUT/'admitted-final-uncomputed.json').write_text(payload+'\n')
        parsed=from_json(payload)
        assert parsed.final_kj_mol==1.5
        REPORT['metrics']['invalid_final_roundtrip']=True
    if empty is not None:
        (OUT/'admitted-final-empty-ledger.json').write_text(to_json(empty)+'\n')
    return dict(partial_ledgers_checked=7,joint_final_error=with_cov.final_standard_error_kj_mol,
                exact_weighted_error=math.sqrt(float(w@joint@w)))

def correlation():
    data,names,_=harmonic_data(count=6000,seed=19911,mode='correlated')
    corrected=analyze(data,spec(names))
    naive=analyze(replace(data,sampling_mode='independent'),spec(names))
    assert corrected.diagnostics['retained_samples'] < len(data.sample_ids)/3
    assert corrected.restrained_standard_error_kj_mol > 2*naive.restrained_standard_error_kj_mol
    assert min(corrected.diagnostics['statistical_inefficiency'].values()) > 5
    assert min(corrected.diagnostics['effective_samples']) > 100
    exchanged=replace(data,walker_ids=('exchanging',)*len(data.sample_ids),sequence_numbers=tuple(range(len(data.sample_ids))))
    reject('correlated_exchanging_history',lambda:analyze(exchanged,spec(names)))
    short,shortnames,_=harmonic_data(count=6,seed=3111)
    low=analyze(short,spec(shortnames))
    assert 'fewer_than_100_effective_contributions' in low.diagnostics['quality_flags']
    return dict(corrected_error=corrected.restrained_standard_error_kj_mol,naive_error=naive.restrained_standard_error_kj_mol,
                retained=corrected.diagnostics['retained_samples'],input=len(data.sample_ids),
                minimum_g=min(corrected.diagnostics['statistical_inefficiency'].values()),
                minimum_contributions=min(corrected.diagnostics['effective_samples']))

def midpoint_new_ensembles():
    names=('end0','middle+','middle-','end1')
    psets=[parameters(Direction=direction,Lambda1=lam,Lambda2=lam,Alpha=0.,W0=w,UOffset=.4,
                      Acore=.35,Umax=12.,Ubcore=.8) for direction,lam,w in ((1.,0.,.8),(1.,.5,.4),(-1.,.5,-.5),(-1.,0.,-.2))]
    schedule=production_schedule(tuple(zip(names,psets)))
    energy=lambda x,p:independent_expression(50*x*x,50*(x+.3)**2,25*x*x,p)
    partition=np.array([quad(lambda x:math.exp(-energy(x,p)/RT),-np.inf,np.inf,epsabs=1.e-12,epsrel=1.e-11,limit=300)[0] for p in psets])
    F=-RT*np.log(partition)
    d0,d1,bridge=F[1]-F[0],F[2]-F[3],F[2]-F[1]
    assert abs(bridge) > .1
    exact=F[0]-F[3]
    assert abs(exact+.5) < 1.e-9
    assert abs((d1-d0)-exact) > .1
    value,_=directional_difference(d0,d1,bridge,np.eye(3)*.01)
    assert abs(value-exact) < 1.e-10
    reject('missing_directional_bridge',lambda:directional_difference(d0,d1,None,np.eye(3)))
    grid=np.linspace(-2.,2.,50001)
    rng=np.random.default_rng(980041)
    sampled,xs,raw=[],[],[]
    for name,p in zip(names,psets):
        density=np.exp(-np.array([energy(x,p) for x in grid])/RT)
        cdf=cumulative_trapezoid(density,grid,initial=0.);cdf/=cdf[-1]
        x=np.interp(rng.random(7000),cdf,grid)
        xs.extend(x);sampled.extend((name,)*len(x))
        raw.extend((50*t*t,50*(t+.3)**2,25*t*t,energy(t,p)) for t in x)
    data=records(schedule,sampled,raw,prefix='new-midpoint')
    thermo=replace(spec(names),endpoint_weights={names[0]:1.,names[-1]:-1.})
    result=analyze(data,thermo)
    assert abs(result.restrained_kj_mol-exact) <= .1
    assert abs(result.restrained_kj_mol-exact) <= 3*result.restrained_standard_error_kj_mol
    reduced=reduced_potentials(data)
    mbar=estimate_free_energies(reduced,(7000,)*4)
    uwham=estimate_free_energies(reduced,(7000,)*4,estimator='atom_uwham')
    np.testing.assert_allclose(mbar['free_energies_dimensionless'],uwham['free_energies_dimensionless'],atol=1.e-8,rtol=0)
    w=np.array((0.,-1.,1.,0.))
    measured_bridge=float(w@mbar['free_energies_dimensionless'])*RT
    bridge_error=math.sqrt(float(w@mbar['covariance_dimensionless']@w))*RT
    assert abs(measured_bridge-bridge) <= 3*bridge_error
    (OUT/'new-midpoint-records.json').write_text(to_json(data)+'\n')
    np.savez_compressed(OUT/'new-midpoint-ensembles.npz',x_nm=xs,all_reduced_potentials=reduced,
                        midpoint_cross_reduced=reduced[1:3,7000:21000],exact_free_energies_kj_mol=F)
    return dict(exact_bridge=float(bridge),estimated_bridge=measured_bridge,bridge_error=bridge_error,
                exact_endpoint=float(exact),estimate=result.restrained_kj_mol,error=result.restrained_standard_error_kj_mol,
                minimum_contributions=min(result.diagnostics['effective_samples']))

def worker_raw_replay():
    base=ROOT/'Worker_Log/Milestone_04/evidence/G08_v1'
    rows=[]
    fieldnames=('sample_ids','sampled_state_ids','walker_ids','sequence_numbers','u0_raw_kJ_mol','u1_raw_kJ_mol','outside_energy_kJ_mol','observed_total_kJ_mol')
    for seed in (41,73,109):
        directory=base/'md-focused-attempt'/f'seed-{seed}'
        data=from_json((directory/'records.json').read_text())
        bundle=from_json((directory/'bundle.json').read_text())
        assert bundle.physical.content_identity==data.physical_identity
        assert bundle.transfer.content_identity==data.transfer_identity
        assert bundle.restraints.content_identity==data.restraint_identity
        frames=np.load(directory/'frames.npz')
        xyz=frames['positions_nm'][:,0,:]
        raw=frames['raw_kj_mol']
        f=frames['full_real_forces_kj_mol_nm'][:,0,:]
        shift=np.array((.3,0.,0.))
        physical0=50*np.sum(xyz*xyz,axis=1)
        physical1=50*np.sum((xyz+shift)**2,axis=1)
        outside=25*np.sum(xyz*xyz,axis=1)
        lambdas={state.state_id:state.parameters['Lambda'] for state in data.schedule.states}
        lam=np.array([lambdas[state] for state in data.sampled_state_ids])
        refraw=np.c_[physical0,physical1,outside,physical0+lam*(physical1-physical0)+outside]
        stored=np.array([data.u0_raw_kJ_mol,data.u1_raw_kJ_mol,data.outside_energy_kJ_mol,data.observed_total_kJ_mol]).T
        np.testing.assert_allclose(raw,refraw,rtol=0,atol=1.e-8)
        np.testing.assert_allclose(stored,raw,rtol=0,atol=0)
        forces=-150*xyz-lam[:,None]*np.array((30.,0.,0.))
        np.testing.assert_allclose(f,forces,rtol=0,atol=1.e-7)
        names=tuple(s.state_id for s in data.schedule.states)
        thermo=spec(names)
        mbar=analyze(data,thermo)
        uwham=analyze(data,thermo,estimator='atom_uwham')
        np.testing.assert_allclose([mbar.restrained_kj_mol,mbar.restrained_standard_error_kj_mol],
                                   [uwham.restrained_kj_mol,uwham.restrained_standard_error_kj_mol],atol=1.e-7,rtol=0)
        assert abs(mbar.restrained_kj_mol-1.5) <= .1
        assert abs(mbar.restrained_kj_mol-1.5) <= 3*mbar.restrained_standard_error_kj_mol
        walkers=np.asarray(data.walker_ids)
        indices=np.concatenate([np.flatnonzero(walkers==walker)[2000:] for walker in dict.fromkeys(data.walker_ids)])
        last=replace(data,**{name:tuple(getattr(data,name)[i] for i in indices) for name in fieldnames})
        half=analyze(last,thermo)
        assert abs(half.restrained_kj_mol-mbar.restrained_kj_mol) <= 3*(half.restrained_standard_error_kj_mol+mbar.restrained_standard_error_kj_mol)
        rows.append(dict(seed=seed,value=mbar.restrained_kj_mol,error=mbar.restrained_standard_error_kj_mol,
                         last_half=half.restrained_kj_mol,last_half_error=half.restrained_standard_error_kj_mol,
                         retained=mbar.diagnostics['retained_samples'],minimum_contributions=min(mbar.diagnostics['effective_samples']),
                         max_raw_error=float(np.max(np.abs(raw-refraw))),max_force_error=float(np.max(np.abs(f-forces)))))
    mean=float(np.mean([r['value'] for r in rows]))
    error=math.sqrt(sum(r['error']**2 for r in rows))/len(rows)
    spread=float(np.std([r['value'] for r in rows],ddof=1))
    assert abs(mean-1.5) <= .1 and abs(mean-1.5) <= 3*error
    saved=from_json((base/'midpoint-independent-ensembles/unequal-midpoint-records.json').read_text())
    frame=np.load(base/'midpoint-independent-ensembles/unequal-midpoint-frames.npz')
    reduced=reduced_potentials(saved)
    np.testing.assert_allclose(frame['midpoint_cross_reduced'],reduced[1:3,5000:15000],atol=0,rtol=0)
    mbar=estimate_free_energies(reduced,(5000,)*4)
    uwham=estimate_free_energies(reduced,(5000,)*4,estimator='atom_uwham')
    np.testing.assert_allclose(mbar['free_energies_dimensionless'],uwham['free_energies_dimensionless'],atol=1.e-8,rtol=0)
    return dict(seeds=rows,mean=mean,mean_error=error,replicate_spread=spread,worker_midpoint_both_estimators=True)

if __name__=='__main__':
    REPORT['versions']={name:importlib.metadata.version(name) for name in ('numpy','scipy','pymbar','atom-openmm','OpenMM')}
    for name,action in (('quadrature_and_independent_harmonic_samples',known_answer),('nonlinear_native_contexts',nonlinear_contexts),
                        ('finite_wall_independent_integrals',finite_volumes),('generic_unequal_count_estimators',generic_estimators),
                        ('record_admission_and_state_reordering',admissions_and_reordering),('partial_corrections_and_joint_covariance',corrections_and_covariance),
                        ('AR1_correlation_and_contributions',correlation),('new_unequal_midpoint_ensembles',midpoint_new_ensembles),
                        ('worker_raw_frame_and_seed_replay',worker_raw_replay)):
        check(name,action)
    (OUT/'independent-probe-results.json').write_text(json.dumps(REPORT,indent=2)+'\n')
    print(json.dumps({'positives':len(REPORT['positives']),'required_rejections':len(REPORT['required_rejections']),
                      'admitted_faults':len(REPORT['findings']),'failures':len(REPORT['failures'])},indent=2))
    raise SystemExit(1 if REPORT['findings'] or REPORT['failures'] else 0)
