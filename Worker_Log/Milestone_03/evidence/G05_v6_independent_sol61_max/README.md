# G05 v6 independent GPT-6.1 Sol / MAX closure evidence

Canonical decision: [Gate_05_v6_audit.md](../../Gate_05_v6_audit.md). This is the narrow final R2 review by the continuing independent v4/v5 reviewer. No QM calculations, implementation, commits, publication or delegation occurred. All synthetic artifacts belong to this new exclusive directory; submitted science and earlier reviews are unchanged.

[audit-start.json](audit-start.json) identifies the initially clean tree, exact commits and source hashes. [final-state.json](final-state.json) records final invariance and the canonical complete v4 scientific-result digest. `run_check.py` preserves command receipts and logs exclusively. All scientific shells activated `/workspace/atom-mlmm-g05-v2/activate.sh` and set repository plus `src` on PYTHONPATH.

| Receipt and log | Purpose and outcome |
|---|---|
| [supervisor-loss-replay.json](supervisor-loss-replay.json), [log](supervisor-loss-replay.log) | Exact byte-identical independent v5 probe; **1 passed in 3.18 s** |
| [maintained-supervisor-loss.json](maintained-supervisor-loss.json), [log](maintained-supervisor-loss.log) | New maintained supervisor-loss regression; **1 passed in 3.14 s** |
| [cleanup-refusal.json](cleanup-refusal.json), [log](cleanup-refusal.log), [observations](cleanup-refusal-observed.json) | Already-reaped supervisor with persistent fake group: TERM/KILL, bounded virtual-time wait, refusal exception; no actual processes/signals |
| [preservation.json](preservation.json), [log](preservation.log), [observations](preservation-observed.json) | 46 QM hashes, 1,435 unchanged snapshot entries, scientific/history/source/model/reviewer subtree preservation and unchanged R1/R3 helper bodies |
| [final-docs.json](final-docs.json), [log](final-docs.log) | Documentation and self-tests after adding this review |

[Probe source](test_supervisor_loss.py) is copied byte-for-byte from v5; its existing `E=Path(__file__).resolve().parent` safely redirects every artifact into this directory. [Observed facts](supervisor-loss-probe/observed.json) show a real synthetic reference child killed before subsequent scheduling, exit -9 retained, successful group cleanup and no failed-job record promotion. The synthetic worker kills only its actual supervisor; the coordinator under review must clean its remaining group. The probe also cleans its own group in `finally`. None of the synthetic records enters chemical fixtures. The fixed-directory probe intentionally refuses a replay over existing artifacts; future replay must use a new directory.

[Bounded-refusal source](check_cleanup_refusal.py) substitutes a fake reaped process, signal recorder, persistent member enumeration and virtual clock only inside its own in-memory module. Its 5.01 seconds are simulated, not real wall time or an actual unkillable worker experiment. [Preservation source](check_preservation.py) performs byte, Git and AST checks without model/QM evaluation. Its `preserved_scientific_results_sha256` refers to the retained partial first v4 serialization artifact; the complete authoritative `scientific-results-v2.json` is independently bound in final-state.json, matching the v5 canonical digest. No earlier artifact was overwritten.

The prior [v4 science audit](../../Gate_05_v4_audit.md) and [v5 R1/R3 closure](../../Gate_05_v5_audit.md) are carried forward only after preservation checks. The final worker's actual 336-test/42-recovery/9-environment/doc executions were inspected, not claimed as fresh reviewer reruns. Acceptance remains limited to the fixed neutral nonperiodic CPU G05 profile. G06/G07 and broader qualification remain pending.
