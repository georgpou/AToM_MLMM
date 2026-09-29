# G06: Check periodic images and which classical interactions remain

**Part of:** [M03](../milestones/M03-mechanical-hybrid.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

An apparently distant ligand can contact a periodic image. Also, replacing some classical terms with ML can remove or duplicate interactions. Both errors may produce a trajectory without an obvious crash.

## Expected outcome

A term-by-term periodic interaction report and geometry checks that detect unintended image contacts and boundary problems.

**Not part of this gate:** An energy diagnostic is not automatically a free-energy correction. Do not add an unreviewed long-range repair.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M03: outcome and dependencies](../milestones/M03-mechanical-hybrid.md) | See how this gate fits into the larger result. |
| [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting) | Check periodic contacts and the terms that remain in the mixed energy. |
| [S06: Independent oracles and fault injection](../specs/S06-validation-and-tolerances.md#independent-oracles-and-fault-injection) | Use an independent answer and prove the tests catch known mistakes. |
| [Scientific notes](../reference/scientific-notes.md) | Diagnostic-versus-correction meaning or performance units, as relevant. |
| [This gate's log folder](../../../Worker_Log/Milestone_03/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G04](../gates/G04-link-boundary-and-derivatives.md), [G05](../gates/G05-local-model-adapter.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G04 cap/boundary oracle; G05 real model graph and adapter; fixed candidate periodic force settings.

**Outputs used by later gates:** Periodic interaction ledger, independent mask diagnostics, model-graph/distance checks and safe-domain rejection reports.

**Planned source/test paths:** `ledger.py`, `geometry.py`, `tests/integration/test_mechanical_pme.py`, `tests/integration/test_periodic_geometry.py`, `tests/integration/test_masked_interactions.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G06-T1` | Audit the exact builder result on a tiny periodic fixture | `P0-TEST-G06-01`, `P0-TEST-G06-06` |
| `G06-T2` | Build independently checked interaction diagnostics | `P0-TEST-G06-02` |
| `G06-T3` | Validate coordinates and graphs under periodicity | `P0-TEST-G06-03`, `P0-TEST-G06-04`, `P0-TEST-G06-05`, `P0-TEST-G06-06` |

### G06-T1: audit the exact builder result on a tiny periodic fixture

Start with an analytic model substitute and a small charged system, not a protein. Save the original-MM and retained-MM energies on identical coordinates and box. Inspect changed exceptions and every boundary term. Verify ordinary ML-MM interactions survive while artificial cap classical interactions do not appear.

The candidate short-range path retains a periodic electrostatic contribution according to the inherited audit. Measure it under the admitted version rather than calling the entire original cavity-ligand MM interaction 'missing'. Keep cutoff, switching, PME tolerance/realized parameters and dispersion correction explicit. Start the transparent ledger fixture without analytical dispersion correction; any later enabling is a reviewed change.

**Finish this part with:** the relevant test results above and a worker log that states `G06-T1` as its scope. Completing this part alone does not complete G06.

### G06-T2: build independently checked interaction diagnostics

Implement the charge-mask identity from S04. Disable LJ for the electrostatic diagnostic, update exception charge products, and fix realized PME settings consistently. Include nonneutral subsets to expose a background-convention mistake. Test quadratic charge scaling as an independent relation. Implement a separate LJ mask only for supported mixing/switching rules.

These measurements establish what was removed, not an automatic free-energy correction. The optional physical approximation assessment must define the alternative Hamiltonian first. An average energy difference alone is not that correction.

**Finish this part with:** the relevant test results above and a worker log that states `G06-T2` as its scope. Completing this part alone does not complete G06.

### G06-T3: validate coordinates and graphs under periodicity

Use orthorhombic image enumeration to check the admitted minimum-image helper. Test a cap boundary near a box face, whole-molecule wrapping, box changes, a bulk ligand near a periodic cavity copy, and two ligand components where relevant. Compare the independent geometry with actual model neighbor edges, including caps and periodic shifts.

Scan across image-choice seams and model cutoffs. Define any restricted admissible domain explicitly; adding a restraint to keep it safe creates a thermodynamic obligation. A 0.2 nm beyond-cutoff margin is a starting setup guard, not a proof covering all trajectory excursions. Record checks on representative pilot frames once available.

**Finish this part with:** the relevant test results above and a worker log that states `G06-T3` as its scope. Completing this part alone does not complete G06.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G06-01 | `tests/integration/test_mechanical_pme.py::test_ml_mm_cross_interactions_retained` | Moving an MM probe changes expected real ML-MM Coulomb/LJ interactions; the cap creates no new classical interaction center. | P0-REQ-003, P0-REQ-006 |
| P0-TEST-G06-02 | `tests/integration/test_masked_interactions.py::test_pme_charge_mask_cross_identity` | Four charge-mask evaluations reproduce the cross contribution with consistent mesh, exceptions and nonneutral-background convention. | P0-REQ-003 |
| P0-TEST-G06-03 | `tests/integration/test_periodic_geometry.py::test_images_caps_and_bulk_separation` | Catch a periodic cavity/cap/ligand reconnection missed by primary-box distances, including full-protein clearance. | P0-REQ-005 |
| P0-TEST-G06-04 | `tests/integration/test_periodic_geometry.py::test_cap_wrapping_and_image_seam_continuity` | Whole-molecule wrapping and admitted image-choice seams preserve the specified energy/force behavior or are explicitly excluded from the admitted domain. | P0-REQ-005 |
| P0-TEST-G06-05 | `tests/integration/test_periodic_geometry.py::test_backend_graph_matches_independent_geometry` | Actual model edges, including periodic shifts, agree with the admitted independent distance/image search. | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G06-06 | `tests/integration/test_mechanical_pme.py::test_nonstandard_forces_and_box_rejected` | Charge offsets, LJPME, unqualified custom mixing or triclinic cells are rejected rather than approximated silently. | P0-REQ-023 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_mechanical_pme.py tests/integration/test_masked_interactions.py tests/integration/test_periodic_geometry.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Unexplained periodic discontinuity, cross-force loss, or image reconnection blocks periodic production. Fix the exact convention or narrow its allowed range of configurations; do not invent a generic PME correction first.

## Keep future changes possible

The complete physical bundle owns periodic behavior. The transfer assembler never implements a mechanical-only tail removal or assumes a long-range model factorizes.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Task stem:** `Gate_06`\
**Worker:** `Gate_06_vN_worker.md`\
**Matching audit:** `Gate_06_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
