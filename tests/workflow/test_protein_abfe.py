"""Bounded protein ABFE preflight harness; intentionally no selected target."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_two_cut_structural_controls_share_the_original_system_and_conventions():
    import openmm as mm
    from atm_mlmm.embeddings.mechanical import original_system
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.ledger import inventory_system
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec
    from tests.cap_collection_oracle import DATA, input_case

    original, cavity_spec, snapshot = input_case()
    ligand_original, ligand_only_spec, ligand_snapshot = input_case(mixed_zero_cut=True)
    assert original == ligand_original
    assert snapshot == ligand_snapshot
    assert len(cavity_spec.permitted_cuts) == 2
    assert not ligand_only_spec.permitted_cuts
    control_doc = json.loads((ROOT / 'fixtures/protein_structural_control/v1/controls.json').read_text())
    assert control_doc['scope'] == 'synthetic_structural_control_only'
    assert control_doc['source_fixture'] == 'fixtures/two_cut_control'
    all_mm = original_system(original, require_inventory_identity=True)
    assert inventory_system(all_mm).content_identity == original.prepared_mm_inventory_identity
    ligand_bundle = build_physical(
        ligand_original, resolve_partition(ligand_original.topology, ligand_only_spec), model_spec(),
        EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'),
        cap_distance_nm=DATA['cap_distance_nm'])
    cavity_bundle = build_physical(
        original, resolve_partition(original.topology, cavity_spec), model_spec(),
        EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'),
        cap_distance_nm=DATA['cap_distance_nm'])
    assert ligand_bundle.manifest['boundary_builder_version'] == 2
    assert ligand_bundle.links == ()
    assert cavity_bundle.manifest['boundary_builder_version'] == 2
    assert len(cavity_bundle.links) == 2
    assert {frozenset((link.ml_parent_id, link.mm_parent_id))
            for link in cavity_bundle.links} == {
                frozenset(edge) for edge in cavity_spec.permitted_cuts}
    cavity_system = mm.XmlSerializer.deserialize(cavity_bundle.system_xml)
    assert all(cavity_system.isVirtualSite(link.final_particle_index)
               and cavity_bundle.masses_da[link.final_particle_index] == 0.
               for link in cavity_bundle.links)
    assert len(cavity_bundle.manifest['cap_force_ownership']) == 2
    for bundle in (ligand_bundle, cavity_bundle):
        real_indices = {bundle.real_to_final[atom.atom_id]
                        for atom in original.topology.atoms}
        assert tuple(bundle.masses_da[bundle.real_to_final[atom.atom_id]]
                     for atom in original.topology.atoms) == original.masses_da
        assert all(bundle.masses_da[i] == 0. for i in range(len(bundle.masses_da))
                   if i not in real_indices)
        assert bundle.constraints == tuple(
            (bundle.real_to_final[a], bundle.real_to_final[b], distance)
            for a, b, distance in original.constraints)
        assert bundle.manifest['periodicity'] == 'nonperiodic'
        assert bundle.manifest.get('box_nm') is None
    assert control_doc['control_models']['all_mm']['status'] == 'original_mm_reference'
    assert control_doc['control_models']['ligand_only']['builder'] == 'common_build_physical'
    assert control_doc['control_models']['cavity_inclusive']['builder'] == 'common_build_physical'
    assert control_doc['comparability'] == 'same input/masses/constraints/box; distinct intended Hamiltonians'


def test_protein_abfe_correction_ledger_preserves_atm_source_and_unresolved_applicability():
    from atm_mlmm.schema import from_json

    path = ROOT / 'fixtures/protein_abfe/abfe-correction-ledger-v1.json'
    ledger = json.loads(path.read_text())
    assert ledger['binding_result'] == 'not_evaluated'
    assert ledger['protocol']['installed_distribution'] == 'atom-openmm==8.5.0b0'
    assert ledger['protocol']['upstream_release_tag'] == 'v8.5.0'
    assert ledger['protocol']['U15_source_sha256']
    assert ledger['protocol']['U37_access'] == 'HTTP 403; document unavailable in this environment'
    assert 'not_claimed' in ledger['protocol']['correction_procedure_status']
    assert ledger['domain']['bound'] is None and ledger['domain']['bulk'] is None
    assert all(row['status'] == 'required_uncomputed' for row in ledger['obligations'])
    assert {row['id'] for row in ledger['obligations']} == {
        'translation_standard_state', 'bound_release', 'orientation',
        'conformation', 'state_counting', 'midpoint_bridge'}
    assert all(row['accounting_classification'] not in ('already_in_path', 'not_applicable')
               for row in ledger['obligations'])
    assert next(row for row in ledger['obligations'] if row['id'] == 'midpoint_bridge')[
        'accounting_classification'] == 'applicability_unresolved'
    assert all(row['applicability'] for row in ledger['obligations'])
    assert all(row['additive_calculation_authorized'] is False for row in ledger['obligations'])
    typed = from_json((ROOT / 'fixtures/protein_abfe/thermodynamics-v1.json').read_text())
    assert typed.observable == 'standard_binding_free_energy'
    assert typed.sign_convention == 'bound_minus_bulk'
    assert all(row.status == 'required_uncomputed' for row in typed.corrections)
    assert ledger['correction_source'] == 'C relative-binding schema template; ABFE interpretation explicit'


def test_protein_proposal_is_an_actionable_hold_not_an_empty_support_test():
    from tools.prepare_protein_input import validate_manifest

    proposal = ROOT / 'fixtures/protein_abfe/target-proposal-v1.json'
    result = validate_manifest(proposal)
    assert result['status'] == 'blocked'
    assert result['missing_fields']
    assert result['binding_result'] == 'not_evaluated'
    assert result['complete_target_selected'] is False
