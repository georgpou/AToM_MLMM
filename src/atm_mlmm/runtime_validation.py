"""Dependency-light checks shared by worker loading and restart admission."""
from collections.abc import Mapping
import hashlib
import math
from pathlib import Path
import re

from .schema import IdentityError


_SOURCE_PREFIX = 'runtime/source/atm_mlmm/'
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def verify_source_inventory(bundle_root: Path, manifest_files: Mapping[str, str], *,
                            current_source_root: Path) -> None:
    """Require a complete recursive source inventory and verify every artifact.

    This check deliberately imports no executable bundle or scientific backend.
    Bundle locations may move as long as all relative paths and bytes remain
    unchanged.
    """
    if not isinstance(manifest_files, Mapping):
        raise IdentityError('worker manifest files must be a path-to-digest mapping')
    root = Path(bundle_root).resolve()
    source_root = Path(current_source_root).resolve()
    if not root.is_dir() or not source_root.is_dir():
        raise IdentityError('worker bundle/source root is unavailable')

    for name, digest in manifest_files.items():
        if (not isinstance(name, str) or not name or '\\' in name or
                not isinstance(digest, str) or _SHA256.fullmatch(digest) is None):
            raise IdentityError('worker manifest contains a malformed artifact path or SHA-256')
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise IdentityError(f'worker artifact path escapes bundle: {name}')
        candidate = root
        for part in relative.parts:
            candidate = candidate/part
            if candidate.is_symlink():
                raise IdentityError(f'worker artifact path contains a symbolic link: {name}')
        resolved = candidate.resolve()
        if root not in resolved.parents or not resolved.is_file():
            raise IdentityError(f'worker artifact path is outside the bundle or missing: {name}')
        if hashlib.sha256(resolved.read_bytes()).hexdigest() != digest:
            raise IdentityError(f'worker file artifact hash mismatch: {name}')

    declared_source = {
        name for name in manifest_files
        if name.startswith(_SOURCE_PREFIX) and name.endswith('.py')
    }
    current_paths = sorted(source_root.rglob('*.py'))
    if any(path.is_symlink() for path in current_paths):
        raise IdentityError('current Python source tree contains a symbolic link')
    current_source = {
        _SOURCE_PREFIX + path.relative_to(source_root).as_posix()
        for path in current_paths
    }
    if declared_source != current_source:
        raise IdentityError('worker source inventory differs from the complete current Python source tree')

    for name in sorted(current_source):
        bundled_digest = manifest_files[name]
        current_path = source_root/name[len(_SOURCE_PREFIX):]
        if not current_path.is_file() or hashlib.sha256(current_path.read_bytes()).hexdigest() != bundled_digest:
            raise IdentityError(f'worker source differs from current source: {name}')


def portable_state_clock(portable_state_xml: str) -> tuple[int, float]:
    """Read exact step/time identity from a portable OpenMM State."""
    import xml.etree.ElementTree as ET
    import openmm as mm
    from openmm import unit

    try:
        root = ET.fromstring(portable_state_xml)
        if root.tag != 'State':
            raise IdentityError('portable artifact must be a State')
        state = mm.XmlSerializer.deserialize(portable_state_xml)
        step = state.getStepCount()
        time_ps = float(state.getTime().value_in_unit(unit.picosecond))
    except IdentityError:
        raise
    except Exception as error:
        raise IdentityError(f'portable State cannot be read: {error}') from error
    if type(step) is not int or step < 0 or not math.isfinite(time_ps):
        raise IdentityError('portable State clock is nonfinite or malformed')
    return step, time_ps


def validate_restored_state(worker, *, state_id: str, portable_state_xml: str,
                            expected_step_count: int, expected_time_ps: float,
                            compare_portable_parameters: bool = True):
    """Validate actual restored context state against its saved portable State.

    The comparison is observational: it requests no energy or forces and does
    not advance the integrator. Exact step/time identity is intentionally
    separate from elapsed-time accumulation bounds.
    """
    import numpy as np
    import openmm as mm
    from openmm import unit
    import xml.etree.ElementTree as ET
    from .workflow import _snapshot
    from .schedule import schedule_state

    if (type(expected_step_count) is not int or expected_step_count < 0 or
            isinstance(expected_time_ps, bool) or
            not isinstance(expected_time_ps, (int, float)) or
            not math.isfinite(expected_time_ps)):
        raise IdentityError('saved checkpoint clock is malformed')
    if type(compare_portable_parameters) is not bool:
        raise IdentityError('portable parameter comparison flag must be boolean')
    try:
        root = ET.fromstring(portable_state_xml)
        if root.tag != 'State':
            raise IdentityError('portable artifact must be a State')
        portable = mm.XmlSerializer.deserialize(portable_state_xml)
        actual = worker.evaluator.context.getState(
            getPositions=True, getVelocities=True, getParameters=True)
        snapshot = _snapshot(worker)
        portable_positions = portable.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        portable_velocities = portable.getVelocities(asNumpy=True).value_in_unit(
            unit.nanometer/unit.picosecond)
        actual_positions = actual.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        actual_velocities = actual.getVelocities(asNumpy=True).value_in_unit(
            unit.nanometer/unit.picosecond)
        actual_step = worker.evaluator.context.getStepCount()
        actual_time_ps = float(actual.getTime().value_in_unit(unit.picosecond))
        portable_step = portable.getStepCount()
        portable_time_ps = float(portable.getTime().value_in_unit(unit.picosecond))
    except IdentityError:
        raise
    except Exception as error:
        raise IdentityError(f'restored checkpoint/portable State cannot be inspected: {error}') from error

    if (not np.isfinite(actual_positions).all() or not np.isfinite(actual_velocities).all() or
            not np.isfinite(portable_positions).all() or not np.isfinite(portable_velocities).all()):
        raise IdentityError('restored checkpoint or portable State has nonfinite coordinates/velocities')
    if (actual_positions.ndim != 2 or actual_positions.shape[1:] != (3,) or
            portable_positions.shape != actual_positions.shape or
            actual_velocities.shape != actual_positions.shape or
            portable_velocities.shape != actual_velocities.shape):
        raise IdentityError('restored checkpoint/portable State particle shapes disagree')
    if (actual_step != expected_step_count or actual_time_ps != expected_time_ps):
        raise IdentityError('restored checkpoint clock disagrees with saved state')
    if (portable_step != expected_step_count or portable_time_ps != expected_time_ps):
        raise IdentityError('portable State clock disagrees with saved state')

    physical = worker.bundle.physical
    particle_indices = [physical.real_to_final[atom.atom_id] for atom in physical.topology.atoms]
    actual_snapshot = np.asarray(snapshot.positions_nm, dtype=float)
    actual_velocities_real = np.asarray(snapshot.velocities_nm_ps, dtype=float)
    if not np.array_equal(actual_snapshot, portable_positions[particle_indices]):
        raise IdentityError('restored checkpoint coordinates disagree with portable State')
    if not np.array_equal(actual_velocities_real, portable_velocities[particle_indices]):
        raise IdentityError('restored checkpoint velocities disagree with portable State')

    actual_parameters = dict(actual.getParameters())
    portable_parameters = dict(portable.getParameters())
    if (any(not math.isfinite(float(value)) for value in actual_parameters.values()) or
            any(not math.isfinite(float(value)) for value in portable_parameters.values())):
        raise IdentityError('restored checkpoint/portable State parameters are nonfinite')
    if compare_portable_parameters and actual_parameters != portable_parameters:
        raise IdentityError('restored checkpoint parameters disagree with portable State')
    expected_parameters = dict(schedule_state(worker.bundle.schedule, state_id).parameters)
    if any(actual_parameters.get(name) != value for name, value in expected_parameters.items()):
        raise IdentityError('restored checkpoint parameters disagree with saved state identity')

    periodic = physical.manifest.get('periodicity') == 'orthorhombic-pme-v1'
    if periodic:
        try:
            actual_box = actual.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
            portable_box = portable.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
        except Exception as error:
            raise IdentityError(f'restored periodic box cannot be inspected: {error}') from error
        if (not np.isfinite(actual_box).all() or not np.isfinite(portable_box).all() or
                actual_box.shape != (3, 3) or portable_box.shape != (3, 3)):
            raise IdentityError('restored checkpoint/portable State box is nonfinite or malformed')
        if (not np.array_equal(np.asarray(snapshot.box_nm), actual_box) or
                not np.array_equal(np.asarray(snapshot.box_nm), portable_box) or
                not np.array_equal(actual_box, portable_box)):
            raise IdentityError('restored checkpoint box disagrees with portable State')
    if (not np.isfinite(np.asarray(snapshot.positions_nm, dtype=float)).all() or
            not np.isfinite(np.asarray(snapshot.velocities_nm_ps, dtype=float)).all()):
        raise IdentityError('restored real coordinates or velocities are nonfinite')
    return snapshot
