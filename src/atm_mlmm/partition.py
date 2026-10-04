"""Resolve a fixed whole-ligand/protein selection from explicit connectivity."""
import hashlib
from .identity import atom_index
from .schema import IdentityError, ResolvedPartition, UnsupportedCapability

ELEMENTS = frozenset(('H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I'))


def _components(selected, graph):
    remaining = set(selected)
    components = []
    while remaining:
        todo, found = [min(remaining)], set()
        while todo:
            atom = todo.pop()
            if atom in found:
                continue
            found.add(atom)
            todo.extend(graph[atom] & selected - found)
        remaining -= found
        components.append(frozenset(found))
    return components


def _is_ring_cut(a, b, graph):
    todo, seen = [a], set()
    while todo:
        node = todo.pop()
        if node == b:
            return True
        if node in seen:
            continue
        seen.add(node)
        todo.extend(n for n in graph[node] if frozenset((node, n)) != frozenset((a, b)) and n not in seen)
    return False


def resolve_partition(topology, spec):
    atoms = {a.atom_id: a for a in topology.atoms}
    selected, protein = set(spec.ml_ids), set(spec.protein_ml_ids)
    if not selected <= atoms.keys():
        raise IdentityError(f'unknown selected real IDs: {sorted(selected - atoms.keys())}')
    graph = {a: set() for a in atoms}
    for bond in topology.bonds:
        graph[bond.atom1].add(bond.atom2)
        graph[bond.atom2].add(bond.atom1)
    membership = {a: m for m in topology.molecules for a in m.atom_ids}
    for bond in topology.bonds:
        if membership[bond.atom1].molecule_id != membership[bond.atom2].molecule_id:
            raise IdentityError(f'bond contradicts molecule membership: {bond.atom1}-{bond.atom2}')
    if any(membership[a].role != 'protein' for a in protein):
        raise UnsupportedCapability('protein selection contains a nonprotein atom')
    # Bond connectivity, rather than atom names, completes protein hydrogens.
    hydrogens = {neighbor for a in protein for neighbor in graph[a] if atoms[neighbor].element == 'H'}
    protein |= hydrogens
    selected |= hydrogens
    if {a for a in selected if membership[a].role == 'protein'} != protein:
        raise IdentityError('protein_ml_ids do not describe the selected protein atoms')
    for a in selected:
        if atoms[a].element not in ELEMENTS:
            raise UnsupportedCapability(f'unknown/unsupported element {atoms[a].element}: {a}')
        if membership[a].role not in ('ligand', 'protein', 'host'):
            raise UnsupportedCapability(f'unsupported selected molecule role: {membership[a].role}')
    for molecule in topology.molecules:
        if molecule.role == 'host' and set(molecule.atom_ids) & selected:
            if not set(molecule.atom_ids) <= selected:
                raise UnsupportedCapability(f'complete static host required: {molecule.molecule_id}')
            if molecule.formal_charge != 0 or molecule.multiplicity != 1:
                raise UnsupportedCapability(f'neutral unambiguous singlet host required: {molecule.molecule_id}')
            if len(_components(set(molecule.atom_ids), graph)) != 1:
                raise IdentityError(f'disconnected host membership: {molecule.molecule_id}')
        if molecule.role == 'ligand':
            if not set(molecule.atom_ids) <= selected:
                raise UnsupportedCapability(f'complete ligand required: {molecule.molecule_id}')
            if molecule.formal_charge != 0 or molecule.multiplicity != 1:
                raise UnsupportedCapability(f'neutral unambiguous singlet ligand required: {molecule.molecule_id}')
            if len(_components(set(molecule.atom_ids), graph)) != 1:
                raise IdentityError(f'disconnected ligand membership: {molecule.molecule_id}')
    crossing = []
    for bond in topology.bonds:
        if (bond.atom1 in selected) != (bond.atom2 in selected):
            a, b = (bond.atom1, bond.atom2) if bond.atom1 in selected else (bond.atom2, bond.atom1)
            if membership[a].role != 'protein' or membership[b].role != 'protein' or membership[a].molecule_id != membership[b].molecule_id:
                raise UnsupportedCapability(f'ligand/nonprotein cut forbidden: {a}-{b}')
            if atoms[a].element != 'C' or atoms[b].element != 'C' or bond.order != 1 or bond.kind != 'ordinary':
                raise UnsupportedCapability(f'only ordinary protein C-C cuts admitted: {a}-{b}')
            if _is_ring_cut(a, b, graph):
                raise UnsupportedCapability(f'ring cut forbidden: {a}-{b}')
            crossing.append((a, b))
    if {frozenset(c) for c in crossing} != {frozenset(c) for c in spec.permitted_cuts}:
        raise UnsupportedCapability(f'crossing bonds differ from permitted cuts: {crossing}')
    if len({b for _, b in crossing}) != len(crossing):
        raise UnsupportedCapability('multiple caps on an MM parent forbidden')
    components = _components(selected, graph)
    if any(sum(a in component for a, _ in crossing) > 1 for component in components):
        raise UnsupportedCapability('initial protein fragments require a single cut per component')
    states = {frozenset(s.atom_ids): s for s in spec.component_states}
    if len(states) != len(spec.component_states) or set(states) != set(components):
        raise UnsupportedCapability('explicit chemical states must match every completed ML component')
    for ids, state in states.items():
        if state.formal_charge != 0 or state.multiplicity != 1:
            raise UnsupportedCapability(f'charged/ambiguous fragment unsupported: {sorted(ids)}')
    identities = tuple(hashlib.sha256('\0'.join(sorted(c)).encode()).hexdigest() for c in components)
    return ResolvedPartition(tuple(sorted(selected)), tuple(sorted(protein)), tuple(sorted(crossing)),
                             identities, (), atom_index(topology))
