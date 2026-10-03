# G05 reference recovery and chemical evaluation — attempt 4 — worker

**Scope:** Continue G05 on `m03-reference-g05`, recover the approved M00 v3
quantum references, validate numerical controls, then run G05-T4 and applicable
source/environment checks. Independent audit is deferred to the user's next
instruction; no reviewer is dispatched. G06/G07 remain outside this assignment.
**Outcome:** ready_for_audit; all assigned programming, 46 QM references,
12 numerical controls, actual chemical comparisons and reports are complete.
Independent full-G05 acceptance remains pending.
**Model/version:** GPT-6 / Codex; exact serving version not exposed.
**Reasoning setting:** not exposed.
**QM finished:** 2026-10-03T19:15:41+00:00. Final packaging time is recorded in
the audit snapshot metadata.
**Previous worker/audit:** `Gate_05_v3_worker.md`; scoped software acceptance in
`Gate_05_v2_audit.md` remains inherited. No new independent audit is claimed.

## Snapshot and references

Recovered published checkpoint `4bb2547` into the same named child at
`/workspace/AToM_MLMM-m03-reference-g05`; the fresh machine initially contained
only main at `2d7bcc9`. Main and accepted predecessors remain unchanged.
Read the current AGENTS, STATUS, G05, exact M00 v3 reference plan, fresh-session
handoff, approved decision, launch/interruption/stop evidence, CPU environment
guide, development commands, S06 numerical/physical-reference rules and S07
evidence/qualification rules. The prior agreement persists.

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

Calculation source is frozen at `419b64f7bd79199a0bf999e456f1564fc184cf75`.
Launch command/digests, installed identities, all earlier verification outputs
and a 116-file source/input manifest are in `evidence/G05_v4/`. The new attempt
is `Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v2/`.
All **46 records** are complete: eight exact historical rows and **38 new
exit-zero workers**. All 46 actual logs explicitly report energy/wavefunction
convergence. Every record passes the maintained importer; all 12 numerical
controls pass before the fixture bundle is created. The resumed session used
3.747807789 h; cumulative charged time is **4.400612052 h** including prior
launch-to-stop overhead. Maximum measured new-worker RSS is **4.670959473 GiB**.
Total cgroup high-water reaches 8 GiB because it includes cache; OOM/OOM-kill
counters remain zero. All private quantum scratch is removed. Original v1
orders, records and logs retain their exact bytes.

Both G05-T4 chemical tests pass on all 34 inputs. Largest conformer RMS/max
energy errors are 0.175964/0.286225 kcal/mol (limits 1/2), interaction RMS/max
0.338725/0.455604 and contact-minus-separated RMS/max 0.339018/0.455940 kcal/mol
(limits 0.5/1). Raw force RMS/max-vector errors are at most
0.0213261/0.0866131 eV/angstrom (limits 0.05/0.15); projected full-parent
RMS/max-vector at most 0.0145145/0.0866131. Net ligand vector error is at most
0.0397629 eV/angstrom (limit 0.05). Seven required attraction signs and all four
compressed-repulsion signs pass; every weak/separated row is retained.
The [actual report](evidence/G05_v4/RESULTS.md) links per-row CSVs, all cap and
full-parent/ligand forces, raw model captures, timing/identity tables and PNG/PDF
figures. Independent report projections agree with captured metrics to 1e-12.

Automatic approval review rejected `git push origin m03-reference-g05` because
it requires explicit source/history export authorization to that GitHub
destination. No publication is claimed; unaffected calculation/report work
completed locally. Explicit publication authorization is still required; the
completed immutable snapshot is concrete and reviewable.

## Checks

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
| Repaired full source run | 309 passed / 2 absent-quantum failures; 17 recovery cases collected before the last added concurrency parameter |
| Final prelaunch full source run | 310 passed / 2 failures, exactly the two absent-quantum chemical checks; all 18 recovery cases included |
| Intermediate full source run | 297 passed / 6 failures: two absent-quantum checks plus four recovery cases stopped by the initial overstrict total-cache guard; retained and superseded by the repaired checks |
| Strict environment validation | 9/9 environment/documentation checks passed; exact results at installed-prefix validation JSON |
| Reference interpreter/basis check | Psi4 1.10.2; both actual basis-file hashes match frozen values |
| Read-only recovery check | 46 required names, 8 reused, exactly 38 scheduled; original hashes unchanged |
| `finalize_quantum.py`, main Python with repo/src on PYTHONPATH | Exit 0; all 46 actual references, all 12 controls, unchanged 116 calculation source/input hashes and the final hashed fixture re-import passed |
| `python -m pytest tests/integration/test_chemical_reference.py -v` with capture directory | Exit 0; **2 passed in 9.74 s**, complete actual model-vs-Q results preserved |
| Final `python -m pytest -q` | Exit 0; **312 passed in 136.26 s**, all applicable CPU source checks including stable G05 assertions |
| `report_results.py`, main Python with repo/src on PYTHONPATH | Exit 0; all 34 rows, 20 contact signs, 28 capped projections, 46 job identities and 12 numerical controls saved; figure visually inspected |
| Partial numerical progress command | Initial direct import failed because src was absent from PYTHONPATH; corrected command succeeded, without changing dependencies or evaluating a model |

Numerical-control maxima: 0.0000580569 kcal/mol energy (limit 0.02),
0.0000467775 eV/angstrom force RMS (limit 0.002), 0.0002234143 eV/angstrom
maximum atom-vector force (limit 0.005). Final documentation/hash/source lineage
verification is recorded with the audit snapshot.

## Audit handoff and remaining scope

All assigned calculations/checks/reports are complete. See the
[audit handoff](evidence/G05_v4/AUDIT_HANDOFF.md) and its immutable source/data
snapshot metadata. An independent full-G05 reviewer should inspect all eight
stable gate assertions plus the recovery and actual-reference evidence; no
reviewer decision is supplied here. The user will choose the audit model and
procedure. Do not dispatch Astra/high or proceed to G06/G07 without that new
instruction. Model qualification metadata is unchanged, and no gate acceptance
or protein/periodic/GPU/electrostatic/ABFE/RBFE qualification is claimed.
