"""Local additivity is asserted only on the pinned ML energy contribution."""
import numpy as np
import pytest

from tests.integration.test_model_adapter import real_case, assert_agree, capture
from tests.model_oracle import derived_input

pytestmark = pytest.mark.model_assets


def test_declared_local_component_additivity():
    from atm_mlmm.model_reference import NativeMACE
    native = NativeMACE()
    bundle, snapshot = real_case()
    numbers, x, _ = derived_input(bundle, snapshot)
    # Actual legacy raw order is the five ligand atoms followed by four real
    # protein-side atoms and the derived hydrogen cap. Freeze that identity.
    assert bundle.model_input_ids[:5] == ('l10', 'l11', 'l12', 'l8', 'l9')
    contacting = native.evaluate(numbers, x)
    assert any((i < 5) != (j < 5) for i, j in contacting['directed_edges'])
    parts_contact = [native.evaluate(numbers[:5], x[:5]), native.evaluate(numbers[5:], x[5:])]
    # Deliberately constructing two independent graphs removes contact edges.
    split_energy = sum(p['energy_kj_mol'] for p in parts_contact)
    split_forces = np.vstack([p['forces_kj_mol_nm'] for p in parts_contact])
    with pytest.raises(AssertionError):
        assert_agree(split_energy, split_forces, contacting['energy_kj_mol'], contacting['forces_kj_mol_nm'])
    separated_x = x.copy(); separated_x[:5] += (0., 2., 0.)
    separated = native.evaluate(numbers, separated_x)
    assert not any((i < 5) != (j < 5) for i, j in separated['directed_edges'])
    parts = [native.evaluate(numbers[:5], separated_x[:5]), native.evaluate(numbers[5:], separated_x[5:])]
    assert_agree(separated['energy_kj_mol'], separated['forces_kj_mol_nm'],
                 sum(p['energy_kj_mol'] for p in parts), np.vstack([p['forces_kj_mol_nm'] for p in parts]))
    capture('locality', {'scope': 'ML energy only, total energy with compatible atom references',
                        'contacting': contacting, 'deliberately_split_contact_parts': parts_contact,
                        'separated': separated, 'separate_components': parts})
