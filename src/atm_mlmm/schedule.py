"""Exact native OpenMM expressions and admitted parameter domains (S05)."""
import math

from .schema import MalformedInput, ScheduleSpec, ScheduleState, UnsupportedCapability

LINEAR_EXPRESSION = 'u0+Lambda*(u1-u0)'
PRODUCTION_EXPRESSION = (
    'select(step(Direction), u0, u1) + '
    'select(Lambda2-Lambda1, ((Lambda2-Lambda1)/Alpha)*log(1+exp(-Alpha*(usc-Uh)))'
    ' + Lambda2*usc + W0, Lambda2*usc + W0);'
    'usc = select(Acore, select(step(u-Ubcore), (Umax-Ubcore)*fsc+Ubcore, u), u);'
    'fsc = (z^Acore-1)/(z^Acore+1);'
    'z = 1 + 2*(y/Acore) + 2*(y/Acore)^2;'
    'y = (u-Ubcore)/(Umax-Ubcore);'
    'u = select(step(Direction), 1, -1)*(u1-(u0 + UOffset))')
PRODUCTION_UNITS = dict(Lambda1='dimensionless', Lambda2='dimensionless', Alpha='mol/kJ',
                        Uh='kJ/mol', W0='kJ/mol', Umax='kJ/mol', Ubcore='kJ/mol',
                        Acore='dimensionless', Direction='dimensionless', UOffset='kJ/mol')


def linear_schedule(states, *, temperature_K=300.):
    result = ScheduleSpec('linear', LINEAR_EXPRESSION,
                          tuple(ScheduleState(name, {'Lambda': value}) for name, value in states),
                          {'Lambda': 'dimensionless'}, temperature_K)
    validate_schedule(result)
    return result


def production_schedule(states, *, temperature_K=300.):
    result = ScheduleSpec('softplus', PRODUCTION_EXPRESSION,
                          tuple(ScheduleState(name, values) for name, values in states),
                          PRODUCTION_UNITS, temperature_K)
    validate_schedule(result)
    return result


def validate_schedule(schedule):
    if schedule.kind == 'linear':
        if schedule.expression != LINEAR_EXPRESSION or dict(schedule.parameter_units) != {'Lambda': 'dimensionless'}:
            raise UnsupportedCapability('unreviewed linear expression or units')
        if any(not 0 <= s.parameters['Lambda'] <= 1 for s in schedule.states):
            raise MalformedInput('linear Lambda outside [0,1]')
    elif schedule.kind == 'softplus':
        if schedule.expression != PRODUCTION_EXPRESSION or dict(schedule.parameter_units) != PRODUCTION_UNITS:
            raise UnsupportedCapability('unreviewed production expression or units')
        for state in schedule.states:
            p = state.parameters
            if not all(0 <= p[k] <= 1 for k in ('Lambda1', 'Lambda2')):
                raise MalformedInput('production Lambda outside [0,1]')
            if p['Direction'] not in (-1., 1.) or p['Acore'] < 0:
                raise MalformedInput('invalid Direction/Acore domain')
            if p['Alpha'] < 0 or (p['Lambda1'] != p['Lambda2'] and p['Alpha'] == 0):
                raise MalformedInput('nonlinear softplus requires positive Alpha')
            if p['Umax'] <= p['Ubcore']:
                raise MalformedInput('Umax must exceed Ubcore')
        fixed = ('Umax', 'Ubcore', 'Acore', 'UOffset')
        if any(any(s.parameters[k] != schedule.states[0].parameters[k] for k in fixed) for s in schedule.states):
            raise UnsupportedCapability('soft-core parameters and perturbation offset are fixed across states')
    else:
        raise UnsupportedCapability(f'unadmitted schedule: {schedule.kind}')


def schedule_state(schedule, state_id):
    for state in schedule.states:
        if state.state_id == state_id:
            return state
    raise MalformedInput(f'unknown schedule state: {state_id}')


def softened_perturbation(u0, u1, schedule, parameters):
    if schedule.kind == 'linear':
        return u1-u0
    p = parameters
    u = p['Direction']*(u1-u0-p['UOffset'])
    if p['Acore'] == 0 or u <= p['Ubcore']:
        return u
    y = (u-p['Ubcore'])/(p['Umax']-p['Ubcore'])
    z = 1+2*y/p['Acore']+2*(y/p['Acore'])**2
    # tanh(a*log(z)/2) is algebraically (z**a-1)/(z**a+1).
    return (p['Umax']-p['Ubcore'])*math.tanh(.5*p['Acore']*math.log(z))+p['Ubcore']
