# M00 analytic CPU contracts — v1 worker

**Scope:** S01–S07 scientific contract version 1, relevant to G00-T1 and G01-T1/T2/T3 on `core-analytic-cpu`.\
**Outcome:** ready_for_audit.\
**Snapshot:** `m00-audit-m01-development`; base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`; specifications unchanged from base.\
**Author:** Codex / GPT-6; exact model version and reasoning setting not exposed.

## Decisions submitted for independent review

- Preserve S02's physical/protocol/ATM/analysis composition (ADR-0001/0002). Records use stable real IDs and collections of groups, with forces on every influencing real coordinate. No actual electrostatic implementation is admitted.
- Preserve S03's nm, kJ/mol, kJ/mol/nm, ps and K conventions; negative-gradient forces; explicit nonperiodic box; immutable owned data; strict versioned JSON. M01 implements the records needed for input, selection, protocol descriptions, full-force results and evidence. Runtime engines and later-gate records wait for their owning gates.
- Preserve S04's retained-MM plus local-model Hamiltonian, ordinary neutral C–C protein cuts, fixed-distance cap Jacobian and single force projection. Formal chemical state is explicit and distinct from partial-charge sums. Cut rings, peptide bonds, disulfides, ligand cuts and repeated MM cap parents are rejected. Connectivity determines fragment hydrogens.
- Preserve S05's fixed full-particle maps, nonlinear expression derivatives, endpoint signs, midpoint bridge, finite-wall restraint volume and correction completeness. These definitions are reviewed here; numerical implementation belongs to later gates.
- Preserve S06's exact structural equality and starting numerical tolerances. No threshold is relaxed. M01 tests identity, record and inventory behavior against hand-specified answers and uses deliberate malformed inputs.
- Preserve S07's profile-specific evidence and independent acceptance. Model assets/GPU tests are nonapplicable to the analytic profile and remain pending for their own profiles.
- Reuse the CPU guide's exact main NumPy 2 / Amber NumPy 1.26 split, native OpenMM ATM, source commits and separate AToM tag/package version. A fresh locked installation is needed on this machine; this review does not assert installation success.

## Extension walkthroughs

An environment-dependent physical energy changes its embedding/model implementation and declared derivative capabilities. It must return forces on the MM environment and rebuild mapped geometry. Protocol descriptions, common results, raw analysis and ATM composition stay unchanged. G02's harmonic ML/MM coordinate probe, then G04/G07's cap-parent probe, provide the behavioral evidence; G01 only verifies the records/import boundary.

Two unequal, noncontiguous mobile molecules change the protocol preset and its group-count/map validation. Neither the physical input nor force record gets a required first/optional second ligand. The same full-particle transfer definition and assembler are retained. G01 tests group data now; G02 tests actual mapped evaluation.

## Physical-reference decision boundary

S06's G05-T4/G07-T4 reference obligations remain mandatory before protein physical claims. This scoped analytic review does **not** accept a chemical profile or invent universal chemical tolerances. Exact capped molecules/conformers/contact geometries, electronic-structure method/basis/settings, digests and profile-specific energy/force/boundary limits require a separate recorded M00 decision **before any reference comparison is inspected**. No such comparison is run in this assignment. Missing reference decisions/data block that later physical profile, not G00/G01 structural work.

## Requirement ownership and handoff

S01 owns scope and fixed membership; S02 owns P0-REQ-001/021 architecture; S03 owns P0-REQ-002/010/024 identities, units and records; S04 owns P0-REQ-003/023 ledger and chemistry; S07 owns P0-REQ-014/025/026 provenance and evidence. G00-01/02 and G01-01 through G01-07 are the executable M01 coverage. P0-REQ-028 prevents a capability declaration being presented as qualification.

Read-only review used M00, G00, G01, S01–S07, README, DEVELOPMENT, AGENTS and the maintained CPU guide. The independent reviewer must identify unresolved conflicts and record the exact accepted scope in the matching audit. Analytic approval does not imply full M00 physical-reference closure.
