# Planned tests: names and locations

These 82 entries describe tests to implement, not a test run. Gate pages explain their expected answers and map them to small tasks. The original 81 definitions are retained; G01 now also names the original-MM inventory check its work already required.

A task log records the checks actually run and their results. Do not infer test success from this catalog or from a source file merely existing. Planned source paths may be changed only with a recorded update to the task/index and dependent references; keep the test IDs stable.

| Test ID | Gate | Planned pytest node | Requirements |
|---|---|---|---|
| P0-TEST-G00-01 | [G00](gates/G00-environment-and-provenance.md) | `tests/unit/test_environment.py::test_required_apis_and_versions` | P0-REQ-014 |
| P0-TEST-G00-02 | [G00](gates/G00-environment-and-provenance.md) | `tests/unit/test_environment.py::test_environment_manifest_complete` | P0-REQ-014 |
| P0-TEST-G00-03 | [G00](gates/G00-environment-and-provenance.md) | `tests/unit/test_environment.py::test_model_asset_hash_and_policy` | P0-REQ-014, P0-REQ-029 |
| P0-TEST-G00-04 | [G00](gates/G00-environment-and-provenance.md) | `tests/integration/test_checkpoint_loading.py::test_trusted_checkpoint_loads_in_fresh_process` | P0-REQ-014 |
| P0-TEST-G00-05 | [G00](gates/G00-environment-and-provenance.md) | `tests/unit/test_environment.py::test_unavailable_platform_is_unqualified` | P0-REQ-032 |
| P0-TEST-G01-01 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/unit/test_identity.py::test_chain_insertion_and_permutation_identity` | P0-REQ-002 |
| P0-TEST-G01-02 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/unit/test_partition.py::test_fixed_complete_mobile_groups` | P0-REQ-002, P0-REQ-023 |
| P0-TEST-G01-03 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/contracts/test_schema.py::test_versioned_round_trip_and_units` | P0-REQ-024, P0-REQ-010 |
| P0-TEST-G01-04 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/contracts/test_architecture_boundaries.py::test_shared_contracts_have_no_model_import` | P0-REQ-001, P0-REQ-021 |
| P0-TEST-G01-05 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/contracts/test_capabilities.py::test_unsupported_combination_fails_closed` | P0-REQ-023, P0-REQ-028 |
| P0-TEST-G01-06 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/contracts/test_evidence_schema.py::test_acceptance_requires_evidence` | P0-REQ-025, P0-REQ-026 |
| P0-TEST-G01-07 | [G01](gates/G01-identity-partition-and-contracts.md) | `tests/unit/test_force_inventory.py::test_original_mm_inventory_and_unknown_force` | P0-REQ-003, P0-REQ-023 |
| P0-TEST-G02-01 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/integration/test_pythonforce_atm.py::test_linear_endpoint_and_force_identity` | P0-REQ-013 |
| P0-TEST-G02-02 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/integration/test_pythonforce_atm.py::test_permuted_subset_and_units` | P0-REQ-002, P0-REQ-010, P0-REQ-030 |
| P0-TEST-G02-03 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/integration/test_pythonforce_atm.py::test_nonzero_outside_term_and_tuple_order` | P0-REQ-011, P0-REQ-013 |
| P0-TEST-G02-04 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/contracts/test_transfer_protocols.py::test_one_and_two_unequal_mobile_groups` | P0-REQ-022 |
| P0-TEST-G02-05 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/contracts/test_physical_evaluator.py::test_environment_force_and_recomputed_mapping` | P0-REQ-006, P0-REQ-007 |
| P0-TEST-G02-06 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/contracts/test_physical_evaluator.py::test_evaluation_history_independence` | P0-REQ-007 |
| P0-TEST-G02-07 | [G02](gates/G02-analytic-force-in-native-atm.md) | `tests/contracts/test_fault_injection.py::test_known_transfer_errors_are_detected` | P0-REQ-030 |
| P0-TEST-G03-01 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_atom_force_routing.py::test_pythonforce_explicit_group_route` | P0-REQ-011, P0-REQ-021 |
| P0-TEST-G03-02 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_active_force_groups.py::test_all_physical_groups_integrated` | P0-REQ-012 |
| P0-TEST-G03-03 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_active_force_groups.py::test_preparation_and_export_copies` | P0-REQ-012 |
| P0-TEST-G03-04 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_atom_force_routing.py::test_both_protocols_match_native_oracle` | P0-REQ-021, P0-REQ-022 |
| P0-TEST-G03-05 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_atom_force_routing.py::test_upstream_unit_and_key_conversion` | P0-REQ-010, P0-REQ-021 |
| P0-TEST-G03-06 | [G03](gates/G03-atom-routing-and-integration.md) | `tests/workflow/test_atom_force_routing.py::test_duplicate_and_nested_atm_rejected` | P0-REQ-011, P0-REQ-023 |
| P0-TEST-G04-01 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_link_geometry.py::test_cap_position_and_zero_mass` | P0-REQ-008 |
| P0-TEST-G04-02 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_link_geometry.py::test_cap_parent_chain_rule` | P0-REQ-004 |
| P0-TEST-G04-03 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_boundary_ledger.py::test_each_boundary_term_disposition` | P0-REQ-003, P0-REQ-008 |
| P0-TEST-G04-04 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_link_geometry.py::test_actual_and_nonidentity_index_maps` | P0-REQ-002 |
| P0-TEST-G04-05 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_link_geometry.py::test_stationary_cap_force_under_atm` | P0-REQ-004, P0-REQ-013 |
| P0-TEST-G04-06 | [G04](gates/G04-link-boundary-and-derivatives.md) | `tests/integration/test_link_geometry.py::test_cap_environment_cross_derivative` | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G05-01 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_model_adapter.py::test_native_and_openmm_energy_forces` | P0-REQ-010 |
| P0-TEST-G05-02 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_model_adapter.py::test_real_parent_forces_with_model_caps` | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G05-03 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_locality.py::test_declared_local_component_additivity` | P0-REQ-009 |
| P0-TEST-G05-04 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_model_adapter.py::test_consistent_translation_rotation_and_permutation` | P0-REQ-010, P0-REQ-030 |
| P0-TEST-G05-05 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_model_domain.py::test_contact_cutoff_and_counterfactual_scans` | P0-REQ-020 |
| P0-TEST-G05-06 | [G05](gates/G05-local-model-adapter.md) | `tests/integration/test_model_adapter.py::test_local_asset_fresh_process_reload` | P0-REQ-014, P0-REQ-029 |
| P0-TEST-G06-01 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_mechanical_pme.py::test_ml_mm_cross_interactions_retained` | P0-REQ-003, P0-REQ-006 |
| P0-TEST-G06-02 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_masked_interactions.py::test_pme_charge_mask_cross_identity` | P0-REQ-003 |
| P0-TEST-G06-03 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_periodic_geometry.py::test_images_caps_and_bulk_separation` | P0-REQ-005 |
| P0-TEST-G06-04 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_periodic_geometry.py::test_cap_wrapping_and_image_seam_continuity` | P0-REQ-005 |
| P0-TEST-G06-05 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_periodic_geometry.py::test_backend_graph_matches_independent_geometry` | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G06-06 | [G06](gates/G06-periodicity-and-interaction-ledger.md) | `tests/integration/test_mechanical_pme.py::test_nonstandard_forces_and_box_rejected` | P0-REQ-023 |
| P0-TEST-G07-01 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/integration/test_joint_hybrid_atm.py::test_direct_native_and_atom_agree` | P0-REQ-013, P0-REQ-021 |
| P0-TEST-G07-02 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/integration/test_joint_hybrid_atm.py::test_mm_boundary_parent_force` | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G07-03 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/integration/test_joint_hybrid_atm.py::test_joint_contact_and_disconnected_graph` | P0-REQ-002, P0-REQ-009 |
| P0-TEST-G07-04 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/integration/test_joint_hybrid_atm.py::test_only_mobile_groups_translate` | P0-REQ-002, P0-REQ-013 |
| P0-TEST-G07-05 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/contracts/test_embedding_extension.py::test_environment_provider_reuses_atm_and_protocols` | P0-REQ-001, P0-REQ-028 |
| P0-TEST-G07-06 | [G07](gates/G07-joint-cavity-ligand-atm.md) | `tests/integration/test_joint_hybrid_atm.py::test_joint_periodic_geometry_and_forces` | P0-REQ-005 |
| P0-TEST-G08-01 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/sampling/test_analytic_free_energy.py::test_harmonic_known_difference` | P0-REQ-016, P0-REQ-030 |
| P0-TEST-G08-02 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/unit/test_schedule.py::test_reduced_energies_match_context` | P0-REQ-018 |
| P0-TEST-G08-03 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/unit/test_schedule.py::test_active_midpoint_difference_requires_bridge` | P0-REQ-017 |
| P0-TEST-G08-04 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/unit/test_restraint_volume.py::test_finite_wall_and_standard_state_sign` | P0-REQ-016 |
| P0-TEST-G08-05 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/unit/test_restraint_volume.py::test_required_correction_cannot_default_to_zero` | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G08-06 | [G08](gates/G08-thermodynamics-and-estimators.md) | `tests/sampling/test_analytic_free_energy.py::test_estimators_covariance_and_offsets` | P0-REQ-018, P0-REQ-019 |
| P0-TEST-G09-01 | [G09](gates/G09-solvent-preparation-and-export.md) | `tests/workflow/test_solvated_handover.py::test_bulk_site_and_real_cross_forces` | P0-REQ-003, P0-REQ-005 |
| P0-TEST-G09-02 | [G09](gates/G09-solvent-preparation-and-export.md) | `tests/workflow/test_solvated_handover.py::test_same_hamiltonian_in_preparation` | P0-REQ-012, P0-REQ-021 |
| P0-TEST-G09-03 | [G09](gates/G09-solvent-preparation-and-export.md) | `tests/workflow/test_solvated_handover.py::test_worker_load_matches_direct_state` | P0-REQ-015, P0-REQ-021 |
| P0-TEST-G09-04 | [G09](gates/G09-solvent-preparation-and-export.md) | `tests/workflow/test_solvated_handover.py::test_saved_raw_records_reconstruct_states` | P0-REQ-018 |
| P0-TEST-G09-05 | [G09](gates/G09-solvent-preparation-and-export.md) | `tests/workflow/test_solvated_handover.py::test_both_mapped_geometries_remain_admitted` | P0-REQ-020, P0-REQ-005 |
| P0-TEST-G10-01 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_fresh_process.py::test_offline_cache_independent_reload` | P0-REQ-029, P0-REQ-015 |
| P0-TEST-G10-02 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_restart.py::test_checkpoint_and_state_semantics` | P0-REQ-015 |
| P0-TEST-G10-03 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_replica_exchange.py::test_acceptance_uses_actual_reduced_energies` | P0-REQ-018, P0-REQ-015 |
| P0-TEST-G10-04 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_replica_exchange.py::test_parameter_update_and_state_history` | P0-REQ-015, P0-REQ-018 |
| P0-TEST-G10-05 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_fresh_process.py::test_model_and_openmm_worker_device` | P0-REQ-015, P0-REQ-032 |
| P0-TEST-G10-06 | [G10](gates/G10-restart-and-replica-exchange.md) | `tests/workflow/test_restart.py::test_interruption_resume_without_duplicate_records` | P0-REQ-015, P0-REQ-019 |
| P0-TEST-G11-01 | [G11](gates/G11-protein-abfe.md) | `tests/workflow/test_protein_abfe.py::test_prepared_target_and_every_boundary` | P0-REQ-002, P0-REQ-004 |
| P0-TEST-G11-02 | [G11](gates/G11-protein-abfe.md) | `tests/workflow/test_protein_abfe.py::test_control_ensemble_and_identity` | P0-REQ-003, P0-REQ-013 |
| P0-TEST-G11-03 | [G11](gates/G11-protein-abfe.md) | `tests/workflow/test_protein_abfe.py::test_abfe_result_correction_ledger` | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G11-04 | [G11](gates/G11-protein-abfe.md) | `tests/workflow/test_protein_abfe.py::test_bulk_placement_and_box_sensitivity_recorded` | P0-REQ-005, P0-REQ-019 |
| P0-TEST-G11-05 | [G11](gates/G11-protein-abfe.md) | `tests/workflow/test_protein_abfe.py::test_protein_restart_exchange_and_domain` | P0-REQ-015, P0-REQ-020 |
| P0-TEST-G12-01 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/workflow/test_rbfe_transforms.py::test_opposite_group_maps_and_cap_identity` | P0-REQ-022, P0-REQ-002 |
| P0-TEST-G12-02 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/workflow/test_rbfe_transforms.py::test_correct_bound_component_and_no_spurious_contact` | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G12-03 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/sampling/test_binding_closure.py::test_symmetric_a_to_a_free_energy` | P0-REQ-016 |
| P0-TEST-G12-04 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/sampling/test_binding_closure.py::test_reversed_pair_sign` | P0-REQ-016, P0-REQ-031 |
| P0-TEST-G12-05 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/sampling/test_binding_closure.py::test_abfe_rbfe_comparison_matches_states` | P0-REQ-031, P0-REQ-019 |
| P0-TEST-G12-06 | [G12](gates/G12-dual-ligand-rbfe.md) | `tests/workflow/test_rbfe_transforms.py::test_shared_pipeline_and_restart` | P0-REQ-001, P0-REQ-022, P0-REQ-015 |
| P0-TEST-G13-01 | [G13](gates/G13-performance-and-release.md) | `tests/workflow/test_release_bundle.py::test_clean_offline_reproduction` | P0-REQ-025, P0-REQ-029 |
| P0-TEST-G13-02 | [G13](gates/G13-performance-and-release.md) | `tests/contracts/test_release_evidence.py::test_claimed_profiles_have_required_evidence` | P0-REQ-025, P0-REQ-032 |
| P0-TEST-G13-03 | [G13](gates/G13-performance-and-release.md) | `tests/unit/test_benchmark_metrics.py::test_time_and_resource_units` | P0-REQ-027 |
| P0-TEST-G13-04 | [G13](gates/G13-performance-and-release.md) | `tests/integration/test_optimization_equivalence.py::test_optimized_scope_preserves_hamiltonian` | P0-REQ-027, P0-REQ-011 |
| P0-TEST-G13-05 | [G13](gates/G13-performance-and-release.md) | `tests/contracts/test_release_evidence.py::test_implementation_sampling_physics_separate` | P0-REQ-025, P0-REQ-028, P0-REQ-032 |
