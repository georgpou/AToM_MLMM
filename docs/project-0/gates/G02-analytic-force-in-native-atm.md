# G02: Check ATM using energies and forces with known answers

**Part of:** [M02](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A simple spring-like energy has an answer we can calculate independently. It reveals mapping and force errors before a real model or a protein makes them difficult to isolate.

## Expected outcome

One shared ATM route that reproduces known energies and forces for one mobile group, two unequal groups, and a simple MM-environment-dependent energy.

**Not part of this gate:** These are analytic tests, not a molecular RBFE result or an electrostatic-embedding implementation.

## Before starting

Required earlier gates: [G00](../gates/G00-environment-and-provenance.md), [G01](../gates/G01-identity-partition-and-contracts.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G01 records/maps; G00 checked Reference/CPU API; explicit analytic fixtures with hand-written expected transformed coordinates.

**Outputs used by later gates:** Analytic PhysicalBundle factory; `resolve_protocol`, `build_atm`, `evaluate_physical`, `evaluate_atm`; independent endpoint and derivative checks.

**Planned source/test paths:** `atm.py`, `geometry.py`, `protocols/abfe.py`, `protocols/rbfe.py`, `endpoints.py`, `derivatives.py`, `fixtures/analytic/`, `tests/contracts/`, `tests/integration/test_pythonforce_atm.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G02-T1` | Construct a genuinely independent oracle | `P0-TEST-G02-01`, `P0-TEST-G02-02`, `P0-TEST-G02-03` |
| `G02-T2` | Run the same contracts on both protocol shapes | `P0-TEST-G02-04` |
| `G02-T3` | Challenge the ML-only-force assumption | `P0-TEST-G02-05`, `P0-TEST-G02-06`, `P0-TEST-G02-07` |

### G02-T1: construct a genuinely independent expected answer

**Read:** [S03: Proposed signatures](../specs/S03-data-and-interface-contracts.md#proposed-signatures); [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy).

Use an importable analytic Python callback with known negative energy derivatives. Begin with harmonic per-particle terms and a coupling term. Check selected-particle order, energy units, force units, and translation vectors independently of the tested mapping helper. The callback must survive fresh-process serialization; a notebook-local lambda is not sufficient.

Construct the native linear ATM expression for lambda 0, 0.37, and 1. Independently evaluate each physical coordinate state in a separate context. Explicitly identify raw child energies versus the expression energy. Add a nonzero outside harmonic term to expose scope errors. Use S06's analytic tolerances and a finite-difference step sweep.

### G02-T2: run the same contracts on both protocol shapes

**Read:** [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules); [S05: One protocol contract, two initial presets](../specs/S05-protocol-and-thermodynamic-contracts.md#one-protocol-contract-two-initial-presets).

Introduce both protocol resolvers now. A one-group fixture and a two-group fixture use the same physical bundle, assembler, energy records, and checker. In the second fixture the ligand groups have unequal lengths and noncontiguous original IDs. Both produce full final-particle maps rather than a model-specific ligand slice.

This does not run a molecular RBFE calculation. It catches shared-interface assumptions early enough that G12 should be additional qualification rather than a rewrite.

### G02-T3: challenge the ML-only-force assumption

**Read:** [S04: Early environment-dependent contract probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe); [numeric example](#numeric-environment-force-example).

Use the S04 analytic environment coupling. Check nonzero equal-and-opposite real ML/MM forces, environmental motion, transformed ligand motion, and A-B-A evaluation order. Do not precompute an environment descriptor at the original geometry and pass it unchanged to both endpoints.

Run deliberately introduced mistakes after the correct implementation passes. A test suite that remains green when environment forces or an entire physical child force are removed is not a useful oracle. Save the smallest complete reproducer and rerun after fresh-process reload.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

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

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_pythonforce_atm.py tests/contracts/test_transfer_protocols.py tests/contracts/test_physical_evaluator.py tests/contracts/test_fault_injection.py -v
```

**Stop and diagnose:** Any direct/ATM mismatch stops neural-model integration. Reproduce it with the analytic fixture and isolate mapping, selection, ownership, units, or OpenMM composition before modifying chemistry.

## Keep future changes possible

When accepted, this gate provides the first positive evidence that the interfaces accommodate two ligand groups and environment-dependent forces. It is explicitly not evidence that a real electrostatic embedding has been implemented.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_02/`\
**Worker:** `Gate_02_vN_worker.md`; **audit:** `Gate_02_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).

## Numeric environment-force example

G02 uses a deliberately simple energy, not an electrostatic model:

$$E=\tfrac12\kappa|\mathbf r_m-\mathbf r_e|^2.$$

Here `m` is a model atom, `e` is an MM environment atom, and kappa is a spring constant. With kappa=10 kJ/mol/nm squared, m at (0.2,0,0) nm and e at (0.5,0,0) nm, the energy is 0.45 kJ/mol and the x forces are +3 and -3 kJ/mol/nm. Moving m by +0.1 nm changes the energy to 0.20 and the forces to +2 and -2. Moving only e to 0.6 nm from the original geometry gives 0.80 and +4/-4.

These values provide an independent expected answer. A shared evaluator that returns only ML forces must fail. So must code that reuses the old distance after ATM moves the ligand. Test the same evaluator with one and two mobile groups. This protects the extension point without implementing electrostatic embedding now.

After the correct test passes, deliberately remove an environment force or reuse stale coordinates in an isolated test copy. The test must fail. This checks the test itself; never leave the deliberate mistake in production code.
