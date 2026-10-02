"""Coordinate finite differences; rebuild the evaluation after each perturbation."""
from dataclasses import replace
import numpy as np

from .schema import MalformedInput


def finite_difference_forces(energy, snapshot, step_nm):
    if not np.isfinite(step_nm) or step_nm <= 0:
        raise MalformedInput('finite-difference step must be positive and finite')
    positions = np.asarray(snapshot.positions_nm, dtype=float)
    result = np.empty_like(positions)
    for atom in range(len(positions)):
        for axis in range(3):
            plus, minus = positions.copy(), positions.copy()
            plus[atom, axis] += step_nm
            minus[atom, axis] -= step_nm
            result[atom, axis] = -(energy(replace(snapshot, positions_nm=plus))-
                                  energy(replace(snapshot, positions_nm=minus)))/(2*step_nm)
    return result
