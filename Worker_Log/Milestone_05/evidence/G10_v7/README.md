# G10 v7 evidence

The bounded runtime/durability worker starts from `bfbaa873cf13570313c945a9665f84580dde7439`; see [the worker report](../../Gate_10_v7_worker.md) for scope and outcomes. The v5 independent RED audit and original probes remain at [the audit](../../Gate_10_v5_audit.md) and [its evidence index](../G10_v5_independent/README.md).

| File | Evidence |
| --- | --- |
| `assignment-brief.md` | Saved bounded assignment and protected invariants. |
| `focused-red.log.gz`, `r6-red.log.gz` | Starting-source RED and corrected real-helper syscall RED. |
| `r6-harness-misassertion-red.log.gz`, `focused-green1/2.log.gz` | Preserved harness misassertion and interim failures; not product evidence. |
| `focused-green3.log.gz` | Final focused regressions: 16 passed, 44 deselected. |
| `fresh-v2-pilots.log.gz` | Fresh v2 ABFE224/RBFE233 pilots: 2 passed in 208.70 s. Attempt artifacts remain in `/workspace/G10_v7_artifacts/v7-attempt-001`. |
| `full-cpu-suite.log.gz` | One final CPU suite on the frozen combined source: exit 0, 626 passed, no skip text, 1221.89 s. |
| `docs-self-test.log`, `diff-check.log` | Documentation-link and whitespace checks. |
| `sha256sums.txt` | Digests for source, regressions, reports and retained result evidence. |

The final result commit is the source snapshot; the report/evidence commit follows it. No independent acceptance is claimed.
