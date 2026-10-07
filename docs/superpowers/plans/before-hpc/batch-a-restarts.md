# Batch A — restart admission and live status

**Worker:** gpt-6-luna/max; no subagents. Read the parent plan's global constraints, `AGENTS.md`, S07 loading/restart rules and the three review findings. No whole-repository onboarding.

**Purpose:** Repair B01–B03/RR-01–RR-03 and reconcile B04. The new multistate controller's v8 clock, atomicity and rollback repairs remain accepted within their original scope; the new defects affect the older fixed-window/pair entry points.

**Files:** Modify `src/atm_mlmm/workflow.py`, `adapters/atom.py`, and the older controller portions of `exchange.py`; use `persistence.py`/`exchange_journal.py` only where a shared check needs them. Create `src/atm_mlmm/runtime_validation.py` for shared admission checks if this avoids duplicate logic. Extend `tests/workflow/test_engine_restart.py`, `test_persistent_exchange.py`, `test_worker_handover.py`; create `test_restored_state_admission.py`. Update live `docs/project-0/STATUS.md`.

**Interfaces:** Preserve `resume_run`, `resume_exchange`, `load_worker_run`, checkpoint versus portable-State semantics and public return shapes. Other batches rely on those APIs. A source helper, if created, is `verify_source_inventory(bundle_root: Path, manifest_files: Mapping[str, str], *, current_source_root: Path) -> None`; it imports no scientific backend. A state helper may be `validate_restored_state(worker, *, state_id: str, portable_state_xml: str, expected_step_count: int, expected_time_ps: float) -> Snapshot`; compare the additional saved-row fields at the controller that knows their phase/units.

## A1 — complete source identity, before loading executable artifacts

- [ ] Write `test_missing_bundled_source_rejects_before_load`: make a fresh seven-atom fixed-window prefix; remove only `runtime/source/atm_mlmm/chemical_reference.py` from the manifest, recompute manifest/metadata bindings, then instrument loading/execution. Expected: `IdentityError`, zero load/execute calls. The original review admitted 37/38 modules.
- [ ] Add corresponding extra-entry, changed-byte and identical-relocated-bundle cases. Discover the current complete recursive `.py` set; do not hardcode 38, because this batch may add a module. Check declared/current/bundled sets, containment and hashes.
- [ ] Run the new nodes once to establish the meaningful failures; keep output. Then share the existing complete-inventory logic used by exchange instead of maintaining a weaker fixed-window loop. Apply the complete check to trusted worker loading as well, before deserialization.
- [ ] Preserve `trusted=False` rejection and path relocation. Source identity is content-based; moving a byte-identical bundle is allowed. A changed source tree creates a new run, not a migration of an old sealed prefix.

## A2 — actual restored state and full mapped geometry

- [ ] Write `test_invalid_restored_geometry_rejects_before_step`: restore a real checkpoint whose ligand `b1` exactly overlaps a protein atom, preserving consistent file hashes. The existing domain check independently gives map0 Bondi ratio 0 below 0.65. Step and energy sentinels must remain uncalled; passive State capture/failure preservation is allowed.
- [ ] Write fixed-window and pair `test_restored_checkpoint_time_must_match_saved_state`: after one 0.0005 ps step, change checkpoint time alone from 0.0005 to 1.0005 ps and update its declared digest, leaving row/portable State unchanged. Expected: reject before stepping. Original behavior completed step 2 at 1.001 ps.
- [ ] Add a small valid continuation control and one coordinates/velocities/box/parameters mismatch parameterization. Use actual native checkpoint/State bytes, not only mocked report dictionaries. Validate the saved artifact's internal consistency and the actual restored Context.
- [ ] Implement the admission order: verify artifacts/profile → load trusted worker → restore → capture finite actual coordinates/velocities/box/parameters/clocks → compare with the correct saved phase → check both full maps and cap parents → refresh energy/full real forces and compare required saved records → step. Do not let an energy evaluation precede geometry admission.
- [ ] Exact saved/actual step and time equality is distinct from the elapsed-time roundoff envelope. Reuse the finite outward-rounded v8 envelope where elapsed time is checked; do not introduce `isclose` for exact clocks, reject valid large-origin stagnation, or rerun long repeated-addition/MD proofs.
- [ ] Reuse the v8 restored-state checks where appropriate, without blindly comparing pre-swap parameters to post-swap assignment. Energy parity must include raw endpoints, outside and total; forces cover every influencing real atom. Keep existing unit-conversion allowances, never broaden tolerances.
- [ ] Check preserved failure output and valid continuation histories/RNG behavior. Do not alter commit/rename/rollback semantics to fix these admission defects; if shared code changes touch multistate admission, run its affected inert-rejection regressions.

## A3 — focused verification and truthful status

- [ ] Run `python -m pytest tests/workflow/test_restored_state_admission.py tests/workflow/test_engine_restart.py tests/workflow/test_persistent_exchange.py tests/workflow/test_worker_handover.py -q` after changes. Add only affected multistate nodes if that code changed. Use the existing tiny controls; no new molecular pilot is needed.
- [ ] Reconcile STATUS's lower Next work/M05 row with final v8 bounded acceptance. Record these older-path repairs as worker-tested on the new branch and awaiting any later authorized independent review. Preserve v5/v7 RED and v8 GREEN historical files.
- [ ] Commit the intended changes, write `Batch_A_vN_worker.md` with exact tests and source identity, and hand over the public APIs unchanged plus the shared-helper signatures. No audit and no full-suite run at this batch boundary; the user-selected consolidated run follows E.

**Done:** all three original contradictions reject before the affected operation; a valid fresh prefix still continues; relocation/trust/failure preservation remain intact. If a reproduction file is unavailable, the explicit recipe above is sufficient; do not spend a worker recovering all old artifact trees.
