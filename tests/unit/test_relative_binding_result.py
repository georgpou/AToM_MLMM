"""S05 relative standard binding records use an explicit B-minus-A sign."""

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from atm_mlmm.analysis import combine_free_energies
from atm_mlmm.schema import (BindingResult, CorrectionRecord, MalformedInput,
                             ThermodynamicSpec, from_json, to_json)


OBLIGATIONS = ('translation_standard_state', 'bound_release', 'orientation',
               'conformation', 'state_counting', 'midpoint_bridge')


def correction_ledger(*, unresolved=None, translation=None, release=None):
    rows = []
    for name in OBLIGATIONS:
        if name == unresolved:
            rows.append(CorrectionRecord(name, 'required_uncomputed', None, None, ''))
        elif name == 'translation_standard_state' and translation is not None:
            rows.append(CorrectionRecord(name, 'computed', translation[0], translation[1],
                                         'analytic A-minus-B standard-volume difference'))
        elif name == 'bound_release' and release is not None:
            rows.append(CorrectionRecord(name, 'computed', release[0], release[1],
                                         'joint endpoint release calculation'))
        else:
            rows.append(CorrectionRecord(name, 'zero_demonstrated', 0., 0.,
                                         'matched endpoint evidence: '+name))
    return tuple(rows)


def relative_spec(*, corrections=None, endpoint_weights=None, endpoint_descriptions=None):
    return ThermodynamicSpec(
        'relative_standard_binding_free_energy',
        endpoint_weights or {'state-alpha': 1., 'state-zulu': -1.},
        'B_minus_A', (('state-zulu', 'bridge-state'), ('bridge-state', 'state-alpha')),
        endpoint_descriptions or {'state-zulu': 'ligand A bound endpoint',
                                  'state-alpha': 'ligand B bound endpoint'},
        OBLIGATIONS, correction_ledger() if corrections is None else corrections,
        1.6605390671738466, 'matched domain and standard-state box',
        'explicitly matched translational restraints', 'matched orientation convention',
        'explicit one-pose state-counting convention')


def test_relative_standard_definition_accepts_explicit_b_minus_a_endpoints():
    spec = relative_spec(corrections=correction_ledger(unresolved='translation_standard_state'))

    assert spec.endpoint_weights == {'state-alpha': 1., 'state-zulu': -1.}
    assert spec.sign_convention == 'B_minus_A'
    assert spec.standard_volume_nm3 == pytest.approx(1.6605390671738466)


def test_relative_definition_rejects_implicit_sign_volume_or_correction_obligations():
    spec = relative_spec()
    for changes in (
        {'sign_convention': 'endpoint_difference'},
        {'endpoint_weights': {'state-alpha': .5, 'state-zulu': -.5}},
        {'standard_volume_nm3': None},
        {'correction_obligations': OBLIGATIONS[:-1], 'corrections': correction_ledger()[:-1]},
    ):
        with pytest.raises(MalformedInput):
            replace(spec, **changes)


def test_relative_value_uses_declared_physical_endpoints_and_is_gauge_invariant():
    spec = relative_spec()
    ids = ('state-zulu', 'bridge-state', 'state-alpha')
    energies = (0., 19., 1.5)
    covariance = np.diag((.02, .03, .08))
    forward = combine_free_energies(ids, energies, covariance, spec)
    shifted = combine_free_energies(ids, np.asarray(energies)+87.25, covariance, spec)
    assert forward.restrained_kj_mol == pytest.approx(1.5)
    assert shifted.restrained_kj_mol == pytest.approx(1.5)
    assert forward.final_kj_mol == pytest.approx(1.5)
    assert forward.final_standard_error_kj_mol == pytest.approx(np.sqrt(.10))

    # IDs sort in an order that carries no endpoint meaning. The explicit
    # endpoint descriptions and weights preserve B-minus-A when state order flips.
    reversed_spec = relative_spec(
        endpoint_weights={'state-zulu': 1., 'state-alpha': -1.},
        endpoint_descriptions={'state-zulu': 'ligand B bound endpoint',
                               'state-alpha': 'ligand A bound endpoint'})
    reverse = combine_free_energies(('state-alpha', 'bridge-state', 'state-zulu'),
                                    (1.5, 19., 0.), covariance[::-1, ::-1], reversed_spec)
    assert reverse.restrained_kj_mol == pytest.approx(-1.5)
    assert reverse.final_kj_mol == pytest.approx(-1.5)


def test_relative_corrections_are_signed_and_need_joint_covariance():
    ledger = correction_ledger(translation=(-.4, 0.), release=(.2, .3))
    spec = relative_spec(corrections=ledger)
    state_covariance = np.zeros((3, 3))
    state_covariance[0, 0], state_covariance[2, 2], state_covariance[0, 2] = .04, .01, .01
    state_covariance[2, 0] = .01
    withheld = combine_free_energies(('state-alpha', 'bridge-state', 'state-zulu'),
                                     (1.5, 12., 0.), state_covariance, spec)
    assert withheld.restrained_kj_mol == pytest.approx(1.5)
    assert withheld.final_kj_mol is None
    assert withheld.unresolved_corrections == ('correction_covariance',)

    joint = np.zeros((3+len(ledger), 3+len(ledger)))
    joint[:3, :3] = state_covariance
    joint[4, 4] = .3**2  # bound_release follows translation_standard_state.
    joint[0, 4] = joint[4, 0] = -.01
    final = combine_free_energies(('state-alpha', 'bridge-state', 'state-zulu'),
                                 (1.5, 12., 0.), state_covariance, spec,
                                 joint_covariance_kj2_mol2=joint)
    assert final.final_kj_mol == pytest.approx(1.3)
    assert final.final_standard_error_kj_mol == pytest.approx(np.sqrt(.10))
    assert from_json(to_json(final)) == final


@pytest.mark.parametrize('missing', OBLIGATIONS)
def test_every_uncomputed_relative_correction_withholds_final(missing):
    spec = relative_spec(corrections=correction_ledger(unresolved=missing))
    result = combine_free_energies(('state-alpha', 'bridge-state', 'state-zulu'),
                                   (1.5, 12., 0.), np.eye(3), spec)
    assert result.final_kj_mol is None
    assert missing in result.unresolved_corrections


def test_relative_result_admission_rejects_serialization_bypass_and_legacy_final():
    spec = relative_spec()
    result = combine_free_energies(('state-zulu', 'bridge-state', 'state-alpha'),
                                   (0., 12., 1.5), np.eye(3), spec)
    assert from_json(to_json(result)) == result

    payload = json.loads(to_json(result))
    payload['data']['final_kj_mol'] = -1.5
    with pytest.raises(MalformedInput):
        from_json(json.dumps(payload))

    with pytest.raises(MalformedInput):
        BindingResult(1.5, .2, (), (), 1.5, .2, 'unverified-relative-definition')


def test_matched_a_to_a_control_is_zero_compatible_with_nonzero_instantaneous_difference():
    from scipy.integrate import quad

    spec = relative_spec(endpoint_descriptions={
        'state-zulu': 'ligand A; same spectator, box, cavity, constraints, and restraints',
        'state-alpha': 'ligand A; same spectator, box, cavity, constraints, and restraints'})
    result = combine_free_energies(('state-zulu', 'bridge-state', 'state-alpha'),
                                   (7.25, 10., 7.25), np.diag((.02, .03, .08)), spec)
    assert result.restrained_kj_mol == pytest.approx(0.)
    assert result.final_kj_mol == pytest.approx(0.)

    # Two identical harmonic ligands exchange opposite fixed translations.
    # Each coordinate integral is invariant under a change of variables,
    # while this specific instantaneous configuration has nonzero delta U.
    rt, k, displacement = .00831446261815324*300., 100., .3
    base = quad(lambda x: math.exp(-.5*k*x*x/rt), -np.inf, np.inf)[0]
    shifted = quad(lambda x: math.exp(-.5*k*(x+displacement)**2/rt), -np.inf, np.inf)[0]
    two_ligand_partition_ratio = (shifted/base)**2
    instantaneous_delta = .5*k*displacement**2 + .5*k*displacement**2
    assert -rt*math.log(two_ligand_partition_ratio) == pytest.approx(0., abs=1.e-12)
    assert instantaneous_delta == pytest.approx(9.)


def test_d_e_relative_ledger_template_keeps_all_molecular_corrections_uncomputed():
    fixture = (Path(__file__).resolve().parents[2]/
               'fixtures/analytic/exchange-analysis-v1/relative-binding-template.json')
    spec = from_json(fixture.read_text())
    assert isinstance(spec, ThermodynamicSpec)
    assert spec.observable == 'relative_standard_binding_free_energy'
    assert spec.sign_convention == 'B_minus_A'
    assert set(spec.correction_obligations) == set(OBLIGATIONS)
    assert {item.status for item in spec.corrections} == {'required_uncomputed'}
    assert all(item.value_kj_mol is None and item.standard_error_kj_mol is None
               for item in spec.corrections)
