# G09 scientific-error preservation — v4 worker

**Scope:** close Important G09-R2; carry forward the reviewed bounded sparse
TIP3P/PME G09-T1/T2/T3 and single G10-T2 pair boundary without changing their
scientific definitions. Reference double/MACE CPU float64, two CPUs.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-05 UTC; exact evidence capture time is in the snapshot.\
**Model/version:** GPT-6-based Codex; exact model/version and reasoning setting
not exposed.\
**Previous:** [v3 worker](Gate_09_v3_worker.md) / [v3 audit](Gate_09_v3_audit.md).\
**Snapshot:** branch `m04-engine-readiness`; reviewed submission/base
`b11c16750ad111a2fcafcda7a2d51c6690254e97`; tested repair
`027f8173babc13606afb24d96f58148704e38b1b`. The subsequent submission commit
contains documentation, audits and evidence only; the reviewer records its SHA.

## Repair and scientific boundaries

Verified the review finding against the actual handler and CLI. G09-R2 is
Important because an archive write failure replaced the scientific exception
and omitted primary metadata in the normal CLI. Successful numerical results
were unaffected. No additional Critical/Important/Minor finding was reported.

The handler now writes primary provenance first, attempts cached State,
checkpoint and each transformed map independently, and records archive
operation/type/message diagnostics in metadata and notes on the original
exception. The CLI prints those notes. The original exception object, type,
message and traceback are preserved even if a directory or metadata write
fails. A pre-existing failure directory is not overwritten. No energy/force
reevaluation or failed sample insertion occurs. XML still preserves nonfinite
coordinates; unavailable step/time provenance is explicit `null`.

Only failure handling and CLI diagnostics change. The independently accepted
[scientific amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md)
and [G10 v1 pair scope](Gate_10_v1_audit.md) are unchanged. Exact exported-State
parity, minimum-image periodic anchors and sparse-water limitations carry
forward; no scientific input, model, lock or tolerance was tuned. V3 artifacts
are frozen rather than migrated to new source.

## Actual verification

All commands ran serially from `/workspace/AToM_MLMM`, after
`source /workspace/atom-mlmm-g09-v3/activate.sh`, with
`OPENBLAS_NUM_THREADS=2` and `PYTHONPATH="$PWD/src"`.

| Command/check | Exit and observed result |
|---|---|
| `python -m pytest -q tests/workflow/test_failure_archive_errors.py` before repair | 1; **12 expected failures in 2.78 s**. Original error/CLI/artifact contracts fail at directory, step count, cached State capture/serialization/write, checkpoint capture/write, each map write and atomic metadata replacement boundaries |
| `python -m pytest -q tests/workflow/test_failure_archive_errors.py tests/workflow/test_failure_geometries.py tests/workflow/test_engine_failure_retention.py tests/workflow/test_engine_restart.py` | 0; **19 passed in 28.52 s**, no skips; exact original exception identity, primary/secondary CLI messages, available artifacts/provenance and no reevaluation/sample insertion |
| `python -m pytest -q --basetemp=/tmp/atom-mlmm-cloud-r2-full` | 0; **501 passed in 498.74 s**, no skips, including all actual solvent/model/exchange checks |
| `python tools/check_docs.py --self-test`; `git diff --check` | 0; zero documentation errors/eight self-tests; clean diff before submission |
| Cgroup `memory.events` after the full suite | `oom=0`, `oom_kill=0`, `oom_group_kill=0` |

[Evidence](evidence/G09_v4/README.md) retains RED/GREEN/full logs, an actual
map-write-fault archive, exact snapshot and 49 source/input/regression hashes.
Root verification does not close R2 independently.

## Handoff

Obtain focused closure review on the frozen new submission. Carry forward v3
scientific/G10 acceptance only after verifying that the relevant definitions,
inputs, force routing and adapter are unchanged. The assigned reviewer writes
`Gate_09_v4_audit.md`; submitted workers/evidence remain frozen.

Dense-solvent preparation, broad periodic restraint excursions, implicit
solvent, GPU, persistent exchange/RNG/history supervision, recovery after an
exchange failure, exchanging-walker statistics, equilibrium/affinity and full
G09/G10/M05 remain open. G07 physical failures and 29 missing references remain;
QM accounting is still 2325.644650052/86400 s. No QM/production job ran. T4
lysozyme and Slurm/HPC work remain user initiated.
