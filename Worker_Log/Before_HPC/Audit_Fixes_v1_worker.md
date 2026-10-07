# Before-HPC audit fixes v1 worker

Implemented F1–F5 on `before_HPC`, based on `a78af5ce9c74f09c8ddeba373187c99a7f72035b`. The staged code/test/status patch has stable patch ID `f36279166d5cc33b371cc4fee718b3f0b56aef4a`. The local commit and frozen tree identity are reported to the parent agent.

F1 now derives persistent initialization identity from the saved per-worker initial State bytes, integrator seed stream, runtime identity, and initial host RNG artifact. Run, walker, and sample IDs do not contribute. The bounded producer-to-analyzer control rejects repeated streams despite changed run/walker IDs and a different prose claim; separate host-RNG-only, integrator-seed-only, and prepared-state controls produce distinct identities. It uses three workers, two boundaries, one step per boundary. F2 validates typed profile fields, positive resources, storage/checkpoint safeguards, and all profile artifact hashes against the verified bundle bytes; the CLI now verifies the supplied bundle directory. `environment/hpc/run-guide.md` documents the required bundle identity format and interface. F3 compares declared, current, and recursively enumerated bundled Python source sets, rejecting undeclared files and symlinks while retaining relocation. F4 requires each physical-solvent stage to include every declared force owner exactly once. F5 distinguishes missing fields from explicit `system.periodic_box_nm: null`, empty `system.constraints`, and empty `model.permitted_c_c_cuts`; the complete existing-fixture manifest remains input-only with no binding or production acceptance.

Focused controls were run with the required CPU activation and thread environment. The final bounded compatibility command was:

```bash
pytest -q tests/workflow/test_persistent_initialization_provenance.py \
  tests/sampling/test_exchange_uncertainty.py::test_mislabeled_iid_histories_and_reused_initializations_are_rejected \
  tests/sampling/test_exchange_uncertainty.py::test_independent_run_resampling_keeps_complete_runs_without_nested_blocks \
  tests/workflow/test_persistent_exchange.py::test_multistate_source_inventory_must_match_before_trusted_load \
  tests/workflow/test_runtime_source_inventory_recursive.py \
  tests/environment/test_hpc_profile.py \
  tests/workflow/test_protein_input_admission.py
```

The final run at `2026-10-07T19:32:25Z` exited `0`: **27 passed**, no skips, in 10.00 seconds. An isolated F1 control run at `19:30:01Z` exited `0` (**1 passed** in 7.26 seconds); the final compatibility run also includes the later label-independence assertion. Every test shell sourced `/workspace/before-hpc-cpu-v2/activate.sh` and exported `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. Exact outputs and per-finding RED/GREEN receipts are under `evidence/audit-fixes-v1/`.

The original controls failed as intended: F1 did not reject duplicate persistent initialization; F2 had **7 failures / 2 passes** on typed contradictions, format-only readiness, and modified bundle bytes; F3 accepted an undeclared nested Python file; F4 accepted empty and partial stage-owner lists (**2 failures / 1 complete-owner pass**); F5 blocked the complete manifest and named the three explicit values as missing. During F5 test construction, one incomplete fixture initially lacked the inventory identity required by the existing loader, and the next run exposed JSON serialization of frozen `MappingProxy` provenance. The fixture now derives the unchanged system inventory from its existing serialized System, and provenance equality handles immutable mappings and tuples. An early F1 test-chain attempt also failed while deliberately rewriting a journal metadata record without resealing its chain; that harness attempt was discarded. These were setup/diagnostic failures, not remaining source failures.

C3 remains a separate open gap. No physical endpoint definitions were invented, and no scientific or release hold changed. No cluster job, production sampling, QM, GPU, scheduler, package rebuild, or full suite replay was run. STATUS now points to this worker record and no longer says to pause before Batch B; it does not claim independent acceptance.
