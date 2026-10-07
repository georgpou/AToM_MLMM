"""Reproducible fixed-coordinate MACE two-cap derivative evidence."""
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from atm_mlmm.atm import PhysicalEvaluator
from atm_mlmm.hybrid import build_physical
from atm_mlmm.models.mace import model_spec
from atm_mlmm.partition import resolve_partition
from atm_mlmm.schema import EmbeddingSpec, RuntimeSpec
from tests.cap_collection_oracle import IDS, input_case


original, spec, snapshot = input_case()
bundle = build_physical(
    original, resolve_partition(original.topology, spec), model_spec(),
    EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
    probe=None, cap_distance_nm=.117,
)
assert len(bundle.links) == 2
print("links", [(link.ml_parent_id, link.mm_parent_id, link.distance_nm)
                for link in bundle.links])
runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "Verlet")
parent_ids = ("p1_ml", "p1_mm", "p2_ml", "p2_mm", "p1_env", "p2_env")
with PhysicalEvaluator(bundle, runtime) as evaluator:
    reference = evaluator.evaluate(snapshot)
    forces = np.asarray(reference.forces_kj_mol_nm)
    print("energy_kj_mol", reference.energy_kj_mol)
    errors_by_step = []
    for step_nm in (1e-4, 1e-5):
        errors = []
        for atom_id in parent_ids:
            atom = IDS.index(atom_id)
            for axis in range(3):
                energies = []
                for sign in (1., -1.):
                    positions = np.asarray(snapshot.positions_nm, dtype=float).copy()
                    positions[atom, axis] += sign * step_nm
                    energies.append(evaluator.evaluate(
                        replace(snapshot, positions_nm=positions)
                    ).energy_kj_mol)
                estimate = -(energies[0] - energies[1]) / (2 * step_nm)
                errors.append(estimate - forces[atom, axis])
        errors_by_step.append(float(np.sqrt(np.mean(np.square(errors)))))
    selected = np.asarray([
        forces[IDS.index(atom_id), axis]
        for atom_id in parent_ids for axis in range(3)
    ])
    rms_reference = float(np.sqrt(np.mean(np.square(selected))))
    limit = 1e-3 + 1e-4 * rms_reference
    print("steps_nm", (1e-4, 1e-5))
    print("parent_environment_rms_errors", errors_by_step)
    print("rms_reference_force", rms_reference, "s06_limit", limit)
    assert errors_by_step[-1] <= limit
    assert errors_by_step[-1] <= errors_by_step[0] + 1e-6
print("MACE_TWO_CAP_CROSSCHECK_PASS")
