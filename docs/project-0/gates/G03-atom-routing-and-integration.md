# G03: Make sure AToM evaluates and integrates every intended force

**Part of:** [M02](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A correct physical system can become wrong when a workflow omits a force, duplicates it, or leaves its force group outside the integrator. Preparation and production both need checking.

## Expected outcome

A small AToM adapter that matches the native-ATM checks for both protocol shapes, with an explicit force-routing report.

**Not part of this gate:** Keep AToM-specific names, units, and class selection inside its adapter. Do not disguise a PythonForce by renaming it.

## Before starting

Required earlier gates: [G01](../gates/G01-identity-partition-and-contracts.md), [G02](../gates/G02-analytic-force-in-native-atm.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G02 native analytic oracles and both protocol definitions; G01 force inventory and stable IDs.

**Outputs used by later gates:** Explicit ownership/routing report; narrow AToM adapter; physical-preparation and production-export copies with checked masks.

**Planned source/test paths:** `routing.py`, `adapters/atom.py`, `prepare.py`, `tests/workflow/test_atom_force_routing.py`, `tests/workflow/test_active_force_groups.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G03-T1` | Route by explicit ownership, not misleading labels | `P0-TEST-G03-01`, `P0-TEST-G03-06` |
| `G03-T2` | Verify actual integration in every stage | `P0-TEST-G03-02`, `P0-TEST-G03-03` |
| `G03-T3` | Contain upstream knowledge | `P0-TEST-G03-04`, `P0-TEST-G03-05` |

### G03-T1: route by explicit ownership, not misleading labels

**Read:** [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution); [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules).

Create a separate physical export copy with all physical potential forces assigned to an unoccupied reserved group, initially 1. Use AToM's explicit group-selection mechanism. Recursively enumerate the constructed system: each physical force belongs once under ATM, each separately defined restraint belongs in its intended scope, and originals are not left active outside after child-force copying.

Do not rename `PythonForce` as a nonbonded force to trigger default matching. The original audit found the default selection insufficient for the cavity-inclusive case; demonstrate this failure in a regression fixture rather than assuming upstream behavior is unchanged.

### G03-T2: verify actual integration in every stage

**Read:** [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution); [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy).

Force routing and integration masks are separate checks. Introduce a marker force large enough that an omitted group is obvious. Compare full-state forces with the groups used by the actual integrator, separately for ABFE, RBFE, and ordinary physical preparation.

Use the project-owned group-0 preparation copy. Export a reserved-group copy only after preparation. Do not feed that copy into an unqualified stock no-ATM path. Keep LangevinMiddle and the conservative timestep explicit; do not assume production settings control stock preparation internals.

### G03-T3: contain upstream knowledge

**Read:** [S02: Dependency rules and ownership tests](../specs/S02-architecture-and-dependencies.md#dependency-rules-and-ownership-tests); [S03: Proposed signatures](../specs/S03-data-and-interface-contracts.md#proposed-signatures).

Keep upstream classes, `VARIABLE_FORCE_GROUP`, ligand selection keys, timestep/displacement units, and file handover names in `adapters/atom.py`. Compare both protocol paths with G02's native oracle before admitting them. Restoring a State may override parameters, so include parameter state in checks rather than comparing only coordinates.

The narrow adapter should reuse upstream scheduling and replica exchange. If a small upstream patch is necessary, document the exact commit/diff and reproducer. Do not fork ATM's mathematical definition to resolve routing.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G03-01 | `tests/workflow/test_atom_force_routing.py::test_pythonforce_explicit_group_route` | The intended Python force is a child of ATM exactly once; the default name-based route is not accepted as proof. | P0-REQ-011, P0-REQ-021 |
| P0-TEST-G03-02 | `tests/workflow/test_active_force_groups.py::test_all_physical_groups_integrated` | Compare full force with the integrator-selected force using a deliberately large marker force in each relevant group. | P0-REQ-012 |
| P0-TEST-G03-03 | `tests/workflow/test_active_force_groups.py::test_preparation_and_export_copies` | The physical preparation copy is all-active; the reserved-group production copy cannot silently omit a physical term. | P0-REQ-012 |
| P0-TEST-G03-04 | `tests/workflow/test_atom_force_routing.py::test_both_protocols_match_native_oracle` | ABFE and RBFE upstream construction paths reproduce the same native-ATM observables without changing the physical builder. | P0-REQ-021, P0-REQ-022 |
| P0-TEST-G03-05 | `tests/workflow/test_atom_force_routing.py::test_upstream_unit_and_key_conversion` | Convert 0.5 fs to 0.0005 ps and nm displacements to Angstrom once; select protocol-specific upstream ligand keys only inside the adapter. | P0-REQ-010, P0-REQ-021 |
| P0-TEST-G03-06 | `tests/workflow/test_atom_force_routing.py::test_duplicate_and_nested_atm_rejected` | Reject an already nested ATM input, an occupied reserved force group, and a physical force left both outside and inside. | P0-REQ-011, P0-REQ-023 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v
```

**Stop and diagnose:** An omitted active group or double-counted force blocks downstream gates even if trajectories appear stable. Fix the adapter or a narrowly identified upstream behavior; do not proceed by relaxing energy tolerances.

## Keep future changes possible

The adapter may select upstream ABFE/RBFE classes, but the scientific physical builder and shared ATM contracts remain unchanged. Environment-dependent analytic forces must still route correctly.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_02/`\
**Worker:** `Gate_03_vN_worker.md`; **audit:** `Gate_03_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M02 combined review

**Review scope:** G02, G03. **Earlier milestone reviews:** M01. These are combined-review conditions, not additional implementation prerequisites.

Review direct/native/AToM comparisons with a nonzero outside restraint. Confirm the raw endpoint tuple order, all-real-force output, subset remapping and active integration masks. Check that the test suite fails when a physical force is omitted or counted twice.

Inspect the unequal two-ligand fixture and the analytic environment-coupled fixture. The same assembler must handle them without added embedding branches. Moving only an MM environment atom and reevaluating A-B-A must produce the expected result, catching stale descriptors and missing environment derivatives.

These are analytic transfer-kernel claims. They do not qualify a pretrained model, protein cap, physical electrostatic embedding or molecular RBFE.

G02 and G03 accepted on admitted analytic profiles, including deliberately introduced mistakes and both protocol shapes. An agent can identify each physical/outside contribution and each module boundary.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_02_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
