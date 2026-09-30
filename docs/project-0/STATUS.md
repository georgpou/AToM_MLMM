# Current status and qualification

This snapshot contains reviewed architecture, documentation tooling and CPU installation/provenance tooling; the molecular platform is not implemented. [M00 attempt 1](../../Worker_Log/Milestone_00/Milestone_00_v1_worker.md) has an [independent design audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md). No numerical gate acceptance is claimed. Historical documentation attempts remain immutable; their claims are not automatically evidence for this checkout.

## Gate and milestone summary

This is the only live progress summary. Link each change to the exact snapshot, profile, worker/audit record and actual evidence. Gate pages define work, not separate status claims.

| ID | Work status | Evidence | Next condition |
|---|---|---|---|
| [M00](milestones/M00-architecture-review.md) | accepted | [Full design audit, source snapshot 2d7bcc94](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) | Numerical/model/GPU work requires its own evidence |
| [M01](gates/G01-identity-partition-and-contracts.md#m01-combined-review) | in_progress | G00-T1 cloud setup underway | G00/G01 and combined review |
| [M02](gates/G03-atom-routing-and-integration.md#m02-combined-review) | not_started | none | Required gates and combined review |
| [M03](gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | not_started | none | Required gates and combined review |
| [M04](gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | not_started | none | Required gates and combined review |
| [M05](gates/G10-restart-and-replica-exchange.md#m05-combined-review) | not_started | none | Required gates and combined review |
| [M06](gates/G11-protein-abfe.md#m06-combined-review) | not_started | none | Required gates and combined review |
| [M07](gates/G12-dual-ligand-rbfe.md#m07-combined-review) | not_started | none | Required gates and combined review |
| [M08](gates/G13-performance-and-release.md#m08-combined-review) | not_started | none | Required gates and combined review |
| [G00](gates/G00-environment-and-provenance.md) | in_progress | G00-T1 implementation; cloud checks pending | CPU solve/check evidence and independent audit; model/GPU separate |
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

## Record evidence without duplicate bookkeeping

For each actual attempt, record the task/subscope, attempt number, profile, snapshot, worker-log path, audit-log path when it exists, decision and open findings. Link these records from the relevant summary row; do not create example passes or invented log pointers. Gate pages specify their folder/stem. Existing logs remain the history, not just the newest pointer.

An accepted small task can leave its gate in progress. Accepted parts must coexist on the reviewed snapshot with required combined regressions. Keep CPU/GPU, model and other distinct profiles separate. Changes that affect an accepted contract or profile invalidate the relevant evidence until checked again. The scientific evidence-record schemas in S03/S07 remain required; removing the documentation planning index does not remove those runtime records.

## Qualification profiles

A component saying it can support a feature is not proof that the complete setup works. A simple environment-dependent test is not a real electrostatic embedding. This initial matrix contains no numerical evidence from a live repository. Actual results belong in the worker/audit logs and [status](STATUS.md), with the tested setup stated explicitly.

| Physical provider | Protocol | Purpose | Current evidence in this package | Primary gates |
|---|---|---|---|---|
| Analytic local | ABFE one group | Coordinate, energy, units, ownership | Planned; not_run | G02-G03 |
| Analytic local | RBFE two unequal groups | No one-ligand assumptions in common code | Planned; not_run | G02-G03 |
| Analytic environment-coupled | ABFE one group | Full MM derivatives and mapped-environment reevaluation | Planned; not_run | G02, G04, G07 |
| Analytic environment-coupled | RBFE two groups | Protocol/provider independence | Planned; not_run | G02-G03, G07 |
| Local MACE + mechanical caps | Toy transfer | Native/adapter/link/PBC composition | Planned; not_run | G04-G07 |
| Local MACE + mechanical caps | Solvated workflow | Preparation, restart, exchange | Planned; not_run | G09-G10 |
| Local MACE + mechanical caps | Protein ABFE | Molecular absolute-binding profile | Planned; not_run | G11 |
| Local MACE + mechanical caps | Protein RBFE | Molecular relative-binding profile | Planned; not_run | G12 |
| Actual electrostatic embedding | ABFE or RBFE | Future new physical profile | Deferred; unsupported by this plan's numerical evidence | New extension gates required |
| Long-range/charge-aware new model | Either protocol | Future model/periodic bookkeeping | Deferred; unsupported by this plan's numerical evidence | New model/embedding qualification |
| Metals/reactive/adaptive regions | Either protocol | Future chemistry/method development | Out of initial scope | New scientific specification |

CPU/GPU, precision, timestep, model hash, environment lock, constraints, box convention and ensemble subdivide every relevant row. G13 admits only profiles with the required evidence. Completing one row cannot silently qualify its neighbor.

For each future admission, record: declared capabilities, applicable contracts, executed tests, fixture/source/model identities, physical limitations, skipped/unavailable checks, reviewer and evidence locations. A generic `supports_electrostatic: true` flag is not an admission mechanism.

The first admitted profile can be `core-analytic-cpu`, without actual neural weights. Mark real-model loader tests not applicable to that narrow claim; do not count them as passes. Upgrade the G00 asset/loader evidence before G05 and qualify the complete mechanical model combination in later gates. See S07 for applicability versus outcome.

## First implementation work

Complete the relevant M00 design review, then G00 environment checks and G01 tasks. Start with the analytic CPU setup when weights or GPUs are unavailable; the missing evidence still blocks their later specific claims.
