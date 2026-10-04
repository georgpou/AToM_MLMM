# Independent pilot revalidation evidence

Reviewer runtime: GPT-6.1-sol / MAX. Final scoped decision: [Gate_07_v3_audit.md](../../Gate_07_v3_audit.md), source `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`.

- `source-check-initial.json`, `pause-state-preserved.json`, `source-initial/`: exact resumed inputs and original/ledger hashes.
- `probe_initial_idempotence.py`, `initial-idempotence-results.json`, `initial-idempotence-case/`: reproduced acceptance of edited correction measurements before repair.
- `source-repaired/`, `source-snapshot-repaired.json`, `reserved-retry-results.json`, `reserved-ordinary-retry-case/`: intermediate source and genuine-retry regression evidence.
- `source-final/`, `source-snapshot-final.json`, `probe-results-final.json`, `probes-final/`: intermediate fixed classification source and rejection/crash checks.
- `probe_rename_recovery_durability.py`, `rename-recovery-durability-case/result.json`: reproduced the missing parent fsync after interrupted rename.
- `changes-required-findings.md`: preserved earlier decisions and their source identities.
- `source-durable/`, `source-snapshot-durable.json`: final reviewed byte snapshot; `final-state.json` checks all six hashes against the final working tree and commit.
- `independent_revalidation_probes.py`, `probe-results-durable.json`, `probes-durable/`: 42 independent named checks using isolated copies of the actual data.
- `probe_repaired_rename_durability.py`, `rename-durability-repaired-results.json`, `durable-rename-*-case/result.json`: checkpoint/fsync traces through both recovery paths after interrupted rename.
- `adapter-durable-reviewed.log`, `verification-commands.json`: maintained focused suite and actual command outcomes.
- `pre-admission-state.json`: canonical authorization, byte-exact original/ledger and all 46 accepted G05 records, original audit pin, process-group and scratch observations.

All mutations are confined to this independent evidence directory. No actual QM, model tests, canonical ledger/original-attempt changes, cleanup deletions, implementation edits, commits or pushes were performed by the reviewer. Synthetic partial staging remains preserved and deliberately requires manual recovery; it is not silently overwritten or discarded.
