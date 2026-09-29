# M06: First protein ABFE demonstration

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Apply the qualified framework to one ordinary protein ABFE example without changing its physical or thermodynamic definitions.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M05](../milestones/M05-solvated-workflow.md)

**Log folder:** [Worker_Log/Milestone_06](../../../Worker_Log/Milestone_06/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G11](../gates/G11-protein-abfe.md) | Run the first protein ABFE example | `Gate_11_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Review all selected side-chain cuts and the target input independently of the ML builder. Check at least one representative derivative component for every boundary-parent pair. Compare all-MM, ligand-only and cavity-inclusive controls with clear mass/constraint semantics.

Inspect the full thermodynamic result ledger and relevant sampling/overlap evidence. Review alternative bulk placement and justified box-size sensitivity as physical-model assessment, separate from sampling uncertainty. Confirm restart, exchange, graph and alternate-state domain checks remain valid at realistic system size.

## Acceptance condition

G11 accepted for one explicit target/model/embedding/protocol/runtime profile. The result states what is deterministic validation, pilot evidence, sampled estimation and remaining physical limitation.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_06_vN_worker.md` and `Milestone_06_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** M07 can qualify a molecular ligand pair using the already shared two-group contracts. Experimental superiority remains a Project-1 question.
