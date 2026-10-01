from dataclasses import replace
import pytest


def test_chain_insertion_and_permutation_identity(topology):
    from atm_mlmm.identity import atom_index, find_atom
    from atm_mlmm.schema import IdentityError
    assert find_atom(topology, chain='A', residue='7', insertion_code='A', atom_name='CA') == 'p-a'
    assert find_atom(topology, chain='B', residue='7', insertion_code='', atom_name='C1') == 'l-a1'
    assert find_atom(topology, chain='C', residue='7', insertion_code='', atom_name='C1') == 'l-b1'
    reordered = replace(topology, atoms=tuple(reversed(topology.atoms)))
    assert atom_index(topology)['p-a'] == 2
    assert atom_index(reordered)['p-a'] == 5
    assert set(atom_index(topology)) == set(atom_index(reordered))
    duplicate_metadata = replace(topology.atoms[0], atom_id='extra')
    extra_mol = replace(topology.molecules[0], atom_ids=topology.molecules[0].atom_ids + ('extra',))
    ambiguous = replace(topology, atoms=topology.atoms + (duplicate_metadata,),
                        molecules=(extra_mol,) + topology.molecules[1:])
    with pytest.raises(IdentityError, match='ambiguous'):
        find_atom(ambiguous, chain='A', residue='7', insertion_code='', atom_name='CB')
    with pytest.raises(IdentityError, match='duplicate'):
        replace(topology, atoms=topology.atoms + (topology.atoms[0],))
