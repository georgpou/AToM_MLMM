# M01 analytic CPU implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. Independent M00 and combined M01 review use superpowers:requesting-code-review.

**Goal:** Implement G00-T1 and G01-T1/T2/T3 with runnable analytic CPU evidence.

**Architecture:** Dependency-light frozen records carry stable real IDs, fixed selections, collections of mobile groups and full real forces. Partition validation owns chemistry/connectivity; the ledger adapter inventories OpenMM without changing the system. Provenance and evidence validation fail explicitly.

**Tech Stack:** Python standard library for records; locked OpenMM for API/inventory checks; pytest in the maintained CPU environment.

**Spec:** S01–S07 version 1; [G00](../../project-0/gates/G00-environment-and-provenance.md), [G01](../../project-0/gates/G01-identity-partition-and-contracts.md), and the scoped [M00 worker](../../../Worker_Log/Milestone_00/Milestone_00_v1_worker.md).

## Global constraints

- Common units: nm, kJ/mol, kJ/mol/nm, ps, K; negative-gradient forces.
- Fixed complete ligand membership; cuts only on supported neutral protein C–C boundaries.
- Shared records/identity/protocols import without OpenMM or ML libraries.
- No changed package locks, silent capability fallback or invented qualification.
- Model/GPU/reference-chemistry scope stays pending; main stays unchanged.

## Review focus

- Reordered atoms and duplicate chain/residue metadata preserve IDs; duplicate IDs fail.
- Hydrogen completion follows bonds; ring/peptide/ligand cuts and charged/unknown fragments fail.
- Input lists/dicts cannot mutate sealed records; incompatible schema fields/units fail.
- Capabilities cannot accept actual electrostatic physics or count declarations as evidence.
- MM exceptions/offsets/settings and unsupported forces are recorded or explicitly rejected.

### Task 1: G00-T1

**Files:** `src/atm_mlmm/environment.py`, `persistence.py`, `tests/unit/test_environment.py`.

**Interfaces:** `check_required_apis()` and `characterize_environment(repository, setup_root)` produce a versioned manifest with exact locks, inventories, source identities and check results.

- [ ] Write/run failing API and complete-manifest tests, including missing API and changed provenance faults.
- [ ] Implement native ATM, selected-particle PythonForce, mixed-system info and serialization probes; verify installed locks/sources and both dependency checks.
- [ ] Run G00 nodes, OpenMM installation and maintained validation; save evidence and worker log.

### Task 2: G01-T1/T2

**Files:** `schema.py`, `identity.py`, `partition.py`, `capabilities.py`, `protocols/abfe.py`, `protocols/rbfe.py`; matching unit/contract tests and versioned fixtures.

**Interfaces:** S03's `resolve_partition(topology, spec)` and `validate_request(request, capabilities)`; protocol-specific group-count validation; strict `to_json/from_json` record round trips.

- [ ] Write/run all five planned identity/partition/schema/architecture/capability nodes against hand-specified inputs and malformed variants.
- [ ] Implement the smallest M01 record set, immutable normalization, stable-ID lookup, graph selection/cut validation and explicit capability rejection.
- [ ] Verify one/two unequal groups, all-real-force order, unit/version rejection and dependency-light imports.

### Task 3: G01-T3 and combined M01

**Files:** `ledger.py`, evidence validation in `schema.py`, `tests/unit/test_force_inventory.py`, `tests/contracts/test_evidence_schema.py`, frozen original-MM fixture.

**Interfaces:** `inventory_system(system)` preserves particles, constraints, box and all supported force parameters; immutable evidence requires requirement/test/profile/snapshot/reviewer coverage before acceptance.

- [ ] Write/run failing independent inventory and acceptance-schema tests, including offsets, force settings and unknown force classes.
- [ ] Implement complete inventory for admitted standard forces without mutation; reject unknown forces; save fixture digest.
- [ ] Run all applicable CPU tests, strict environment validation and documentation checks.
- [ ] Commit tested code and worker logs; obtain independent combined G00/G01/M01 review, repair findings with regression tests, update STATUS and push the development branch.
