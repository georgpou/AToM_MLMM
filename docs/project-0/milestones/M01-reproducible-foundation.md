# M01: Reproducible inputs and versioned contracts

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Establish reproducible dependencies, immutable inputs and versioned records that both future protocols and embeddings can reuse.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M00](../milestones/M00-architecture-review.md)

**Log folder:** [Worker_Log/Milestone_01](../../../Worker_Log/Milestone_01/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G00](../gates/G00-environment-and-provenance.md) | Check the software and record exactly what is installed | `Gate_00_vN_worker.md` / `_audit.md` |
| [G01](../gates/G01-identity-partition-and-contracts.md) | Give every atom a reliable identity and define shared records | `Gate_01_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Review the G00 manifest rather than just import screenshots. Software identity includes source commit, package metadata, resolved builds and checkpoint digest. Missing GPU evidence stays missing. M01 may accept the core analytic CPU profile without neural weights; actual model loader/asset prerequisites must be admitted before G05. Confirm the trusted loader policy and allowed model use.

Inspect G01 identity fixtures with duplicate residue numbers, reordered indices, incomplete ligands and forbidden boundaries. Confirm shared records and protocol descriptions import without a model or GPU. Review schema round trips and capability rejection. An actual electrostatic request must not fall back silently to mechanical embedding.

## Acceptance condition

G00 and G01 are accepted for their declared profiles; stable IDs, units, schema and evidence contracts are demonstrable. Any deferred asset/hardware profile is explicitly blocked rather than marked qualified.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_01_vN_worker.md` and `Milestone_01_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** G02 can now implement both protocol shapes using analytic energy providers. Downstream tasks consume the reviewed records rather than inventing new incompatible dictionaries.
