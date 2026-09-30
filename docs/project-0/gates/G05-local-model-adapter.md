# G05: Check one real ML model and its adapter

**Part of:** [M03](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A real checkpoint adds units, atom ordering, loading, and model-domain risks. Compare it with its native evaluator before trusting it through the hybrid system.

## Expected outcome

A checkpoint-specific record of native/adapter agreement, boundary forces, loading, and behavior at connected, separated, and compressed geometries.

**Not part of this gate:** Qualify one fixed checkpoint. A toy model cannot stand in for unavailable real-model evidence.

## Before starting

Required earlier gates: [G04](../gates/G04-link-boundary-and-derivatives.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G04 analytic physical-builder/cap contracts; G00 approved asset and candidate environment.

**Outputs used by later gates:** Real mechanical model adapter, native reference evaluator, checkpoint-specific compatibility card, contact-domain data and locality evidence.

**Planned source/test paths:** `models/mace.py`, `model_reference.py`, `hybrid.py`, `fixtures/capped_alanine/`, `tests/integration/test_model_adapter.py`, `tests/integration/test_locality.py`, `tests/integration/test_model_domain.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G05-T1` | Freeze exactly what the model means | `P0-TEST-G05-06` |
| `G05-T2` | Compare independent evaluations | `P0-TEST-G05-01`, `P0-TEST-G05-02`, `P0-TEST-G05-03`, `P0-TEST-G05-04` |
| `G05-T3` | Establish an admitted numerical domain | `P0-TEST-G05-05`, `P0-TEST-G05-06` |

### G05-T1: freeze exactly what the model means

**Read:** [Environment: model assets and loading](../../../ATM_MLMM_Environment.md#model-assets-and-loading); [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested).

Use one approved local model, initially the proposed MACE-OFF23-small checkpoint. Save elements, architecture, cutoff, dtype, locality, and chemical-domain limitations. Explicitly request the same energy convention in both native and OpenMM paths. The inherited plan distinguishes MACE's `interaction_energy` from a ligand-protein pair energy; do not interpret that name as an interaction decomposition.

Use `energy` as the proposed baseline output and account for the adapter's eV/Angstrom conversion. The inherited adapter factor is 96.4853 for eV to kJ/mol with the additional inverse-length factor for forces; confirm it in the admitted source. Constant atom-reference shifts may cancel for a fixed composition but cannot justify raw comparisons across different atom counts.

### G05-T2: compare independent evaluations

**Read:** [S04: Locality is a capability, not a core axiom](../specs/S04-embedding-and-model-contracts.md#locality-is-a-capability-not-a-core-axiom); [S06: Starting numerical thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds).

Use a neutral ligand, a precisely capped side-chain fixture, and a joint contacting complex. Record actual model input ordering, caps, box and settings. Compare energy and raw model-coordinate gradients through the native interface, then compare projected real-parent forces in the physical bundle. Run finite-difference step sweeps rather than accepting a single fortuitous step size.

Test translation, consistent joint rotation/box handling, and atom permutations. Separate components beyond all actual neighbor edges and compare against compatible separate evaluations. In the contacting fixture ensure the joint graph is really supplied; splitting residues/ligands into batch items would remove desired interactions.

### G05-T3: establish an admitted numerical domain

**Read:** [S06: Model admissibility before long trajectories](../specs/S06-validation-and-tolerances.md#model-admissibility-before-long-trajectories); [S04: Model data and local disconnected fragments](../specs/S04-embedding-and-model-contracts.md#model-data-and-local-disconnected-fragments).

Run approach, compression, cap-adjacent rotation, cutoff-crossing and separated-state scans. Inspect the alternate geometry that ATM will evaluate even when it carries little current weight. Characterize deliberate extreme overlaps without pretending every singular coincidence must be supported. Save nonfinite results and unphysical wells rather than masking them.

Test offline fresh-process loading and serialization on CPU. GPU qualification follows the same mathematical checks with its own measured precision. Actual chemical accuracy or fine-tuning remains a separate study unless the candidate model fails to provide a usable potential on the allowed range of configurations.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G05-01 | `tests/integration/test_model_adapter.py::test_native_and_openmm_energy_forces` | Same asset, ordered coordinates, box, dtype and energy convention agree within calibrated reference tolerances. | P0-REQ-010 |
| P0-TEST-G05-02 | `tests/integration/test_model_adapter.py::test_real_parent_forces_with_model_caps` | Native raw cap derivatives, projected by the independent oracle, match real-parent OpenMM forces. | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G05-03 | `tests/integration/test_locality.py::test_declared_local_component_additivity` | A disconnected joint ML graph equals separately evaluated compatible components; the assertion is not applied to the total hybrid energy or a nonlocal provider. | P0-REQ-009 |
| P0-TEST-G05-04 | `tests/integration/test_model_adapter.py::test_consistent_translation_rotation_and_permutation` | Joint coordinate/box transformations and atom reordering preserve the expected scalar/vector behavior. | P0-REQ-010, P0-REQ-030 |
| P0-TEST-G05-05 | `tests/integration/test_model_domain.py::test_contact_cutoff_and_counterfactual_scans` | Admitted contact and cutoff scans yield finite values and interpretable repulsion; preserve failing alternate geometry and graph for diagnosis. | P0-REQ-020 |
| P0-TEST-G05-06 | `tests/integration/test_model_adapter.py::test_local_asset_fresh_process_reload` | The exact checkpoint and output convention survive offline reload; no cache-dependent replacement or dtype change occurs. | P0-REQ-014, P0-REQ-029 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_model_adapter.py tests/integration/test_locality.py tests/integration/test_model_domain.py -v
```

**Stop and diagnose:** Distinguish model-domain failures from mapping, units, precision and neighbor construction. A model replacement or residual repulsion changes the physical definition and requires reviewed requalification, not a hidden fallback.

## Keep future changes possible

Locality is declared by the provider and used only by appropriate tests. Another local model should satisfy the same contract suite; an environment-dependent provider is not required to pass vacuum-style disconnected additivity.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Worker:** `Gate_05_vN_worker.md`; **audit:** `Gate_05_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).
