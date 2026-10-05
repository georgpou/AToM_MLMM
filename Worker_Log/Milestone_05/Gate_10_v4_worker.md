# G10 multistate runtime — v4 core worker

**Scope:** G10 implementation Tasks 1–3; persistent 3–8-state serial exchange core and analytic/fault checks on the locked CPU profile.
**Outcome:** core implementation complete; Task 4 and combined audit pending.
**Model/effort:** GPT-6 Luna / max.
**Finished:** 2026-10-05T22:44:20+00:00.
**Snapshot:** branch `g10-engine-next`; exact base `bd44b2c93a5cba40225dba632f0277e535467be9`; code/result commit `cef01748db1d872775c1cb88e67f881182066e6c`; test-only secondary-archive follow-up `5a8ab584cc9af9e74afb7f2d926ca8b4af688e41`. The report/status/evidence commit follows these commits and is identified by the final handoff.

## Changes

The [reviewed G10 plan](evidence/G10_v3/implementation-plan.md) and
[standalone design audit](Gate_10_v3_audit.md) were GREEN before
implementation. The additive APIs `run_multistate_exchange`,
`resume_multistate_exchange` and `read_multistate_boundaries` implement an
explicit versioned three-to-eight-state controller. It admits only connected
unique state-pair sweeps under exact 300 K Reference/double/NVT/LangevinMiddle
runtime and sealed geometry settings. The existing actual AToM pair adapter
owns every decision. Workers and coordinates stay fixed while a full
walker-to-state permutation is re-resolved for each ordered pair.

Each boundary stages worker samples, full forces/raw records, portable States
and checkpoints before the next integration. The adapter decision callback
durably records the full before/after permutation and attempt history before
refresh. Recursive tree sealing publishes all final worker States/checkpoints,
reports and both host RNG streams with one directory rename. Inert journal
validation binds runtime/schedule/geometry identities, source inventory,
sample and attempt identities, complete histories, phase arithmetic, RNG
chain and initial/final assignments. Resume freshly compares every saved raw
and total field and portable-State coordinates/velocities/parameters/box
against the restored checkpoints before integration. Precommit failure retains
all available worker evidence; pending work requires explicit archive and
whole-boundary replay. Postrename commits remain authoritative.

The analytic tests cover overlapping-pair acceptance order `[0,1,2]` →
`[1,0,2]` → `[2,0,1]`, stable sample-time state IDs, ABFE and unequal RBFE
nonlinear/outside-anchor energy oracles, actual-adapter acceptance thresholds,
all-worker replay, pair compatibility, exact source inventory, caller RNG
isolation, malformed/tampered journals, checkpoint freshness and secondary
archive failures. No adapter physics, workflow persistence, dependency, force
definition or chemistry was changed.

Implementation commits changed `src/atm_mlmm/exchange.py`,
`src/atm_mlmm/exchange_journal.py`,
`tests/workflow/test_persistent_exchange.py` and
`tests/workflow/test_replica_exchange.py`. The test-only follow-up changes
`tests/workflow/test_persistent_exchange.py`. This report snapshot also updates
`docs/project-0/STATUS.md` and adds this worker record plus the `evidence/G10_v4/`
artifacts linked below.

## Verification

| Check | Command and working directory | Profile/input identity | Exit and observed result |
|---|---|---|---|
| Retained pair/export/restart suite | `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q`, repository root | `/workspace/m05-cpu-setup-v2`; `OPENBLAS_NUM_THREADS=2`; `PYTHONPATH=$PWD/src`; final source/result commit `cef0174…` | **73 passed in 195.08 s; no skips.** Full raw output: [required-pair-export-restart.log](evidence/G10_v4/required-pair-export-restart.log). |
| Primary/secondary failure archive | `python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_primary_error_survives_secondary_worker_archive_failure -q`, repository root | Same locked CPU profile; test-only follow-up `5a8ab58…` | **1 passed in 2.44 s.** Full raw output: [secondary-archive-regression.log](evidence/G10_v4/secondary-archive-regression.log). The injected secondary `OSError` was kept in `failure.json` and exception notes while the original `RuntimeError` remained primary. |
| Staged RED/GREEN history | See exact late regression commands and explicitly labeled earlier summaries | Actual worker trace; late failures are output excerpts, not complete raw logs | [red-green-regressions.md](evidence/G10_v4/red-green-regressions.md). Earlier Task 1–3 runs were not tee'd; this evidence distinguishes their summarized counts from saved raw logs and records corrected test-setup failures. |
| Documentation self-test | `python tools/check_docs.py --self-test`, repository root | Repository Markdown/local-link validation | Exit 0; zero errors, 212 Markdown files and 1,434 local links checked. Final post-report output: [docs-self-test.json](evidence/G10_v4/docs-self-test.json). |
| Whitespace | `git diff --check`, repository root | Complete worker source/test/report changes | Exit 0; no whitespace errors. |
| Source/test integrity | SHA-256 manifest | Code/result and test-only follow-up snapshots above | [source-hashes.txt](evidence/G10_v4/source-hashes.txt); output/log checksums: [artifact-hashes.txt](evidence/G10_v4/artifact-hashes.txt). The initial artifact check used the wrong working directory; the corrected check passed all five entries. |

All scientific test commands ran serially after sourcing
`/workspace/m05-cpu-setup-v2/activate.sh`, with two BLAS threads. The new
runtime checks use small analytic cases (three workers, at most two boundaries
and one step per boundary); no resource, dependency, or environment failure
was observed. The earlier retained baseline remains the existing 31-pass
result and was not rerun as a historical review.

## Handoff

This is core implementation evidence, not G10 or M05 acceptance. No new
solvated pilots, usage documentation, QM, GPU, production or HPC runs were
performed. The full CPU suite remains reserved until the next worker’s Task 4
is complete. The next sequential worker owns the solvated ABFE/RBFE pilots,
usage documentation and combined CPU verification; only after that batch
should the independent Sol audit begin. No secondary archive error escaped
the injected regression. G05/G07 reference gaps, affinity/mixing claims,
exchanging-walker uncertainty, molecular accuracy and broader scientific
qualification remain unchanged and pending.
