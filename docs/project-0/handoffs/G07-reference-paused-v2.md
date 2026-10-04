# Resume the paused G07 reference continuation

The user requested a graceful stop on **2026-10-04**, because the session's five-hour quota was nearly exhausted. This pause does not reset or extend either quantum budget. Continue only when the user resumes this thread.

## Exact checkout and preserved state

- Repository: `/workspace/AToM_MLMM`, branch **`m03-g06-g07`**, tracking `origin/m03-g06-g07`. The requested named worktree was absent. Do not create a child branch, duplicate branch or separate worktree; do not reset, rebase, force-push or touch main.
- Published starting commit: `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`. Reviewed execution source: `4e2cb06b0e5e0b3b081e379969428ec93a807866`, its direct child. The pause commit also carries explicitly unfinished validation repairs; it is not a newly accepted execution snapshot.
- Actual quantum ledger: `Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1/progress.json`. **2,325.643222641 seconds charged**, **84,074.356777359 seconds remaining** of the cumulative 86,400-second batch cap. Pilot cap is 3,600 cumulative seconds, so only 1,274.356777359 seconds remain for another pilot worker; a repeat of the measured calculation would not fit. Do not rerun it.
- Separate authorization: `Worker_Log/Milestone_03/evidence/G07_v2/authorization.json`, SHA-256 `fb20e06a6179df03ef6ced63cc09a4d1bdc74e024fc08cb5c5e301bd1079d216`. Keep this exact binding and ledger. Matrix remains frozen, including its historical authorization false.
- All 46 accepted G05 records, all frozen scientific inputs/settings/locks/model assets and previous numerical evidence remain unchanged. Matrix reuse covers 20 exact G05 baseline records; no G05 worker was launched.

## Pilot result and the admission defect

One actual QM worker ran: `ethanol-methanol-d3-r0--full-parent`, under `jobs/ethanol-methanol-d3-r0--full-parent/attempt-0001/` in the ledger directory. It exited **0** after **2,325.623395559 seconds**, with energy **−726.579702009341 Hartree** and **32 finite gradient rows**. Psi4 explicitly says **`Energy and wave function converged.`** at line 295. Final iteration 18 has energy change `1.14824e-11` and RMS residual `5.77813e-11`, both below the frozen `1e-10` criteria.

The original G07 admission check incorrectly required the literal `SCF has converged.`. Its immutable receipt records the parser error despite the successful computation. Therefore **one record is computed, zero are queue-admitted, and 29 jobs have never run**. The queue still reports 30 incomplete jobs. Preserve that distinction until reviewed revalidation closes the defect.

- Record SHA-256: `c1e34ea209bf4949c0f200859a75a35072ee5cf6e1750f8d7a9044a7259f0eed`.
- Original rejection receipt SHA-256: `b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f`.
- Worker group 23384 and all matching actual attempt processes are absent. Receipt confirms whole-group cleanup. Private scratch was removed only after durable diagnostics/receipt. **No actual `attempt-0002` exists and no validation correction has been applied.**
- Peak group RSS **3,425,435,648 bytes (3.190 GiB)**; peak scratch **9,679,518,016 bytes (9.015 GiB)**; minimum free disk **10,652,585,984 bytes (9.921 GiB)**. OOM/OOM-kill deltas were zero. Cgroup usage reached 8 GiB because of reclaimable file cache; this was not an observed OOM.

The independent GPT-6.1-sol/MAX reviewer checked the actual pilot and found a parser defect, rather than failed SCF. Its original [execution audit](../../../Worker_Log/Milestone_03/Gate_07_v2_audit.md) accepts source `4e2cb06` only. Any pilot addendum is separate and does not accept the unfinished repair or physical G07/M03.

## Unfinished repair: verify before using it

The pause snapshot preserves changes to `tools/resume_joint_quantum.py` and `tests/unit/test_joint_quantum_execution.py`:

1. Accept both exact affirmative convergence messages. A meaningful new RED test reproduced the actual rejection; the two focused affirmative/negative checks then passed.
2. Add `--revalidate-pilot`, pinned to this exact original rejection receipt. Proposed behavior validates the canonical authorization/ledger, environment, exact record and diagnostics, absence of live workers/group, and the specific zero-exit parser error. Under the exclusive lease it durably copies original evidence into a validation-only `attempt-0002`, preserving the original receipt and recording that inputs/launch/identities/time are historical copies. Atomic directory publication precedes normal coordinator recovery/admission. It never launches QM or resets/debits the original computation again.

The reviewer approved this design **in principle**, subject to reviewing the concrete implementation. The new unit run was interrupted on the user's stop request: **26 passed in 46.97 seconds; exit 2 / KeyboardInterrupt**. This is an incomplete verification run, not full acceptance. New RED, focused GREEN and interrupted output are preserved in `evidence/G07_v2/`. The earlier accepted source separately passed 403 full CPU tests and 64 independent affected/recovery tests; those results cannot be attributed to this new code.

On resume, inspect local changes and current HEAD before any update. Verify preserved source hashes in [pause-state.json](../../../Worker_Log/Milestone_03/evidence/G07_v2/pause-state.json). Finish meaningful tests of correction durability, idempotence, evidence tamper rejection, lease/live-process refusal, original receipt preservation, unchanged debit and no QM launch. Run the affected suite and full available CPU regression, then request GPT-6.1-sol at MAX reasoning to audit the exact repair snapshot. Do not overwrite either original receipt or the prior audit. No additional user approval is needed for the previously authorized safe repair, tests or normal publication.

Only after that review may the existing reference activation and the exact canonical CLI be used with `--revalidate-pilot`; omit `--continue-batch`. Confirm that it admits one existing record without another scientific worker, keeps the original receipt unchanged, and carries the same ledger. If the repair is inadequate, preserve it as unfinished and correct it through further RED/GREEN tests; do not bypass receipt checks manually.

## Batch constraint and physical interpretation

The reviewed conservative runtime screen projects **122,992.524584 seconds (34.1646 h)** for the remaining 29 jobs, versus **84,074.356777 seconds (23.3540 h)** remaining. Remaining job runtimes are unmeasured; this is a screening estimate, not proof of exact future duration. It nevertheless fails the current adapter's reviewed continuation envelope. **Do not launch the batch, silently weaken the screen or extend/reset the budget.** Prepare a hash-bound pilot assessment with continuation false and report the concrete resource/budget constraint. Largest frozen basis/auxiliary sizes also forecast substantially larger scratch, so review the separate basis-sizing evidence and available disk.

No complete contact-minus-separated full-parent QM comparison exists: the pilot's separated counterpart and other new descriptions are missing. Do not compare unlike absolute composition energies. Preserve the distinction between MACE-versus-QM on the same cap and cap/retained-MM-versus-complete-parent QM. Project any artificial-cap force onto both real parents exactly once and retain every real MM force. All seven prior sensitivity exceedances and all controls remain unchanged; G07-T4 and M03 physical acceptance remain blocked. Do not start M04/G08.

## Environment and cleanup

If this machine persists, activate reference with `source /workspace/atom-mlmm-g07/activate-reference.sh`, then set `PYTHONPATH=/workspace/AToM_MLMM/src` for scientific CLI use. Main testing uses `source /workspace/atom-mlmm-g07/activate.sh`; keep Amber separate. Actual profile is two CPUs, 8 GiB RAM, no swap; reference is exactly Psi4 1.10.2 / LibXC 7.0.0 and all 105 locked packages. If the machine is replaced, inspect its quota/RAM/swap/disk/network first and rebuild from the unchanged locks, preserving the same saved ledger and authorization binding rather than creating a fresh budget.

Read [the cleanup strategy](../../../Worker_Log/Milestone_03/evidence/G07_v2/cleanup-strategy.md) and inventory. The successful pilot's temporary scratch is gone. No package caches, code, logs, fixtures, accepted records, model assets or environments were deleted. Approximately 1.325 GiB of task-owned package-download archives are potential disk recovery candidates; archive/delete only exact verified candidates if needed. Keep live resume log/resource paths uncompressed; lossless archive copies are allowed after closure and hash/round-trip verification. Deleting disk files does not solve excessive anonymous worker RAM.

Finish the worker report, STATUS, actual pilot assessment and necessary independent audit after resuming; commit and normal-push only this branch and verify the remote SHA. This handoff supersedes the old M04/G08 recommendation.
