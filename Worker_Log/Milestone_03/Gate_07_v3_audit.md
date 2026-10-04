# G07 pilot validation-only repair — v3 independent audit

**Reviewed worker/snapshot:** [Gate_07_v2_worker.md](Gate_07_v2_worker.md), branch `m03-g06-g07`, source commit `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`, parent `daa1efa345e1ac2a756f1ff0442389eae862a0d6`. The actual quantum pilot ran earlier on `4e2cb06b0e5e0b3b081e379969428ec93a807866`.\
**Scope/profile:** execution validation and safe admission of the one already-computed pilot; offline CPU recovery. Numerical G06/G07 acceptance is inherited.\
**Reviewer and finished time:** independent GPT-6.1-sol / MAX, actual spawn configuration confirmed; 2026-10-04 12:29:53 UTC.\
**Verdict:** **accepted_for_scope** — concrete validation-only correction/admission, with no QM launch and no batch continuation.

## Reviewed identities

The frozen, working and committed hashes match exactly; [final-state.json](evidence/G07_v2_revalidation_independent/final-state.json) records all comparisons.

| File | SHA-256 |
|---|---|
| `tools/resume_joint_quantum.py` | `67372fbe9c8083aebfa77886240608fcadacba930a1d7c643d6ae9f11938f61f` |
| `tests/unit/test_joint_quantum_execution.py` | `094d71ada6f3382b9f3b872088a242526c8f903ffd4123c11a6f04aba9287f30` |
| `tools/resume_neutral_quantum.py` | `d7fd518d9663c60399e101c94c518f8f13b03625cff41e34546b96bfeae1e63d` |
| `tools/quantum_worker_guard.py` | `5dc02bb86f411bb62ab74e4a0f7579e9e54dafbf3b41ffa79be58f00b9e60030` |
| `tools/generate_neutral_quantum.py` | `f8555fd12670bd6a434c981297b9234de7dfaf6ca22738f88ea393de987cfeff` |
| Separate `authorization.json` | `fb20e06a6179df03ef6ced63cc09a4d1bdc74e024fc08cb5c5e301bd1079d216` |

The neutral coordinator, guard, generator and authorization remain unchanged from the accepted execution source. The [v2 audit](Gate_07_v2_audit.md) retains the exact launch-pinned SHA `79e9725654cdd5d8b3c315ddbee07f773121285f2ab9f0583ce511d3a758f9e8`. The subsequent pause note and [pilot handoff](evidence/G07_v2_execution_independent/pilot-review-handoff.md) remain separately preserved.

## Actual pilot and independent checks

The original `attempt-0001` receipt SHA is `b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f`; record SHA is `c1e34ea209bf4949c0f200859a75a35072ee5cf6e1750f8d7a9044a7259f0eed`. It exited 0 with reason null and verified whole-group cleanup. All frozen data and receipt-bound hashes passed. Its 32 gradient rows are finite. Psi4 1.10.2 explicitly says “Energy and wave function converged.” at line 295; final SCF energy change `1.14824e-11` and RMS commutator `5.77813e-11` are below the frozen `1e-10` limits. The original validation rejection came from requiring a different literal convergence message. The repaired parser accepts both explicit success messages and continues to reject missing convergence and the explicit failure message.

The ledger charged **2325.643222641 seconds**, leaving **23.353988 hours**. Peak sampled group RSS/HWM was **3.190 GiB**, conservative unreclaimable/dirty pressure **3.505 GiB**, scratch **9.015 GiB**, and minimum free disk **9.921 GiB**. Cgroup current reached 8 GiB and `max` events rose 220602, with zero OOM/OOM-kill/group-kill deltas; cache pressure is distinct from worker RSS. The source process group and private scratch are absent. Full measurements remain in [pilot-observations.json](evidence/G07_v2_execution_independent/pilot-observations.json).

After activating `/workspace/atom-mlmm-g07/activate.sh`, the auditor ran:

- `python -m pytest -q tests/unit/test_joint_quantum_execution.py`: **35 passed in 56.00 s**, exit 0; [log](evidence/G07_v2_revalidation_independent/adapter-durable-reviewed.log).
- [Independent isolated-copy probes](evidence/G07_v2_revalidation_independent/independent_revalidation_probes.py) on the exact retained repaired source: **42 named checks**, exit 0; [results](evidence/G07_v2_revalidation_independent/probe-results-durable.json). These cover failed exits/timeouts/resource stops/unrelated errors, changed receipt/data/log/order/launch/resources, malformed/nonfinite data, lease/live process/group/ledger rejection, edited correction measurements/markers/copied evidence/statements, six publication-loss boundaries, fsync ordering, idempotence, ordinary retry and normal promotion.
- [Rename-loss recovery probes](evidence/G07_v2_revalidation_independent/probe_repaired_rename_durability.py): both ordinary recovery and corrective replay sync the rename parent **before the first admitted checkpoint**, exit 0; [results](evidence/G07_v2_revalidation_independent/rename-durability-repaired-results.json).
- Read-only canonical authorization validation and exact-byte comparison of all **46 accepted G05 records** against base `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`: passed; [state](evidence/G07_v2_revalidation_independent/pre-admission-state.json).

All probes used isolated copies, made zero worker launches, and left the actual original attempt and ledger unchanged. A single harmless Python process was started and stopped solely to test live-process rejection. Successful copied-data recovery admitted one record, retained the original debit with only small coordinator-session additions, created no further attempts, and stopped at `pilot_assessment_pending`. Repeating it preserved correction receipt bytes and did not launch a worker.

The auditor inspected the worker's separately supervised full CPU regression: **416 passed in 272.69 s**, exit 0, no skips/deselections; supervisor wall 275.37985 s, peak process-tree RSS 1,758,347,264 bytes, and zero OOM deltas. [Recorded result](evidence/G07_v2/post-pilot-durable-revalidation-full-cpu-suite/result.json) and [test log](evidence/G07_v2/post-pilot-durable-revalidation-full-cpu-suite/command.log). The auditor ran no heavy model tests or QM. `git diff --check` passed. `python tools/check_docs.py` returned exit 0 with zero local-documentation errors; output is preserved in `documentation-validation.log` within the independent evidence directory.

## Findings and closure

The [retained changes-required findings](evidence/G07_v2_revalidation_independent/changes-required-findings.md) and reproductions preserve every earlier failure; prior evidence was not overwritten.

| Finding | Closure on the reviewed source |
|---|---|
| R1: edited correction wall/RSS could pass reuse and admission | The shared checker derives the entire corrected receipt and copied-file hashes from the pinned original; both entry points reject edits. |
| R2: removed correction markers could bypass that checker | Sidecar/receipt marker detection is unconditional; canonical reserved-path detection also binds the pinned original rejection. Removing both markers is rejected. |
| C1: reserved-path detection incorrectly rejected genuine second worker attempts | It now requires the original parser-rejection pin for reserved-path detection; a genuine retry after exit 23 passes ordinary validation. |
| R3: loss after rename could resume admission without durable parent entry | The shared checker syncs the correction directory and its parent before returning. Both recovery paths independently pass the interrupted-boundary checkpoint trace. |

No execution-safety finding remains open for this correction.

## Decision and handoff

The worker may apply **only `--revalidate-pilot`** under the original canonical authorization/output and exclusive queue lease, using the reviewed source. It copies the exact original evidence to a durably published validation-only `attempt-0002`, preserves the original rejection receipt, and admits the existing finite record through the maintained coordinator. No rerun, debit reset, changed approval, or batch continuation is accepted by this audit. At review completion the actual attempt still had **0/30 admitted**, no correction directory, and unchanged original/ledger hashes; actual admission and its resulting checkpoint must be recorded separately.

The reviewed 29-job remaining-time screen is **34.164590 hours**, exceeding **23.353988 hours** remaining. A continuation assessment cannot honestly pass under this budget. The optional cleanup inventory/strategy remains as recorded in the pause handoff; the auditor performed no deletion. Reclaimed disk space cannot remedy the time screen.

All **seven inherited physical sensitivity failures remain blocked**. G07-T4 and combined M03 physical closure remain unqualified. A subsequent single-contact force decomposition can provide limited arithmetic evidence; it cannot supply missing full-parent separated references or accept the physical gate. Numerical G06/G07 acceptance was not re-audited.
