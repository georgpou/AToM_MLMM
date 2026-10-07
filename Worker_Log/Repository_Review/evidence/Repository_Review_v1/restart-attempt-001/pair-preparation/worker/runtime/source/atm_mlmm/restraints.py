"""S05 separable translational integrals; coupled/periodic domains reject."""
import math
from numbers import Real

from .schema import MalformedInput, NumericalDomainError, UnsupportedCapability

MOLAR_GAS_CONSTANT_KJ_MOL_K = .00831446261815324


def _positive(value, name, *, zero=False):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise NumericalDomainError(f'{name}: finite real value required')
    if value < 0 if zero else value <= 0:
        raise MalformedInput(f'{name}: positive value required')


def finite_wall_volume_nm3(radius_nm, spring_kj_mol_nm2, temperature_K, *, domain):
    """Full 4pi radial integral for a flat bottom plus harmonic exterior.

    Only an explicitly justified infinite-space separable domain is admitted.
    A caller must not use this approximation for a finite periodic domain.
    """
    if domain != 'infinite_space':
        raise UnsupportedCapability('finite-wall domain must be declared infinite_space')
    _positive(radius_nm, 'radius_nm', zero=True)
    _positive(spring_kj_mol_nm2, 'spring_kj_mol_nm2')
    _positive(temperature_K, 'temperature_K')
    a = spring_kj_mol_nm2/(2*MOLAR_GAS_CONSTANT_KJ_MOL_K*temperature_K)
    width = 1/math.sqrt(a)
    volume = 4*math.pi*(radius_nm**3/3 + radius_nm**2*math.sqrt(math.pi)*width/2
                        + radius_nm*width**2 + math.sqrt(math.pi)*width**3/4)
    if not math.isfinite(volume) or volume <= 0:
        raise NumericalDomainError('finite-wall volume is nonfinite or nonpositive')
    return volume


def translational_standard_state_correction(volume_nm3, temperature_K, standard_volume_nm3):
    """-RT ln(Veff/Vstandard) under the declared bound-minus-bulk convention."""
    for value, name in ((volume_nm3, 'volume_nm3'), (temperature_K, 'temperature_K'),
                        (standard_volume_nm3, 'standard_volume_nm3')):
        _positive(value, name)
    return -MOLAR_GAS_CONSTANT_KJ_MOL_K*temperature_K*(math.log(volume_nm3)-math.log(standard_volume_nm3))
