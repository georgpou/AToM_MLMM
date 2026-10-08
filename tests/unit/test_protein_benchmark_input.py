import pytest
from atm_mlmm.schema import AtomIdentity, Bond, MoleculeState, TopologyView


def example():
    atoms = (AtomIdentity('ca', 'C', 'A', '36', '', 'CA'),
             AtomIdentity('cb', 'C', 'A', '36', '', 'CB'),
             AtomIdentity('h', 'H', 'A', '36', '', 'HB'),
             AtomIdentity('l1', 'C', 'L', '1', '', 'C1'),
             AtomIdentity('l2', 'H', 'L', '1', '', 'H1'))
    return TopologyView(atoms, (Bond('ca', 'cb'), Bond('cb', 'h'), Bond('l1', 'l2')),
        (MoleculeState('protein', ('ca', 'cb', 'h'), 'protein', None, 1),
         MoleculeState('ligand', ('l1', 'l2'), 'ligand', 0, 1)))


def test_fixed_sidechain_selection_keeps_complete_ligand_and_cap_parents():
    from atm_mlmm.protein_input import benchmark_partition
    from atm_mlmm.partition import resolve_partition
    spec = benchmark_partition(example(), 'cavity',
        {'chain': 'A', 'residues': ['36'], 'cut': ['CB', 'CA']})
    resolved = resolve_partition(example(), spec)
    assert set(resolved.ml_ids) == {'cb', 'h', 'l1', 'l2'}
    assert resolved.boundary_edges == (('cb', 'ca'),)
    assert set(resolved.protein_ml_ids) == {'cb', 'h'}
    assert all(state.formal_charge == 0 for state in resolved.component_states)


def test_ligand_only_uses_same_complete_ligand_with_no_cuts():
    from atm_mlmm.protein_input import benchmark_partition
    spec = benchmark_partition(example(), 'ligand', {})
    assert set(spec.ml_ids) == {'l1', 'l2'}
    assert spec.permitted_cuts == ()


def test_cavity_rejects_missing_residue_before_builder():
    from atm_mlmm.protein_input import benchmark_partition
    with pytest.raises(ValueError, match='absent'):
        benchmark_partition(example(), 'cavity',
            {'chain': 'A', 'residues': ['99'], 'cut': ['CB', 'CA']})


def test_prepared_pdb_blank_insertion_codes_select_the_declared_cavity(tmp_path):
    import openmm as mm
    from openmm import app, unit
    from atm_mlmm.protein_input import prepared_benchmark_input, benchmark_partition
    topology = app.Topology()
    protein = topology.addResidue('PHE', topology.addChain('A'), id='36')
    ca = topology.addAtom('CA', app.element.carbon, protein)
    cb = topology.addAtom('CB', app.element.carbon, protein)
    topology.addBond(ca, cb)
    ligand = topology.addResidue('L1', topology.addChain('L'), id='1')
    topology.addAtom('C1', app.element.carbon, ligand)
    topology.setPeriodicBoxVectors((mm.Vec3(3, 0, 0), mm.Vec3(0, 3, 0),
                                   mm.Vec3(0, 0, 3))*unit.nanometer)
    path = tmp_path / 'prepared.pdb'
    with path.open('w') as handle:
        app.PDBFile.writeFile(topology, [[0, 0, 0], [.15, 0, 0], [1, 0, 0]]*unit.nanometer,
                             handle, keepIds=True)
    pdb = app.PDBFile(str(path))
    assert next(pdb.topology.residues()).insertionCode == ' '
    system = mm.System()
    for _ in range(3):
        system.addParticle(12.)
    system.setDefaultPeriodicBoxVectors(*pdb.topology.getPeriodicBoxVectors())
    original = prepared_benchmark_input(pdb, system,
        {'id': 'probe', 'formal_charge': 0, 'atom_count': 1}, {'source': 'synthetic test'})
    spec = benchmark_partition(original.topology, 'cavity',
        {'chain': 'A', 'residues': ['36'], 'cut': ['CB', 'CA']})
    assert len(spec.protein_ml_ids) == 1
    assert len(spec.ml_ids) == 2
