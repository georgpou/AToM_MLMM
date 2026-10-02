# M02 analytic ATM implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan inline, task by task. The user requested a separate independent combined M02 audit after implementation.

**Goal:** Complete G02 then G03 on `core-analytic-cpu`, inheriting accepted M01 and scientific contract version 1.

**Architecture:** Immutable dependency-light records carry sealed physical artifacts, explicit real/final/model maps and fixed full-particle translations. One native assembler/evaluator consumes these records. A narrow adapter uses the pinned AToM ABFE/RBFE construction and integration methods with explicit force-group routing, without selecting physical energy by protocol.

**Tech stack:** Locked Python 3.11.16, NumPy 2.4.6, OpenMM 8.6.1, AToM 8.5.0b0 (source `9e26c5a3811038be1c98e3be6af4c78cd0dd57a7`); separate locked AmberTools environment.

**Spec:** [M02 handoff](../../project-0/handoffs/M02-implementation-and-audit.md), [G02](../../project-0/gates/G02-analytic-force-in-native-atm.md), [G03](../../project-0/gates/G03-atom-routing-and-integration.md), and their S01–S07 sections.

## Global constraints

- Starting parent/new-branch commit: `87146b4cc7fbd0b58d6688903a5ba081b813ac13`; accepted M01 handoff is an ancestor. Keep main and the parent unchanged, preserve existing work, publish only `m02-analytic-atm`.
- Use nm, kJ/mol, kJ/mol/nm, ps and K; negative gradients on every influencing real atom. Fixed membership and complete mobile ligands; initial protein/cap shifts are zero.
- All physical potential terms belong once under ATM. Outside harmonic restraints are separately declared and counted once. Preparation is a separate all-active group-0 copy.
- Freeze Reference limits at 1e-8 kJ/mol and 1e-7 kJ/mol/nm per component; direct/ATM starting limits remain 1e-4 kJ/mol and 5e-3 kJ/mol/nm. Finite-difference steps: 1e-3, 1e-4, 1e-5 nm. No relaxation.
- No dependency/lock/checkpoint-policy changes; no silent downloads. PythonForce serialization is executable and only explicitly trusted, hash-checked artifacts may be reloaded.
- Admit nonperiodic analytic Reference/CPU double/float64 NVT, with LangevinMiddle or the existing Verlet control and timestep <=0.0005 ps. Neural chemistry, caps, periodic physics, actual electrostatic physics and molecular binding remain unqualified.

## Review focus

- Nonidentity `oldToNew`, permuted selected-particle order and unequal noncontiguous ligand groups must preserve full maps, identity and force order.
- Mutation of a child, full displacement map, fixed membership or restored parameter state must fail before evaluation or be explicitly restored and checked.
- Missing, duplicate, nested or misrouted physical forces must fail recursive ownership and numerical checks; integrator masks need their own marker-force check.
- Soft-core/softplus transition regions, reverse direction, offsets and invalid parameter domains must retain the exact expression and chain rule.
- Fresh-process trusted serialization must work offline with no original cache; corrupt or untrusted bytes must fail before executable deserialization.

## Task 1: Fresh baseline and G02 records/maps

**Files:** Extend `src/atm_mlmm/schema.py`; create `geometry.py`, `tests/contracts/test_transfer_protocols.py`, `fixtures/analytic/`; preserve the existing protocol descriptions and identity validator.

**Interfaces:** `resolve_protocol(bundle: PhysicalBundle, protocol: ProtocolSpec) -> TransferDefinition`; explicit consumed `oldToNew`, real/final/model maps. New records use the existing version-1 JSON machinery; runtime contexts are separate.

- [ ] Activate the locked installation in every shell; save strict validation and full/analytic baseline outputs. Resolve any reproducible baseline failure without weakening assertions.
- [ ] Write and run failing map/record tests, including `test_one_and_two_unequal_mobile_groups`, nonidentity source mapping, round trips, invalid membership and malformed/unsupported map requests.
- [ ] Implement immutable M02 records and the generic resolver; keep heavy imports out of common records/protocols.
- [ ] Run affected tests and existing schema/architecture tests; expect complete passes.

## Task 2: Complete G02 native oracle

**Files:** Create `src/atm_mlmm/analytic.py`, `atm.py`, `schedule.py`, `endpoints.py`, `derivatives.py`; create `tests/integration/test_pythonforce_atm.py`, `tests/contracts/test_physical_evaluator.py`, `tests/contracts/test_fault_injection.py` and test-only oracle utilities.

**Interfaces:** `make_analytic_bundle` produces the same PhysicalBundle for both protocol shapes. `build_atm(bundle, transfer, schedule, restraints) -> AlchemicalBundle`; `evaluate_physical(bundle, snapshot, runtime) -> EnergyForces`; `evaluate_atm(bundle, snapshot, state_id, runtime) -> AtmEvaluation`. Persistent evaluators permit explicit A-B-A checks without cached geometry inputs.

- [ ] Write all nine G02 gate nodes; run and retain intended absent-API failures after verifying numerical dependencies.
- [ ] Implement importable selected harmonic/environment callbacks, the sealed analytic bundle and one shared native assembler/evaluator. Independently hand-transform coordinates and derive all forces in tests.
- [ ] Test lambda 0/0.37/1, selected order `[2,0]`, nonzero outside energy, explicit `(u1,u0,expression)` tuple and exact nonlinear soft-core/softplus chain rule (both directions, transitions, offsets, finite-difference sweep).
- [ ] Test environment-only motion and A-B-A, fresh offline reload, wrong indices, omitted environment/child forces, stale geometry, reversed tuple, factor-of-ten forces and double counting. Each deliberate fault must trigger a locating diagnostic.
- [ ] Run the exact G02 full-gate command and the available CPU suite; record thresholds and measured errors. Commit G02 code only on the child branch.

## Task 3: Complete G03 adapter and combined handoff

**Files:** Create `src/atm_mlmm/routing.py`, `prepare.py`, `adapters/atom.py`, `tests/workflow/test_atom_force_routing.py`, `tests/workflow/test_active_force_groups.py`; extend architecture checks; write `Worker_Log/Milestone_02/Gate_02_v1_worker.md`, `Gate_03_v1_worker.md` and evidence.

**Interfaces:** Separate preparation/export copies preserve the physical identity and maps. Routing reports enumerate recursive ownership. The adapter selects pinned upstream protocol classes, keys and units, invokes their actual construction/integrator methods, and hands over/checks State parameters. Shared native evaluation remains protocol/provider-independent.

- [ ] Write/run the seven G03 failing gate nodes before implementation.
- [ ] Implement reserved-group admission, explicit upstream routing, recursive ownership/removal checks and separate group-0 preparation.
- [ ] Compare both upstream protocol paths against G02 direct/native observables. Verify 0.5 fs ->0.0005 ps and nm ->Angstrom once; actual LangevinMiddle masks and large markers in preparation/ABFE/RBFE; full maps after construction, changes and reload.
- [ ] Run G02/G03 commands, analytic selection, full available suite, upstream regression, documentation self-tests and `git diff --check`; save exact outputs, identities and numerical measurements.
- [ ] Pin the completed snapshot in a commit. Arrange a reviewer who authored none of the changes to independently audit all G02/G03 requirements and combined M02 with the accepted M01 prerequisite. Preserve submitted logs/findings; use new attempts and failing/passing regressions for repairs and independent closure.
- [ ] Update STATUS and acceptance evidence from the actual audit decision. Commit report-only additions, push only the new branch, verify remote identity and a clean worktree; report exact tests and remaining profile limits.

## Execution record

The existing clean checkout is suitable; repository instructions expressly prefer it. Implementation is inline, with one separate independent combined reviewer. This is execution of the user's supplied reviewed contracts and handoff, not a change to scientific definitions requiring a new design approval.
