# Current work status

This package records a documentation revision, not an implemented molecular platform. No numerical gate or M00 design review has been accepted here. Existing work in an uninspected live repository must be assessed from that checkout and its evidence, not assumed absent or complete.

**Documentation work:** [Documentation attempt 1](../../Worker_Log/Milestone_00/Documentation_v1_worker.md), ready for an independent audit. This does not count as M00 approval. The code/test plans remain unexecuted.

## Gate and milestone summary

The table and [plan-index.json](plan-index.json) must agree. Task pages link here instead of keeping their own stale status labels. Actual worker/audit logs and snapshots support a status; changing the label alone does not establish acceptance.

| ID | Work status | Evidence | Next condition |
|---|---|---|---|
| [M00](milestones/M00-architecture-review.md) | not_started | none | Design review required |
| [M01](milestones/M01-reproducible-foundation.md) | not_started | none | Required gate evidence and combined review |
| [M02](milestones/M02-transfer-kernel.md) | not_started | none | Required gate evidence and combined review |
| [M03](milestones/M03-mechanical-hybrid.md) | not_started | none | Required gate evidence and combined review |
| [M04](milestones/M04-thermodynamic-accounting.md) | not_started | none | Required gate evidence and combined review |
| [M05](milestones/M05-solvated-workflow.md) | not_started | none | Required gate evidence and combined review |
| [M06](milestones/M06-abfe-demonstration.md) | not_started | none | Required gate evidence and combined review |
| [M07](milestones/M07-rbfe-demonstration.md) | not_started | none | Required gate evidence and combined review |
| [M08](milestones/M08-project-1-handover.md) | not_started | none | Required gate evidence and combined review |
| [G00](gates/G00-environment-and-provenance.md) | not_started | not_run | Assigned work under M01 |
| [G01](gates/G01-identity-partition-and-contracts.md) | not_started | not_run | Assigned work under M01 |
| [G02](gates/G02-analytic-force-in-native-atm.md) | not_started | not_run | Assigned work under M02 |
| [G03](gates/G03-atom-routing-and-integration.md) | not_started | not_run | Assigned work under M02 |
| [G04](gates/G04-link-boundary-and-derivatives.md) | not_started | not_run | Assigned work under M03 |
| [G05](gates/G05-local-model-adapter.md) | not_started | not_run | Assigned work under M03 |
| [G06](gates/G06-periodicity-and-interaction-ledger.md) | not_started | not_run | Assigned work under M03 |
| [G07](gates/G07-joint-cavity-ligand-atm.md) | not_started | not_run | Assigned work under M03 |
| [G08](gates/G08-thermodynamics-and-estimators.md) | not_started | not_run | Assigned work under M04 |
| [G09](gates/G09-solvent-preparation-and-export.md) | not_started | not_run | Assigned work under M05 |
| [G10](gates/G10-restart-and-replica-exchange.md) | not_started | not_run | Assigned work under M05 |
| [G11](gates/G11-protein-abfe.md) | not_started | not_run | Assigned work under M06 |
| [G12](gates/G12-dual-ligand-rbfe.md) | not_started | not_run | Assigned work under M07 |
| [G13](gates/G13-performance-and-release.md) | not_started | not_run | Assigned work under M08 |

## What the labels mean

| Gate or milestone status | Meaning |
|---|---|
| `not_started` | No work has been recorded for the claimed scope |
| `in_progress` | Some work exists, but required work remains |
| `ready_for_review` | The whole claimed scope is submitted with evidence |
| `changes_requested` | An audit found required corrections for that scope |
| `blocked` | A required resource, result, or decision is missing |
| `accepted` | An identified reviewer accepted the full stated scope and setup |
| `invalidated` | A later relevant change means earlier acceptance no longer applies |

Worker attempts separately use `ready_for_audit`, `partial`, or `blocked`. Audit files use `accepted_for_scope`, `changes_required`, or `blocked`. An accepted `G01-T1` can leave G01 `in_progress` because other parts remain. Do not promote a whole gate after one small accepted repair.

## Record a new attempt without losing earlier work

The index provides `log_directory`, `log_stem`, `tasks`, and optional `latest_worker_log` / `latest_audit_log` pointers for each gate or milestone. Paths to logs are relative to the repository root; task-document paths are relative to `docs/project-0/`. Use null when there is no log, not an invented filename.

Use `execution_records` for small completed or partial assignments once they exist. Each entry should identify task ID, smaller scope, attempt, profile, worker-log path, audit-log path if any, snapshot identity, and audit decision. It records history; it does not automatically accept a gate. Do not insert a fabricated example entry. `acceptance_records` remains empty until actual whole-gate or milestone acceptance exists.

When a summary changes, update this table and the index in the same change and cite the actual log/evidence. Keep separate records when one model/hardware setup passes and another is blocked. The latest pointer is a convenience; unresolved older findings still matter.

## First implementation work

Complete the relevant M00 design review, then G00 environment checks and G01's small tasks. Start with the analytic CPU setup when model weights or a GPU are unavailable. The missing resources remain prerequisites for their later claims; they are not silently waived.
