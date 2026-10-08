# AToM FKBP benchmark and cleanup — v1 worker

**Scope:** User-requested protein/ligand selection, AToM workflow automation and
cluster-oriented repository cleanup; locked CPU profile.
**Outcome:** Benchmark workflow and cleanup complete; reviewed source passed CPU verification and actual MM/ML-MM short runs on 2026-10-08 UTC.
**Snapshot:** `hpc-atom-benchmark`, base
`590cb5258696042b29856df37f6053ba820d2f56` (`before_HPC`). Main/predecessor unchanged.
Implementation is inline; one fresh-context final reviewer. Model/effort values
are not exposed by this runtime.

The result source, launcher, tests and molecular inputs are identified by
[validated-files.json](evidence/atom-benchmark-v1/validated-files.json).
Every reviewed file matches the final snapshot; runtime source also matches
the sealed molecular setup. Large run outputs remain outside Git at
`/workspace/fkbp-final-validation` and `/workspace/fkbp-mm-validation`.

## Changes

- Curated FKBP12 BUT, PRP and neutral DAP from exact AToM v8.5.0 source bytes,
  with licence, chemistry, file hashes and literature provenance. The upstream
  FKBP example supports target selection; no published ATM accuracy is inferred
  from the Pan et al. MD/FEP study and no reference affinities are guessed.
- Added one stage launcher and dependency-light job orchestration. Setup,
  preparation and production are separate; saved source/input identities,
  exclusive job locks and failed-attempt retention prevent accidental mixing.
- Called installed AToM `make_system`, `abfe_structprep` and `abfe_production`.
  The physical builder/ledger remain unchanged. The narrow adapter activates all
  physical forces in preparation, fixes volume and the declared timestep, translates units/indices and
  exports all physical forces into stock ATM once. The single-ligand fixed map
  avoids the tutorial's ghost/variable-map extension outside current support.
- Cavity mode uses fixed Phe36/Ile56/Phe99 CB–CA side-chain cuts and existing
  caps; ligand-only and MM controls use the same protocol settings. Initial
  periodic bulk clearance is recorded. The 0.5 fs, fixed-cell profile is explicit.
- Retired 7,965 historical files / 216,057,640 bytes. Retained evidence was
  compared byte for byte to the predecessor, including accepted support-matrix
  receipts/audits, M00 reference lineage and G07 authorization/budget. Git history
  is unchanged. The active tree had no Colab notebooks; their generated historic
  evidence was retired. Environment replay archives/locks and approved assets
  remain required and were retained. New run outputs are ignored.
- Updated README, benchmark guide and live STATUS; retired document links point
  to the exact predecessor. Historical required Markdown bytes are unchanged.

## Verification

Environment installed at `/workspace/hpc-benchmark-cpu` using the repository's
exact CPU installer/locks. Activate its `activate.sh` in each scientific shell.
Its installation validation passed; main Python/NumPy 2 remains separate from
AmberTools/NumPy 1.26. No dependency lock or checkpoint bytes were changed.

| Check | Command from repository root | Actual outcome |
|---|---|---|
| Focused TDD | New workflow/partition/preparation tests before implementation | Intended missing implementation/force-mask failures reproduced |
| Native PDB regression | `python -m pytest tests/unit/test_protein_benchmark_input.py -q` | Blank insertion-code selection failed, then 4 passed after normalization |
| Admission regressions | Workflow path/symlink and corrected-nodefile tests | 3 intended failures, then passed |
| Worker allocation regressions | Unsupported/ambiguous nodefile tests | 5 intended failures, then passed |
| Focused final set | `python -m pytest tests/workflow/test_benchmark_atom_adapter.py tests/workflow/test_benchmark_workflow.py tests/unit/test_protein_benchmark_input.py -q` | 26 passed in 0.48 s |
| Stock ATM oracle | Included in focused set | Both-map polynomial energies and virtual-site parent forces agree; forces nested once, active integrator mask and NVT checked |
| Initial actual parameterization | `python scripts/run_benchmark.py setup --ligand but --mode cavity --smoke` in fresh external output roots | GAFF helper failed against locked modern generator; changed only configuration to upstream OpenFF 2.3.0. Next attempt exposed blank PDB insertion code; corrected with RED/GREEN regression. Both failed outputs retained externally |
| Actual FKBP set | `python scripts/run_benchmark.py setup --output /workspace/fkbp-final-validation --mode cavity --smoke` | All 3 setup receipts verified; complete ligand maps, 3 undisplaced caps each, initial clearances 1.8657–1.9391 nm (required 1.1 nm) |
| Stable-source CPU suite | `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | 713 passed, 57 deselected in 1089.61 s; exit 0 |
| Review repairs | Interruption, mass-weighted centroid and preserved 0.5 fs timestep regressions | RED reproduced; GREEN passed. Independent abrupt-exit test retained partial bytes and blocked retry; both upstream hooks restored |
| MM preparation and production | `python scripts/run_benchmark.py prepare --output /workspace/fkbp-mm-validation --ligand but --mode mm`; `python scripts/run_benchmark.py run --output /workspace/fkbp-mm-validation --ligand but --mode mm --nodefile /workspace/fkbp-cpu.nodes` | Both exit 0; exact fixed cell, 0.5 fs logs, finite energies, upstream spawned CPU worker/exchange and normal termination; no affinity |
| Capped ML/MM preparation and production | `python scripts/run_benchmark.py prepare --output /workspace/fkbp-final-validation --ligand but --mode cavity`; `python scripts/run_benchmark.py run --output /workspace/fkbp-final-validation --ligand but --mode cavity --nodefile /workspace/fkbp-cpu.nodes` | Both exit 0; ordinary minimization completed, six finite saved states with exact fixed cells, 0.5 fs; native PythonForce inside ATM, spawned CPU worker and replica exchange. 22 replicas scheduled; 11 finite one-step samples under the one-minute smoke limit. All 22 checkpoints finite with exact fixed cells; no affinity |
| Model compatibility | `python -m pytest tests/integration/test_joint_hybrid_atm.py -m model_assets -k "direct_native_and_atom_agree or mm_boundary_parent_force" -q` | 2 passed, 8 deselected in 9.47 s |
| Independent review | Fresh subagent initial review and focused repair review | 26 passed in 0.43 s; both findings closed and timestep preservation checked; no material remaining findings |
| Documentation | `python tools/check_docs.py --self-test` | Zero errors; eight self-checks passed |
| Staged whitespace | `git diff --cached --check` with exact upstream PDB/licence paths excluded | Pass for authored files; upstream fixed-column/CRLF bytes remain hash-verified and unchanged |
| Cleanup preservation | Exact SHA-256 comparison of retained historical files to base | All retained bytes unchanged; original model/environment/reference fixtures unchanged |

Two earlier CPU suites overlapped live source edits: 686 passed / one source-inventory
failure / 57 deselected; then 709 passed / one changed-source failure / 57 deselected. The worker validates the complete source tree;
the final suite therefore runs on stable source. This is not counted as a passing
suite. Raw failed attempts are retained in the external validation directories.

## Completion and next action

Independent review closed the interrupted-preparation overwrite and centroid-weight
findings and confirmed the timestep repair; see the matching
[audit record](AToM_Benchmark_v1_audit.md). The
[evidence index](evidence/atom-benchmark-v1/README.md) locates the final receipts
and compact validation output. CPU suite, all-ligand setup and both actual short
workflow checks are complete on the same source snapshot.
No cluster allocation was submitted, no long production/QM was launched, no
affinity was inferred, and no scientific tolerance/ledger/budget was relaxed.
The current model profile is CPU/Reference; GPU and actual cluster restart/storage
qualification remain pending. Default sample counts are a pilot, not equilibrium
or convergence evidence. Read the benchmark guide for final-location setup and
explicit worker allocation. Next, reproduce the locked environment and short
workflow within the actual cluster allocation before choosing pilot resources
and sampling lengths. Existing G07/C3/thermodynamic/physical holds remain.
