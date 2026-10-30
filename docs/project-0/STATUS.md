# Current status

## Cosmos continuation handoff — 2026-10-30

The user designated `COSMOS` as the Cosmos integration branch: all future task
branches descend from it, with PRs and merges targeting `COSMOS`. The
[active handoff](handoffs/COSMOS-HANDOFF.md) records activation, exact current
passes/failures, the first bounded portability repair and subsequent gate and
milestone reproduction order. This assignment publishes the preserved setup and
handoff on that branch; publication adds no scientific or cluster acceptance.
See the [handoff worker](../../Worker_Log/Documentation/Cosmos_Handoff_v1_worker.md)
for verification and publication evidence. The installation and red full-suite
results below remain unchanged; no numerical tests were repeated for this doc task.

## Cosmos portability audit repairs — 2026-10-30

The user authorized root to repair F01/F02 directly. Neutral resource thresholds
are restored to their original policy, and G07 correction admission preserves
the exact approved historical validator identity while rejecting unknown ones.
No historical receipt, reference, canonical path or budget was rewritten.
Six new regression cases reproduced 3 intended failures/3 passes before repair
(Slurm 4067784). Job 4067914 passed **13 targeted/tamper tests**, followed by **733 CPU tests
passed / 57 deselected** on cn131 (8 CPUs, 12 GiB, Slurm `0:0`, 13:12).
All eight tested source hashes verify and 1,160 protected base files are unchanged. See the
[v2 worker](../../Worker_Log/Documentation/Cosmos_Portability_v2_worker.md) and
[fresh-auditor handoff](handoffs/COSMOS-PORTABILITY-AUDIT.md). Fresh user-selected review remains pending. This academic account cannot
connect to GitHub; the user delegated publication to another Codex account
using the prepared packet/prompt. No commit, push or PR was made here; no merge
or next gate is authorized.

## Cosmos portability prerequisite — 2026-10-30

The bounded recovery portability repair is implemented on
`cosmos/portability-repair`, based on `4d5b266d982e5e72596e475712eafbbe110e001f`.
The repair measures free space on the actual attempt/output filesystem, maps
cgroup-v2 resources from the worker leaf through the Slurm job boundary, and
allows the relocated worker to read only its exact sealed bundle and the
resolved installed interpreter prefix. Original checkout, old-run and cache
denials remain in force. Frozen scientific definitions, authorization, ledger
and two-thread execution caps are unchanged; resource-policy preservation is
qualified by the audit findings below.

The four-file focused COSMOS batch passed **88 tests** (Slurm job 4066756).
The one full available CPU suite passed **727 tests; 57 were deselected** (job
4066801, 8 CPUs, 12 GiB, one task, 11:58 scheduler elapsed). This is software
regression evidence on the CPU profile only; actual QM admission, scientific
gate acceptance and GPU qualification remain open. No commit was made because
the checkout has no local Git author identity; root will review and publish.
See the [portability worker log](../../Worker_Log/Documentation/Cosmos_Portability_v1_worker.md),
[task report](../../.runtime/cosmos-cpu/portability-repair/task-1-report.md)
and final file manifest in that report.

The user's requested [root audit](../../Worker_Log/Documentation/Cosmos_Portability_v1_audit.md)
requires changes: F01 identifies an unintended neutral resource-threshold change;
F02 independently reproduces rejection of the unchanged accepted G07 correction
when operational script edits change the pinned validator hash. Root verified
1,160 protected scientific/specification/reference/environment files unchanged.
The later user-authorized v2 repair is recorded above; the original audit is
preserved and no gate acceptance is claimed. The 727/57 result above remains evidence for the tested snapshot.

## Cosmos environment setup — 2026-10-30

The exact CPU ML/MM and separate AmberTools environments are installed locally
under `.runtime/cosmos-cpu`; activate via
`source environment/hpc/cosmos/activate.sh`. All nine installation checks passed
on Slurm CPU node cn024. The initial full CPU regression baseline was red:
**654 passed, 50 failed, 12 errors, 57 deselected**. The portability prerequisite
above subsequently resolved the observed `/workspace` assumptions and relocation
guard failure; its final CPU-suite result is recorded above. See the
[worker record](../../Worker_Log/Documentation/Cosmos_Environment_v1_worker.md)
and [Cosmos usage guide](../../environment/hpc/cosmos/README.md).
This is installation evidence; cluster/workflow parity, GPU and scientific holds
remain unqualified. No scientific definition or frozen approval was changed.

## Local checkout refresh — 2026-10-30

The local non-Git folder was backed up and replaced with `hpc-atom-benchmark` at
`70ad284745617122627f217cd86d58237a2435ee`. File-copy/Git integrity checks,
documentation checks and six dependency-light identity/schema tests passed.
This administrative refresh adds no environment, model, hardware or scientific
qualification. See the [refresh record](../../Worker_Log/Documentation/Repository_Refresh_v2_worker.md)
for backup verification, cleanup and exact scope.

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
