# Current status

**G10 multistate Tasks 1–4: v7 independent combined audit PAUSED; no final decision.**
The user requested a usage-limit checkpoint while the audit was incomplete.
The sole `gpt-6.1-sol / max` auditor completed 53 focused passes (0 skips),
three additional inert NumPy challenges and source/evidence identity checks;
broader arithmetic/transaction/current-record probes remain pending. A fourth
extra challenge stopped at an audit-harness serialization error, preserved in
the raw evidence. No scoped GREEN or repair closure is claimed. Continue from
[the durable checkpoint](../../Worker_Log/Milestone_05/evidence/G10_v7_independent/CONTINUATION.md)
and [partial v7 audit](../../Worker_Log/Milestone_05/Gate_10_v7_audit.md) before any fix.
The complete v5 RED / changes_required decision remains the prior decision.
Task A (R1/R4/R7 and inert capture/report clock agreement) is now implemented in
code/result commit `8157b24ee93a841dbf91cf10a02a19dd321e6c88`; its worker record
and evidence are in [Gate_10_v6_worker.md](../../Worker_Log/Milestone_05/Gate_10_v6_worker.md).
Tasks B and C (R2/R3 and R5/R6) are implemented and self-checked in the v7
worker report; the combined independent audit remains pending. This is not G10
acceptance.

After the user resumed the saved pause, the sole independent `gpt-6.1-sol / max`
[v5 combined audit](../../Worker_Log/Milestone_05/Gate_10_v5_audit.md) reviewed
frozen HEAD `edd587679aaa110ea687cca29b9e3aee70b7b6f0`, source/test-identical to
completed worker submission `ecace38b34e15fae65508b2ee9cd2f535a1b85c4`.
Seven material findings require repairs: complete inert type/limit/identity
admission, restored checkpoint clocks, geometry guards on restored coordinates,
refreshed-energy consistency, postcommit failure records, cross-parent and
rollback-file fsync coverage, and nested manifest sealing. The fresh independent
checks include **47 pytest passes, no skips**, two analytic numerical controls,
both exact v2 molecular records, 36 actual schedule evaluations and eight pair
matrices, plus 17 violating characterization cases grouped into those findings.
The Task 4 representation comparator passes its scoped numerical review; it
does not close the other obligations. No implementation repair was made during
the audit. Source, tests, specifications, worker reports and failed artifacts
remain frozen. The [independent evidence](../../Worker_Log/Milestone_05/evidence/G10_v5_independent/README.md)
records exact commands, outcomes, hashes and minimal repairs/regressions.
The [audit-ready pause handoff](handoffs/G10-MULTISTATE-AUDIT-READY.md) remains
historical provenance. The bounded repair batch is complete; next, resume and
finish the paused independent combined audit before multistate acceptance or
any additional repair.

The [repair batch](handoffs/G10-MULTISTATE-REPAIR-BATCH.md) was shortened at
the user's request: Task A followed by one combined runtime/durability worker.
Completed [v6 Task A](../../Worker_Log/Milestone_05/Gate_10_v6_worker.md) has code
commit `8157b24ee93a841dbf91cf10a02a19dd321e6c88` and clean report/evidence
commit `f0bfbc5019e1741c23e9308f863054dd32c3bec0`. Its R1/R4/R7 and inert-clock
self-checks pass **37 focused tests** (36 challenge PASS/0 VIOLATION) and
**74 retained compatibility tests**, no skips. The completed [v7 runtime and
durability worker](../../Worker_Log/Milestone_05/Gate_10_v7_worker.md) starts at
`bfbaa873cf13570313c945a9665f84580dde7439`, submits source/result commit
`27e1639fefdde8ccca62263846204237391bf621`, passes the fresh v2 pilots (**2
tests**) and the one final CPU suite (**626 passed, no skip text**). Its exact
RED/GREEN traces, test outputs and hashes are indexed in
[G10 v7 evidence](../../Worker_Log/Milestone_05/evidence/G10_v7/README.md).
The combined independent audit remains next; no independent repair acceptance
is claimed and the v5 RED decision remains.

**Completed G10 worker submission.** On `g10-engine-next`, the multistate core source/result commit
`cef01748db1d872775c1cb88e67f881182066e6c` adds the bounded 3–8-state serial
controller and analytic/fault regressions, with test-only archive follow-up
`5a8ab584cc9af9e74afb7f2d926ca8b4af688e41`. Task 4 starts from exact clean
HEAD `1f26d2e52f63f0d3b734c5e5dd0f4fe0f51dd8df`; code/result commit
`a507bbddfccc1a88b8df4ab18277040889bf379c` adds v2 ABFE/RBFE pilots, usage docs,
and a minimal checkpoint/sample identity repair. The repair preserves exact
sample/report hashes and portable-State/checkpoint equality, adds a `1e-15 nm`
captured-sample/checkpoint position bound for measured OpenMM unit-roundtrip
drift, and uses the existing `1e-8` raw-energy comparison. Physical definitions
and accepted Hamiltonian tolerances are unchanged. The fresh pilots pass
**2 tests in 156.56 s**; required pair/export/restart compatibility passes
**74 tests in 171.69 s**; the single combined CPU suite passes **577 tests in
913.26 s**, all with no skips. The docs self-test reports zero errors. Full
failure and source history, local run artifacts, and resource scopes are in
the [G10 v5 evidence](../../Worker_Log/Milestone_05/evidence/G10_v5/README.md)
and [v5 worker record](../../Worker_Log/Milestone_05/Gate_10_v5_worker.md).
This is implementation evidence, not G10/M05 acceptance. Full G10/M05,
affinity/equilibrium/mixing/uncertainty claims and existing G07 physical/
reference blockers remain open; the 46 G05 records and QM ledger
`2325.6446500519996 / 86400 s` are unchanged. The v4 core report remains
preserved at [Gate_10_v4_worker.md](../../Worker_Log/Milestone_05/Gate_10_v4_worker.md).

**Current continuation: CPU engine development on `cloud-engine-continuation`.**
The [current handoff](handoffs/CLOUD-ENGINE-CONTINUATION.md) supersedes earlier
implementation assignments. The branch starts at accepted report snapshot
`2c02cc2713924140a82aefda37fd5885747e5837`, retaining published M04 predecessor
`fab6388b041acc4362f30b5ff7d3789a33fc536f`; main is unchanged. Scientific source
`424a859732b77b2f91cd03b12bb3f0b8adf3f541` passes **543 full CPU tests in606.45s**,
no skips. The [G09 v5 worker](../../Worker_Log/Milestone_05/Gate_09_v5_worker.md)
and [G10 v2 combined worker](../../Worker_Log/Milestone_05/Gate_10_v2_worker.md)
deliver64-water local controls (224/233 atoms), independent both-map full forces,
solvated offline/checkpoint/portable-State evidence, four-round persistent
pair-exchange pilots and complete sealed exports. The original CPU locks,
MACE bytes and S06 limits remain unchanged.

The user withdrew notebook delivery and external execution experiments. Their
tooling and obsolete assignments are removed; accepted CPU code, locks, model,
fixtures, reference ledgers and scientific evidence are retained. Historical
results below describe their exact reviewed snapshots, not new gate acceptance.

The [cleanup worker](../../Worker_Log/Documentation/Cloud_Engine_Continuation_v1_worker.md)
records **31 focused CPU passes in 117.17 s**, zero skips, and 8,391 retained
files matching the accepted base. No next-gate implementation is claimed.
The [independent cleanup audit](../../Worker_Log/Documentation/Cloud_Engine_Continuation_v1_audit.md)
accepts the administrative scope on `d600b0783060c0bfec96d5330f9b522d73de5ec4`
with no material findings; this is not a new gate or milestone acceptance.
The [orchestration update](../../Worker_Log/Documentation/Cloud_Engine_Orchestration_v1_worker.md)
requires serial Luna/max workers and Sol 6.1/max audits of completed task batches,
with the auditor finishing before repairs begin; see the current handoff.
The [G09 v5 audit](../../Worker_Log/Milestone_05/Gate_09_v5_audit.md) and
[G10 v2 combined audit](../../Worker_Log/Milestone_05/Gate_10_v2_audit.md) accept
the [new definition](specs/m05-dense-exchange-amendment.md) and declared CPU scope,
with52 independent passes,0skips and additional geometry/derivative/recovery probes.
No material findings or required repairs remain. The reduced stock OpenMM Reference artifact is reported;
engine/general runtime code is unchanged, with only synthetic fixture input
roundoff formatting. Full M05, molecular accuracy and M03 remain open.

**Bounded cloud solvent/exchange technical scope accepted; G09-R2 closed.**
On `m04-engine-readiness`, the [G09 v3 worker](../../Worker_Log/Milestone_05/Gate_09_v3_worker.md)
and [G10 v1 worker](../../Worker_Log/Milestone_05/Gate_10_v1_worker.md) add sparse
rigid TIP3P/orthorhombic PME controls (56/65 real atoms), live-box/full-map
guards, actual periodic worker export, two-map failure archives and one pinned
AToM pair-exchange boundary with fresh four-entry energies/state histories.
The [G09 v3 audit](../../Worker_Log/Milestone_05/Gate_09_v3_audit.md) accepts the
[scientific amendment](specs/cloud-solvent-control-amendment.md), and the
[G10 v1 audit](../../Worker_Log/Milestone_05/Gate_10_v1_audit.md) accepts the
bounded pair scope. Independent checks passed 28 affected tests and seven
probes; one contract probe exposed Important G09-R2: a secondary archive error
hid the scientific failure in the CLI. V3 source `5645db24f707adbdaff34dc7de6ac04b518d7d6b`
and all its evidence remain frozen; its 489-test result remains valid for that
submission. Both CLI water pilots saved nine frames/18 sampling steps,
preserved full real forces and boxes, with peak process RSS below 0.85 GiB.

The [G09 v4 worker](../../Worker_Log/Milestone_05/Gate_09_v4_worker.md) submits
repair source `027f8173babc13606afb24d96f58148704e38b1b`: primary provenance is
written first, each artifact is attempted independently, and secondary archive
errors are retained in metadata/exception notes and shown by the CLI. The
original exception is preserved without evaluation reentry/sample insertion.
Twelve new regressions first failed; 19 affected and **501 full CPU tests passed
in 498.74 s**, no skips. The [G09 v4 audit](../../Worker_Log/Milestone_05/Gate_09_v4_audit.md)
independently passes **21 focused checks and six additional probes**, verifies
all 49 source/input/regression hashes, and closes R2 on exact submission
`09a85d979fe9fce2ceca23da74509846254df9b1`. It accepts the bounded G09 subsets
and carries forward the unchanged G10 single-pair scope and scientific amendment.
Dense-solvent equilibration, persistent exchange/RNG/history supervision,
GPU, molecular accuracy and full G09/G10/M05 remain open. The
[historical handoff](handoffs/CLOUD-ENGINE-after-G09-v4.md) records the exact
source/submission, environment, saved attempts and remaining work. The
[v2 continuation](handoffs/CLOUD-ENGINE-after-G09-v2.md) stays frozen. This branch
continues published `m03-g06-g07` at
`fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86`; main and that predecessor remain
unchanged. The original [engine-readiness handoff](handoffs/ENGINE-READINESS-fresh-agent-v1.md)
remains a historical broader assignment. T4 lysozyme L99A and Slurm setup are reserved
for user-initiated HPC work. Cloud tests target numerical correctness and stable
bounded execution; MLIP physical accuracy remains unqualified.

**The bounded vacuum cloud technical scope is independently accepted; G09-R1 is closed.**
The [shared runner guide](../../examples/cloud_engine/README.md) covers one
manifest/settings path for 48-atom 18-crown-6/methanol, 32-atom capped ABFE and
41-atom unequal-ligand RBFE. It implements all-active phased preparation, actual
pinned worker PDB/System/State construction, full real-force/raw-state records,
same-profile checkpoint continuation, portable-State checks and relocated
offline resume. The [v1 worker](../../Worker_Log/Milestone_05/Gate_09_v1_worker.md)
and [v1 audit](../../Worker_Log/Milestone_05/Gate_09_v1_audit.md) remain frozen on
source `34cc6ba0d3e618450128b4a679ffc64046c48733`; their 22 independent affected
passes, 49 admission rejections and numerical oracles are carried forward
explicitly. The [v1 host pilot](../../Worker_Log/Milestone_05/evidence/G09_v1/host-pilot-diagnostics.json)
completed **60 frames/300 steps**, 0.05 ps per state, with finite full arrays,
both unchanged map guards passing and peak RSS about **0.94 GiB**.

The [v2 worker](../../Worker_Log/Milestone_05/Gate_09_v2_worker.md) submits repair
source `3246f0cbd6f66702e4b196bace593efba776a25e`, exact frozen submission
`9fe93357f0852d7c018ab41923cc0d58cb0615e1`. Guard, integration and final-State
failures now retain advanced State/checkpoint and attempted-record provenance
without reevaluating failed energy/forces or appending a failed sample. Root
full CPU verification passes **461 tests in 399.38 s**, no skips; a separate
fresh CLI smoke saves nine frames/18 steps with the same physical/alchemical
identities as v1. The strict restart oracle compares one identical prepared
bundle, preserving exact equality rather than mixing independent minimization
roundoff with checkpoint continuity.

The [actual GPT-6.1-sol/MAX v2 audit](../../Worker_Log/Milestone_05/Gate_09_v2_audit.md)
closes R1: **nine fresh affected passes**, the unchanged original reproducer
passes, and **six independent actual-worker prefix/failure challenges** verify
exact retention, provenance, unchanged committed samples and original errors.
All 111 scientific files, 507 retained artifacts and 8,150 submitted blobs
were independently verified. Acceptance covers partial G09-T2/T3 vacuum and
G10-T1/T3 worker/restart/offline/journal subsets. That vacuum-only audit did not
qualify solvent, exchange, GPU, equilibrium, molecular accuracy or full G09/G10/M05. No binding
estimate or new QM calculation ran; no blocker currently needs user help.

**G08 and combined M04 are accepted for the analytic CPU scope; G08-R1 is closed.**
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
admission with absent/uncomputed corrections. V1 evidence is frozen. The
[v2 worker](../../Worker_Log/Milestone_04/Gate_08_v2_worker.md) on source
`8cf2494424d796fc3fc393e25b00e05b6281a85f` binds final results to complete matching
definitions/ledgers, preserves legacy partial records, and passes **21 focused /
437 full CPU tests**. The actual
[GPT-6.1-sol/MAX v2 audit](../../Worker_Log/Milestone_04/Gate_08_v2_audit.md)
confirms 437 fresh full passes, 21 affected passes, 72 independent rejections and
23 positive round trips; it accepts the refined amendments and combined M04 on
exact submission `c0280818ad18fa5e95a022eccc892e2310a41721`. Molecular binding,
GPU and G07/M03 physical acceptance remain unqualified/open.

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

Continue the main engine on Codex Cloud using the
[current assignment](handoffs/CLOUD-ENGINE-CONTINUATION.md). First repair the
seven required findings from the [G10 v5 combined implementation audit](../../Worker_Log/Milestone_05/Gate_10_v5_audit.md)
as one bounded sequential batch, then obtain a new independent combined audit.
The standalone [G10 v3 design](../../Worker_Log/Milestone_05/Gate_10_v3_worker.md)
is **GREEN / accepted_for_scope** by the [Sol 6.1/max design audit](../../Worker_Log/Milestone_05/Gate_10_v3_audit.md)
on `678aa3e2db9d5f77517ad8cfb278ac8a4df7032d`; runtime implementation is complete
but its combined acceptance is RED / changes_required. This is G10-T2/T3 technical work, not a new
gate definition or full M05 acceptance. Then advance deterministic G11/G12 protein and dual-ligand
support and G13 packaging/resource measurements as their technical dependencies
are satisfied. Preserve the shared engine and accepted pair regression path.

Use existing tiny ABFE/RBFE controls and small serial CPU checks. The accepted
18-crown-6/methanol input is ABFE only; a methanol-to-ethanol host–guest RBFE input
still needs preparation and qualification. Expensive QM, equilibrated solvent,
long protein/production sampling and cluster settings are deferred to HPC.
G06/G07 numerical review remains accepted; G07-T4/M03 physical closure and full
M05 remain open. Preserve all accepted G05 data, seven sensitivity exceedances,
pilot force failures and the cumulative quantum ledger. The
[remaining-reference handoff](handoffs/G07-reference-remaining-v2.md) retains the
failed resource screen and safe continuation conditions. This cleanup does not
authorize a new QM budget or production continuation.

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
| M04 / G08 analytic thermodynamic accounting | accepted | [GPT-6.1-sol/MAX v2 audit](../../Worker_Log/Milestone_04/Gate_08_v2_audit.md), exact c0280818/source8cf2494; G08-R1 closed, refined amendments and combined M04 analytic CPU accepted; 437 full/21 affected passes |
| M05 / G09-G10 cloud technical subsets | accepted_for_scope / partial (full milestone); multistate changes_required | [G09 v5 audit](../../Worker_Log/Milestone_05/Gate_09_v5_audit.md) / [G10 v2 combined audit](../../Worker_Log/Milestone_05/Gate_10_v2_audit.md):543 full/52 independent CPU passes; denser/exchange/restart definition accepted; [G10 v3 standalone multistate design](../../Worker_Log/Milestone_05/Gate_10_v3_audit.md) GREEN on `678aa3e2db9d5f77517ad8cfb278ac8a4df7032d`; [G10 v5 combined implementation audit](../../Worker_Log/Milestone_05/Gate_10_v5_audit.md) RED on `edd587679aaa110ea687cca29b9e3aee70b7b6f0`, seven required repairs, 47 fresh independent pytest passes plus numerical/fault controls; full M05 open. Earlier lineage: [G09 v4 audit](../../Worker_Log/Milestone_05/Gate_09_v4_audit.md): R1/R2 closed, bounded explicit-water G09 subsets and unchanged G10 pair scope accepted; 501 root CPU passes, 21 independent focused passes/six probes; full M05 open |
| M06-M08 / G11-G13 | technical implementation pending / physical qualification deferred | Advance deterministic CPU engine support as relevant runtime prerequisites pass; reserve demanding protein calculations and Slurm settings for HPC; retain full-milestone qualification requirements |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model small-system chemical / protein qualification | accepted_for_scope / not_run | Sol 6.1/MAX v6 audit accepts neutral CPU G05 and all eight assertions; R1/R2/R3 closed. Protein qualification remains G07/later work. |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
