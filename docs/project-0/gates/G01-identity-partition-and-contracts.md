# G01: Give every atom a reliable identity and define shared records

**Part of:** [M01](../milestones/M01-reproducible-foundation.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

Link atoms can change particle counts and array positions. The code must still know which real atom it is moving. Shared records must also support both one and two ligands before either protocol becomes complicated.

## Expected outcome

Checked atom identities, fixed ML selections, shared input/output records, and a saved inventory of the original MM system.

**Not part of this gate:** No neural model or protein binding calculation is needed. Do not bury one-ligand assumptions inside common records.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M01: outcome and dependencies](../milestones/M01-reproducible-foundation.md) | See how this gate fits into the larger result. |
| [S01: Permanent invariants](../specs/S01-scope-and-invariants.md#permanent-invariants) | Keep atom membership, energy meaning, and physical scope unchanged. |
| [S02: Dependency rules and ownership tests](../specs/S02-architecture-and-dependencies.md#dependency-rules-and-ownership-tests) | Keep basic records independent of model imports and GPU setup. |
| [S03: Shared units and array conventions](../specs/S03-data-and-interface-contracts.md#shared-units-and-array-conventions) | Use the same units and atom ordering in every component. |
| [S03: Records, required fields, and ownership](../specs/S03-data-and-interface-contracts.md#records-required-fields-and-ownership) | Implement the agreed record fields rather than a second data format. |
| [S03: Errors, capabilities, and schema evolution](../specs/S03-data-and-interface-contracts.md#errors-capabilities-and-schema-evolution) | Reject unsupported data or requests without silently changing their meaning. |
| [This gate's log folder](../../../Worker_Log/Milestone_01/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G00](../gates/G00-environment-and-provenance.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G00 environment/source identity; reviewed record definitions and scope.

**Outputs used by later gates:** Checked records that do not require heavy model libraries; `resolve_partition`; `validate_request`; saved input examples with a format version; an unchanged original-MM inventory and atom maps.

**Planned source/test paths:** `schema.py`, `capabilities.py`, `identity.py`, `partition.py`, `ledger.py`, `tests/unit/test_identity.py`, `tests/unit/test_partition.py`, `tests/contracts/`, `tests/unit/test_force_inventory.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G01-T1` | Implement stable identities and fixed selection | `P0-TEST-G01-01`, `P0-TEST-G01-02` |
| `G01-T2` | Implement the common records and extension boundaries | `P0-TEST-G01-03`, `P0-TEST-G01-04`, `P0-TEST-G01-05` |
| `G01-T3` | Inventory the original MM system and connect requirements to evidence | `P0-TEST-G01-06`, `P0-TEST-G01-07` |

### G01-T1: implement stable identities and fixed selection

Implement the minimum `AtomIdentity` and `TopologyView` fields needed for this task from S03; G01-T2 completes the other shared records. Do not invent a second temporary identity format.

Use unique per-input real-atom IDs together with chain, residue, insertion, element, and atom-name metadata. Build intentionally awkward topologies: duplicate residue numbers, noncontiguous ligand atoms, reordered particles, and incomplete molecules. Establish expected selected identities by hand. Resolve boundaries using actual connectivity and include the selected fragment's hydrogens.

Enumerate and validate every crossing bond. Begin with the reviewed neutral single-cut policy. Reject unknown elements, unsupported chemistry, ambiguous charged fragments, and multiple caps per MM parent. Distinguish formal chemical states from inherited partial-charge sums. Reject before context construction when the metadata suffices.

**Finish this part with:** the relevant test results above and a worker log that states `G01-T1` as its scope. Completing this part alone does not complete G01.

### G01-T2: implement the common records and extension boundaries

Implement the fields in S03, including a tuple of `MobileGroup` records and forces on all real atoms in `EnergyForces`. The ABFE/RBFE protocol checks whether it has the required number of ligands; the shared physical record does not assume that number. Do not encode a required first ligand and optional second ligand throughout common records.

Add schema-version, round-trip, unit, empty-field, and unknown-capability tests. Prevent shared data from being changed accidentally after it is finalized. A schema record can exist before a physical implementation, but cannot imply the capability works. Test that basic records can be imported without loading a model or GPU library. Do not add unused future model classes.

**Finish this part with:** the relevant test results above and a worker log that states `G01-T2` as its scope. Completing this part alone does not complete G01.

### G01-T3: inventory the original MM system and connect requirements to evidence

Capture particle counts, masses, constraints, force classes/names/groups, bonded terms, exceptions, offsets, and box settings before conversion. Use distinctive fixture parameters. Unknown force types fail rather than being silently ignored. Save the original immutable fixture and its identity.

Implement the lightweight evidence-record validation needed for later tests. Each planned behavior has requirement IDs and an independent expected result. The existence of this record does not make its tests pass; it prevents status from drifting away from evidence.

**Finish this part with:** the relevant test results above and a worker log that states `G01-T3` as its scope. Completing this part alone does not complete G01.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G01-01 | `tests/unit/test_identity.py::test_chain_insertion_and_permutation_identity` | Duplicate residue numbers across chains remain distinct; real IDs survive reordering; ambiguous identities fail explicitly. | P0-REQ-002 |
| P0-TEST-G01-02 | `tests/unit/test_partition.py::test_fixed_complete_mobile_groups` | Resolve complete ligands and all boundary edges; reject incomplete ligands, ring/ligand cuts, duplicate group membership and unsupported fragments. | P0-REQ-002, P0-REQ-023 |
| P0-TEST-G01-03 | `tests/contracts/test_schema.py::test_versioned_round_trip_and_units` | Round-trip reviewed JSON fixtures without changing order/units; reject unknown major schema versions and incompatible required fields. | P0-REQ-024, P0-REQ-010 |
| P0-TEST-G01-04 | `tests/contracts/test_architecture_boundaries.py::test_shared_contracts_have_no_model_import` | Import shared records/protocol descriptions without OpenMM, model weights or CUDA; reject disallowed module dependencies. | P0-REQ-001, P0-REQ-021 |
| P0-TEST-G01-05 | `tests/contracts/test_capabilities.py::test_unsupported_combination_fails_closed` | A requested actual electrostatic profile is rejected rather than relabeled mechanical; a declared capability is not marked qualified. | P0-REQ-023, P0-REQ-028 |
| P0-TEST-G01-06 | `tests/contracts/test_evidence_schema.py::test_acceptance_requires_evidence` | A status update without requirement/test/profile/reviewer evidence cannot satisfy the acceptance schema. | P0-REQ-025, P0-REQ-026 |
| P0-TEST-G01-07 | `tests/unit/test_force_inventory.py::test_original_mm_inventory_and_unknown_force` | Preserve an independently specified original-MM inventory of particles, masses, constraints, force terms, exceptions, offsets, and box settings; reject unsupported force classes rather than omitting them. | P0-REQ-003, P0-REQ-023 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/unit/test_identity.py tests/unit/test_partition.py tests/contracts/test_schema.py tests/contracts/test_architecture_boundaries.py tests/contracts/test_capabilities.py tests/contracts/test_evidence_schema.py tests/unit/test_force_inventory.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Unresolved identity, connectivity, unit semantics, or conflicts in shared inputs and outputs stop implementation at this layer. Do not build neural model logic on top of ambiguous atom ownership.

## Keep future changes possible

The shared records already allow one or two ligand groups and forces on every real atom. Real RBFE and electrostatic physics are not required to test these data boundaries.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_01/`\
**Task stem:** `Gate_01`\
**Worker:** `Gate_01_vN_worker.md`\
**Matching audit:** `Gate_01_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
