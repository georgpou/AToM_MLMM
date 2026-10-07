from dataclasses import replace
import pytest


def test_fixed_complete_mobile_groups(topology, partition_spec):
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import UnsupportedCapability, IdentityError
    resolved = resolve_partition(topology, partition_spec)
    assert resolved.ml_ids == ('l-a1', 'l-a2', 'l-b1', 'l-b2', 'l-b3', 'p-b', 'p-h')
    assert resolved.protein_ml_ids == ('p-b', 'p-h')
    assert resolved.boundary_edges == (('p-b', 'p-a'),)
    assert resolved.source_map['l-a1'] == 5
    assert resolved.rejected_conditions == ()
    # The resolver owns copies and produces the same membership after reordering.
    assert resolve_partition(replace(topology, atoms=tuple(reversed(topology.atoms))), partition_spec).ml_ids == resolved.ml_ids
    with pytest.raises(UnsupportedCapability, match='complete ligand'):
        resolve_partition(topology, replace(partition_spec, ml_ids=partition_spec.ml_ids[:-1]))
    with pytest.raises(IdentityError, match='duplicate'):
        replace(partition_spec, ml_ids=partition_spec.ml_ids + ('p-b',))
    with pytest.raises(UnsupportedCapability, match='cut'):
        resolve_partition(topology, replace(partition_spec, permitted_cuts=()))


@pytest.mark.parametrize('fault', ['ring', 'peptide', 'disulfide', 'charged', 'unknown_element', 'ambiguous', 'multiple_caps'])
def test_forbidden_boundaries_and_chemical_states(topology, partition_spec, fault):
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import AtomIdentity, Bond, UnsupportedCapability
    if fault == 'ring':
        topology = replace(topology, bonds=topology.bonds + (Bond('p-a', 'p-h'),))
    elif fault == 'peptide':
        topology = replace(topology, bonds=(replace(topology.bonds[0], kind='peptide'),) + topology.bonds[1:])
    elif fault == 'disulfide':
        topology = replace(topology, bonds=(replace(topology.bonds[0], kind='disulfide'),) + topology.bonds[1:])
    elif fault in ('charged', 'ambiguous'):
        state = replace(partition_spec.component_states[0], formal_charge=1 if fault == 'charged' else None)
        partition_spec = replace(partition_spec, component_states=(state,) + partition_spec.component_states[1:])
    elif fault == 'unknown_element':
        topology = replace(topology, atoms=(replace(topology.atoms[0], element='Xx'),) + topology.atoms[1:])
    else:
        topology = replace(topology,
            atoms=topology.atoms + (AtomIdentity('p-c', 'C', 'A', '8', '', 'CB'),),
            bonds=topology.bonds + (Bond('p-c', 'p-a'),),
            molecules=(replace(topology.molecules[0], atom_ids=topology.molecules[0].atom_ids + ('p-c',)),) + topology.molecules[1:])
        partition_spec = replace(partition_spec,
            ml_ids=partition_spec.ml_ids + ('p-c',), protein_ml_ids=('p-b', 'p-c'),
            permitted_cuts=(('p-b', 'p-a'), ('p-c', 'p-a')))
    with pytest.raises(UnsupportedCapability):
        resolve_partition(topology, partition_spec)


def test_mobile_group_membership_matches_complete_ligand(topology):
    from atm_mlmm.identity import validate_mobile_groups
    from atm_mlmm.schema import MobileGroup, UnsupportedCapability
    from atm_mlmm.protocols.rbfe import make_protocol
    a = MobileGroup('A', ('l-a2', 'l-a1'), ('ligand',), 'ligand-a')
    b = MobileGroup('B', ('l-b3', 'l-b1', 'l-b2'), ('ligand',), 'ligand-b')
    validate_mobile_groups(topology, make_protocol((a, b), (1, 0, 0)))
    with pytest.raises(UnsupportedCapability, match='complete'):
        validate_mobile_groups(topology, make_protocol((replace(a, atom_ids=('l-a1',)), b), (1, 0, 0)))
    with pytest.raises(UnsupportedCapability):
        validate_mobile_groups(topology, make_protocol((replace(a, molecule_id='protein'), b), (1, 0, 0)))


def test_cross_molecule_bond_and_multiple_component_cuts_fail(topology, partition_spec):
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import AtomIdentity, Bond, ComponentState, UnsupportedCapability, IdentityError
    # Molecule metadata must agree with graph connectivity, even when both ends are selected.
    linked = replace(topology, bonds=topology.bonds + (Bond('l-a1', 'l-b1'),))
    with pytest.raises((UnsupportedCapability, IdentityError), match='molecule'):
        resolve_partition(linked, partition_spec)
    # One selected protein fragment may not silently acquire two end caps.
    extended = replace(topology,
        atoms=topology.atoms + (AtomIdentity('p-c', 'C', 'A', '8', '', 'CA'),),
        bonds=topology.bonds + (Bond('p-b', 'p-c'),),
        molecules=(replace(topology.molecules[0], atom_ids=topology.molecules[0].atom_ids + ('p-c',)),) + topology.molecules[1:])
    spec = replace(partition_spec, permitted_cuts=(('p-b', 'p-a'), ('p-b', 'p-c')))
    with pytest.raises(UnsupportedCapability, match='single.cut'):
        resolve_partition(extended, spec)
