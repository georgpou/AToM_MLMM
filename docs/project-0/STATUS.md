# Current status

G05 on the same child `m03-reference-g05` is **ready_for_review** for final R2
closure. The [v5 audit](../../Worker_Log/Milestone_03/Gate_05_v5_audit.md)
independently closed **R1 and R3** and reproduced a supervisor-loss R2 case.
The [v6 worker](../../Worker_Log/Milestone_03/Gate_05_v6_worker.md) repairs it:
the coordinator verifies whole-group cleanup after every supervisor exit before
receipt/promotion/scratch cleanup or any next launch. The user explicitly
approved their repair and publication of this branch. Repair source is
`ac414dcb4a5f401312616f08faa17ece5ea35e9e`, recorded in the v6 worker.
R1 preserves known completion failures and receipts; R2 holds the queue lease
through a supervised, checkpointed launch and kills the group on coordinator
loss; R3 makes record/receipt bytes and directory entries durable before progress.
**42 recovery cases and 336 full-suite tests pass; strict environment is 9/9.**
No QM calculations were rerun. All 46 references and the frozen scientific
inputs, results, logs, histories, model and limits are unchanged. Independent
repair closure remains pending. Actual calculation source remains
`419b64f7bd79199a0bf999e456f1564fc184cf75`; reviewed source/data remains
`a99a4448f14386e79c1546dd32fd83a33b9ac424`, continuing published checkpoint
`4bb2547` and accepted G04 predecessor `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`.

The [independent evidence](../../Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/README.md)
records **312 full-suite passes**, **18 focused G05 passes**, **9/9** environment
checks and **0 documentation errors / 8 self-tests**. Independent arithmetic
verified all 34 chemical rows, 28 cap/full-parent projections, 12 numerical
controls and required signs. All 1,439 submitted hashes and the frozen source,
inputs, reference locks and model identity were verified before this status
update. Three new synthetic recovery probes fail at their intended assertions
and document the defects; their closure requires no new QM calculations.

All **46 actual QM records** are complete: 34 frozen neutral-singlet chemical
targets, ten mandatory rotations and two finer-grid controls. Eight historical
records were reused by exact SHA-256; 38 new workers exited zero with complete
finite gradients and explicit SCF convergence in every saved Psi4 log. The
[approved exact M00 v3 plan](reference/M00-neutral-reference-plan-v3.md), basis,
settings, model identity and numerical/chemical limits are unchanged. The
maintained importer validated every reference, and **all 12 numerical controls
passed before the hashed quantum fixture bundle was created**.

Both G05-T4 actual model-versus-quantum checks passed. Largest per-family
conformer RMS/maximum errors are **0.176/0.286 kcal/mol** (limits 1/2);
contact-minus-separated RMS/maximum are **0.339/0.456 kcal/mol** (limits 0.5/1).
Largest raw force component RMS/atom-vector errors are **0.02133/0.08661
eV/angstrom** (limits 0.05/0.15); largest projected full-parent errors are
**0.01451/0.08661 eV/angstrom**. Largest net ligand force-vector error is
**0.03976 eV/angstrom** (limit 0.05). All seven required attraction and four
compressed-repulsion sign checks passed; every weak/separated row is retained.
[Actual results, tables and exportable figures](../../Worker_Log/Milestone_03/evidence/G05_v4/RESULTS.md)
retain all cases, raw outputs, cap forces and both real-parent projections.

Final full source suite: **312 passed**. Recovery software: **18 focused
passes**, with meaningful missing-feature, cache-headroom and live-worker
RED/GREEN evidence preserved. Strict environment checks passed **9/9** before
launch; final documentation/packaging verification is recorded in the
[continuation worker](../../Worker_Log/Milestone_03/Gate_05_v4_worker.md).
The fresh machine's absent main/Amber/reference prefixes were rebuilt under
the unchanged locks, including all 105 exact reference packages.

Cumulative charged quantum wall time is **4.400612 h**, including a conservative
**2350.09535 s** debit for the prior launch-to-stop interval; the resumed session
used **3.747808 h**. Runtime allocation was two threads and **3 GiB Psi4 memory**
under the approved 5 GiB upper cap. Maximum measured new-worker RSS was
**4.670959 GiB**. Total cgroup memory includes cache and reached the 8 GiB cap;
zero OOM/OOM-kill events were recorded. All private quantum scratch is cleaned.
The original stopped attempt is unchanged; new orders/logs/receipts, one-second
resource samples and durable progress remain in the separate resumed attempt.

Inherited software decisions remain the [v1](../../Worker_Log/Milestone_03/Gate_05_v1_audit.md)
and [v2](../../Worker_Log/Milestone_03/Gate_05_v2_audit.md) scoped audits on
`a7768e3`/`3124c6d`; the importer approval-binding finding is closed.
The [M00 v3 design audit](../../Worker_Log/Milestone_00/Milestone_00_v3_audit.md)
and explicit user scientific/budget agreement persist. The full-G05 v4 recovery
R1/R3 findings are independently closed in v5; the v6 final R2 repair awaits
closure. Inherited decisions do not close that remaining finding.
Model metadata remains unqualified until acceptance. Protein binding, periodic/GPU/electrostatic
physics and complete ABFE/RBFE remain outside this demonstrated scope.

The earlier automatic publication rejection required explicit source/history
export authorization. The user has now authorized fixes and publication to the
existing GitHub branch. Remote publication will follow repair closure; no new
push is claimed yet.

G04 is independently **accepted_for_scope** on child `m03-link-boundary` for `core-analytic-cpu`, nonperiodic Reference/CPU. The actual fresh-context **gpt-6-astra / high** reviewer accepted **G04-T1/T2/T3 and all seven stable assertions** on exact frozen submission `35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a`, carrying tested source/input commit `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The [G04 v1 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [independent evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_independent_r2/README.md) record the complete decision. [Acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json) covers seven checks/seven requirements; [closure evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/README.md) preserves the exact reviewed source and submitted worker evidence.

Independent results: **24 G04 cases, 262 full-suite passes, 261 analytic passes/1 deselected, G02 78/G03 38/admission 74, strict environment 9/9 and upstream 1**. New reviewer probes pass **37 comparisons, 24 all-coordinate FD sweeps, 13 cap rejections/two positives**, and trusted fresh offline cap reload across all three mapped states. Actual cap geometry, both parents, exact MM dispositions, nonidentity full maps, cap-MM derivatives and invariant force/torque are qualified. Native nested redistribution was measured correct before repairs; production recomputes sites after positioning. The nonblocking FD comment attribution is [corrected by measured force-class decomposition](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/fd-attribution-correction.md). Definitions, tolerances, locks and earlier evidence remain unchanged. The interrupted first Astra process supplies no decision; its captures and [actual reviewer history](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/reviewer-history.md) are preserved. No G04 blocker remains. M03 stays open until G07; [the next-dependency handoff](handoffs/M03-after-G04.md) stops this assignment at G04 acceptance.

M02 is independently **accepted_for_scope** on `m02-analytic-atm` for `core-analytic-cpu`. The **gpt-6-astra / high** reviewer closed **M02-R1/R2/R3**, accepted G02-T1/T2/T3 and G03-T1/T2/T3, and explicitly accepted **combined G02/G03/M02** on exact submitted snapshot `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`, carrying repaired source/input commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. The [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) and [G03/M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md) record the decision and remaining scope limits. The continuation preserves published handoff `a8098a43d46df76b981861aa8dec0522d31be966` and inherited M01 acceptance.

The [G02 v2 worker](../../Worker_Log/Milestone_02/Gate_02_v2_worker.md), [G03/M02 v2 worker](../../Worker_Log/Milestone_02/Gate_03_v2_worker.md) and [worker evidence](../../Worker_Log/Milestone_02/evidence/M02_v2/README.md) record the fresh **164-test** baseline, reproduction of **13 v1 failed rejections**, meaningful RED/GREEN and minimal repairs. Independent v2 reruns passed **238 full-suite tests**, **237 analytic tests/1 deselected**, **78 original G02**, **38 original G03**, **74 new admission cases**, **9 strict environment checks** and **1 upstream regression**. The preserved admission probe rejects all **18 negatives** and retains both positive State restorations; additional independently authored probes pass **120 rejections/9 positives**. Numerical replay passes **66 comparisons**, eight all-real finite-difference sweeps and eight upstream A-B-A cases with unchanged errors/limits; trusted offline stale-artifact detection still succeeds. [Independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_independent/README.md) identifies the actual reviewed runs. Core and Amber remain separate under unchanged locks.

The [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) covers all 16 stable G02/G03 checks and 11 requirement IDs on the exact reviewed snapshot. [Closure/publication evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/README.md) verifies report-only differences and all [127 repaired source/input hashes](../../Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json). The unexecuted draft and all 28 handoff milestone files remain unchanged. The [v1 G02 audit](../../Worker_Log/Milestone_02/Gate_02_v1_audit.md) and [v1 G03/M02 audit](../../Worker_Log/Milestone_02/Gate_03_v1_audit.md) retain their historical `changes_required` decisions for `a13019390f9770a42a5711bbb98025bd571ea40b`. [Fresh-agent handoff](handoffs/M02-fresh-agent-continuation.md) and [v1 independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v1_independent/README.md) remain provenance. Only `m02-analytic-atm` is published; main remains `2d7bcc94f901738e39f536f16de84699d4e8d631` and predecessor remains `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.

M01's analytic CPU implementation is independently accepted for `core-analytic-cpu` on `m00-audit-m01-development`. The [combined v2 audit](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md) reviewed snapshot `04944c67fc04c1667723f5292a07f8401cb94184`, carrying tested code `141c7fbcf2c5407e7880512d5481639bdc81bf57`. [G00 worker](../../Worker_Log/Milestone_01/Gate_00_v1_worker.md) records exact CPU APIs/provenance; [G01/M01 repair worker](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) records identities, fixed partitions, immutable versioned records, capability rejection, MM inventory and evidence validation. The full available suite passed 47 tests; the analytic selection passed 46 with one model test deselected. Strict environment validation passed all nine checks. [Repair validation evidence](../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz) and [complete environment identity](../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) identify the tested profile. The saved [original-MM inventory](../../Worker_Log/Milestone_01/evidence/M01_v2/original-mm-inventory.json) and [acceptance record](../../Worker_Log/Milestone_01/evidence/M01_v2/acceptance.json) carry the scoped handoff. These results do not accept a molecular gate.

The [independent M00 audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) accepts scientific contract version 1 for G00-T1/G01-T1/T2/T3 on `core-analytic-cpu`. The subsequent exact M00 v3 physical-reference design was separately reviewed and explicitly approved before these calculations and comparisons; full G05 qualification awaits recovery repair and independent closure of the v4 findings. The prior [repository preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) remains setup/example provenance.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

The requested full-[G05](gates/G05-local-model-adapter.md) v4 audit is complete,
and **R1/R3** are closed. The final R2 repair is ready in v6. Next is focused
independent closure and user-authorized branch publication. Preserve the completed
46-reference batch, fixed scientific settings and model; no QM rerun is needed.
[G06](gates/G06-periodicity-and-interaction-ledger.md) and
[G07](gates/G07-joint-cavity-ligand-atm.md) are subsequent assignments, supplying
periodic qualification and combined M03 closure. [G08](gates/G08-thermodynamics-and-estimators.md)
is a separate M04 analysis path. Broader physical profiles remain deferred.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 / analytic CPU design | accepted_for_scope | [Independent version 1 design review](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) |
| M00 / physical-reference design | accepted_for_scope | Exact v3 design independently accepted and explicitly approved; reference convergence and G05 comparisons independently verified; G05 recovery closure remains |
| M01 / G00-T1, G01-T1/T2/T3 | accepted_for_scope | [Independent combined v2 review](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md); 47-test result on the recorded CPU profile |
| M02 / G02-T1/T2/T3, G03-T1/T2/T3 | accepted_for_scope | [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) / [G03-M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md); R1/R2/R3 closed on exact reviewed snapshot; [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) |
| G04 / analytic CPU | accepted | [Astra high full-G04 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json); no blocking findings |
| M03 / G04-G07 | in_progress | G04 accepted; applicable G05/G06 and G07 combined review still required |
| M04-M08 / G08-G13 | not_started | Follow [roadmap](../../README.md#roadmap) and gate prerequisites |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model small-system chemical / protein qualification | ready_for_review / not_run | G05 saved scientific results independently verified; R1/R3 closed; v6 R2 repair passes and awaits closure. Protein qualification remains G07/later work. |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
