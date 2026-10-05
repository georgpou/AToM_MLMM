# G10 multistate runtime design — v3 independent audit

**Reviewed worker:** [G10 v3 worker](Gate_10_v3_worker.md), `gpt-6-luna / max`.\
**Branch and submitted HEAD:** `g10-engine-next`, `678aa3e2db9d5f77517ad8cfb278ac8a4df7032d`.\
**Design content HEAD:** `179c3035c6b70293811b6dd6e24319fd9ac932db`; the later worker-log commit is report-only.\
**Base:** `3952a9b36a92e37f0f98fdf3981c9320368a18b3`; accepted ancestor `2c02cc2713924140a82aefda37fd5885747e5837`.\
**Actual reviewer:** `gpt-6.1-sol / max`, standalone `/root/g10_design_audit`. The orchestrator confirmed the exact accepted spawn arguments; separate build/version metadata is not exposed. No reviewer subagents were spawned.\
**Finished UTC:** 2026-10-05T21:26:59+00:00.\
**Verdict:** **GREEN / accepted_for_scope — standalone design only.** No material design finding or required design repair remains.

This review accepts the [proposed amendment](../../docs/project-0/specs/g10-multistate-runtime-amendment.md)
and [implementation plan](evidence/G10_v3/implementation-plan.md) as the prerequisite
for a separate G10-T2/T3 implementation batch. It does not accept an implemented
multistate controller, its future tests or pilots, complete G10/M05, or any new
scientific capability. The reviewed specification, plan, worker report and
production source were not repaired during this review.

## Evidence and commands

All commands ran in `/workspace/AToM_MLMM-g10`. Scientific Python shells used
`source /workspace/m05-cpu-setup-v2/activate.sh` and
`export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. New calculations were
deterministic, serial, negligible-memory checks; no OpenMM Context, model load,
integration, molecular simulation, QM, GPU, production or HPC job was started.

| Command or inspection | Result and evidence |
|---|---|
| `git rev-parse HEAD`; `git branch --show-current`; `git merge-base --is-ancestor 2c02cc2713924140a82aefda37fd5885747e5837 HEAD` | Exact submitted HEAD and child branch confirmed; accepted ancestor check exited 0. |
| `git diff --name-status 3952a9b36a92e37f0f98fdf3981c9320368a18b3 678aa3e2db9d5f77517ad8cfb278ac8a4df7032d` | Only the specification, implementation plan, worker log and reporting updates in STATUS changed. |
| `git diff --quiet 3952a9b36a92e37f0f98fdf3981c9320368a18b3 678aa3e2db9d5f77517ad8cfb278ac8a4df7032d -- src tests fixtures environment models` | Exit 0. Protected source, tests, scientific fixtures, locks and model bytes are unchanged. All other tracked evidence/ledger paths also lie outside the complete four-file change set. |
| Compact-diff byte comparison with `git diff BASE HEAD` | Exact equality; `/workspace/g10-design-review.diff` SHA-256 `045ffdfb0ee8d09a7a52ba8de00d8b48a81b494f39636b4938f949d595991726`. Its content was inspected alongside the full changed documents. |
| Numbered source/contract reads using `nl`, `sed` and `rg` | AGENTS, current handoff, G10-T2/T3 and stable assertions, relevant S05 raw/reduced energies and S07 observables/restart, accepted M05 amendment, and retained exchange/journal/workflow/persistence/adapter contracts reviewed. No unrelated historical audit was reopened. |
| `python Worker_Log/Milestone_05/evidence/G10_v3_independent/design_probe.py` | Exit 0. [Independent probe](evidence/G10_v3_independent/design_probe.py) and [complete result](evidence/G10_v3_independent/design-probe.json): protected-tree/source checks, both fixture manifests, exact finite permutation kernels, units/sign/threshold checks, and both host RNG streams. |
| `python tools/check_docs.py --self-test` | Exit 0; 0 errors, 210 Markdown files, 1,423 local links and all eight self-tests passed; [documentation output](evidence/G10_v3_independent/docs-check.log). |
| `git diff --check` and staged report-only scope check | Exit 0; clean whitespace and only audit/evidence/STATUS changes. |

The provided retained-engine baseline was inspected, not rerun: **31 passed,
zero skips, 115.64 s**, from `/workspace/g10-start-baseline.log`, SHA-256
`7ba7622aac12e8047c32c9578647d22c56c6a796553195611330c5c889039162`.
The provided unchanged-lock setup validation has **9/9 exit-zero checks** at
`2026-10-05T20:54:57.844982+00:00`, from
`/workspace/m05-cpu-setup-v2/latest-validation.json`, SHA-256
`5b9e70f8014ac7d29818aa0206366497ec6513400578e2f75b2b34a5309f66a3`.
Their names, results and hashes are preserved in the independent JSON. These
are inherited retained-engine/environment evidence, not new multistate results.
An exploratory `inspect.getsource` call on NumPy's Cython random alias exited 1
with `TypeError`; corrected module inspection and the deterministic RNG probe
established the actual aliases without relying on nonexistent Python source.

## Applicable coding and design assertions

Every GREEN in this section concerns the submitted design requirements and their
implementability against retained contracts. Planned pytest nodes remain unrun.

| ID and assertion | Decision | Reproducible evidence and location |
|---|---|---|
| C1 — Additive public API, strict admission and bounded state/pair selection | **GREEN — design** | Amendment lines 20–78 and plan Task 1: distinct run/resume APIs, inert reader, 3–8 distinct sealed schedule IDs, integer in-range nonself pairs, no repeated undirected edge, connected coverage, at most 28 attempts/eight contexts, fixed 300 K Reference double/CPU NVT. Types and numerical limits must be validated before execution; malformed and unsupported inputs have planned loader-spy rejection tests. Existing `workflow._integer` rejects booleans and invalid integer ranges (lines 42–45). |
| C2 — Mode/version, source and executable-load ordering | **GREEN — design** | Amendment lines 66–78 and 231–270; plan Task 1. Pair and multistate modes cannot resume each other. Hashes, typed inert bundle/schedule information and all histories precede trusted System/model loading. Exact recursive `.py` inventory set equality precedes per-file digest comparisons. Retained export already copies the full inventory (`adapters/atom.py` lines 263–288); the proposal explicitly closes the current listed-path-only check (`exchange.py` lines 24–37). The independent current inventory contains 38 files. Frozen older workers require their exact original checkout. |
| C3 — Stable walkers and live full-permutation resolution | **GREEN — design** | Amendment lines 80–115; plan Task 2. One fixed worker per walker; coordinates/velocities/integrator remain attached to it. The declared state-index pair is resolved against the current inverse permutation immediately before every call. Independent example resolves workers `(0,1)` then `(0,2)` and yields `[0,1,2] → [1,0,2] → [2,0,1]`. |
| C4 — Exactly one integration/capture per walker and immutable sample-time state | **GREEN — design** | Amendment lines 90–108 and 151–162; plan Tasks 2/3. Stage each successful sample/State/checkpoint before the next worker integrates. Sweep decisions use fixed boundary coordinates; there is no integration between pairs. Sample `state_id` remains its capture-time assignment; per-attempt before/after and final full assignments are separate. This fits `EvaluationRecords` and S07 raw-observable semantics. |
| C5 — Complete per-attempt journal and recursive all-worker commit | **GREEN — design** | Amendment lines 164–207; plan Task 3. Before-call attempt record, evaluated/decision/refreshed phases and full history are durable before the next pair. Decision/history writes complete before adapter refresh continues. Every staged sample, final report, final worker State/checkpoint, permutation and both RNG documents is recursively hash-bound and fsynced. A single directory rename publishes one complete boundary. The retained flat two-worker `seal/verify` (journal lines 34–57) requires the explicitly planned recursive extension; it is not claimed sufficient unchanged. |
| C6 — Default pending rejection, explicit whole-boundary replay and unique records | **GREEN — design** | Amendment lines 209–229 and 263–270; plan Task 3. Default rejection preserves pending bytes. Explicit opt-in archives the complete failure tree, hashes, attempted phases and primary/secondary errors, then restores every preceding committed checkpoint, the full permutation and both host streams. Replays recreate deterministic `(run,boundary,walker)` IDs; incomplete samples never enter derived analysis. Complete committed prefix, strict sequences and linked manifests prevent duplicated or silently lost committed records. |
| C7 — Local ownership and postrename authority | **GREEN — design** | Amendment lines 166, 188–194, 223–229 and 269–270; plan Task 3. Nonblocking exclusive controller lock; local same-filesystem rename is the commit point. A later parent fsync or reporting failure cannot roll it back. Resume verifies the published boundary and rebuilds derived outputs. Mounted durable storage remains export-only. Retained lock and rename contracts are in `exchange_journal.py` lines 24–31 and `exchange.py` lines 73–78. |
| C8 — Integrity versus fresh checkpoint validation | **GREEN — design** | Amendment lines 233–268; plan Tasks 1/3. Inert shapes/types, identities, unit/raw-total arithmetic and stored total-to-reduced matrix arithmetic are checked before executable loading. Physical freshness is separately checked after restoring every latest committed context, comparing fresh raw/full energies, parameters and coordinate identity to final-state reports/portable State before any integration. A rehashed alternate checkpoint is a specifically planned negative control; un-rehashed tamper and mode/source/history failures use a pre-load spy. |

## Required fault and closure coverage

The following coverage is **GREEN as a design/test requirement**, not an executed
fault-test result. Implementation review must inspect the actual injections and
their assertions, rather than accept test names or copied expected values.

| Required challenge | Submitted design/plan coverage and implementation closure check |
|---|---|
| Partial integration after worker 0, during worker 1 | Amendment lines 225–229, 281–287; plan Task 3 Step 1. Verify durable worker-0 sample/State/checkpoint, all available worker failure captures, unchanged committed reports, byte-preserving default rejection and exact whole-boundary replay from one shared starting checkpoint. |
| First and later pair evaluation/decision/refresh persistence | Amendment lines 171–180, 201–207, 281–287; plan Task 3 Steps 3/7. Preserve the available phase/history prefix and full resolved-worker provenance; absent decision is never rejection. Assert callback failure stops the sweep. |
| Capture/checkpoint, seal and rename before publication | Amendment lines 90–94, 182–190, 281–287; plan Task 3 Step 3. Preserve all available staging/failure evidence and confirm no committed boundary appears. |
| Parent fsync after rename and derived-report failure | Amendment lines 223–229, 284–287; plan Task 3 Step 3. Confirm the complete published directory remains authoritative, hash verification succeeds on resume and derived outputs rebuild without sample duplication. |
| Archive secondary failures and all-worker capture without reevaluation | Amendment lines 209–215, 285–287; plan Task 3 Steps 1/7. Inject archive failures, retain the original exception and secondary diagnostics, attempt every available worker/artifact independently, and use an energy/force reentry spy. Retained `_archive_failure` already supports independent cached-State/checkpoint/map captures (`workflow.py` lines 270–325). |
| Permutation/sample/RNG/phase/checkpoint tamper, ownership/mode/source rejection | Amendment lines 231–270, 288–292; plan Task 1 and Task 3 Step 5. Verify correct loader ordering, malformed/repeated/missing histories, both mode directions, missing source module and changed digest, concurrent controller rejection, and fresh restored-context rejection of a hash-consistent stale-energy checkpoint before `integrator.step`. |

Successful implementation closure additionally requires unchanged pair regressions,
the combined full CPU suite on one source snapshot, actual counts/skips/timing,
and both bounded solvated pilots. These requirements remain outstanding.

## Applicable physics and chemistry assertions

| ID and assertion | Decision | Evidence and location |
|---|---|---|
| P1 — One production decision/evaluation path | **GREEN — design** | Amendment lines 12–18, 95–100 and 119–149; plan Task 2. The scheduler calls only `adapters.atom.attempt_pair_exchange` for pair decisions. Retained adapter lines 421–480 require two actual compatible `WorkerRun` objects, evaluate all four full context potentials, restore predecision assignments, invoke pinned AToM 8.5.0b0 `pairwise_metropolis_sampling`, and refresh the resulting states. No copied production Hamiltonian or Metropolis routine is proposed. |
| P2 — Hamiltonian, outside terms and independent expectations | **GREEN — design** | S05 defines `U_k = K + Phi_k(u0,u1)` and `v_k=U_k/(RT)`. Amendment lines 119–156 and 274–279; plan Task 2 Step 3 requires both independent nonlinear analytic/outside expectations and fresh actual-context comparisons for every four-entry matrix, forced acceptance/rejection and parameter refresh. The admitted outside static anchor is state-independent. A new state-dependent outside Hamiltonian is explicitly excluded. Comparing matrix entries is essential because this outside contribution cancels from the exponent even when incorrectly omitted. |
| P3 — Complete chemistry/groups/maps/caps and force ownership preserved | **GREEN — design** | Amendment lines 56–64, 151–156 and 304–313; plan global constraints. Same sealed physical/alchemical identity, fixed ML membership, complete ligands, both-map geometry guards, units, cap construction and full real forces on MM atoms/cap parents are retained. Retained `AtmEvaluator` checks system/routing ownership and fixed full-particle maps, then extracts total real forces and distinct raw/outside/total energies. Protected source/fixture/lock/model diff is empty; no new chemistry or supported embedding/ensemble is claimed. |
| P4 — Exact existing shared-runner pilot inputs and bounded resources | **GREEN — design** | Plan Task 4 uses `run_configuration`, three workers, two boundaries and one step; maximum design pilot bounds are three workers/four boundaries/two steps. Independent inert manifests confirm existing v2 ABFE: 224 atoms, complete neutral six-atom methanol; unequal RBFE: 233 atoms, complete neutral six-atom methanol and nine-atom acetamide; both have 64 waters, 300 K and the existing outside anchor. Bounded preparation-count overrides are execution settings, preserving the exact scientific fixture/force-field/Hamiltonian bytes. Pilots are planned, not run or chemically qualified. |

## Applicable mathematical assertions

| ID and assertion | Decision | Independent evidence and limits |
|---|---|---|
| M1 — Units and four-entry matrix | **GREEN — design/math** | `beta = 1/(0.00831446261815324 * 300) = 0.4009078501424201 mol/kJ`; multiplying each complete kJ/mol total gives dimensionless entries. Amendment lines 134–147 matches retained adapter lines 447–450 and S05. The probe includes nonzero state-independent outside terms in every entry and verifies their cancellation only in the exponent. |
| M2 — Exponent sign and acceptance probability | **GREEN — design/math** | `delta = v_i(y)+v_j(x)-v_i(x)-v_j(y)`, `P=min(1,exp(-delta))`, equals the swapped-to-current Boltzmann ratio. The unchanged actual pinned scalar routine accepts a forced draw below `exp(-0.7)`, rejects one above it, and accepts a negative exponent without a NumPy draw. This is a scalar mathematical probe, not a substitute for planned actual-context multistate tests. |
| M3 — State-pair permutation algebra | **GREEN — design/math** | Exact independent overlap example and full before/after permutations match amendment lines 110–115 and plan Task 2 Step 1. Resolve each pair from the live permutation; stale original walker resolution gives the wrong second call. |
| M4 — Ordered-kernel stationarity and statistical restraint | **GREEN — design/math** | Each symmetric fixed state-pair proposal is an involution, with Metropolis ratio for the same joint Boltzmann target. Each kernel preserves that target, so their ordered composition also preserves it. The six-permutation rational probe verifies both individual 6×6 kernels' detailed balance and all six stationary probabilities exactly, yet finds ten whole-sweep detailed-balance violations; one flux is `5/124` versus reverse `0`. A flat-energy connected triangle also leaves one walker fixed at boundary endpoints. Connectivity alone does not qualify irreducibility or mixing. Amendment lines 157–162 expressly limits the claim to valid pair-kernel composition and withholds whole-sweep reversibility, mixing/convergence/uncertainty/affinity/accuracy; finite-step MD equilibrium is not newly proven. |
| M5 — Both host RNG streams and deterministic continuation | **GREEN — design/math** | The actual upstream aliases are Python `random.choice` and NumPy legacy `_random`. Retained helpers (`exchange.py` lines 40–63) preserve complete Python/legacy NumPy state, including Gaussian caches, isolate caller globals and restore controller streams. Independent JSON roundtrip reproduces cached normal variates, nine paired draws, both post-streams and unchanged caller states. Amendment lines 166–169, 186–218 and plan Tasks 2/3 require both streams plus all OpenMM checkpoints and full permutation at every boundary. Whole-worker checkpoint replay remains a future implementation assertion, restricted to the identical admitted software/hardware profile; portable State does not promise RNG/trajectory identity. |

## Findings, decision and handoff

No material design findings or required design repairs were identified. The
applicable coding/design, protected physics/chemistry and mathematical assertions
above are explicitly **GREEN for this standalone proposal**. The next serial
Luna/max worker may implement the bounded plan; that finished combined runtime
batch needs its own independent Sol 6.1/max audit before implementation acceptance.
STATUS may record only this completed design acceptance and its canonical audit.

Multistate runtime correctness, fault/restart execution, pilots, full G10/M05,
GPU, equilibrium/convergence, affinity, chemical accuracy and exchanging-walker
uncertainty remain **unqualified or pending**. Existing G07 physical blockers
remain: seven sensitivity exceedances, measured pilot force failures and 29
missing references. All 46 accepted G05 records and the charged QM ledger
`2325.6446500519996 / 86400 s` remain unchanged; the remaining-job resource screen
remains false. This review adds no quantum budget, physical acceptance or
permission for production/HPC continuation. No source, tests, fixture, tolerance,
model, package lock, prior worker log, reference record or prior decision was
modified; only this audit, its small evidence and report-only STATUS are committed.
