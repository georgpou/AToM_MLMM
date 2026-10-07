"""Frozen small topology and independent force helpers for Batch B."""
import hashlib
import json
from pathlib import Path

import numpy as np
import openmm as mm
from openmm import unit

from atm_mlmm.schema import (
    AtomIdentity, Bond, ComponentState, MoleculeState, PartitionSpec, Snapshot,
    SystemInput, TopologyView,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/two_cut_control"
DATA = json.loads((FIXTURE / "input.json").read_text())
IDS = tuple(DATA["real_atom_order"])


def input_case(*, mixed_zero_cut=False):
    atoms = tuple(AtomIdentity(
        row["id"], row["element"], row["chain"], row["residue"],
        row["insertion_code"], row["atom_name"],
    ) for row in DATA["atoms"])
    bonds = tuple(Bond(row["atom1"], row["atom2"], row["order"], row["kind"])
                  for row in DATA["bonds"])
    molecules = tuple(MoleculeState(
        row["molecule_id"], tuple(row["atom_ids"]), row["role"],
        row["formal_charge"], row["multiplicity"],
    ) for row in DATA["molecules"])
    topology = TopologyView(atoms, bonds, molecules)
    xml = (FIXTURE / "original-mm.xml").read_text()
    assert hashlib.sha256(xml.encode()).hexdigest() == DATA["mm_system_sha256"]
    system = mm.XmlSerializer.deserialize(xml)
    original = SystemInput(
        xml, DATA["mm_system_sha256"], topology, tuple(DATA["positions_nm"]),
        DATA["box_nm"], tuple(DATA["masses_da"]), tuple(DATA["constraints"]),
        DATA["force_field_provenance"],
        prepared_mm_inventory_identity=DATA["mm_parameter_identity"],
    )
    if mixed_zero_cut:
        selected = tuple(a for molecule in molecules if molecule.role == "ligand"
                         for a in molecule.atom_ids)
        protein = ()
        cuts = ()
        state_ids = tuple(tuple(a for a in molecule.atom_ids)
                          for molecule in molecules if molecule.role == "ligand")
    else:
        selected = tuple(DATA["ml_ids"])
        protein = tuple(DATA["protein_ml_ids"])
        cuts = tuple(tuple(edge) for edge in DATA["permitted_cuts"])
        state_ids = tuple(tuple(row["atom_ids"]) for row in DATA["component_states"])
    states = tuple(ComponentState(ids, 0, 1) for ids in state_ids)
    partition = PartitionSpec(selected, protein, cuts, states)
    snapshot = Snapshot(IDS, tuple(DATA["positions_nm"]), DATA["box_nm"])
    return original, partition, snapshot


def frozen_mm_identity():
    """Check the source fixture independently of the hybrid builder."""
    from atm_mlmm.ledger import inventory_system

    xml = (FIXTURE / "original-mm.xml").read_text()
    system = mm.XmlSerializer.deserialize(xml)
    assert inventory_system(system).content_identity == DATA["mm_parameter_identity"]
    force = next(f for f in system.getForces() if isinstance(f, mm.NonbondedForce))
    observed = []
    for atom_id, i in zip(IDS, range(len(IDS))):
        q, sigma, epsilon = force.getParticleParameters(i)
        observed.append({
            "atom_id": atom_id,
            "charge_e": q.value_in_unit(unit.elementary_charge),
            "sigma_nm": sigma.value_in_unit(unit.nanometer),
            "epsilon_kj_mol": epsilon.value_in_unit(unit.kilojoule_per_mole),
        })
    assert observed == DATA["mm_nonbonded_parameters"]
    assert len(DATA["component_states"]) == 4
    assert sorted(map(len, [DATA["component_states"][2]["atom_ids"],
                            DATA["component_states"][3]["atom_ids"]])) == [3, 4]
    return system


def analytic_force_answer(positions, *, cap_terms, direct_environment_terms=(),
                          ligand_terms=(), distances=None):
    """Independent collection energy and full-real-force oracle.

    Each cap term owns its cap-local energy and environment pair. Ligand and
    direct environment terms are evaluated once, outside the cap loop.
    """
    from atm_mlmm.geometry import final_positions

    x = np.asarray(positions, dtype=float)
    index = {atom_id: i for i, atom_id in enumerate(IDS)}
    distances = {} if distances is None else distances
    forces = np.zeros_like(x)
    energy = 0.0
    cap_positions = {}
    for term in cap_terms:
        a, b = index[term["ml_parent_id"]], index[term["mm_parent_id"]]
        vector = x[b] - x[a]
        length = np.linalg.norm(vector)
        normal = vector / length
        distance = float(term.get("distance_nm", distances.get(
            (term["ml_parent_id"], term["mm_parent_id"]), DATA["cap_distance_nm"])))
        h = x[a] + distance * normal
        jacobian = distance / length * (np.eye(3) - np.outer(normal, normal))
        cap_positions[term["cap_id"]] = h
        delta = h - np.asarray(term["center_nm"], dtype=float)
        cap_force = -float(term["cap_k"]) * delta
        energy += 0.5 * float(term["cap_k"]) * np.dot(delta, delta)
        if term.get("environment_k", 0.0):
            env = index[term["environment_id"]]
            delta = h - x[env]
            k = float(term["environment_k"])
            energy += 0.5 * k * np.dot(delta, delta)
            cap_force -= k * delta
            forces[env] += k * delta
        forces[a] += (np.eye(3) - jacobian).T @ cap_force
        forces[b] += jacobian.T @ cap_force
    for term in direct_environment_terms:
        a, b = index[term["model_id"]], index[term["environment_id"]]
        delta = x[a] - x[b]
        k = float(term["k"])
        energy += 0.5 * k * np.dot(delta, delta)
        forces[a] -= k * delta
        forces[b] += k * delta
    for term in ligand_terms:
        atom = index[term["atom_id"]]
        delta = x[atom] - np.asarray(term["center_nm"], dtype=float)
        k = float(term["k"])
        energy += 0.5 * k * np.dot(delta, delta)
        forces[atom] -= k * delta
    return energy, forces, cap_positions
