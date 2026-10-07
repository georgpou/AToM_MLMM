# Before HPC Batch A v1 worker record

**Worker:** `gpt-6-luna/max`, inline packet execution, no subagents. **Scope:** A1–A3 only. **Finished:** 2026-10-07 11:11:57 UTC. No molecular pilot, QM, long MD, dependency substitution, full-suite run, audit, or independent review was performed.

## Identity and result

Checkout: `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`; starting planning child `42e3e318c2e90c09e16d9faa6461afd70df8c9cf`, descended from the reviewed/published base `4ad8ee835809325ceec8a017222415043347967d`. Implementation and STATUS are in source commit `8757c0e37cb7530eeb695b9db6576a6009a4debb`. At that commit, `src/atm_mlmm` contained 39 Python files; the recursive path-and-content manifest SHA-256 was `2488f04206441edf220fb910cdc009a3109e558f7e924cdc78e520a9a15d4fe8`.

The final packet command passed **84 passed, 0 failed, 0 skipped**, exit 0, in 92.05 seconds. Output: [focused-final.log](evidence/batch-a-v1/focused-final.log), SHA-256 `cb9f407131efe95224040f306e0006aed264d11905e341925a5aa3639bfff7eb`; observed completion was 2026-10-07 11:07:54 UTC. Exact command and environment:

```sh
cd /workspace/AToM_MLMM-before-HPC
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python -m pytest tests/workflow/test_restored_state_admission.py tests/workflow/test_engine_restart.py tests/workflow/test_persistent_exchange.py tests/workflow/test_worker_handover.py -q
```

The unchanged CPU profile was `/workspace/before-hpc-cpu-v2`, Python 3.11.16/OpenMM 8.6.1, under the 8 GiB cgroup limit. Parent setup validation at `logs/validation-20261007T105100Z-2151/results.json` records all nine checks at exit 0; this worker did not repeat environment setup validation.

The post-STATUS local documentation check exited 0: 256 Markdown files, 1,655 local links, and 57 external links intentionally not fetched, with no errors. Exact shell body:

```sh
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python tools/check_docs.py
```

Output is [docs-check-final.log](evidence/batch-a-v1/docs-check-final.log). This check validates local documentation links only.

## Repairs and coverage

`runtime_validation.py` adds dependency-light `verify_source_inventory(bundle_root, manifest_files, *, current_source_root)`, exact `portable_state_clock(xml)`, and observational `validate_restored_state(worker, *, state_id, portable_state_xml, expected_step_count, expected_time_ps, compare_portable_parameters=True)`. The worker loader, fixed-window continuation, pair exchange, and the existing multistate restoration path share these checks. Public signatures and return shapes of `resume_run`, `resume_exchange`, and `load_worker_run` remain unchanged.

Source inventory admission now rejects missing, extra, changed, escaped, symlinked, malformed, or hash-mismatched files before executable loading while allowing a byte-identical relocated bundle. Restart admission checks actual restored finite state and exact clocks, saved sample fields, both full maps/cap parents before evaluation, then refreshed raw energies and full real forces before stepping. Pair restart performs the corresponding portable/checkpoint, saved-row, geometry, and energy checks. Failure evidence remains passive and available.

The packet run includes the entire `test_persistent_exchange.py`; therefore the shared validator's affected multistate behavior was covered in that run, with no duplicate multistate run. The relevant nodes include `test_multistate_source_inventory_must_match_before_trusted_load`, `test_multistate_inert_admission_binds_runtime_and_initial_assignment`, `test_multistate_restore_rejects_actual_clock_mismatch_before_evaluation`, `test_multistate_guard_checks_actual_restored_coordinates_before_any_evaluation`, `test_multistate_inert_admission_rejects_tampered_artifacts_before_load`, `test_multistate_checkpoint_energy_is_refreshed_after_restore_before_integration`, `test_multistate_fresh_restore_compares_complete_total_before_next_integration`, and `test_multistate_restore_rejects_portable_parameter_disagreement_before_integration`. All other nodes in that file also passed.

The focused actual-artifact RED output is preserved in [focused-red-confirmed.log](evidence/batch-a-v1/focused-red-confirmed.log): **11 failed, 1 passed**, exit 1, 4.91 seconds. It reproduced the missing/extra/changed-source admissions, both mapped geometry cases, fixed-window and pair clock drift, and four saved-row mismatches; the valid-prefix continuation was the passing control. The original shell argument vector for this early targeted selection was not captured, but the output retains the exact 12 node IDs and tracebacks. One preceding collection-only attempt exited 4 because a new test had an invalid import; it was corrected before the behavioral baseline, and its output was overwritten by the next run, so that raw output is unavailable. No old failure was regenerated to recover it. The first broad four-file attempt is retained in [focused-green-attempt1.log](evidence/batch-a-v1/focused-green-attempt1.log): 72 passed/12 failed, exit 1, 79.67 seconds. It exposed test-fixture/assertion setup issues (portable parity and pair-manifest resealing), an assertion-placement error, and a legacy error-message expectation; those were corrected without loosening scientific thresholds. An intermediate geometry-fixture run is in [focused-fixcheck.log](evidence/batch-a-v1/focused-fixcheck.log), 12 passed/2 failed; the fixture was corrected to keep the portable State consistent with the modified native checkpoint. The focused post-fix check [focused-fixcheck-2.log](evidence/batch-a-v1/focused-fixcheck-2.log) passed 14/14, exit 0, 4.57 seconds.

No A1–A3 requirement remains uncovered. STATUS now records final G10 v8 bounded multistate acceptance, while keeping full M05 open and describing these older-path repairs as worker-tested on `before_HPC`, awaiting any later authorized independent review. No new gate acceptance is claimed. Implementation and STATUS are committed; this worker record and compact evidence are the following evidence commit.
