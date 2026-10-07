"""Dual-ligand RBFE input description; no atom-pair correspondence required."""
from ..schema import Endpoint, ProtocolSpec, UnsupportedCapability


def make_protocol(groups, displacement_nm):
    groups = tuple(groups)
    if len(groups) != 2:
        raise UnsupportedCapability('RBFE requires two complete mobile groups')
    return ProtocolSpec('rbfe', groups, {'displacement_nm': displacement_nm},
                        (Endpoint('A-bound', 'A bound; B bulk'), Endpoint('B-bound', 'B bound; A bulk')),
                        'ddG_bind_B_minus_A')
