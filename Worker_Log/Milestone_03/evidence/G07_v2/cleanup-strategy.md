# G07 cleanup and memory recovery

The user's 2026-10-04 follow-up authorizes identifying safe cleanup and archiving options while preserving code, logs and essential program assets. Cleanup must preserve the scientific record and the same cumulative execution ledger. The inventory in [cleanup-candidate-inventory.json](cleanup-candidate-inventory.json) records actual paths and sizes; it is an inventory, not a deletion receipt.

## Memory problems

Disk cleanup does not solve excessive anonymous worker RAM. The worker guard must first stop and verify the entire supervised process group if its RSS exceeds 6 GiB, an OOM event occurs, or the conservative pressure guard is exceeded. Keep the failed receipt, partial SCF output, one-second resource samples, input order, worker identities and charged wall time. Never remove an open scratch file or compress a live log to try to keep a worker running.

Use `memory.stat`, process-group RSS and OOM-event deltas to distinguish reclaimable file cache from worker memory. Cgroup total usage near 8 GiB, or increases in its `max` counter, do not by themselves establish an OOM. The kernel can reclaim clean file cache. No privileged cache-dropping operation is needed. If exact settings exceed the verified RSS envelope, checkpoint and report the measured requirement; the remedy is an explicitly reviewed larger machine/resource profile, retaining the frozen scientific settings and accumulated budget.

## Safe removal after each attempt

The maintained coordinator removes only the attempt's private `scratch/` directory after whole-group cleanup, validation where possible, durable diagnostics and its completion receipt. This applies to successful and failed attempts. Scratch contains recomputable Psi4 integral intermediates and temporary wavefunction files; it is not a restart checkpoint supported by this queue. Interrupted or failed calculations remain incomplete, and their charged time is retained. Verify the recorded supervisor group and matching attempt processes are absent before manual recovery cleanup. Preserve any required diagnostics outside `scratch/` first.

Keep every `record.json`, `order.json`, `launch.json`, `receipt.json`, worker identity, SCF/launcher log, `resources.jsonl`, `progress.json`, provenance/hash manifest and failure artifact. Keep source and published companion logs. The resume validator checks their exact paths and bytes. Do not delete an entire attempt directory, even if it failed. Do not remove another attempt's scratch or historical evidence.

## Installation files that can be reclaimed if disk headroom requires it

The closed package-download archives listed in the inventory total **1,422,977,620 bytes (1.325 GiB), 328 files**. After installation and locked artifact verification, these `.conda` and `.tar.bz2` downloads can be removed individually from the task-owned download cache. Preserve their package URLs/hashes, explicit locks and installation diagnostics. Do not remove extracted cache trees, cache locks, active environment prefixes or dependencies reached through hardlinks/symlinks. Package archives are already compressed; zipping them adds little value.

The verified Miniforge installer is another reconstructible download (approximately 119 MB). Preserve its version, SHA-256 and successful/failed bootstrap logs before removing that exact file. The abandoned first bootstrap prefix is approximately 533 MB; it is a candidate only after confirming that no activation script, active prefix, process executable, open file or symlink uses it and that the failed-install diagnostics are preserved. It must not be confused with the successful `conda`, `reference-env`, main or Amber prefix.

Use a path-specific manifest with pre-removal size/hash, reason, process-use checks and post-removal free space for any deletion. Avoid blanket `git clean`, `rm -rf` over evidence/environment roots, or `mamba clean --all`. Cleanup cannot silently loosen the 5 GiB free-disk guard or a time budget.

## Lossless archival after collecting the data

Closed, unreferenced installation/test logs may be stored as deterministic gzip files with SHA-256 values for both original and compressed bytes and a decompression round-trip check. Existing installation logs already use this approach. Scientific logs and one-second samples remain readable at their original paths while the G07 queue is resumable: replacing them with compressed-only files would break completion-receipt validation.

After all required data and audits are collected, a lossless archive may include complete records, inputs, logs, samples, receipts, checkpoints and a path/hash manifest. Verify the archive can reproduce every original byte before publishing it. Retain the originals needed by the live queue unless a separately reviewed restoration path is supplied. An archive copy is useful for transfer; it is not permission to discard scientific logs or provenance.

Repository code, tests, frozen fixtures, all 46 accepted G05 records, model weights/manifests, settings/locks, active environments and scientific evidence are essential and excluded from cleanup. This attempt's actual cleanup outcome and any safely reclaimed bytes are recorded in the worker report and final verification, rather than inferred from this strategy.
