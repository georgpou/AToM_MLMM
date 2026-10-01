# Current status and qualification

This snapshot contains plans, documentation tooling and a reproducible CPU dependency setup, not an implemented molecular platform. No M00 design approval or numerical gate acceptance is claimed. The [independent reproduction v2 audit](../../Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md) reports **changes_required** for the clean baseline. Its fresh CPU installation and eight environment checks passed; required documentation-delivery and loading-policy findings remain open. Earlier Documentation v1-v4 submissions remain historical and have not been rewritten or retroactively approved.

## Independent setup and baseline audit

The audit branch is `m01-g00-environment-audit-v1`, created directly from setup tip `28f89cb23bdb7081c3723b9794fbde7d9bb50dca`. It audits submitted reproduction result `dcfd99d51e991f0cf6f838b81f2f14752b0a9afa` separately from later handout changes. [Raw evidence](../../Worker_Log/Documentation/evidence/Cloud_CPU_Reproduction_v2_audit/) records an empty-prefix installation, strict validation, exact inventories/artifacts/upstream identities, activation, replay and controlled failure propagation. These are development-environment results, not scientific G00 acceptance.

**Delivery:** the audit payload `ef6ed3ab432c443d5e1c8dad5b9211cbd9a7d925` and publication-note commit `c2b3269cda9085c462e1429e5e160237357c2702` are published on `origin/m01-g00-environment-audit-v1`. The user directly approved pushing this separate branch and prohibited changes to main. [Publication verification](../../Worker_Log/Documentation/evidence/Cloud_CPU_Reproduction_v2_audit/publication-success.json) confirms the remote audit commit and unchanged main/setup heads. The earlier [approval rejection record](../../Worker_Log/Documentation/evidence/Cloud_CPU_Reproduction_v2_audit/publication-block.json) remains historical; that delivery blocker is resolved and is not an environment or scientific-runtime error. The repair handout's remote-fetch commands can now inherit the published audit branch. Required findings A01-A03 remain open.

| Finding | Current disposition | Importance and next action |
|---|---|---|
| A01 - missing Documentation v4 amendment | open; blocks the intended scientific-document baseline | At the audited parent, eighteen documentation files match the historical before hashes; P0-REQ-033, G05-T4/G07-T4 and the 93-node catalog are absent. Recover the original delivery or record/review a new traceable amendment before proceeding against the claimed revised plan. |
| A02 - two source anchors and U40/U41 | open; low runtime impact, required documentation closure | No effect on CPU calculations. These are genuinely missing source records, not obsolete folder paths. Repair meaningful provenance once under A01; zero doc errors/eight self-tests are needed for clean-baseline closure. |
| A03 - MACECalculator unsafe-loading override | open; required helper repair | The calculator import resets the variable after the helper clears it. CPU smokes still pass and no weights were loaded. A scratch second cleanup passes the policy regression; production repair and independent review remain necessary. |
| A04 - OpenCL/optional acceleration warnings | closed as nonblocking for tested CPU scope | Replay keeps the same symlink and passes all CPU checks. Do not delete links, substitute packages, suppress stderr or reopen without relevant new evidence. GPU/OpenCL/serialization claims remain unqualified. |
| A05 - historical outer driver 1 / installer 0 | no reproduced current defect; historical cause unknown | Current real Cloud fallback succeeds with status 0; all five controlled artifact failures return 1 before installation. No speculative fix needed. Preserve the historical unknown; reopen only with a reproducible driver/status trace. |
| A06 - stale progress/task pointers | closed by audit reporting update | This status and root task-entry links now identify the actual audit and next repair assignment. No production or scientific repair is self-approved. |

The previously missing wheel delivery is independently confirmed resolved: all 51 wheels and three complete upstream archives match their locked identities. The standard Conda registry sandbox prerequisite was resolved with narrow access and a new absent prefix; no package/network installation blocker remains on the tested host. Both environment-only and strict runs retain docs exit 1; all eight checker self-tests pass. The complete clean baseline is **not accepted**.

**Next assignment:** [close A01-A03 on a child of the audit branch](../../NEXT_AGENT_REPAIR_HANDOUT.md), suggested `m01-g00-environment-repair-v3`. Preserve the closed CPU dispositions above. Obtain independent review of repairs, then complete relevant M00 review and applicable G00-T1/G01 tasks. Do not repeat the full audit without changed evidence or count setup smoke checks as numerical gates.

## Gate and milestone summary

This is the only live progress summary. Link each change to the exact snapshot, profile, worker/audit record and actual evidence. Gate pages define work, not separate status claims.

| ID | Work status | Evidence | Next condition |
|---|---|---|---|
| [M00](milestones/M00-architecture-review.md) | not_started | none | Design review required |
| [M01](gates/G01-identity-partition-and-contracts.md#m01-combined-review) | not_started | none | Required gates and combined review |
| [M02](gates/G03-atom-routing-and-integration.md#m02-combined-review) | not_started | none | Required gates and combined review |
| [M03](gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | not_started | none | Required gates and combined review |
| [M04](gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | not_started | none | Required gates and combined review |
| [M05](gates/G10-restart-and-replica-exchange.md#m05-combined-review) | not_started | none | Required gates and combined review |
| [M06](gates/G11-protein-abfe.md#m06-combined-review) | not_started | none | Required gates and combined review |
| [M07](gates/G12-dual-ligand-rbfe.md#m07-combined-review) | not_started | none | Required gates and combined review |
| [M08](gates/G13-performance-and-release.md#m08-combined-review) | not_started | none | Required gates and combined review |
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

Close the required baseline audit findings above, complete the relevant M00 design review, then perform G00 environment checks and G01 tasks. Start with the analytic CPU setup when weights or GPUs are unavailable; the missing evidence still blocks their later specific claims.
