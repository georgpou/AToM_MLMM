# M05: Reproducible solvated workflow

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Demonstrate one complete explicit-solvent preparation, run, restart and exchange workflow with preserved Hamiltonian and data meaning.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M03](../milestones/M03-mechanical-hybrid.md), [M04](../milestones/M04-thermodynamic-accounting.md)

**Log folder:** [Worker_Log/Milestone_05](../../../Worker_Log/Milestone_05/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G09](../gates/G09-solvent-preparation-and-export.md) | Add solvent and hand the prepared system to a worker | `Gate_09_vN_worker.md` / `_audit.md` |
| [G10](../gates/G10-restart-and-replica-exchange.md) | Check restart, process boundaries, and replica exchange | `Gate_10_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Inspect the actual worker export and reload at fixed coordinates before dynamics: atom map, constraints, box, active forces, parameters, energy and full real forces must agree. Review both mapped geometries, not only the statistically favorable one.

Recreate the bundle in a fresh offline process with the original cache unavailable. Distinguish checkpoint continuation from portable-State guarantees. Review two-state exchange energies independently and verify thermodynamic-state versus walker histories after restart.

Check worker device placement where GPU evidence is claimed. Multiple GPUs are separately qualified. A short multiwindow pilot demonstrates execution and record integrity, not converged affinity.

## Acceptance condition

G09 and G10 accepted for the declared solvated runtime profile with explicit raw records, no hidden asset dependency, and valid exchange/restart behavior.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_05_vN_worker.md` and `Milestone_05_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** M06 may introduce a real protein. The small solvated bundle remains a complete regression fixture and a worker-debugging reproducer.
