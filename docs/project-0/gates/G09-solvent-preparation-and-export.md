# G09: Add solvent and hand the prepared system to a worker

**Part of:** [M05](../milestones/M05-solvated-workflow.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

Water, periodic electrostatics, and saved input files introduce new ways to change a validated system unintentionally. The actual worker must load the same physical and thermodynamic definitions.

## Expected outcome

A self-contained solvated example whose preparation, exported files, worker state, energies, and forces agree.

**Not part of this gate:** A short pilot checks workflow behavior; it is not automatically a converged binding calculation.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M05: outcome and dependencies](../milestones/M05-solvated-workflow.md) | See how this gate fits into the larger result. |
| [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution) | Count each force once and make sure the integrator uses it. |
| [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting) | Check periodic contacts and the terms that remain in the mixed energy. |
| [S07: Planned artifact bundle](../specs/S07-artifacts-and-qualification.md#planned-artifact-bundle) | Save enough information for another process to reconstruct the system. |
| [S07: Required observable names](../specs/S07-artifacts-and-qualification.md#required-observable-names) | Preserve unambiguous endpoint, outside, and total energy records. |
| [This gate's log folder](../../../Worker_Log/Milestone_05/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G07](../gates/G07-joint-cavity-ligand-atm.md), [G08](../gates/G08-thermodynamics-and-estimators.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G07 joint physical model; G08 thermodynamic/analysis definitions and known-answer checks.

**Outputs used by later gates:** Solvated capped-fragment bundle, project-owned preparation, pinned AToM export, and short multiwindow preflight evidence.

**Planned source/test paths:** `fixtures/solvated_fragment/`, `prepare.py`, `persistence.py`, `adapters/atom.py`, `tests/workflow/test_solvated_handover.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G09-T1` | Add solvent without changing the embedded model | `P0-TEST-G09-01` |
| `G09-T2` | Own the preparation sequence and export | `P0-TEST-G09-02`, `P0-TEST-G09-03` |
| `G09-T3` | Run a pilot without relabeling it convergence | `P0-TEST-G09-04`, `P0-TEST-G09-05` |

### G09-T1: add solvent without changing the embedded model

Use the same neutral capped-fragment/ligand fixture and a declared classical solvent convention. Choose a box with two admitted physical ligand placements. Check the entire protein/fragment and periodic images, not only local model edges. Retain and test classical ligand-water/ion coupling in the separated state.

Declare NVT temperature, conservative timestep, constraints, PME and dispersion settings. Density equilibration, if used, is a separately checked preparation operation; fixed-volume production does not imply that untested pressure/virial behavior is supported.

**Finish this part with:** the relevant test results above and a worker log that states `G09-T1` as its scope. Completing this part alone does not complete G09.

### G09-T2: own the preparation sequence and export

Use the all-active physical preparation copy for minimization and gradual thermalization. Then create the validated alchemical states from G08's exact expressions. Do not inherit hidden stock timesteps or intermediate-parameter assignments. Check that the initial topology/PDB coordinates are safe for any preliminary evaluation, even when the higher-precision State replaces them afterward.

The inherited pinned handover uses `<basename>.pdb`, `<basename>_sys.xml`, and `<basename>_0.xml`; verify the complete actual contract in the admitted AToM source. Include model and environment manifests, atom maps, ledger, schedules and restraint obligations. Load through the real worker construction path and compare observables before a single step.

**Finish this part with:** the relevant test results above and a worker log that states `G09-T2` as its scope. Completing this part alone does not complete G09.

### G09-T3: run a pilot without relabeling it convergence

Run a small multiwindow schedule only after direct/worker parity. Save both raw endpoint energies and representative coordinates. Independently reevaluate states, check the directional connection, monitor counterfactual model domain and periodic separation, and record state labels.

This gate demonstrates complete solvated plumbing. Its duration is chosen for these checks, not by copying a publication's production length. A successful short pilot is not a converged affinity or an experimental-accuracy assessment.

**Finish this part with:** the relevant test results above and a worker log that states `G09-T3` as its scope. Completing this part alone does not complete G09.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G09-01 | `tests/workflow/test_solvated_handover.py::test_bulk_site_and_real_cross_forces` | Bulk placement clears the full solute and relevant images; ligand retains classical solvent interactions. | P0-REQ-003, P0-REQ-005 |
| P0-TEST-G09-02 | `tests/workflow/test_solvated_handover.py::test_same_hamiltonian_in_preparation` | Minimization/thermalization and production export share physical identity, constraints and all-active force semantics. | P0-REQ-012, P0-REQ-021 |
| P0-TEST-G09-03 | `tests/workflow/test_solvated_handover.py::test_worker_load_matches_direct_state` | Reload expected PDB/System/State handover, then compare coordinates, box, parameters, constraints, energies and real forces before stepping. | P0-REQ-015, P0-REQ-021 |
| P0-TEST-G09-04 | `tests/workflow/test_solvated_handover.py::test_saved_raw_records_reconstruct_states` | Every saved pilot record preserves unambiguous raw energies, direction and state ID and permits independent reevaluation. | P0-REQ-018 |
| P0-TEST-G09-05 | `tests/workflow/test_solvated_handover.py::test_both_mapped_geometries_remain_admitted` | Pilot frames check caps, periodic separation, graph edges and nonfinite alternate-state behavior; failures archive both geometries. | P0-REQ-020, P0-REQ-005 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_solvated_handover.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** If preparation changes the physical identity or export/reload changes observables, reduce to the small fixture. Do not treat solvated noise as an explanation for a deterministic mismatch.

## Keep future changes possible

The preparation function consumes admitted bundles and shared phase settings. It must not become a separate pipeline per embedding or per ligand count.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_05/`\
**Task stem:** `Gate_09`\
**Worker:** `Gate_09_vN_worker.md`\
**Matching audit:** `Gate_09_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
