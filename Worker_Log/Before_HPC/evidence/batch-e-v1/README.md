# Batch E evidence index

This directory records the Batch E red/fix checks, final focused tests, package wheel build/install, successful fresh-process CLI paths, benchmark input/receipt, validated local bundle, exact approved asset identities, and dry-run HPC profile result. Failed logs are retained beside their corrected runs; no log was overwritten.

The parent-owned consolidated `python -m pytest -q` run started at 15:09:16 UTC and ended at 15:22:42 UTC after 806.469 seconds with exit `-9`, six failure markers, and no final pytest summary. The recorded cgroup peak was 8,592,265,216 bytes with `oom_kill=1`, consistent with the 8 GiB memory limit. This is an interrupted, unresolved validation attempt and is not a full-suite pass. The parent is collecting affected test names and running bounded diagnostics.

Key final receipts:

- `focused-core-committed-001.log`: 31 focused tests, zero skips, code commit `b3504f09e224b6f8fc636615ec3284e9326c6d45`, tree `97a88372e4edafba6d3e7ee8ab8202117578c00c`.
- `focused-machine-data-final-001.log`: final support/requirement matrix and HPC template checks, 7 passed, zero skips.
- `installed-fresh-worker-002.log`: final wheel installed from the local bundle in a venv derived from the validated CPU environment; `PYTHONPATH` unset, network blocked, exact asset hashes, fresh worker manifest `b63044c4ca9dcfe1d2f126c2e5bc861af869ac09fa804ce097c0e1ca221821f3`.
- `benchmark-receipt-final-001.json`: five serial CPU processes, exact source/input/model/profile identities and per-process timing/RSS.
- `release-bundle-final-003-manifest.json`: final verified local bundle manifest; SHA-256 `d1e917fe4b6db41c7f1ff7727248a1b92c0fb5f7210c2db95ce649a1e44930d6`.
- `local-hpc-driver-dryrun-001.log`: bounded driver default and held HPC template output; no hidden suite or scheduler submission.

The bundle at `/tmp/atom-mlmm-batch-e-release-bundle-003` is local and hash-verified. It explicitly does not claim a complete offline dependency reinstall. The complete worker report and scope limits are in `../Batch_E_v1_worker.md`.
