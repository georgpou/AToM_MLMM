# G02: Check ATM using energies and forces with known answers

**Part of:** [M02](../milestones/M02-transfer-kernel.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

A simple spring-like energy has an answer we can calculate independently. It reveals mapping and force errors before a real model or a protein makes them difficult to isolate.

## Expected outcome

One shared ATM route that reproduces known energies and forces for one mobile group, two unequal groups, and a simple MM-environment-dependent energy.

**Not part of this gate:** These are analytic tests, not a molecular RBFE result or an electrostatic-embedding implementation.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M02: outcome and dependencies](../milestones/M02-transfer-kernel.md) | See how this gate fits into the larger result. |
| [S03: Proposed signatures](../specs/S03-data-and-interface-contracts.md#proposed-signatures) | Use the same function inputs and outputs as later gates. |
| [S04: Early environment-dependent contract probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe) | Check forces on MM atoms and reevaluation after a coordinate change. |
| [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy) | Distinguish raw child energies, outside terms, and the sampled energy. |
| [S06: Starting numerical thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds) | Use the stated precision checks and force-error limits. |
| [This gate's log folder](../../../Worker_Log/Milestone_02/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G00](../gates/G00-environment-and-provenance.md), [G01](../gates/G01-identity-partition-and-contracts.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G01 records/maps; G00 checked Reference/CPU API; explicit analytic fixtures with hand-written expected transformed coordinates.

**Outputs used by later gates:** Analytic PhysicalBundle factory; `resolve_protocol`, `build_atm`, `evaluate_physical`, `evaluate_atm`; independent endpoint and derivative checks.

**Planned source/test paths:** `atm.py`, `geometry.py`, `protocols/abfe.py`, `protocols/rbfe.py`, `endpoints.py`, `derivatives.py`, `fixtures/analytic/`, `tests/contracts/`, `tests/integration/test_pythonforce_atm.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G02-T1` | Construct a genuinely independent oracle | `P0-TEST-G02-01`, `P0-TEST-G02-02`, `P0-TEST-G02-03` |
| `G02-T2` | Run the same contracts on both protocol shapes | `P0-TEST-G02-04` |
| `G02-T3` | Challenge the ML-only-force assumption | `P0-TEST-G02-05`, `P0-TEST-G02-06`, `P0-TEST-G02-07` |

### G02-T1: construct a genuinely independent expected answer

Use an importable analytic Python callback with known negative energy derivatives. Begin with harmonic per-particle terms and a coupling term. Check selected-particle order, energy units, force units, and translation vectors independently of the tested mapping helper. The callback must survive fresh-process serialization; a notebook-local lambda is not sufficient.

Construct the native linear ATM expression for lambda 0, 0.37, and 1. Independently evaluate each physical coordinate state in a separate context. Explicitly identify raw child energies versus the expression energy. Add a nonzero outside harmonic term to expose scope errors. Use S06's analytic tolerances and a finite-difference step sweep.

**Finish this part with:** the relevant test results above and a worker log that states `G02-T1` as its scope. Completing this part alone does not complete G02.

### G02-T2: run the same contracts on both protocol shapes

Introduce both protocol resolvers now. A one-group fixture and a two-group fixture use the same physical bundle, assembler, energy records, and checker. In the second fixture the ligand groups have unequal lengths and noncontiguous original IDs. Both produce full final-particle maps rather than a model-specific ligand slice.

This does not run a molecular RBFE calculation. It catches shared-interface assumptions early enough that G12 should be additional qualification rather than a rewrite.

**Finish this part with:** the relevant test results above and a worker log that states `G02-T2` as its scope. Completing this part alone does not complete G02.

### G02-T3: challenge the ML-only-force assumption

Use the S04 analytic environment coupling. Check nonzero equal-and-opposite real ML/MM forces, environmental motion, transformed ligand motion, and A-B-A evaluation order. Do not precompute an environment descriptor at the original geometry and pass it unchanged to both endpoints.

Run deliberately introduced mistakes after the correct implementation passes. A test suite that remains green when environment forces or an entire physical child force are removed is not a useful oracle. Save the smallest complete reproducer and rerun after fresh-process reload.

**Finish this part with:** the relevant test results above and a worker log that states `G02-T3` as its scope. Completing this part alone does not complete G02.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G02-01 | `tests/integration/test_pythonforce_atm.py::test_linear_endpoint_and_force_identity` | At lambda 0, 0.37 and 1, raw child energies match hand-transformed direct evaluations and forces match their analytic weighted sum. | P0-REQ-013 |
| P0-TEST-G02-02 | `tests/integration/test_pythonforce_atm.py::test_permuted_subset_and_units` | A selected-particle order [2, 0] gives the correct energy/force scatter; a factor-of-ten force error fails. | P0-REQ-002, P0-REQ-010, P0-REQ-030 |
| P0-TEST-G02-03 | `tests/integration/test_pythonforce_atm.py::test_nonzero_outside_term_and_tuple_order` | Unpack u1,u0,energy explicitly; a nonzero outside restraint appears once in total energy and not in raw child energy. | P0-REQ-011, P0-REQ-013 |
| P0-TEST-G02-04 | `tests/contracts/test_transfer_protocols.py::test_one_and_two_unequal_mobile_groups` | The same assembler accepts ABFE and RBFE with unequal group sizes and noncontiguous IDs; only specified groups move. | P0-REQ-022 |
| P0-TEST-G02-05 | `tests/contracts/test_physical_evaluator.py::test_environment_force_and_recomputed_mapping` | For the S04 harmonic coupling, moving only the MM atom changes energy; ATM translation changes its force; all real derivatives match. | P0-REQ-006, P0-REQ-007 |
| P0-TEST-G02-06 | `tests/contracts/test_physical_evaluator.py::test_evaluation_history_independence` | Evaluate geometry A, then B, then A; the final A result matches the first and does not reuse stale mapped descriptors. | P0-REQ-007 |
| P0-TEST-G02-07 | `tests/contracts/test_fault_injection.py::test_known_transfer_errors_are_detected` | Deliberate wrong-index, omitted force, reversed raw tuple and stale-environment injections fail the appropriate checks. | P0-REQ-030 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_pythonforce_atm.py tests/contracts/test_transfer_protocols.py tests/contracts/test_physical_evaluator.py tests/contracts/test_fault_injection.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Any direct/ATM mismatch stops neural-model integration. Reproduce it with the analytic fixture and isolate mapping, selection, ownership, units, or OpenMM composition before modifying chemistry.

## Keep future changes possible

When accepted, this gate provides the first positive evidence that the interfaces accommodate two ligand groups and environment-dependent forces. It is explicitly not evidence that a real electrostatic embedding has been implemented.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_02/`\
**Task stem:** `Gate_02`\
**Worker:** `Gate_02_vN_worker.md`\
**Matching audit:** `Gate_02_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
