# Current status

M02 is **changes_requested** on `m02-analytic-atm`. The [independent G02 audit](../../Worker_Log/Milestone_02/Gate_02_v1_audit.md) and [G03/combined M02 audit](../../Worker_Log/Milestone_02/Gate_03_v1_audit.md) reviewed `a13019390f9770a42a5711bbb98025bd571ea40b`, carrying tested code `4c952dba5563572cf9e39527e64fe28ee201c385`. They independently passed **164** full-suite tests, **163 with 1 deselected** in the analytic selection, **78 G02**, **38 G03**, all **9 strict environment checks** and **1 upstream regression**. However, **13 required admission rejections failed**: M02-R1 actual-expression/schedule mismatch, M02-R2 fixed physical globals and child/schedule name collisions, and M02-R3 renamed duplicate-force admission. Passing numerical controls do not accept these scientific-contract gaps. [Independent evidence and reproducers](../../Worker_Log/Milestone_02/evidence/M02_v1_independent/README.md) record the findings and closure checks.

The user paused the original implementer and requested a **fresh-agent handoff before any new regression execution or repair**. [Continuation handoff](handoffs/M02-fresh-agent-continuation.md) records completed work, exact identities, concerns and next steps; its regression draft is unexecuted and outside the test tree. No repair has been applied, no new acceptance record created, and all 126 source/test/fixture/environment hashes still match the tested code. Continue from this branch with a fresh assessment, preserve v1 submissions, then use new repair/independent-closure attempts. Main and the fetched predecessor remain unchanged: the child and parent began at matching `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.

[G02 worker](../../Worker_Log/Milestone_02/Gate_02_v1_worker.md), [G03/combined worker](../../Worker_Log/Milestone_02/Gate_03_v1_worker.md), [numerical evidence](../../Worker_Log/Milestone_02/evidence/M02_v1/numerical-results.json), [raw validation](../../Worker_Log/Milestone_02/evidence/M02_v1/validation.json.gz) and [exact environment identity](../../Worker_Log/Milestone_02/evidence/M02_v1/environment-manifest.json.gz) retain the implementation/baseline submission. The fresh repaired baseline passed 47 tests. Qualification remains seven-real-atom analytic Reference/CPU only, subject to the open audit findings.

M01's analytic CPU implementation is independently accepted for `core-analytic-cpu` on `m00-audit-m01-development`. The [combined v2 audit](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md) reviewed snapshot `04944c67fc04c1667723f5292a07f8401cb94184`, carrying tested code `141c7fbcf2c5407e7880512d5481639bdc81bf57`. [G00 worker](../../Worker_Log/Milestone_01/Gate_00_v1_worker.md) records exact CPU APIs/provenance; [G01/M01 repair worker](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) records identities, fixed partitions, immutable versioned records, capability rejection, MM inventory and evidence validation. The full available suite passed 47 tests; the analytic selection passed 46 with one model test deselected. Strict environment validation passed all nine checks. [Repair validation evidence](../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz) and [complete environment identity](../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) identify the tested profile. The saved [original-MM inventory](../../Worker_Log/Milestone_01/evidence/M01_v2/original-mm-inventory.json) and [acceptance record](../../Worker_Log/Milestone_01/evidence/M01_v2/acceptance.json) carry the scoped handoff. These results do not accept a molecular gate.

The [independent M00 audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) accepts scientific contract version 1 for G00-T1/G01-T1/T2/T3 on `core-analytic-cpu`. Full M00 physical-reference closure remains open: exact G05/G07 references, quantum method/settings and profile limits need a separate reviewed decision before comparison results are inspected. The prior [repository preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) remains setup/example provenance.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

Use the [fresh-agent continuation](handoffs/M02-fresh-agent-continuation.md) to reassess and repair **M02-R1/R2/R3**, run meaningful failing/passing regressions and applicable/full checks, then obtain independent **G02/G03/M02** closure on the repaired snapshot. After acceptance, G04 physical boundary work and G08 analysis can start separately under their prerequisites. Keep G00 model/GPU profiles pending until needed, and resolve M00 physical-reference choices before any G05/G07 reference comparison. The [original M02 handoff](handoffs/M02-implementation-and-audit.md) retains branch/provenance instructions.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 / analytic CPU design | accepted_for_scope | [Independent version 1 design review](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) |
| M00 / physical-reference closure | blocked | Predeclare/review exact G05/G07 reference inputs, method, metrics and limits |
| M01 / G00-T1, G01-T1/T2/T3 | accepted_for_scope | [Independent combined v2 review](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md); 47-test result on the recorded CPU profile |
| M02 / G02-T1/T2/T3, G03-T1/T2/T3 | changes_requested | Fresh-agent repair of M02-R1/R2/R3 and independent combined closure; no repairs/new regressions run yet |
| M03-M08 / G04-G13 | not_started | Follow [roadmap](../../README.md#roadmap) and gate prerequisites |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model chemical/protein qualification | not_run | G00/G05/G07 evidence and predeclared physical-reference limits |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
