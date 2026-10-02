"""Local MACE-OFF23/GAFF mechanical ML/MM single point with one link atom."""
import argparse
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "models/mace-off23-small/MACE-OFF23_small.model"
CHECKPOINT_SHA256 = "165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f"


def load_calculator(checkpoint=CHECKPOINT):
    """Load only the explicitly approved, pinned academic checkpoint."""
    import sys
    # Direct example execution also works without adding a distribution to the
    # locked installation; pytest already provides this source path.
    source = str(ROOT / 'src')
    if source not in sys.path:
        sys.path.insert(0, source)
    from atm_mlmm.models.mace import make_calculator
    return make_calculator(checkpoint)


def run_calculation():
    import importlib.metadata as metadata
    import numpy as np
    import openmm as mm
    from openmm import app, unit
    from openmmml import MLPotential
    import torch

    before_slice = slice in torch.serialization.get_safe_globals()
    calculator = load_calculator()
    fixture = ROOT / "fixtures/mace_link"
    data = json.loads((fixture / "input.json").read_text())
    xml = (fixture / "mm-system.xml").read_text()
    if hashlib.sha256(xml.encode()).hexdigest() != data["mm_system_sha256"]:
        raise ValueError("MM fixture SHA-256 mismatch")
    mm_system = mm.XmlSerializer.deserialize(xml)
    topology = app.Topology()
    chain = topology.addChain()
    residues = [topology.addResidue(name, chain) for name in ["CAV", "LIG"]]
    atoms = [topology.addAtom(a["name"], app.Element.getByAtomicNumber(a["atomic_number"]),
                             residues[a["residue"]]) for a in data["atoms"]]
    for a, b in data["bonds"]:
        topology.addBond(atoms[a], atoms[b])
    parent_a, parent_b = data["boundary_parents"]
    info = MLPotential("ase").createMixedSystem(
        topology, mm_system, data["ml_real_indices"], embedding="mechanical",
        calculator=calculator, returnInfo=True, forceGroup=1,
        linkAtomDistances=[(parent_a, parent_b, data["link_distance_nm"] * unit.nanometer)],
    )
    system = info["system"]
    real_count = len(atoms)
    link_indices = [i for i in range(system.getNumParticles()) if system.isVirtualSite(i)]
    if len(link_indices) != 1 or system.getNumParticles() != real_count + 1:
        raise ValueError("The fixture must produce exactly one appended link site")
    link = link_indices[0]
    if system.getParticleMass(link).value_in_unit(unit.dalton) != 0:
        raise ValueError("Link site has an independent mass")
    if info["oldToNew"] != list(range(real_count)):
        raise ValueError("Unexpected real-particle map; review the fixture mapping")
    positions = np.vstack([np.asarray(data["positions_nm"]), np.zeros((1, 3))])
    integrator = mm.VerletIntegrator(0.0005 * unit.picosecond)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName("CPU"))
    reference_integrator = mm.VerletIntegrator(0.0005 * unit.picosecond)
    reference_context = mm.Context(system, reference_integrator,
                                   mm.Platform.getPlatformByName("Reference"))

    def evaluate(coordinates, forces=False):
        context.setPositions(coordinates * unit.nanometer)
        context.computeVirtualSites()
        state = context.getState(getEnergy=True, getForces=forces, getPositions=forces)
        energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        if not forces:
            return float(energy)
        real_forces = state.getForces(asNumpy=True).value_in_unit(
            unit.kilojoule_per_mole / unit.nanometer
        )[:real_count]
        return float(energy), np.asarray(real_forces), state

    def reference_energy(coordinates):
        # CPU NonbondedForce energy rounding is amplified by small FD steps.
        # The same Hamiltonian on Reference supplies the double-precision oracle.
        reference_context.setPositions(coordinates * unit.nanometer)
        reference_context.computeVirtualSites()
        return reference_context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilojoule_per_mole
        )

    try:
        energy, forces, state = evaluate(positions, forces=True)
        if not np.isfinite(energy) or not np.isfinite(forces).all():
            raise ValueError("Nonfinite ML/MM energy or real forces")
        link_position = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[link]
        if not np.isclose(np.linalg.norm(link_position - positions[parent_a]),
                          data["link_distance_nm"], atol=1e-12):
            raise ValueError("Incorrect fixed-length cap geometry")
        ml_state = context.getState(getEnergy=True, getForces=True, groups=1 << 1)
        mm_state = context.getState(getEnergy=True, groups=1 << 0)
        ml_energy = ml_state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        mm_energy = mm_state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        ml_forces = ml_state.getForces(asNumpy=True).value_in_unit(
            unit.kilojoule_per_mole / unit.nanometer
        )[:real_count]
        np.testing.assert_allclose(energy, ml_energy + mm_energy, rtol=0, atol=1e-8)
        parent_norms = [float(np.linalg.norm(ml_forces[p])) for p in [parent_a, parent_b]]
        if not all(norm > 1e-8 for norm in parent_norms):
            raise ValueError("The asymmetric fixture must expose ML forces on both cap parents")
        reference_value = reference_energy(positions)
        np.testing.assert_allclose(energy, reference_value, rtol=0, atol=1e-4)
        errors = []
        for parent in [parent_a, parent_b]:
            component_errors = []
            for axis in range(3):
                estimates = []
                for step in [1e-4, 1e-5]:
                    plus, minus = positions.copy(), positions.copy()
                    plus[parent, axis] += step
                    minus[parent, axis] -= step
                    estimates.append(-(reference_energy(plus) - reference_energy(minus)) / (2 * step))
                np.testing.assert_allclose(estimates[-1], forces[parent, axis],
                                           rtol=0, atol=5e-3)
                np.testing.assert_allclose(estimates[-1], estimates[-2],
                                           rtol=1e-4, atol=5e-3)
                component_errors.append(float(abs(estimates[-1] - forces[parent, axis])))
            errors.append(component_errors)
        # Leave the Context at the original snapshot and verify repeatability.
        np.testing.assert_allclose(evaluate(positions), energy, rtol=0, atol=1e-8)
        if "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD" in os.environ:
            raise ValueError("A global unsafe-loading override remains enabled")
        if (slice in torch.serialization.get_safe_globals()) != before_slice:
            raise ValueError("The trusted e3nn slice allowance escaped its scope")
        return {
            "scope": "MACE/GAFF/link-atom CPU single-point smoke; no gate or physical-profile acceptance",
            "platform": context.getPlatform().getName(), "dtype": "float64",
            "model_sha256": CHECKPOINT_SHA256, "energy_convention": "energy",
            "real_particles": real_count, "link_particles": len(link_indices),
            "link_mass_da": 0.0, "ml_real_indices": data["ml_real_indices"],
            "boundary_parents": [parent_a, parent_b],
            "energy_kJ_mol": energy, "ml_energy_kJ_mol": float(ml_energy),
            "retained_mm_energy_kJ_mol": float(mm_energy),
            "ml_boundary_parent_force_norms_kJ_mol_nm": parent_norms,
            "real_forces_kJ_mol_nm": forces.tolist(),
            "max_real_force_norm_kJ_mol_nm": float(np.linalg.norm(forces, axis=1).max()),
            "finite_energy_and_real_forces": True,
            "boundary_parent_force_errors_kJ_mol_nm": errors,
            "force_check_oracle": "Reference-platform energy finite differences",
            "finite_difference_steps_nm": [1e-4, 1e-5],
            "cpu_reference_energy_difference_kJ_mol": float(abs(energy - reference_value)),
            "boundary_parent_force_check_passed": True,
            "unsafe_loading_override_present": False, "loading_scope_restored": True,
            "versions": {name: metadata.version(name) for name in
                         ["mace-torch", "torch", "openmm", "openmmml", "numpy"]},
        }
    finally:
        del reference_context, reference_integrator, context, integrator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()
    result = run_calculation()
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
