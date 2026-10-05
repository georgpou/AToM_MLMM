"""Failed sampling retains both map coordinates without energy reentry."""
import numpy as np
import openmm as mm
from openmm import unit
import pytest

from tests.workflow.test_engine_failure_retention import test_advanced_actual_worker_failure_is_archived as _challenge


@pytest.mark.parametrize('origin', ('integration', 'final_state'))
def test_failure_retains_both_mapped_coordinates(tmp_path, monkeypatch, origin):
    from atm_mlmm.schema import from_json
    _challenge(tmp_path, monkeypatch, origin)
    directory = tmp_path / 'attempt'
    bundle = from_json((directory / 'worker/bundle.json').read_text())
    failed = directory / 'failure-000000'
    original = mm.XmlSerializer.deserialize((failed / 'state.xml').read_text())
    for label, displacement in (('map0', bundle.transfer.displacement0_nm), ('map1', bundle.transfer.displacement1_nm)):
        state = mm.XmlSerializer.deserialize((failed / f'{label}-state.xml').read_text())
        expected = original.getPositions(asNumpy=True).value_in_unit(unit.nanometer)+np.array(displacement)
        np.testing.assert_array_equal(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer), expected)
        np.testing.assert_array_equal(state.getVelocities(asNumpy=True), original.getVelocities(asNumpy=True))
        assert state.getPeriodicBoxVectors() == original.getPeriodicBoxVectors()
