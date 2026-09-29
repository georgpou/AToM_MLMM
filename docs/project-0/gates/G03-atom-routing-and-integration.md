# G03: Make sure AToM evaluates and integrates every intended force

**Part of:** [M02](../milestones/M02-transfer-kernel.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

A correct physical system can become wrong when a workflow omits a force, duplicates it, or leaves its force group outside the integrator. Preparation and production both need checking.

## Expected outcome

A small AToM adapter that matches the native-ATM checks for both protocol shapes, with an explicit force-routing report.

**Not part of this gate:** Keep AToM-specific names, units, and class selection inside its adapter. Do not disguise a PythonForce by renaming it.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M02: outcome and dependencies](../milestones/M02-transfer-kernel.md) | See how this gate fits into the larger result. |
| [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution) | Count each force once and make sure the integrator uses it. |
| [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules) | Preserve real atom identities when building final particle maps. |
| [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy) | Distinguish raw child energies, outside terms, and the sampled energy. |
| [This gate's log folder](../../../Worker_Log/Milestone_02/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G01](../gates/G01-identity-partition-and-contracts.md), [G02](../gates/G02-analytic-force-in-native-atm.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G02 native analytic oracles and both protocol definitions; G01 force inventory and stable IDs.

**Outputs used by later gates:** Explicit ownership/routing report; narrow AToM adapter; physical-preparation and production-export copies with checked masks.

**Planned source/test paths:** `routing.py`, `adapters/atom.py`, `prepare.py`, `tests/workflow/test_atom_force_routing.py`, `tests/workflow/test_active_force_groups.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G03-T1` | Route by explicit ownership, not misleading labels | `P0-TEST-G03-01`, `P0-TEST-G03-06` |
| `G03-T2` | Verify actual integration in every stage | `P0-TEST-G03-02`, `P0-TEST-G03-03` |
| `G03-T3` | Contain upstream knowledge | `P0-TEST-G03-04`, `P0-TEST-G03-05` |

### G03-T1: route by explicit ownership, not misleading labels

Create a separate physical export copy with all physical potential forces assigned to an unoccupied reserved group, initially 1. Use AToM's explicit group-selection mechanism. Recursively enumerate the constructed system: each physical force belongs once under ATM, each separately defined restraint belongs in its intended scope, and originals are not left active outside after child-force copying.

Do not rename `PythonForce` as a nonbonded force to trigger default matching. The original audit found the default selection insufficient for the cavity-inclusive case; demonstrate this failure in a regression fixture rather than assuming upstream behavior is unchanged.

**Finish this part with:** the relevant test results above and a worker log that states `G03-T1` as its scope. Completing this part alone does not complete G03.

### G03-T2: verify actual integration in every stage

Force routing and integration masks are separate checks. Introduce a marker force large enough that an omitted group is obvious. Compare full-state forces with the groups used by the actual integrator, separately for ABFE, RBFE, and ordinary physical preparation.

Use the project-owned group-0 preparation copy. Export a reserved-group copy only after preparation. Do not feed that copy into an unqualified stock no-ATM path. Keep LangevinMiddle and the conservative timestep explicit; do not assume production settings control stock preparation internals.

**Finish this part with:** the relevant test results above and a worker log that states `G03-T2` as its scope. Completing this part alone does not complete G03.

### G03-T3: contain upstream knowledge

Keep upstream classes, `VARIABLE_FORCE_GROUP`, ligand selection keys, timestep/displacement units, and file handover names in `adapters/atom.py`. Compare both protocol paths with G02's native oracle before admitting them. Restoring a State may override parameters, so include parameter state in checks rather than comparing only coordinates.

The narrow adapter should reuse upstream scheduling and replica exchange. If a small upstream patch is necessary, document the exact commit/diff and reproducer. Do not fork ATM's mathematical definition to resolve routing.

**Finish this part with:** the relevant test results above and a worker log that states `G03-T3` as its scope. Completing this part alone does not complete G03.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G03-01 | `tests/workflow/test_atom_force_routing.py::test_pythonforce_explicit_group_route` | The intended Python force is a child of ATM exactly once; the default name-based route is not accepted as proof. | P0-REQ-011, P0-REQ-021 |
| P0-TEST-G03-02 | `tests/workflow/test_active_force_groups.py::test_all_physical_groups_integrated` | Compare full force with the integrator-selected force using a deliberately large marker force in each relevant group. | P0-REQ-012 |
| P0-TEST-G03-03 | `tests/workflow/test_active_force_groups.py::test_preparation_and_export_copies` | The physical preparation copy is all-active; the reserved-group production copy cannot silently omit a physical term. | P0-REQ-012 |
| P0-TEST-G03-04 | `tests/workflow/test_atom_force_routing.py::test_both_protocols_match_native_oracle` | ABFE and RBFE upstream construction paths reproduce the same native-ATM observables without changing the physical builder. | P0-REQ-021, P0-REQ-022 |
| P0-TEST-G03-05 | `tests/workflow/test_atom_force_routing.py::test_upstream_unit_and_key_conversion` | Convert 0.5 fs to 0.0005 ps and nm displacements to Angstrom once; select protocol-specific upstream ligand keys only inside the adapter. | P0-REQ-010, P0-REQ-021 |
| P0-TEST-G03-06 | `tests/workflow/test_atom_force_routing.py::test_duplicate_and_nested_atm_rejected` | Reject an already nested ATM input, an occupied reserved force group, and a physical force left both outside and inside. | P0-REQ-011, P0-REQ-023 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** An omitted active group or double-counted force blocks downstream gates even if trajectories appear stable. Fix the adapter or a narrowly identified upstream behavior; do not proceed by relaxing energy tolerances.

## Keep future changes possible

The adapter may select upstream ABFE/RBFE classes, but the scientific physical builder and shared ATM contracts remain unchanged. Environment-dependent analytic forces must still route correctly.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_02/`\
**Task stem:** `Gate_03`\
**Worker:** `Gate_03_vN_worker.md`\
**Matching audit:** `Gate_03_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
