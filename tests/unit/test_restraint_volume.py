"""Independent radial integrals and explicit S05 correction obligations."""
from dataclasses import replace
import math

import numpy as np
import pytest
from scipy.integrate import quad

RT = .00831446261815324 * 300.


def thermodynamics(*, standard=False, corrections=()):
    from atm_mlmm.schema import ThermodynamicSpec
    return ThermodynamicSpec(
        observable='standard_binding_free_energy' if standard else 'restrained_free_energy',
        endpoint_weights={'zero': -1., 'one': 1.},
        sign_convention='bound_minus_bulk' if standard else 'endpoint_difference',
        state_connections=(('zero', 'one'),),
        endpoint_descriptions={'zero': 'bulk endpoint', 'one': 'bound endpoint'},
        correction_obligations=('translation_standard_state', 'bound_release', 'orientation',
                                'conformation', 'state_counting', 'midpoint_bridge') if standard else (),
        corrections=corrections,
        standard_volume_nm3=1.6605390671738466 if standard else None,
        domain_description='Declared separable infinite-space bulk translation and bound domain',
        restraint_description='Bulk spherical flat bottom; explicit bound release',
        orientation_description='Lab-frame orientation; release status is explicit',
        state_counting_description='One pose, unit symmetry; evidence required')


def test_finite_wall_and_standard_state_sign():
    from atm_mlmm.restraints import finite_wall_volume_nm3, translational_standard_state_correction
    for radius, spring in ((0., 50.), (.2, 50.), (.7, 7.), (.5, 1.e8)):
        a = spring/(2*RT)
        integral = 4*math.pi*(radius**3/3 + quad(
            lambda s: (s+radius)**2*math.exp(-a*s*s), 0., np.inf,
            epsabs=1.e-12, epsrel=1.e-12)[0])
        # Scale the stiff-wall oracle before quadrature so its narrow tail is resolved.
        if spring > 1.e6:
            integral = 4*math.pi*(radius**3/3 + quad(
                lambda t: (t/math.sqrt(a)+radius)**2*math.exp(-t*t)/math.sqrt(a),
                0., np.inf, epsabs=1.e-12)[0])
        actual = finite_wall_volume_nm3(radius, spring, 300., domain='infinite_space')
        assert actual == pytest.approx(integral, rel=1.e-11, abs=1.e-12)
    assert finite_wall_volume_nm3(0., 50., 300., domain='infinite_space') == pytest.approx((2*math.pi*RT/50.)**1.5)
    assert finite_wall_volume_nm3(.5, 1.e20, 300., domain='infinite_space') == pytest.approx(4*math.pi*.5**3/3, rel=1.e-8)
    assert translational_standard_state_correction(2., 300., 1.) == pytest.approx(-RT*math.log(2.))
    assert translational_standard_state_correction(.5, 300., 1.) == pytest.approx(RT*math.log(2.))


@pytest.mark.parametrize('args', ((-.1, 50., 300.), (.1, 0., 300.), (.1, -1., 300.), (.1, 50., 0.), (.1, float('nan'), 300.)))
def test_volume_rejects_invalid_or_undefined_domain(args):
    from atm_mlmm.restraints import finite_wall_volume_nm3
    from atm_mlmm.schema import MalformedInput
    with pytest.raises(MalformedInput):
        finite_wall_volume_nm3(*args, domain='infinite_space')
    with pytest.raises(ValueError, match='domain'):
        finite_wall_volume_nm3(.1, 50., 300., domain='periodic_box')


def test_required_correction_cannot_default_to_zero():
    from atm_mlmm.analysis import combine_free_energies
    from atm_mlmm.schema import CorrectionRecord, MalformedInput, from_json, to_json
    spec = thermodynamics(standard=True)
    result = combine_free_energies(('zero', 'one'), (0., 1.5), ((0., 0.), (0., .04)), spec)
    assert result.restrained_kj_mol == 1.5
    assert result.restrained_standard_error_kj_mol == .2
    assert result.final_kj_mol is None
    assert set(result.unresolved_corrections) == set(spec.correction_obligations)
    with pytest.raises(MalformedInput, match='evidence'):
        CorrectionRecord('orientation', 'zero_demonstrated', 0., 0., '')
    with pytest.raises(MalformedInput):
        CorrectionRecord('orientation', 'required_uncomputed', 0., 0., '')
    corrections = tuple(CorrectionRecord(name, 'zero_demonstrated', 0., 0., 'fixture proof: '+name)
                        for name in spec.correction_obligations)
    corrections = (CorrectionRecord('translation_standard_state', 'computed', -RT*math.log(2.), 0.,
                                    'independent Veff=2 Vstandard'),) + corrections[1:]
    complete = replace(spec, corrections=corrections)
    assert from_json(to_json(complete)) == complete
    finished = combine_free_energies(('zero', 'one'), (0., 1.5), ((0., 0.), (0., .04)), complete)
    assert finished.final_kj_mol == pytest.approx(1.5-RT*math.log(2.))
    assert finished.final_standard_error_kj_mol == .2
    # An uncertain correction without joint covariance must not gain a final error bar.
    uncertain = replace(corrections[1], status='computed', value_kj_mol=.2, standard_error_kj_mol=.1)
    result = combine_free_energies(('zero', 'one'), (0., 1.5), ((0., 0.), (0., .04)),
                                  replace(complete, corrections=(corrections[0], uncertain)+corrections[2:]))
    assert result.final_kj_mol is None
    assert 'correction_covariance' in result.unresolved_corrections


def test_endpoint_weights_and_covariance_are_explicit():
    from atm_mlmm.analysis import combine_free_energies
    from atm_mlmm.schema import MalformedInput
    covariance = np.array([[.09, .08], [.08, .16]])
    spec = thermodynamics()
    result = combine_free_energies(('zero', 'one'), (17., 18.5), covariance, spec)
    assert result.restrained_kj_mol == 1.5
    assert result.restrained_standard_error_kj_mol == pytest.approx(.3)
    reverse = replace(spec, endpoint_weights={'zero': 1., 'one': -1.})
    assert combine_free_energies(('zero', 'one'), (17., 18.5), covariance, reverse).restrained_kj_mol == -1.5
    with pytest.raises(MalformedInput, match='weights'):
        replace(spec, endpoint_weights={'zero': 1., 'one': 1.})
    with pytest.raises(MalformedInput):
        combine_free_energies(('zero', 'one'), (0., 1.), ((1., 2.), (2., 1.)), spec)


def test_joint_correction_covariance_controls_final_uncertainty():
    from atm_mlmm.analysis import combine_free_energies
    from atm_mlmm.schema import CorrectionRecord, IdentityError
    spec = thermodynamics(standard=True)
    corrections = tuple(CorrectionRecord(name, 'zero_demonstrated', 0., 0., 'independent fixture proof')
                        for name in spec.correction_obligations)
    corrections = (corrections[0], CorrectionRecord('bound_release', 'computed', .3, .3, 'joint sampled release'))+corrections[2:]
    spec = replace(spec, corrections=corrections)
    joint = np.zeros((8, 8))
    joint[1, 1], joint[3, 3] = .04, .09
    joint[1, 3] = joint[3, 1] = -.03
    result = combine_free_energies(('zero', 'one'), (0., 1.5), ((0., 0.), (0., .04)), spec,
                                   joint_covariance_kj2_mol2=joint)
    assert result.final_kj_mol == 1.8
    assert result.final_standard_error_kj_mol == pytest.approx(math.sqrt(.04+.09-2*.03))
    wrong = joint.copy()
    wrong[3, 3] = .16
    with pytest.raises(IdentityError, match='correction errors'):
        combine_free_energies(('zero', 'one'), (0., 1.5), ((0., 0.), (0., .04)), spec,
                              joint_covariance_kj2_mol2=wrong)
