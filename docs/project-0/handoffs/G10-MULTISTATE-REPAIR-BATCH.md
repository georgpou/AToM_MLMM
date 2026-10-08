# G10 v5 RED — bounded sequential repair batch

**Prepared:** 2026-10-06 UTC. **Branch:** `g10-engine-next`.
The complete Sol 6.1/max [v5 audit](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/Gate_10_v5_audit.md)
finished RED before repairs began (`a90e192ec0d87524e8fbf77a18d62b4b81a37195`).
Its seven findings and every failed characterization remain preserved. Root
verified all 29 independent hashes and unchanged reviewed source. Numerical
energy/force/decision checks passed; runtime admission and durability did not.

The original three-task plan is retained in commit `c27358668499ef596a73468936bc21279ebb1b6a`.
The user requested faster progress. Keep completed/active Task A unchanged and
combine the remaining runtime/durability repairs in one bounded worker, reducing
onboarding and duplicate compatibility runs without waiving any assertion.

| Sequential task | Required repairs | Worker record |
| --- | --- | --- |
| A: inert admission and record/seal consistency | R1/R4/R7; complete types/limits/all-worker seeds/RNG/inverses/sample identities; inert clock types/agreement; refresh binding; root-only manifest exclusion. | `Gate_10_v6_worker.md` |
| B: restored runtime and failure durability; final combined verification | R2/R3/R5/R6; actual restored/portable/report/sample clocks and expected increments; actual restored both-map guards before any evaluation/step; cached postcommit failure records; every rollback file and both rename parents synced. | `Gate_10_v7_worker.md` |

Only root spawns. Exact workers `gpt-6-luna / max`, auditor `gpt-6.1-sol / max`;
at most root plus one running side agent. Root verifies each completed FINAL
report, raw results, hashes and clean snapshot before the next task. Finish the
entire batch before one combined audit, expected `Gate_10_v7_audit.md` only when
actually performed. Let that auditor finish before repairs; repeat the complete
repair/review loop if material findings remain. Self-checks are not independent
acceptance. Root does not implement fixes.

Use the [reviewed amendment](../specs/g10-multistate-runtime-amendment.md),
[v3 plan](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md),
complete v5 audit and [independent reproducers/results](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_independent/README.md).
Every negative must reach its intended validator: R2/R3 energy-consistent cases
must pass repaired inert arithmetic/type checks. Verify no loader/output mutation
for inert failures, and no evaluation/pending/step for invalid restored clocks or
both-map geometry. Keep the reviewed `1e-15 nm` position roundoff guard, exact
portable/checkpoint/velocity/box/parameter and own-snapshot checks, and existing
`1e-8` energy/full-force bounds. Document clock comparison rationale; scientific
definition/tolerance changes require standalone review first.

Publication is authoritative after rename. Actual parent-fsync and each derived
write fault must preserve immutable commits plus primary/secondary errors and
all available cached worker checkpoint/State/both-map State evidence separately,
without energy/force reentry. Trace every preserved file/nested directory before
rollback archive rename, and both rename parents afterward. Preserve exact
whole-boundary replay, sample IDs/history/permutations/both RNG streams without
duplicate/lost records. Syscall tests do not prove observed power-loss behavior.

Every scientific shell activates `/workspace/m05-cpu-setup-v2/activate.sh` and
sets `OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. Serial two-CPU/8-GiB jobs;
tiny analytic controls. Final worker uses fresh exact v2 224-atom ABFE and
233-atom unequal-ligand RBFE attempts through the shared engine: three workers,
two boundaries/one step, only four preparation-count overrides. Preserve old
frozen sources/failures; never resume/migrate old bundles under new source.

Test changed requirements first. Final available CPU suite runs once on finished
combined source and includes the required persistent/replica/export/solvated
restart files, avoiding a separate duplicate compatibility run. Rerun only for
new source changes/failures. Record concise RED/GREEN evidence, exact snapshots,
commands/exits/counts/skips/source hashes, model/effort/UTC, protected-tree checks
and docs/whitespace results. Keep all earlier failures and decisions immutable.

Protect pair APIs, pinned adapter/Hamiltonian/Metropolis, chemistry/maps/caps/full
real forces/units/derivatives, fixtures/locks/model bytes and reference ledgers.
No QM/GPU/production/HPC scripts/jobs. All 46 G05 records, seven G07 sensitivity
exceedances, original pilot force failures, 29 missing references and charged
`2325.6446500519996 / 86400 s` ledger with false continuation screen stay unchanged.
Full G10/M05, chemical accuracy/protein, affinity/equilibrium/mixing/convergence,
correlated-walker uncertainty and GPU/HPC/release remain open/blocked;
`binding_result=not_evaluated`.
