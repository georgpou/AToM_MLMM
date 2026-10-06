# G10 multistate Tasks 1–4 — v5 independent combined audit

**Verdict: RED / changes_required.** Seven material findings block acceptance of
the combined implementation. Numerical agreement on admitted analytic and v2
molecular records passed; it does not close the admission, restored-state or
durability findings below. There is no qualified GREEN for this batch.

**Reviewed workers:** [v4 core](Gate_10_v4_worker.md) and
[v5 pilots/combined submission](Gate_10_v5_worker.md).
**Branch:** `g10-engine-next`, `/workspace/AToM_MLMM-g10`.
**Frozen reviewed HEAD:** `edd587679aaa110ea687cca29b9e3aee70b7b6f0`.
**Combined worker submission:** `ecace38b34e15fae65508b2ee9cd2f535a1b85c4`.
**Code/result:** `a507bbddfccc1a88b8df4ab18277040889bf379c`.
**Accepted standalone design audit:** `bd44b2c93a5cba40225dba632f0277e535467be9`.
**Actual auditor:** `gpt-6.1-sol / max`, root-dispatched sole independent auditor
`/root/g10_combined_audit_v5`; the dispatch identifies model/effort, and separate
build metadata is not exposed. No auditor subagents were spawned.
**Review completed UTC:** 2026-10-06T09:13:31+00:00; report-only verification and
commit follow the scientific review. Their exact outcomes are recorded in the
[independent evidence](evidence/G10_v5_independent/README.md) and final handoff.

The user resumed the saved pre-audit pause. The historical
[pause packet](../../docs/project-0/handoffs/G10-MULTISTATE-AUDIT-READY.md) remains
an immutable record of that earlier state; STATUS is the live summary. This
audit covers the entire design-to-worker Tasks 1–4 increment, including both
pilot source repairs. It does not reopen unrelated accepted reviews or accept
full G10/M05, molecular accuracy, protein physics, GPU/HPC, production or
exchanging-walker statistics. Source, tests, specifications, worker reports and
scientific artifacts stayed frozen throughout review.

## Snapshot, contracts and independent evidence

I read AGENTS, STATUS, the current continuation and audit-ready handoffs,
DEVELOPMENT/CPU guides, G10-T2/T3 and stable assertions, relevant S05/S07/S06
contracts, the reviewed multistate amendment, v3 worker/design audit/plan, both
original worker instructions, v4/v5 reports, focused fault/oracle tests,
diagnostics and retained adapter/workflow/persistence paths. The exact compact
diff was byte-compared to Git and its production/test/usage content reviewed.
Only `exchange.py` and `exchange_journal.py` changed in production.

[Independent identity results](evidence/G10_v5_independent/identity-results.json)
verify all 38 recursive Python source paths/digests, all 24 submitted manifest
entries at **ecace38**, source/test/fixture/environment/model/usage equality
between the pause HEAD and submission, and unchanged specifications, fixtures,
locks/models and M03 records since the accepted design. The decompressed
151,308-byte combined diff is exactly SHA-256
`9fc744b7d305dbaf3797e9bd28e2664b2550a00fbf99e56c1ace6067bffe9bd6`.
The two production hashes are:

| File | SHA-256 |
| --- | --- |
| `src/atm_mlmm/exchange.py` | `317fca331def3ef32be709f3ad77f63cd888788e3f335a8cf5ad45df67e1aec9` |
| `src/atm_mlmm/exchange_journal.py` | `29c6aaa3aef92cdb326b39fce9264e5a018f1db9ea3af414e4bdd50d8794a9a8` |

All 20 frozen prepared/controller bundles from the five attempts/two cases were
independently checked against their original complete manifests and 38-file
source inventories, including the retained model/lock assets. The four failed
gzip traces are byte-identical to their local uncompressed originals. Earlier
bundles were inspected inertly and never loaded under substituted source.
Their failures remain failures: focused 2/83.53 s, repaired 2/94.99 s, repair2
2/129.37 s and final-focused 2/162.39 s. These are retained worker outcomes,
not newly executed trials.

Every scientific shell sourced `/workspace/m05-cpu-setup-v2/activate.sh` and
exported `OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. Jobs were serial on the
two-CPU/8-GiB machine. Actual profile: Python 3.11.16, OpenMM 8.6.1 Reference
double, atom-openmm 8.5.0b0, MACE 0.3.16 CPU float64, NumPy 2.4.6, Torch 2.8.0,
distribution identity
`1865672db5d5a8db6c4d6abc4035d2eb0d70339cb85c1958f85eac7e7800fbf1`.
No packages, weights, fixtures, scientific definitions or tolerances were
changed, and no QM/GPU/HPC/production job ran.

| Fresh independent command/control | Actual result |
| --- | --- |
| `python .../identity_probe.py` | Exit 0; 38 source files, 24 submitted hashes, 20 frozen worker bundles and four raw failed logs verified. |
| `python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py -k 'multistate or partial_integration' -q` | Exit 0; **42 passed, 0 skipped, 20 deselected, 74.87 s**. Tests were inspected for actual injections/assertions. |
| Two unchanged pair nodes: persistent identical-prefix continuation and actual reduced-energy acceptance | Exit 0; **5 passed, 0 skipped, 7.31 s**. This independently checks preserved pair behavior. |
| `python .../analytic_admission_probe.py` | Complete saved result; exit 1 for **seven observed contract violations among nine rejection challenges**. Both independent analytic numerical cases and the exact stationarity/RNG control passed. |
| `python .../transaction_restore_probe.py` | Complete saved result; exit 1 for **five observed violating cases**: restored timeline, restored geometry, actual postrename fsync, derived writing and syscall-order coverage. |
| `python .../molecular_probe.py` | Exit 0; both exact v2 cases, 36 fresh schedule evaluations, eight complete attempted pair matrices, full forces, reconstruction, both snapshot identities, prefix hashes and stale-coordinate rejection passed. **Zero new molecular integration steps/preparation frames.** |
| `python .../additional_inert_probe.py` | Complete saved result; exit 1 for **five observed contract violations**. Valid 8-state/28-edge selection and 15 invalid public selections passed without context construction. |

There are **47 fresh pytest passes**, no skips, plus the separately recorded
independent controls and **17 violating characterization cases** grouped into
the seven findings below. The nonzero characterization exits preserve real
unexpected admissions/continuations; they are not dependency failures or hidden
test-harness errors. All raw commands, exit statuses, completion timestamps,
scripts and complete results are in the evidence directory.

The worker's hash-verified **577-pass/0-skip/913.26-s** full CPU suite,
**74-pass/0-skip/171.69-s** required compatibility suite and
**2-pass/0-skip/156.56-s** complete molecular pilot invocation are retained
evidence on the reviewed source. I did not repeat the full suite. Passing those
tests does not cover the independent gaps found here.

## Findings and smallest repair requirements

### G10-v5-R1 — Important: incomplete inert type, limit and identity admission

`exchange_journal.py` metadata/RNG/inverse/sample/report validators accept
malformed but correctly resealed declarations, allowing trusted worker loading.
The complete reproducer and loader-spy results are in
[analytic-admission-results](evidence/G10_v5_independent/analytic-admission-results.json)
and [additional-inert-results](evidence/G10_v5_independent/additional-inert-results.json).
The admitted cases are:

- `steps_per_boundary=1000000`, which the run API rejects at its exclusive limit;
- `integrator_seed_base=2147483647`, so subsequent worker seeds overflow the
  adapter's signed-positive bound; validation must cover every intended worker;
- Boolean `host_rng_seed`, Boolean inverse entries and Boolean sample sequences;
- a Python Gaussian cache containing a string or overflowed JSON `1e309`;
  `random.Random.setstate` accepts that cache, so it is not a finite/type oracle;
- a conflicting `record.state_to_walker_final`, despite the separate inverse
  file remaining correct;
- a final report with Boolean step and string time;
- sample `physical_identity`/`transfer_identity` replaced by zero hashes.

All ten cases pass the inert reader and reach the loader spy. Source admission
itself correctly rejects changed/missing listed modules, and invalid force
components/permutations correctly reject; those positives do not close these
fields. Relevant locations are `exchange_journal.py` lines 172–215, 343–384,
426–455, 476–495 and 533–564, and `exchange.py` lines 702–713.

**Smallest repair:** validate the complete declared metadata and all stored
identity/index/sequence/step/time fields before any executable load; mirror the
public limits on resume; require `seed_base + N - 1 < 2**31`; explicitly validate
the full Python RNG structure and finite optional Gaussian cache; bind every
stored inverse and sample physical/transfer identity to the sealed records.
Use exact integer checks that reject booleans. Apply the seed-range admission
before first load/output initialization as well as on resume.

**Regression requirement:** each saved challenge rejects inertly with a loader
spy remaining uncalled and no attempt/pending evidence mutation. Add public-run
coverage for a prepared seed that cannot generate all N valid worker seeds;
retain valid Gaussian-cache roundtrip and valid 3/8-state limit controls.

### G10-v5-R2 — Important: restored checkpoint step/time are unchecked

`_fresh_multistate_check` compares coordinates, velocities, box, parameters and
energies but never compares context/portable-State step/time to the saved report
and captured sample. The inert validator likewise leaves the final report clock
unchecked. The independent probe changes only worker 0's checkpoint/portable
clock to step **99**, time **9.99 ps**, retaining identical Snapshot,
positions/velocities, energies and forces. The reader admits it and resume
completes, committing step **100** at **9.9905 ps** after a previous sample at
step **1**, **0.0005 ps**. The declared increment is one; the recorded increment
becomes 99.

[Transaction results](evidence/G10_v5_independent/transaction-restore-results.json)
retain both clocks, snapshots and manifest hashes. Locations:
`exchange.py` lines 411–482; `exchange_journal.py` lines 492–495, 533–564.

**Smallest repair:** validate finite/types and internal sample/final-report clock
agreement inertly, then compare restored checkpoint and portable-State step/time
with their saved boundary values before evaluation/integration. Validate the
per-walker boundary step increments against `steps_per_boundary` and the
admitted timestep, preserving any explicitly justified time roundoff bound.

**Regression requirement:** the resealed clock-only checkpoint rejects before
pending creation or integration, including a portable/checkpoint clock mismatch
and a backward or skipped sample clock. Identical-prefix continuation must retain
the existing exact checkpoint/RNG/sample behavior.

### G10-v5-R3 — Important: geometry admission checks the prepared state before restore

`_execute_multistate` calls `_geometry(worker, _snapshot(worker), ...)` **before**
`_fresh_multistate_check` restores the latest checkpoint. The restored coordinates
are then evaluated and integrated before the next geometry check. This violates
the retained both-map/domain safeguards before dynamics.

The independent analytic reproducer moves the complete one-atom environmental
molecule onto ligand atom `a1`; maps, ligands, membership and Hamiltonian remain
unchanged. The actual unchanged guard rejects the restored map0 Bondi ratio
**0 < 0.65**. All affected sample/final and pair-matrix numerical records were
freshly recomputed and resealed, isolating geometry from stale-energy rejection.
Resume instead checks three prepared step-0 geometries, evaluates all three
restored contexts at step 1, advances worker 0 to **step 2**, creates pending
work, and only then rejects ratio **3.39283705e-05**. Its failure archive records
the already advanced worker. Evidence: the transaction results; locations
`exchange.py` lines 418–457 and 530–551.

**Smallest repair:** run the existing full `_geometry` guard on every restored
actual Snapshot after restore/coordinate provenance admission and before energy
evaluation or integration. Keep both mapped molecular/cap/clearance checks and
their unchanged thresholds; do not add or weaken physics.

**Regression requirement:** resealed, energy-consistent invalid map0 and map1
coordinates reject before evaluation, pending creation and integration, with
all committed artifacts unchanged. The valid molecular restart/comparator and
existing geometry tests must continue to pass.

### G10-v5-R4 — Important: refreshed energies are not bound to the evaluated matrix

`_validate_refreshed` checks only two finite energies and final state labels.
At fixed boundary coordinates each refreshed total must equal the appropriate
already evaluated complete raw total. Adding **123 kJ/mol** to attempt 0's first
refreshed energy, resealing, and leaving all evaluated/decision/history/final
records intact passes the inert reader and reaches trusted loading. The latest
fresh checkpoint comparison never checks this earlier attempt field.
Evidence: `refreshed-energy-arithmetic` in the analytic admission results;
location `exchange_journal.py` lines 238–247 and 518–524.

**Smallest repair:** after reconstructing the accepted/rejected assignment,
compare both refreshed energies to the corresponding `raw_energies` full totals
from that same evaluated 2-by-2 matrix, under the existing `1e-8 kJ/mol` bound.
Retain raw/outside/total naming and the one pinned acceptance implementation.

**Regression requirement:** both accepted and rejected paths reject a changed
finite refreshed total before loading. Correct nonlinear/outside matrices and
actual-context refresh values continue to pass without tolerance changes.

### G10-v5-R5 — Important: postrename/report failures lose required failure evidence

The boundary exception handler archives only while `pending.exists()`.
Once rename has published the boundary, an actual parent-fsync exception skips
all primary/worker failure records. Derived-record writing occurs outside the
handler after the contexts close, so its exceptions likewise retain no run-local
failure evidence. Independent injections at the **actual postrename sync call**
and `to_json` leave two valid authoritative boundaries and an unchanged prior
prefix, but **no error record, all-worker captures or transformed map States**.
The primary Python exception propagates; it is not durably preserved in the run.
Locations: `exchange.py` lines 398–404, 633–647 and 649–672. The worker's parent
fsync test raises after its original publish function already completed its
fsync; it tests commit authority but not an actual failing fsync or error archive.

**Smallest repair:** retain published boundaries as authoritative and immutable,
but archive the primary error and every available cached worker State/checkpoint/
both mapped States into a unique separate failure tree after rename or derived
writing failures. Keep contexts available through required failure capture or
use the committed cached artifacts without energy/force reentry. Preserve the
primary error and independent secondary diagnostics.

**Regression requirement:** real postrename parent-fsync plus records,
observations and summary-write failures retain complete available all-worker
evidence without evaluation reentry. Resume verifies/rebuilds the committed
prefix with unchanged boundary hashes and no duplicate/lost samples; secondary
archive failures do not replace the primary error.

### G10-v5-R6 — Important: source-parent and rollback-file durability are incomplete

Publication renames `run/pending` into `run/boundaries/index` and fsyncs only the
destination parent. This is a cross-directory rename: the source parent also
needs fsync to durably record removal of the pending entry. The independent
syscall trace records sealed file/directory fsyncs, rename, then only
`run/boundaries` fsync; `run` is missing. Separately,
`preserve_multistate_pending` fsyncs its new rollback marker and directories but
does not fsync the preserved failure files. The inherited cached failure helper
writes those XML/checkpoint/error files without file fsync, so the subsequent
archive rename does not complete their promised durability.

The trace in transaction results reproduces a previously unsynced failure State
and confirms no `state.xml` file fsync before rollback publication. This is a
proven syscall-order gap, **not a claimed observed power-loss/data-loss trial**.
Locations: `exchange.py` lines 398–404; `exchange_journal.py` lines 580–603;
retained `workflow._archive_failure` writes at lines 297–325.

**Smallest repair:** after commit rename fsync both source and destination
parents, treating any postrename error as an authoritative published boundary;
before rollback archive rename fsync every preserved file and nested directory,
then both parents. Preserve their bytes and hashes and the existing primary-error
policy. No filesystem/physics expansion is needed.

**Regression requirement:** traced ordering proves all preserved files are
synced before archive rename and both parents after cross-directory rename;
inject each postrename parent failure and retain authority/failure evidence.
Existing serial exact-prefix rollback/replay must still pass.

### G10-v5-R7 — Important: nested `manifest.json` files bypass recursive sealing

Both `seal_tree` and `verify_tree` exclude every file whose **basename** is
`manifest.json`, rather than only the root seal. Adding arbitrary bytes at
`attempts/0000/manifest.json` inside an existing attempt directory changes no
top-level manifest hash and is ignored by the actual inventory/expected layout.
The inert reader admits it and the loader spy runs. Its bytes can subsequently
change without any seal detecting the change. Evidence:
`nested-unsealed-manifest` in additional inert results; locations
`exchange_journal.py` lines 274–319.

**Smallest repair:** exclude only `directory / 'manifest.json'` from its own
file inventory. Every other recursive file must be hashed or rejected, and the
required multistate layout must reject this extra nested file.

**Regression requirement:** an added or modified nested `manifest.json` inside
an already expected directory rejects before loading; changing those bytes
cannot leave a supposedly verified complete boundary valid. Retain exact normal
sealing, symlink rejection and prefix replay.

## Explicit coding, physics/chemistry and mathematics decisions

| ID and applicable assertion | Decision and evidence |
| --- | --- |
| C1 — Additive bounded public API and complete argument/admission types/limits | **RED**, R1. Public state/pair limits work, including inert 8-state/28-edge control, but resumed metadata/seeds/types are incomplete. |
| C2 — Pair API, mode separation and exact recursive source identity before executable load | **GREEN for these assertions.** Source/adapter equality, 38-file inventory challenges, mode tests and five fresh pair passes. Frozen older bundles retain exact original sources. |
| C3 — Stable walkers, serial integration and live full permutation per edge | **GREEN.** Overlap example resolves workers `(0,1)` then `(0,2)`, `[0,1,2] → [1,0,2] → [2,0,1]`; inspected/fresh scheduler tests and independent analytic/molecular histories. No coordinates/velocities/integrator/walker IDs exchange. |
| C4 — Captured sample labels, unique IDs/sequences and complete step/time history | **RED**, R1/R2. Normal labels/IDs/full records and replay pass; Boolean sequences and stale checkpoint clocks remain admitted. |
| C5 — All-worker recursive hash-bound/fsynced atomic boundary | **RED**, R6/R7. Normal recursive publication and one rename exist; nested files and cross-parent/rollback durability remain incomplete. |
| C6 — Phase durability, no-mutation default pending rejection, explicit whole-boundary replay and failure preservation | **RED**, R5/R6. First/later evaluated/decision/refreshed faults, successful worker-0 staging, secondary-error preservation, no-mutation rejection and exact replay pass; postcommit failure archival/durability do not. |
| C7 — Nonblocking local controller ownership and postrename authority | **GREEN.** Fresh ownership and publication tests plus real injected fsync/derived failures preserve the authoritative prefix. This does not satisfy R5/R6. |
| C8 — Inert admission plus complete actual restored-state validation before integration | **RED**, R1/R2/R3. Hash/source/energy/coordinate safeguards pass but malformed fields, clocks and actual restored geometry are incomplete. |
| C9 — Complete internally consistent evaluated/decision/refreshed/history records | **RED**, R1/R4. Decisions/history/permutation are durably stored before refresh and ordinarily agree; duplicated inverse and refreshed-total arithmetic are incompletely bound. |
| P1 — One retained Hamiltonian/evaluation/Metropolis path | **GREEN.** Only two production scheduler/journal modules changed; every pair delegates to unchanged `adapters.atom.attempt_pair_exchange` and pinned AToM 8.5.0b0. No second production Hamiltonian or acceptance routine. |
| P2 — Fresh four-entry complete potentials, parameter refresh and outside accounting | **GREEN for actual admitted numerical evaluations.** Independent nonlinear/endpoint/outside formulas, poisoned state controls and 36 actual molecular cross-state evaluations; nonzero outside terms are included in every matrix entry. Stored-refresh validation separately fails R4. |
| P3 — Fixed complete chemistry/maps/ML/caps/full real force ownership and both-map guards before dynamics | **RED**, R3. Complete ligands, fixed ML/maps/caps, real forces including MM/cap parents and once-only force routing remain intact, but restored-domain admission occurs too late. |
| P4 — Exact shared-engine v2 molecular inputs and bounded technical pilots | **GREEN for this assertion.** 224-atom ABFE/233-atom unequal RBFE, complete methanol (6)/acetamide (9), 64 waters, exact four count overrides, three contexts, two boundaries/one step, six samples/four attempts per case. Fresh audit adds no molecular integration/preparation. |
| P5 — Protected scientific definitions, physical limits, models/locks/references and no chemistry expansion | **GREEN for preservation.** Independent protected-tree checks; no chemical-reference accuracy or protein claim is newly accepted. |
| M1 — Beta, units, independent force derivatives and raw-energy reconstruction | **GREEN.** Beta `0.4009078501424201 mol/kJ`, complete kJ/mol divided by RT, all-real nonlinear derivative weights; analytic raw errors ≤`2.842170943040401e-14`, force errors ≤`7.105427357601002e-15`; actual molecular reconstruction error ≤`5.820766091346741e-11`. |
| M2 — Exchange sign/probability and forced positive-exponent accept/reject | **GREEN.** Actual pinned adapter thresholds pass for ABFE and RBFE, using independently positive deltas and draws on opposite sides of `exp(-delta)`; exponent is `v_i(y)+v_j(x)-v_i(x)-v_j(y)`. |
| M3 — Full inverse-permutation algebra and immutable capture-time labels | **RED for complete stored consistency**, R1/C9. Executed algebra, accepted overlap and rejected/accepted parameter-refresh paths retain the correct live walkers and labels, but a conflicting stored duplicate inverse remains admitted. |
| M4 — Ordered pair-kernel stationarity and restrained statistical claims | **GREEN.** Exact six-permutation Fraction control preserves the product target for each pair and their ordered composition, while exhibiting 20 whole-sweep detailed-balance violations. No irreducibility, mixing, equilibrium of finite-step MD, convergence, affinity or exchanging-walker uncertainty is inferred. Records remain `correlated`; `binding_result=not_evaluated`. |
| M5 — Complete valid host RNG records, clocks and deterministic checkpoint replay | **RED**, R1/R2. Both valid cached-normal/draw streams, global isolation and identical-prefix all-worker checkpoint replay pass; malformed Python caches and invalid resumed clocks remain accepted. |
| M6 — Stored phase arithmetic consistent with complete energies | **RED**, R4. Matrix-to-total/beta/exponent checks work, but a contradictory finite postdecision energy is accepted. |

**Category decisions: coding RED; physics/chemistry RED for runtime guard
preservation; mathematics RED for recorded RNG/timeline/phase consistency.**
The unchanged accepted energy, force, probability and stationarity equations
need no repair. None of these category decisions qualifies MACE chemical
accuracy or changes earlier physical/reference blockers.

## Independent decision on the Task 4 comparator refinement

The original strict representation failures are real and preserved. Keeping the
exact captured Snapshot/report hash while comparing restored real positions at
absolute **`1e-15 nm`**, `rtol=0`, is a justified technical comparison refinement
for the measured OpenMM unit round trips. The original diagnosis's maximum was
`6.5052130349130266e-18 nm`; my successful fresh checks, including another context
evaluation/repositioning, measured at most **`5.551115123125783e-17 nm`** for
ABFE and **`5.204170427930421e-18 nm`** for RBFE, still below the declared bound.
These are different recorded observation windows, not a revision of the failed
trial measurement.

The allowed numeric differences are confined to that position comparison and
the already declared absolute **`1e-8 kJ/mol`** raw-energy comparisons. Both exact
sample/report coordinate hashes remain bound. Portable-State/checkpoint
positions/velocities/parameters/box remain exact; captured-sample velocities,
box, real IDs and units remain exact. The complete saved and fresh EnergyForces
field sets match, numeric total/force comparisons retain **`1e-8`**, and every
other field remains exact. Critically, saved `total.snapshot_identity` equals
its **captured Snapshot's** identity and fresh `total.snapshot_identity` equals
its **restored Snapshot's** identity; neither field is skipped. Shape/finite
guards cover the compared position/force/raw arrays and the actual Snapshot
constructor. The unvalidated clock/type fields are separately material R1/R2,
not excused by this refinement.

Both exact successful molecular records pass those checks with **zero raw-energy
and full-force discrepancy**. Complete independent mixing-formula errors are
zero; matrix/exponent/reconstruction differences reach only one binary rounding
unit, `5.820766091346741e-11`, from equivalent division/multiplication order.
The deliberately resealed **`2.000177801164682e-12 nm`** displacement remains
inertly hash-valid but rejects before any WorkerRun evaluation or pending
creation in both fresh audit challenges.

I find no material numerical/scientific-tolerance waiver in this documented
refinement. It resolves a representation mismatch under the existing physical
contract and is reviewed here as an explicit implementation variance from the
standalone exact-identity design. The whole batch remains RED because the
separate admission, geometry, clock, phase and durability obligations are not
met. This comparator decision cannot turn G07's physical failures GREEN.

## Decision and handoff

The combined Tasks 1–4 submission is **RED / changes_required**. Repair all seven
findings as one complete bounded sequential repair batch, preserve this report
and every failed artifact, run meaningful failing regressions before the fixes,
the affected/required compatibility checks and combined checks on the resulting
snapshot, then obtain one new independent Sol 6.1/max combined audit. No repair
was made or started during this audit, and no push/reset/rebase/merge occurred.

Only this independent report/evidence and accurate report-only STATUS changes
are committed. The existing 46 G05 records, seven G07 sensitivity exceedances,
pilot force failures, 29 missing references and charged QM ledger
`2325.6446500519996 / 86400 s` with false continuation screen are unchanged.
Full G10/M05, chemical accuracy, protein qualification, GPU/HPC, production,
equilibrium/mixing/convergence, affinity and uncertainty for correlated exchanging
walkers remain blocked or open. `binding_result` remains `not_evaluated`.

Report-only verification passes: documentation self-test has all eight controls
true and zero errors; working/staged diff checks pass; all 38 reviewed source
hashes and the protected source/test/specification/scientific trees remain
unchanged. The first documentation attempt found its own linked output file
missing before creation; that failed output/cause is preserved in the evidence,
and precreating the log resolves the link error. Exact verification commands,
exit statuses, completion UTC and permitted staged paths are recorded in
`completion-results.json`; the final handoff names the audit commit and clean
Git status. No scientific check was repeated to resolve this documentation error.
