"""Stable real identities; particle indices are derived for each input ordering."""
from .schema import IdentityError, UnsupportedCapability


def atom_index(topology):
    return {atom.atom_id: i for i, atom in enumerate(topology.atoms)}


def find_atom(topology, *, chain, residue, insertion_code, atom_name):
    matches = [a.atom_id for a in topology.atoms
               if (a.chain, a.residue, a.insertion_code, a.atom_name) == (chain, residue, insertion_code, atom_name)]
    if len(matches) != 1:
        raise IdentityError(f'ambiguous or absent atom: {chain}/{residue}/{insertion_code}/{atom_name}, matches={matches}')
    return matches[0]


def validate_force_coverage(result, topology):
    expected = tuple(a.atom_id for a in topology.atoms)
    if result.real_atom_ids != expected:
        raise IdentityError(f'force real-atom coverage/order differs: expected {expected}, got {result.real_atom_ids}')


def validate_mobile_groups(topology, protocol):
    molecules = {m.molecule_id: m for m in topology.molecules}
    seen = set()
    for group in protocol.mobile_groups:
        molecule = molecules.get(group.molecule_id)
        if molecule is None or molecule.role != 'ligand' or 'ligand' not in group.roles:
            raise UnsupportedCapability(f'mobile group is not a known ligand molecule: {group.group_id}')
        if set(group.atom_ids) != set(molecule.atom_ids):
            raise UnsupportedCapability(f'complete mobile ligand required: {group.group_id}')
        if molecule.molecule_id in seen:
            raise IdentityError(f'duplicate mobile molecule: {molecule.molecule_id}')
        seen.add(molecule.molecule_id)
