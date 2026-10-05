# G10 persistent exchange and solvated restart — v2 worker

**Scope:** G10 and combined G09/G10 bounded CPU technical increment; Reference
double / approved MACE CPU float64; earlier accepted scopes carried forward only
where unchanged.\
**Outcome:** accepted_for_scope by the independent combined audit; wider scopes remain open.\
**Finished:** 2026-10-05T14:56:55.234424+00:00.\
**Snapshot:** `m05-colab-workflows`, base `fab6388b041acc4362f30b5ff7d3789a33fc536f`,
frozen scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.

## Changes

Persistent scheduling wraps the existing actual pair adapter; it supplies no
alternate Hamiltonian or Metropolis implementation. Two stable walkers retain
coordinates/velocities while states exchange. Each complete round hash-binds
predecision raw/full-force samples, fresh four-entry energies, evaluated/decision/
refreshed phases, state histories, post-refresh States/checkpoints and both Python
and NumPy host RNG streams. A local nonblocking lock prevents concurrent control.

Unique pending rounds are preserved after errors. Default resume rejects them;
explicit rollback archives every file and restores both workers/RNGs from the
last complete boundary before replay. One rename commits the round; published
rounds remain authoritative after later reporting/fsync errors. Cached original
and both mapped failures are attempted independently without evaluation reentry.
Fresh saved-boundary energy and map-guard checks reject stale/mismatched records.
Correlated records reconstruct the complete schedule; exchanging-walker
statistical estimation remains unqualified.

The [definition](../../docs/project-0/specs/m05-dense-exchange-amendment.md)
is independently accepted for this scope. The separate TPU notebook/profile probes the identical real
checkpoint, actual hardware/arithmetic, energy/coordinate gradients, cap-parent
projection, graph changes, FD sweeps and synchronized component costs. Timing
qualification requires numeric/precision/fallback checks. CPU locks/production
device guards remain unchanged; OpenMM/PME/integration stay CPU.

## Verification

All commands use the unchanged locked CPU environment and two threads. Scientific
jobs were serial, with15-minute pilot bounds and complete-round persistence.

| Check | Command | Observed result |
|---|---|---|
| Persistent actual analytic-worker exchange and notebook CLI | `python -m pytest tests/workflow/test_persistent_exchange.py tests/environment/test_m05_notebooks.py -q` | 15 passed12.74s: deterministic prefix replay/RNG, unique histories, accepted/rejected decisions, phase/journal/refresh failures, lock/tamper/stale-energy/map faults |
| Solvated offline/relocated reconstruction and restart | `python -m pytest tests/workflow/test_solvated_process_restart.py -q` | 4 passed47.99s; actual ABFE/RBFE sparse solvated MACE workers; original checkout/run/caches/network denied, actual CPU-float64 model tensors and Reference context checked |
| Actual dense two-worker exchange | `python -m atm_mlmm exchange /workspace/m05-evidence/dense-{abfe,rbfe} --output /workspace/m05-evidence/dense-{abfe,rbfe}-exchange --rounds 4 --steps-per-round 2 --seed 711 --trusted` (serial) | Both exit0; eight unique samples/four complete rounds each; 23.16/29.38s, peak RSS0.76/0.78GiB |
| TPU orchestration/admission/failure diagnostics | Focused `tests/environment/test_tpu_experiment.py` and notebook tests | Ten lightweight checks passed; FD-label and graph-shape tests exposed issues retained and repaired; final actual-reference GREEN is covered by the final suite |

Same prepared checkpoint continuation agrees exactly after two steps on this
profile. Portable State agreement covers fixed coordinates, energy/full forces,
parameters, box, masses and constraints separately; it promises no RNG/trajectory
identity. Initial immutable dense bundles predate the TPU-only addition; RBFE
exchange runs its exact bundled source, and physical/controller hashes match the
frozen source. Full archives and journals are in
[evidence/M05_v1](evidence/M05_v1/README.md).

## Combined scope and handoff

This submission combines the new G09 local-water numerical/coupling/preparation/
export scope and G10 solvated offline/restart plus transactional pair scheduling.
It does not close full M05 or M03 physical requirements. Checkpoint guarantees
require identical source/software/hardware; portable States differ.

Actual Colab CPU, TPU/CUDA/multigpu execution and benchmarks remain **not_run**.
The actual-MACE CPU reference is delivered; no import, selected runtime or
requested dtype qualifies TPU. Preserve unsupported operators/precision as
negative evidence. No liquid-density/equilibrium, molecular accuracy, affinity,
protein, pressure/virial or production claim; no new QM/HPC/GCP work. The final full CPU suite passed **543 tests in606.45s**, no skips, exit0, on the
frozen source (`python -m pytest -q --basetemp=/workspace/m05-evidence/full-suite-final
--junitxml=/workspace/m05-evidence/full-suite-final.xml`). Its actual-MACE reference
check passes all108 configurations, FD derivatives and changed graph shapes;
reference SHA `8a625d5bdcbac5cc1ddeb244ff12d095b14f811a287ca18732f86c943dba8d73`.
Full raw reference plus startup/steady CPU timings is sealed.
The independent combined technical review accepted this frozen scope.

Independent review accepted this scope with no required repairs: [audit](Gate_10_v2_audit.md).
The single reviewer passed52 fresh checks, with0skips, and independent raw-data
probes. See [review evidence](evidence/M05_v1_review/README.md). Scientific source
and submitted evidence remain unchanged; these acceptance lines are reporting only.
