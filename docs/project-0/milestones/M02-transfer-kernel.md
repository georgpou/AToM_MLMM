# M02: Embedding-independent transfer kernel

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Demonstrate that the transfer kernel handles one or two mobile groups and full environment-dependent forces without model-specific logic.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M01](../milestones/M01-reproducible-foundation.md)

**Log folder:** [Worker_Log/Milestone_02](../../../Worker_Log/Milestone_02/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G02](../gates/G02-analytic-force-in-native-atm.md) | Check ATM using energies and forces with known answers | `Gate_02_vN_worker.md` / `_audit.md` |
| [G03](../gates/G03-atom-routing-and-integration.md) | Make sure AToM evaluates and integrates every intended force | `Gate_03_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Review direct/native/AToM comparisons with a nonzero outside restraint. Confirm the raw endpoint tuple order, all-real-force output, subset remapping and active integration masks. Check that the test suite fails when a physical force is omitted or counted twice.

Inspect the unequal two-ligand fixture and the analytic environment-coupled fixture. The same assembler must handle them without added embedding branches. Moving only an MM environment atom and reevaluating A-B-A must produce the expected result, catching stale descriptors and missing environment derivatives.

These are analytic transfer-kernel claims. They do not qualify a pretrained model, protein cap, physical electrostatic embedding or molecular RBFE.

## Acceptance condition

G02 and G03 accepted on admitted analytic profiles, including deliberately introduced mistakes and both protocol shapes. An agent can identify each physical/outside contribution and each module boundary.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_02_vN_worker.md` and `Milestone_02_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** M03 mechanical hybrid work and M04 analytic thermodynamic work may proceed in parallel. They converge before any solvated binding interpretation.
