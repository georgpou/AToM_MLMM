# M03 G05 continuation: reviewed plan, pending user decision and quantum data

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

Current recorded full suite: **285 passed, 2 failed**; both failures are
G05-T4's missing actual quantum references before any model comparison runs.
Inherited G02/G03/admission/G04 results are **78/38/74/24**; strict environment
**9/9**, upstream **1**, analytic **265 passes / 21 deselected**, docs zero errors/eight self-tests. Larger arrays,
including diagnostic extreme inputs and every failed attempt, are under
[G05 evidence](../../../Worker_Log/Milestone_03/evidence/G05_v1/README.md).

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

**Explicit user agreement is still pending.** The async question presents the
scientific choices/limits and budget. The actual
[decision record](../../../Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-pending.json)
has user_agreed=false; do not flip it based on elapsed time, a review decision
or a generic continuation instruction predating this exact proposal. No target
Q calculations/model comparisons have been generated or inspected.

## Next authorized steps after that decision

1. Record the user's actual agreement with provenance, preserving the pending
   record, exact reviewed commit and manifest/audit digests. Revise/re-review
   any scientific changes before comparisons.
2. Use the separate reference environment. The current working prefix is
   `/workspace/atom-mlmm-reference-pilot-v2/env`; reproduce it from the SHA lock
   if unavailable. Main environment is `/workspace/atom-mlmm-g05-v2/activate.sh`;
   unchanged installer is available for fresh environments. Amber stays separate.
3. Run `tools/generate_neutral_quantum.py` with `--plan-root
   fixtures/chemical_reference_v3`, actual `--approval` record, explicit
   `--reference-python`, and a **new** `--output` directory. It verifies the
   frozen input/package hashes, runs 46 isolated offline quantum gradients,
   saves all outputs/failures, and enforces the total 12 h timeout. Freeze the
   records/manifest under `fixtures/chemical_reference_v3/quantum/` only with
   complete provenance; no quantum runtime enters the core package.
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
