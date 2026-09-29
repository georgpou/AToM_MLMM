# M00: Shared architecture and contract review

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Review the scientific scope and the interfaces that later gates must preserve before implementing a mechanical-only or one-ligand-specific design.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** None; this is the initial design review.

**Log folder:** [Worker_Log/Milestone_00](../../../Worker_Log/Milestone_00/README.md).

## Design sections to review

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| Design review | Review the shared specifications, in small sections if needed. | `Milestone_00_vN_worker.md` / `_audit.md` |

## First reading route for the design review

Read [S01](../specs/S01-scope-and-invariants.md) for scope, [S02](../specs/S02-architecture-and-dependencies.md) for responsibilities, [S03](../specs/S03-data-and-interface-contracts.md) for shared records, [S04](../specs/S04-embedding-and-model-contracts.md) for energy and link rules, [S05](../specs/S05-protocol-and-thermodynamic-contracts.md) for thermodynamics, [S06](../specs/S06-validation-and-tolerances.md) for checks, and [S07](../specs/S07-artifacts-and-qualification.md) for evidence. These can be split into explicit review assignments.

## Combined review: what to check and why

Read S01-S05 together. Confirm that the physical builder owns all embedding physics, the transfer protocol owns geometry and result meaning, and the ATM assembler consumes both without model or ligand-count branches. Confirm full-real-atom force coverage, fixed membership, explicit units, and schema/version rules.

Walk through two future changes on paper. First, replace the local mechanical provider with an environment-dependent energy that exerts forces on MM atoms. Second, replace a one-ligand transfer with two unequal mobile groups. Identify the exact modules that change and those that must not change. The early analytic tests in G01-G03 must expose an implementation that violates these boundaries.

Review requirement ownership, proposed tolerances, candidate dependencies and the cap/periodic/thermodynamic definitions. Do not approve an actual electrostatic Hamiltonian by implication; only its extension boundary is being designed here. Identify scientific questions as explicit decisions rather than leaving agents to guess during coding.

## Acceptance condition

An identified reviewer records the scope, reviewed spec revisions, accepted/amended decisions and requirement ownership. No unresolved conflict in a public force/map/unit/correction contract remains. This is a design acceptance, not a numerical pass.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_00_vN_worker.md` and `Milestone_00_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** Authorize G00-G01 as small assigned tasks. The specification remains versioned and amendable; approval does not authorize silently skipping later gates.
