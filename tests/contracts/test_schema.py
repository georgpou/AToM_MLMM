from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import pytest

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures/contracts/protocol-v1.json'


def test_versioned_round_trip_and_units():
    from atm_mlmm.schema import from_json, to_json, Units, Snapshot, MalformedInput
    original = json.loads(FIXTURE.read_text())
    record = from_json(FIXTURE.read_text())
    assert record.mobile_groups[0].atom_ids == ('a3', 'a1')
    assert record.mobile_groups[1].atom_ids == ('b1', 'b4', 'b2')
    assert json.loads(to_json(record)) == original
    snapshot = Snapshot(('real-1', 'real-2'), ((0.01, 0.02, 0.03), (0.3, 0.4, 0.5)), None)
    assert from_json(to_json(snapshot)) == snapshot
    assert snapshot.units == Units('nm', 'kJ/mol', 'kJ/mol/nm', 'ps', 'K')
    with pytest.raises(MalformedInput, match='units'):
        Units('angstrom', 'eV', 'eV/angstrom', 'fs', 'K')
    for version in ('2.0', '1.1', '', 1):
        bad = dict(original, schema_version=version)
        with pytest.raises(MalformedInput, match='schema_version'):
            from_json(json.dumps(bad))
    bad = json.loads(FIXTURE.read_text())
    bad['data']['mandatory_future_field'] = 3
    with pytest.raises(MalformedInput, match='mandatory_future_field'):
        from_json(json.dumps(bad))
    bad['data'].pop('mandatory_future_field')
    bad['data'].pop('mobile_groups')
    with pytest.raises(MalformedInput, match='mobile_groups'):
        from_json(json.dumps(bad))


def test_records_own_immutable_data_and_full_real_forces(topology):
    from atm_mlmm.schema import Snapshot, EnergyForces, IdentityError, NumericalDomainError
    from atm_mlmm.identity import validate_force_coverage
    positions = [[0.0, 0.0, 0.0] for _ in topology.atoms]
    ids = tuple(a.atom_id for a in topology.atoms)
    snapshot = Snapshot(ids, positions, None)
    positions[0][0] = 999
    assert snapshot.positions_nm[0][0] == 0
    with pytest.raises(FrozenInstanceError):
        snapshot.box_nm = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    force = EnergyForces(1.5, ids, [[0, 0, 0] for _ in ids], 'physical-a', 'snapshot-a', diagnostics={'max_error': [0.0]})
    validate_force_coverage(force, topology)
    with pytest.raises(TypeError):
        force.diagnostics['max_error'] = 4
    with pytest.raises(TypeError):
        force.diagnostics['max_error'][0] = 4
    with pytest.raises(IdentityError, match='force'):
        validate_force_coverage(replace(force, real_atom_ids=ids[:-1], forces_kj_mol_nm=force.forces_kj_mol_nm[:-1]), topology)
    with pytest.raises(IdentityError, match='force'):
        validate_force_coverage(replace(force, real_atom_ids=tuple(reversed(ids))), topology)
    with pytest.raises(NumericalDomainError, match='nonfinite'):
        replace(force, energy_kj_mol=float('nan'))
    with pytest.raises(ValueError):
        replace(snapshot, box_nm=((0, 0, 0), (0, 0, 0), (0, 0, 0)))


def test_empty_duplicate_wrong_shape_and_unknown_fields_fail():
    from atm_mlmm.schema import Snapshot, MobileGroup, MalformedInput, IdentityError, from_json
    with pytest.raises(MalformedInput):
        MobileGroup('', (), (), '')
    with pytest.raises(IdentityError):
        MobileGroup('a', ('id', 'id'), ('ligand',), 'molecule')
    with pytest.raises(MalformedInput):
        Snapshot(('id',), ((1, 2),), None)
    with pytest.raises(MalformedInput):
        from_json('{"schema_version":"1.0","record_type":"Unimplemented","data":{}}')


def test_protocol_presets_validate_counts_and_disjoint_groups():
    from atm_mlmm.schema import MobileGroup, UnsupportedCapability, IdentityError
    from atm_mlmm.protocols.abfe import make_protocol as abfe
    from atm_mlmm.protocols.rbfe import make_protocol as rbfe
    a = MobileGroup('A', ('a1', 'a2'), ('ligand',), 'a')
    b = MobileGroup('B', ('b1', 'b2', 'b3'), ('ligand',), 'b')
    assert len(abfe((a,), (1, 0, 0)).mobile_groups) == 1
    assert len(rbfe((a, b), (1, 0, 0)).mobile_groups) == 2
    with pytest.raises(UnsupportedCapability, match='one'):
        abfe((a, b), (1, 0, 0))
    with pytest.raises(UnsupportedCapability, match='two'):
        rbfe((a,), (1, 0, 0))
    with pytest.raises(IdentityError, match='overlap'):
        rbfe((a, MobileGroup('B', ('a2',), ('ligand',), 'b')), (1, 0, 0))


def test_system_input_carries_original_identity_units_and_provenance(topology):
    from atm_mlmm.schema import SystemInput, from_json, to_json, MalformedInput, IdentityError
    ids = tuple(a.atom_id for a in topology.atoms)
    original = SystemInput('original-mm.xml', 'a'*64, topology,
                           tuple((0, 0, 0) for _ in ids), None,
                           tuple(12.0 for _ in ids), (('p-a', 'p-b', 0.153),),
                           {'force_field': 'analytic-contract-fixture', 'version': '1'})
    assert from_json(to_json(original)) == original
    with pytest.raises(MalformedInput, match='masses'):
        replace(original, masses_da=())
    with pytest.raises(IdentityError, match='constraint'):
        replace(original, constraints=(('missing', 'p-b', 0.153),))
    with pytest.raises(MalformedInput, match='provenance'):
        replace(original, force_field_provenance={})
