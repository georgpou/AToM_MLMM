# Tiny cloud engine checks

One runner prepares and samples all three examples on the locked CPU environment:

| Configuration | Real atoms | Purpose |
|---|---:|---|
| [18-crown-6/methanol](../../fixtures/cloud_host_guest/v2/config.json) | 48 | Whole neutral host/guest, all ML, vacuum |
| [Capped-fragment ABFE](../../fixtures/cloud_fragment_controls/v1/abfe/config.json) | 32 | Real MM ledger, one protein C-C cap, one complete guest |
| [Capped-fragment RBFE](../../fixtures/cloud_fragment_controls/v1/rbfe/config.json) | 41 | Same engine with two unequal complete guests |

These short runs check engine plumbing. MACE coverage, equilibrium, standard
binding corrections and affinity accuracy are unqualified. The existing G07
physical-reference failures remain open. T4 lysozyme L99A is reserved for HPC.

From the repository root:

```bash
source /workspace/atom-mlmm-g08-r2/activate.sh
export OPENBLAS_NUM_THREADS=2
export PYTHONPATH="$PWD/src"
python -m atm_mlmm check fixtures/cloud_host_guest/v2/config.json
python -m atm_mlmm run fixtures/cloud_host_guest/v2/config.json --output /tmp/my-cloud-attempt --trusted
python -m atm_mlmm resume /tmp/my-cloud-attempt --trusted
```

Use your installed activation path and a new output directory for each attempt.
`--trusted` explicitly permits executable System/PythonForce/model loading; use
only artifacts you trust. `check` validates declarative records and settings.
`run` preserves input files before geometry admission and never overwrites an
attempt. A completed `resume` verifies existing output without duplicating it.

For a new admitted system, supply hashed `system-input.json`, `partition.json`
and `snapshot.json` records in an input manifest, then point the configuration
at that manifest and its SHA-256. Select `protocol_kind: abfe` or `rbfe`; mobile
groups are complete declared ligand molecules. Change temperatures, bounded
minimization/phase steps, seed, frame stride and counts in `settings`. The
qualified timestep is at most 0.0005 ps. An optional top-level `schedule` accepts
the complete typed ScheduleSpec used by the shared API. The default is three
explicit positive-direction states with Lambda1=Lambda2=0/0.5/1, Acore=0,
UOffset=W0=0, Umax=10000 and Ubcore=500 kJ/mol. The resolved configuration saves
every parameter. Unknown settings fail early with an actionable error.

The initial runner supports nonperiodic Reference double NVT and pinned MACE
CPU float64. Implicit solvent, solvated PME, CUDA and replica exchange remain
pending. Adding a solvent setting cannot silently introduce a new Hamiltonian.
All selected static hosts must be complete neutral singlets; protein fragments
retain the existing admitted C-C cut policy.

`summary.json` reports scope, counts, identities, timing and process peak RSS.
`preparation.json` records actual phase settings and observations. `records.json`
contains shared raw EvaluationRecords; `observations.json` includes every real
force, coordinates, velocities, state parameters and named energy terms. No
binding estimate is generated. `samples/000000/` and later immutable chunks bind
each observation to its State and checkpoint. `worker/` is a complete portable
source/model/environment/PDB/System/State bundle with manifest hashes.

To relocate an attempt, copy its complete directory, activate the identical
locked environment, set `PYTHONPATH` to `<copy>/worker/runtime/source`, then run
`python -m atm_mlmm resume <copy> --trusted`. Checkpoints require the identical
software/source/runtime profile; portable States restore observables without
promising identical RNG continuation. Resume supports a committed sample prefix.
Preparation interrupted before metadata creation must start a new attempt.
An incomplete `.pending-*` sample transaction blocks continuation and preserves
its files for inspection. Concurrent controllers and automatic hard-crash repair
are not supported by this first runner.

The rejected original host pose is retained at
[v1](../../fixtures/cloud_host_guest/v1/manifest.json). It fails the unchanged
distance guard before model startup. The admitted
[v2 geometry](../../fixtures/cloud_host_guest/v2/manifest.json) was selected by
whole-host distances rather than energy or affinity.
