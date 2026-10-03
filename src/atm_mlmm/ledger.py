"""Read-only original-MM inventory. Unsupported terms are never omitted.

Parameter tuples use OpenMM's public API ordering in its common nm/kJ/mol
units. This captures the original system; it does not decide retained terms.
"""
import hashlib
import copy
from collections import Counter
from .schema import ForceInventory, ForceRecord, UnsupportedCapability


def inventory_system(system):
    import openmm as mm
    from openmm import unit

    def value(item):
        if unit.is_quantity(item):
            converted = item.value_in_unit_system(unit.md_unit_system)
            if isinstance(converted, (float, int)):
                return float(converted)
            return tuple(float(v) for v in converted)
        return item

    def terms(force, number_method, parameter_method):
        return tuple(tuple(value(v) for v in getattr(force, parameter_method)(i))
                     for i in range(getattr(force, number_method)()))

    forces = []
    supported = (mm.HarmonicBondForce, mm.HarmonicAngleForce, mm.PeriodicTorsionForce,
                 mm.RBTorsionForce, mm.NonbondedForce, mm.CMMotionRemover)
    for i in range(system.getNumForces()):
        force = system.getForce(i)
        if type(force) not in supported:
            raise UnsupportedCapability(f'original-MM force unsupported: index {i}, {type(force).__name__}, {force.getName()}')
        if isinstance(force, mm.HarmonicBondForce):
            parameters = {'terms': terms(force, 'getNumBonds', 'getBondParameters')}
        elif isinstance(force, mm.HarmonicAngleForce):
            parameters = {'terms': terms(force, 'getNumAngles', 'getAngleParameters')}
        elif isinstance(force, (mm.PeriodicTorsionForce, mm.RBTorsionForce)):
            parameters = {'terms': terms(force, 'getNumTorsions', 'getTorsionParameters')}
        elif isinstance(force, mm.CMMotionRemover):
            parameters = {'frequency': force.getFrequency()}
        else:
            parameters = dict(
                method=force.getNonbondedMethod(), cutoff_nm=value(force.getCutoffDistance()),
                switching=force.getUseSwitchingFunction(), switching_distance_nm=value(force.getSwitchingDistance()),
                dispersion_correction=force.getUseDispersionCorrection(), ewald_tolerance=force.getEwaldErrorTolerance(),
                reaction_field_dielectric=force.getReactionFieldDielectric(),
                reciprocal_force_group=force.getReciprocalSpaceForceGroup(), include_direct_space=force.getIncludeDirectSpace(),
                exceptions_periodic=force.getExceptionsUsePeriodicBoundaryConditions(),
                pme=tuple(value(v) for v in force.getPMEParameters()),
                ljpme=tuple(value(v) for v in force.getLJPMEParameters()),
                particles=terms(force, 'getNumParticles', 'getParticleParameters'),
                exceptions=terms(force, 'getNumExceptions', 'getExceptionParameters'),
                global_parameters=tuple((force.getGlobalParameterName(j), force.getGlobalParameterDefaultValue(j))
                                        for j in range(force.getNumGlobalParameters())),
                particle_offsets=terms(force, 'getNumParticleParameterOffsets', 'getParticleParameterOffset'),
                exception_offsets=terms(force, 'getNumExceptionParameterOffsets', 'getExceptionParameterOffset'),
            )
        forces.append(ForceRecord(i, type(force).__name__, force.getName(), force.getForceGroup(),
                                  force.usesPeriodicBoundaryConditions(), parameters))
    sites = {}
    for i in range(system.getNumParticles()):
        if not system.isVirtualSite(i):
            continue
        site = system.getVirtualSite(i)
        data = dict(class_name=type(site).__name__, parents=tuple(site.getParticle(j) for j in range(site.getNumParticles())))
        if isinstance(site, (mm.TwoParticleAverageSite, mm.ThreeParticleAverageSite)):
            data['weights'] = tuple(site.getWeight(j) for j in range(site.getNumParticles()))
        elif isinstance(site, mm.OutOfPlaneSite):
            data.update(weight12=site.getWeight12(), weight13=site.getWeight13(), weight_cross=site.getWeightCross())
        elif isinstance(site, mm.LocalCoordinatesSite):
            data.update(origin_weights=tuple(site.getOriginWeights()), x_weights=tuple(site.getXWeights()),
                        y_weights=tuple(site.getYWeights()), local_position_nm=value(site.getLocalPosition()))
        else:
            raise UnsupportedCapability(f'unsupported original-MM virtual site {i}: {type(site).__name__}')
        sites[str(i)] = data
    xml = mm.XmlSerializer.serialize(system)
    return ForceInventory(hashlib.sha256(xml.encode()).hexdigest(),
                          tuple(value(system.getParticleMass(i)) for i in range(system.getNumParticles())),
                          tuple(tuple(value(v) for v in system.getConstraintParameters(i)) for i in range(system.getNumConstraints())),
                          tuple(value(v) for v in system.getDefaultPeriodicBoxVectors()), sites, tuple(forces))


def boundary_dispositions(original, retained, old_to_new, real_ids):
    """Diff actual MM parameters in real-ID order, without reimplementing predicates.

    Original bonded terms can only be retained unchanged or removed. Original
    exceptions can additionally be replaced by zero-charge/zero-LJ exclusions.
    Added ML-pair exclusions and the cap's inert nonbonded entry are explicit.
    Counter matching preserves repeated terms rather than collapsing them.
    """
    from .schema import IdentityError
    before, after = inventory_system(original), inventory_system(retained)
    if len(before.forces) != len(after.forces):
        raise IdentityError('boundary ledger force count mismatch')
    inverse = {new:old for old,new in enumerate(old_to_new)}
    rows = []

    def row(kind, force_index, original_index, atoms, source, target, disposition):
        rows.append(dict(kind=kind,force_index=force_index,original_index=original_index,
                         atom_ids=tuple(real_ids[a] for a in atoms),original_parameters=tuple(source),
                         retained_parameters=tuple(target),disposition=disposition))

    for source,target in zip(before.forces,after.forces):
        if source.class_name != target.class_name:
            raise IdentityError('boundary ledger force type mismatch')
        kind,arity = {'HarmonicBondForce':('bond',2),'HarmonicAngleForce':('angle',3),
                      'PeriodicTorsionForce':('torsion',4),'RBTorsionForce':('torsion',4)}.get(source.class_name,(None,None))
        if kind:
            terms = Counter(tuple(inverse[p] for p in term[:arity])+tuple(term[arity:]) for term in target.parameters['terms'])
            for index,term in enumerate(source.parameters['terms']):
                found = terms[term]>0
                if found: terms[term]-=1
                row(kind,source.index,index,term[:arity],term[arity:],term[arity:] if found else (),
                    'retained' if found else 'removed')
            if +terms:
                raise IdentityError('retained MM contains unrecognized added/modified bonded terms')
        elif source.class_name=='NonbondedForce':
            settings_before = {k:v for k,v in source.parameters.items() if k not in ('particles','exceptions')}
            settings_after = {k:v for k,v in target.parameters.items() if k not in ('particles','exceptions')}
            changes = {k for k in settings_before if settings_before[k] != settings_after[k]}
            if changes:
                if changes != {'exceptions_periodic'} or not settings_after['exceptions_periodic']:
                    raise IdentityError('mechanical boundary changed unrecognized nonbonded settings')
                row('nonbonded_settings',source.index,None,(),tuple(sorted(settings_before.items())),
                    tuple(sorted(settings_after.items())),'changed_periodic_exception_convention')
            for old,parameters in enumerate(source.parameters['particles']):
                actual=target.parameters['particles'][old_to_new[old]]
                if actual != parameters:
                    raise IdentityError('mechanical boundary changed real charge/LJ parameters')
                row('nonbonded_particle',source.index,old,(old,),parameters,actual,'retained')
            for new,p in enumerate(target.parameters['particles']):
                if new not in inverse:
                    if p[0]!=0 or p[2]!=0:
                        raise IdentityError('cap has unintended classical nonbonded interactions')
                    row('nonbonded_particle',source.index,None,(),(),p,'added_inert_cap')
            actual={frozenset((inverse[a],inverse[b])):tuple(p) for a,b,*p in target.parameters['exceptions']
                    if a in inverse and b in inverse}
            seen=set()
            for index,(a,b,*p) in enumerate(source.parameters['exceptions']):
                key=frozenset((a,b));seen.add(key)
                value=actual.get(key)
                if value is None:
                    raise IdentityError('boundary unexpectedly removed an exception record')
                if value==tuple(p):disposition='retained'
                elif value[0]==0 and value[2]==0:disposition='replaced_by_exclusion'
                else:raise IdentityError('boundary exception changed to an unrecognized interaction')
                row('exception',source.index,index,(a,b),p,value,disposition)
            for pair,p in sorted(actual.items(),key=lambda item:sorted(item[0])):
                if pair not in seen:
                    if p[0]!=0 or p[2]!=0:
                        raise IdentityError('added real-pair exception is not an exclusion')
                    row('exception',source.index,None,tuple(sorted(pair)),(),p,'added_exclusion')
        else:
            raise UnsupportedCapability(f'boundary ledger unsupported force: {source.class_name}')
    constraints=Counter((frozenset((inverse[a],inverse[b])),d) for a,b,d in after.constraints)
    for index,(a,b,d) in enumerate(before.constraints):
        term=(frozenset((a,b)),d);found=constraints[term]>0
        if found:constraints[term]-=1
        row('constraint',None,index,(a,b),(d,),(d,) if found else (), 'retained' if found else 'removed')
    if +constraints:raise IdentityError('boundary added/modified constraints')
    return tuple(rows)


def validate_pme_system(system, box_nm):
    """Narrow G06 mechanical PME admission; never approximate other forces."""
    import openmm as mm
    from openmm import unit
    from .geometry import orthorhombic_lengths
    lengths = orthorhombic_lengths(box_nm)
    allowed = (mm.HarmonicBondForce,mm.HarmonicAngleForce,mm.PeriodicTorsionForce,
               mm.RBTorsionForce,mm.NonbondedForce)
    if any(type(f) not in allowed for f in system.getForces()):
        raise UnsupportedCapability('unqualified custom/nonstandard PME force or mixing')
    forces = [f for f in system.getForces() if isinstance(f,mm.NonbondedForce)]
    if len(forces) != 1:
        raise UnsupportedCapability('exactly one standard PME NonbondedForce required')
    force = forces[0]
    if force.getNonbondedMethod() != mm.NonbondedForce.PME:
        raise UnsupportedCapability('only PME, not LJPME or alternative methods, admitted')
    if force.getNumParticleParameterOffsets() or force.getNumExceptionParameterOffsets() or force.getNumGlobalParameters():
        raise UnsupportedCapability('charge/LJ offsets and globals are unsupported')
    if force.getUseDispersionCorrection():
        raise UnsupportedCapability('analytical dispersion correction requires a separate review')
    cutoff = force.getCutoffDistance().value_in_unit(unit.nanometer)
    if cutoff <= 0 or min(lengths) <= 2*cutoff:
        raise UnsupportedCapability('PME cutoff requires a box larger than twice the cutoff')
    if force.getUseSwitchingFunction() and not 0 < force.getSwitchingDistance().value_in_unit(unit.nanometer) < cutoff:
        raise UnsupportedCapability('switch distance must be positive and below cutoff')
    return force


def _mask_diagnostic(system, positions_nm, box_nm, cavity, ligand, *, kind, scale=1.):
    import numpy as np
    import openmm as mm
    from openmm import unit
    from .schema import IdentityError
    validate_pme_system(system,box_nm)
    n = system.getNumParticles()
    first, second = tuple(cavity),tuple(ligand)
    if (len(set(first)) != len(first) or len(set(second)) != len(second) or set(first)&set(second)
            or any(isinstance(i,bool) or not isinstance(i,(int,np.integer)) or i<0 or i>=n for i in first+second)):
        raise IdentityError('mask sets must be disjoint unique valid particle indices')
    x = np.asarray(positions_nm,dtype=float)
    if x.shape != (n,3) or not np.isfinite(x).all() or not np.isfinite(scale):
        raise IdentityError('mask needs every finite particle coordinate and finite charge scale')
    # Copy the actual sites/masses but isolate the standard nonbonded force.
    isolated = copy.deepcopy(system)
    for i in reversed(range(isolated.getNumForces())):
        if not isinstance(isolated.getForce(i),mm.NonbondedForce): isolated.removeForce(i)
    force = isolated.getForce(0)
    particles = [force.getParticleParameters(i) for i in range(n)]
    exceptions = [force.getExceptionParameters(i) for i in range(force.getNumExceptions())]
    isolated.setDefaultPeriodicBoxVectors(*(mm.Vec3(*v) for v in box_nm))
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(isolated,integrator,mm.Platform.getPlatformByName('Reference'))
    try:
        realized = force.getPMEParametersInContext(context)
    finally:
        del context,integrator
    # Resolve once, then bind every mask to identical realized alpha and mesh.
    force.setPMEParameters(*realized)
    energies = {}
    charges = {}
    for name, selected in (('union',set(first)|set(second)),('cavity',set(first)),('ligand',set(second)),('empty',set())):
        for i,(q,s,e) in enumerate(particles):
            force.setParticleParameters(i,q*scale if kind=='charge' and i in selected else 0.,s,
                                        e if kind=='lj' and i in selected else 0.)
        for i,(a,b,q,s,e) in enumerate(exceptions):
            active = a in selected and b in selected
            force.setExceptionParameters(i,a,b,q*scale**2 if kind=='charge' and active else 0.,s,
                                         e if kind=='lj' and active else 0.)
        integrator = mm.VerletIntegrator(.0005)
        context = mm.Context(isolated,integrator,mm.Platform.getPlatformByName('Reference'))
        try:
            context.setPositions(x);context.computeVirtualSites()
            energies[name] = float(context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole))
            charges[name] = float(sum(particles[i][0].value_in_unit(unit.elementary_charge)*scale for i in selected)) if kind=='charge' else 0.
        finally:
            del context,integrator
    if not np.isfinite(list(energies.values())).all():
        from .schema import NumericalDomainError
        raise NumericalDomainError('nonfinite masked interaction energy')
    alpha = realized[0]
    if unit.is_quantity(alpha): alpha = alpha.value_in_unit(unit.nanometer**-1)
    return {'kind':kind,'energies_kj_mol':energies,
            'cross_kj_mol':energies['union']-energies['cavity']-energies['ligand']+energies['empty'],
            'realized_pme':(float(alpha),*map(int,realized[1:])), 'mask_net_charges_e':charges,
            'background_convention':'openmm-uniform-neutralizing-background',
            'lj_mixing':'Lorentz-Berthelot', 'scope':'energy diagnostic, not a free-energy correction'}


def charge_mask_diagnostic(system, positions_nm, box_nm, cavity, ligand, *, scale=1.):
    return _mask_diagnostic(system,positions_nm,box_nm,cavity,ligand,kind='charge',scale=scale)


def lj_mask_diagnostic(system, positions_nm, box_nm, cavity, ligand):
    return _mask_diagnostic(system,positions_nm,box_nm,cavity,ligand,kind='lj')
