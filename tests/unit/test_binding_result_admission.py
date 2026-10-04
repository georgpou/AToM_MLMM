"""Final binding records must independently enforce S05 correction completeness."""
from dataclasses import replace
import json

import numpy as np
import pytest

from atm_mlmm.analysis import combine_free_energies
from atm_mlmm.schema import (BindingResult, CorrectionRecord,
                             MalformedInput, ThermodynamicSpec, from_json, to_json)

OBLIGATIONS = ('translation_standard_state', 'bound_release', 'orientation',
               'conformation', 'state_counting', 'midpoint_bridge')


def definition(corrections=()):
    return ThermodynamicSpec('standard_binding_free_energy', {'bulk': -1., 'bound': 1.},
        'bound_minus_bulk', (('bulk', 'bound'),), {'bulk': 'bulk', 'bound': 'bound'},
        OBLIGATIONS, corrections, 1.6605390671738466, 'separable test domains',
        'explicit test restraints', 'explicit orientation release', 'one test pose')


def resolved():
    return tuple(CorrectionRecord(name, 'zero_demonstrated', 0., 0.,
                                 'independent test proof: '+name) for name in OBLIGATIONS)


def produce(spec, **kwargs):
    return combine_free_energies(('bulk', 'bound'), (0., 1.5), ((0., 0.), (0., .04)), spec, **kwargs)


def nested(record):
    payload = json.loads(to_json(record))
    payload.pop('schema_version')
    return payload


def test_final_requires_embedded_thermodynamic_definition():
    with pytest.raises(MalformedInput):
        BindingResult(1.5, .2, (), (), 1.5, .2, 'unverified-definition')
    partial = produce(definition())
    payload = json.loads(to_json(partial))
    payload['data'].update(final_kj_mol=1.5, final_standard_error_kj_mol=.2,
                           unresolved_corrections=[])
    payload['data'].pop('thermodynamics', None)
    with pytest.raises(MalformedInput):
        from_json(json.dumps(payload))


def test_final_definition_identity_observable_and_ordered_ledger_match():
    result = produce(definition(resolved()))
    assert result.thermodynamics.content_identity == result.thermodynamic_identity
    assert from_json(to_json(result)) == result
    for changes in (
        {'thermodynamics': None}, {'thermodynamic_identity': 'different-definition'},
        {'thermodynamics': replace(result.thermodynamics, observable='restrained_free_energy')},
        {'corrections': ()}, {'corrections': result.corrections[::-1]},
        {'corrections': result.corrections+(result.corrections[0],)},
        {'unresolved_corrections': ('orientation',)}, {'final_kj_mol': 2.},
    ):
        with pytest.raises(MalformedInput):
            replace(result, **changes)
        payload = json.loads(to_json(result))
        for key, value in changes.items():
            if isinstance(value, ThermodynamicSpec):
                value = nested(value)
            elif key == 'corrections':
                value = [nested(c) for c in value]
            payload['data'][key] = value
        with pytest.raises(MalformedInput):
            from_json(json.dumps(payload))
    for missing in OBLIGATIONS:
        ledger = tuple(c for c in result.corrections if c.correction_id != missing)
        spec = replace(result.thermodynamics, corrections=ledger)
        with pytest.raises(MalformedInput):
            replace(result, corrections=ledger, thermodynamics=spec,
                    thermodynamic_identity=spec.content_identity)
        payload = json.loads(to_json(result))
        payload['data'].update(corrections=[nested(c) for c in ledger],
                               thermodynamics=nested(spec), thermodynamic_identity=spec.content_identity)
        with pytest.raises(MalformedInput):
            from_json(json.dumps(payload))


def test_uncomputed_correction_cannot_hide_its_unresolved_status():
    ledger = (CorrectionRecord(OBLIGATIONS[0], 'required_uncomputed', None, None, ''),)+resolved()[1:]
    partial = produce(definition(ledger))
    assert partial.final_kj_mol is None
    with pytest.raises(MalformedInput):
        replace(partial, final_kj_mol=1.5, final_standard_error_kj_mol=.2,
                unresolved_corrections=())
    payload = json.loads(to_json(partial))
    payload['data'].update(final_kj_mol=1.5, final_standard_error_kj_mol=.2,
                           unresolved_corrections=[])
    with pytest.raises(MalformedInput):
        from_json(json.dumps(payload))
    with pytest.raises(MalformedInput):
        replace(partial, unresolved_corrections=('unknown',))


def test_partial_and_covariance_aware_final_round_trips():
    partial = produce(definition())
    assert from_json(to_json(partial)) == partial
    legacy = json.loads(to_json(partial))
    legacy['data'].pop('thermodynamics', None)
    old_payload = json.dumps(legacy, sort_keys=True, allow_nan=False)
    loaded = from_json(old_payload)
    assert loaded.thermodynamics is None and loaded.final_kj_mol is None
    assert to_json(loaded) == old_payload
    ledger = resolved()
    ledger = (ledger[0], CorrectionRecord('bound_release', 'computed', .3, .3,
                                         'joint sampled release proof'))+ledger[2:]
    spec = definition(ledger)
    withheld = produce(spec)
    assert withheld.unresolved_corrections == ('correction_covariance',)
    assert from_json(to_json(withheld)) == withheld
    joint = np.zeros((8, 8))
    joint[1, 1], joint[3, 3] = .04, .09
    joint[1, 3] = joint[3, 1] = -.03
    final = produce(spec, joint_covariance_kj2_mol2=joint)
    assert final.final_kj_mol == pytest.approx(1.8)
    assert final.final_standard_error_kj_mol == pytest.approx(np.sqrt(.07))
    assert from_json(to_json(final)) == final
