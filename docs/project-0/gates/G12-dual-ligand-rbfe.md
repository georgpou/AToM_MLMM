# G12: Run the first two-ligand RBFE example

**Part of:** [M07](../milestones/M07-rbfe-demonstration.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

The shared architecture already allows two mobile groups. This gate checks the molecular result, both ligand identities, and the meaning of comparisons against ABFE.

## Expected outcome

A nontrivial ligand-pair example, an identity control, a sign-reversal check, and a careful comparison of matching thermodynamic states.

**Not part of this gate:** Do not create an RBFE-specific energy engine. Do not interpret a finite-box spectator-ligand effect as a code defect without checking the state definitions.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M07: outcome and dependencies](../milestones/M07-rbfe-demonstration.md) | See how this gate fits into the larger result. |
| [S05: One protocol contract, two initial presets](../specs/S05-protocol-and-thermodynamic-contracts.md#one-protocol-contract-two-initial-presets) | Handle one or two complete ligand groups through the same shared records. |
| [S05: Shared analysis and molecular closure](../specs/S05-protocol-and-thermodynamic-contracts.md#shared-analysis-and-molecular-closure) | Compare free-energy differences only after matching their state definitions. |
| [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules) | Preserve real atom identities when building final particle maps. |
| [This gate's log folder](../../../Worker_Log/Milestone_07/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G11](../gates/G11-protein-abfe.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G11 protein ABFE baseline; G02/G03 early two-ligand contracts; G10 worker reliability; a reviewed ligand-pair manifest.

**Outputs used by later gates:** One nontrivial RBFE profile, A-to-A and reversal controls, graph/identity evidence and a matched-state closure report.

**Planned source/test paths:** `fixtures/protein_two_ligands/`, `tests/workflow/test_rbfe_transforms.py`, `tests/sampling/test_binding_closure.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G12-T1` | Qualify molecular two-ligand geometry on the small fixture | `P0-TEST-G12-01`, `P0-TEST-G12-02`, `P0-TEST-G12-06` |
| `G12-T2` | Run identity, reversal and nontrivial-pair controls | `P0-TEST-G12-03`, `P0-TEST-G12-04`, `P0-TEST-G12-06` |
| `G12-T3` | Interpret closure against matched states | `P0-TEST-G12-05` |

### G12-T1: qualify molecular two-ligand geometry on the small fixture

Add a second complete ligand first to the small solvated fixture. Use explicit opposite fixed maps and hand-checked final identities. Test both coordinate states, cap-parent derivatives and unexpected ligand-ligand/image contacts. The architecture already admitted two groups in G02; this gate adds molecular evidence rather than introducing the concept for the first time.

Keep one cavity, model, cap, embedding and classical convention across comparable calculations. Do not change the receptor model per ligand while expecting exact cancellation. Re-run fresh-process and two-worker checks with the larger joint model input.

**Finish this part with:** the relevant test results above and a worker log that states `G12-T1` as its scope. Completing this part alone does not complete G12.

### G12-T2: run identity, reversal and nontrivial-pair controls

Use a symmetric A-to-A calculation with matched restraints. Its equilibrium free-energy difference should be zero, but its instantaneous perturbations can be nonzero because environments and conformations differ. Evaluate zero-consistency using the declared uncertainty criteria and adequate overlap.

Then run a nontrivial A-to-B pair and reverse the endpoint labeling. Apply the explicit relative sign convention from S05. Check that identity/name ordering and upstream-specific keys never change the selected ligand set or reverse a correction silently.

**Finish this part with:** the relevant test results above and a worker log that states `G12-T2` as its scope. Completing this part alone does not complete G12.

### G12-T3: interpret closure against matched states

Compare an RBFE with corresponding ABFE differences and, where useful, a small closed cycle. The two-ligand box has a spectator molecule: simple subtraction of independent one-ligand ABFEs is not automatically an exact closure relation. Use matched spectator controls or quantify the contribution, alongside restraint, finite-box and model-region differences.

Keep covariance where calculations share data or corrections. A mismatch first triggers an audit of thermodynamic definition, restraints, identity and spectator effects; it is not immediate evidence of faulty ML chemistry.

**Finish this part with:** the relevant test results above and a worker log that states `G12-T3` as its scope. Completing this part alone does not complete G12.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G12-01 | `tests/workflow/test_rbfe_transforms.py::test_opposite_group_maps_and_cap_identity` | Complete A/B groups receive the prescribed opposite translations; protein/cap maps and identities remain unchanged. | P0-REQ-022, P0-REQ-002 |
| P0-TEST-G12-02 | `tests/workflow/test_rbfe_transforms.py::test_correct_bound_component_and_no_spurious_contact` | Each endpoint connects the intended local-model ligand to the cavity and excludes unintended other-ligand/image contacts. | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G12-03 | `tests/sampling/test_binding_closure.py::test_symmetric_a_to_a_free_energy` | Symmetric A-to-A equilibrium difference is compatible with zero under predeclared uncertainty criteria, without requiring instantaneous perturbation zero. | P0-REQ-016 |
| P0-TEST-G12-04 | `tests/sampling/test_binding_closure.py::test_reversed_pair_sign` | Reversed endpoint labels negate the intended relative observable while preserving the same physical model and correction accounting. | P0-REQ-016, P0-REQ-031 |
| P0-TEST-G12-05 | `tests/sampling/test_binding_closure.py::test_abfe_rbfe_comparison_matches_states` | Account for spectator-ligand, restraint, cavity/model/constraint and finite-box differences before interpreting closure. | P0-REQ-031, P0-REQ-019 |
| P0-TEST-G12-06 | `tests/workflow/test_rbfe_transforms.py::test_shared_pipeline_and_restart` | The larger joint input uses the same physical builder, ATM assembler, observable schema and restart contracts without per-RBFE physics forks. | P0-REQ-001, P0-REQ-022, P0-REQ-015 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_rbfe_transforms.py tests/sampling/test_binding_closure.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** A graph/map/identity failure returns to the existing small two-group oracle. A closure failure requires state matching before code or model changes. Do not create a second simulation engine to make one RBFE example run.

## Keep future changes possible

This milestone tests the benefit of designing multiple-group protocols early. Actual electrostatic RBFE will need a new physical profile, not a duplicate pipeline.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_07/`\
**Task stem:** `Gate_12`\
**Worker:** `Gate_12_vN_worker.md`\
**Matching audit:** `Gate_12_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
