# Cosmos repository-local environment

From the repository root, activate the installed CPU environment with:

```bash
source environment/hpc/cosmos/activate.sh
```

For Amber's separate NumPy 1.26 Python, use `source environment/hpc/cosmos/activate-amber.sh`.
Return to main with `source environment/hpc/cosmos/activate.sh`. Main Python uses NumPy 2;
Amber executables remain available without switching main Python.

Installation prefixes, caches and logs live under `.runtime/cosmos-cpu/`.
Temporary files use the short repository-local `.tmp/` path to fit Unix socket
limits. Both directories are ignored by Git. No shell startup files are edited. Conda's
global environment registry is disabled, so activate by these scripts rather than
expecting a short name in `conda env list`. Do not move installed Conda prefixes.

The Cosmos wrapper uses system Conda only to bootstrap a local Conda 26.7.2 client;
its exact client package inventory is saved in `logs/bootstrap-conda-explicit.lock`.
The scientific environments use the unchanged SHA-256 URL and wheel locks in
[the CPU bundle](../../cloud-cpu/README.md). `ATOM_MLMM_CA_BUNDLE` selects the RHEL
system trust store. TLS and artifact verification remain enabled. The unexecuted
Miniforge download was inspected because its default bootstrap forces global
registration; the Cosmos wrapper avoids that bootstrap.

## Slurm

The account `LU2025-2-123` and GPU partition `gpua100i` come from your original
[sample scripts](../../../Slurm_example/), which are preserved unchanged. The
CPU default `lu48` was confirmed with `sinfo` and the account checked using
`sbatch --test-only`. Check that your allocation remains active before reuse.

Submit from the repository root. Create the local log directory first:

```bash
mkdir -p .runtime/cosmos-cpu/logs
sbatch environment/hpc/cosmos/install.sbatch
# Later, to validate an existing install:
sbatch environment/hpc/cosmos/validate.sbatch
```

These scripts request one task and two CPU cores, matching threaded Python work.
The install limit is one hour; validation is thirty minutes, each with 12 GB RAM.
They retain output and actual validation statuses locally. The installation also
runs the available CPU suite, excluding the declared GPU/model-asset/slow profiles.
While waiting, use timed waits and occasional `squeue -j JOBID`/`sacct -j JOBID`
checks; no high-frequency polling is needed.

[GPU diagnostic template](gpu-diagnostic.sbatch) is provided but was not submitted.
It requests one GPU for five minutes and prints device/plugin information only.
The pinned PyTorch build and current MACE callback are CPU-only. It is not a GPU
production script or a qualification result. No Python-version-specific plugin
path is forced; OpenMM reports plugin load failures explicitly.

The cleaner pattern is one task with explicit CPUs per task, activation through a
shared wrapper, and small Python entry points rather than editing Python scripts
with sed for each ligand. Actual benchmark work should use the repository's
[benchmark CLI](../../../benchmarks/fkbp/README.md) in its admitted CPU profile.

## Current regression limitation

All nine environment checks pass on Cosmos. The full CPU suite currently reports
654 passed, 50 failed, 12 errors and 57 deselected. Quantum recovery tests assume
the old `/workspace` layout, and the offline relocation test blocks its own
repository-local relocated output. These are recorded portability failures;
installation/validation jobs that include the full suite consequently return
nonzero despite a usable environment. See the
[worker record](../../../Worker_Log/Documentation/Cosmos_Environment_v1_worker.md).
GPU/model/physical acceptance remains separate.
