# Cloud engine continuation cleanup — v1 worker

**Scope:** user-authorized removal of abandoned execution tooling, repository
onboarding correction and a prepared Codex Cloud engine continuation branch.\
**Outcome:** ready_for_audit; next gate implementation pending.\
**Finished:** 2026-10-05 UTC.\
**Snapshot:** `cloud-engine-continuation`; accepted base
`2c02cc2713924140a82aefda37fd5885747e5837`; cleanup source/documentation commit
`4f77c0599f0f05dc0e4fa35567074450c9dbfb46`. Subsequent worker/evidence changes are
reporting only. Main and published predecessor branches are unchanged.

## Changes

Removed both notebooks, their guide/tests, the isolated TPU profile, probe/module/
tests, three obsolete assignments and two execution-only planning/handoff logs.
The unreviewed cancelled notebook implementation was excluded by branching from
the accepted base. No engine, fixture, scientific limit, package lock, model or
reference-ledger change was taken from that work.

Updated README, AGENTS, DEVELOPMENT and STATUS to the
[current handoff](../../docs/project-0/handoffs/CLOUD-ENGINE-CONTINUATION.md).
Marked two older engine handoffs as historical. Removed only the optional
experiment section from the accepted amendment; its CPU scientific definition
is unchanged. Two historical worker/audit links now point to their exact Git
snapshot, preserving the original decisions and all other text. Scientific
audit/evidence records remain because they support accepted CPU engine results;
their historical external-execution references are not active instructions.
Original removed files and reports remain recoverable in Git history.

## Verification

From the repository root, science commands activated
`/workspace/m05-cpu-setup-v2/activate.sh` with
`OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. Main/Amber remain separate under
unchanged locks; that installation's earlier validation passed all nine checks.

| Check | Exact command | Observed result |
|---|---|---|
| Focused CPU export/exchange/restart | `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q --junitxml=/tmp/cloud-engine-cleanup-focused.xml` | **31 passed, 0 skipped, 117.17 s**, exit 0; actual pinned MACE/OpenMM solvent cases included |
| Preservation | `python Worker_Log/Documentation/evidence/Cloud_Engine_Continuation_v1/verify_preservation.py` | **8,391 retained files**, including 52 stored symlinks, match the accepted base; only the listed administrative exceptions; ledger SHA256 unchanged |
| Documentation | `python tools/check_docs.py --self-test` | Zero local-link/heading errors, all eight self-tests pass |
| Whitespace | `git diff --check` | Exit 0 |

Evidence: [focused JUnit](evidence/Cloud_Engine_Continuation_v1/focused.xml),
[preservation](evidence/Cloud_Engine_Continuation_v1/preservation.json),
[documentation](evidence/Cloud_Engine_Continuation_v1/documentation.json).
The full historical 543-test suite was not repeated for this removal-only task.
Its recorded acceptance remains tied to the original reviewed source; these
31 checks do not establish a new gate/milestone acceptance.

## Handoff

First proposed implementation is a reviewed G10-T2/T3 multi-state serial CPU
scheduler, preserving the accepted two-worker path. Follow with exchanging-walker
analysis and G11/G12/G13 technical work as dependencies pass. No scheduler or new
protein feature is implemented by this cleanup. Prepare/qualify the requested
18-crown-6 methanol-to-ethanol RBFE input when needed; only methanol ABFE is
currently accepted. Preserve G07 physical failures and the original QM budget;
demanding calculations and cluster settings are reserved for HPC. The independent
review, if completed, belongs in `Cloud_Engine_Continuation_v1_audit.md` and does
not retroactively approve the cancelled notebook branch.
