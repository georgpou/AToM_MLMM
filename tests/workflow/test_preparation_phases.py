"""Bounded phases preserve all-active physical identity and explicit settings."""
from dataclasses import replace
import numpy as np
import pytest
import openmm as mm
from openmm import unit
from tests.analytic_oracle import case, REFERENCE


def test_explicit_phases_keep_physical_hamiltonian_and_full_forces():
    from atm_mlmm.prepare import prepare_phases
    from atm_mlmm.atm import PhysicalEvaluator
    physical, _, _, _, snapshot = case(marker=20.)
    result = prepare_phases(physical, snapshot, REFERENCE,
                            temperatures_K=(10., 100., 300.), steps_per_phase=2,
                            minimization_iterations=10, seed=41)
    assert result['physical_identity'] == physical.content_identity
    assert [p['temperature_K'] for p in result['phases']] == [10., 100., 300.]
    assert all(p['timestep_ps'] == .0005 and p['integration_groups'] == [0] for p in result['phases'])
    state = mm.XmlSerializer.deserialize(result['state_xml'])
    final = result['snapshot']
    assert np.isfinite(final.positions_nm).all()
    with PhysicalEvaluator(physical, REFERENCE) as direct:
        value = direct.evaluate(final)
        assert np.isfinite(value.forces_kj_mol_nm).all()
        assert value.energy_kj_mol == pytest.approx(result['phases'][-1]['energy_kj_mol'], abs=1.e-8)
    assert np.array(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)).shape == (len(physical.masses_da),3)


def test_bad_phase_settings_reject_before_context():
    from atm_mlmm.prepare import prepare_phases
    from atm_mlmm.schema import MalformedInput
    physical, _, _, _, snapshot = case()
    for changes in ({'temperatures_K':(300.,10.)}, {'temperatures_K':(10.,200.)},
                    {'steps_per_phase':-1}, {'minimization_iterations':0}, {'seed':0}):
        with pytest.raises(MalformedInput):
            prepare_phases(physical, snapshot, REFERENCE, **changes)


def test_phase_seeds_are_applied_before_context_initialization():
    from atm_mlmm.prepare import prepare_phases
    physical, _, _, _, snapshot = case()
    a = prepare_phases(physical,snapshot,REFERENCE,seed=73)
    b = prepare_phases(physical,snapshot,REFERENCE,seed=73)
    c = prepare_phases(physical,snapshot,REFERENCE,seed=109)
    assert a['snapshot'].positions_nm == b['snapshot'].positions_nm
    assert a['state_xml'] == b['state_xml']
    assert a['snapshot'].positions_nm != c['snapshot'].positions_nm
