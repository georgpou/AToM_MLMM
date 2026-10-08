"""Convert prepared molecular bytes to the existing physical-builder records."""
import hashlib

from .schema import (AtomIdentity, Bond, ComponentState, MoleculeState, PartitionSpec,
                     SystemInput, TopologyView)


def _connected(graph, start, forbidden=None):
    visited, pending = set(), [start]
    while pending:
        atom = pending.pop()
        if atom in visited:
            continue
        visited.add(atom)
        pending.extend(b for b in graph[atom]
                       if forbidden is None or frozenset((atom, b)) != forbidden)
    return visited


def benchmark_partition(topology, mode, cavity):
    """Select fixed residue side chains after explicit CB-CA cuts, plus whole ligand."""
    ligands = [m for m in topology.molecules if m.role == 'ligand']
    if len(ligands) != 1 or (ligands[0].formal_charge, ligands[0].multiplicity) != (0, 1):
        raise ValueError('benchmark requires one complete neutral singlet ligand')
    ligand = ligands[0]
    states = [ComponentState(ligand.atom_ids, 0, 1)]
    protein, cuts = set(), []
    if mode == 'cavity':
        atoms = {a.atom_id: a for a in topology.atoms}
        graph = {a: set() for a in atoms}
        for bond in topology.bonds:
            graph[bond.atom1].add(bond.atom2)
            graph[bond.atom2].add(bond.atom1)
        for residue in cavity['residues']:
            parents = []
            for name in cavity['cut']:
                matches = [a.atom_id for a in atoms.values()
                           if (a.chain, a.residue, a.insertion_code, a.atom_name) ==
                           (cavity['chain'], residue, '', name)]
                if len(matches) != 1:
                    raise ValueError(f'cavity atom absent or ambiguous: {residue}/{name}')
                parents.append(matches[0])
            ml, mm = parents
            if mm not in graph[ml]:
                raise ValueError('declared cavity cut is not a prepared bond')
            sidechain = _connected(graph, ml, frozenset(parents))
            if mm in sidechain or any(
                    (atoms[a].chain, atoms[a].residue) != (cavity['chain'], residue)
                    for a in sidechain):
                raise ValueError('cut does not isolate a single neutral side-chain component')
            if protein & sidechain:
                raise ValueError('cavity components overlap')
            protein.update(sidechain)
            cuts.append((ml, mm))
            states.append(ComponentState(tuple(sorted(sidechain)), 0, 1))
    elif mode != 'ligand':
        raise ValueError('ML partition mode must be ligand or cavity')
    return PartitionSpec(tuple(sorted(protein | set(ligand.atom_ids))),
                         tuple(sorted(protein)), tuple(cuts), tuple(states))


def prepared_benchmark_input(pdb, system, ligand, provenance):
    """No parameterization or structure repair: consume AToM's complete MM output."""
    import openmm as mm
    from openmm import unit
    from .ledger import inventory_system
    from .partition import _components
    atoms = tuple(AtomIdentity(
        f'c{a.residue.chain.index}:{a.residue.chain.id}/r{a.residue.index}:'
        f'{a.residue.id}:{a.residue.insertionCode}/{a.name}', a.element.symbol,
        a.residue.chain.id, a.residue.id, a.residue.insertionCode.strip(), a.name)
        for a in pdb.topology.atoms())
    source = list(pdb.topology.atoms())
    ids = tuple(a.atom_id for a in atoms)
    if len(ids) != system.getNumParticles() or any(system.isVirtualSite(i) for i in range(len(ids))):
        raise ValueError('prepared benchmark must contain real atoms only')
    bonds = tuple(Bond(ids[b.atom1.index], ids[b.atom2.index], float(b.order or 1))
                  for b in pdb.topology.bonds())
    graph = {a: set() for a in ids}
    for bond in bonds:
        graph[bond.atom1].add(bond.atom2)
        graph[bond.atom2].add(bond.atom1)
    lookup = dict(zip(ids, source))
    molecules = []
    aa = {'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'HID',
          'HIE', 'HIP', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR',
          'TRP', 'TYR', 'VAL'}
    for number, members in enumerate(_components(set(ids), graph)):
        names = {lookup[a].residue.name for a in members}
        if names == {'L1'}:
            role, charge, name = 'ligand', ligand['formal_charge'], ligand['id']
            if len(members) != ligand['atom_count']:
                raise ValueError('prepared ligand lost or gained real atoms')
        elif names <= aa:
            role, charge, name = 'protein', None, f'protein-{number}'
        elif names <= {'HOH', 'WAT'}:
            role, charge, name = 'water', 0, f'water-{number}'
        elif len(members) == 1 and names <= {'NA', 'CL', 'Na+', 'Cl-'}:
            role, charge, name = 'ion', None, f'ion-{number}'
        else:
            raise ValueError(f'unrecognized prepared molecule: {sorted(names)}')
        molecules.append(MoleculeState(name, tuple(a for a in ids if a in members), role, charge, 1))
    topology = TopologyView(atoms, bonds, tuple(molecules))
    if len([m for m in molecules if m.role == 'ligand']) != 1:
        raise ValueError('prepared input requires exactly one complete ligand')
    xml = mm.XmlSerializer.serialize(system)
    box = tuple(tuple(v.value_in_unit(unit.nanometer)) for v in system.getDefaultPeriodicBoxVectors())
    constraints = tuple((ids[a], ids[b], d.value_in_unit(unit.nanometer))
                        for a, b, d in (system.getConstraintParameters(i)
                                        for i in range(system.getNumConstraints())))
    return SystemInput(xml, hashlib.sha256(xml.encode()).hexdigest(), topology,
        tuple(tuple(v) for v in pdb.positions.value_in_unit(unit.nanometer)), box,
        tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(len(ids))),
        constraints, provenance, prepared_mm_inventory_identity=inventory_system(system).content_identity)
