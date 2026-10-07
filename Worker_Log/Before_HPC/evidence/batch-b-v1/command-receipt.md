# Batch B command receipt

Checkout: `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`, base HEAD `9dc4758caa7e51efc1df76c59688d739098a422c`. Commands used the already validated `/workspace/before-hpc-cpu-v2` environment; no setup validation or baseline suite was repeated. Scientific shell prefix:

```sh
cd /workspace/AToM_MLMM-before-HPC
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

Identity snapshot at final focused checks: Python 3.11.16; OpenMM 8.6.1; NumPy 2.4.6; torch 2.8.0; mace-torch 0.3.16; atom-openmm 8.5.0b0; x86_64. Approved MACE checkpoint SHA-256: `165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`. Fixture identities are in [the worker record](../../Batch_B_v1_worker.md).

## Final checks

| UTC | Exact command | Result | Preserved output |
|---|---|---|---|
| 2026-10-07 11:45:53 | `pytest -q tests/contracts/test_general_input_admission.py tests/integration/test_cap_collections.py tests/unit/test_partition.py tests/integration/test_boundary_ledger.py` | exit 0; 30 passed, 0 skipped, 16.74 s | `focused-b-attempt2.log` |
| 2026-10-07 11:47:22 | `pytest -q tests/integration/test_link_geometry.py tests/workflow/test_worker_handover.py` | exit 0; 28 passed, 0 skipped, 15.13 s | `single-cap-compat-attempt3.log` |
| 2026-10-07 11:48:32 | `pytest -q tests/integration/test_cap_collections.py::test_approved_mace_two_cap_fixed_coordinate_parent_derivatives` | exit 0; 1 passed, 0 skipped, 5.61 s | `mace-two-cap-attempt3.log` |
| 2026-10-07 11:51:06 | `python Worker_Log/Before_HPC/evidence/batch-b-v1/mace-two-cap-crosscheck.py` | exit 0; two actual MACE caps; 18 parent/environment components at each step; RMS error `0.161319` at `1e-4 nm` and `0.001613` at `1e-5 nm`, versus scaled S06 limit `1.366496` | `mace-two-cap-attempt4.log` |
| 2026-10-07 11:38:55 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_bounded_restart_through_common_runner_in_fresh_process` | exit 0; 1 passed, 0 skipped, 13.02 s | `common-restart-attempt5.log` |
| 2026-10-07 11:37:04 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_alchemical_bundle_trusted_reload_in_fresh_process` | exit 0; 1 passed, 0 skipped | `fresh-reload-attempt1.log` |
| 2026-10-07 11:44:48 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_ledger_and_nonidentity_particle_mapping` | exit 0; 1 passed, 0 skipped | `collection-controls-attempt7.log` |

`git diff --cached --check -- . ':(exclude)Worker_Log/Before_HPC/evidence/batch-b-v1/*.log'` returned exit 0. Raw pytest outputs remain byte-for-byte and contain whitespace from traceback context lines. No skipped tests were reported in the final checks. The test harness emitted only the expected optional cuequivariance-unavailable notice while loading MACE; the approved CPU MACE path still completed.

## Preserved red and diagnostic attempts

All output files below are unique and retained. Earlier commands used the same activation/thread prefix above. “Deselected” tests are not skips.

| UTC | Test selection / command | Result and observed issue | Output |
|---|---|---|---|
| 11:23:19 | `pytest -q tests/contracts/test_general_input_admission.py` | exit 1; 3 failed, 1 passed. Red admission controls showed missing component-state propagation and unsupported collection/mixed input. | `red-input-admission-attempt1.log` |
| 11:27:27 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_collection_probe_matches_independent_per_edge_force_oracle` | exit 1; 1 failed. Expected pre-implementation import failure for `atm_mlmm.models.analytic_caps`. | `red-cap-collection-probe-attempt1.log` |
| 11:28:33 | `pytest -q tests/contracts/test_general_input_admission.py tests/integration/test_cap_collections.py` | exit 1; 5 failed, 2 passed. The interleaved topology builder and explicit state path were not implemented yet. | `admission-collection-attempt1.log` |
| 11:29:09 | same command | exit 1; 4 failed, 3 passed. Exposed the noncontiguous-residue topology limit and a fixture assertion/unit mistake. | `admission-collection-attempt2.log` |
| 11:29:19 | same command | exit 0; 7 passed, 0 skipped. | `admission-collection-attempt3.log` |
| 11:30:12 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_parent_cartesian_derivatives_both_maps` | exit 1; test helper accessed a nonexistent `bundle.physical` field. | `cartesian-attempt1.log` |
| 11:30:22 | `pytest -q tests/integration/test_cap_collections.py -k parent_cartesian` | exit 0; 1 passed, 2 deselected. | `cartesian-attempt2.log` |
| 11:32:39, 11:32:51, 11:33:05, 11:33:11 | `pytest -q tests/integration/test_cap_collections.py -k two_cap` | Four exploratory exits 1 (3 passed, 1 failed; 3 deselected each). Assertions initially assumed a different internal-bond ledger disposition and duplicate-ID diagnostic order; production ledger behavior was inspected and the controls corrected. | `collection-controls-attempt1.log` through `collection-controls-attempt4.log` |
| 11:33:19 | same command | exit 0; 4 passed, 3 deselected. | `collection-controls-attempt5.log` |
| 11:36:00, 11:36:15 | inline fixed-coordinate MACE probe output | First probe stopped after successful two-cap construction on a tuple-indexing mistake. Second probe completed both-cap parent/environment finite differences; its numeric output is retained and its reproducible script is `mace-two-cap-crosscheck.py`. The exact pytest node also passed in the final-check table. | `mace-two-cap-attempt1.log`, `mace-two-cap-attempt2.log` |
| 11:37:07 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_bounded_restart_through_common_runner_in_fresh_process` | exit 1; geometry admission correctly rejected the fixture’s original second-ligand clearance (`0.490204039 nm < 0.65 nm`). The workflow-only test snapshot now translates the complete second ligand by 1 nm, preserving its internal geometry. | `common-restart-attempt1.log` |
| 11:37:26 | same command | exit 1; adapter `_topology` appended an interleaved atom to an earlier noncontiguous residue. | `common-restart-attempt2.log` |
| 11:38:13 | same command | exit 1; duplicate `Hcap` PDB atom names caused the reader to drop a cap particle. Adapter topology now gives each cap its own numbered residue. | `common-restart-attempt3.log` |
| 11:38:36 | same command | exit 1; test assertion assumed a flat serialized JSON shape instead of the typed `data` envelope. | `common-restart-attempt4.log` |
| 11:38:55 | same command | exit 0; 1 passed. | `common-restart-attempt5.log` |
| 11:44:26 | `pytest -q tests/integration/test_cap_collections.py::test_two_cap_ledger_and_nonidentity_particle_mapping` | exit 1; newly strict metadata validation changed which malformed invariant failed first; the test now updates declared edges so its duplicate-parent control isolates that invariant. | `collection-controls-attempt6.log` |
| 11:46:22 | `pytest -q tests/integration/test_link_geometry.py tests/workflow/test_worker_handover.py` | exit 1; 27 passed, 1 failed. The alias-ID control had a stale distance/ownership manifest; it now updates those rows so the alias rejection is isolated. | `single-cap-compat-attempt2.log` |

The untouched coordination edit in `Worker_Log/Before_HPC/progress.md` is parent-owned and excluded from staging.
