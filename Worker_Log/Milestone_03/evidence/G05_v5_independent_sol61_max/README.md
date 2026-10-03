# G05 v5 independent closure evidence

Canonical decision: [Gate_05_v5_audit.md](../../Gate_05_v5_audit.md). Reviewer is the user's configured **GPT-6.1 Sol / MAX** independent reviewer continuing its fresh-context v4 audit. Scope is R1/R2/R3 closure, preserving prior science. No real QM or finalized coordinator was run, and no source/STATUS changes were made.

- [audit-start.json](audit-start.json): clean initial tree, exact repair/source/base identities and hashes.
- [recovery-closure.json](recovery-closure.json) and [recovery-closure.log](recovery-closure.log): fresh 41-case focused replay, all passed.
- [supervisor-loss.json](supervisor-loss.json), [supervisor-loss.log](supervisor-loss.log), [test source](test_supervisor_loss.py), [observed facts](supervisor-loss-probe/observed.json): intended failing contract assertion, proving the remaining R2 supervisor-loss path with synthetic subprocesses. Probe cleanup kills the orphan group.
- [preservation.json](preservation.json): 1,435 unchanged v4 snapshot files, 46 unchanged reference records, unchanged v4 submitted/reviewer science and history, exact 105-package reference lock; inspected worker 335-test/9-check/docs results are clearly distinguished from reviewer executions.
- [final-state.json](final-state.json): exact final HEAD, submitted-source hashes, index/tree invariance and worker cleanup.
- [final-docs.log](final-docs.log): final documentation self-test output; command/timing receipt is `final-docs.json`.

The independent probe's fixed directory is an exclusive evidence destination. Replay requires a new directory, rather than overwriting these files. Synthetic fixture progress mutates only within that new probe directory; submitted scientific/attempt files are untouched. `run_check.py` writes each command's output and receipt exclusively.

R1 and R3 are closed. R2's launch/checkpoint fix passes, but a surviving coordinator schedules more work after its supervisor is killed while the prior reference child remains live. Verdict: **changes_required**. The next review should target that single process-group cleanup repair and inherit the unchanged prior scientific/R1/R3 evidence.
