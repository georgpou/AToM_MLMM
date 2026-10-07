"""ABFE input description; coordinate-map resolution belongs to G02."""
from ..schema import Endpoint, ProtocolSpec, UnsupportedCapability


def make_protocol(groups, displacement_nm):
    groups = tuple(groups)
    if len(groups) != 1:
        raise UnsupportedCapability('ABFE requires one complete mobile group')
    return ProtocolSpec('abfe', groups, {'displacement_nm': displacement_nm},
                        (Endpoint('bound', 'ligand in bound domain'), Endpoint('bulk', 'ligand in bulk domain')),
                        'dG_bind_bound_minus_bulk')
