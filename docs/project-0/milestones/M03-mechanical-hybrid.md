# M03: Capped mechanical ML/MM qualification

**Progress:** [STATUS.md](../STATUS.md). This page defines a combined review, not an instruction to implement every gate in one session.

## Why and expected outcome

Qualify one explicitly defined capped mechanical ML/MM Hamiltonian through the shared transfer machinery.

A gate answers one testable question. This milestone checks that its gate results fit together and support the stated result. One good worker log does not by itself finish a milestone.

## Read for this task

Read [AGENTS.md](../../../AGENTS.md), this page, and the relevant gate pages below. For a combined review, read the accepted worker/audit records and only the specification sections needed to check them. For a gate assignment, follow that gate's own smaller reading list. [The documentation map](../../README.md) explains the rest of the folder.

**Earlier milestones required for this review:** [M02](../milestones/M02-transfer-kernel.md)

**Log folder:** [Worker_Log/Milestone_03](../../../Worker_Log/Milestone_03/README.md).

## Gates that make up this milestone

| Gate | Question | Log names in this milestone's folder |
|---|---|---|
| [G04](../gates/G04-link-boundary-and-derivatives.md) | Check one link atom and the forces on its real parents | `Gate_04_vN_worker.md` / `_audit.md` |
| [G05](../gates/G05-local-model-adapter.md) | Check one real ML model and its adapter | `Gate_05_vN_worker.md` / `_audit.md` |
| [G06](../gates/G06-periodicity-and-interaction-ledger.md) | Check periodic images and which classical interactions remain | `Gate_06_vN_worker.md` / `_audit.md` |
| [G07](../gates/G07-joint-cavity-ligand-atm.md) | Combine the capped fragment, ligand, model, and ATM | `Gate_07_vN_worker.md` / `_audit.md` |

## Combined review: what to check and why

Inspect the cap-parent Jacobian evidence and the complete retained/removed boundary ledger. Verify caps are derived sites with the intended classical treatment. An energy-only check is not sufficient.

Review native-model agreement, units/energy convention, local-component tests, counterfactual contact scans and offline identity. Inspect the exact retained PME convention, mask diagnostics and periodic geometry/seam tests; do not call all classical cavity-ligand electrostatics missing by definition.

Finally inspect the small capped-cavity/ligand fixture through direct, native ATM and AToM paths. Include MM-parent derivatives and the early extension-contract regressions. The combined fixture remains the reproducible reference for later protein failures.

## Acceptance condition

G04-G07 accepted for the declared local mechanical profile; no unexplained identity, derivative, interaction-ledger, image or counterfactual-domain failure remains.

Use the actual snapshots, test results, and previous audit decisions. M00 needs recorded design approval rather than simulation evidence. Every later milestone needs its required gate results and earlier milestone reviews. A reviewer must state the supported setup and any still-unavailable model or hardware evidence.

Do not require model or GPU tests for a claim that is explicitly limited to the analytic CPU setup. Do not use that narrower acceptance to claim model or GPU support. A technical dependency must be satisfied by evidence for the feature the next task uses.

## Small assignments and the handoff

The user can assign one gate, a task within it, or one part of this combined review. Record the scope and stop at that boundary. For a review of this milestone itself, use `Milestone_03_vN_worker.md` and `Milestone_03_vN_audit.md`. Gate work uses the gate filenames listed above, not milestone filenames.

Follow [the logging rules](../../../Worker_Log/README.md). The [milestone-review checklist](../templates/milestone-review.md) supplements the standard worker/audit templates; it is not a second report to maintain. A review split across sessions is accepted only after the combined requirements are covered.

**What follows:** Combine with M04 to begin M05 solvent/workflow qualification. This milestone alone does not imply a correct binding free-energy cycle.
