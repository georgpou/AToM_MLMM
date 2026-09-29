# M04: Thermodynamic and statistical accounting

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Establish that the state definitions and estimator report the intended free-energy quantity, not merely plausible numbers.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M02](../milestones/M02-transfer-kernel.md)

**Log folder:** [Worker_Log/Milestone_04](../../../Worker_Log/Milestone_04/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G08](../gates/G08-thermodynamics-and-estimators.md) | Check the free-energy calculation against a known answer | `Gate_08_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Review the +1.5 kJ/mol harmonic answer, reversed sign and zero-restraint limit using independent quadrature and independent samples. Inspect the actual reduced-potential reconstruction against context evaluations.

Examine a deliberately nonidentical directional midpoint and its bridge correction. Inspect finite-wall translation volume, orientation/release obligations and the rejection of an undefined standard binding result. A missing correction must not be treated as zero.

Compare independent estimators on the same mathematical state set and review correlation, covariance, effective support and uncertainty handling. A thermostat trajectory and a final printed error bar are not enough evidence.

## Acceptance condition

G08 accepted with deterministic formula checks, known-answer sampling evidence, explicit correction status and independent analysis agreement.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_04_vN_worker.md` and `Milestone_04_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** M05 requires both M03 and M04. The common analysis consumes state energies and protocol meaning; it remains independent of embedding labels.
