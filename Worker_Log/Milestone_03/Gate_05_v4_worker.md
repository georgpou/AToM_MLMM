# G05 reference recovery and chemical evaluation — attempt 4 — worker

**Scope:** Continue G05 on `m03-reference-g05`, recover the approved M00 v3
quantum references, validate numerical controls, then run G05-T4 and applicable
source/environment checks. Independent audit is deferred to the user's next
instruction; no reviewer is dispatched. G06/G07 remain outside this assignment.
**Outcome:** partial; recovery implemented and launch checks complete; actual QM
completion and chemical comparisons pending.
**Model/version:** GPT-6 / Codex; exact serving version not exposed.
**Reasoning setting:** not exposed.
**Checkpoint:** 2026-10-03T15:25:07+00:00.
**Previous worker/audit:** `Gate_05_v3_worker.md`; scoped software acceptance in
`Gate_05_v2_audit.md` remains inherited. No new independent audit is claimed.

## Snapshot and references

Recovered published checkpoint `4bb2547` into the same named child at
`/workspace/AToM_MLMM-m03-reference-g05`; the fresh machine initially contained
only main at `2d7bcc9`. Main and accepted predecessors remain unchanged.
Read the current AGENTS, STATUS, G05, exact M00 v3 reference plan, fresh-session
handoff, approved decision, launch/interruption/stop evidence, CPU environment
guide and development commands. The prior agreement persists.

Verified all eight stopped worker record SHA-256 values and all 46 frozen
input-file hashes. Prior worker time is 1931.9925 s; recovery conservatively
debits the entire launch-to-stop interval, **2350.09535 s**, including coordinator
and checkpoint overhead. Idle time during the user-requested pause is excluded.
The remaining authorized calculation budget starts at 40849.90465 s.

## Changes and decisions

- Added `tools/resume_neutral_quantum.py`: exact history/record validation,
  eight-record reuse, remaining queue, immutable per-job attempts, atomic
  progress with fsync, cumulative sessions/deadline, exclusive coordinator
  lock, old-worker detection, process-group termination and orphan-record
  recovery without fabricated coordinator exit receipts.
- Workers receive private scratch, two threads and a **3 GiB runtime allocation**
  under the approved 5 GiB upper cap. Frozen scientific settings stay unchanged.
  Actual allocation and worker maximum RSS are saved in new records. Each job
  gets sampled RSS/cgroup/disk evidence and an exit/resource receipt.
- Ruling: treat clean file cache and reclaimable slab as reclaimable — fresh
  locked installation brought total cgroup usage near its cap while anonymous
  RAM was about 1 GiB. Guard unreclaimable RAM and worker RSS at 7 GiB and disk
  headroom at 2 GiB; keep raw total/cgroup events in the evidence. The guard
  blocks the run, never changes a quantum method or numerical threshold.
- Ruling: a lost coordinator session is conservatively charged until recovery;
  unknown exit status remains unknown. Original attempts/orders/logs are kept.
- User instruction supersedes the handoff's Astra/high review step: perform
  implementation, calculations and reports here; notify when audit alone remains.

Rebuilt absent core/Amber environments using the maintained verified installer
and reference environment using the frozen 105-package explicit lock. The first
Miniforge bootstrap failed at the missing read-only Conda registry. Created the
narrow registry directory, preserved the incomplete prefix, and retried
successfully. Main, Amber and reference prefixes remain separate.

## Checks so far

Commands run from the child checkout after main activation unless indicated.

| Check | Actual outcome |
|---|---|
| Baseline `python -m pytest -q` | 292 passed; both named chemical reference tests failed for absent complete quantum bundle |
| Initial recovery RED | Six expected failed assertions because recovery runner did not exist; three negative cases initially passed for that same missing-file reason and were subsequently checked against the implemented runner |
| Initial recovery GREEN | 9 passed |
| Cache-guard regression RED | Failed expected memory-pressure assertion; captured in `g05-memory-guard-red.log` |
| Hardened recovery GREEN | 17 passed; synthetic records only, never chemical evidence |
| Live-worker missing-identity RED | Expected failure: recovery incorrectly admitted a live old PID when start identity was unavailable; repaired conservatively |
| Final focused recovery checks | 18 passed, including rejection of live workers with missing start identity |
| Repaired full source run | 309 passed / 2 absent-quantum failures; 17 recovery cases collected before the last added concurrency parameter; final 18-case full run underway |
| Final prelaunch full source run | 310 passed / 2 failures, exactly the two absent-quantum chemical checks; all 18 recovery cases included |
| Intermediate full source run | 297 passed / 6 failures: two absent-quantum checks plus four recovery cases stopped by the initial overstrict total-cache guard; retained and superseded by the repaired checks |
| Strict environment validation | 9/9 environment/documentation checks passed; exact results at installed-prefix validation JSON |
| Reference interpreter/basis check | Psi4 1.10.2; both actual basis-file hashes match frozen values |
| Read-only recovery check | 46 required names, 8 reused, exactly 38 scheduled; original hashes unchanged |

## Pending

Commit the calculation source; launch one QM worker;
complete all 38 remaining targets/controls within the cumulative budget. Validate
every row and numerical control before creating the hashed quantum fixture
bundle. Run both chemical nodes and report every exceeded limit without tuning
the science. Finish the required source checks and audit-ready snapshot/report.
Full G05 remains pending. The user will decide how to conduct the audit.
