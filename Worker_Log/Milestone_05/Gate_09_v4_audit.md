# G09 scientific-error preservation — v4 audit

**Reviewed worker:** [Gate_09_v4_worker.md](Gate_09_v4_worker.md).\
**Snapshot:** `m04-engine-readiness`, exact HEAD `09a85d979fe9fce2ceca23da74509846254df9b1`, tested repair `027f8173babc13606afb24d96f58148704e38b1b`, against independently reviewed `b11c16750ad111a2fcafcda7a2d51c6690254e97`.\
**Scope/profile:** focused Important G09-R2 closure; unchanged locked Reference-double/MACE-CPU-float64 profile, two CPUs.\
**Reviewer:** independent `gpt-6.1-sol`, MAX dispatch setting; no delegated agents.\
**Finished:** 2026-10-05T11:13:05+00:00.\
**Verdict:** **accepted_for_scope; G09-R2 closed.**

## Evidence

Read the v4 worker/evidence, reviewed the complete repair diff and regression logic, and verified S07 failure/provenance obligations against the original [v3 finding](Gate_09_v3_audit.md). Production changes are confined to failure archiving and CLI exception-note display. No scientific definition, successful sampling path, physical builder, force routing, model, lock, fixture, numerical limit or exchange adapter changed.

Commands ran serially from `/workspace/AToM_MLMM` after `source /workspace/atom-mlmm-g09-v3/activate.sh`, with `OPENBLAS_NUM_THREADS=2` and `PYTHONPATH=/workspace/AToM_MLMM/src`. [Independent evidence](evidence/G09_v4_independent/README.md) retains exact commands, concise logs, probes and four compound-failure CLI/metadata captures.

| Independent check | Actual outcome |
|---|---|
| New archive-error regressions, both-map failure geometry, actual worker failure retention, engine restart, original independent map-preservation contract and nonfinite-coordinate probe | Exit 0; **21 passed in 39.92 s**, no skips |
| Additional actual-worker compound-failure/CLI/metadata/pre-existing-directory/nonfinite-time probes | Exit 0; **6 passed in 1.51 s**, no skips |
| `python Worker_Log/Milestone_05/evidence/G09_v4_independent/verify.py` | Exit 0; all **49 source/input/regression hashes** match HEAD and the tested repair, and all **10 capture hashes** match; earlier scientific evidence/models/locks are unchanged |

The captured **501 passed in 498.74 s** full CPU suite is submitted verification, not an independently repeated full suite. The obsolete v3 CLI characterization expecting the defect was deliberately excluded.

## Findings and closure

No new Critical, Important or Minor finding was identified. G09-R2 is closed by the following independently verified behavior:

- Every challenged failure propagates the exact original exception object, type, message and original scientific traceback. State/walker/sample/sequence/journal and transfer provenance remain correct whenever metadata can be saved.
- Cached-State capture/serialization/write, checkpoint capture/write, step-count, individual map writes and metadata replacement failures produce explicit secondary operation/type/message diagnostics. The normal CLI prints the original `NumericalDomainError` followed by archive notes, including when metadata cannot be retained.
- Simultaneously unavailable State and checkpoint still retain primary metadata; simultaneous State/checkpoint/map0 write failures still retain map1. Each independent available artifact is attempted. A failed first metadata write is recovered by the final update; a failed final update preserves the primary record and reports the failed update through exception/CLI notes.
- Unavailable/nonfinite cached time is explicitly `null`, with its cause diagnosed; all other available artifacts survive. The original nonfinite-coordinate probe retains nonfinite State/map XML unchanged.
- A pre-existing failure directory retains every original file byte-for-byte, reports the directory conflict, and performs no subsequent State/checkpoint capture or overwrite.
- No challenge reevaluates failed energy/forces or inserts a failed sample.

The archive cannot guarantee an artifact when its capture/write or directory is unavailable. It now preserves and surfaces the primary cause plus explicit secondary diagnostics under those conditions, which satisfies the effect-based closure requirement.

## Decision and handoff

Carry forward the [v3 scientific amendment decision](Gate_09_v3_audit.md) and [G10 v1 single-pair acceptance](Gate_10_v1_audit.md) onto this repair snapshot. Exact hash/diff checks confirm unchanged sparse rigid TIP3P inputs, orthorhombic PME/dispersion accounting, minimum-image periodic anchors, force ownership, tolerances and exchange definitions. The amendment's only document changes record the existing review status/decision; its scientific body is identical.

With G09-R2 closed and G09-R1 still closed, accept the submitted bounded G09-T1/T2/T3 technical subsets and the unchanged G10-T2 single actual-worker pair boundary for scope. Existing v3 sealed attempts remain frozen and are not silently migrated to new source. Only this audit and new independent evidence were written; STATUS remains for the parent handoff.

This does not close full G09/G10 or M05. Dense liquid/preparation, broad periodic restraint excursions, state-dependent outside models, implicit solvent, GPU, new solvated offline/process qualification, persistent exchange/RNG/history supervision, postexchange-failure recovery, exchanging-walker statistics, equilibrium/affinity and molecular/MLIP physical accuracy remain unqualified. G07 physical failures, 29 missing references and the 2325.644650052/86400-second QM ledger remain unchanged. No installation, QM or production job ran.
