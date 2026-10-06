# G10 multistate Task A — v6 worker

**Status:** Task A implementation and bounded checks complete; root verification
and the later combined audit remain pending. **Branch:** `g10-engine-next`.
**Starting HEAD:** `c27358668499ef596a73468936bc21279ebb1b6a`. **Code/result
commit:** `8157b24ee93a841dbf91cf10a02a19dd321e6c88`. **Worker:**
`gpt-6-luna / max`. **Finished:** 2026-10-06T10:41:20+00:00 UTC.

This worker handled only R1, R4, R7, and inert sample/final-report clock type
and agreement checks required before Task B. It did not implement restored
runtime clocks or geometry (R2/R3), nor postcommit failure capture or fsync
changes (R5/R6). The original v5 RED report and evidence remain unchanged.

The tests-first focused run captured RED on the untouched starting production
source: **34 failed, 3 passed**. It showed malformed inert
declarations reaching the trusted loader, both accepted and rejected `+123`
kJ/mol refreshed-energy contradictions being admitted, and added/modified
nested manifests escaping recursive sealing. The loader-spy/tree-hash evidence
is preserved in `evidence/G10_v6/focused-red-baseline-results.json` and its raw
log. Two earlier harness checks are also retained and explicitly named as
harness checks; they are not finding evidence.

The repair validates exact integer public limits and the complete intended
worker seed range before loading or creating output; checks Python and NumPy
RNG structures, all stored inverse/index/sequence values and sample identities;
and validates finite, exact-type report clocks against capture-time samples.
Refreshed totals are bound to their selected workers' same-attempt evaluated
raw-matrix entries under the existing `1e-8 kJ/mol` bound on either assignment.
Recursive tree sealing excludes only the root `manifest.json`; nested manifests
are inventoried and rejected by the sealed layout/hash checks. No Hamiltonian
or Metropolis implementation was copied, and no tolerance or physical
definition changed.

The fresh inert challenge result records **36 PASS / 0 VIOLATION**, with loader
calls empty and before/after run-tree hashes equal. The combined focused module
passes **37 tests, 0 skipped**. Separate saved result logs show the R1 selection
at **33 passed / 4 deselected**, R4 at **2 passed / 35 deselected**, and R7 at
**2 passed / 35 deselected**. Positive controls retain valid three/eight-state
selection, finite nonempty Gaussian-cache roundtrips, actual adapter nonlinear
and outside terms, and exact pair/restart behavior. The required retained
compatibility command passes **74 tests, 0 skipped**.

| Check | Command | Result / raw evidence |
| --- | --- | --- |
| Focused baseline RED | `python -m pytest tests/workflow/test_multistate_inert_repairs.py -q` | Exit 1; 34 failed, 3 passed. Exact raw output is `evidence/G10_v6/focused-red-baseline.log.gz`; results are in `focused-red-baseline-results.json`. |
| Focused repaired source | `python -m pytest tests/workflow/test_multistate_inert_repairs.py -q` | Exit 0; 37 passed, no skips. `evidence/G10_v6/focused-green.log` and `focused-green-results.json`. |
| Retained compatibility | `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q` | Exit 0; 74 passed, no skips, 247.19 s. `evidence/G10_v6/compatibility.log`. |
| Documentation | `python tools/check_docs.py --self-test` | Exit 0; zero errors; 223 Markdown files, 1,532 local links, 57 external links not fetched; all self-tests true. `evidence/G10_v6/docs-self-test.log`. |
| Whitespace | `git diff --cached --check` | Exit 0 after preserving pytest traces as gzip evidence. The earlier staged check flagged literal trailing spaces from captured pytest source excerpts; exact output is `evidence/G10_v6/diff-check.log.gz`. Final clean output is `evidence/G10_v6/diff-check.log`. |

The first documentation self-test after drafting the report found that its
linked SHA manifest had not yet been created; that failed output is preserved
in `docs-self-test-incomplete-manifest.log`. After adding the manifest, the
document check passed with zero errors as recorded above. The byte-exact RED
and harness traces are tracked as gzip files to preserve their captured
whitespace; temporary uncompressed copies were kept outside Git during closeout.

The implementation commits only `src/atm_mlmm/exchange.py`,
`src/atm_mlmm/exchange_journal.py`, and
`tests/workflow/test_multistate_inert_repairs.py`. Their SHA-256 digests and
result-log digests are recorded in [`evidence/G10_v6/README.md`](evidence/G10_v6/README.md)
and the adjacent `sha256sums.txt`. The complete diff from the starting HEAD
contains no other source/test paths. No full 577-test suite, molecular pilot,
QM, GPU, HPC or production job was run for this intermediate task.

Task A's worker checks are self-checks, not independent closure. Tasks B and C
remain open, and all seven findings still require the final combined
`gpt-6.1-sol / max` audit. Existing scientific and ledger limitations in the
v5 report remain unchanged.
