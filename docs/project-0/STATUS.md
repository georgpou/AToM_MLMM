# Current status

## FKBP benchmark and repository cleanup — completed 2026-10-08

Current work is on `hpc-atom-benchmark`, a child of `before_HPC` at
`590cb5258696042b29856df37f6053ba820d2f56`. The selected target is FKBP12 with
BUT, PRP and explicitly neutral DAP from the pinned AToM v8.5.0 example.
The [benchmark guide](../../benchmarks/fkbp/README.md) is the current usage entry.

The launcher separates planning, system setup, preparation and production.
Parameterization, preparation and the production scheduler use installed AToM
APIs. The existing physical builder supplies capped mechanical ML/MM; preparation
activates all physical forces and remains NVT. Production transfers the complete
ligand and nests the physical force group once. CPU/Reference are admitted;
CUDA/HIP are pending.

The stable-source CPU regression suite passed **713 tests / 57 deselected**;
the focused workflow/native force/PDB/nodefile checks passed **26 tests** and
two real-model adapter/boundary checks passed. The locked two-environment CPU
installer checks passed. All three molecular cavity setups were verified.
BUT preparation and short production completed for both MM and capped ML/MM,
with finite samples, exact fixed cells and spawned AToM CPU workers. The capped
run scheduled 22 replicas and sampled 11 within its one-minute smoke limit;
this is workflow evidence only. Independent review closed both findings and
verified the timestep repair. Exact commands and evidence are in the
[task record](../../Worker_Log/Before_HPC/AToM_Benchmark_v1_worker.md).
No new scientific gate or milestone acceptance is claimed.

The cleanup retires **7,965 tracked historical files / 216,057,640 bytes** from
the checkout. Required acceptance evidence, neutral references, charged QM
receipts/budget, environment locks/replay inputs and model assets are preserved.
Retained historical evidence was checked byte for byte against the predecessor.
The [history guide](../../Worker_Log/README.md) explains recovery; Git history
is unchanged. Active Colab notebooks were already absent. Closed notebook-era
run evidence and copied source/environment/run trees were retired.

## Scientific and hardware holds

The [support matrix](support-matrix.json) and
[requirement matrix](before-hpc-requirement-matrix.json) retain their exact prior
acceptance/evidence scope. The shared CPU engine has bounded prior numerical and
runtime acceptance; this workflow does not establish protein accuracy.

G07 boundary sensitivity and the **29 missing quantum references** (19 full-parent,
10 alternate-cap) remain open. The charged QM ledger remains
**2325.6446500519996 / 86400 seconds**, leaving **84074.355349948 seconds**;
no QM calculations or budget changes were made. The 46 accepted G05 neutral
reference records remain unchanged. The C3 unmatched-physical-state closure,
protein chemistry, molecular thermodynamic corrections/convergence, release
licensing, GPU qualification and cluster/storage/restart parity remain held.
`binding_result=not_evaluated`.

## Prior checkpoints

The detailed before-HPC publication and engine development record remains at the
[exact predecessor STATUS](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/docs/project-0/STATUS.md).
The [engine handoff](handoffs/CLOUD-ENGINE-CONTINUATION.md) and
[G07 reference handoff](handoffs/G07-reference-remaining-v2.md) retain the scientific
continuation context. The accepted audit bytes used by the support matrix remain
local. No old documentation audit needs to be recovered as an onboarding task.
