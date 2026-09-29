# G05: Check one real ML model and its adapter

**Part of:** [M03](../milestones/M03-mechanical-hybrid.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

A real checkpoint adds units, atom ordering, loading, and model-domain risks. Compare it with its native evaluator before trusting it through the hybrid system.

## Expected outcome

A checkpoint-specific record of native/adapter agreement, boundary forces, loading, and behavior at connected, separated, and compressed geometries.

**Not part of this gate:** Qualify one fixed checkpoint. A toy model cannot stand in for unavailable real-model evidence.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M03: outcome and dependencies](../milestones/M03-mechanical-hybrid.md) | See how this gate fits into the larger result. |
| [S04: Locality is a capability, not a core axiom](../specs/S04-embedding-and-model-contracts.md#locality-is-a-capability-not-a-core-axiom) | Check graph separation only when the model justifies additivity. |
| [S06: Model admissibility before long trajectories](../specs/S06-validation-and-tolerances.md#model-admissibility-before-long-trajectories) | Look for invalid energies or forces before expensive sampling. |
| [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested) | Tie a result to the actual code, checkpoint, input, and hardware. |
| [Environment note](../reference/environment.md) | Candidate software, approved model files, and loading risks. |
| [This gate's log folder](../../../Worker_Log/Milestone_03/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G04](../gates/G04-link-boundary-and-derivatives.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G04 analytic physical-builder/cap contracts; G00 approved asset and candidate environment.

**Outputs used by later gates:** Real mechanical model adapter, native reference evaluator, checkpoint-specific compatibility card, contact-domain data and locality evidence.

**Planned source/test paths:** `models/mace.py`, `model_reference.py`, `hybrid.py`, `fixtures/capped_alanine/`, `tests/integration/test_model_adapter.py`, `tests/integration/test_locality.py`, `tests/integration/test_model_domain.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G05-T1` | Freeze exactly what the model means | `P0-TEST-G05-06` |
| `G05-T2` | Compare independent evaluations | `P0-TEST-G05-01`, `P0-TEST-G05-02`, `P0-TEST-G05-03`, `P0-TEST-G05-04` |
| `G05-T3` | Establish an admitted numerical domain | `P0-TEST-G05-05`, `P0-TEST-G05-06` |

### G05-T1: freeze exactly what the model means

Use one approved local model, initially the proposed MACE-OFF23-small checkpoint. Save elements, architecture, cutoff, dtype, locality, and chemical-domain limitations. Explicitly request the same energy convention in both native and OpenMM paths. The inherited plan distinguishes MACE's `interaction_energy` from a ligand-protein pair energy; do not interpret that name as an interaction decomposition.

Use `energy` as the proposed baseline output and account for the adapter's eV/Angstrom conversion. The inherited adapter factor is 96.4853 for eV to kJ/mol with the additional inverse-length factor for forces; confirm it in the admitted source. Constant atom-reference shifts may cancel for a fixed composition but cannot justify raw comparisons across different atom counts.

**Finish this part with:** the relevant test results above and a worker log that states `G05-T1` as its scope. Completing this part alone does not complete G05.

### G05-T2: compare independent evaluations

Use a neutral ligand, a precisely capped side-chain fixture, and a joint contacting complex. Record actual model input ordering, caps, box and settings. Compare energy and raw model-coordinate gradients through the native interface, then compare projected real-parent forces in the physical bundle. Run finite-difference step sweeps rather than accepting a single fortuitous step size.

Test translation, consistent joint rotation/box handling, and atom permutations. Separate components beyond all actual neighbor edges and compare against compatible separate evaluations. In the contacting fixture ensure the joint graph is really supplied; splitting residues/ligands into batch items would remove desired interactions.

**Finish this part with:** the relevant test results above and a worker log that states `G05-T2` as its scope. Completing this part alone does not complete G05.

### G05-T3: establish an admitted numerical domain

Run approach, compression, cap-adjacent rotation, cutoff-crossing and separated-state scans. Inspect the alternate geometry that ATM will evaluate even when it carries little current weight. Characterize deliberate extreme overlaps without pretending every singular coincidence must be supported. Save nonfinite results and unphysical wells rather than masking them.

Test offline fresh-process loading and serialization on CPU. GPU qualification follows the same mathematical checks with its own measured precision. Actual chemical accuracy or fine-tuning remains a separate study unless the candidate model fails to provide a usable potential on the allowed range of configurations.

**Finish this part with:** the relevant test results above and a worker log that states `G05-T3` as its scope. Completing this part alone does not complete G05.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G05-01 | `tests/integration/test_model_adapter.py::test_native_and_openmm_energy_forces` | Same asset, ordered coordinates, box, dtype and energy convention agree within calibrated reference tolerances. | P0-REQ-010 |
| P0-TEST-G05-02 | `tests/integration/test_model_adapter.py::test_real_parent_forces_with_model_caps` | Native raw cap derivatives, projected by the independent oracle, match real-parent OpenMM forces. | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G05-03 | `tests/integration/test_locality.py::test_declared_local_component_additivity` | A disconnected joint ML graph equals separately evaluated compatible components; the assertion is not applied to the total hybrid energy or a nonlocal provider. | P0-REQ-009 |
| P0-TEST-G05-04 | `tests/integration/test_model_adapter.py::test_consistent_translation_rotation_and_permutation` | Joint coordinate/box transformations and atom reordering preserve the expected scalar/vector behavior. | P0-REQ-010, P0-REQ-030 |
| P0-TEST-G05-05 | `tests/integration/test_model_domain.py::test_contact_cutoff_and_counterfactual_scans` | Admitted contact and cutoff scans yield finite values and interpretable repulsion; preserve failing alternate geometry and graph for diagnosis. | P0-REQ-020 |
| P0-TEST-G05-06 | `tests/integration/test_model_adapter.py::test_local_asset_fresh_process_reload` | The exact checkpoint and output convention survive offline reload; no cache-dependent replacement or dtype change occurs. | P0-REQ-014, P0-REQ-029 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_model_adapter.py tests/integration/test_locality.py tests/integration/test_model_domain.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Distinguish model-domain failures from mapping, units, precision and neighbor construction. A model replacement or residual repulsion changes the physical definition and requires reviewed requalification, not a hidden fallback.

## Keep future changes possible

Locality is declared by the provider and used only by appropriate tests. Another local model should satisfy the same contract suite; an environment-dependent provider is not required to pass vacuum-style disconnected additivity.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Task stem:** `Gate_05`\
**Worker:** `Gate_05_vN_worker.md`\
**Matching audit:** `Gate_05_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
