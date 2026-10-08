# FKBP12 fragment benchmark

The initial set is BUT, PRP and **neutral** DAP from the pinned
[AToM FKBP example](https://github.com/Gallicchio-Lab/AToM-OpenMM/tree/9e26c5a3811038be1c98e3be6af4c78cd0dd57a7/examples/ABFE/fkbp).
FKBP12 is a small, well characterized protein, and these fragments have known
bound poses. The reference study is
[Pan, Xu, Palpant and Shaw (2017)](https://doi.org/10.1021/acs.jctc.7b00172).
That paper provides MD/FEP context; it is not presented here as an ATM validation.
The AToM example is the direct evidence that this target is supported upstream.

| ID | Ligand | Complete atoms, including H | Computational state |
|---|---|---:|---|
| `but` | 4-hydroxybutan-2-one | 14 | Neutral singlet |
| `prp` | 1-hydroxypropan-2-one | 11 | Neutral singlet |
| `dap` | 4-(diethylamino)butan-2-one | 27 | Neutral singlet |

DAP and the upstream protonated DAPP are distinct states. DAPP is excluded;
sulfur-containing fragments are also excluded by the admitted H/C/N/O model
domain. No experimental affinities have been guessed or copied without checking
their conditions. The benchmark manifest records this explicitly.
The receptor and SDF files are unchanged upstream bytes, with SHA-256 identities
and the upstream licence retained in [benchmark.json](benchmark.json).

## Physical setup and minimal AToM changes

The installed AToM distribution is `8.5.0b0`, upstream tag `v8.5.0`, commit
`9e26c5a3811038be1c98e3be6af4c78cd0dd57a7`.
The adapter verifies the installed preparation/production source bytes.
It calls `make_system`, `abfe_structprep` and `abfe_production`; it does not
copy or replace the upstream scheduler or replica exchange.

Upstream parameterization uses Amber14, TIP3P, 0.15 M salt and OpenFF 2.3.0
(the FKBP example's own ligand force field). The shared builder supplies the
mechanical ML/MM Hamiltonian and MM interaction ledger. Compare three modes:

| Mode | ML membership |
|---|---|
| `mm` | MM baseline, with the same AToM protocol settings |
| `ligand` | Complete neutral ligand |
| `cavity` | Complete ligand plus Phe36, Ile56 and Phe99 side chains |

Cavity membership is fixed: CB–CA cuts, neutral singlet fragments and 0.109 nm
hydrogen caps. Protein cap parents move during dynamics and remain undisplaced
by ligand transfer. The whole ligand translates by `[0, 0, 4]` nm; an initial
periodic clearance check covers the full protein and caps. This check is not a
trajectory guarantee or a free-energy correction.

The narrow adaptations are: export the existing hybrid system; activate every
physical force during stock preparation; keep the declared 0.5 fs timestep and
all preparation loops at fixed volume; and route the complete physical force group into stock ATM production
once. Atom indices, AToM options and unit conversions stay in the adapter.
The upstream FKBP tutorial uses a ghost/variable-displacement RBFE implementation
of ABFE. This workflow uses AToM's existing single-ligand **fixed-displacement
ABFE** APIs to stay within the program's admitted transfer profile.

The fixed orthorhombic cell, disabled analytical dispersion correction,
1 Da hydrogen masses and 0.5 fs timestep are explicit choices for the
current ML/MM profile. Shared builder constraint rules apply inside the ML region.
There are no positional protein restraints. The flat-bottom ligand centroid
restraint uses three receptor CA atoms, the initial offset and upstream constants.
Production uses the upstream 22-state schedule in [atom.json](atom.json).
The default one-hour / ten-sample settings are a pilot, not a convergence claim.

## Commands

Run from a source checkout with the locked CPU environment activated:

```bash
python scripts/run_benchmark.py plan --output runs/fkbp
python scripts/run_benchmark.py setup --mode cavity --output runs/fkbp
python scripts/run_benchmark.py prepare --mode cavity --output runs/fkbp
python scripts/run_benchmark.py run --mode cavity --output runs/fkbp --nodefile /absolute/path/nodes.local
```

The default selects all three ligands sequentially; `--ligand but` selects one.
Use separate output roots for `mm`, `ligand` and `cavity` comparisons. Setup writes
the original MM input, partition/physical/transfer records, system XML, PDB,
initial geometry check and saved AToM options. Source/input/file identities are
checked before subsequent stages. `--smoke` belongs to **setup** and records two
steps per preparation loop and one production step/sample for plumbing checks;
minimization still uses AToM's ordinary convergence criterion.

For longer production, copy this benchmark directory, edit `atom.json` before
setup, and refresh that file's SHA-256 entry in the copied `benchmark.json`.
Then pass `--manifest /path/to/copy/benchmark.json`. Keep the timestep, ensemble,
force routing and chemistry unchanged unless deliberately qualifying a new
profile. Never edit saved job inputs or receipts to resume with different physics.

A preparation-attempt marker is flushed before upstream execution; even abrupt
process death prevents a retry from overwriting partial outputs. A failed
computational stage retains its outputs and a failure receipt when the process
can write one. Use a
fresh output root for a new attempt. Missing prerequisites do not poison a job.
Production cannot be silently relaunched over an existing attempt. AToM's native
restart and checkpoint files remain available, but restart admission through
this launcher is not yet qualified. Generated jobs are not relocation portable:
set up in the final shared run location and keep the source snapshot unchanged.

## Cluster allocation

The current MACE callback is CPU only. The launcher admits CPU/Reference workers;
CUDA/HIP, cluster parity and cluster restart trials remain pending. Install under
a writable shared prefix using `ATOM_MLMM_SETUP_ROOT`, as described in the
[environment guide](../../environment/cloud-cpu/README.md).

Run preparation and production within your site's allocation. Supply an AToM
nodefile with six comma-separated fields:
`hostname,platform:device,threads,platform,username,scratch`.
For one local CPU worker inside an existing Slurm allocation:

```bash
mkdir -p "$TMPDIR"
printf 'localhost,0:0,%s,CPU,,%s\n' "$SLURM_CPUS_PER_TASK" "$TMPDIR" > nodes.local
python scripts/run_benchmark.py run --ligand but --mode cavity \
  --output /absolute/shared/run/root --nodefile "$PWD/nodes.local"
```

Choose memory, walltime, account and partition from the actual cluster; no job is
submitted by the launcher. Use unique slots for multiple workers and account for
each worker's model memory and threads. Keep outputs on a filesystem that supports
locking and atomic rename. Follow the [HPC guide](../../environment/hpc/run-guide.md)
for measured environment/storage/checkpoint qualification.

Binding estimates still require equilibration/mixing/convergence checks, both
alchemical legs, midpoint consistency and the declared restraint/standard-state
corrections. Preparation or a successful scheduler return does not establish a
binding free energy. The existing G07 chemistry/boundary holds remain in
[STATUS](../../docs/project-0/STATUS.md).
