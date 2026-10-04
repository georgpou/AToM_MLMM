"""A static neutral whole host has an explicit role, not a protein alias."""
from dataclasses import replace
import pytest


def host_case(topology, partition_spec):
    host = replace(topology.molecules[1], role='host')
    return replace(topology, molecules=(topology.molecules[0], host)+topology.molecules[2:]), partition_spec


def test_neutral_complete_host_is_static(topology, partition_spec):
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.identity import validate_mobile_groups
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup, UnsupportedCapability
    topology, spec = host_case(topology, partition_spec)
    result = resolve_partition(topology, spec)
    assert set(topology.molecules[1].atom_ids) <= set(result.ml_ids)
    assert result.protein_ml_ids == ('p-b', 'p-h')
    group = MobileGroup('host', topology.molecules[1].atom_ids, ('ligand',), topology.molecules[1].molecule_id)
    with pytest.raises(UnsupportedCapability, match='ligand'):
        validate_mobile_groups(topology, make_protocol((group,), (1., 0., 0.)))


@pytest.mark.parametrize('fault', ('partial', 'charged', 'ambiguous', 'disconnected'))
def test_host_admission_rejects_unsupported_state(topology, partition_spec, fault):
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import UnsupportedCapability, IdentityError
    topology, spec = host_case(topology, partition_spec)
    if fault == 'partial':
        spec = replace(spec, ml_ids=tuple(a for a in spec.ml_ids if a != topology.molecules[1].atom_ids[0]))
    elif fault == 'disconnected':
        atoms = set(topology.molecules[1].atom_ids)
        topology = replace(topology, bonds=tuple(b for b in topology.bonds if not {b.atom1, b.atom2} <= atoms))
    else:
        host = replace(topology.molecules[1], formal_charge=1 if fault == 'charged' else 0,
                       multiplicity=None if fault == 'ambiguous' else 1)
        topology = replace(topology, molecules=(topology.molecules[0], host)+topology.molecules[2:])
    with pytest.raises((UnsupportedCapability, IdentityError), match='host'):
        resolve_partition(topology, spec)
