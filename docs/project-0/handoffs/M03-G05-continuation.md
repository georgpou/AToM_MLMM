# M03 G05 continuation: paused references and pending full audit

The user requested a stop and fresh-session handoff on 2026-10-03.
[Fresh-session handoff](M03-G05-fresh-session.md) is now the starting point.
Reuse this same branch. Eight exact energy/gradient records are saved;
38 calculations remain. No old quantum process was visible at checkpoint.

Start from child `m03-reference-g05`, descended from exact accepted published
G04 handoff `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`. Preserve main,
`m00-audit-m01-development`, `m02-analytic-atm` and `m03-link-boundary`.
Commit/push only the child. STATUS and the new G00/M00/G05 worker/audit records
are authoritative; no full G05 acceptance has been claimed.

## Actual completed scope

Pinned MACE-OFF23-small SHA256
`165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`,
CPU float64, total `energy`, actual ASE CODATA2014 unit factors. Trusted
hash/authorization/licence checks precede weight loading; default Torch policy
remains intact. The deterministic ASE facade stores an inert asset recipe and
resolves bundled weights in the current installation. Native direct graph and
autograd oracle, independent raw cap Jacobian/full-real force oracle, actual
OpenMM adapter, nonidentity map, transforms, component FD/faults, joint/disjoint
graphs, domain/counterfactual scans, moved offline serialization and nested ATM
are implemented. Six software stable assertions pass; candidate metadata is
explicitly unqualified. Definitions, model, locks and inherited MM ledger are
unchanged; there is no manual cap-force projection in production.

Current recorded full suite: **292 passed, 2 failed**; both failures are
G05-T4's missing actual quantum references before any model comparison runs.
Inherited G02/G03/admission/G04 results are **78/38/74/24**; strict environment
**9/9**, upstream **1**, analytic **272 passes / 22 deselected**, docs zero errors/eight self-tests. Larger arrays,
including diagnostic extreme inputs and every failed attempt, are under
[G05 evidence](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_03/evidence/G05_v1/README.md).

The software-reviewed snapshot is `a7768e375476667139db374dc0091999263a37de`.
The first software reviewer was interrupted for the user's quota pause after
saving full/analytic/environment captures; it supplied no verdict. On 2026-10-03
the user resumed the assignment. All 269 source/input hashes and all 105 separate
reference-package lock entries were reverified without scientific reruns.
A new actual Astra/high/fresh-context reviewer examined that same immutable
software snapshot and accepts G00-T2 plus six G05 software assertions in the
[v1 audit](../../../Worker_Log/Milestone_03/Gate_05_v1_audit.md). Its prepared-T4 importer finding
has been repaired in the child after six intended RED rejection failures and
ten GREEN integrity/metric checks. The original proposal and all chemical
inputs/settings/limits remain unchanged. The [v2 worker](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_03/Gate_05_v2_worker.md)
and [270-file repair manifest](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_03/evidence/G05_v2/source-input-manifest.json)
identify this code-only repair. The [v2 audit](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_03/Gate_05_v2_audit.md)
independently closes R1 and accepts prepared-loading readiness on exact
`3124c6d275bf19a32ce364dfdb83b11115828ac5`; full chemical/G05 acceptance
remains pending. See
[resume state](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_03/evidence/G05_resume_20261003/resume-state.json).

## Frozen M00 decision

[V3 exact proposal](../reference/M00-neutral-reference-plan-v3.md) at
`a825f5f1c2d8cf4146133c2049ef1c4eca550e93` is independently accepted for
design by actual **gpt-6-astra/high/fresh context**, conditional on explicit
user agreement. [V3 audit](../../../Worker_Log/Milestone_00/Milestone_00_v3_audit.md):
965 applicable structure/geometry and 131 provenance checks. Preserve V2's
changes_required audit and the score-free 120-degree retained-peptide repair.
G05 raw coordinates and all chemical limits remain unchanged from V2.

The proposal has 34 neutral singlet CHNO targets (capped ethanol/butane,
complete methanol/acetamide and four contact families), ten monomer rotation
controls and two fine-grid confirmations. Quantum method is restricted
omega-B97M-D3(BJ)/def2-TZVPPD, exact settings/hash lock under
`fixtures/chemical_reference_v3/`. Proposed budget 12 wall-hours / 2 threads / 5 GiB.
Per-family energy RMS/max limits 1/2 kcal/mol conformers and 0.5/1 kcal/mol contacts;
per-structure force RMS 0.05 / maximum atom vector 0.15 eV/angstrom, net ligand maximum 0.05 eV/angstrom.
Never alter limits, select samples or replace physics after seeing results.
All 20 future G07 joint rows/50 cut descriptions are frozen; prepared actual
GAFF 2.2.20 / AM1-BCC charges/XML/retained ledger must be frozen before G07-T4,
which remains later work.

**Explicit user agreement was received on 2026-10-03** after the full scientific
plan, limits and resource cap were presented. The new
[approved decision](../../../Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json)
records the actual statement and exact reviewed manifest/audit digests. The
historical pending record remains false and unchanged. No target Q calculation
or comparison preceded agreement. The user requests a fresh-session handoff
using this same child branch directly and has now explicitly requested a stop
before chemical completion. Do not create another branch merely to restart
context.

## Remaining authorized steps

1. Explicit agreement is recorded; preserve both actual approved and historical
   pending records, the exact reviewed commit and manifest/audit digests. The
   approved quantum-only batch is paused in
   `Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v1/`
   with launch metadata in `launch-v1.json`. Preserve eight saved records and
   all logs. Transport recovery failed; no coordinator manifest was written.
   The cause is unknown. Do not restart completed work blindly.
   Revise/re-review any scientific changes before comparisons.
2. Use the separate reference environment. The current working prefix is
   `/workspace/atom-mlmm-reference-pilot-v2/env`; reproduce it from the SHA lock
   if unavailable. Main environment is `/workspace/atom-mlmm-g05-v2/activate.sh`;
   unchanged installer is available for fresh environments. Amber stays separate.
3. The current `tools/generate_neutral_quantum.py` has no resume mode and writes
   progress only at completion. Add/test/review validated reuse and durable
   progress before launching the remaining 38 jobs. Check the 8-GiB container
   RAM headroom: its lifetime peak reached the cap without an OOM-kill event.
   Storage currently has about 14.28 GiB free. Preserve frozen settings and the
   approved total budget, including time already spent. Freeze records/manifest
   under `fixtures/chemical_reference_v3/quantum/` only with complete provenance
   and all controls; no quantum runtime enters the core package.
4. Run both `tests/integration/test_chemical_reference.py` stable checks. They
   enforce fine-grid/rotation controls before scoring, same-composition zeros,
   interaction/contact-minus-separated errors, raw/projected parent and ligand
   force metrics, signs and unchanged limits. Preserve every failing row.
   The metric/unit tests are software checks, not quantum substitutes. The
   generation and comparison path has not yet run on target data.
5. Resolve missing/failed reference data honestly. Any exceeded limit requires
   justified narrowed scope or reviewed physical change; do not hide failures.
6. Run all applicable suites/checks and obtain a new **complete exact-snapshot
   gpt-6-astra/high/fresh** G05 review (reviewer writes no implementation).
   A scoped software review cannot supply final G05 acceptance. Update only
   actual reviewed scope, publish the child and stop at accepted G05.

G06/G07 follow; M03 closes at G07. No periodic, GPU, protein ABFE/RBFE,
electrostatic embedding or complete-workflow qualification follows here.
