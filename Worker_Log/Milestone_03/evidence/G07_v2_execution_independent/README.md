# Independent G07 v2 execution safety evidence

Reviewer: actual GPT-6.1-sol / MAX, fresh isolated subagent context, no delegated reviewer. Scope is execution safety only; no numerical G06/G07 re-audit, actual QM or heavy model run.

The final decision is [Gate_07_v2_audit.md](../../Gate_07_v2_audit.md). Initial findings remain in [initial-changes-required-audit.md](initial-changes-required-audit.md). Review base is `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`; accepted source commit is `4e2cb06b0e5e0b3b081e379969428ec93a807866`.

| Artifact | Purpose |
|---|---|
| [snapshot-check-initial.json](snapshot-check-initial.json), [initial snapshot](execution-source-snapshot-initial.json) | Exact six original hashes and base; original code is preserved in `reviewed-source-initial/`. |
| [initial independent probes](independent-probes-initial.json) | Reproduced copied-approval budget/lease reset and lost-convergence-log recovery, plus safe failed-exit/retry and coordinator-loss behavior. |
| [initial assessment checks](assessment-probes-initial.json), [supplemental initial checks](supplemental-probes-initial.json) | Assessment identity checks/zero-projection hole, independent matrix tamper, cumulative pilot ceiling and empty system swap configuration. |
| [repaired snapshot check](snapshot-check-repaired.json), [repaired snapshot](execution-source-snapshot-repaired.json) | Exact repaired hashes at freeze; code preserved in `reviewed-source-repaired/`. |
| [repaired test command](pytest-repaired-command.json), [repaired output](pytest-repaired.txt) | Fresh 64-case adapter/recovery/interruption run, exit 0, 138.15 s. |
| [repaired independent probes](independent-probes-repaired.json) | Production approval/output rejection, durability ordering, evidence tamper, measured assessment bounds, exact30-job synthetic continuation/reuse, cumulative ceilings and coordinator loss. |
| [accepted record preservation](accepted-record-preservation.json), [actual resources](actual-resources-initial.json) | All46 accepted G05 records and20 reused baselines remain exact; observed actual cgroup and disk. |
| [final-state.json](final-state.json) | Working/committed hashes at exact accepted source commit, base, unchanged accepted records, and absence of actual approved attempt. |

All executions activated `/workspace/atom-mlmm-g07/activate.sh`. The independently authored commands were:

```bash
python Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/independent_execution_probes.py
python Worker_Log/Milestone_03/evidence/G07_v2_execution_independent/repaired_execution_probes.py
```

The probe scripts create unused case directories; their completed case directories preserve orders, launches, synthetic outputs, receipts, resources and exact subprocess command/result lines. To rerun, preserve the existing case directories first and select a new copy/directory rather than overwriting them. Synthetic records are **not chemical evidence** and must never be imported as references.

The repaired script substitutes its audit authorization path/hash only inside a test-process harness and substitutes only the reference executable boundary. Production source has no synthetic test switch. Its real production CLI checks use the exact real authorization and perform read-only preflight/rejection only. `durability-events.json` within the repaired pilot case preserves the independent fsync-before-checkpoint observations.

No repository implementation, scientific input, model, lock, threshold, accepted record, branch, commit or remote was changed by this auditor. Worker-provided full-suite403-pass evidence was inspected separately; the auditor's own fresh test evidence is the lightweight64-case run.
