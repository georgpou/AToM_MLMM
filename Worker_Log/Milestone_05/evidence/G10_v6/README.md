# G10 v6 Task A evidence

This evidence records the bounded R1/R4/R7 implementation and inert clock
admission prerequisite. Starting HEAD is
`c27358668499ef596a73468936bc21279ebb1b6a`; code/result commit is
`8157b24ee93a841dbf91cf10a02a19dd321e6c88`. The untouched-source focused RED
run is preserved alongside the repaired-source and compatibility outputs.
[`Gate_10_v6_worker.md`](../../Gate_10_v6_worker.md) records scope, root causes,
commands, counts, and the remaining R2/R3/R5/R6 work.

| Evidence | Meaning |
| --- | --- |
| `focused-red-baseline.log.gz`, `focused-red-baseline-results.json` | Tests-first RED: 34 failures, 3 passes; 34 recorded violations reach the loader spy on the untouched source. The gzip log preserves the exact raw bytes. |
| `focused-green.log`, `focused-green-results.json` | Full focused module: 37 passes; all 36 challenge entries PASS and 0 VIOLATION. |
| `r1-green.*`, `r4-green.*`, `r7-green.*` | Per-finding repaired-source results. |
| `compatibility.log` | Retained four-module compatibility command: 74 passes, zero skips. |
| `docs-self-test.log`, `diff-check.log` | Required documentation and whitespace checks. |
| `focused-red-harness-check.log.gz`, `focused-red-assertion-check.log.gz` | Retained harness-only attempts; not finding evidence. The gzip files preserve exact raw bytes. |
| `diff-check.log.gz`, `diff-check.log` | Exact first whitespace-check output and final clean staged diff check. |

SHA-256 digests for the code, regression, report, status, and retained result
files are listed in [`sha256sums.txt`](sha256sums.txt). All JSON results include
the challenge artifact hashes, loader-call records, and before/after tree hashes.
