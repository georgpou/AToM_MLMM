"""Read-only original-MM inventory. Unsupported terms are never omitted.

Parameter tuples use OpenMM's public API ordering in its common nm/kJ/mol
units. This captures the original system; it does not decide retained terms.
"""
import hashlib
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
