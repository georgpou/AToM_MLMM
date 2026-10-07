# Before HPC audit fixes — independent audit v2

**Verdict: changes required.** F2, F4 and F5 are resolved for their bounded admission scope. F1 fixes the persistent initialization fingerprint but introduces a duplicate-history admission regression in block resampling. F3 fixes the shared loader/continuation verifier, while the journal reader retains the original inventory omission. No scientific, milestone, release or hardware hold is closed by this review.

Reviewed branch `before_HPC`, HEAD `0409da8dd7f6c8889a64bd37efbe7102cd9005ef`, checkout `/workspace/AToM_MLMM-before-HPC`; implementation `4887cc40b56e29bfd0760e487b1ebe5b110eefb3`, base `a78af5ce9c74f09c8ddeba373187c99a7f72035b`. Source tree `9181b18a10900f17badc5b21eee2b1ea7bc4bc64`; tests tree `da52a0df1acad7f0550198db14ba264742762855`. Sole fresh independent auditor, 2026-10-07 UTC; no nested agents, remediation, commit or publication.

## Scope and evidence

Read `AGENTS.md`, relevant current handoff/STATUS and C/E packet sections, the original [v1 audit](Before_HPC_Audit_v1.md), [fix summary](Before_HPC_Audit_Fixes_v1_summary.md), [worker report](Audit_Fixes_v1_worker.md), implementation delta, affected source/test bodies, HPC CLI/run guide, and retained final compatibility/identity receipts. The implementation-to-reviewed-HEAD diff contains no source/tool/test/environment/fixture/package changes. This is one targeted F1–F5 review with two concrete shared-interface follow-ups, not another exhaustive A–E audit.

The retained [compatibility run](evidence/audit-fixes-v1/compatibility-002.log) reports **27 passed, zero skipped, exit 0, 10.00 s**, at 19:32:25–19:32:36 UTC. Its tests were inspected rather than rerun. The orchestration [identity receipt](evidence/audit-fixes-orchestration-v1/final-identity.json) records preservation of all 386 supplied files and the original audit; these inventories were not independently rehashed again. Retained worker logs are whitespace-normalized text evidence, not byte-exact stdout. Historical/sealed records remain untouched.

## Ranked findings

### V2-F1 — High: the fix permits duplicate histories through synchronized-block analysis

**Locations:** `src/atm_mlmm/exchange_analysis.py:303`, `:225`, `:390`, `:453`.

The previous unconditional duplicate-initialization check is now inside `if resampling.method == 'independent_runs'`. Consequently, two histories with different run/sample IDs but identical initialization identities and identical observations are accepted by `synchronized_blocks`. That method draws blocks separately for each history and combines both sets of observations. It therefore treats copies of one trajectory as separate sources of random variation. The same path reports across-run mean standard error, which can collapse to zero for duplicates. Resampling complete walker frames protects dependence within a run; it does not account for perfect dependence between duplicated runs.

**Fresh evidence:** [inert probe source](evidence/audit-v2/admission_probe.py), [output](evidence/audit-v2/admission-probe.log), [receipt](evidence/audit-v2/admission-probe-receipt.json). Two synthetic histories generated from the same seed contain identical energy records and identical initialization provenance, with distinct run/sample IDs. The `independent_runs` positive refusal raises the expected initialization error. The same duplicate pair under `synchronized_blocks` reaches the first fit. A distinct-seed block pair also reaches fitting. All fitting was intercepted, so this demonstrates the admission regression without asserting a measured covariance error or running dynamics. The condition is shared by synthetic and persistent histories; the retained producer test separately establishes identical fingerprints for renamed persistent duplicate streams.

**Minimal recommendation:** retain duplicate-initialization refusal whenever multiple histories are combined under either method, unless an explicit cross-history dependence treatment is implemented. Add a block-method duplicate refusal alongside a distinct-stream positive control. The stronger persistent fingerprint should be retained.

### V2-F3 — Medium: persistent journal validation bypasses the corrected source inventory helper

**Locations:** `src/atm_mlmm/exchange_journal.py:139`, `:368`, `:375`; consumer `src/atm_mlmm/exchange_analysis.py:62`.

`read_multistate_boundaries` still calls its separate `_verify_multistate_source`. This verifier compares declared Python paths with current source and checks declared bytes, but never enumerates the actual bundled Python tree. Thus journal-derived analysis can accept worker source containing undeclared Python files or symlinks even though the repaired loader/continuation path refuses the same source. This is a remaining F3 interface omission, not a regression in the new helper and not an observed executable-load bypass: the journal reader is inert, and the actual loader/continuation callers use the repaired helper.

**Fresh evidence:** [inert probe source](evidence/audit-v2/journal_inventory_probe.py), [output](evidence/audit-v2/journal-inventory-probe.log), [receipt](evidence/audit-v2/journal-inventory-probe-receipt.json). Both verifiers accept a matching 44-module copy. Adding one undeclared nested `.py` file is accepted by the journal verifier and rejected by `verify_source_inventory`. Replacing it with an undeclared `.py` symlink produces the same disagreement. The copied source was never imported. This directly exercises the journal's source-check helper; no whole journal was fabricated, modified or resumed.

**Minimal recommendation:** route journal source admission through the same complete recursive verifier, preserving manifest identity checks, and add an inert journal-reader refusal control for undeclared files/symlinks with a relocated positive control.

## F1–F5 dispositions

| Original finding | Disposition and inspected support |
|---|---|
| **F1: persistent initialization** | **Partially resolved; V2-F1 blocks acceptance.** `_journal_frames` at `exchange_analysis.py:101` now hashes each verified initial State, the integrator seed sequence, typed runtime identity, and initial host RNG artifact. Run/walker/sample IDs and narrative evidence are excluded. `read_multistate_boundaries` verifies the initial sealed inventory and metadata/worker contract before these bytes are consumed. The retained producer test covers renamed/prose-altered duplicates plus distinct prepared-state, host-RNG-only and integrator-seed-only controls. Its distinct controls establish fingerprint/admission behavior, not sampling adequacy. |
| **F2: HPC admission** | **Resolved for local declaration/byte-identity admission.** `hpc.py:27` validates schema, field types, positive allocations, storage safeguard, scheduler and checkpoint semantics. `hpc.py:109` calls the bundle verifier and compares all four profile artifact identities with verified inventory/content hashes. Manifest-only callers remain held. The CLI verifies the directory containing the supplied regular `manifest.json`; the guide documents the inventory-hash convention and unchanged dry-run scope. Retained tests cover typed contradictions, format-only refusal, a matching CLI positive, source-identity mismatch and modified file bytes. The tiny fake wheel/asset fixture tests byte binding only; it does not qualify a usable release, model authorization or actual storage behavior. |
| **F3: recursive source inventory** | **Loader/continuation fix resolved; journal interface remains open under V2-F3.** `runtime_validation.py:17` now compares declared, current and recursively enumerated bundled Python sets, verifies declared bytes, and rejects symlinks. Worker loading and fixed/pair/multistate continuation use it. Retained tests cover relocated matching trees, undeclared nested modules, nested symlinks and rejection before trusted load. The journal reader's separate implementation needs the same contract. |
| **F4: active force owners** | **Resolved.** `validate_solvent_recipe.py:188` requires a nonempty unique declared owner list; `:192` requires every stage list to contain unique nonempty strings and exactly the declared set. Empty, partial, duplicate and extra stage owners therefore cannot pass. Retained tests exercise empty/partial refusal and complete-owner admission. This validates input declarations, not physical force execution or solvent chemistry. |
| **F5: explicit empty decisions** | **Resolved.** `prepare_protein_input.py:29` separates missing keys from the three field-specific valid explicit values: null box, empty constraints and empty cuts. Downstream comparisons still bind those values to loaded artifacts. `:61` recursively converts immutable mappings/tuples into canonical JSON-compatible values, fixing the newly exposed provenance comparison without discarding keys or values. The complete existing-fixture test reaches input-only admission with all three values, including frozen provenance; the unresolved proposal still blocks. No target was selected and production acceptance remains false. |

## Fresh checks and omissions

Only the two characterization scripts above were executed: **exit 0**, respectively **0.235 s** at 19:49:26 UTC and **0.093 s** at 19:50:07 UTC. Exit 0 confirms reproduction of the recorded admission defects, not passing acceptance tests. Receipts retain exact activation/command, Python path, UTC times, reviewed HEAD/source tree, script hashes, output and exits. Both ran serially with `/workspace/before-hpc-cpu-v2/activate.sh`, `PYTHONPATH="$PWD/src"`, two OpenBLAS/OpenMP/MKL threads and the 8 GiB cgroup limit; Amber was not used.

No dependency installation, model loading, QM, dynamics, production, cluster/GPU trial, numerical qualification, package rebuild, full bundle rehash or full-suite replay occurred. Retained tests are scoped evidence, not fresh whole-suite verification. Existing records and sealed workers were preserved. Audit writes consist only of this file and `evidence/audit-v2/`.

## Remaining holds and stop

- The original full CPU suite remains **unresolved after SIGKILL near 8 GiB, with no final pytest summary**. The 27 affected passes do not replace it.
- C3 physical-endpoint comparison/refusal remains open. Real protein/physical solvent inputs, applicable AToM corrections and their domains, adequate independent molecular sampling, convergence and linked covariance remain unqualified; no final binding result is accepted.
- G07 retains 29 missing references, 46 preserved records, seven exceedances and original failures. Charged/remaining/estimated-continuation budgets remain 2325.6446500519996 / 84074.355349948 / 122992.52458401839 seconds; authorization remains false. No QM budget or reference was changed.
- Actual cluster/GPU/storage/checkpoint parity, licensing, fully offline reproduction and independent release reproduction remain open. Existing wheels/bundles predate these fixes; no rebuild or current-source package acceptance occurred. The model's academic noncommercial restriction remains.

The next minimal work, only if separately authorized, is V2-F1 and the narrow journal-source V2-F3 follow-up with focused refusal/positive controls. This report authorizes no remediation or further audit. The auditor stops after delivery.
