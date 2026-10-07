# Implementation ledger — docs/superpowers/plans/2026-10-07-before-hpc.md

User steering: stop and report after each Luna batch; next batch needs explicit user approval. No audit/reviewer agents. Exactly five gpt-6-luna/max workers, sequential, no nested workers.

Setup: fetched published g10-engine-next at 4ad8ee835809325ceec8a017222415043347967d; before_HPC isolated in /workspace/AToM_MLMM-before-HPC. Original clean work checkout preserved. Reviewed-base delta empty. Supplied files retained verbatim; identities in evidence/setup-v1/handoff-identity.json.

Plan interfaces: A preserves restart/loading APIs and establishes shared admission; B extends cap/input collections consumed by D; C extends analysis/result records consumed by D/E; D prepares inputs consumed by E; E packages results and hands final frozen code to consolidated checks. Shared edits run in A–E order. Scientific holds stay holds. No known task/global-rule conflict in these packets.

A: not started. B–E: pending approval at each preceding boundary.
