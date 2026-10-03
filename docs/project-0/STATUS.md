# Current status

The child `m03-reference-g05` continues exact published G04 handoff
`bc788aeeedb4dc45026ac1bff44bd4fb533b325a`. G00-T2/G05-T1 loading checks and
16 independent real-model adapter/locality/domain/reload cases pass; current G05 work
remains **partial**, with chemical checks and complete independent
gate review pending. The [corrected exact M00 proposal](reference/M00-neutral-reference-plan-v3.md)
contains 34 hashed neutral structures, reference settings/limits and future
G07 controls plus ten monomer-grid rotation controls. Actual Astra/high v2
review required repair of one retained-peptide clash; the score-free v3
repair is independently accepted for design by actual fresh-context
gpt-6-astra/high on `a825f5f1c2d8cf4146133c2049ef1c4eca550e93`:
965 applicable structural/geometry and 131 package/basis/provenance checks.
See the [v3 audit](../../Worker_Log/Milestone_00/Milestone_00_v3_audit.md).
Quantum-only feasibility succeeded in a separate locked Psi4
prefix; the user explicitly approved the exact plan, limits and 12-hour/two-thread/
5-GiB budget on 2026-10-03. Both chemical test nodes
now exist and fail closed for absent quantum data; no skip or analytic
substitute is counted as a chemical pass. No
target model-versus-quantum results have been inspected. New
[G00 worker](../../Worker_Log/Milestone_01/Gate_00_v2_worker.md),
[M00 worker](../../Worker_Log/Milestone_00/Milestone_00_v2_worker.md) and
[G05 worker](../../Worker_Log/Milestone_03/Gate_05_v1_worker.md) record actual scope.
Latest full current-source result is **292 passed / 2 missing-quantum-data failures**;
analytic **272 passed / 22 deselected**, inherited G02/G03/admission/G04
**78/38/74/24**, strict **9/9**, upstream **1** and docs zero errors/eight
self-tests. The first G05 software reviewer was interrupted for the user's quota
pause after saving independent full/analytic/environment runs; it supplied no
verdict. A fresh-context Astra/high reviewer completed the exact software
snapshot `a7768e375476667139db374dc0091999263a37de`, accepting G00-T2 and the
six G05 software assertions; the [G05 v1 audit](../../Worker_Log/Milestone_03/Gate_05_v1_audit.md)
leaves T4 readiness changes_required for approval-plan binding. Quantum-only
target generation is running from committed `3124c6d275bf19a32ce364dfdb83b11115828ac5`;
model-versus-quantum comparison has not started. Its prepared-reference importer finding is repaired with a
six-case RED/GREEN rejection regression; [v2 worker](../../Worker_Log/Milestone_03/Gate_05_v2_worker.md)
records the repair. The [v2 Astra/high audit](../../Worker_Log/Milestone_03/Gate_05_v2_audit.md)
closes G05-v1-R1 and accepts prepared-loading readiness on exact `3124c6d`:
ten focused passes, one independent synthetic positive and 29 rejections,
270 matched source/input hashes. This is not chemical or full-G05 acceptance.
[Continuation](handoffs/M03-G05-continuation.md) records the
remaining reference and qualification steps. Inherited acceptance below is unchanged.

G04 is independently **accepted_for_scope** on child `m03-link-boundary` for `core-analytic-cpu`, nonperiodic Reference/CPU. The actual fresh-context **gpt-6-astra / high** reviewer accepted **G04-T1/T2/T3 and all seven stable assertions** on exact frozen submission `35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a`, carrying tested source/input commit `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The [G04 v1 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [independent evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_independent_r2/README.md) record the complete decision. [Acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json) covers seven checks/seven requirements; [closure evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/README.md) preserves the exact reviewed source and submitted worker evidence.

Independent results: **24 G04 cases, 262 full-suite passes, 261 analytic passes/1 deselected, G02 78/G03 38/admission 74, strict environment 9/9 and upstream 1**. New reviewer probes pass **37 comparisons, 24 all-coordinate FD sweeps, 13 cap rejections/two positives**, and trusted fresh offline cap reload across all three mapped states. Actual cap geometry, both parents, exact MM dispositions, nonidentity full maps, cap-MM derivatives and invariant force/torque are qualified. Native nested redistribution was measured correct before repairs; production recomputes sites after positioning. The nonblocking FD comment attribution is [corrected by measured force-class decomposition](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/fd-attribution-correction.md). Definitions, tolerances, locks and earlier evidence remain unchanged. The interrupted first Astra process supplies no decision; its captures and [actual reviewer history](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/reviewer-history.md) are preserved. No G04 blocker remains. M03 stays open until G07; [the next-dependency handoff](handoffs/M03-after-G04.md) stops this assignment at G04 acceptance.

M02 is independently **accepted_for_scope** on `m02-analytic-atm` for `core-analytic-cpu`. The **gpt-6-astra / high** reviewer closed **M02-R1/R2/R3**, accepted G02-T1/T2/T3 and G03-T1/T2/T3, and explicitly accepted **combined G02/G03/M02** on exact submitted snapshot `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`, carrying repaired source/input commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. The [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) and [G03/M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md) record the decision and remaining scope limits. The continuation preserves published handoff `a8098a43d46df76b981861aa8dec0522d31be966` and inherited M01 acceptance.

The [G02 v2 worker](../../Worker_Log/Milestone_02/Gate_02_v2_worker.md), [G03/M02 v2 worker](../../Worker_Log/Milestone_02/Gate_03_v2_worker.md) and [worker evidence](../../Worker_Log/Milestone_02/evidence/M02_v2/README.md) record the fresh **164-test** baseline, reproduction of **13 v1 failed rejections**, meaningful RED/GREEN and minimal repairs. Independent v2 reruns passed **238 full-suite tests**, **237 analytic tests/1 deselected**, **78 original G02**, **38 original G03**, **74 new admission cases**, **9 strict environment checks** and **1 upstream regression**. The preserved admission probe rejects all **18 negatives** and retains both positive State restorations; additional independently authored probes pass **120 rejections/9 positives**. Numerical replay passes **66 comparisons**, eight all-real finite-difference sweeps and eight upstream A-B-A cases with unchanged errors/limits; trusted offline stale-artifact detection still succeeds. [Independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_independent/README.md) identifies the actual reviewed runs. Core and Amber remain separate under unchanged locks.

The [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) covers all 16 stable G02/G03 checks and 11 requirement IDs on the exact reviewed snapshot. [Closure/publication evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/README.md) verifies report-only differences and all [127 repaired source/input hashes](../../Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json). The unexecuted draft and all 28 handoff milestone files remain unchanged. The [v1 G02 audit](../../Worker_Log/Milestone_02/Gate_02_v1_audit.md) and [v1 G03/M02 audit](../../Worker_Log/Milestone_02/Gate_03_v1_audit.md) retain their historical `changes_required` decisions for `a13019390f9770a42a5711bbb98025bd571ea40b`. [Fresh-agent handoff](handoffs/M02-fresh-agent-continuation.md) and [v1 independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v1_independent/README.md) remain provenance. Only `m02-analytic-atm` is published; main remains `2d7bcc94f901738e39f536f16de84699d4e8d631` and predecessor remains `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.

M01's analytic CPU implementation is independently accepted for `core-analytic-cpu` on `m00-audit-m01-development`. The [combined v2 audit](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md) reviewed snapshot `04944c67fc04c1667723f5292a07f8401cb94184`, carrying tested code `141c7fbcf2c5407e7880512d5481639bdc81bf57`. [G00 worker](../../Worker_Log/Milestone_01/Gate_00_v1_worker.md) records exact CPU APIs/provenance; [G01/M01 repair worker](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) records identities, fixed partitions, immutable versioned records, capability rejection, MM inventory and evidence validation. The full available suite passed 47 tests; the analytic selection passed 46 with one model test deselected. Strict environment validation passed all nine checks. [Repair validation evidence](../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz) and [complete environment identity](../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) identify the tested profile. The saved [original-MM inventory](../../Worker_Log/Milestone_01/evidence/M01_v2/original-mm-inventory.json) and [acceptance record](../../Worker_Log/Milestone_01/evidence/M01_v2/acceptance.json) carry the scoped handoff. These results do not accept a molecular gate.

The [independent M00 audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) accepts scientific contract version 1 for G00-T1/G01-T1/T2/T3 on `core-analytic-cpu`. Full M00 physical-reference closure remains open: exact G05/G07 references, quantum method/settings and profile limits need a separate reviewed decision before comparison results are inspected. The prior [repository preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) remains setup/example provenance.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

Analytic G04 continuation is complete. [G05](gates/G05-local-model-adapter.md) follows with its approved model-asset/loading prerequisites and checkpoint-specific native/adapter qualification; M00 must predeclare and independently review exact physical-reference choices before G05/G07 chemical comparisons. [G06](gates/G06-periodicity-and-interaction-ledger.md) then qualifies periodic geometry/interaction accounting under its actual prerequisites, and [G07](gates/G07-joint-cavity-ligand-atm.md) supplies combined M03 closure. [G08](gates/G08-thermodynamics-and-estimators.md) is a separate M04 analysis path under accepted G02/G03 prerequisites. Follow the [post-G04 handoff](handoffs/M03-after-G04.md). Molecular, chemical/protein, GPU/full-model, periodic/actual electrostatic and full workflow qualification remain deferred. The [original M02 handoff](handoffs/M02-implementation-and-audit.md) remains historical provenance.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 / analytic CPU design | accepted_for_scope | [Independent version 1 design review](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) |
| M00 / physical-reference design | accepted_for_scope | Exact v3 design independently accepted and explicitly approved by user; target reference convergence/comparison still pending |
| M01 / G00-T1, G01-T1/T2/T3 | accepted_for_scope | [Independent combined v2 review](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md); 47-test result on the recorded CPU profile |
| M02 / G02-T1/T2/T3, G03-T1/T2/T3 | accepted_for_scope | [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) / [G03-M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md); R1/R2/R3 closed on exact reviewed snapshot; [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) |
| G04 / analytic CPU | accepted | [Astra high full-G04 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json); no blocking findings |
| M03 / G04-G07 | in_progress | G04 accepted; applicable G05/G06 and G07 combined review still required |
| M04-M08 / G08-G13 | not_started | Follow [roadmap](../../README.md#roadmap) and gate prerequisites |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model chemical/protein qualification | not_run | G00/G05/G07 evidence and predeclared physical-reference limits |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
