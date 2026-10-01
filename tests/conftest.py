"""Hand-defined awkward topology: a protein cut and unequal ligand groups."""
import pytest


@pytest.fixture
def topology():
    from atm_mlmm.schema import AtomIdentity, Bond, MoleculeState, TopologyView
    # IDs are persistent input identities; this deliberately interleaves molecules.
    atoms = (
        AtomIdentity('p-b', 'C', 'A', '7', '', 'CB'),
        AtomIdentity('l-a2', 'H', 'B', '7', '', 'H1'),
        AtomIdentity('p-a', 'C', 'A', '7', 'A', 'CA'),
        AtomIdentity('l-b1', 'C', 'C', '7', '', 'C1'),
        AtomIdentity('p-h', 'H', 'A', '7', '', 'HB'),
        AtomIdentity('l-a1', 'C', 'B', '7', '', 'C1'),
        AtomIdentity('l-b2', 'H', 'C', '7', '', 'H1'),
        AtomIdentity('l-b3', 'H', 'C', '7', '', 'H2'),
    )
    bonds = (Bond('p-b', 'p-a'), Bond('p-b', 'p-h'),
             Bond('l-a1', 'l-a2'), Bond('l-b1', 'l-b2'), Bond('l-b1', 'l-b3'))
    molecules = (
        MoleculeState('protein', ('p-a', 'p-b', 'p-h'), 'protein', 0, 1),
        MoleculeState('ligand-a', ('l-a1', 'l-a2'), 'ligand', 0, 1),
        MoleculeState('ligand-b', ('l-b1', 'l-b2', 'l-b3'), 'ligand', 0, 1),
    )
    return TopologyView(atoms, bonds, molecules)


@pytest.fixture
def partition_spec():
    from atm_mlmm.schema import ComponentState, PartitionSpec
    return PartitionSpec(
        ml_ids=('p-b', 'l-a1', 'l-a2', 'l-b1', 'l-b2', 'l-b3'),
        protein_ml_ids=('p-b',), permitted_cuts=(('p-b', 'p-a'),),
        component_states=(
            ComponentState(('p-b', 'p-h'), 0, 1),
            ComponentState(('l-a1', 'l-a2'), 0, 1),
            ComponentState(('l-b1', 'l-b2', 'l-b3'), 0, 1),
        ),
    )
