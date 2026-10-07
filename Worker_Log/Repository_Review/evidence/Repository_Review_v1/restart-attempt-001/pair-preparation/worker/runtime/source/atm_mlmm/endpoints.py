"""Independent-reference comparison with component-level diagnostics."""
import numpy as np

from .schema import QualificationError


def check_reference(evaluation, *, u0, u1, expression, outside, forces,
                     energy_tolerance=1e-8, force_tolerance=1e-7):
    comparisons = dict(u0=(evaluation.raw.u0_raw_kJ_mol, u0),
                       u1=(evaluation.raw.u1_raw_kJ_mol, u1),
                       expression=(evaluation.raw.atm_expression_energy_kJ_mol, expression),
                       outside=(evaluation.raw.outside_energy_kJ_mol, outside),
                       total=(evaluation.total.energy_kj_mol, expression+outside))
    errors = {}
    for name, (actual, expected) in comparisons.items():
        error = abs(actual-expected)
        if not np.isfinite(expected) or error > energy_tolerance:
            raise QualificationError(f'{name} energy mismatch: {actual} vs {expected}, error {error}')
        errors[name+'_error_kJ_mol'] = error
    actual, expected = np.asarray(evaluation.total.forces_kj_mol_nm), np.asarray(forces)
    if actual.shape != expected.shape or not np.isfinite(expected).all():
        raise QualificationError('force reference must cover every real coordinate')
    difference = np.abs(actual-expected)
    index = np.unravel_index(np.argmax(difference), difference.shape)
    maximum = float(difference[index])
    if maximum > force_tolerance:
        raise QualificationError(f'force mismatch at {evaluation.total.real_atom_ids[index[0]]}, axis {index[1]}: error {maximum}')
    errors['max_force_error_kJ_mol_nm'] = maximum
    return errors
