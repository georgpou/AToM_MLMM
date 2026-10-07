"""General-input admission controls assigned to Before HPC Batch B."""
from dataclasses import replace

import pytest

from tests.cap_collection_oracle import DATA, IDS, frozen_mm_identity, input_case


def test_two_cut_fixture_freezes_distinct_neutral_components_and_mm_parameters():
    frozen_mm_identity()
    cuts = DATA["permitted_cuts"]
    assert len(cuts) == 2
    assert cuts[0] != cuts[1]
    assert cuts[0][1] != cuts[1][1]
    assert all(DATA["atoms"][i]["id"] not in {a for edge in cuts for a in edge}
               for i in (1, 3, 5, 7, 9, 11, 12))
    assert len(DATA["component_states"]) == 4
    assert all(state["formal_charge"] == 0 and state["multiplicity"] == 1
               for state in DATA["component_states"])
    assert tuple(DATA["real_atom_order"]) == IDS


def test_resolved_partition_preserves_explicit_component_chemistry():
    from atm_mlmm.partition import resolve_partition

    _, spec, _ = input_case()
    resolved = resolve_partition(input_case()[0].topology, spec)
    assert {frozenset(state.atom_ids) for state in resolved.component_states} == {
        frozenset(state.atom_ids) for state in spec.component_states
    }
    assert all(state.formal_charge == 0 and state.multiplicity == 1
               for state in resolved.component_states)


def test_two_cut_native_build_admits_every_declared_cap_by_parent():
    from atm_mlmm.embeddings.mechanical import seal_boundary_result
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec

    original, spec, _ = input_case()
    resolved = resolve_partition(original.topology, spec)
    bundle = build_physical(
        original, resolved, model_spec(),
        EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
        cap_distance_nm=DATA["cap_distance_nm"],
    )
    assert len(bundle.links) == 2
    assert {(link.ml_parent_id, link.mm_parent_id) for link in bundle.links} == {
        tuple(edge) for edge in DATA["permitted_cuts"]
    }
    assert len({link.cap_id for link in bundle.links}) == 2
    assert bundle.manifest["boundary_builder_version"] == 2
    assert bundle.chemistry_states == resolved.component_states


def test_zero_cut_mixed_ligands_retain_mm_environment():
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec

    original, spec, _ = input_case(mixed_zero_cut=True)
    resolved = resolve_partition(original.topology, spec)
    bundle = build_physical(
        original, resolved, model_spec(),
        EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
        cap_distance_nm=DATA["cap_distance_nm"],
    )
    assert bundle.ml_atom_ids == resolved.ml_ids
    assert len(bundle.links) == 0
    assert bundle.manifest["boundary_builder_version"] == 2
    assert bundle.manifest["original_mm_inventory"]
    assert bundle.manifest["retained_mm_xml"]


def test_v2_input_rejects_declared_original_parameter_inventory_disagreement():
    from atm_mlmm.embeddings.mechanical import original_system
    from atm_mlmm.schema import IdentityError

    original, _, _ = input_case()
    inventory_identity = DATA["mm_parameter_identity"]
    original = replace(original, prepared_mm_inventory_identity=inventory_identity)
    system = frozen_mm_identity()
    force = next(f for f in system.getForces() if f.__class__.__name__ == "NonbondedForce")
    from openmm import unit
    q, sigma, epsilon = force.getParticleParameters(0)
    force.setParticleParameters(0, q + 0.01 * unit.elementary_charge, sigma, epsilon)
    import openmm as mm
    corrupted_xml = mm.XmlSerializer.serialize(system)
    corrupted = replace(
        original,
        prepared_mm_artifact=corrupted_xml,
        prepared_mm_sha256=__import__("hashlib").sha256(corrupted_xml.encode()).hexdigest(),
    )
    with pytest.raises(IdentityError, match="inventory"):
        original_system(corrupted, require_inventory_identity=True)


def test_builder_rejects_forged_partition_and_unknown_model_chemistry():
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec, IdentityError, UnsupportedCapability

    original, spec, _ = input_case()
    resolved = resolve_partition(original.topology, spec)
    forged = replace(resolved, boundary_edges=(('p1_ml', 'p2_mm'), ('p2_ml', 'p2_mm')))
    with pytest.raises((IdentityError, UnsupportedCapability), match='boundary|partition|cut'):
        build_physical(
            original, forged, model_spec(),
            EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
            cap_distance_nm=DATA["cap_distance_nm"],
        )
    unknown = replace(model_spec(), chemical_state_support="unreviewed_charged_states")
    with pytest.raises(UnsupportedCapability, match="MACE semantics"):
        build_physical(
            original, resolved, unknown,
            EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
            cap_distance_nm=DATA["cap_distance_nm"],
        )


def test_original_mm_declared_masses_and_constraints_are_exact():
    from atm_mlmm.embeddings.mechanical import original_system
    from atm_mlmm.schema import IdentityError

    original, _, _ = input_case()
    wrong_masses = list(original.masses_da)
    wrong_masses[0] += .001
    with pytest.raises(IdentityError, match="masses/constraints"):
        original_system(replace(original, masses_da=tuple(wrong_masses)), require_inventory_identity=True)
    with pytest.raises(IdentityError, match="masses/constraints"):
        original_system(replace(original, constraints=(("p1_ml", "p1_mm", .15),)),
                        require_inventory_identity=True)
