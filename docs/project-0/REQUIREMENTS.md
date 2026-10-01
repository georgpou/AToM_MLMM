# Requirement locator

Requirements P0-REQ-001 through P0-REQ-032 retain their meanings; P0-REQ-033 adds the scoped physical-reference checks. Read only those named by the assigned task. Gate-local acceptance tables own planned assertions and pytest nodes; this optional index does not duplicate them.

| Requirement | Required behavior | Specification | Primary gate |
|---|---|---|---|
| P0-REQ-001 | Physical energy and coordinate-transfer implementations remain independent. | [S02](specs/S02-architecture-and-dependencies.md) | [G01](gates/G01-identity-partition-and-contracts.md) |
| P0-REQ-002 | Stable real-atom identities, fixed ML membership, and complete mobile ligands survive remapping. | [S03](specs/S03-data-and-interface-contracts.md) | [G01](gates/G01-identity-partition-and-contracts.md) |
| P0-REQ-003 | The embedding owns an explicit retained-MM, ML, and coupling interaction ledger. | [S04](specs/S04-embedding-and-model-contracts.md) | [G06](gates/G06-periodicity-and-interaction-ledger.md) |
| P0-REQ-004 | Link-coordinate derivatives are propagated once to every affected real parent. | [S04](specs/S04-embedding-and-model-contracts.md) | [G04](gates/G04-link-boundary-and-derivatives.md) |
| P0-REQ-005 | Box, image, cap, graph, and transform conventions agree at every evaluation. | [S04](specs/S04-embedding-and-model-contracts.md) | [G06](gates/G06-periodicity-and-interaction-ledger.md) |
| P0-REQ-006 | The physical result includes forces on every coordinate that influences its energy, including MM atoms. | [S04](specs/S04-embedding-and-model-contracts.md) | [G02](gates/G02-analytic-force-in-native-atm.md) |
| P0-REQ-007 | Environment-dependent inputs are recomputed for each mapped geometry; caches cannot change the Hamiltonian. | [S04](specs/S04-embedding-and-model-contracts.md) | [G02](gates/G02-analytic-force-in-native-atm.md) |
| P0-REQ-008 | Derived link sites have no independent thermal degree of freedom or unintended classical interaction. | [S04](specs/S04-embedding-and-model-contracts.md) | [G04](gates/G04-link-boundary-and-derivatives.md) |
| P0-REQ-009 | Disconnected-component additivity is a local-model test, never a universal embedding assumption. | [S04](specs/S04-embedding-and-model-contracts.md) | [G05](gates/G05-local-model-adapter.md) |
| P0-REQ-010 | Coordinates, energies, forces, timestep, precision, and conversion policy have explicit units. | [S03](specs/S03-data-and-interface-contracts.md) | [G05](gates/G05-local-model-adapter.md) |
| P0-REQ-011 | Every physical term has exactly one owner and a declared ATM child/outside scope. | [S02](specs/S02-architecture-and-dependencies.md) | [G03](gates/G03-atom-routing-and-integration.md) |
| P0-REQ-012 | All intended forces are active in preparation and production integration. | [S02](specs/S02-architecture-and-dependencies.md) | [G03](gates/G03-atom-routing-and-integration.md) |
| P0-REQ-013 | Raw endpoints and mapped forces match independent evaluation with explicit diagnostic ordering. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G02](gates/G02-analytic-force-in-native-atm.md) |
| P0-REQ-014 | Software, model weights, license review, and checkpoint-loading policy are recorded and reproducible. | [S07](specs/S07-artifacts-and-qualification.md) | [G00](gates/G00-environment-and-provenance.md) |
| P0-REQ-015 | Fresh-process reload, restart, parameter changes, and worker devices preserve the declared state. | [S07](specs/S07-artifacts-and-qualification.md) | [G10](gates/G10-restart-and-replica-exchange.md) |
| P0-REQ-016 | Endpoint signs, binding domains, restraints, and standard-state corrections are explicit. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G08](gates/G08-thermodynamics-and-estimators.md) |
| P0-REQ-017 | Directional midpoint identity is demonstrated or a measured bridge is included. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G08](gates/G08-thermodynamics-and-estimators.md) |
| P0-REQ-018 | Saved raw energies reconstruct the actual sampled reduced potentials and schedule. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G08](gates/G08-thermodynamics-and-estimators.md) |
| P0-REQ-019 | Overlap, correlation, and covariance enter the uncertainty assessment. | [S06](specs/S06-validation-and-tolerances.md) | [G08](gates/G08-thermodynamics-and-estimators.md) |
| P0-REQ-020 | Admitted counterfactual geometries have finite, usable model energies and consistent forces. | [S06](specs/S06-validation-and-tolerances.md) | [G05](gates/G05-local-model-adapter.md) |
| P0-REQ-021 | AToM-specific keys, classes, force groups, and units stay inside the workflow adapter. | [S02](specs/S02-architecture-and-dependencies.md) | [G03](gates/G03-atom-routing-and-integration.md) |
| P0-REQ-022 | One- and two-ligand protocols use the same physical and ATM interfaces from the first analytic tests. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G02](gates/G02-analytic-force-in-native-atm.md) |
| P0-REQ-023 | Unsupported chemistry, capabilities, force classes, and combinations fail explicitly. | [S03](specs/S03-data-and-interface-contracts.md) | [G01](gates/G01-identity-partition-and-contracts.md) |
| P0-REQ-024 | Schema changes are versioned, reviewed, and tested against prior serialized fixtures. | [S03](specs/S03-data-and-interface-contracts.md) | [G01](gates/G01-identity-partition-and-contracts.md) |
| P0-REQ-025 | Qualification is scoped to a complete configuration and requires evidence, not a support flag. | [S07](specs/S07-artifacts-and-qualification.md) | [G13](gates/G13-performance-and-release.md) |
| P0-REQ-026 | Specification, failing test, minimum implementation, refactor, and review are traceable. | [S06](specs/S06-validation-and-tolerances.md) | [G01](gates/G01-identity-partition-and-contracts.md) |
| P0-REQ-027 | Performance optimizations preserve the qualified Hamiltonian and deterministic tests. | [S06](specs/S06-validation-and-tolerances.md) | [G13](gates/G13-performance-and-release.md) |
| P0-REQ-028 | Future extension contracts do not imply electrostatic, metal, or reactive support. | [S01](specs/S01-scope-and-invariants.md) | [G07](gates/G07-joint-cavity-ligand-atm.md) |
| P0-REQ-029 | Workers need no unrecorded download and load only approved executable artifacts. | [S07](specs/S07-artifacts-and-qualification.md) | [G10](gates/G10-restart-and-replica-exchange.md) |
| P0-REQ-030 | Independent oracles and deliberately injected faults demonstrate that checks detect errors. | [S06](specs/S06-validation-and-tolerances.md) | [G02](gates/G02-analytic-force-in-native-atm.md) |
| P0-REQ-031 | Protein ABFE and RBFE reuse one cavity/model/boundary definition for comparable results. | [S05](specs/S05-protocol-and-thermodynamic-contracts.md) | [G12](gates/G12-dual-ligand-rbfe.md) |
| P0-REQ-032 | Absent hardware, skipped tests, and short pilots cannot be reported as numerical qualification. | [S07](specs/S07-artifacts-and-qualification.md) | [G13](gates/G13-performance-and-release.md) |
| P0-REQ-033 | Real-model chemical and boundary adequacy is checked on small frozen references with M00-reviewed methods and limits before protein claims. | [S06](specs/S06-validation-and-tolerances.md#small-system-physical-references) | [G05](gates/G05-local-model-adapter.md), [G07](gates/G07-joint-cavity-ligand-atm.md) |
