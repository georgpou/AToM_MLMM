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
    if len(bundle.masses_da) != len(expected):
        raise UnsupportedCapability('derived-particle construction requires G04 qualification')
    positions = [None]*len(bundle.masses_da)
    for atom_id, coordinate in zip(expected, snapshot.positions_nm):
        positions[bundle.real_to_final[atom_id]] = coordinate
    return tuple(positions)


def validate_transfer(bundle, transfer):
    if transfer != resolve_protocol(bundle, transfer.protocol):
        raise IdentityError('fixed full-particle maps or physical membership differ from the protocol')
