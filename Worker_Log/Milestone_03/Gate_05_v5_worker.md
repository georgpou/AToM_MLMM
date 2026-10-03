# G05 recovery findings R1/R2/R3 — v5 worker

**Scope:** Repair the three findings from the [v4 audit](Gate_05_v4_audit.md),
preserving the completed neutral CPU reference data. The user explicitly
authorized these repairs and publication of the existing `m03-reference-g05`
branch. No QM calculations or finalized coordinators were rerun.

**Base:** `439314ba2b306651de2947f914f4cdda44e6dbae` on the same child branch.
**Source/result snapshot:** The [snapshot record](evidence/G05_v5/snapshot.json)
identifies the immutable repair source commit and exact changed-file hashes.
Actual calculation source remains `419b64f7bd79199a0bf999e456f1564fc184cf75`;
saved source/data baseline remains `a99a4448f14386e79c1546dd32fd83a33b9ac424`.
**Outcome:** Ready for independent repair closure; full G05 acceptance is not
claimed by this worker.

R1 now reads and validates per-attempt completion receipts during salvage and
checkpoint restoration. Known nonzero exits, timeout/resource stop reasons and
validation errors remain failures; retries preserve their original records and
receipts. Known successful exits remain known, and genuinely absent receipts
remain unknown. New receipt hashes bind the exact saved worker record. A
previously admitted known failure is rejected before further scheduling.

R2 uses a small standard-library supervisor. It inherits the queue's flock lease
across spawn, waits on a pipe until its identity is durably checkpointed, and
terminates its whole process group when the coordinator disappears. The raw
reference worker also retains the lease. Legacy processes under attempt
directories are reconciled before launch; persisted PID/start ticks still
protect against PID reuse. RSS samples include reference children and the
supervisor. The method, reference interpreter, two Psi4 threads and allocation
cap are unchanged.

R3 publishes worker JSON and promoted records using fsynced bytes, atomic rename
and directory fsync. Receipts and their directory entries are durable before
admission; source records and promoted copies precede progress/ready manifests.
Legacy restored data are synced before new checkpoints. A missing published
copy can be restored from its surviving validated per-job source without
rerunning the calculation; present corrupted copies still block recovery.

## Validation

All shells used `/workspace/atom-mlmm-g05-v2/activate.sh`. Synthetic workers
execute only software stand-ins under pytest temporary directories; they are
never added to chemical fixtures.

| Command/evidence | Actual result |
|---|---|
| Receipt regression RED / GREEN | 6 intended failures and 1 pass; then all 7 passed |
| Launch-boundary RED / GREEN | 3 intended orphan failures and 1 pass; then all 4 passed |
| Durability/restoration RED / GREEN | Intended missing-fsync, non-atomic-write and missing-copy failures; then all 3 passed |
| Legacy durability RED | Both intended unsynced legacy checkpoint failures reproduced before repair |
| `python -m pytest tests/unit/test_quantum_recovery.py tests/unit/test_quantum_interruptions.py -v` | **41 passed in 92.52 s**, exit 0 |
| `python -m pytest -q` | **335 passed in 205.14 s**, exit 0 |
| `python /workspace/atom-mlmm-g05-v2/validate.py --repository "$PWD"` | **9/9 passed**, exit 0 |
| `check_preservation.py reference-preservation.json` | All **46** records validated; **1,435** untouched snapshot files match; only three existing repair source/test files and live STATUS differ from the v4 manifest; reference environment lock matches |

The initial combined interruption RED run included an after-authorization
test-driver timeout because the old code had no authorization stage. The driver
was corrected to fault the equivalent old running-worker stage; the retained
second RED run has three intended orphan assertions. This intermediate failure
is not counted as a successful reproduction. All logs remain in
[v5 evidence](evidence/G05_v5/).

The bare suite includes all eight G05 stable assertions, both actual chemical
comparisons and all numerical controls. The quantum fixture manifest hash is
unchanged: `48565f02f39afae45132ea4048ea8302f170b3e0efef0702228fa6ff3c809ad0`.
All original/resumed QM records, orders, logs, receipts, report captures, model
weights, frozen inputs and limits remain byte-identical. Real guard behavior
with Psi4 is not newly calculated; crash/group/lock behavior is exercised using
actual synthetic processes, pipes, flocks, fsync traces and forced coordinator
exits. No actual power failure was injected.

## Handoff

Independent Sol 6.1/MAX closure should check R1/R2/R3 on this exact repaired
snapshot, inherit only unchanged valid v4 scientific evidence, and avoid QM
regeneration. After closure, publish the authorized branch and verify its remote
SHA. Main and earlier accepted branches remain unchanged. Protein, periodic,
GPU, electrostatic, sampling and complete ABFE/RBFE remain outside scope;
M03 still needs G07 combined review.
