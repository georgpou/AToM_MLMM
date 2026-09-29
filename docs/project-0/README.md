# Project 0: roadmap and task map

**Documentation edition:** 2. **Implementation evidence:** see [STATUS.md](STATUS.md). The edition number describes the documents, not a working software release.

## What we are trying to build

Build a correct, reusable ML/MM energy model containing a whole ligand, selected protein atoms, and hydrogen link atoms at protein boundaries. Use that same physical model inside ATM for both ABFE and RBFE. First establish correct energies, forces, state definitions, and workflow behavior; later test useful accuracy on ordinary binders.

Mechanical embedding is the first physical implementation. Keep it separate from the transfer protocol so a future embedding does not require separate ABFE and RBFE engines. Early small tests check two mobile ligands and forces on environment atoms, without claiming electrostatic embedding has been implemented.

## Choose one task

Read [AGENTS.md](../../AGENTS.md), then the assigned gate's **Read for this task** section. Check its prerequisites and earlier logs. Default to one named task or repair per session. [Assignment examples](guides/assigning-work.md) show worker, audit, and repair prompts.

| Milestone | Expected larger result | Gates | Worker/audit folder |
|---|---|---|---|
| [M00](milestones/M00-architecture-review.md) | Shared architecture and contract review | Design review | [Milestone_00](../../Worker_Log/Milestone_00/README.md) |
| [M01](milestones/M01-reproducible-foundation.md) | Reproducible inputs and versioned contracts | [G00](gates/G00-environment-and-provenance.md), [G01](gates/G01-identity-partition-and-contracts.md) | [Milestone_01](../../Worker_Log/Milestone_01/README.md) |
| [M02](milestones/M02-transfer-kernel.md) | Embedding-independent transfer kernel | [G02](gates/G02-analytic-force-in-native-atm.md), [G03](gates/G03-atom-routing-and-integration.md) | [Milestone_02](../../Worker_Log/Milestone_02/README.md) |
| [M03](milestones/M03-mechanical-hybrid.md) | Capped mechanical ML/MM qualification | [G04](gates/G04-link-boundary-and-derivatives.md), [G05](gates/G05-local-model-adapter.md), [G06](gates/G06-periodicity-and-interaction-ledger.md), [G07](gates/G07-joint-cavity-ligand-atm.md) | [Milestone_03](../../Worker_Log/Milestone_03/README.md) |
| [M04](milestones/M04-thermodynamic-accounting.md) | Thermodynamic and statistical accounting | [G08](gates/G08-thermodynamics-and-estimators.md) | [Milestone_04](../../Worker_Log/Milestone_04/README.md) |
| [M05](milestones/M05-solvated-workflow.md) | Reproducible solvated workflow | [G09](gates/G09-solvent-preparation-and-export.md), [G10](gates/G10-restart-and-replica-exchange.md) | [Milestone_05](../../Worker_Log/Milestone_05/README.md) |
| [M06](milestones/M06-abfe-demonstration.md) | First protein ABFE demonstration | [G11](gates/G11-protein-abfe.md) | [Milestone_06](../../Worker_Log/Milestone_06/README.md) |
| [M07](milestones/M07-rbfe-demonstration.md) | First protein RBFE demonstration | [G12](gates/G12-dual-ligand-rbfe.md) | [Milestone_07](../../Worker_Log/Milestone_07/README.md) |
| [M08](milestones/M08-project-1-handover.md) | Qualified release and Project 1 handover | [G13](gates/G13-performance-and-release.md) | [Milestone_08](../../Worker_Log/Milestone_08/README.md) |

M03 and M04 can progress separately once their actual gate dependencies pass. Both are needed for M05. The [gate index](gates/README.md) lists direct implementation dependencies. A milestone review adds a combined check; it does not replace its gates or require a one-session implementation.

## Where to find the details

[Shared specifications](specs/README.md) define the scientific rules and shared inputs/outputs. [The requirement index](REQUIREMENTS.md) connects those rules to [planned tests](TEST_CATALOG.md). [The support matrix](QUALIFICATION_MATRIX.md) distinguishes small analytic checks from real-model, molecular, and GPU claims. [The source register](reference/sources.md) and [scientific notes](reference/scientific-notes.md) support focused review.

Use [Worker_Log](../../Worker_Log/README.md) for actual work and audit reports. Technical checklists and report templates live in `templates/`, not as alternative report locations. The [working guide](guides/spec-and-test-workflow.md) explains the specification-first, test-first cycle.

## What this package does not claim

The 14 gates, 9 milestones, 7 specifications, 32 requirements, and 82 planned acceptance tests describe work to do. They do not prove that the molecular platform is implemented. This edition adds task-sized handoffs and clearer reading routes without changing existing scientific gate IDs, test IDs, units, or formulas. One named inventory test was added to cover work G01 already required.

[Provenance](PROVENANCE.md) records the supplied baseline and this revision. [Documentation QA](DOCUMENTATION_QA.md) records document checks only. [Safe integration](guides/repository-integration.md) explains the complete package versus the patch from edition 1. The unchanged original note is historical reference, not the current implementation rulebook.
