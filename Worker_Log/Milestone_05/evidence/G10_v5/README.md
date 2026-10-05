# G10 v5 pilot evidence

This folder records Task 4’s bounded v2-water pilots, the necessary snapshot
freshness repair, all focused attempts, post-repair compatibility checks, and
the combined CPU-suite result. It is implementation evidence for the Task 4
scope, not Gate 10 or M05 acceptance.

The complete run trees are retained locally outside Git at
`/workspace/G10_v5_artifacts/`. The successful integrated attempts are
`probe-fix1/abfe/` and `probe-fix1/rbfe/`; the earlier failed attempts are
`focused/`, `repaired/`, `repair2/`, and `final-focused/`. These artifacts are
available in this workspace but are not automatically copied to replacement
or HPC machines. The tracked exports deliberately contain hashes and compact
diagnostics instead of another copy of the model assets.

## Pilot result

`pilot-probe-fix1.log` records **2 passed in 156.56 s, no skips**. Each case
started from an unchanged copy of its v2 fixture, changed only the four
bounded preparation counts, prepared through `workflow.run_configuration`,
then used three actual workers, all three 300 K schedule states, ordered pairs
`((0,1),(1,2))`, two boundaries, and one integration step per worker per
boundary. The ABFE case contains 224 real atoms; the unequal-ligand RBFE case
contains 233. Both completed with six samples and four pair attempts. Every
sample retains ordered real atom IDs, full forces, raw fields, parameters,
velocities, periodic box and both-map geometry diagnostics. The checks also
retain stable IDs/sequences, capture-time states, full permutations, pair
resolution, accepted-state refresh and all-worker replay bytes.

The independent energy oracle used each saved boundary coordinate on all
three actual worker contexts. All four 2-by-2 pair matrices per case,
including the nonzero outside anchor, matched the actual-context raw and
reduced energies within the existing `1e-8` tolerance. The six-column full
schedule reconstruction matched actual contexts with maximum absolute reduced
energy error `0.0` in both cases. The outside anchor was nonzero for all 18
sample/state evaluations per case. Replay started from an identical copied
committed prefix; all final boundary artifacts, worker State/checkpoint bytes,
RNGs, raw observations, decisions, histories and permutations matched, and
the initial and first committed-prefix bytes remained unchanged.

Each successful run also includes a deliberately resealed worker-0 checkpoint
and portable State shifted by approximately `2.00018e-12 nm` from its saved
sample. The inert journal reader accepted the correctly resealed tree. Runtime
resume rejected it with `restored checkpoint coordinates differ from captured
sample beyond unit-conversion roundoff`, before any `WorkerRun.evaluate` call
or pending-boundary creation. See the per-case
`stale-coordinate-rejection.json` files and `final-pilot-export.json`.

`resource-metrics.json` samples the pytest parent process’s `VmRSS` every
10 ms during preparation, the initial one-boundary prefix, each continuation,
and replay. This scope includes the Python/test harness and does not sample the
later independent oracle/probe assertions. The controller’s `summary.json`
separately records each run’s elapsed execution and process high-water RSS as
reported by `getrusage(RUSAGE_SELF)`. The pilot machine memory limit was
8,589,934,592 bytes; the largest sampled continuation RSS was 2,087,329,792
bytes (RBFE). The whole focused pytest invocation took 156.56 s. These are
bounded-run resource measurements, not resource qualification for longer
simulations.

## Repair and comparison record

The starting source was exactly clean HEAD
`1f26d2e52f63f0d3b734c5e5dd0f4fe0f51dd8df`; its `exchange.py` SHA-256 is
`801757d189765d4b28088fe5dcc98b46866c5ae0e1257fd02d2eb3dba6cfeec2`.
`pilot-focused.log.gz` retains the first two molecular attempts and their
`focused/` bundles. They exposed an exact report/sample coordinate-digest
rejection after an actual pair energy refresh had round-tripped coordinates
through OpenMM unit conversion. The measured position difference was at most
`6.5052130349130266e-18 nm` (ABFE at most `5.421010862427522e-18 nm`); no
integration step occurred between capture and the refresh.

The first minimal source repair is retained verbatim as
[`source-snapshots/repair1-exchange.py`](source-snapshots/repair1-exchange.py),
SHA-256 `4e592c9e045dd9ca1efbb084d81f07ac2c606c9f5366453a8ea02d8de62d01f9`.
Its fresh runs are retained under `repaired/` and in `pilot-repaired.log.gz`.
After admitting the measured coordinate round trip at `1e-15 nm` and using
`1e-8 kJ/mol` raw-energy comparison, both reached the complete raw/total/
parameter guard and failed only on `total.snapshot_identity`. My comparison of
the retained actual-context repair1 attempts found zero difference in every
raw field, total energy and full force, with parameters unchanged. This failure
is retained; it was not reclassified as a pass.

The final source is retained verbatim as
[`source-snapshots/repair2-exchange.py`](source-snapshots/repair2-exchange.py),
SHA-256 `317fca331def3ef32be709f3ad77f63cd888788e3f335a8cf5ad45df67e1aec9`;
the same bytes are in the current `src/atm_mlmm/exchange.py` and every final
worker bundle. It preserves the exact hash from the report to the captured
sample and independently checks the restored checkpoint snapshot identity.
Portable-State/checkpoint coordinate, velocity, parameter and box equality
remains exact. Captured-sample/checkpoint positions use the explicit
`1e-15 nm` round-trip bound; sample velocities and box remain exact. Raw
energy fields use absolute `1e-8 kJ/mol` comparison. Total energy and every
full-force component retain their existing `1e-8` tolerances; parameters,
units, identities, runtime/platform and force ownership remain exact. The
accepted Hamiltonian and physical definitions, adapter, Metropolis path and
physical tolerances were not changed.

`pilot-repair2.log.gz` records a test-contract-only failure after fresh execution
and byte-identical restart replay, before the independent numerical-oracle
block: the test looked for `pair_count` under a nested `record`, while
`read_multistate_boundaries` returns it at the boundary level. `pilot-final-focused.log.gz`
records the next test-only setup failure: the stale-probe helper looked for a
final permutation in run metadata instead of the final boundary record. The
successful fresh integrated attempt used the actual boundary-record
permutation, derived real-particle indices from the sealed worker bundle, and
passed the complete numerical-oracle block and stale-state rejection probe
for both fixtures. The exact failed stdout/stderr logs are gzip-compressed
without changing their bytes; uncompressed copies are also retained in
`/workspace/G10_v5_artifacts/raw-logs/`. The full failed attempt outputs and
matching source inventories remain retained. The exact
field differences, tolerance record and per-case deliberate rejection results
are machine-readable in [`repair-diagnostics.json`](repair-diagnostics.json).

## Verification and identities

All scientific commands sourced
`/workspace/m05-cpu-setup-v2/activate.sh` and set
`OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`; runs were serial. Final pilot
profiles record Python 3.11.16, OpenMM 8.6.1 Reference double, atom-openmm
8.5.0b0, mace-torch 0.3.16, NumPy 2.4.6, Torch 2.8.0, MACE CPU float64 and
distribution identity
`1865672db5d5a8db6c4d6abc4035d2eb0d70339cb85c1958f85eac7e7800fbf1`.
The source, fixture and exact worker-source inventories for every attempt are
in [`source-inventory.json`](source-inventory.json). Original v2 configuration
hashes are ABFE `95442f332740badd917230a5d7fd96786640eb371383d184b3947405668a57ac`
and RBFE `ea2accbd2902e9a3caa8eeea20deda99e2ff656bb3b7dac004b394950c11ecb9`.
The compact full-sample/oracle/replay export is
[`final-pilot-export.json`](final-pilot-export.json). The complete pilot
command is reproducible with [`run-pilots.sh`](run-pilots.sh). Tracked code,
fixture, report and evidence checksums are in
[`artifact-hashes.txt`](artifact-hashes.txt).

| Check | Result | Raw log |
|---|---:|---|
| First pilots on clean starting source | 2 failed in 83.53 s; coordinate identity exposed | `pilot-focused.log.gz` |
| First minimal repair | 2 failed in 94.99 s; only snapshot identity remained | `pilot-repaired.log.gz` |
| Second repair, before reader-shape test fix | 2 failed in 129.37 s; checks/replay passed before test assertion | `pilot-repair2.log.gz` |
| Stale-probe setup attempt | 2 failed in 162.39 s; test metadata lookup only | `pilot-final-focused.log.gz` |
| Fresh integrated pilots | **2 passed in 156.56 s; no skips** | `pilot-probe-fix1.log` |
| Required post-repair pair/export/restart suite | **74 passed in 171.69 s; no skips** | `required-post-repair.log` |
| Combined full CPU suite | See v5 worker report | `full-cpu-suite.log` |
| Docs self-test and whitespace check | See v5 worker report | `docs-self-test.json`, `git-diff-check.txt` |

No binding result was evaluated. No affinity, equilibration, mixing,
convergence or exchanging-walker uncertainty result follows from these short
technical runs. Full G10/M05 and the existing G07 physical/reference blockers
remain open; the 46 G05 records and the QM ledger
`2325.6446500519996 / 86400 s` are unchanged. No QM/GPU/production/HPC run was
performed.
