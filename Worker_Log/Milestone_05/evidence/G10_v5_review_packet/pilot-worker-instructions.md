# G10 implementation batch: serial solvated pilots and combined evidence

This draft executes only after the orchestrator supplies the completed core worker report, exact starting HEAD, and prior GREEN design audit. Do not start early or spawn agents. Model is `gpt-6-luna`, reasoning `max`.

## Scope, prerequisites, and files

Work in `/workspace/AToM_MLMM-g10` on `g10-engine-next`. Finish Task 4 and combined verification from `Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md`. Read AGENTS, the reviewed amendment/audit, relevant core worker report and interfaces, and the existing shared runner/fixture helpers. Create `tests/workflow/test_multistate_exchange_pilots.py`, update `examples/cloud_engine/README.md`, and produce the next unused G10 worker log/evidence provided by the orchestrator. Preserve core tests and existing pair API.

Use exact immutable `fixtures/solvated_fragment/v2/{abfe,rbfe}` inputs, prepared independently for this new source through `workflow.run_configuration`; do not resume an old sealed bundle using this checkout or import the v1 `water_run` fixture as if it were v2. Configuration overrides may only bound iteration/step/frame counts and fresh output paths, not chemistry, parameters, constraints, caps, maps, tolerance or physical definitions. Each preparation saves only a few frames. Keep the original 18-crown-6/methanol ABFE fixture unchanged; no host–guest RBFE input is requested here.

## Required pilot behavior and independent expectations

Run ABFE then unequal-ligand RBFE serially, each with exactly three stable actual workers, all three declared schedule states, ordered state pairs `((0,1),(1,2))`, two scheduling boundaries and one integration step per worker/boundary. Absolute pilot ceilings remain three workers, four boundaries, two steps/boundary. Use the same multistate APIs and pinned pair adapter as analytic controls. No parallel scientific jobs.

Expect six committed predecision samples and four pair attempts per two-boundary case. Check each sample's real-atom order/full-force shape (224 ABFE / 233 RBFE for these v2 controls), finite complete raw records, velocities, box, full state parameters, both-map geometry diagnostics, unique `(run,boundary,walker)` IDs and monotone per-walker sequences `[1,2]`. Preserve complete ligand membership and cap-parent forces. Validate each full permutation is a bijection and each pair resolves the actual current walkers, with unchanged unselected workers. Sample capture-time states remain separate from final assignments.

Independently reevaluate every attempted pair's four complete potentials from saved boundary coordinates on actual contexts (separate restored/fresh contexts when needed), compare the reduced-energy matrix and exponent within the unchanged 1e-8 energy/reconstruction tolerance, and include the existing nonzero outside anchor. Reconstruct the full schedule matrix from retained raw predecision records and compare with actual context energies; do not count a matrix-shape assertion alone as a numerical oracle. This new scheduling test does not requalify MACE chemistry or reopen unrelated accepted force FD reviews.

Demonstrate checkpoint restart from an identical copied committed prefix: stop after one boundary, fork that exact run/checkpoint/RNG history, continue both serially and compare committed IDs/raw observations/attempts/permutations/all-worker states/RNGs. Preserve the initial committed bytes. Optionally include one focused molecular pending rollback/replay if it adds coverage beyond deterministic core faults; do not run a redundant large fault matrix. All failures retain raw output/error records; no discarded samples or relaxed tolerance. Summaries must state technical-only scope and `binding_result=not_evaluated`; no uncertainty or affinity result.

## Resources and scientific safeguards

Every scientific shell activates the unchanged prefix:

```bash
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

Two CPU threads, Reference double/MACE CPU float64/NVT300K, 8GiB machine limit. Use serial jobs; record elapsed wall time and peak RSS for actual bounded pilots. No QM, GPU, new chemistry, extended solvent/protein sampling, Slurm/HPC scripts, dependency installation or package/weight replacement. Existing 46 G05 records, seven G07 sensitivity exceedances/pilot failures/29 missing references and QM ledger `2325.6446500519996 / 86400s`, false continuation screen stay unchanged. Full G10/M05, chemical accuracy, protein physics, equilibrium/mixing/convergence, affinity and exchanging-walker uncertainty remain open.

## Tests, logs and completion

Establish meaningful assertions and save the first new pilot test's actual failure before repair if a new defect is exposed; otherwise the core API already exists and a successful first integration check is not falsely labelled RED. Run changed pilot checks first. Repair only concrete defects necessary to fulfill this batch; if that requires core source changes, notify the orchestrator with the failing check and minimal scope before proceeding, then rerun affected core tests. Never implement another Hamiltonian/Metropolis path or weaken an approved definition.

When all implementation tasks are integrated and new focused checks pass, run the available full CPU suite on the combined source once. The final core worker has already run the required pair/export/restart command on its final production source: do not repeat that separate command merely for a new test/docs commit when source is unchanged; the full suite includes those same tests. If this pilot task makes a concrete necessary source repair, rerun the affected core checks and required compatibility command before the full suite, recording the reason.

```bash
python -m pytest tests/workflow/test_multistate_exchange_pilots.py -q
python -m pytest -q
python tools/check_docs.py --self-test
git diff --check
```

Keep raw RED/GREEN/focused/full output, actual counts/skips/statuses/durations, exact source/model/fixture/environment identities, pilot raw artifacts and hashes. Save complete sealed pilot attempts outside Git if large, and a small reproducible script plus hashed exports/compact raw evidence inside the assigned evidence folder; record exact local paths. No old evidence migrations. Audit must receive actual accessible raw pair/state/history artifacts, not only aggregate summary claims. Do not package duplicate restricted weights unnecessarily.

Write the next unused `Gate_10_vN_worker.md` with bounded task scope, actual model/effort, UTC finish, exact starting/source/result/report-only commits, changes and every verification outcome. Update STATUS with actual completed technical evidence pending final independent combined audit, never gate/milestone acceptance. The final auditor comes only after this whole batch is done. Commit your changes, no push/reset/rebase. Return status, commit, test counts, evidence paths, resource outcomes and concerns, then END your turn.
