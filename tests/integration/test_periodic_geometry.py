"""G06-03/04/05: independent images, wrapping and actual ASE/MACE shifts."""
from dataclasses import replace
import itertools
import numpy as np
import pytest
from tests.periodic_oracle import BOX, periodic_case, periodic_input, enumerated_displacement


def test_images_caps_and_bulk_separation():
    from atm_mlmm.geometry import minimum_image, validate_bulk_clearance
    from atm_mlmm.schema import NumericalDomainError
    for delta in itertools.product((-7.1, -1.61, -.1, .1, 1.61, 7.1), repeat=3):
        expected, _ = enumerated_displacement(delta)
        np.testing.assert_allclose(minimum_image(delta, BOX), expected, rtol=0, atol=1e-12)
    protein = np.array(((.1, .1, .1), (1.3, 1.3, 1.3)))
    # Bulk appears distant in primary coordinates but reconnects to a protein image.
    with pytest.raises(NumericalDomainError, match='clearance'):
        validate_bulk_clearance([[3.25, .1, .1]], protein, [[.217, .1, .1]], BOX, cutoff_nm=.45)
    # Full-protein MM clearance, beyond the selected cavity/cap.
    with pytest.raises(NumericalDomainError, match='clearance'):
        validate_bulk_clearance([[1.4, 1.3, 1.3]], protein, [[.217, .1, .1]], BOX, cutoff_nm=.45)
    assert validate_bulk_clearance([[1.4, .1, 1.3]], protein, [[.217, .1, .1]], BOX, cutoff_nm=.45)['minimum_distance_nm'] > .65


def test_cap_wrapping_and_image_seam_continuity():
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.geometry import unwrap_molecules
    from tests.link_oracle import REFERENCE
    bundle, snapshot = periodic_case(real_model=True)
    x = np.array(snapshot.positions_nm)
    x[:8] += (3.15, -.06, .03)
    original = replace(snapshot, positions_nm=x)
    wrapped = replace(snapshot, positions_nm=np.mod(x, np.diag(BOX)))
    unwrapped = unwrap_molecules(bundle.topology, wrapped.positions_nm, BOX)
    np.testing.assert_allclose(np.diff(unwrapped[:8], axis=0), np.diff(x[:8], axis=0), atol=1e-12)
    with PhysicalEvaluator(bundle, REFERENCE) as evaluator:
        a, b = evaluator.evaluate(original), evaluator.evaluate(wrapped)
        assert abs(a.energy_kj_mol-b.energy_kj_mol) <= 1e-4
        np.testing.assert_allclose(a.forces_kj_mol_nm, b.forces_kj_mol_nm, atol=5e-3, rtol=0)
        # A complete ligand crosses a primary-box face; canonical wrapping must
        # preserve its geometry and actual forces on both cap parents.
        for shift in (-1e-6, 0., 1e-6):
            r = x.copy(); r[8:] += (3.2-x[8, 0]+shift, 0., 0.)
            direct = evaluator.evaluate(replace(snapshot, positions_nm=r))
            image = evaluator.evaluate(replace(snapshot, positions_nm=np.mod(r, np.diag(BOX))))
            assert abs(direct.energy_kj_mol-image.energy_kj_mol) <= 1e-4
            np.testing.assert_allclose(direct.forces_kj_mol_nm, image.forces_kj_mol_nm, atol=5e-3, rtol=0)
        enlarged = replace(snapshot, box_nm=tuple(tuple(v*1.1 for v in row) for row in BOX))
        assert np.isfinite(evaluator.evaluate(enlarged).energy_kj_mol)
        restored = evaluator.evaluate(original)
        assert abs(restored.energy_kj_mol-a.energy_kj_mol) <= 1e-4
        np.testing.assert_allclose(restored.forces_kj_mol_nm, a.forces_kj_mol_nm, atol=5e-3, rtol=0)


@pytest.mark.model_assets
def test_backend_graph_matches_independent_geometry():
    from ase import Atoms
    from atm_mlmm.geometry import periodic_edges
    from atm_mlmm.models.mace import make_calculator
    calculator = make_calculator()
    positions = np.array(((.03, .2, .3), (3.12, .2, .3), (.03, .5, .3), (1.5, 1.5, 1.5)))
    atoms = Atoms(numbers=[6, 1, 1, 6], positions=positions*10, cell=np.asarray(BOX)*10, pbc=True)
    batch = calculator._atoms_to_batch(atoms)
    actual = {(int(i), int(j), tuple(int(v) for v in shift)) for (i,j),shift in
              zip(batch['edge_index'].T.tolist(), batch['unit_shifts'].tolist())}
    expected = set(periodic_edges(positions, BOX, .45))
    assert actual == expected
    assert any(any(shift) for _,_,shift in actual)
    np.testing.assert_allclose(batch['shifts'].numpy(), np.asarray(batch['unit_shifts'])@np.asarray(BOX)*10, atol=1e-12)
    # Actual local cutoff behavior across both sides; no sample is discarded.
    from atm_mlmm.model_reference import NativeMACE
    native = NativeMACE()
    records = []
    for distance in (.44999, .45, .45001):
        records.append(native.evaluate([6,1], [[0.,0.,0.],[distance,0.,0.]]))
    assert records[0]['directed_edges'] and not records[2]['directed_edges']
    assert abs(records[0]['energy_kj_mol']-records[2]['energy_kj_mol']) <= 1e-4
    np.testing.assert_allclose(records[0]['forces_kj_mol_nm'], records[2]['forces_kj_mol_nm'], atol=5e-3, rtol=0)


@pytest.mark.parametrize('box', (((1.,0.,0.),(.1,1.,0.),(0.,0.,1.)),
                               ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))))
def test_runtime_unsafe_box_rejected(box):
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.schema import UnsupportedCapability
    from tests.link_oracle import REFERENCE
    bundle, snapshot = periodic_case()
    with PhysicalEvaluator(bundle, REFERENCE) as evaluator:
        with pytest.raises(UnsupportedCapability):
            evaluator.evaluate(replace(snapshot, box_nm=box))


def test_ambiguous_bond_image_is_outside_admitted_domain():
    from atm_mlmm.geometry import unwrap_molecules
    from atm_mlmm.schema import NumericalDomainError
    original,_,snapshot = periodic_input()
    x = np.array(snapshot.positions_nm);x[1,0] = x[0,0]+BOX[0][0]/2
    with pytest.raises(NumericalDomainError,match='ambiguous'):
        unwrap_molecules(original.topology,x,BOX)


@pytest.mark.model_assets
def test_wrapped_cap_derivative_fault_is_detected(monkeypatch):
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm import geometry
    from tests.link_oracle import REFERENCE
    bundle,snapshot = periodic_case(real_model=True)
    x = np.array(snapshot.positions_nm);x[:8]+=(3.15,0.,0.)
    frame = replace(snapshot,positions_nm=np.mod(x,np.diag(BOX)))
    with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
        expected = evaluator.evaluate(frame)
        monkeypatch.setattr(geometry,'unwrap_molecules',lambda topology,positions,box:np.array(positions))
        faulty = evaluator.evaluate(frame)
        with pytest.raises(AssertionError):
            np.testing.assert_allclose(faulty.forces_kj_mol_nm,expected.forces_kj_mol_nm,atol=5e-3,rtol=0)


@pytest.mark.model_assets
def test_actual_cap_graph_matches_enumerated_images(monkeypatch):
    from atm_mlmm.models.mace import PinnedASECalculator
    from atm_mlmm.atm import PhysicalEvaluator
    from tests.link_oracle import REFERENCE
    normal = PinnedASECalculator.get_forces
    captures = []
    def capture(calculator,atoms=None):
        batch = calculator._engine()._atoms_to_batch(atoms)
        captures.append((atoms.get_positions()/10.,atoms.get_cell().array/10.,
            {(int(i),int(j),tuple(int(v) for v in shift)) for (i,j),shift in
              zip(batch['edge_index'].T.tolist(),batch['unit_shifts'].tolist())}))
        return normal(calculator,atoms)
    monkeypatch.setattr(PinnedASECalculator,'get_forces',capture)
    bundle,snapshot = periodic_case(real_model=True)
    x = np.array(snapshot.positions_nm);x[:8]+=(3.15,0.,0.)
    with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
        evaluator.evaluate(replace(snapshot,positions_nm=np.mod(x,np.diag(BOX))))
    assert captures
    for positions,box,actual in captures:
        assert len(positions) == len(bundle.model_input_ids) and bundle.model_input_ids[-1].startswith('cap:')
        expected = set()
        for i in range(len(positions)):
            for j in range(len(positions)):
                if i==j:continue
                vector,shift = enumerated_displacement(positions[j]-positions[i],box)
                if np.linalg.norm(vector)<.45:expected.add((i,j,tuple(int(v) for v in shift)))
        assert actual == expected
