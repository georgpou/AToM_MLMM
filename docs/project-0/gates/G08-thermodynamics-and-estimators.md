# G08: Check the free-energy calculation against a known answer

**Part of:** [M04](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

Correct endpoint forces do not prove that signs, restraints, midpoint connections, or statistical analysis are correct. An exactly solvable case tests the complete thermodynamic accounting.

## Expected outcome

A known-answer free-energy test, checked restraint corrections, and agreement between independent analyses using the same states and data.

**Not part of this gate:** Do not call an uncorrected transfer result a standard binding free energy. Do not assume two directional midpoints are identical.

## Before starting

Required earlier gates: [G02](../gates/G02-analytic-force-in-native-atm.md), [G03](../gates/G03-atom-routing-and-integration.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G02-G03 analytic energies and state records; reviewed signs, correction obligations and exact expressions.

**Outputs used by later gates:** `ThermodynamicSpec`, correction validation, reduced-potential reconstruction, independent PyMBAR/UWHAM checks and `analyze`.

**Planned source/test paths:** `restraints.py`, `schedule.py`, `analysis.py`, `tests/unit/test_schedule.py`, `tests/unit/test_restraint_volume.py`, `tests/sampling/test_analytic_free_energy.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G08-T1` | Validate a nonzero thermodynamic answer without MD | `P0-TEST-G08-01`, `P0-TEST-G08-04` |
| `G08-T2` | Verify schedule and midpoint accounting | `P0-TEST-G08-02`, `P0-TEST-G08-03`, `P0-TEST-G08-05` |
| `G08-T3` | Compare estimators and then sampled dynamics | `P0-TEST-G08-01`, `P0-TEST-G08-06` |

### G08-T1: validate a nonzero thermodynamic answer without MD

**Read:** [S05: Known nonzero analytic answer](../specs/S05-protocol-and-thermodynamic-contracts.md#known-nonzero-analytic-answer); [S05: Standard translational volume](../specs/S05-protocol-and-thermodynamic-contracts.md#standard-translational-volume).

Use the harmonic physical/displaced energies and outside restraint from S05. Independently integrate the partition functions. Generate independent analytic samples so the estimator can be checked without conflating integrator sampling errors. Evaluate the full known lambda curve, zero-restraint limit, and reversed endpoint labels.

Implement explicit endpoint weights and correction obligations. Do not let an analysis routine infer 'ABFE' from a directory or choose a sign from an upstream variable name. A raw restrained result can be reported while a final binding quantity remains undefined.

### G08-T2: verify schedule and midpoint accounting

**Read:** [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy); [S05: Directional midpoints](../specs/S05-protocol-and-thermodynamic-contracts.md#directional-midpoints); [S05: Binding definition and correction completeness](../specs/S05-protocol-and-thermodynamic-contracts.md#binding-definition-and-correction-completeness).

Reconstruct all reduced energies from raw endpoint and outside terms, including direction, soft-core/softplus settings and offsets. Compare selected rows with actual contexts. Test an active directional mismatch rather than only an unmodified common midpoint. The bridge enters the bound-minus-bulk combination with the sign specified in S05.

Implement the finite-wall translation integral and test the zero-radius harmonic and hard-wall limits. Include orientation/pose/state-counting conditions explicitly. Similar restraint names or lambda values do not prove cancellation or identity.

### G08-T3: compare estimators and then sampled dynamics

**Read:** [S05: Shared analysis and molecular closure](../specs/S05-protocol-and-thermodynamic-contracts.md#shared-analysis-and-molecular-closure); [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility).

Run PyMBAR and the pinned AToM Python UWHAM path on mathematically compatible states. Account for differences in raw input naming and leg conventions. Only afterward use short MD-generated samples and assess correlation, overlap, effective contributions and repeated seeds.

Use S06's known-answer criteria, including both a standard-error criterion and absolute error bound. Enlarging an error bar is not a pass strategy. Keep midpoint/release uncertainty and covariance explicit in the result ledger.

This gate can be developed alongside G04-G07 once G02-G03 pass. It must be accepted before G09 is used to make any binding-free-energy claim.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G08-01 | `tests/sampling/test_analytic_free_energy.py::test_harmonic_known_difference` | The specified constants give F1-F0=+1.5 kJ/mol, reverse=-1.5; kr=0 gives zero; quadrature and analytic samples agree. | P0-REQ-016, P0-REQ-030 |
| P0-TEST-G08-02 | `tests/unit/test_schedule.py::test_reduced_energies_match_context` | For every declared state, reconstructed raw/softened/outside total equals direct context evaluation on saved frames. | P0-REQ-018 |
| P0-TEST-G08-03 | `tests/unit/test_schedule.py::test_active_midpoint_difference_requires_bridge` | A deliberately different directional midpoint is detected; including its independently evaluated bridge restores the known result. | P0-REQ-017 |
| P0-TEST-G08-04 | `tests/unit/test_restraint_volume.py::test_finite_wall_and_standard_state_sign` | Full finite-wall integral matches quadrature and limiting cases; standard-state sign follows the declared bound-minus-bulk convention. | P0-REQ-016 |
| P0-TEST-G08-05 | `tests/unit/test_restraint_volume.py::test_required_correction_cannot_default_to_zero` | Required uncomputed orientation/release/bridge entries prevent a final standard binding result; demonstrated zero needs evidence. | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G08-06 | `tests/sampling/test_analytic_free_energy.py::test_estimators_covariance_and_offsets` | Independent estimators agree on identical reduced states; constant energy shifts cancel; covariance and correlated samples are treated as specified. | P0-REQ-018, P0-REQ-019 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v
```

**Stop and diagnose:** An undefined state, incorrect sign, uncomputed required correction, disconnected estimator support or analytic mismatch blocks binding interpretation. Longer protein trajectories cannot repair these failures.

## Keep future changes possible

The estimator consumes reduced potentials and protocol-supplied observable definitions. It neither knows the model name nor needs separate mechanical/electrostatic implementations.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_04/`\
**Worker:** `Gate_08_vN_worker.md`; **audit:** `Gate_08_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M04 combined review

**Review scope:** G08. **Earlier milestone reviews:** M02. These are combined-review conditions, not additional implementation prerequisites.

Review the +1.5 kJ/mol harmonic answer, reversed sign and zero-restraint limit using independent quadrature and independent samples. Inspect the actual reduced-potential reconstruction against context evaluations.

Examine a deliberately nonidentical directional midpoint and its bridge correction. Inspect finite-wall translation volume, orientation/release obligations and the rejection of an undefined standard binding result. A missing correction must not be treated as zero.

Compare independent estimators on the same mathematical state set and review correlation, covariance, effective support and uncertainty handling. A thermostat trajectory and a final printed error bar are not enough evidence.

G08 accepted with deterministic formula checks, known-answer sampling evidence, explicit correction status and independent analysis agreement.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_04_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
