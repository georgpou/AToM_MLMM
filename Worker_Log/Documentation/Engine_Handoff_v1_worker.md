# Engine-readiness handoff and storage maintenance — v1 worker

**Scope:** successor-agent assignment, branch preparation and bounded maintenance; no new scientific implementation or calculations.\
**Outcome:** ready_for_handoff; maintenance and documentation verified. Remote publication is checked after the final commit.\
**Finished:** 2026-10-04 UTC; exact verification time is in the linked verification receipt.\
**Snapshot:** new `m04-engine-readiness` copied from published `m03-g06-g07` at `fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86`. Main is `2d7bcc94f901738e39f536f16de84699d4e8d631`. Scientific source remains the reviewed predecessor; this task changes reports and closed-copy storage only.

## Assignment and changes

The user explicitly redirected future work toward technical ML/MM engine readiness, subsequent gates/milestones and longer cluster trials, requested cleanup of nonrequired files, and requested a new branch copied from the predecessor. The [fresh-agent handoff](../../docs/project-0/handoffs/ENGINE-READINESS-fresh-agent-v1.md) implements that direction. It starts with G08 known-answer thermodynamics and proceeds to scoped preparation/export, restart/exchange and cluster preflight. Later full-gate and combined physical requirements remain explicit. STATUS points to the current assignment; two older handoffs are labeled superseded rather than erased.

The clean predecessor and its remote SHA were checked before branching. `git switch -c m04-engine-readiness` created the child in the existing `/workspace/AToM_MLMM` checkout. No extra worktree, reset, rebase, main edit or force-push was used. This task did not implement G08 or launch QM/production workers, and it did not reopen accepted numerical audits.

## Actual cleanup

The [one-off command](evidence/Engine_Handoff_v1/cleanup-command.py), [output](evidence/Engine_Handoff_v1/cleanup-command.log), [bounded deletion plan](evidence/Engine_Handoff_v1/deletion-plan.json), and [result](evidence/Engine_Handoff_v1/cleanup-result.json) record the operation. The command is a completed maintenance record, not a reusable QM launch/resume utility.

- Removed 328 compressed package downloads only after matching SHA-256 to installed package metadata; retained URLs, hashes and locks. Removed the verified Miniforge installer under its frozen SHA. Total download removal: **1,547,491,781 bytes**.
- Removed 105 ignored regenerable Python bytecode/pytest-cache files: **2,261,972 bytes**. No useful source or scientific log was deleted.
- Replaced two closed independent recovery-probe copies with lossless archives. Original content: **550,923,512 bytes / 1,606 files**; archive size: **20,613,592 bytes**. Every member's decompressed hash/size was checked before removal, preserving failed synthetic samples and partial cases. [Restoration instructions](../Milestone_03/evidence/G07_v2_revalidation_independent/CLOSED-PROBES.md) and complete member manifests are published alongside the archives. Top-level audit code/logs/results remain readable.
- Retained canonical G07 attempts, original/revalidated records, SCF logs, resource samples, receipts, authorization, assessment and cumulative ledger, all G05 data, active environments, extracted caches, model assets, locks, source and tests. The abandoned bootstrap prefix was conservatively retained.

Immediately after cleanup, **7,441 other tracked files had identical hashes** to the clean predecessor. Three later reporting-only edits are explicitly excluded from the final recheck. Active worker/installer/test scans found none; candidate file descriptors and active-prefix symlinks found no use. The process scan could not inspect file descriptors of two system Docker daemons; the other 118 entries were zombies, confirmed by a [follow-up](evidence/Engine_Handoff_v1/process-state-followup.json). Exact task-owned compressed downloads and closed copies were selected, not shared daemon storage.

Free disk increased from **19,707,158,528 to 21,790,773,248 bytes**: **2,083,614,720 bytes reclaimed**, or **1.941 GiB**. Measured headroom after cleanup was **20.294 GiB**. The machine still has two CPUs, 8 GiB RAM and no configured swap; cleanup does not enlarge anonymous RAM or reset quantum time. The reviewed largest-job scratch-plus-reserve projection remains greater than this headroom, and the remaining QM runtime screen remains above the existing allowance.

## Verification

| Check | Exact command / input | Observed outcome |
|---|---|---|
| Published predecessor and absent target branch | `git ls-remote origin refs/heads/m04-engine-readiness refs/heads/m03-g06-g07 refs/heads/main` | Target absent; G07 `fc6dbe3...`, main `2d7bcc9...`. |
| Bounded cleanup | `python /tmp/engine-handoff-cleanup.py > /tmp/engine-handoff-cleanup.log 2>&1`, repository root | Exit 0; per-file hashes and resource/deletion receipt saved. Exact command bytes copied to evidence. |
| Main/Amber environment after deletion | `source /workspace/atom-mlmm-g07/activate.sh` then `python environment/cloud-cpu/validate.py --root /workspace/atom-mlmm-g07 --repository /workspace/AToM_MLMM` | Exit 0; **9/9** checks pass, including inventories, pip consistency, OpenMM, potential/ATM smoke, separate Amber integration, upstream UWHAM and documentation. [Full results](evidence/Engine_Handoff_v1/post-cleanup-environment.json). |
| Fresh archive restoration and protected assets | `python Worker_Log/Documentation/evidence/Engine_Handoff_v1/verify-cleanup.py` | Exit 0; **1,606 files restored**, sizes/content/modes/base hashes match; **7,438** nonreporting retained base files unchanged. [Receipt](evidence/Engine_Handoff_v1/verification.json). |
| Final documentation | `python tools/check_docs.py --self-test --output Worker_Log/Documentation/evidence/Engine_Handoff_v1/final-docs.json` | Exit 0; **zero errors, eight self-tests pass**. |
| Reporting format | `git diff --check -- docs`; staged new handoff/maintenance documentation and command scripts also checked | Passed for the reporting/source scope; native scientific log formatting is preserved. |

The earlier **416-pass** full CPU suite is inherited evidence on unchanged scientific source, not a new run claimed by this maintenance task. No full numerical suite or independent scientific audit was repeated for report/archive-only changes. Fresh archive restoration, exact protected-file comparison and environment/documentation validation are the applicable new checks.

## Handoff

Deliver the published `m04-engine-readiness` branch and exact remote-verified SHA. The predecessor/main remain unchanged. The new agent's first implementation task is G08-T1, then G08-T2/T3, with necessary independent review by GPT-6.1-sol/MAX. Technical work proceeds with honest partial scopes while **29 G07 references, seven sensitivity failures and the pilot's additional physical force failures remain open**. Longer production and broad physical assessment are planned for the cluster after runtime/profile parity and the required cluster configuration are established.
