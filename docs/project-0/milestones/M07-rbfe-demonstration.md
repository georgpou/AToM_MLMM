# M07: First protein RBFE demonstration

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Complete the relative-binding capability using the same physical builder, transfer assembler, workflow and analysis records.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M06](../milestones/M06-abfe-demonstration.md)

**Log folder:** [Worker_Log/Milestone_07](../../../Worker_Log/Milestone_07/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G12](../gates/G12-dual-ligand-rbfe.md) | Run the first two-ligand RBFE example | `Gate_12_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Inspect opposite complete-ligand maps, cap identity, correct bound-component graphs and unintended ligand/image contacts. Re-run reload/exchange checks for the larger joint input.

Review symmetric A-to-A and nontrivial reversed-pair results with explicit sign and correction conventions. Compare against ABFE differences only after matching cavity/model/constraint/restraint and spectator-ligand definitions. A finite-box mismatch is not automatically a code defect, and apparent closure does not excuse an identity error.

## Acceptance condition

G12 accepted for the declared molecular RBFE profile with identity/reversal controls, matched-state closure interpretation and no separate RBFE physical engine.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_07_vN_worker.md` and `Milestone_07_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** M08 reviews reproducibility, performance and exact release claims. Real electrostatic ABFE/RBFE remains a future physical-profile extension.
