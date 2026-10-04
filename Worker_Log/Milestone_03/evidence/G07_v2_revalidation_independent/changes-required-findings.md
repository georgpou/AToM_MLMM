# Independent G07 pilot revalidation findings retained before final review

Reviewer runtime: GPT-6.1-sol / MAX, confirmed by the actual parent spawn configuration. Scope is execution safety for one validation-only correction, not numerical G06/G07 or combined M03 acceptance. All reproductions used isolated copies of the actual pilot. No auditor QM launch, original-attempt or canonical-ledger mutation, implementation edit, deletion, or commit occurred.

## R1 — correction receipt measurements were not checked during reuse

The paused adapter (`feab0c473f301432969c1ec4cd3c06ed93f57bb52bec7f5cd314c614a644acc6`, above source commit `4e2cb06b0e5e0b3b081e379969428ec93a807866`) accepted a corrected receipt with `wall_seconds` changed from 2325.623395559 to zero. Both direct revalidation and ordinary record validation/admission accepted it. The original source and canonical ledger remained unchanged.

Reproducer and result: `probe_initial_idempotence.py`, `initial-idempotence-results.json`, `initial-idempotence-case/`. The repair adds one shared checker deriving the full corrected receipt and every copied byte from the hash-pinned original. Final e0dcee probes reject altered wall/RSS, copied logs/identities/original receipt and altered correction statements through both entry points.

## R2 — correction classification must survive removed markers

Relying only on a removable receipt marker would let ordinary recovery avoid that shared checker. Root preserved a failing marker-removal test, then added sidecar and canonical reserved-path detection. Independent `probe-results-final.json` verifies removal of the receipt marker and removal of both receipt marker and sidecar fail closed. The latter retains the displaced sidecar in the audit fixture.

## C1 — reserved-path detection initially rejected genuine worker retries

The intermediate adapter (`e221904557f4e0294e1f31925f4d84da3af0898939591f036b03c629d6a0bbe9`) treated every canonical pilot `attempt-0002` as a correction, including a genuine second worker attempt after a first exit 23. Preserved reproducer: `reserved-ordinary-retry-case/`, `reserved-retry-results.json`. Root's full intermediate regression reproduced the failure (413 passed / 1 failed). The final reserved-path condition also requires the exact pinned original parser-rejection receipt; marker and sidecar checks remain unconditional. Independent final ordinary-second-worker validation passes.

## R3 — interrupted rename was not made durable before resumed admission

Source commit `daa1efa345e1ac2a756f1ff0442389eae862a0d6` (parent `4e2cb06b0e5e0b3b081e379969428ec93a807866`), adapter hash `e0dcee4054ae0ef0b8521918c9808b27b24bcadfbf7f8de3d97c6b17afcd1985`, fails the crash-after-rename boundary. The independent check injects coordinator loss immediately after `.revalidation-staging-v1` is renamed to `attempt-0002`, before the parent-directory fsync. The next ordinary `--revalidate-pilot` run validates that complete directory, promotes one record and durably checkpoints its provenance without ever syncing `jobs/PILOT`, the parent whose rename entry must be persisted. A power failure can therefore lose the referenced attempt directory despite the admitted checkpoint.

Reproducer: `probe_rename_recovery_durability.py`; detailed fsync/checkpoint trace: `rename-recovery-durability-case/result.json`. It records `parent_synced_before_admitted_checkpoint=false`, `parent_synced_at_all_on_resume=false`, zero worker calls, and exact unchanged canonical source/ledger hashes. The required repair must sync the correction directory's rename parent before reuse or checkpoint. Putting the guarantee in the shared checker also covers ordinary coordinator recovery without the revalidation option.

Decision for these snapshots: **changes_required**. R1/R2/C1 have been reproduced and their repairs verified on e0dcee; R3 must be repaired and checked on a newly frozen source before actual correction/admission. The reviewed 29-job 34.164590-hour remaining screen still exceeds the 23.353988-hour remaining budget, so this review cannot permit batch continuation. Seven inherited physical sensitivity failures remain blocked.

## Subsequent closure — 2026-10-04 12:28 UTC

All findings above are now closed on source `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`, adapter SHA `67372fbe9c8083aebfa77886240608fcadacba930a1d7c643d6ae9f11938f61f`, tests SHA `094d71ada6f3382b9f3b872088a242526c8f903ffd4123c11a6f04aba9287f30`. The shared correction checker syncs both target and rename parent before returning; independently injected rename loss followed by both corrective replay and ordinary recovery now syncs that parent before the admitted checkpoint. Evidence: `rename-durability-repaired-results.json`, the two `durable-rename-*-case/result.json` traces, 42-check `probe-results-durable.json`, and 35-pass `adapter-durable-reviewed.log`. The original changes-required decisions and reproductions above remain preserved. The separate final v3 audit accepts only no-QM correction/admission; budget and physical blocks remain unchanged.
