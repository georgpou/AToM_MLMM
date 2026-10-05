# G10 multistate runtime design — v3 worker

**Scope:** G10-T2/T3 standalone design and implementation plan only; proposed Reference double / CPU NVT scheduler, no runtime execution.
**Outcome:** ready_for_audit.
**Model:** `gpt-6-luna` / `max`.
**Finished:** 2026-10-05T21:11:51+00:00.
**Snapshot:** branch `g10-engine-next`; base `3952a9b36a92e37f0f98fdf3981c9320368a18b3`; final design/spec/plan/STATUS result `179c3035c6b70293811b6dd6e24319fd9ac932db` (this worker log is a report-only addition).

## Changes

The [proposed amendment](../../docs/project-0/specs/g10-multistate-runtime-amendment.md)
defines an additive `run_multistate_exchange` / `resume_multistate_exchange` API,
three-to-eight explicit states, a connected ordered pair sweep, live
walker-permutation resolution, once-per-boundary integration, sample-time
state identity, actual-adapter-only pair decisions, and one durable boundary
transaction with explicit rollback. It requires exact recursive source
inventory equality before trusted load, stages each successful worker sample
and State/checkpoint before the next integration, and retains every pair's
per-attempt phases and full permutation history. The worked three-state sweep
accepting `(0,1)` then `(1,2)` yields `[2,0,1]`. The independent energy checks
use the existing nonzero state-independent static anchor; no new state-dependent
outside Hamiltonian is admitted. Inert hash/history and matrix arithmetic checks
run before trusted load; a fresh actual-context saved-energy comparison runs
after checkpoint restoration and before integration.

The [implementation plan](evidence/G10_v3/implementation-plan.md) maps the
design to bounded sequential work and named RED/GREEN assertions, including
pair regressions and serial three-worker pilots prepared through the shared
runner from the existing solvated v2 ABFE and unequal-ligand RBFE fixtures.
`STATUS.md` marks this proposed increment `ready_for_audit`, not implemented or
accepted. The unchanged CPU setup was validated by the orchestrator: **9/9
environment checks** passed at `2026-10-05T20:54:57.844982+00:00`. The retained
engine baseline passed **31 tests in 115.64 s**, zero skips; raw output is
`/workspace/g10-start-baseline.log`.

## Verification

| Check | Command and working directory | Profile/input identity | Exit and observed result |
|---|---|---|---|
| Documentation links/headings | `python tools/check_docs.py --self-test`, repository root | Final G10 v3 design/report docs | Exit 0; 0 errors, 209 Markdown files, 1,415 local links, eight self-tests passed. |
| Source/test scope | `git diff 3952a9b36a92e37f0f98fdf3981c9320368a18b3 -- src tests`, repository root | Required clean starting HEAD | Exit 0; empty diff. No source or test files changed. |
| Whitespace | `git diff --check`, repository root | Documentation changes | Exit 0; no whitespace errors. |
| Retained pair/runtime baseline | `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q`, repository root | Orchestrator-run unchanged locked CPU environment; starting source | **31 passed, 0 skipped, 115.64 s**; raw output `/workspace/g10-start-baseline.log`. |

## Handoff

No source or test code changed, and no multistate runtime, solvated pilot, GPU,
QM, production, or HPC job was run. This proposal is not an implementation or
acceptance of G10/M05. Next action: independent `gpt-6.1-sol / max` audit of the
exact design snapshot; implementation remains gated on that audit. Existing
pair behavior for newly prepared source-matched bundles remains an explicit
regression constraint. Frozen older bundles must use their original source and
cannot silently migrate. Exchanging-walker uncertainty, whole-sweep detailed
balance, mixing/convergence, affinity, and molecular accuracy remain
unqualified. Preserve all G05/G07 reference blockers and the QM ledger as
written in the design.
