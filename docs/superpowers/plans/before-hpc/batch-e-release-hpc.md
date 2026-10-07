# Batch E — technical package, CPU costs and guarded HPC handoff

**Worker:** gpt-6-luna/max; no subagents. Depends on available A–D outputs. Read G13, S07, original G09/G10 assertions and the existing CPU setup guide. Use the completed review's evidence map; do not conduct a new repository audit.

**Purpose:** Finish cloud parts of B07/B09/B14/B15 and the small useful B16 CLI gaps. Package the scoped technical implementation and prepare exact next experiments; do not release or accept whole milestones.

**Files:** Create `pyproject.toml`, `tools/build_release_bundle.py`, `tools/benchmark_cpu.py`, `tools/run_before_hpc_checks.py`, `tests/workflow/test_release_bundle.py`, `tests/contracts/test_release_evidence.py`, `tests/unit/test_benchmark_metrics.py`, and `environment/hpc/` template/checker/run-guide files. Extend `__main__.py`, `models/mace.py`, environment/provenance code only for packaging/profile needs. Add a support matrix and the final worker handoff under `docs/project-0/`.

**Interfaces:** Keep `python -m atm_mlmm` working; a console entry point may call its existing `main`. Add thin `exchange-multistate`, `resume-multistate` and explicit `analyze` commands that call existing library APIs with declared JSON inputs. Do not add new physical/exchange routes. Bundle builder outputs a hashed source/wheel/input/asset/evidence manifest; an HPC checker consumes it plus an explicit cluster-profile JSON and produces a pass/fail/held JSON, never a scheduler submission.

## E1 — installability, offline artifacts and failure behavior

- [ ] Add minimal source-layout packaging using the already pinned setuptools 84.0.0 and wheel 0.48.0; do not invoke dependency solving or change the scientific locks. Build with `python -m pip wheel --no-deps --no-build-isolation . --wheel-dir <fresh-output>`.
- [ ] Inventory code/dependency/model licensing and citations from existing files. Preserve the academic noncommercial model license and authorization. Do not invent an absent project license or claim publication rights; a missing licensing decision is a release hold, not a reason to block local testing.
- [ ] Test a clean project install in an isolated temporary environment using already validated locked dependencies. Run outside the checkout with PYTHONPATH unset; verify the imported package location. This is clean **project** installation, not an independent colleague reproduction or a fresh hardware/environment qualification.
- [ ] Fix the current repository-relative model-asset assumption for installed use: allow an explicit `ATOM_MLMM_MODEL_DIR`/documented asset directory containing the identical checkpoint, manifest and license. Verify all existing hashes/authorization before loading. Keep the checkout default; missing or changed assets reject. No network fetch, new weights or global unsafe Torch loader.
- [ ] Build a local offline bundle with exact source/model/package/input identities and applicable evidence references. Reuse existing sealed worker exports. Dependencies not actually present in local caches must be reported as unavailable; do not label a network-dependent reinstall fully offline.
- [ ] Test an installed tiny analytic calculation and one approved fixed-coordinate model/worker load from the supplied bundle. Include missing/modified asset, incomplete manifest, untrusted load and deliberate runtime failure controls; failure records survive. Help/import success alone is insufficient.

## E2 — common command line and repeatable developer checks

- [ ] Add CLI wrappers for the existing 3–8-state serial scheduler, explicit full connected pair graph, seed/count arguments and default rejection/explicit pending recovery. Delegate all admission, energy and decision work to the existing APIs.
- [ ] Add explicit analysis inputs for C's records/thermodynamic/resampling specifications and optional joint covariance. Preserve the development/unsupported statistical labels and incomplete-result behavior. CLI users must not accidentally turn a tiny preflight into a final binding result.
- [ ] Add subprocess CLI argument/error/roundtrip tests using tiny controls. Reuse the library's numerical assertions; do not mirror its calculations in duplicate CLI tests. Make `tools/run_before_hpc_checks.py` a bounded command/receipt driver for the prescribed final checks, without a second audit or hidden long jobs.
- [ ] Document check → prepare → bounded run/exchange → resume/recover → explicit analysis flow, exact setup activation, artifact locations, failure recovery and remaining limits. Keep numerical/implementation details out of normal user success messages unless needed for the decision.

## E3 — actual small CPU resource measurements

- [ ] Measure each case in a fresh serial process: all-MM, ligand-only, cavity-inclusive, native ATM and actual worker on matched small admitted inputs. Separate context startup, model load, first evaluation, repeated fixed-coordinate evaluations and permitted tiny stepping. Record CPU model/threads, wall time, peak RSS, source/model/input/profile identities and raw receipt.
- [ ] Use eight repeated fixed-coordinate evaluations for the small steady-evaluation measurement; runtime stepping remains at the parent plan's tiny counts. Report both the count and timing variability. A two-step pilot timing is not qualified production throughput and test-suite RSS is not a benchmark.
- [ ] Add independent unit tests for `ns/day = 0.0864*dt_fs/step_seconds`; e.g. 0.5 fs and 0.1 s/step gives 0.432 ns/day. Distinguish per-worker rates, aggregate simulated time, wall time and total CPU use so serial replicas are not counted twice.
- [ ] Identify bottlenecks and estimate later resource needs from measured quantities only. Do not optimize, change physics/timestep or extrapolate CPU numbers into GPU performance under this assignment.

## E4 — full requirement matrix and scientific/HPC preparation

- [ ] Produce a finite G00–G13/original-milestone assertion matrix using the gate definitions and retained evidence. For every applicable original G09/G10/M05 row, show accepted unchanged evidence, new worker-tested evidence, missing implementation, physical block or unavailable hardware. Include general inputs/protein/RBFE/statistics/release dependencies. Do not equate a new scheduler with full M05 closure.
- [ ] Make support claims machine-checkable by model/embedding/protocol/hardware/precision/ensemble/input profile. Existing accepted rows cite exact prior snapshot/profile; new rows say worker-tested, awaiting separately authorized review. Test that unrun GPU/large-sampling/physics claims cannot become “accepted” by completing a code checkbox.
- [ ] Freeze the G07 missing-reference task inventory: 19 full-parent plus 10 alternate-cap records, exact inputs/method/thresholds, all 46 preserved records, seven exceedances, original pilot failures and immutable receipts. Reuse hashes; do not regenerate data.
- [ ] Write a dry-run QM feasibility report using the preserved ledger: 2325.6446500519996 s charged, 84074.355349948 s remaining, existing continuation estimate 122992.52458401839 s, authorization false. Prepare the exact existing execution/ledger/interruption commands and required future resource decision. No reset/increase, relaxed threshold or QM launch.
- [ ] Prepare `environment/hpc/profile-template.json`, a profile checker and guarded parity/restart trial instructions. Require explicit cluster platform/CPU or device, driver/software/artifact identities, storage paths/type, allocation/threads/memory/time and checkpoint compatibility. Unknown details stay missing; do not guess a scheduler or add untested GPU support.
- [ ] Define the eventual small cluster trial: fixed-coordinate full energies/forces/both maps/parameters, actual device/precision, trusted offline load, checkpoint versus State meaning, interruption/resume, all histories/workers/both RNG streams, failure archive and local storage lock/rename/fsync behavior. Same-profile checkpoint continuation must match; portable-State initialization does not promise an identical stochastic path.
- [ ] Scripts default to validate/dry-run, never submit or resume old source under new code. Prepare unique run names, resource receipts, termination/budget guards and explicit input-dependent sample plans. Actual cluster trial and demanding runs require the user's later instructions.

## E5 — consolidated checks and final handover

- [ ] Run focused package/CLI/resource/support-matrix tests and the installed/offline checks. Preserve output and exact omissions. Do not create skipped tests merely to fill original planned gate names.
- [ ] Hand the frozen final code identity to the orchestrator for **one** full CPU `python -m pytest -q`, final docs self-test and whitespace checks. No per-worker full-suite baseline or extra compatibility run. Any real failure goes to its code owner with its original evidence preserved.
- [ ] Record one worker log and the support/resource/HPC documents, commit intended artifacts, and help produce `Before_HPC_vN_summary.md`. State that no independent review, remote publication, physical qualification or cluster run occurred.

**Done:** technical package and small local offline checks work, actual scoped CPU costs are recorded, original obligations are mapped, and guarded cluster/QM/sampling instructions are ready. G13 release/independent reproduction and hardware/physical requirements remain open where unperformed. Stop after reporting to the user.
