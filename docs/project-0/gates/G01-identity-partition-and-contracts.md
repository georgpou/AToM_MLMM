# G01: Give every atom a reliable identity and define shared records

**Part of:** [M01](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

Link atoms can change particle counts and array positions. The code must still know which real atom it is moving. Shared records must also support both one and two ligands before either protocol becomes complicated.

## Expected outcome

Checked atom identities, fixed ML selections, shared input/output records, and a saved inventory of the original MM system.

**Not part of this gate:** No neural model or protein binding calculation is needed. Do not bury one-ligand assumptions inside common records.

## Before starting

Required earlier gates: [G00](../gates/G00-environment-and-provenance.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G00 environment/source identity; reviewed record definitions and scope.

**Outputs used by later gates:** Checked records that do not require heavy model libraries; `resolve_partition`; `validate_request`; saved input examples with a format version; an unchanged original-MM inventory and atom maps.

**Planned source/test paths:** `schema.py`, `capabilities.py`, `identity.py`, `partition.py`, `ledger.py`, `tests/unit/test_identity.py`, `tests/unit/test_partition.py`, `tests/contracts/`, `tests/unit/test_force_inventory.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G01-T1` | Implement stable identities and fixed selection | `P0-TEST-G01-01`, `P0-TEST-G01-02` |
| `G01-T2` | Implement the common records and extension boundaries | `P0-TEST-G01-03`, `P0-TEST-G01-04`, `P0-TEST-G01-05` |
| `G01-T3` | Inventory the original MM system and connect requirements to evidence | `P0-TEST-G01-06`, `P0-TEST-G01-07` |

### G01-T1: implement stable identities and fixed selection

**Read:** [S03: Shared units and array conventions](../specs/S03-data-and-interface-contracts.md#shared-units-and-array-conventions); [S03: AtomIdentity and TopologyView rows](../specs/S03-data-and-interface-contracts.md#records-required-fields-and-ownership); [S04: Mechanical baseline and boundary policy](../specs/S04-embedding-and-model-contracts.md#mechanical-baseline-and-boundary-policy).

Implement the minimum `AtomIdentity` and `TopologyView` fields needed for this task from S03; G01-T2 completes the other shared records. Do not invent a second temporary identity format.

Use unique per-input real-atom IDs together with chain, residue, insertion, element, and atom-name metadata. Build intentionally awkward topologies: duplicate residue numbers, noncontiguous ligand atoms, reordered particles, and incomplete molecules. Establish expected selected identities by hand. Resolve boundaries using actual connectivity and include the selected fragment's hydrogens.

Enumerate and validate every crossing bond. Begin with the reviewed neutral single-cut policy. Reject unknown elements, unsupported chemistry, ambiguous charged fragments, and multiple caps per MM parent. Distinguish formal chemical states from inherited partial-charge sums. Reject before context construction when the metadata suffices.

### G01-T2: implement the common records and extension boundaries

**Read:** [S03: Records, required fields, and ownership](../specs/S03-data-and-interface-contracts.md#records-required-fields-and-ownership); [S03: Errors, capabilities, and schema evolution](../specs/S03-data-and-interface-contracts.md#errors-capabilities-and-schema-evolution); [S02: Dependency rules and ownership tests](../specs/S02-architecture-and-dependencies.md#dependency-rules-and-ownership-tests).

Implement the fields in S03, including a tuple of `MobileGroup` records and forces on all real atoms in `EnergyForces`. The ABFE/RBFE protocol checks whether it has the required number of ligands; the shared physical record does not assume that number. Do not encode a required first ligand and optional second ligand throughout common records.

Add schema-version, round-trip, unit, empty-field, and unknown-capability tests. Prevent shared data from being changed accidentally after it is finalized. A schema record can exist before a physical implementation, but cannot imply the capability works. Test that basic records can be imported without loading a model or GPU library. Do not add unused future model classes.

### G01-T3: inventory the original MM system and connect requirements to evidence

**Read:** [S04: The physical contract is broader than the first embedding](../specs/S04-embedding-and-model-contracts.md#the-physical-contract-is-broader-than-the-first-embedding); [S03: ledger/evidence record rows](../specs/S03-data-and-interface-contracts.md#records-required-fields-and-ownership); [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested).

Capture particle counts, masses, constraints, force classes/names/groups, bonded terms, exceptions, offsets, and box settings before conversion. Use distinctive fixture parameters. Unknown force types fail rather than being silently ignored. Save the original immutable fixture and its identity.

Implement the lightweight evidence-record validation needed for later tests. Each planned behavior has requirement IDs and an independent expected result. The existence of this record does not make its tests pass; it prevents status from drifting away from evidence.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

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

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/unit/test_identity.py tests/unit/test_partition.py tests/contracts/test_schema.py tests/contracts/test_architecture_boundaries.py tests/contracts/test_capabilities.py tests/contracts/test_evidence_schema.py tests/unit/test_force_inventory.py -v
```

**Stop and diagnose:** Unresolved identity, connectivity, unit semantics, or conflicts in shared inputs and outputs stop implementation at this layer. Do not build neural model logic on top of ambiguous atom ownership.

## Keep future changes possible

The shared records already allow one or two ligand groups and forces on every real atom. Real RBFE and electrostatic physics are not required to test these data boundaries.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_01/`\
**Worker:** `Gate_01_vN_worker.md`; **audit:** `Gate_01_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M01 combined review

**Review scope:** G00, G01. **Earlier milestone reviews:** M00. These are combined-review conditions, not additional implementation prerequisites.

Review the G00 manifest rather than just import screenshots. Software identity includes source commit, package metadata, resolved builds and checkpoint digest. Missing GPU evidence stays missing. M01 may accept the core analytic CPU profile without neural weights; actual model loader/asset prerequisites must be admitted before G05. Confirm the trusted loader policy and allowed model use.

Inspect G01 identity fixtures with duplicate residue numbers, reordered indices, incomplete ligands and forbidden boundaries. Confirm shared records and protocol descriptions import without a model or GPU. Review schema round trips and capability rejection. An actual electrostatic request must not fall back silently to mechanical embedding.

G00 and G01 are accepted for their declared profiles; stable IDs, units, schema and evidence contracts are demonstrable. Any deferred asset/hardware profile is explicitly blocked rather than marked qualified.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_01_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
