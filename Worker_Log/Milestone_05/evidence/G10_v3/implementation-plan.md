# G10 multistate runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded, serial CPU controller that runs an explicit connected sweep over three to eight schedule states while preserving the accepted pair API and committing each full worker boundary atomically.

**Architecture:** New versioned APIs in `exchange.py` own stable walkers, sequential integration, current-permutation resolution, and calls to the existing pair adapter. `exchange_journal.py` validates a hash-sealed boundary prefix and publishes or rolls back one complete boundary; per-worker sample staging and per-attempt permutation/phase records remain inert until commit.

**Tech Stack:** Python, OpenMM Reference double, pinned AToM 8.5.0b0 pair adapter, NumPy legacy RNG, pytest, existing locked CPU/MACE environment.

**Spec:** `docs/project-0/specs/g10-multistate-runtime-amendment.md`

## Global Constraints

- Declare 3–8 distinct sealed schedule-state IDs and a connected ordered sweep of distinct unordered state-index pairs; maximum 28 attempts per sweep.
- Use at most 8 simultaneous actual worker contexts; solvated pilots use 3 workers, at most 4 boundaries, at most 2 integration steps per boundary, and only a few prepared frames.
- Use one 300 K Reference/CPU NVT Hamiltonian/runtime/model/force-field/constraint/map identity and the existing pinned `attempt_pair_exchange` for every pair decision.
- Persist full real forces, raw energy fields, high-precision coordinates, full walker-to-state permutations, and both Python/NumPy legacy RNG states.
- Admit history, hashes, exact recursive Python-source inventory, permutations, samples, phases, RNGs, checkpoints, and mode before trusted executable load.
- Preserve the existing `run_exchange` / `resume_exchange` API and pair regressions; frozen source bundles use their exact source and cannot migrate.
- Keep the accepted physical Hamiltonian, caps, maps, units, forces, tolerances, package locks, model bytes, and 46 G05 records unchanged.
- Preserve the seven G07 sensitivity exceedances, pilot force failures, 29 missing references, and the QM ledger charged `2325.6446500519996 / 86400 s`; do not run QM, production, GPU, or HPC jobs.
- A successful design audit is a prerequisite to implementation. A technical scheduler result does not accept complete G10/M05, molecular accuracy, affinity, equilibrium, mixing, convergence, or exchanging-walker uncertainty.

## Review Focus

- A later ordered pair resolves walkers from the full permutation after the prior decision; `tests/workflow/test_persistent_exchange.py::test_multistate_sweep_resolves_overlapping_pairs_after_each_accept`.
- A partial worker integration leaves already-produced sample/State/checkpoint evidence staged and excluded from analysis until exact whole-boundary replay; `tests/workflow/test_persistent_exchange.py::test_partial_integration_stages_worker_zero_and_replays_entire_boundary`.
- A corrupted journal or source inventory is rejected before any trusted worker loader runs; `tests/workflow/test_persistent_exchange.py::test_multistate_inert_admission_rejects_tampered_artifacts_before_load`.
- A failure after rename or during summary rebuild keeps the sealed boundary authoritative; `tests/workflow/test_persistent_exchange.py::test_multistate_postrename_failure_keeps_boundary_authoritative`.
- Pair matrices include nonlinear state energy and state-dependent outside energy after every parameter refresh; `tests/workflow/test_replica_exchange.py::test_multistate_decision_uses_fresh_nonlinear_outside_energies`.

---

## File and interface map

- Modify `src/atm_mlmm/exchange.py`: add `run_multistate_exchange(prepared_run: Path, output: Path, *, state_ids: Sequence[str], state_pairs: Sequence[tuple[int, int]], boundaries: int, steps_per_boundary: int, seed: int, trusted: bool = False, stop_after_boundaries: int | None = None) -> dict[str, object]`, `resume_multistate_exchange(directory: Path, *, trusted: bool = False, stop_after_boundaries: int | None = None, recover_pending: bool = False) -> dict[str, object]`, and reuse the existing `attempt_pair_exchange` without editing its decision logic or signature.
- Modify `src/atm_mlmm/exchange_journal.py`: add `read_multistate_boundaries(directory: Path, *, allow_pending: bool = False) -> list[dict[str, object]]`, recursive artifact sealing/verification, complete mode/history/source admission, and whole-boundary pending preservation. Keep pair reader semantics for pair mode.
- Keep `src/atm_mlmm/adapters/atom.py`, `src/atm_mlmm/workflow.py`, and `src/atm_mlmm/persistence.py` unchanged unless a focused regression proves a narrowly scoped shared helper is required; do not duplicate adapter logic.
- Modify `tests/workflow/test_persistent_exchange.py` for scheduling, staging, transactions, admission, replay, and fault cases.
- Modify `tests/workflow/test_replica_exchange.py` for actual-context energy/parameter checks and independent nonlinear/outside accept/reject thresholds.
- Create `tests/workflow/test_multistate_exchange_pilots.py` using existing `water_run` fixtures from `tests/workflow/test_solvated_handover.py` and `fixtures/solvated_fragment/v2/{abfe,rbfe}`; run serially.
- Update `examples/cloud_engine/README.md` with the new API's bounded use, versioned resume, and pilot limits. Do not add a CLI unless implementation review finds a concrete requirement that cannot be met through the specified API.

## Task 1: Inert admission, limits, and source identity

**Files:** `src/atm_mlmm/exchange.py`, `src/atm_mlmm/exchange_journal.py`, `tests/workflow/test_persistent_exchange.py`.

**Interfaces:** The reader verifies `mode="persistent-multistate-exchange-v1"` and returns the committed inert boundary prefix before worker construction. The new APIs validate the ordered state IDs/pair sweep against the sealed schedule and reject pair-mode input. Source admission compares exact recursive `.py` paths under `src/atm_mlmm` with `worker/manifest.json`, then checks every hash.

- [ ] **Step 1: Add failing tests** `test_multistate_admission_requires_connected_three_to_eight_schedule_states`, `test_pair_and_multistate_modes_cannot_resume_each_other`, and `test_multistate_source_inventory_must_match_before_trusted_load` in `tests/workflow/test_persistent_exchange.py`. Assert rejection for 2/9 states, repeated IDs, missing/out-of-range indices, disconnected or duplicate edges, non-300 K input, pair metadata, a missing bundled source path, and a changed digest; monkeypatch `load_worker_run` to fail if called before any rejection.
- [ ] **Step 2: Run the RED nodes** with `python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_admission_requires_connected_three_to_eight_schedule_states tests/workflow/test_persistent_exchange.py::test_pair_and_multistate_modes_cannot_resume_each_other tests/workflow/test_persistent_exchange.py::test_multistate_source_inventory_must_match_before_trusted_load -q`. Expected: missing multistate API/reader and missing inventory/mode rejection.
- [ ] **Step 3: Implement the new argument validator and inert reader** in the two source modules. Preserve pair public signatures and require complete source-inventory set equality before trusted loads.
- [ ] **Step 4: Rerun the three RED nodes**; expected: each rejection assertion passes and the trusted-loader spy remains uncalled.

## Task 2: Serial sweep, identity history, and fresh pair matrices

**Files:** `src/atm_mlmm/exchange.py`, `tests/workflow/test_persistent_exchange.py`, `tests/workflow/test_replica_exchange.py`.

**Interfaces:** `run_multistate_exchange` creates one context for each stable walker. It integrates each worker once per boundary, records the capture-time `state_id`, and then calls `attempt_pair_exchange` with the two workers found by resolving each ordered state pair against the current full permutation. The adapter's report is nested under a uniquely indexed attempt record; the scheduler only updates state-label assignments from its `accepted` flag.

- [ ] **Step 1: Add failing scheduler tests** `test_multistate_sweep_resolves_overlapping_pairs_after_each_accept` and `test_multistate_sample_state_is_distinct_from_final_assignment` in `tests/workflow/test_persistent_exchange.py`. For initial `[0,1,2]` and pairs `[(0,1),(1,2)]`, force both pair calls accepted; assert the workers are `(0,1)` then `(0,2)`, the intermediate permutation is `[1,0,2]`, final permutation is `[2,0,1]`, and boundary sample state IDs stay `[0,1,2]`.
- [ ] **Step 2: Run the RED nodes** with `python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_sweep_resolves_overlapping_pairs_after_each_accept tests/workflow/test_persistent_exchange.py::test_multistate_sample_state_is_distinct_from_final_assignment -q`. Expected: missing scheduler/history behavior.
- [ ] **Step 3: Add failing adapter/oracle tests** `test_multistate_decision_uses_fresh_nonlinear_outside_energies` and `test_multistate_actual_adapter_accept_and_reject_thresholds` in `tests/workflow/test_replica_exchange.py`. For both ABFE and unequal-ligand RBFE analytic controls, independently compute all four actual-context reduced energies at beta `1 / (0.00831446261815324 * 300)`, include nonlinear ATM terms and a nonzero outside term, compare matrix/exponent/raw entries, and control actual adapter draws below/above `exp(-delta)`.
- [ ] **Step 4: Run the RED adapter/oracle nodes** with `python -m pytest tests/workflow/test_replica_exchange.py::test_multistate_decision_uses_fresh_nonlinear_outside_energies tests/workflow/test_replica_exchange.py::test_multistate_actual_adapter_accept_and_reject_thresholds -q`. Expected: missing multistate integration; existing pair decision nodes still pass unchanged.
- [ ] **Step 5: Implement the sequential controller** in `exchange.py`; integrate once per worker, preserve immutable sample-time assignment, resolve every state pair immediately before the adapter call, isolate both host RNGs, and store all pair reports/permutations. Do not alter `attempt_pair_exchange` or its four-context-evaluation behavior.
- [ ] **Step 6: Rerun the four scheduler/oracle nodes**; expected: overlap mapping, sample-state separation, fresh outside-inclusive 2-by-2 energies, parameter refresh, and both forced decisions pass.

## Task 3: Durable boundary staging, commit, and replay

**Files:** `src/atm_mlmm/exchange.py`, `src/atm_mlmm/exchange_journal.py`, `tests/workflow/test_persistent_exchange.py`.

**Interfaces:** A pending boundary stages each worker's sample/raw record, portable State, and checkpoint before the next integration. Each attempt persists its resolved pair, full before permutation, callback phase files, and full after permutation before the next pair. A committed directory rename is the only analysis-insertion point. `resume_multistate_exchange(..., recover_pending=True)` archives pending evidence and replays from the previous all-worker checkpoint/permutation/Python+NumPy RNG boundary.

- [ ] **Step 1: Add failing partial-integration test** `test_partial_integration_stages_worker_zero_and_replays_entire_boundary`. Fail worker 1 after worker 0 completes one integration and is durably staged. Assert the pending tree includes worker 0's unique sample/raw/full-force record, portable State, and checkpoint plus independent cached failure captures for all workers; no report or committed prefix includes the staged sample; default resume does not mutate the tree; explicit rollback archives its hashes/errors and recreates the reference boundary with identical committed IDs, decisions, permutations, checkpoints, and RNG states.
- [ ] **Step 2: Run that RED node** with `python -m pytest tests/workflow/test_persistent_exchange.py::test_partial_integration_stages_worker_zero_and_replays_entire_boundary -q`. Expected: missing multistate staging/replay contract.
- [ ] **Step 3: Add failing phase and publication tests** `test_multistate_phase_persistence_failure_rolls_back_whole_sweep`, `test_multistate_capture_seal_and_precommit_failures_do_not_publish`, and `test_multistate_postrename_failure_keeps_boundary_authoritative`. Inject `evaluated`, `decision`, and `refreshed` writes in the first and later pair, final capture/checkpoint, seal, rename, parent fsync after rename, and derived report failures. Assert each pending attempt retains full before/after provenance available at failure; pre-rename has no commit, post-rename has a verified authoritative commit.
- [ ] **Step 4: Run those RED nodes** with their exact `pytest` node IDs. Expected: missing atomic boundary and per-attempt history behavior.
- [ ] **Step 5: Add failing integrity/ownership test** `test_multistate_inert_admission_rejects_tampered_artifacts_before_load`, parametrized over permutation, sample ID/sequence, RNG, phase, and checkpoint tampering, plus `test_multistate_lock_rejects_concurrent_controller`. Assert validation runs before the trusted-loader spy and default pending rejection preserves bytes exactly.
- [ ] **Step 6: Run those RED nodes** with `python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_inert_admission_rejects_tampered_artifacts_before_load tests/workflow/test_persistent_exchange.py::test_multistate_lock_rejects_concurrent_controller -q`. Expected: missing complete hash/history admission.
- [ ] **Step 7: Implement recursive transaction sealing/verification and whole-boundary replay** in `exchange_journal.py` and `exchange.py`. Stage and fsync each sample and each attempt history before proceeding; retain primary and secondary archive errors independently for every worker without energy/force reentry; only build `EvaluationRecords`, observations, and summary from the sealed prefix.
- [ ] **Step 8: Run all new Task 3 nodes**; expected: exact replay with stable IDs/permutations/both RNGs, inert tamper rejection, no-mutation default rejection, and correct rename commit semantics.

## Task 4: Shared-engine solvated pilots and usage record

**Files:** `tests/workflow/test_multistate_exchange_pilots.py`, `examples/cloud_engine/README.md`.

**Interfaces:** Use `run_configuration` from existing `water_run` fixture preparations, then call `run_multistate_exchange(prepared_run, output, state_ids=all_three_schedule_ids, state_pairs=((0,1),(1,2)), boundaries=2, steps_per_boundary=1, seed=...)`. Run one ABFE and one unequal-ligand RBFE case serially. No chemistry, fixture, force-field, or preparation change is part of the pilot.

- [ ] **Step 1: Add failing pilot node** `test_solvated_abfe_and_unequal_rbfe_multistate_pilot` in `tests/workflow/test_multistate_exchange_pilots.py`, parameterized by the existing fixture. Assert three stable walkers, two committed boundaries, one integration step per worker/boundary, full real-force/raw sample fields, a connected pair history with valid permutations, unique per-boundary sample IDs, and `binding_result == "not_evaluated"`.
- [ ] **Step 2: Run the pilot node** with `python -m pytest tests/workflow/test_multistate_exchange_pilots.py::test_solvated_abfe_and_unequal_rbfe_multistate_pilot -q`. Expected before code: missing controller API; later expected result is two serial fixture cases passing under the limits.
- [ ] **Step 3: Update the cloud engine README** with the exact API call, state-pair indexing, versioned resume/explicit rollback, 3–8 state/eight-context bound, and technical-only pilot caveat.
- [ ] **Step 4: Rerun the pilot node**; expected: both existing v2 water fixtures pass with three contexts, two boundaries, and one integration step per boundary.

## Combined verification and handoff

- [ ] Run the new focused nodes once after implementation is integrated; do not repeat tests for every edit.
- [ ] Run the required pair regression command from the repository root after locked CPU activation: `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q`. Expected: existing pair, offline, restart, and export regressions pass unchanged alongside multistate checks.
- [ ] Run the available full CPU suite once on the same combined source snapshot: `python -m pytest -q`. Record actual counts, skips, durations, and environment identity; any skip remains unqualified.
- [ ] Run `python tools/check_docs.py --self-test`; record actual output.
- [ ] Stop and hand the exact combined diff, hashes, task log, and focused evidence to one independent `gpt-6.1-sol / max` audit. Do not repair during an active audit. An audit may accept only the scoped implementation; full G10/M05, exchanging-walker statistics, molecular accuracy, and affinity remain unqualified.
