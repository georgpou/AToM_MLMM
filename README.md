# AToM ML/MM

Project 0 builds a reusable ML/MM energy model containing complete ligands, selected protein atoms and hydrogen link atoms, then evaluates it through ATM for ABFE and RBFE. The first implementation uses mechanical embedding and uncomplicated neutral chemistry. Project 1 tests physical accuracy after numerical and thermodynamic correctness is established.

**Current state:** planning and documentation only in this supplied snapshot. No numerical gate or M00 design review is accepted. [Status and qualification](docs/project-0/STATUS.md) records actual evidence; files named under future `src/` and `tests/` paths are not implemented merely because the plan names them.

## Start with the assigned task

An implementation worker reads [AGENTS.md](AGENTS.md), the named gate/task and its specific reading links, plus relevant prior findings. An auditor starts from the exact worker log and recorded snapshot. Do not read all documentation by default. [Environment setup](ATM_MLMM_Environment.md) is needed when installing or qualifying software, not for every editing task.

Example assignment: "Implement **G01-T1** in its gate page. Do not start T2/T3. Read only its referenced specification sections and relevant previous findings. Leave the next `Gate_01_vN_worker.md` under `Worker_Log/Milestone_01/`." For review, name that worker log; for repair, name its matching audit and finding IDs.

## Roadmap

Milestones group outcomes; gates contain separately assignable tasks. The final gate carries each milestone's combined-review criteria, except the initial M00 design review. Log folders are created when first used; no placeholder README or empty report is required.

| Milestone | Outcome | Gates / closing review | Earlier milestone reviews | Log folder |
|---|---|---|---|---|
| [M00](docs/project-0/milestones/M00-architecture-review.md) | Shared architecture and contracts | Design review | None | `Worker_Log/Milestone_00/` |
| [M01](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | Reproducible inputs and contracts | [G00](docs/project-0/gates/G00-environment-and-provenance.md), [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md); [combined review](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | [M00](docs/project-0/milestones/M00-architecture-review.md) | `Worker_Log/Milestone_01/` |
| [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | Shared transfer kernel | [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md), [G03](docs/project-0/gates/G03-atom-routing-and-integration.md); [combined review](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | [M01](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | `Worker_Log/Milestone_02/` |
| [M03](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | Capped mechanical hybrid | [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md), [G05](docs/project-0/gates/G05-local-model-adapter.md), [G06](docs/project-0/gates/G06-periodicity-and-interaction-ledger.md), [G07](docs/project-0/gates/G07-joint-cavity-ligand-atm.md); [combined review](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | `Worker_Log/Milestone_03/` |
| [M04](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | Thermodynamic accounting | [G08](docs/project-0/gates/G08-thermodynamics-and-estimators.md); [combined review](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | `Worker_Log/Milestone_04/` |
| [M05](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | Solvated preparation and workflow | [G09](docs/project-0/gates/G09-solvent-preparation-and-export.md), [G10](docs/project-0/gates/G10-restart-and-replica-exchange.md); [combined review](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | [M03](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review), [M04](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | `Worker_Log/Milestone_05/` |
| [M06](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | Protein ABFE | [G11](docs/project-0/gates/G11-protein-abfe.md); [combined review](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | [M05](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | `Worker_Log/Milestone_06/` |
| [M07](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | Protein RBFE | [G12](docs/project-0/gates/G12-dual-ligand-rbfe.md); [combined review](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | [M06](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | `Worker_Log/Milestone_07/` |
| [M08](docs/project-0/gates/G13-performance-and-release.md#m08-combined-review) | Release and Project 1 handover | [G13](docs/project-0/gates/G13-performance-and-release.md); [combined review](docs/project-0/gates/G13-performance-and-release.md#m08-combined-review) | [M07](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | `Worker_Log/Milestone_08/` |

### Gate prerequisites

These direct dependencies govern implementation; milestone combined reviews do not add hidden prerequisites. M00 must review the relevant design. S07 limits each prerequisite to the features actually used: analytic CPU evidence does not qualify weights or GPUs, and G05 additionally needs the G00 model-asset/loading evidence.

| Gate | Direct earlier gates |
|---|---|
| [G00](docs/project-0/gates/G00-environment-and-provenance.md) | None; relevant M00 design review |
| [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md) | [G00](docs/project-0/gates/G00-environment-and-provenance.md) |
| [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md) | [G00](docs/project-0/gates/G00-environment-and-provenance.md), [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md) |
| [G03](docs/project-0/gates/G03-atom-routing-and-integration.md) | [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md), [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md) |
| [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md) | [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md), [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md) |
| [G05](docs/project-0/gates/G05-local-model-adapter.md) | [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md) |
| [G06](docs/project-0/gates/G06-periodicity-and-interaction-ledger.md) | [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md), [G05](docs/project-0/gates/G05-local-model-adapter.md) |
| [G07](docs/project-0/gates/G07-joint-cavity-ligand-atm.md) | [G03](docs/project-0/gates/G03-atom-routing-and-integration.md), [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md), [G05](docs/project-0/gates/G05-local-model-adapter.md), [G06](docs/project-0/gates/G06-periodicity-and-interaction-ledger.md) |
| [G08](docs/project-0/gates/G08-thermodynamics-and-estimators.md) | [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md), [G03](docs/project-0/gates/G03-atom-routing-and-integration.md) |
| [G09](docs/project-0/gates/G09-solvent-preparation-and-export.md) | [G07](docs/project-0/gates/G07-joint-cavity-ligand-atm.md), [G08](docs/project-0/gates/G08-thermodynamics-and-estimators.md) |
| [G10](docs/project-0/gates/G10-restart-and-replica-exchange.md) | [G09](docs/project-0/gates/G09-solvent-preparation-and-export.md) |
| [G11](docs/project-0/gates/G11-protein-abfe.md) | [G10](docs/project-0/gates/G10-restart-and-replica-exchange.md) |
| [G12](docs/project-0/gates/G12-dual-ligand-rbfe.md) | [G11](docs/project-0/gates/G11-protein-abfe.md) |
| [G13](docs/project-0/gates/G13-performance-and-release.md) | [G11](docs/project-0/gates/G11-protein-abfe.md), [G12](docs/project-0/gates/G12-dual-ligand-rbfe.md) |

M03 physical work and M04 analysis may advance separately after their actual prerequisites pass; both are required for M05's combined review.

## Reference map

Each type of information has one maintained home. Global procedure and logging live in AGENTS.md; task scope, implementation steps and planned assertions live in gates; progress and profile evidence live in STATUS.md.

| Shared specification | Read for |
|---|---|
| [S01](docs/project-0/specs/S01-scope-and-invariants.md) | Scope and permanent invariants |
| [S06](docs/project-0/specs/S06-validation-and-tolerances.md) | Independent checks, numerical tolerances and sampling |
| [S07](docs/project-0/specs/S07-artifacts-and-qualification.md) | Saved artifacts, qualification evidence and restart |
| [S04](docs/project-0/specs/S04-embedding-and-model-contracts.md) | Embedding, caps, periodic bookkeeping and model contracts |
| [S05](docs/project-0/specs/S05-protocol-and-thermodynamic-contracts.md) | Maps, signs, restraints and free-energy meaning |
| [S02](docs/project-0/specs/S02-architecture-and-dependencies.md) | Module ownership, dependencies and extension rationale |
| [S03](docs/project-0/specs/S03-data-and-interface-contracts.md) | Units, identity and shared input/output records |

Use the [requirement locator](docs/project-0/REQUIREMENTS.md), [source register](docs/project-0/reference/sources.md), and [glossary](docs/project-0/reference/glossary.md) only as needed. The [worker](docs/project-0/templates/worker-log.md) and [audit](docs/project-0/templates/audit-log.md) templates are the only routine handoff forms.

## Documentation checks

From the repository root, run `python tools/check_docs.py --self-test`. It checks local Markdown destinations/anchors and its own deliberate-error cases using the standard library. It does not fetch external websites, install the molecular stack or certify scientific results. Planned scientific tests remain in their owning gates.

## History

The [original brainstorming note](docs/project-0/reference/original-brainstorming-plan.md) and [later large plan](Original_planning_docs/Project_0_ATM_MLMM_Implementation_and_Validation_Plan_crude.md) are historical, not controlling instructions. The [unchanged prior worker report](Worker_Log/Milestone_00/Documentation_v1_worker.md) and its evidence remain at their original paths.

[Documentation cleanup attempt 2](Worker_Log/Milestone_00/Documentation_v2_worker.md) records this consolidation. Its [compressed pre-cleanup snapshot](Worker_Log/Milestone_00/evidence/Documentation_v2/snapshot_before_cleanup.zip) preserves all 84 original project files and the supplied cleanup audit, excluding Git/Finder metadata. Extract that archive elsewhere when reconstructing old evidence, not into the current checkout. Two tiny historical pointer pages remain solely to keep the prior report's links usable; they are not required agent reading. The old documentation checker is snapshot-specific and is not the current validation command.
