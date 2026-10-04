# G08 v2 independent evidence — GPT-6.1-sol / MAX

Exact submission `c0280818ad18fa5e95a022eccc892e2310a41721`; tested source `8cf2494424d796fc3fc393e25b00e05b6281a85f`. The canonical [v2 audit](../../Gate_08_v2_audit.md) records G08-R1 closure and scoped G08/combined M04 acceptance.

- `snapshot_probe.py`, `snapshot-check.json`, `frozen-tracked-manifest.json`, `closing-preservation.json`: exact 83-file source/test manifest, 7,649 submitted Git blobs, ancestry, unchanged v1 evidence and final preservation checks.
- `admission_probe.py`, `admission-results.json`: independently authored 72 negative constructor/JSON cases and 23 positive round trips. Includes both original v1 admitted payloads, every missing/hidden obligation, identity/observable/arithmetic guards, ordered-ledger consistency, an additional declared obligation, deterministic and joint-covariance producer results, and actual v1 partial-result bytes/content identities.
- `command_runner.py`, `*.result.json`, `*.stdout`, `*.stderr`: command arguments, UTC timestamps, exit status, child maximum RSS and cgroup events. `full-cpu` passes 437 tests; `g08-focused` passes 21.

Unchanged numerical evidence is incorporated from [v1](../G08_v1_independent_sol61_max/README.md), without repeating unrelated scientific audits. Outside-repository pytest temporary trees are regenerable, and were not added as publication artifacts. All required commands completed successfully; no failed scientific samples were discarded and no submitted file was repaired by this reviewer.
