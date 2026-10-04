# Current status

**Current assignment: technical ML/MM engine readiness, beginning with M04/G08
on `m04-engine-readiness`.** The user's latest instruction supersedes the
G07-only assignment and authorizes a new branch copied from published
`m03-g06-g07` at `fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86`. The
[fresh-agent handoff](handoffs/ENGINE-READINESS-fresh-agent-v1.md) directs known-answer
thermodynamics, complete energy/force accounting, preparation/export,
restart/exchange and reproducible cluster trials. G08 can proceed from accepted
G02/G03. Later technical development must report its scoped evidence while
preserving unfulfilled physical/combined-review requirements. No new gate code
or longer production run was started during handoff preparation. Main and the
published G07 predecessor remain unchanged.

**G08 and combined M04 require the G08-R1 result-admission repair.**
Source `966a8d61347f65a69f8ba7e6750c4379d4e0503f` implements explicit thermodynamic
records/correction obligations, finite-wall translation, full reduced-potential
reconstruction, active unequal-midpoint bridge checks and independent pinned
PyMBAR/UWHAM analysis. The [v1 worker](../../Worker_Log/Milestone_04/Gate_08_v1_worker.md)
preserves all six stable assertions, failures/repairs, [raw evidence](../../Worker_Log/Milestone_04/evidence/G08_v1/README.md),
and the proposed additive record admission amendment. The unchanged locked
main/Amber environment was rebuilt and passes 9 checks; the final full CPU
suite passes **433 tests**. Three independent native analytic MD seeds satisfy
both known-answer criteria, with mean **1.4813958 +/-0.0437064 kJ/mol** versus
**+1.5**; replicate spread **0.0409745** is separate. Both unequal-midpoint
ensembles and their cross-state energies are preserved. The actual
[GPT-6.1-sol/MAX v1 audit](../../Worker_Log/Milestone_04/Gate_08_v1_audit.md)
confirms the numerics and 433 fresh CPU passes, but rejects final-result record
admission with absent/uncomputed corrections. V1 evidence is frozen; a v2 repair
and independent closure are required. No gate/milestone or molecular binding
acceptance is claimed.

Maintenance reclaimed **2,083,614,720 bytes**; free disk increased from
**18.354 to 20.294 GiB** immediately afterward. Removed 328 verified compressed
package downloads, the verified installer, and ignored Python/pytest caches.
Two closed independent probe trees were losslessly archived, preserving every
one of their **1,606 files** and failure cases with hashes and restoration
instructions. Canonical QM attempts/logs/receipts/ledger, active environments,
code, fixtures, model assets and all 46 G05 records remain intact. Strict
post-cleanup environment checks passed **9/9**. The
[maintenance worker](../../Worker_Log/Documentation/Engine_Handoff_v1_worker.md)
records verification and exact commands. This cleanup does not reset the QM
budget or establish that the remaining references fit its resource screen.

**G06 and G07 numerical scopes are independently accepted; M03 physical closure
remains blocked.** The actual **GPT-6.1-sol/MAX** reviewer audited exact submission
`ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b`, carrying source
`c584086da68654b07f1a477d7ce1e48da42a9838`. The
[G06 audit](../../Worker_Log/Milestone_03/Gate_06_v1_audit.md) accepts all six
assertions; the [G07/M03 audit](../../Worker_Log/Milestone_03/Gate_07_v1_audit.md)
accepts T1/T2/T3 and its seven numerical assertions separately. This is the narrow
small-system single-point **OpenMM Reference double / MACE CPU float64** scope;
OpenMM CPU PME precision, dynamics, protein/binding accuracy and broader profiles
are not qualified. No mathematical/coding repair finding remains in that scope.

Independent checks: **381 full-suite passes**, **45 focused passes**, **9/9 strict
environment checks**, 24 additional alternative-cut periodic route comparisons
and five intermediate force sweeps. All 1,924 initially frozen tracked files and
46 accepted G05 records remained byte-identical during review. The seven
project-specific force-sensitivity exceedances and 30 then-missing quantum references
were physical qualification blockers at that review; **29 remain missing after
the later pilot below**. No limit or scientific input changed.

**Completed G07 assignment: assess the frozen references and checkpoint at the
authorized resource/budget boundary on `m03-g06-g07`.** The user superseded the earlier M04/G08 handoff
and authorized a 24-hour cumulative quantum-worker budget with a one-hour pilot.
The published starting HEAD is `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`;
reviewed execution source `4e2cb06b0e5e0b3b081e379969428ec93a807866` is its direct
child. No separate branch/worktree or M04/G08 work was started.

The current child `m03-g06-g07` continues the published G05 base
`08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`. G06-T1/T2/T3 and G07-T1/T2/T3
implementation and small-system numerical checks are complete on source
`c584086da68654b07f1a477d7ce1e48da42a9838`: **381 CPU-suite passes**, **23 final
G06 focused passes**, and **9/9 strict main/Amber environment checks**. The
independent audit above accepts the implemented numerical scope only. See the
[G06 worker](../../Worker_Log/Milestone_03/Gate_06_v1_worker.md),
[G07 worker](../../Worker_Log/Milestone_03/Gate_07_v1_worker.md), and exact
[snapshot](../../Worker_Log/Milestone_03/evidence/G07_v1/snapshot.json).

**G07-T4 and combined M03 physical closure are blocked.** Actual GAFF/AM1-BCC MM
charges/XML and all **20 rows / 50 physical descriptions** are frozen. All 50
hybrid single points agree numerically with an independent native-model/MM
oracle, but **seven of 40 region-pair comparisons exceed the unchanged
0.05 eV/angstrom net ligand force sensitivity limit** (maximum **0.12165016265111903**).
Maximum contact-energy sensitivity is **0.9744628863435872 kcal/mol**, below its
1.0 limit. Both model region and retained MM contribute. The
[complete failure report](../../Worker_Log/Milestone_03/evidence/G07_v1/RESULTS.md)
retains every pair and separated control. No input or limit was tuned.

The exact new-reference matrix has **30 jobs** (20 full-parent and ten alternative
caps), with **20 exact G05 baseline records reused**. A separate
[authorization](../../Worker_Log/Milestone_03/evidence/G07_v2/authorization.json)
binds the frozen matrix and budget without changing its historical preparation
status. Main/Amber/reference environments were rebuilt under their unchanged
locks; reference packages are exactly **Psi4 1.10.2 / LibXC 7.0.0**. The
[execution audit](../../Worker_Log/Milestone_03/Gate_07_v2_audit.md) independently
accepts the original adapter mechanism at `4e2cb06`, following **403 CPU-suite
passes** and **64 independent affected/recovery passes**.

The full-parent ethanol/methanol pilot computed an energy and 32-row gradient,
exited zero and explicitly converged in **38.76 minutes**. Its initial admission
parser required a different affirmative log phrase. The independently accepted
[v3 recovery repair](../../Worker_Log/Milestone_03/Gate_07_v3_audit.md), source
`fcc1de9619f58934ff0c5835e01ecf3848a8a48c`, passed **416 CPU-suite tests**, **35
independent focused tests** and all independent fault/recovery probes. A durable
validation-only correction then admitted the original result without rerunning
QM or overwriting the original rejection receipt. **One of 30 new references is
complete; 19 full-parent and ten alternative-cap jobs remain incomplete.** The
[worker report](../../Worker_Log/Milestone_03/Gate_07_v2_worker.md) preserves all
failures, exact commands and recovery evidence. The user's session-quota pause
was resumed; the quantum budget was not reset.

Charged quantum wall time is **2,325.644650052 s**, leaving **23.3540 h**. Measured
group RSS peaked at **3.190 GiB**, scratch at **9.015 GiB**, free disk stayed above
**9.921 GiB**, and OOM/OOM-kill deltas were zero. All private scratch and live
actual worker processes are gone. The reviewed remaining-job runtime screen is
**34.1646 h**, which exceeds the remaining allowance; no batch continuation was
launched. Projected largest-job scratch is **16.7615 GiB** against **18.3704 GiB**
free disk at assessment, which also fails the mandatory 5 GiB reserve. These are
screening estimates, not measured requirements for the missing jobs.

The single-contact force decomposition projects the cap onto both parents once
and retains all real MM forces. Same-cap MACE/QM projected RMS/maximum errors are
**0.0127151/0.0759817 eV/angstrom**. Capped QM plus retained MM relative to full
QM gives **0.3942092/2.0543877**, exceeding the unchanged **0.05/0.15** full-real
limits; the baseline hybrid also exceeds both. Complete-parent MACE's maximum
atom-vector/net-ligand errors are **0.1716568/0.1147311**, above **0.15/0.05**.
The capped description's own contact-minus-separated energy error is
**0.265180 kcal/mol**. Full-parent separated QM is absent, so complete energy
partition attribution remains unmeasured. This one contact cannot qualify the
matrix; all seven existing sensitivity failures remain. The independent
GPT-6.1-sol/MAX [v4 audit](../../Worker_Log/Milestone_03/Gate_07_v4_audit.md)
accepts only the actual admission, partial arithmetic and decision to stop;
it confirms direct retained-MM forces and once-projected cap derivatives.
All **46**
accepted G05 records, earlier scientific evidence, model, inputs and locks stay
byte-identical. The [cleanup strategy](../../Worker_Log/Milestone_03/evidence/G07_v2/cleanup-strategy.md)
preserves useful code/logs/assets and identifies only verified temporary or
reconstructible candidates. No cache or essential asset was deleted during that
G07 assignment; the later authorized maintenance at the top of this status
removed only verified downloads/caches and archived closed redundant copies.

G05 on the same child `m03-reference-g05` is **accepted_for_scope** for the
fixed neutral nonperiodic CPU local-reference profile. The independent
**GPT-6.1 Sol / MAX** [v6 audit](../../Worker_Log/Milestone_03/Gate_05_v6_audit.md)
accepts **G05-T1/T2/T3/T4 and all eight stable assertions**, with **R1/R2/R3
closed and no remaining findings**. Exact review HEAD is
`ca12e023f6a6e67321fafd4af642c0975041d7f6`; repair source is
`ac414dcb4a5f401312616f08faa17ece5ea35e9e`, recorded in the
[v6 worker](../../Worker_Log/Milestone_03/Gate_05_v6_worker.md). The coordinator
verifies whole-group cleanup after every supervisor exit before
receipt/promotion/scratch cleanup or any next launch.
R1 preserves known completion failures and receipts; R2 holds the queue lease
through a supervised, checkpointed launch and kills the group on coordinator
loss; R3 makes record/receipt bytes and directory entries durable before progress.
**42 recovery cases and 336 full-suite tests pass; strict environment is 9/9.**
No QM calculations were rerun. All 46 references and the frozen scientific
inputs, results, logs, histories, model and limits are unchanged. The
[closure record](../../Worker_Log/Milestone_03/evidence/G05_v6_closure/acceptance.json)
preserves the decision and exact identities. Actual calculation source remains
`419b64f7bd79199a0bf999e456f1564fc184cf75`; reviewed source/data remains
`a99a4448f14386e79c1546dd32fd83a33b9ac424`, continuing published checkpoint
`4bb2547` and accepted G04 predecessor `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`.

The historical [v4 independent evidence](../../Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/README.md)
records **312 full-suite passes**, **18 focused G05 passes**, **9/9** environment
checks and **0 documentation errors / 8 self-tests**. Independent arithmetic
verified all 34 chemical rows, 28 cap/full-parent projections, 12 numerical
controls and required signs. All 1,439 submitted hashes and the frozen source,
inputs, reference locks and model identity were verified before this status
update. Its three synthetic recovery probes failed at their intended assertions
and documented the original defects. Their RED evidence is preserved; the
v5/v6 repairs and independent reviews close all three without new QM calculations.

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

The original v4 full source suite passed **312 tests**. Recovery software had **18 focused
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
R1/R3 findings are independently closed in v5; the v6 review closes R2 and
accepts the combined limited G05 scope. Frozen model metadata is preserved;
the v6 audit records the current scoped acceptance. Protein binding, periodic/GPU/electrostatic
physics and complete ABFE/RBFE remain outside this demonstrated scope.

The user explicitly authorized these fixes and publication to the existing
GitHub branch. The accepted branch is **published** at
`bb2987f20e31c14543f452b56b7108d1190d0ea3`, independently verified with
`git ls-remote`. The [publication receipt](../../Worker_Log/Milestone_03/evidence/G05_v6_closure/publication.json)
records the destination and normal fast-forward from `4bb2547`; this subsequent
status/receipt commit changes reporting only. Main is unchanged.

G04 is independently **accepted_for_scope** on child `m03-link-boundary` for `core-analytic-cpu`, nonperiodic Reference/CPU. The actual fresh-context **gpt-6-astra / high** reviewer accepted **G04-T1/T2/T3 and all seven stable assertions** on exact frozen submission `35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a`, carrying tested source/input commit `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The [G04 v1 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [independent evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_independent_r2/README.md) record the complete decision. [Acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json) covers seven checks/seven requirements; [closure evidence](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/README.md) preserves the exact reviewed source and submitted worker evidence.

Independent results: **24 G04 cases, 262 full-suite passes, 261 analytic passes/1 deselected, G02 78/G03 38/admission 74, strict environment 9/9 and upstream 1**. New reviewer probes pass **37 comparisons, 24 all-coordinate FD sweeps, 13 cap rejections/two positives**, and trusted fresh offline cap reload across all three mapped states. Actual cap geometry, both parents, exact MM dispositions, nonidentity full maps, cap-MM derivatives and invariant force/torque are qualified. Native nested redistribution was measured correct before repairs; production recomputes sites after positioning. The nonblocking FD comment attribution is [corrected by measured force-class decomposition](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/fd-attribution-correction.md). Definitions, tolerances, locks and earlier evidence remain unchanged. The interrupted first Astra process supplies no decision; its captures and [actual reviewer history](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/reviewer-history.md) are preserved. No G04 blocker remains. M03 stays open until G07; [the next-dependency handoff](handoffs/M03-after-G04.md) stops this assignment at G04 acceptance.

M02 is independently **accepted_for_scope** on `m02-analytic-atm` for `core-analytic-cpu`. The **gpt-6-astra / high** reviewer closed **M02-R1/R2/R3**, accepted G02-T1/T2/T3 and G03-T1/T2/T3, and explicitly accepted **combined G02/G03/M02** on exact submitted snapshot `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`, carrying repaired source/input commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. The [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) and [G03/M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md) record the decision and remaining scope limits. The continuation preserves published handoff `a8098a43d46df76b981861aa8dec0522d31be966` and inherited M01 acceptance.

The [G02 v2 worker](../../Worker_Log/Milestone_02/Gate_02_v2_worker.md), [G03/M02 v2 worker](../../Worker_Log/Milestone_02/Gate_03_v2_worker.md) and [worker evidence](../../Worker_Log/Milestone_02/evidence/M02_v2/README.md) record the fresh **164-test** baseline, reproduction of **13 v1 failed rejections**, meaningful RED/GREEN and minimal repairs. Independent v2 reruns passed **238 full-suite tests**, **237 analytic tests/1 deselected**, **78 original G02**, **38 original G03**, **74 new admission cases**, **9 strict environment checks** and **1 upstream regression**. The preserved admission probe rejects all **18 negatives** and retains both positive State restorations; additional independently authored probes pass **120 rejections/9 positives**. Numerical replay passes **66 comparisons**, eight all-real finite-difference sweeps and eight upstream A-B-A cases with unchanged errors/limits; trusted offline stale-artifact detection still succeeds. [Independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_independent/README.md) identifies the actual reviewed runs. Core and Amber remain separate under unchanged locks.

The [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) covers all 16 stable G02/G03 checks and 11 requirement IDs on the exact reviewed snapshot. [Closure/publication evidence](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/README.md) verifies report-only differences and all [127 repaired source/input hashes](../../Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json). The unexecuted draft and all 28 handoff milestone files remain unchanged. The [v1 G02 audit](../../Worker_Log/Milestone_02/Gate_02_v1_audit.md) and [v1 G03/M02 audit](../../Worker_Log/Milestone_02/Gate_03_v1_audit.md) retain their historical `changes_required` decisions for `a13019390f9770a42a5711bbb98025bd571ea40b`. [Fresh-agent handoff](handoffs/M02-fresh-agent-continuation.md) and [v1 independent evidence](../../Worker_Log/Milestone_02/evidence/M02_v1_independent/README.md) remain provenance. M02 publication is on `m02-analytic-atm`; main remains `2d7bcc94f901738e39f536f16de84699d4e8d631` and predecessor remains `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.

M01's analytic CPU implementation is independently accepted for `core-analytic-cpu` on `m00-audit-m01-development`. The [combined v2 audit](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md) reviewed snapshot `04944c67fc04c1667723f5292a07f8401cb94184`, carrying tested code `141c7fbcf2c5407e7880512d5481639bdc81bf57`. [G00 worker](../../Worker_Log/Milestone_01/Gate_00_v1_worker.md) records exact CPU APIs/provenance; [G01/M01 repair worker](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) records identities, fixed partitions, immutable versioned records, capability rejection, MM inventory and evidence validation. The full available suite passed 47 tests; the analytic selection passed 46 with one model test deselected. Strict environment validation passed all nine checks. [Repair validation evidence](../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz) and [complete environment identity](../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) identify the tested profile. The saved [original-MM inventory](../../Worker_Log/Milestone_01/evidence/M01_v2/original-mm-inventory.json) and [acceptance record](../../Worker_Log/Milestone_01/evidence/M01_v2/acceptance.json) carry the scoped handoff. These results do not accept a molecular gate.

The [independent M00 audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) accepts scientific contract version 1 for G00-T1/G01-T1/T2/T3 on `core-analytic-cpu`. The subsequent exact M00 v3 physical-reference design was separately reviewed and explicitly approved before these calculations and comparisons; the v6 audit accepts full G05 for the fixed neutral nonperiodic CPU profile after independent recovery closure. The prior [repository preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) remains setup/example provenance.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

Repair G08-R1 and obtain actual GPT-6.1-sol/MAX independent closure, then continue
scoped G09/G10 technical preparation/export/restart work under the current
engine-readiness handoff. Report technical evidence separately from molecular
physical qualification. G06/G07 numerical review remains accepted; G07-T4 and
M03 physical closure remain blocked. Preserve all accepted G05 data, controls,
seven sensitivity exceedances, pilot force failures and the unchanged cumulative
quantum ledger. No quantum/production continuation is authorized by this technical
work; the [remaining-reference handoff](handoffs/G07-reference-remaining-v2.md)
retains the failed resource screen and safe continuation conditions.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 / analytic CPU design | accepted_for_scope | [Independent version 1 design review](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) |
| M00 / physical-reference design | accepted_for_scope | Exact v3 design independently accepted and explicitly approved; reference convergence, G05 comparisons and v6 recovery closure independently verified |
| M01 / G00-T1, G01-T1/T2/T3 | accepted_for_scope | [Independent combined v2 review](../../Worker_Log/Milestone_01/Gate_01_v2_audit.md); 47-test result on the recorded CPU profile |
| M02 / G02-T1/T2/T3, G03-T1/T2/T3 | accepted_for_scope | [G02 v2 audit](../../Worker_Log/Milestone_02/Gate_02_v2_audit.md) / [G03-M02 v2 audit](../../Worker_Log/Milestone_02/Gate_03_v2_audit.md); R1/R2/R3 closed on exact reviewed snapshot; [acceptance record](../../Worker_Log/Milestone_02/evidence/M02_v2_closure/acceptance.json) |
| G04 / analytic CPU | accepted | [Astra high full-G04 audit](../../Worker_Log/Milestone_03/Gate_04_v1_audit.md) and [acceptance](../../Worker_Log/Milestone_03/evidence/G04_v1_closure/acceptance.json); no blocking findings |
| G06 / fixed-volume small-system Reference/MACE-CPU | accepted_for_scope | Sol 6.1/MAX accepts six assertions for the narrow numerical profile; wider precision/dynamics profiles remain unqualified |
| G07 / T1/T2/T3 small-system Reference/MACE-CPU | accepted_for_scope | Sol 6.1/MAX accepts seven numerical assertions, periodic and unequal two-ligand composition; physical T4 remains blocked |
| G07 / T4 physical-reference sensitivity | blocked | Seven sensitivity failures plus measured pilot force-approximation exceedances; one validated full-parent reference, 29 missing; runtime/scratch screens exceed current envelope |
| M03 / G04-G07 | blocked | G04/G05 and G06/G07 numerical scopes accepted; resolve G07-T4 physical blockers and obtain closing physical acceptance |
| M04 / G08 analytic thermodynamic accounting | changes_requested | [G08 v1 audit](../../Worker_Log/Milestone_04/Gate_08_v1_audit.md); numerics and 433 independent CPU passes confirmed; G08-R1 final-result admission open, v2 required |
| M05-M08 / G09-G13 | not_started | Retain molecular gate prerequisites and physical-qualification limits |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model small-system chemical / protein qualification | accepted_for_scope / not_run | Sol 6.1/MAX v6 audit accepts neutral CPU G05 and all eight assertions; R1/R2/R3 closed. Protein qualification remains G07/later work. |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
