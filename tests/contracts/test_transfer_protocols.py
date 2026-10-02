from dataclasses import replace

import numpy as np
import pytest

from tests.analytic_oracle import FIXTURE, REFERENCE, case, check, expected_linear


@pytest.mark.parametrize('kind', ('abfe', 'rbfe'))
def test_one_and_two_unequal_mobile_groups(kind):
    from atm_mlmm.atm import build_atm, evaluate_atm
    physical, transfer, schedule, restraints, snapshot = case(kind)
    assert len(transfer.displacement0_nm) == len(transfer.displacement1_nm) == 7
    assert transfer.displacement0_nm == ((0., 0., 0.),)*7
    assert transfer.displacement1_nm == tuple(map(tuple, FIXTURE[kind+'_map1_nm']))
    assert len(transfer.protocol.mobile_groups) == (1 if kind == 'abfe' else 2)
    alchemical = build_atm(physical, transfer, schedule, restraints)
    check(evaluate_atm(alchemical, snapshot, 'middle', REFERENCE), expected_linear(snapshot, kind, .37))


def test_nonidentity_old_to_new_and_record_roundtrip():
    from atm_mlmm.atm import build_atm, evaluate_atm
    from atm_mlmm.schema import from_json, to_json
    permutation = (6, 2, 4, 0, 5, 1, 3)
    physical, transfer, schedule, restraints, snapshot = case('rbfe', old_to_new=permutation)
    assert tuple(physical.real_to_final[a] for a in snapshot.real_atom_ids) == permutation
    assert physical.model_to_final['a1'] == 4
    for original, final in enumerate(permutation):
        assert transfer.displacement1_nm[final] == tuple(FIXTURE['rbfe_map1_nm'][original])
    alchemical = build_atm(physical, transfer, schedule, restraints)
    for record in (physical, transfer, schedule, restraints, alchemical):
        assert from_json(to_json(record)) == record
    check(evaluate_atm(alchemical, snapshot, 'middle', REFERENCE), expected_linear(snapshot, 'rbfe', .37))


def test_reject_incomplete_membership_maps_and_unsupported_geometry():
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.schema import IdentityError, MalformedInput, UnsupportedCapability
    physical, transfer, _, _, _ = case()
    protocol = transfer.protocol
    partial = replace(protocol, mobile_groups=(replace(protocol.mobile_groups[0], atom_ids=('a1',)),))
    with pytest.raises(UnsupportedCapability, match='complete'):
        resolve_protocol(physical, partial)
    with pytest.raises(UnsupportedCapability, match='ML'):
        resolve_protocol(replace(physical, ml_atom_ids=('protein',), model_to_final={'protein': 4}), protocol)
    with pytest.raises(UnsupportedCapability, match='geometry'):
        resolve_protocol(physical, replace(protocol, geometry_requests={'rotation': 30.}))
    with pytest.raises((IdentityError, MalformedInput), match='map|particle'):
        replace(transfer, displacement1_nm=transfer.displacement1_nm[:-1])
    with pytest.raises((IdentityError, MalformedInput), match='map|index'):
        replace(physical, real_to_final={a: 0 for a in physical.real_to_final})


def test_owned_records_and_nonfinite_rejection():
    from atm_mlmm.schema import NumericalDomainError
    physical, transfer, _, _, _ = case()
    source = [list(v) for v in transfer.displacement1_nm]
    copied = replace(transfer, displacement1_nm=source)
    source[0][0] = 999.
    assert copied.displacement1_nm[0][0] == .1
    with pytest.raises(TypeError):
        physical.real_to_final['a1'] = 0
    source[0][0] = float('nan')
    with pytest.raises(NumericalDomainError):
        replace(transfer, displacement1_nm=source)


def test_second_group_has_nonzero_mapped_force():
    from atm_mlmm.atm import build_atm, evaluate_atm
    physical, transfer, schedule, restraints, snapshot = case('rbfe')
    alchemical = build_atm(physical, transfer, schedule, restraints)
    first = evaluate_atm(alchemical, snapshot, 'initial', REFERENCE)
    last = evaluate_atm(alchemical, snapshot, 'final', REFERENCE)
    for i in (3, 6, 5):
        assert np.linalg.norm(first.total.forces_kj_mol_nm[i]) > .1
        assert not np.allclose(first.total.forces_kj_mol_nm[i], last.total.forces_kj_mol_nm[i], atol=1e-7, rtol=0)
