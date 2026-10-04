# G07 reference execution safety — v2 independent audit

**Scope:** execution safety for the frozen 30 new G07 reference jobs; no numerical re-audit and no combined M03 review.  
**Branch/base:** `m03-g06-g07`, `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`.  
**Reviewed snapshot:** [execution-source-snapshot-initial.json](execution-source-snapshot-initial.json), uncommitted adapter/policy/tests and the separate authorization.  
**Reviewer:** independent GPT-6.1-sol, MAX reasoning; parent confirmed actual spawn arguments `model=gpt-6.1-sol`, `reasoning_effort=max`, `fork_turns=none`. No delegated reviewer.  
**Initial finding preservation:** 2026-10-04 UTC; exact times are recorded in the linked command and probe artifacts.  
**Initial verdict:** **changes_required**. No actual Psi4 calculation was launched. A repair snapshot requires a fresh check before launch.

Numerical G06/G07 acceptance is inherited from the accepted v1 audit. The seven physical force-sensitivity failures remain blocked, G07-T4 remains unqualified, and this execution audit cannot accept the physical profile or combined M03.

## Frozen source and checks

[snapshot-check-initial.json](snapshot-check-initial.json) independently verifies all six submitted hashes and the exact base. It also verifies that `quantum_worker_guard.py` and `generate_neutral_quantum.py` remain byte-identical to the base. Original reviewed bytes are retained under `reviewed-source-initial/` so later repair cannot alter these reproductions.

| Reviewed file | SHA-256 |
|---|---|
| `tools/resume_joint_quantum.py` | `5dd094c17cc652900b1c8e905a5ad4417e2ef6824954379ff610360f701e4d0b` |
| `tools/resume_neutral_quantum.py` | `204b60b83c41d9e453b44d9a9bee7d669e82772cf328c567f1d65a0562ccfcb5` |
| `tools/quantum_worker_guard.py` | `5dc02bb86f411bb62ab74e4a0f7579e9e54dafbf3b41ffa79be58f00b9e60030` |
| `tools/generate_neutral_quantum.py` | `f8555fd12670bd6a434c981297b9234de7dfaf6ca22738f88ea393de987cfeff` |
| `tests/unit/test_joint_quantum_execution.py` | `a729e49c5a5a45c54c4aa3255830570094bf11a4c3cb2da8f5f9e1815e6c6970` |
| `Worker_Log/Milestone_03/evidence/G07_v2/authorization.json` | `fb20e06a6179df03ef6ced63cc09a4d1bdc74e024fc08cb5c5e301bd1079d216` |

After activating `/workspace/atom-mlmm-g07/activate.sh`, the maintained lightweight adapter suite passed **16 tests in 8.37 s, exit 0**. Exact invocation/output are in [pytest-initial-command.json](pytest-initial-command.json) and [pytest-initial.txt](pytest-initial.txt). These tests cover frozen queue/pilot order, rebound-matrix rejection, invalid authorization, failed-exit handling, cumulative retry/timeout debit, lease contention, pilot pause, missing initial convergence, and synthetic RSS/disk/OOM stops. They supply execution software evidence only.

The independently authored [independent_execution_probes.py](independent_execution_probes.py) runs retained original source and replaces only the executable boundary with a standard-library stand-in. [independent-probes-initial.json](independent-probes-initial.json) preserves results and every command/attempt/receipt beneath `probes-initial/`. No engine/model is imported or launched by the stand-in.

The independent crash probe kills the coordinator after a TERM-resistant stand-in begins. The inherited lease remains held after coordinator loss, all live group members are gone before recovery, and the interrupted interval is conservatively charged (**5.181686 s**, total subsequent debit **6.197442354 s**). Computed records from a worker exiting 23 are not promoted; retry retains its receipt and increases cumulative debit. Initial absent/nonconverged logs are rejected. Hash substitutions in the pilot assessment for the matrix, record or receipt are rejected, as recorded in [assessment-probes-initial.json](assessment-probes-initial.json).

## Findings requiring repair

| Finding | Evidence/location | Required closure |
|---|---|---|
| **G07-E1, execution blocker: supplied authorization can select a fresh ledger and lease.** | `resume_joint_quantum.py:19–21,116–133` validates the content of any supplied JSON but does not bind it to the actually recorded approval artifact. The independent probe copies that artifact, changes only `attempt_path`, and successfully promotes the pilot in a second output. The first attempt debits **1.272983832 s** at a timeout; the second independently debits **1.015092161 s**. Lease identity also changes with the approval parent. | Bind execution to the exact canonical approved artifact/hash and exact approved attempt/lease identity. Reject a copied/rebound approval or another output before directory creation/launch. Preserve cumulative state across retries; test the original bypass against the repaired snapshot. |
| **G07-E2, execution blocker: admitted checkpoints can survive loss of explicit convergence evidence.** | `validate_joint_record` at `resume_joint_quantum.py:59–71` permits an absent log when `expected_sha` is supplied. The receipt does not hash the convergence log and the coordinator does not fsync it before checkpoint admission. Removing the source pilot log after admission allows ordinary resume to retain the pilot and return `pilot_assessment_pending`, exit 1. | Make the actual convergence evidence durable and hash-bound before receipt/checkpoint admission, then require the unchanged evidence on recovery and continuation. Published record validation must still distinguish source evidence from copied record location. Test missing/changed convergence logs after a completed checkpoint, including repair of a lost promoted copy. |

Two additional observations are preserved for the repair review. `--check-resume` reports a fresh 86,400 s budget and all 30 jobs even when an existing ledger has charged time; it must not be used as the actual continuation-budget assessment. The assessment validator accepts zero runtime/RSS/scratch projections with no measured fields beyond receipt identity. Those projections are insufficient evidence for the authorized measured feasibility decision; any continuation assessment must identify and actually use the pilot measurements, resources, convergence and remaining cumulative envelope.

## Decision and handoff

The submitted initial snapshot is **not accepted for launch**. Repair E1/E2, freeze exact new source, and rerun the reproductions plus affected lightweight recovery checks. Any eventual acceptance will authorize the execution mechanism only: one worker, two threads, 3 GiB internal allocation, 6 GiB maximum group RSS, 5 GiB minimum disk free, one-hour cumulative pilot inside the cumulative 24-hour batch ceiling, a measured hash-bound pause before continuation, and the exact 20 full-parent plus ten alternative-cap jobs. All 46 accepted G05 records, including the 20 exact reused baselines, must remain unchanged.
