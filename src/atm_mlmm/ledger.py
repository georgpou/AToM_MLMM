"""Read-only original-MM inventory. Unsupported terms are never omitted.

Parameter tuples use OpenMM's public API ordering in its common nm/kJ/mol
units. This captures the original system; it does not decide retained terms.
"""
import hashlib
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
