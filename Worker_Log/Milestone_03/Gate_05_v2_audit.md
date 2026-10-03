# G05 prepared-reference provenance repair — v2 independent audit

**Verdict: `accepted_for_scope` for closure of G05-v1-R1 and prepared-T4 reference-loader readiness only.** R1 is closed on exact **`3124c6d275bf19a32ce364dfdb83b11115828ac5`**. **G05-T4 chemical acceptance, P0-TEST-G05-07/08, P0-REQ-033 and full G05 acceptance remain pending.**

**Worker:** [Gate_05_v2_worker.md](Gate_05_v2_worker.md). **Comparison base:** `a7768e375476667139db374dc0091999263a37de`. **Reviewed source:** detached `/workspace/AToM_MLMM-g05-review-v3`, clean before and after execution at the exact submission. **Reviewer:** independent Codex `/root/g05_provenance_repair_v2`, dispatched as actual **gpt-6-astra / high / fresh context**; deployed backend build is not exposed. **Date:** 2026-10-03 UTC; captures give execution timestamps.

The reviewer authored only this audit and new independent evidence/probes. No implementation, repair, delegation, commit, publication, quantum calculation, model comparison or mutable generated-reference review was performed. This review applies the S07 snapshot/provenance and bounded-acceptance requirements, G05-T4 and S06 physical-reference rules. It reads the v1 finding and v2 worker, source/tests, recorded RED/GREEN, exact M00 v3 plan and actual agreement record. [Evidence guide](evidence/G05_v2_independent/README.md) identifies complete commands, outputs and reviewer scripts.

## Independent evidence

All executions activated `/workspace/atom-mlmm-g05-v2/activate.sh`; focused tests/probes used `PYTHONPATH=src` and two OMP/MKL/OpenBLAS threads. The command captures record actual argv, cwd, exact HEAD, clean status before/after, timestamps, interpreter, exit codes and full output.

| Independently executed on 3124c6d | Result |
|---|---|
| `python -m pytest -q tests/unit/test_reference_provenance.py tests/unit/test_reference_metrics.py` | **10 passed**, exit 0, 0.17 s pytest time; `focused.json` |
| Independently constructed synthetic loader probe | **1 matched positive and 29 expected rejections**, exit 0; every invalid case rejected before reference-record access; `binding.json`, `binding-results.json` |
| Source/input and preservation verification | **270/270 manifest hashes match**; **192 protected files** and **61 inherited source/test files** unchanged against a7768; **48 exact M00 v3 files** unchanged against a825f5; exit 0; `snapshot.json`, `snapshot-results.json` |

The source/input manifest includes the actual checkpoint bytes, with SHA-256 `165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`. The protected comparison covers tracked fixtures, model provenance/assets, environment locks, scientific specifications/reference plans and tools. Only `src/atm_mlmm/chemical_reference.py` changed in production; only `tests/unit/test_reference_provenance.py` was added among source/tests/tools/fixtures/models/environment/specifications/reference plans. Scientific geometries, quantum settings, limits, model, locks, model/analytic code, physical builder and MM ledger are preserved.

The worker's preserved RED shows six intended rejection failures and one positive; GREEN shows ten passes. Its full capture reports **292 passed / two missing-quantum-data failures**, and analytic capture **272 passed / 22 deselected**. These captures recorded the then-parent HEAD a7768 in the implementing checkout while the repair was uncommitted; they are retained worker evidence, not independent clean-3124c6d executions. Their digests and commands are recorded in `snapshot-results.json`. The prior independent v1 audit's 29 focused, 214 inherited and 138 coordinate checks concern unchanged code on a7768. Those broad numerical checks were not repeated for this narrow importer-only repair. None of the absent or deselected chemical tests counts as a pass.

## Finding closure

| Finding | Independent assessment |
|---|---|
| **G05-v1-R1 — approval not bound to the plan at load time** | **Closed.** `chemical_reference.py:43–49` hashes the actual loaded `input-manifest.json`, compares that digest with the embedded approval and requires `reviewed_commit` to be a string matching the complete lowercase `[0-9a-f]{40}` form. These checks execute before record iteration. The existing outer-manifest plan/settings, input digests, agreement/reviewer and record integrity/coverage checks remain in place. |

The independent probe uses its own explicitly labelled synthetic H2 geometry and fabricated zero arrays/approval values, entirely outside the scientific fixture tree. It rejects wrong, missing, null, empty and wrongly typed approval hashes; missing/null/malformed commits, including uppercase, nonhex, wrong length, whitespace/newline and nonstring values; false/missing/nonboolean agreement; absent fresh-review/design conditions; an approval and outer manifest that agree with each other on a false digest; and a modified input manifest whose outer hash was updated while its approval remained stale. It also retains rejection of an outer plan-hash mismatch. Instrumented record opens establish that all 29 rejections precede record reading, while the valid synthetic control reads and returns its one expected record. These are software controls, not actual agreement, quantum data or chemical adequacy evidence.

No blocking issue remains within R1. A syntactically valid commit is provenance metadata, not a cryptographic authentication of a reviewer's authority; the requested repair requires a matching plan digest and well-formed exact commit and satisfies that contract. Actual agreement and review provenance remain independently recorded.

## Decision and handoff

The actual new [approved decision](../Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json) records explicit user agreement to the exact M00 v3 plan/limits and **12 wall hours, two CPU threads, 5 GiB**. Its manifest digest matches the frozen inputs and its audit digest matches the recorded M00 v3 audit; its reviewed commit is **`a825f5f1c2d8cf4146133c2049ef1c4eca550e93`**. The historical `decision-pending.json` remains false and byte-identical. This new decision supersedes the older pending-agreement state described in v1; this reviewer neither supplies nor infers approval from synthetic controls.

Accept the repaired importer's prepared-loading readiness on 3124c6d. Retain the v1 acceptance of the six G05 software assertions within its stated source/profile scope. This audit does **not** accept actual generated references, numerical reference controls, chemical comparisons, full G05, protein adequacy, G06/G07 or M03 closure. The ongoing implementer quantum run and mutable outputs were excluded. The next complete independent fresh-context Astra/high G05 audit must review actual references, all 34 targets, ten rotation controls and two fine-grid confirmations, preserved failures and unchanged limits, and all applicable gate assertions together on a new immutable source/data snapshot.
