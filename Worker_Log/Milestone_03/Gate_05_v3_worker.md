# G05 calculation pause and fresh-session handoff — v3 worker

**Scope:** user-requested stop during approved M00/G05 reference generation;
preserve completed calculations and hand over the existing branch.
**Outcome:** partial; software and importer repair accepted for their scopes,
full quantum bundle, chemical comparison and complete G05 review pending.
**Snapshot:** `m03-reference-g05`, published parent
`0935fd1213813e388a5dcc7e689998e907111e13`, unchanged reviewed scientific
source `3124c6d275bf19a32ce364dfdb83b11115828ac5`.

The exact M00 v3 design and user agreement preceded the quantum-only batch.
Eight targets completed: three acetamides, four butanes and the first
butane/acetamide contact. The final contact's 695.5 s calculation wrote its
finite energy/23-atom gradient record and worker completion receipt; only
seven coordinator exit receipts were observed before the execution transport
was lost. No coordinator manifest was saved. Thirty-eight jobs remain:
seven isolated targets, 19 contacts, ten rotations and two finer-grid checks.

The connection error says the exec-server transport disconnected and recovery
timed out after 25 s. Cloud tools recovered; no quantum process was visible at
the checkpoint. The cause is unestablished. The container has 8 GiB RAM and no
swap; its lifetime high-water reached the cap, with no recorded OOM kill.
That is evidence for checking memory headroom, not attribution to this job.
About 14.28 GiB disk is free; saved calculation evidence is about 0.40 MiB.

This checkpoint adds saved attempt files, observations, a read-only provenance
verification helper, this worker log and the fresh-session handoff. STATUS and
the earlier continuation are updated to paused. Production code, frozen
chemical inputs/settings/limits, model, locks and scientific definitions are
unchanged. No additional quantum calculation or comparison was launched.

## Verification

Run from `/workspace/AToM_MLMM-m03-reference-g05` after sourcing
`/workspace/atom-mlmm-g05-v2/activate.sh`:

| Command | Actual result |
|---|---|
| `python Worker_Log/Milestone_00/evidence/M00_reference_v3/verify-stop-state.py` | Exit 0; 270 source/input hashes, 46 frozen-plan hashes, 105 reference packages and all eight saved records verified; 38 missing jobs, no coordinator manifest or visible quantum worker |
| `python tools/check_docs.py --self-test --output Worker_Log/Milestone_00/evidence/M00_reference_v3/checkpoint-docs.json` | Exit 0; zero errors, 109 Markdown files/805 local links, eight self-tests passed; local docs only |
| `git diff --check` | Exit 0 for tracked report updates before staging |
| `git diff --cached --check` | Exit 2 for native whitespace in preserved raw quantum outputs only; raw evidence remains unchanged |
| `git diff --cached --check -- . ':(exclude)Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v1/**'` | Exit 0; authored checkpoint files have no whitespace errors |

The [checkpoint evidence](../Milestone_00/evidence/M00_reference_v3/README.md)
preserves exact observed output/error, record hashes and resource snapshots.
Its `checkpoint-whitespace.json` records the raw-output-only formatting
diagnostics and scoped authored-file check; calculation logs were not trimmed.
The [v1 software audit](Gate_05_v1_audit.md) and [v2 R1 audit](Gate_05_v2_audit.md)
remain the actual independent decisions. No v3 audit was performed.

Earlier saved full-suite result remains 292 passed/two missing-reference
failures, analytic 272 passed/22 deselected. These suites were not rerun for
this evidence/documentation-only checkpoint. Both chemical tests still await
the full real reference bundle; no substitute is counted as a pass.

## Next action

Use the [fresh-session handoff](../../docs/project-0/handoffs/M03-G05-fresh-session.md)
on this same child. The current generator cannot resume and writes the manifest
only at the end. Add/test/review validated reuse and durable progress, check
RAM headroom and the remaining approved budget, complete 38 jobs, validate all
controls, then run the chemical comparisons and obtain complete exact-snapshot
Astra/high/fresh G05 review. Do not restart completed jobs blindly or label
the incomplete attempt ready. Preserve prior attempts and all failed data.
