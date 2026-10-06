# G10 v5 RED — bounded sequential repair batch

**Prepared:** 2026-10-06 UTC. **Branch:** `g10-engine-next`.
The complete Sol 6.1/max [v5 audit](../../../Worker_Log/Milestone_05/Gate_10_v5_audit.md)
finished RED before this batch was defined. Its report-only commit is
`a90e192ec0d87524e8fbf77a18d62b4b81a37195`; reviewed source is unchanged from
`edd587679aaa110ea687cca29b9e3aee70b7b6f0` and worker submission `ecace38…`.
Root verified all 29 independent evidence/report/STATUS hashes at that audit
commit, the saved 47-pass independent pytest outcomes, and protected-tree
equality. No implementation acceptance is claimed.

## Dependency order and completed-task rule

Only root spawns. Each repair worker is exactly `gpt-6-luna` / `max` with a
fresh bounded assignment and exact starting HEAD. At most root plus one running
side agent. The auditor has completed; no repair runs alongside an auditor.

| Sequential task | Findings and boundaries | Planned worker record |
|---|---|---|
| A: inert declarations, refresh arithmetic and recursive seal | R1/R4/R7, including inert sample/report clock type/agreement as prerequisite to R2. Strict types/limits/seeds/RNG/inverses/sample identities; matrix-bound accepted/rejected refresh; exclude only root manifest. | `Gate_10_v6_worker.md` |
| B: restored timeline and both-map admission | R2/R3 after A. Bind sample/report/initial and portable/checkpoint clocks, verify expected step/time increments; guard actual restored coordinates before energy evaluation, pending creation or stepping. | `Gate_10_v7_worker.md` |
| C: published-failure evidence and durable rename/replay | R5/R6 after B. Immutable commit authority plus separate cached all-worker/map failure capture; fsync all preserved files/nested directories and both rename parents. Final combined verification and fresh bounded pilots. | `Gate_10_v8_worker.md` |

Root checks each completed report, raw results, exact snapshots and scope before
starting the next worker. Finish and verify **all three tasks** before one new
combined Sol 6.1/max audit; no intermediate implementation audit or review of
unfinished work. The final matching audit record is created only when performed.
Keep all v5 failures/findings and every repair trial/decision unchanged in logs.

## Contracts and independent expectations

Use the [reviewed design](../specs/g10-multistate-runtime-amendment.md), its
[plan](../../../Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md),
the complete v5 findings and [independent reproducers/results](../../../Worker_Log/Milestone_05/evidence/G10_v5_independent/README.md).
The v5 audit accepts the numerical comparator rationale, not the implementation:
keep `1e-15 nm` captured-position roundoff, exact portable/checkpoint/velocity/
box/parameters and own-snapshot identities, and existing `1e-8` energy/full-force
bounds. Do not weaken them. If a scientific definition or tolerance change is
actually necessary, complete its standalone design/review prerequisite first.

R1 cases must reject before trusted load or output initialization with evidence
unchanged, including each worker seed (`seed_base + N - 1 < 2**31`), the exclusive
one-million-step limit, Boolean fields, invalid finite Gaussian cache, conflicting
inverse, malformed report clock and false sample physical/transfer identities.
Retain valid three/eight-state and cached-normal roundtrips.

R2 must reject the resealed step-99/time-9.99-ps checkpoint after a saved
step-1/time-0.0005-ps sample before evaluation, pending creation or stepping.
Cover portable/checkpoint mismatches and backward/skipped clocks. R3 must reject
energy-consistent invalid **both** map0 and map1 coordinates at that same point,
using unchanged full guards and thresholds.

R4 must bind each refreshed total to the correct same-attempt raw-matrix entry
for actual accepted/rejected assignment, including the nonzero outside term;
the saved `+123 kJ/mol` contradiction must reject inertly. No Hamiltonian or
Metropolis duplication. R7 must detect added/modified nested `manifest.json`
bytes before load and preserve symlink, normal sealing and replay checks.

R5/R6 tests must inject actual source/destination-parent fsync failures and each
records/observations/summary write failure, preserve immutable committed hashes,
primary and secondary errors plus every available cached State/checkpoint/both
map State, and prohibit energy/force reentry. Trace real syscall ordering: every
preserved file and nested directory before archive rename, both parents after
cross-directory rename. Claim syscall coverage, not observed power-loss proof.
Explicit rollback/replay must retain every failure and recreate exact committed
records/permutations/checkpoints/both host RNG streams without duplicates/loss.

## Bounded verification and preserved evidence

Every scientific shell activates `/workspace/m05-cpu-setup-v2/activate.sh` and
sets `OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. CPU jobs are serial on the
two-CPU/8-GiB profile. Tiny analytic controls; final molecular verification uses
unchanged v2 fixtures, three actual workers, two boundaries/one step, only four
bounded preparation-count overrides. Preserve raw failures and new frozen-source
attempts; never migrate old bundles to new source.

Each worker first reproduces relevant RED expectations, makes only its bounded
repairs and reruns changed requirements plus retained pair/export/restart checks.
Task C runs the available full CPU suite once on the **finished combined source**
after all meaningful engine repairs, plus fresh shared-engine v2 ABFE/RBFE pilots.
Root verifies counts/skips/exit statuses and hashes before the combined audit.
Do not repeat unrelated scientific reviews. Each worker records model/effort,
exact base/source/result/report snapshots, UTC, commands, raw outputs and
RED/GREEN history, source/artifact hashes, remaining findings and clean status.
Intermediate self-checks close no independent assertion.

Protect pair APIs, pinned adapter/Hamiltonian/units/derivatives, full forces,
caps/complete ligands/maps, fixtures, locks/model bytes, original worker/audit
records and scientific ledgers. No QM/GPU/production/HPC execution or scripts.
G07 retains seven sensitivity exceedances, original pilot force failures and
29 missing references; all 46 G05 records and charged ledger
`2325.6446500519996 / 86400 s` with false continuation screen remain unchanged.
Full G10/M05, chemical accuracy/protein, affinity/equilibrium/mixing/convergence,
correlated-walker uncertainty and GPU/HPC/release remain open or blocked.
