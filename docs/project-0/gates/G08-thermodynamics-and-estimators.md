# G08: Check the free-energy calculation against a known answer

**Part of:** [M04](../milestones/M04-thermodynamic-accounting.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

Correct endpoint forces do not prove that signs, restraints, midpoint connections, or statistical analysis are correct. An exactly solvable case tests the complete thermodynamic accounting.

## Expected outcome

A known-answer free-energy test, checked restraint corrections, and agreement between independent analyses using the same states and data.

**Not part of this gate:** Do not call an uncorrected transfer result a standard binding free energy. Do not assume two directional midpoints are identical.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M04: outcome and dependencies](../milestones/M04-thermodynamic-accounting.md) | See how this gate fits into the larger result. |
| [S05: Binding definition and correction completeness](../specs/S05-protocol-and-thermodynamic-contracts.md#binding-definition-and-correction-completeness) | Do not label a result ABFE or RBFE while required terms are unresolved. |
| [S05: Standard translational volume](../specs/S05-protocol-and-thermodynamic-contracts.md#standard-translational-volume) | Compute the restraint-volume correction with the stated sign. |
| [S05: Directional midpoints](../specs/S05-protocol-and-thermodynamic-contracts.md#directional-midpoints) | Check that the two legs are connected instead of assuming it. |
| [S05: Known nonzero analytic answer](../specs/S05-protocol-and-thermodynamic-contracts.md#known-nonzero-analytic-answer) | Test the estimator and sign against an independently known result. |
| [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility) | Separate sampling uncertainty, correlation, and physical sensitivity. |
| [This gate's log folder](../../../Worker_Log/Milestone_04/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G02](../gates/G02-analytic-force-in-native-atm.md), [G03](../gates/G03-atom-routing-and-integration.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G02-G03 analytic energies and state records; reviewed signs, correction obligations and exact expressions.

**Outputs used by later gates:** `ThermodynamicSpec`, correction validation, reduced-potential reconstruction, independent PyMBAR/UWHAM checks and `analyze`.

**Planned source/test paths:** `restraints.py`, `schedule.py`, `analysis.py`, `tests/unit/test_schedule.py`, `tests/unit/test_restraint_volume.py`, `tests/sampling/test_analytic_free_energy.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G08-T1` | Validate a nonzero thermodynamic answer without MD | `P0-TEST-G08-01`, `P0-TEST-G08-04` |
| `G08-T2` | Verify schedule and midpoint accounting | `P0-TEST-G08-02`, `P0-TEST-G08-03`, `P0-TEST-G08-05` |
| `G08-T3` | Compare estimators and then sampled dynamics | `P0-TEST-G08-01`, `P0-TEST-G08-06` |

### G08-T1: validate a nonzero thermodynamic answer without MD

Use the harmonic physical/displaced energies and outside restraint from S05. Independently integrate the partition functions. Generate independent analytic samples so the estimator can be checked without conflating integrator sampling errors. Evaluate the full known lambda curve, zero-restraint limit, and reversed endpoint labels.

Implement explicit endpoint weights and correction obligations. Do not let an analysis routine infer 'ABFE' from a directory or choose a sign from an upstream variable name. A raw restrained result can be reported while a final binding quantity remains undefined.

**Finish this part with:** the relevant test results above and a worker log that states `G08-T1` as its scope. Completing this part alone does not complete G08.

### G08-T2: verify schedule and midpoint accounting

Reconstruct all reduced energies from raw endpoint and outside terms, including direction, soft-core/softplus settings and offsets. Compare selected rows with actual contexts. Test an active directional mismatch rather than only an unmodified common midpoint. The bridge enters the bound-minus-bulk combination with the sign specified in S05.

Implement the finite-wall translation integral and test the zero-radius harmonic and hard-wall limits. Include orientation/pose/state-counting conditions explicitly. Similar restraint names or lambda values do not prove cancellation or identity.

**Finish this part with:** the relevant test results above and a worker log that states `G08-T2` as its scope. Completing this part alone does not complete G08.

### G08-T3: compare estimators and then sampled dynamics

Run PyMBAR and the pinned AToM Python UWHAM path on mathematically compatible states. Account for differences in raw input naming and leg conventions. Only afterward use short MD-generated samples and assess correlation, overlap, effective contributions and repeated seeds.

Use S06's known-answer criteria, including both a standard-error criterion and absolute error bound. Enlarging an error bar is not a pass strategy. Keep midpoint/release uncertainty and covariance explicit in the result ledger.

This gate can be developed alongside G04-G07 once G02-G03 pass. It must be accepted before G09 is used to make any binding-free-energy claim.

**Finish this part with:** the relevant test results above and a worker log that states `G08-T3` as its scope. Completing this part alone does not complete G08.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G08-01 | `tests/sampling/test_analytic_free_energy.py::test_harmonic_known_difference` | The specified constants give F1-F0=+1.5 kJ/mol, reverse=-1.5; kr=0 gives zero; quadrature and analytic samples agree. | P0-REQ-016, P0-REQ-030 |
| P0-TEST-G08-02 | `tests/unit/test_schedule.py::test_reduced_energies_match_context` | For every declared state, reconstructed raw/softened/outside total equals direct context evaluation on saved frames. | P0-REQ-018 |
| P0-TEST-G08-03 | `tests/unit/test_schedule.py::test_active_midpoint_difference_requires_bridge` | A deliberately different directional midpoint is detected; including its independently evaluated bridge restores the known result. | P0-REQ-017 |
| P0-TEST-G08-04 | `tests/unit/test_restraint_volume.py::test_finite_wall_and_standard_state_sign` | Full finite-wall integral matches quadrature and limiting cases; standard-state sign follows the declared bound-minus-bulk convention. | P0-REQ-016 |
| P0-TEST-G08-05 | `tests/unit/test_restraint_volume.py::test_required_correction_cannot_default_to_zero` | Required uncomputed orientation/release/bridge entries prevent a final standard binding result; demonstrated zero needs evidence. | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G08-06 | `tests/sampling/test_analytic_free_energy.py::test_estimators_covariance_and_offsets` | Independent estimators agree on identical reduced states; constant energy shifts cancel; covariance and correlated samples are treated as specified. | P0-REQ-018, P0-REQ-019 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** An undefined state, incorrect sign, uncomputed required correction, disconnected estimator support or analytic mismatch blocks binding interpretation. Longer protein trajectories cannot repair these failures.

## Keep future changes possible

The estimator consumes reduced potentials and protocol-supplied observable definitions. It neither knows the model name nor needs separate mechanical/electrostatic implementations.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_04/`\
**Task stem:** `Gate_08`\
**Worker:** `Gate_08_vN_worker.md`\
**Matching audit:** `Gate_08_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
