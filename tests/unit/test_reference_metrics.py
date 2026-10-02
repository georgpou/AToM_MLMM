"""Independent known-number checks of chemical metrics, never a quantum substitute."""
import numpy as np
import pytest


def test_fixed_composition_zeros_and_force_maximum():
    from atm_mlmm.chemical_reference import relative_errors, force_metrics
    # A composition-specific huge atom-reference shift cancels. The maximum
    # must catch a localized defect even when Cartesian RMS is small.
    result=relative_errors([1000.,1002.,1005.],[-300.,-299.,-295.],0)
    np.testing.assert_allclose(result,[0.,1.,0.],atol=1e-12)
    forces=np.zeros((100,3));forces[37]=[.12,.16,0.]
    rms,maximum=force_metrics(forces,np.zeros_like(forces))
    assert maximum==pytest.approx(.2)
    assert rms==pytest.approx(.2/np.sqrt(300.))


def test_missing_quantum_data_fail_closed(tmp_path):
    from atm_mlmm.chemical_reference import load_references
    from atm_mlmm.schema import IdentityError
    with pytest.raises(IdentityError,match='quantum reference'):
        load_references(tmp_path)


def test_force_metric_cannot_broadcast_missing_atoms():
    from atm_mlmm.chemical_reference import force_metrics
    from atm_mlmm.schema import IdentityError
    with pytest.raises(IdentityError,match='Cartesian'):
        force_metrics(np.ones((1,3)),np.ones((2,3)))
