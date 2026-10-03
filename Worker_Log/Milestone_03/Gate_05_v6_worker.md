# G05 final R2 supervisor-loss repair — v6 worker

**Scope:** Close the remaining R2 case from the
[v5 audit](Gate_05_v5_audit.md). R1 and R3 were independently closed there.
The user authorizes repairs and publication of `m03-reference-g05`.
**Base:** `8738d16f8d3813f03c6f05a5c89a4be107159c19`, same child branch.
**Source/result:** Exact source commit and hashes are in the
[v6 snapshot](evidence/G05_v6/snapshot.json).
**Outcome:** Ready for focused final R2 closure; no new independent acceptance
is claimed by this worker.

After every supervisor exit, the coordinator retains its identity while it
reconciles the full process group, sends termination signals to survivors and
waits for no live group members. If cleanup cannot be verified, it rejects
further scheduling. This occurs before receipt publication, record promotion,
scratch deletion and the next launch. Negative supervisor exits remain known
failures; receipt metadata records survivors and successful group cleanup.
The existing coordinator-loss guard, inherited lease, PID/start-tick protection,
resource/deadline accounting and receipt/durability repairs are retained.

Only `tools/resume_neutral_quantum.py` and its maintained interruption test
changed after v5. The independent failing supervisor-loss reproduction was
added to the source suite using synthetic executables under pytest temporary
directories. It kills an actual supervisor, verifies its reference child is
gone before another launch, preserves exit `-9` and prevents ready publication
for the failed attempt. No synthetic result enters chemical fixtures.

## Validation

All scientific shells activated `/workspace/atom-mlmm-g05-v2/activate.sh`.

| Command/check | Actual outcome |
|---|---|
| New supervisor-loss RED | **1 intended overlap failure**, exit 1, retained in v6 evidence |
| Targeted interruption/lock/timeout/supervisor-loss GREEN | **11 passed in 33.39 s**, exit 0 |
| `python -m pytest -q` on final source | **336 passed in 213.92 s**, exit 0; includes all **42** recovery cases, eight stable G05 assertions and both actual chemical comparisons |
| `python /workspace/atom-mlmm-g05-v2/validate.py --repository "$PWD"` | **9/9 passed**, exit 0 |
| Read-only preservation checker | All **46** records validated; all **1,435** unaffected v4 snapshot entries, reference lock, frozen manifests and actual history/evidence bytes unchanged |

[Logs and preservation record](evidence/G05_v6/) preserve actual results.
R1/R3 and earlier launch-boundary/durability RED/GREEN remain in v5 evidence;
the unsuccessful intermediate v5 review is retained rather than relabeled.
No real QM job, finalized coordinator or reference regeneration ran. Saved
calculation source stays `419b64f7bd79199a0bf999e456f1564fc184cf75`; the 46-record
manifest hash stays `48565f02f39afae45132ea4048ea8302f170b3e0efef0702228fa6ff3c809ad0`.
No scientific settings, limits, locks, model assets or production ML/MM source
modules changed. This verifies OS/process behavior with synthetic processes;
no actual power failure or new Psi4 calculation is claimed.

## Handoff

Sol 6.1/MAX should perform focused closure of the v5 supervisor-loss finding
using its preserved independent reproduction and this new snapshot. Prior
scientific evidence and R1/R3 closure apply only because those paths/data are
unchanged and the complete suite passed on final source. After acceptance,
update live STATUS, publish the explicitly authorized branch and verify the
remote SHA. Main and accepted predecessors remain unchanged. G06/G07,
protein/periodic/GPU/electrostatic/sampling and complete ABFE/RBFE remain outside
scope; M03 still needs G07 combined review.
