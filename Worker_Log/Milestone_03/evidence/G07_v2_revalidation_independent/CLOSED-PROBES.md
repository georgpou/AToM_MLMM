# Closed independent probe copies

The user's 2026-10-04 maintenance request authorized cleanup while preserving useful code, logs and scientific evidence. Only the two closed copied probe trees `probes-final/` and `probes-durable/` were replaced by lossless archives. Each contained 803 files; all original bytes are retained, including synthetic failure/partial cases. Top-level reviewer code, logs, results, source snapshots and actual canonical G07 execution/recovery data remain readable and unchanged.

| Original tree | Archive | Member manifest |
|---|---|---|
| `probes-final/` | [probes-final.tar.gz](probes-final.tar.gz) | [probes-final.archive.json](probes-final.archive.json) |
| `probes-durable/` | [probes-durable.tar.gz](probes-durable.tar.gz) | [probes-durable.archive.json](probes-durable.archive.json) |

The manifests record every original repository-relative path, kind, size, SHA-256, mode and original modification time, plus archive hash. Archive headers normalize ownership and timestamps; file contents are exact. Every decompressed member was compared with the original before unlinking the closed expanded copies. A fresh restoration into a private temporary directory is additionally checked in the [maintenance verification](../../../Documentation/evidence/Engine_Handoff_v1/verification.json).

To inspect a closed case, verify the archive's SHA-256 against its manifest, then extract into a new private directory:

```bash
mkdir /tmp/g07-closed-probes-review
tar -xzf Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent/probes-durable.tar.gz -C /tmp/g07-closed-probes-review
```

Run from repository root; the archive carries the full repository-relative prefix. Verify the needed restored files against the manifest before use. For the other tree substitute `probes-final.tar.gz`. Do not extract over canonical attempts or an existing review directory. Restoring the original repository locations for an old probe script requires inspecting existing work first; those scripts are historical fault-injection tools, not launch commands for the real queue.

The frozen G07 artifact manifest at the earlier submission still describes the original paths/bytes. Use this archive manifest to locate those bytes now, or inspect predecessor `fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86` in Git. No old audit or acceptance claim was rewritten. Canonical resumable G07 record/log/receipt paths are excluded from this archive operation.
