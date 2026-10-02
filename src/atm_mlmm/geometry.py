"""Fixed identity-based full-particle translations, independent of physics."""
from .identity import validate_mobile_groups
from .schema import IdentityError, TransferDefinition, UnsupportedCapability


def resolve_protocol(bundle, protocol):
    if protocol.kind not in ('abfe', 'rbfe'):
        raise UnsupportedCapability(f'unknown transfer protocol: {protocol.kind}')
    expected = 1 if protocol.kind == 'abfe' else 2
    if len(protocol.mobile_groups) != expected:
        raise UnsupportedCapability(f'{protocol.kind} requires {expected} complete mobile groups')
    if set(protocol.geometry_requests) != {'displacement_nm'}:
        raise UnsupportedCapability('only fixed translation geometry requests admitted')
    validate_mobile_groups(bundle.topology, protocol)
    mobile = {a for g in protocol.mobile_groups for a in g.atom_ids}
    if not mobile <= set(bundle.ml_atom_ids):
        raise UnsupportedCapability('all mobile ligand atoms must belong to fixed ML membership')
    count = len(bundle.masses_da)
    map0 = ((0., 0., 0.),)*count
    map1 = list(map0)
    displacement = protocol.geometry_requests['displacement_nm']
    # Presets specify signs; the shared assembler consumes the resulting maps.
    for group, sign in zip(protocol.mobile_groups, (1., -1.)):
        for atom_id in group.atom_ids:
            map1[bundle.real_to_final[atom_id]] = tuple(sign*x for x in displacement)
    return TransferDefinition(bundle.content_identity, protocol, map0, map1, count)


def final_positions(bundle, snapshot):
    expected = tuple(a.atom_id for a in bundle.topology.atoms)
    if snapshot.real_atom_ids != expected:
        raise IdentityError('snapshot real-atom order/coverage differs from physical topology')
    if snapshot.box_nm is not None:
        raise UnsupportedCapability('periodic physical evaluation belongs to a later gate')
    # Derived entries are placeholders only. The Context reconstructs them
    # with its validated virtual-site machinery after every setPositions.
    positions = [(0., 0., 0.)]*len(bundle.masses_da)
    for atom_id, coordinate in zip(expected, snapshot.positions_nm):
        positions[bundle.real_to_final[atom_id]] = coordinate
    for link in bundle.links:
        a, b = (positions[bundle.real_to_final[parent]] for parent in (link.ml_parent_id, link.mm_parent_id))
        if a == b:
            raise IdentityError(f'coincident link parents: {link.ml_parent_id}-{link.mm_parent_id}')
    return tuple(positions)


def validate_transfer(bundle, transfer):
    if transfer != resolve_protocol(bundle, transfer.protocol):
        raise IdentityError('fixed full-particle maps or physical membership differ from the protocol')


def validate_sites(system, bundle):
    """Verify executable derived sites against sealed identity-based records."""
    import openmm as mm
    from openmm import unit
    declared={link.final_particle_index for link in bundle.links}
    actual={i for i in range(system.getNumParticles()) if system.isVirtualSite(i)}
    if actual != declared:
        raise IdentityError('actual derived particles differ from sealed link records')
    for link in bundle.links:
        site=system.getVirtualSite(link.final_particle_index)
        if not isinstance(site,mm.LocalCoordinatesSite) or site.getNumParticles()!=2:
            raise IdentityError('link virtual-site type/parent count mismatch')
        parents=tuple(site.getParticle(i) for i in range(2))
        if parents != (bundle.real_to_final[link.ml_parent_id],bundle.real_to_final[link.mm_parent_id]):
            raise IdentityError('link parent identities differ from actual virtual site')
        if (tuple(site.getOriginWeights()),tuple(site.getXWeights()),tuple(site.getYWeights()),
            tuple(site.getLocalPosition().value_in_unit(unit.nanometer))) != ((1.,0.),(-1.,1.),(0.,0.),(link.distance_nm,0.,0.)):
            raise IdentityError('link distance/weights differ from the fixed-length rule')
        if any(link.final_particle_index in system.getConstraintParameters(i)[:2] for i in range(system.getNumConstraints())):
            raise IdentityError('derived cap cannot have a Cartesian constraint')
        for force in system.getForces():
            if isinstance(force,mm.NonbondedForce):
                q,_,e=force.getParticleParameters(link.final_particle_index)
                if q.value_in_unit(unit.elementary_charge)!=0 or e.value_in_unit(unit.kilojoule_per_mole)!=0:
                    raise IdentityError('cap has unintended classical charge/LJ interaction')
