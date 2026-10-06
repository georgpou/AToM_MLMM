# G10 implementation batch: core scheduling and boundary transactions

This brief is a draft until the orchestrator supplies the exact starting HEAD and completed GREEN design audit. Do not execute it before that handoff.

## Task and prerequisites

Implement Tasks 1–3 of `Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md` in `/workspace/AToM_MLMM-g10`, child branch `g10-engine-next`. Read the reviewed amendment, its matching design audit, AGENTS, and only the relevant source/tests. The standalone design must be GREEN before code starts. The orchestrator supplies the exact starting commit; verify it and a clean worktree. You are the only worker; do not spawn agents. Model is `gpt-6-luna`, reasoning `max`.

Deliver an admitted 3–8-state serial controller using the existing actual AToM pair adapter, durable all-worker boundary commits, and deterministic analytic/fault regressions. The later worker owns the new solvated pilots and usage documentation; do not run those pilots in this task. Complete all three tightly related core tasks before reporting. No intermediate audit is needed.

## Files and contract

- Implement additive multistate APIs in `src/atm_mlmm/exchange.py` and inert multistate transaction/history validation in `src/atm_mlmm/exchange_journal.py` with the exact reviewed signatures/mode/artifact layout.
- Preserve `run_exchange`, `resume_exchange`, existing pair journal semantics and their tests. Strengthen shared source admission as required by the design so a missing/new `.py` path rejects, not merely changed hashes among old listed paths.
- Add focused tests to `tests/workflow/test_persistent_exchange.py` and `tests/workflow/test_replica_exchange.py`. A dedicated new core test file is acceptable only if it keeps the reviewed nodes/import contracts explicit; record the choice.
- Reuse `adapters.atom.attempt_pair_exchange`, `load_worker_run`, the existing full-force/raw records, geometry and failure helpers. Do not implement another Hamiltonian or acceptance rule. Keep adapter/workflow/persistence unchanged unless a concrete intended failing regression proves a narrow helper change is necessary; explain it before widening scope.

## Independent expected behavior

Ordered STATE pairs `(0,1)` then `(1,2)`, both accepted, resolve worker indices `(0,1)` then `(0,2)` and transform the full walker assignment `[0,1,2] -> [1,0,2] -> [2,0,1]`. Sample-time states remain `[0,1,2]`. Coordinates, velocities, worker identity and walker identity never exchange. Include reject paths and more than one boundary.

Each pair must freshly evaluate all four complete actual-context energies after parameters change. For analytic ABFE and unequal-ligand RBFE, use the independent `tests/analytic_oracle.py` physical/mapping/nonlinear/outside expectations, with a nonzero existing outside anchor. Reduced energies are complete energy divided by `0.00831446261815324 * 300`. Independently check `delta=v_i(y)+v_j(x)-v_i(x)-v_j(y)` and control actual upstream draws on opposite sides of `exp(-delta)` for a demonstrably positive delta. Poison prior cached states/reports and check current actual parameters/refreshed totals. Do not make a production Metropolis implementation to obtain the expected value.

At each boundary, integrate each walker once sequentially and durably stage its sample/raw/full-force record, State and checkpoint before starting the next. Then execute ordered pairs at fixed coordinates, resolving the inverse permutation each time and persisting each attempt's before/after full assignment and indexed evaluated/decision/refreshed phases. One sealed recursive tree commits all final worker States/checkpoints and both host RNGs by directory rename plus fsync. Only the verified committed prefix contributes to EvaluationRecords/observations/summary. Check unique IDs, per-walker monotone sequences, complete schedule reconstruction, and caller global RNG isolation.

Admission is inert before executable loading: validate limits, exact mode, connected unique edges, schedule membership/temperature/runtime, manifests, recursive source inventory, chain, artifact layout/hashes, phase agreement, sample IDs/sequences, full permutations, matrix arithmetic and RNG documents. After trusted checkpoint restoration, freshly compare complete saved raw/total observations before integration. Both mode directions reject. Old frozen bundles never silently migrate; freshly exported current-source bundles retain pair compatibility.

## Fault and replay expectations

Cover partial integration of worker1 after worker0's successful durable staging, and first/later pair evaluated/decision/refreshed persistence failures. Cover final State/checkpoint capture, seal, precommit rename, postrename parent fsync, records/observations/summary derived writing, tampered identities/RNG/phases/checkpoints/source inventory, and nonblocking controller ownership.

For precommit failures, retain successful staged records plus cached failure captures on every worker and both mapped States without energy/force reentry. Preserve the original exception and secondary archive failures. Default resume rejects pending work without changing any bytes. Explicit rollback preserves the entire failed tree and its hashes, restores ALL previous worker checkpoints/full permutation/both host RNGs and replays the WHOLE boundary. Compare replay with a reference fork copied from the exact same committed boundary, never independent minimizations or unrelated initial RNG states. Verify committed raw records/decisions/permutations/checkpoints/RNGs, unique IDs, no lost/duplicate samples, unchanged committed prefix bytes. A completed rename is authoritative even if reporting/fsync then fails; revalidate and rebuild on resume.

## Protected invariants and resource limits

Preserve physical energy definitions, caps/parents, complete ligand membership, fixed ML, full real forces including MM, both-map guards, maps, constraints, masses, units, signs, tolerances, locked packages, model bytes, fixture bytes and scientific/reference receipts. No QM, GPU, new chemistry, HPC scripts or production. The 46 G05 references and G07 seven sensitivity failures/pilot force failures/29 missing references remain unchanged; QM ledger `2325.6446500519996 / 86400 s`, continuation screen false. Raw reconstruction is permitted; exchanging-walker uncertainty and binding estimates remain unqualified.

Every scientific shell:

```bash
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

Use serial pytest, two CPU threads, small analytic controls (normally three workers), at most four boundaries/two steps per boundary in runtime tests. No parallel jobs. Eight GiB machine memory cap; record any failure and stop the offending job if memory becomes unsafe. Do not install or change dependencies.

## Verification and deliverables

Establish independent expectations and run focused RED tests before implementing each missing behavior; save exact commands and actual intended failures. Missing dependencies do not count as RED. Run the new analytic/fault checks after implementation and the required existing pair/export/restart regression command:

```bash
python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q
python tools/check_docs.py --self-test
git diff --check
```

The completed implementation batch will run the full CPU suite after the later pilot task; do not duplicate it per intermediate edit. Report any required test failure as unfinished and repair within this task's defined scope. Do not waive assertions or loosen tolerances.

Use the next unused `Worker_Log/Milestone_05/Gate_10_vN_worker.md` provided by the orchestrator and matching evidence directory. Record base, source/result/report-only commits, actual model/effort, UTC completion, changed files, RED/GREEN commands, output logs, limits, open findings and next task. Include a source/test hash manifest or exact committed snapshot, and a compact completion report. Update STATUS only with actual core implementation evidence, no acceptance; don't rewrite earlier worker/audit logs. Commit only your changes, no push/reset/rebase. Finish with status, commit, test counts, evidence paths and concerns, then END your turn. The orchestrator must receive final completion before starting the pilot worker.
