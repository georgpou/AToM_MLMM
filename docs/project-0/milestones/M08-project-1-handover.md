# M08: Qualified release and Project 1 handover

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Issue an evidence-backed release decision and a bounded Project-1 handover.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M07](../milestones/M07-rbfe-demonstration.md)

**Log folder:** [Worker_Log/Milestone_08](../../../Worker_Log/Milestone_08/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G13](../gates/G13-performance-and-release.md) | Measure cost and decide what the release actually supports | `Gate_13_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Review a clean offline reproduction and the complete applicable regression suite. Ensure accepted claims reference exact model/embedding/protocol/platform/precision/ensemble profiles. Skipped hardware and unrun long sampling stay visibly unqualified.

Review startup versus steady-state performance, model/worker memory, actual throughput units and any optimization-equivalence evidence. Record independent colleague review only when performed.

Decide whether the framework is qualified for named Project-1 trials, only a narrower configuration, or not yet qualified. Preserve the smallest fixtures, exact manifests, analysis/sign/correction documentation and limitations in the release.

## Acceptance condition

G13 accepted and a release review explicitly states supported, unqualified and deferred combinations. Both ABFE and RBFE claims have their own molecular evidence.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_08_vN_worker.md` and `Milestone_08_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** Project 1 compares ordinary noncovalent systems and may investigate targeted fine-tuning. Later model/embedding changes start from the same contracts but require newly scoped evidence.
