# G10 bounded multistate runtime amendment

**Design status:** proposed; ready for independent audit. This document does not
authorize implementation or accept G10/M05. **Scope:** a serial Reference/CPU
NVT controller for three to eight explicit schedule states, built by composing
the accepted actual-worker pair adapter.

[G10](../gates/G10-restart-and-replica-exchange.md) | [S05](S05-protocol-and-thermodynamic-contracts.md) | [S07](S07-artifacts-and-qualification.md) | [M05 exchange definition](m05-dense-exchange-amendment.md)

## Decision and alternatives

Use a deterministic ordered sweep of explicit state-index pairs and invoke
`atm_mlmm.adapters.atom.attempt_pair_exchange` once for each pair. This retains
the pinned AToM implementation as the only Hamiltonian-evaluation/Metropolis
path. A new N-way decision routine would duplicate physics and probability code;
independent concurrent pair jobs would race over state ownership and make a
whole scheduling boundary difficult to recover atomically. The serial sweep has
bounded CPU throughput and gives one reproducible transaction boundary.

The existing `run_exchange` / `resume_exchange` signatures and pair-mode format
remain available for newly prepared, source-matched runs. Add separately named
multistate APIs and a separate journal mode. A pair run presented to a
multistate resume, or a multistate run presented to a pair resume, is rejected
before worker loading. No in-place conversion of frozen source bundles is
provided.

## Admission and public API

Add the following API in `src/atm_mlmm/exchange.py`:

```python
run_multistate_exchange(
    prepared_run: Path, output: Path, *, state_ids: Sequence[str],
    state_pairs: Sequence[tuple[int, int]], boundaries: int,
    steps_per_boundary: int, seed: int, trusted: bool = False,
    stop_after_boundaries: int | None = None,
)
resume_multistate_exchange(
    directory: Path, *, trusted: bool = False,
    stop_after_boundaries: int | None = None, recover_pending: bool = False,
)
read_multistate_boundaries(
    directory: Path, *, allow_pending: bool = False,
)
```

`state_ids` is an ordered sequence of three to eight distinct, nonempty IDs
present in the sealed worker schedule. `state_pairs` is a nonempty ordered
sequence of `(i, j)` integer indices into that sequence. Each pair has distinct
in-range indices; unordered edges occur once per sweep; their graph is
connected and covers every declared index. This makes the declared sweep
deterministic, bounded by 28 attempts, and able to reach every declared state.
The exact ordered state IDs and pairs are frozen in metadata and hashed with the
run. There is no randomized pair selection or automatic state discovery.

Admit only identical sealed physical, alchemical, runtime, model, force-field,
map, schedule, constraint, box, and software identities for all contexts, at a
single temperature of exactly 300 K. Use Reference double precision, CPU model
execution, NVT, the existing pinned runtime and existing lock files. Create one
actual `WorkerRun` context per stable walker, loaded from the same prepared
worker handover. The hard technical bound is at most eight live contexts; this
is a CPU memory/control bound, not a throughput or qualification claim. Pilot
runs use three contexts. Do not relax complete-ligand or either-map geometry
guards to admit a schedule.

The distinct metadata value is
`mode="persistent-multistate-exchange-v1"`. Pair mode retains
`mode="persistent-pair-exchange-v1"` and is never accepted as multistate input.
The multistate reader likewise rejects pair metadata. Validate argument types,
limits, schedule membership, connected pair coverage, temperature, and sealed
identities before starting an attempt.

`read_multistate_boundaries` is an inert journal reader: it validates and
returns the complete committed boundary prefix without trusted worker loading.
`stop_after_boundaries` limits newly added boundaries, and
`recover_pending=True` is the sole opt-in to archive and replay an incomplete
boundary. The existing pair functions keep their current signatures and
semantics for new source-matched bundles.

## Assignment and sweep semantics

Workers and walkers have fixed, distinct IDs for the run. Coordinates,
velocities, integrator state, and walker ID stay with their worker; only the
thermodynamic state label changes. Store the full `walker_to_state` permutation
as schedule indices in stable walker order at the initial boundary, every
attempt before and after, and every committed boundary. Check that it is a
bijection of `0..N-1`; store or derive its inverse `state_to_walker` and verify
that it agrees. Never infer assignment from a directory name.

For each boundary, integrate every worker exactly once, sequentially, for
`steps_per_boundary` steps under its current state. Capture and durably stage
that worker's unique boundary sample, portable State, and checkpoint before
integrating the next worker. Once all workers are staged, hold every coordinate
fixed while running the full ordered pair sweep. There is no integration between
pair attempts. At each pair `(i, j)`, resolve the current workers from the
current permutation immediately before the call, then pass those two actual
workers, their boundary snapshots, state IDs `(state_ids[i], state_ids[j])`,
and their stable walker IDs to `attempt_pair_exchange`. If accepted, exchange
those workers' two state labels in the full permutation; if rejected, leave the
permutation unchanged. Resolve the next pair again after that decision.

The sample row's `state_id` means the assignment at boundary sample capture,
before any sweep decision. It is immutable for that sample. Each attempt row
separately records the full `walker_to_state_before` and
`walker_to_state_after`, selected state IDs, selected worker/walker IDs, and
the adapter report. The committed boundary separately records its start and
final permutations. This preserves predecision sample meaning when later pair
attempts change the assignment.

For three states, begin with walker assignments `[0, 1, 2]` and sweep pairs
`[(0, 1), (1, 2)]`. If `(0, 1)` accepts, the permutation becomes `[1, 0, 2]`.
Immediately before `(1, 2)`, state 1 now belongs to walker 0 and state 2 to
walker 2, so those are the workers passed to the adapter. If that attempt also
accepts, the final assignments are `[2, 0, 1]`. The second attempt must not use
the stale original state-to-walker mapping.

## Energies and scientific limits

For every attempted pair, the existing adapter freshly evaluates the complete
2-by-2 matrix `v_i(x), v_i(y), v_j(x), v_j(y)` on the actual contexts after
setting the requested state parameters. Every value includes all outside
energy terms. The adapter returns refreshed energies after applying the state
decision. Store all four raw-energy records, all four dimensionless reduced
energies, the exponent, decision, and refreshed records for that exact pair.
Never reuse the prior attempt's matrix, a cached reported potential, or a
sample's `system_total_energy_kJ_mol` as an attempted-pair matrix. Parameter
refresh and context evaluation remain inside `attempt_pair_exchange`; the
scheduler contains no copy of its Hamiltonian or Metropolis calculation.
The current admitted fixture's nonzero static-anchor outside term is
state-independent. This amendment introduces no state-dependent outside
Hamiltonian or restraint; the complete context totals still include every
outside term supported by the sealed worker.

At the admitted temperature,

```text
beta = 1 / (0.00831446261815324 * 300)  mol/kJ
delta = v_i(y) + v_j(x) - v_i(x) - v_j(y)
P(accept) = 1                         if delta <= 0
             exp(-delta)              if delta > 0
```

Independent tests compute the four energies from actual contexts and an
independent nonlinear analytic/outside-term oracle, calculate `delta` and the
threshold independently, then force adapter draws below and above that
threshold to check accept and reject paths. These tests verify the pinned
adapter call; production code still delegates the decision to that adapter.
Check that state parameters and fresh reports match after both accepted and
rejected attempts.

Each predecision sample has one unique ID per `(run, boundary, walker)` and
stores its sample-time state ID, sequence, step/time, positions, velocities,
box, complete schedule parameters, all named raw energies, and full real forces
on all atoms (including MM and cap parents). Save the existing raw
`EvaluationRecords` shape for schedule reconstruction; do not alter energy
names, units, force ownership, caps, maps, or Hamiltonian terms. Attempt matrices
and final assignments remain separate records. The records are correlated
exchange observations for exact raw reconstruction only. This deterministic
composition of valid pair kernels preserves the product target distribution;
it does not establish detailed balance for the whole ordered sweep, mixing,
convergence, exchanging-walker uncertainty, an affinity estimate, or molecular
accuracy.

## Boundary transaction and recovery

Use an exclusive, nonblocking local controller lock. The initial sealed
boundary contains all worker portable States/checkpoints, the identity
permutation, run/state/pair identities, and complete Python and NumPy legacy RNG
states. For each new boundary, create a unique pending directory before any
integration. Stage and fsync each successful worker sample and its portable
State/checkpoint before moving to the next worker. Before each pair call, stage
and fsync the attempt index, resolved walkers, and full before permutation.
The adapter callback writes and fsyncs that attempt's `evaluated`, `decision`,
and `refreshed` phase records. When it emits `decision`, write `decision.json`
with the adapter report plus the full before and computed after permutations;
fsync it before allowing parameter refresh to continue. Write `history.json`
with both permutations and the resolved walker/state mapping at the same point.
Persist `refreshed.json` after post-decision evaluation. Do not start the next
pair until all three phase files and full attempt history are durable. Preserve
all completed and partially attempted phases in the pending tree.

After the final pair, freshly evaluate every worker under its final assigned
state and save per-walker raw/total/parameter values in
`final-state-reports.json`. These are boundary checkpoint checks, not extra
exchange decisions. Then capture all workers' final portable States and
checkpoints, final full permutation, sample rows, attempt histories, and both
post-boundary host RNG streams. Hash-bind every file; fsync files and nested
directories; seal the complete boundary; and publish it by one same-filesystem
directory rename followed by parent-directory fsync. One committed boundary
therefore contains every worker state, every pair phase, the complete
permutation history, and both host RNG streams. `boundaries/000000`, etc. form
the authoritative committed prefix. `records.json`, `observations.json`, and
summary output are rebuildable from that prefix. Samples in a pending tree are
not inserted into those reports.

Use deterministic indexed paths so both successful and interrupted work is
inspectable: staged samples are
`pending/samples/worker-000.json`, `worker-000-state.xml`, and `worker-000.chk`
(with one zero-padded worker index per walker); final context states are
`workers/worker-000-state.xml` and `workers/worker-000.chk`. Zero-based pair
attempt `q` uses `attempts/<q:04d>/attempt.json`, `evaluated.json`,
`decision.json`, `refreshed.json`, and `history.json`. `attempt.json` is durable
before the adapter call and contains the resolved pair and full before
permutation. `decision.json` and `history.json` carry the full before and after
permutations; all present phase files are durable before the next attempt.
Missing later phase files identify where execution stopped without treating an
absent decision as rejection.

Any exception archives cached State/checkpoint and both transformed
coordinate-State records for every worker independently, without force or
energy reentry; the primary error remains primary and secondary archive errors
are retained. Default resume rejects any incomplete pending boundary without
modifying it. Explicit `recover_pending=True` first preserves the entire pending
tree, staged samples, all completed/attempted pair histories and phase files,
hashes, primary and secondary errors in a unique failure archive. It then
reinstantiates every context from the immediately preceding committed
checkpoints, restores the full committed permutation and both host RNG states,
and replays the entire boundary. Nothing from the incomplete boundary is
promoted or analyzed. Deterministic `(run, boundary, walker)` sample IDs are
recreated once in the committed run; failed attempts remain inspectable only in
the failure archive.

A rename is the commit point. If parent fsync or derived-report writing fails
after rename, the published boundary remains authoritative and resume verifies
its hashes before continuing. A partial integration failure after worker 0 has
advanced but while worker 1 fails must leave worker 0's already-staged sample,
State, and checkpoint, plus both workers' failure captures, in the pending
tree. Explicit rollback must then archive that evidence and reproduce the same
complete boundary from the previous checkpoint/RNG/permutation boundary.

## Admission before trusted loading and source identity

Read and hash-verify metadata, mode, declared limits, initial boundary, every
committed boundary, all attempt phases, every full permutation, sample IDs and
sequences, checkpoint/State artifacts, RNG documents, chain links, and the
absence or explicit presence of pending trees before any trusted worker or
executable System/model load. Before loading, also verify field shapes/types,
sample and phase identity, raw-to-total/unit consistency, and that each stored
reduced-energy entry equals its stored full total multiplied by the admitted
beta. These inert checks establish integrity and internal arithmetic
consistency, not physical freshness.

After trusted loading, restore every context from the latest committed
checkpoint under its recorded final state. Before any integration, evaluate the
restored coordinates in the actual context and compare each fresh raw energy,
full total, parameter set, and sample/checkpoint coordinate identity with that
boundary's `final_state_reports` and portable State. Reject stale but
internally consistent saved energies here. Compare the constructed bundle and
runtime identities with the inert manifest before continuing. State IDs and
pair selections are already validated against inert bundle records before
constructing contexts.

Source identity is the exact recursive inventory of Python source files under
`src/atm_mlmm` plus each SHA-256, not only the hashes of source filenames a
worker happened to list. Require exact set equality between that inventory and
the source paths in `worker/manifest.json`, then compare every digest with the
running checkout. This closes the missing-module case: an older bundle cannot
pass simply because every source path it lists still has the same bytes. New
pair and multistate attempts use newly prepared bundles with the full current
inventory. A frozen older bundle must be resumed only with its exact bundled
source/checkout; no migration or source substitution is allowed.

The journal mode is explicit and versioned. Pair/multistate mode confusion,
changed source inventory or hash, changed runtime profile, malformed
permutation, repeated/missing sample sequence, changed RNG data, incomplete
attempt phases, or hash-invalid checkpoints reject before trusted worker load.
An internally rehashed checkpoint with a stale final energy report rejects
after trusted restore through the fresh actual-context comparison and before
integration. The lock protects a local filesystem transaction; mounted durable
storage remains export-only unless separately qualified.

## Required focused controls and faults

Before any pilot, use analytic ABFE/RBFE controls with nonlinear ATM parameters
and the existing nonzero, state-independent outside anchor included in all four
context totals. Independently verify every four-entry matrix, full-force
sample, forced accept and forced reject. Do not add a state-dependent outside
term. Include the
overlapping `(0,1)` then `(1,2)` example to prove current-permutation resolution.

Inject failures at worker 1 integration after worker 0 has integrated and been
durably staged; every attempt's evaluation, decision, and refresh persistence
(including an attempt later in the sweep); final worker capture/checkpoint;
seal; rename before publication; parent fsync after rename; and derived report
rebuild. Assert that failures retain the primary and secondary errors, all
available worker archives, staged samples and attempted phases, that pre-rename
failures are not committed, and that post-rename failures keep the boundary
authoritative. Tamper the full permutation, sample ID/sequence, RNG state,
phase, or checkpoint and assert rejection before trusted loading. Also challenge
default no-mutation pending rejection, explicit whole-boundary replay, the
nonblocking concurrent lock, changed source inventory, and pair/multistate mode
confusion. Run existing persistent pair and pair decision regressions unchanged.

Then run serial three-worker pilots using the existing solvated ABFE and
unequal-ligand RBFE fixtures through the shared engine. Use no more than three
workers, four committed boundaries, two integration steps per boundary, and a
few prepared frames. Preserve fixture bytes and preparation settings' physical
identity. These pilots test execution and journal integrity only; they do not
qualify dense solvent, equilibrium, GPU, G10/M05 as a whole, molecular accuracy,
or binding uncertainty.

## Protected scope

Preserve identical physical/alchemical/runtime identities, complete ligands,
fixed ML membership, both-map guards, complete real-atom forces counted once,
MM atoms and cap parents, the existing Hamiltonian/caps/units/tolerances/locks,
model bytes, and accepted references. Leave the 46 accepted G05 records,
`QM ledger charged 2325.6446500519996 / 86400 s`, failed resource screen,
seven G07 sensitivity exceedances, pilot force failures, and 29 missing
references untouched. Run no QM, production, GPU, HPC, or cluster tooling.

This amendment changes runtime scheduling and transaction records only. The
independent Sol audit must review this design before implementation begins.
