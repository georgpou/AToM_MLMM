# G10 v7 independent combined audit — durable pause

**PAUSED by the user's explicit checkpoint request, 2026-10-06 UTC.** No final
verdict or R1–R7 closure. Prior complete v5 decision remains RED. Root has frozen
source/tests/specifications/worker reports/artifacts and will start no repair or
other agent before the complete continued audit FINAL. Sole actual auditor:
`gpt-6.1-sol / max`, `/root/g10_combined_audit_v7`; no subagents.

Repository `/workspace/AToM_MLMM-g10`, branch `g10-engine-next`. Exact reviewed
HEAD `acfe9f6922d4029f1628aa69d530f0b642f4bb0d`; checkpoint commit is its report-only
descendant. Worker submission `883d5a8c5dbe4953d32fc0125c7c42b41d99db21`;
code/result `27e1639fefdde8ccca62263846204237391bf621`. Current production SHA-256:
`exchange.py` = `1d11414c3435119b485834698ecef4449df3b1418eab00763ecea960c904e095`;
`exchange_journal.py` = `3233d3a32d0c8b544d0eaba73dda8a8979c86d5de60d8067a78f8e4cf81e32e9`.
Full 38-file source inventory is in `identity-results.json`. Exact compact repair
diff raw SHA is `cba3d4f680908fd82d6989487f5b1e07c696acdd7bd5fca8584d3f46b3aa402c`.

Read the bounded [auditor instructions](../G10_v7_review_packet/auditor-instructions.md),
[v5 audit](../../Gate_10_v5_audit.md), completed [v6](../../Gate_10_v6_worker.md)
and [v7](../../Gate_10_v7_worker.md) worker reports and this checkpoint. Those
documents and relevant contracts/repair source have already been read. Avoid
repeating onboarding, accepted equations/force/probability/stationarity proofs,
the 626-test full suite or completed 53-test selection.

## Completed evidence and current process status

Exact commands, exits, UTC and raw hashes: `commands.jsonl`. All scientific
commands sourced `/workspace/m05-cpu-setup-v2/activate.sh` and exported
`OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`; serial two-CPU/8-GiB only.

| Check | Completed result |
| --- | --- |
| Focused repaired admission/runtime/transaction pytest selection | Exit 0; **53 passed, 0 skips, 44 deselected, 42.53 s**; `focused-pytest.log`. |
| Independent identity script | Exit 0; **31 hashes, eight current bundles × 38 source files**, complete manifests, exact two diffs, protected bytes, raw log identities; `identity-results.json`. |
| Extra inert NumPy cases | Three PASS: Boolean key, overflowing key, Boolean index; no trusted loader or output mutation; `repair-results.json`. |
| Broad repair script | Exit 1 at fourth case, **audit-harness serialization error**, 3.39 s; `repair-probe.log`. No later case ran. |
| Current molecular script | Drafted `molecular_probe.py`, **NOT RUN**. |

Both scientific exec sessions completed and were retrieved: focused session
30648 exit 0; repair session 6121 exit 1. Neither was terminated. At checkpoint
there is no active scientific process; old system zombie entries are not running
jobs. The process-check raw output and checkpoint verification are saved.

`/tmp/G10_v7_independent_artifacts` contains the fresh tiny prepared bundle,
one-boundary prefix (two declared boundaries), three completed challenge copies,
and the fourth `numpy-cache-nonfinite` clone, whose intended mutation did not get
written. There is no `reference` or later-case output. All 531 files are preserved
in `paused-analytic-artifacts.tar.gz` with a complete per-file SHA/size inventory
and verified extraction bytes in `paused-artifact-inventory.json`. No molecular
artifact was copied or changed. Current molecular originals are
`/workspace/G10_v7_artifacts/v7-attempt-001/{abfe,rbfe}`; old v5 bundles must never
be loaded under this new source.

## Completed coverage; all final assertion decisions remain pending

| R finding | Fresh completed coverage | Remaining independent work |
| --- | --- | --- |
| R1 | 33 inspected focused nodes; three additional NumPy rejection probes; valid 3/8 selection and Gaussian-cache regression | Complete remaining extra RNG/type/domain cases; checkpoint preserves every existing failure. |
| R2 | Seven focused actual checkpoint/portable, inert skipped/backward and gamma controls | Own zero-evaluation/zero-step loader watches including later worker and same-step shift; nonzero-origin arithmetic/domain review below. |
| R3 | Two energy-consistent focused map0 worker0/map1 worker2 rejections | Own complementary map0 worker2/map1 worker0 cases; record all guards before any evaluation/step/pending. |
| R4 | Two focused accepted/rejected +123 full-total contradictions | Current saved molecular same-attempt complete-matrix/refresh checks. |
| R5 | Five focused actual parent/report failures plus secondary capture regression | Own actual `os.fsync` faults, each derived writer, real checkpoint-open secondary error, all cached captures/no reentry/exact rebuild. |
| R6 | Focused traced publication/rollback ordering plus two parent-fault nodes above | Own actual fd syscall trace/faults for both publication and rollback parents; every file/nested directory before rename; exact replay. |
| R7 | Two focused added/modified nested manifest nodes | Own resealed nested manifest/extra-layout control; seal/symlink assertions inspected in source. |

C1/C4/C8/C9 and M3/M5/M6 have focused validator/identity/timeline/phase coverage,
but remain pending the independent probes. C2/C3/C7 and P1/P5 have source,
protected-tree and unchanged accepted proof reuse checked; no new final decision.
C5/C6 await independent transaction traces. P2/P3/P4 and M1/M2 await current
molecular records plus the unchanged protected numerical proofs. M4's accepted
pair-stationarity proof is reusable (protected equations/adapter); retain that
ordered composition does not imply whole-sweep detailed balance or mixing.
The final report must explicitly decide **every C1–C9/P1–P5/M1–M6** and all R1–R7.

## Unproven concerns and audit-harness correction

No new product counterexample has yet run to completion. Two code-inspection
hypotheses must be resolved before acceptance; do not implement provisional fixes:

1. `_validate_expected_clock` has no finite/nonnegative domain checks of its own,
   while sample/final-report validators require finite time but allow negative
   times. A consistently resealed negative timeline might reach loading. Determine
   the exact required absolute-clock domain and probe actual coherent clocks if
   this is material; do not mistake an isolated direct-helper misuse for a public
   admission failure.
2. With a finite nonnegative prior time `1e308 ps`, the sum inside the roundoff
   bound can overflow to infinity. A resealed prior State/checkpoint/report at
   that time followed by a normal later sample might then pass a huge backward
   elapsed time. This is **not yet executed**. The drafted inert probe sets the
   actual initial State/checkpoint clock without changing Snapshot/energy and
   reseals its chain; inspect that it reaches the intended timeline validator.

The actual harness failure: `numpy-cache-nonfinite` passed `float('inf')` to
production `write_json(... allow_nan=False)`, which failed before reader admission.
On continuation preserve this script/log version, then construct valid JSON
numeric overflow such as `1e309` by a deliberate raw JSON edit and reseal. Do not
weaken production serialization. Avoid blindly rerunning `repair_probe.py`:
its `ART.mkdir(exist_ok=False)` will fail, and fixed case paths already exist.
Load `repair-results.json` into `RESULTS`, skip the three completed cases, use
fresh unique paths for the fourth and later cases, and preserve all old bytes.
Prefer a small continuation driver importing the existing stages after repairing
the harness in a separately preserved script version; no repeated preparation or
completed probes are needed. Restore the archive under a new path only if the
original temporary tree is absent, verifying all inventory hashes first.

## Exact remaining launch pattern, after user resumes

From repository root, the existing recorder logs commands and statuses:

```bash
python Worker_Log/Milestone_05/evidence/G10_v7_independent/run_command.py repair-continuation 'source /workspace/m05-cpu-setup-v2/activate.sh && export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src" && python Worker_Log/Milestone_05/evidence/G10_v7_independent/repair_continuation.py'
python Worker_Log/Milestone_05/evidence/G10_v7_independent/run_command.py molecular-probe 'source /workspace/m05-cpu-setup-v2/activate.sh && export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src" && python Worker_Log/Milestone_05/evidence/G10_v7_independent/molecular_probe.py'
```

`repair_continuation.py` **does not exist yet**; create it as just described.
The molecular script is unexecuted and must be inspected for harness correctness;
it plans 18 fresh actual evaluations of current final/saved samples, no integration
or preparation, full-force/own-Snapshot/clock binding and pure-record all-matrix
arithmetic. It reuses unchanged accepted physics proofs, avoiding redundant
36-state reevaluation. Do not run identity_probe blindly after the report-only
checkpoint: its HEAD assertion is the original reviewed HEAD; compare source and
protected bytes against `identity-results.json` instead.

Finish every independent check and decision before the continued FINAL. Complete
the concise audit report, accurate STATUS, docs/whitespace/protected-byte checks,
audit-only commit and clean status; no push/reset/rebase/merge or source repair.
Preserve full G10/M05/physical/production/statistics exclusions: 46 G05 records,
seven G07 exceedances, original force failures, 29 missing references, charged QM
ledger `2325.6446500519996 / 86400 s`, continuation false;
`binding_result=not_evaluated`. This pause is a usage checkpoint, not acceptance.
