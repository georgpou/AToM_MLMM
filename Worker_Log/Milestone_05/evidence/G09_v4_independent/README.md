# Independent focused G09-R2 closure evidence

Reviewer: `gpt-6.1-sol`, MAX dispatch setting. Exact HEAD
`09a85d979fe9fce2ceca23da74509846254df9b1`; tested repair
`027f8173babc13606afb24d96f58148704e38b1b`.
The [audit](../../Gate_09_v4_audit.md) closes G09-R2 for scope and carries forward
the v3 bounded scientific amendment and G10-v1 pair boundary. Full gates/M05
remain open. No production, submitted test, specification, worker or STATUS
file was edited.

Commands ran serially from `/workspace/AToM_MLMM`:

```bash
source /workspace/atom-mlmm-g09-v3/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH=/workspace/AToM_MLMM/src
python -m pytest -q tests/workflow/test_failure_archive_errors.py tests/workflow/test_failure_geometries.py tests/workflow/test_engine_failure_retention.py tests/workflow/test_engine_restart.py Worker_Log/Milestone_05/evidence/cloud_v3_independent/probes.py::test_map_archive_failure_does_not_hide_original_scientific_error Worker_Log/Milestone_05/evidence/cloud_v3_independent/probes.py::test_nonfinite_failure_states_preserved_without_reentry --basetemp=/tmp/atom-mlmm-cloud-r2-independent-affected
python -m pytest -q Worker_Log/Milestone_05/evidence/G09_v4_independent/probes.py --basetemp=/tmp/atom-mlmm-cloud-r2-independent-probes
python Worker_Log/Milestone_05/evidence/G09_v4_independent/verify.py
```

- `affected.log`: exit 0, 21 passed in 39.92 s, no skips. Includes both original independent preservation contracts; excludes the obsolete defect-expecting CLI characterization.
- `probes.log`: exit 0, 6 passed in 1.51 s. Actual-worker compound failures, transient primary/final metadata write faults, nonfinite cached time and byte-preserving pre-existing-directory handling all pass.
- Four small scenario JSON files retain the actual normal CLI stderr, primary metadata and surviving-file names. The same original exception is asserted at the CLI boundary; compound secondary errors remain explicit.
- `verification.json`/`.log`: exit 0; 49 source/input/regression and 10 capture hashes match; source changes are exactly the two failure/CLI modules plus the regression. Physical definitions, inputs, builder, routing, adapter, tolerances, older scientific evidence, models and locks remain unchanged. Amendment status/decision text changed; its scientific body is equal.

The initial verification script treated the amendment's review-status update as
a scientific spec change. Inspection corrected this reviewer assumption;
the final verifier compares the scientific body separately. No production
failure arose. The submitted 501-test full suite was not repeated.
