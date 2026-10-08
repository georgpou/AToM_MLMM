# G10 completed implementation — paused before combined audit

**Prepared:** 2026-10-06 UTC. **Workspace:** `/workspace/AToM_MLMM-g10`.
**Branch:** `g10-engine-next`. **State:** implementation batch finished;
independent combined implementation audit **NOT STARTED**.

The user clarified the assignment as “G10 design review, implementation, and
audit”, then requested a graceful pause immediately before the Sol 6.1/max
implementation audit. All four side agents have completed and no scientific
calculation remains running. Resume only when the user continues the work.
This packet is orchestration evidence, not an independent review or acceptance.
[STATUS](../STATUS.md) remains the live qualification summary.

## Exact snapshots and completed prerequisites

| Snapshot | Identity and meaning |
|---|---|
| Fresh predecessor | `3952a9b36a92e37f0f98fdf3981c9320368a18b3`, cloned from `cloud-engine-continuation` |
| Accepted ancestor | `2c02cc2713924140a82aefda37fd5885747e5837`, ancestor check passed |
| Standalone design submission | `678aa3e2db9d5f77517ad8cfb278ac8a4df7032d`; content `179c3035c6b70293811b6dd6e24319fd9ac932db` |
| Standalone design audit | `bd44b2c93a5cba40225dba632f0277e535467be9`, Sol 6.1/max, GREEN for design only |
| Core implementation | `cef01748db1d872775c1cb88e67f881182066e6c` |
| Secondary-archive test follow-up | `5a8ab584cc9af9e74afb7f2d926ca8b4af688e41` |
| Core report / pilot starting point | `1f26d2e52f63f0d3b734c5e5dd0f4fe0f51dd8df` |
| Final combined code and pilot tests | `a507bbddfccc1a88b8df4ab18277040889bf379c` |
| Finished combined worker submission | **`ecace38b34e15fae65508b2ee9cd2f535a1b85c4`**; report-only follow-up to final code |

The subsequent root pause-packet commit changes reporting only. Obtain its
identity with `git rev-parse HEAD`; source, tests, fixtures, environment, models
and runner usage must match the finished worker submission exactly. No push,
reset, rebase or merge was performed. Main and published predecessors remain
unchanged. The separate original `/workspace/AToM_MLMM` checkout is not this
G10 branch; do not switch to it accidentally.

## Auditor inputs

Read [AGENTS](../../../AGENTS.md), [DEVELOPMENT](../../DEVELOPMENT.md), the
[CPU setup guide](../../../environment/cloud-cpu/README.md),
[G10-T2/T3](../gates/G10-restart-and-replica-exchange.md), relevant
[S05](../specs/S05-protocol-and-thermodynamic-contracts.md) and
[S07](../specs/S07-artifacts-and-qualification.md) sections, and the following
completed records. Earlier reviews need reopening only for a relevant change
or new failure.

- [Reviewed multistate design](../specs/g10-multistate-runtime-amendment.md),
  [implementation plan](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md),
  [design worker](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/Gate_10_v3_worker.md) and
  [standalone design audit](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/Gate_10_v3_audit.md).
- [Core worker](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/Gate_10_v4_worker.md) and its
  [RED/GREEN history](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v4/red-green-regressions.md).
- [Pilot/combined worker](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/Gate_10_v5_worker.md),
  [evidence index](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5/README.md),
  [repair diagnostics](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5/repair-diagnostics.json),
  [source inventories](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5/source-inventory.json) and
  [compact actual-context/replay export](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5/final-pilot-export.json).
- [Prepared auditor instructions](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/auditor-instructions.md),
  [original core assignment](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/core-worker-instructions.md) and
  [original pilot assignment](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/pilot-worker-instructions.md).
- [Exact combined runtime/test/usage diff](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/combined-runtime.diff.gz),
  [complete changed-path list](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/combined-changed-paths.txt) and
  [root verification with hashes](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v5_review_packet/orchestrator-verification.json).

The compact diff is from the accepted design audit `bd44b2c…` to the completed
worker submission `ecace38…`: six implementation/test/usage files, 2,569
insertions and three deletions, 151,308 bytes; SHA-256
`9fc744b7d305dbaf3797e9bd28e2664b2550a00fbf99e56c1ace6067bffe9bd6`.
The tracked diff is gzip-compressed without changing its bytes; decompress it
for review. Only `exchange.py` and `exchange_journal.py` change in production source.
The adapter, workflow, persistence, analysis, scientific specifications,
fixtures, locks/model assets and protected reference records remain unchanged.
All other changes are listed in the complete path inventory.

## Finished batch and audit assertions

Audit all four tasks together: inert admission/source identity; serial live
state-permutation scheduling/fresh pair matrices; durable all-worker transactions
and rollback/replay; shared-engine solvated pilots/usage/combined verification.
The additive APIs are `run_multistate_exchange`, `resume_multistate_exchange`
and `read_multistate_boundaries`, with separate multistate mode and unchanged
pair API. The reader returns flattened boundary dictionaries.

Require coding, physics/chemistry and mathematics decisions for the full declared
scope. Trace type/limit/source admission before executable load; three to eight
distinct 300 K states and explicit connected unique ordered edges; stable walker
identities and current inverse permutation; capture-time labels and unique IDs;
fresh four-entry complete potentials for every pair through the existing pinned
AToM adapter; parameter refresh and nonzero outside terms; full influencing real
forces, caps/parents, complete ligands and both-map guards. Verify durable
decision/history before refresh, recursively sealed all-worker checkpoints and
both host RNG streams with one atomic rename, failure preservation, default
pending rejection, explicit whole-boundary replay, postrename authority and
fresh restored-context checks before integration. Inspect actual fault assertions
and independent oracles, rather than accepting test names or worker claims.

For overlapping accepted pairs `(0,1),(1,2)`, initial permutation `[0,1,2]`
must become `[1,0,2]`, then `[2,0,1]`, resolving walker pairs `(0,1)`, then
`(0,2)`. At 300 K, beta is `0.4009078501424201 mol/kJ`; dimensionless exponent
is `v_i(y)+v_j(x)-v_i(x)-v_j(y)` and probability is `min(1,exp(-delta))`.
Verify both forced positive-exponent accept/reject cases, raw-energy
reconstruction, units/signs and unchanged force/derivative contracts.
Ordered pair-kernel stationarity is the declared mathematical claim; whole-sweep
reversibility, mixing, equilibrium, converged affinity and exchanging-walker
uncertainty are unqualified. Raw records remain correlated and
`binding_result=not_evaluated`.

## Numerical repair and retained failures

The water pilots exposed representation failures after analytic controls passed.
All four failed pytest traces are retained byte-for-byte in compressed logs;
their uncompressed local copies and hashes verify. Their outcomes remain failures:

| Attempt | Actual result and reason |
|---|---|
| `focused` | 2 failed / 83.53 s; captured-sample versus refreshed-context coordinate digest |
| `repaired` | 2 failed / 94.99 s; saved versus restored `total.snapshot_identity` |
| `repair2` | 2 failed / 129.37 s; test expected nested reader record, before numerical oracle block |
| `final-focused` | 2 failed / 162.39 s; test-only stale-probe permutation lookup, after numerical checks/replay |
| `probe-fix1` | 2 passed / 156.56 s; all numerical, restart and deliberately stale-state checks |

Root verified exact inventories and source hashes of all 20 prepared/controller
worker bundles across these ten case/attempt combinations. Original runtime
bytes are retained; no old attempt was silently resumed under new source.
The first source repair is also tracked as `repair1-exchange.py`; the final
source as `repair2-exchange.py`, both under the v5 `source-snapshots/` directory.

**Independently review the comparator repair.** OpenMM unit round trips measured
position drift at most `6.5052130349130266e-18 nm`. A new absolute `1e-15 nm`
checkpoint-to-captured-sample position bound replaces byte equality there.
Sample/report hashes, portable-State/checkpoint equality, sample velocities/box,
parameters, units and atom identities stay exact. Saved/fresh snapshot identities
must each match their own snapshot. Raw energy fields now use the existing
`1e-8 kJ/mol` bound; total/full-force bounds stay `1e-8`. These are real
technical comparison changes requiring review of rationale, finite/type handling
and design-contract compliance, not authority to waive physical tolerances.
The deliberately resealed real-atom displacement `2.000177801164682e-12 nm`
passed inert validation but was rejected at runtime before evaluation or pending
boundary creation. Do not infer acceptance from this packet.

## Actual verification and retained artifacts

| Final-source check | Observed result; no skips |
|---|---|
| Two solvated multistate pilots | **2 passed in 156.56 s** |
| Required pair/export/restart files after repair | **74 passed in 171.69 s** |
| Available full CPU suite, run once | **577 passed in 913.26 s** |
| Final worker docs | Zero errors; eight self-tests, 214 Markdown files / 1,459 local links |

The complete final logs are in `Worker_Log/Milestone_05/evidence/G10_v5/`.
Root read their outcomes and verified all 24 submitted manifest entries against
`ecace38…`; it did not repeat scientific tests or perform an independent audit.
The worker manifest's STATUS hash refers to that submitted snapshot; this pause
update changes STATUS reporting only. Verify historical hashes from the named
Git snapshot rather than treating later reporting as original worker evidence.

Complete successful artifacts are at
`/workspace/G10_v5_artifacts/probe-fix1/{abfe,rbfe}/`, including prepared workers,
committed runs, copied-prefix replays, actual-context oracles, stale-state probes
and resource records. Failed trees remain under the four attempt names above;
uncompressed logs are in `/workspace/G10_v5_artifacts/raw-logs/`. These local
trees do not automatically transfer to a replacement machine. Tracked compact
exports, source snapshots, identities and the bounded reproducer are in Git;
missing local evidence must be marked unavailable, never silently migrated.

Both cases use the immutable v2 64-water fixtures through `run_configuration`,
only four bounded preparation-count overrides, three workers/all three states,
two boundaries and one integration step per boundary. ABFE has 224 real atoms;
RBFE has 233 and unequal complete methanol/acetamide ligands. Each retains six
samples, four attempts, 18 nonzero outside evaluations and complete 3-by-6
actual-context reduced energies, with maximum reconstruction error `0.0`.
This is not the future crown methanol-to-ethanol RBFE input.

The pytest-parent pilot sampler measured at most 2,087,329,792 bytes during its
recorded operation windows; it includes the harness and excludes the later
oracle/probe block. A near-end full-suite sample showed 6,676,272 KB RSS,
not a continuously measured peak. The machine limit is 8 GiB/two CPUs. These
bounded observations make no G13 release, GPU or HPC performance claim.

## Resume protocol and limits

On continuation, root verifies clean branch/HEAD, packet hashes and unchanged
source/tests, then spawns exactly one auditor using **`gpt-6.1-sol` / `max`**
with `fork_turns="none"` and the prepared instructions. Only root spawns; the
auditor must not spawn. Freeze reviewed source/tests/specifications until its
complete FINAL report. No concurrent worker, repair or additional audit.

Every scientific shell activates:

```bash
cd /workspace/AToM_MLMM-g10
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

A replacement machine installs unchanged locks using `environment/cloud-cpu/install.sh`
with its own external prefix. The validated local profile is Python 3.11.16,
OpenMM 8.6.1 Reference double, atom-openmm 8.5.0b0, MACE 0.3.16 CPU float64,
NumPy 2.4.6 and Torch 2.8.0. Independent probes must be focused and serial,
bounded by three molecular workers/four boundaries/two steps; no new full-suite
repeat without a relevant reason, and no QM/GPU/production/HPC jobs.

Create `Gate_10_v5_audit.md` and `evidence/G10_v5_independent/` only when an
independent review is actually performed. Record exact reviewed identity,
actual model/effort, raw evidence, every finding and final scoped C/P/M decision.
Let that final report finish before any repair. If RED, delegate the entire
bounded repair batch sequentially to `gpt-6-luna` / `max`, verify it, then audit
again with Sol 6.1/max. Root must not implement repairs. Do not substitute models
or relax tolerances to complete the loop.

G07 remains physically blocked: seven sensitivity exceedances, pilot force
failures and 29 missing new references. Preserve all 46 G05 records and the
charged ledger `2325.6446500519996 / 86400 s`, with false continuation screen.
Full G10/M05, molecular accuracy, protein physics, production, solvent
equilibration, affinity and exchanging-walker uncertainty remain open.
Preferred future host–guest RBFE methanol-to-ethanol in 18-crown-6 still needs
independently qualified input. Long calculations and cluster qualification await
HPC resources. A future scoped implementation GREEN does not close these blockers.
