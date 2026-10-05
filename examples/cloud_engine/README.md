# Tiny cloud engine checks

One runner prepares and samples these examples on the locked CPU environment:

| Configuration | Real atoms | Purpose |
|---|---:|---|
| [18-crown-6/methanol](../../fixtures/cloud_host_guest/v2/config.json) | 48 | Whole neutral host/guest, all ML, vacuum |
| [Capped-fragment ABFE](../../fixtures/cloud_fragment_controls/v1/abfe/config.json) | 32 | Real MM ledger, one protein C-C cap, one complete guest |
| [Capped-fragment RBFE](../../fixtures/cloud_fragment_controls/v1/rbfe/config.json) | 41 | Same engine with two unequal complete guests |
| [Explicit-water ABFE control](../../fixtures/solvated_fragment/v1/abfe/config.json) | 56 | Same capped solute plus eight rigid classical TIP3P waters, orthorhombic PME |
| [Explicit-water RBFE control](../../fixtures/solvated_fragment/v1/rbfe/config.json) | 65 | Unequal complete guests with the same water/PME convention |

These short runs check engine plumbing. MACE coverage, equilibrium, standard
binding corrections and affinity accuracy are unqualified. The existing G07
physical-reference failures remain open. T4 lysozyme L99A is reserved for HPC.

From the repository root:

```bash
source /workspace/atom-mlmm-g09-v3/activate.sh
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

The runner supports Reference double NVT and pinned MACE CPU float64, with
nonperiodic inputs or the declared orthorhombic PME convention. The explicit-water
controls are deliberately sparse; liquid density and dense-solvent equilibration
remain unqualified. Their [scientific amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md)
defines rigid TIP3P, unchanged solute membership, constraints, PME, disabled
dispersion correction and minimum-image periodic anchoring. Implicit solvent,
CUDA and a production replica-exchange controller remain pending. A solvent
setting cannot silently introduce a new Hamiltonian.
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
promising identical RNG continuation. Continuation comparisons must start from
the same exact saved System/State and seed: independent ML minimizations can
differ at floating-point roundoff, including the chosen anchor center. Resume
supports a committed sample prefix.
Preparation interrupted before metadata creation must start a new attempt.
An incomplete `.pending-*` sample transaction blocks continuation and preserves
its files for inspection. Concurrent controllers and automatic hard-crash repair
are not supported by this first runner.

The rejected original host pose is retained at
[v1](../../fixtures/cloud_host_guest/v1/manifest.json). It fails the unchanged
distance guard before model startup. The admitted
[v2 geometry](../../fixtures/cloud_host_guest/v2/manifest.json) was selected by
whole-host distances rather than energy or affinity.

The explicit-water inputs contain the complete hashed MM System and topology,
including solvent constraints; the common runner preserves the actual box in
every sample and uses minimum-image distances for both-map geometry guards.
Failures preserve the original cached State/checkpoint plus `map0-state.xml`
and `map1-state.xml` coordinate copies. Mapped copies retain cached parameters
and velocities without reevaluating energies/forces, including nonfinite XML.
Each archive operation is attempted independently. Secondary archive failures
appear in `error.json` when writable and in notes on the original exception;
the CLI displays both. A failed artifact write cannot replace the simulation
error or insert a rejected sample.

For an actual-worker exchange probe, use
`atm_mlmm.adapters.atom.attempt_pair_exchange(workers, snapshots, state_ids, walker_ids)`
with two trusted loaded workers sharing the same complete bundle and runtime.
It evaluates all four full context potentials, delegates the swap decision to
the pinned AToM pairwise Metropolis routine, then refreshes the accepted state
energies. Its report separates fixed walker IDs from before/after state IDs,
stores raw energies and the reduced-energy matrix/exponent, and identifies the
Hamiltonian/runtime. AToM's host RNG supplies the random choice. This is a single
bounded decision, not a persistent exchange scheduler; production RNG/history
supervision and exchanging-walker correlation analysis require later coverage.

To reproduce the frozen water inputs at a new destination, run
`PYTHONPATH=src python tools/build_solvent_control.py /tmp/new-water-inputs`
after locked-environment activation. The tool preserves the solute particle and
exception parameters and never overwrites an existing destination.
