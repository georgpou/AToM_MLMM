# G05 real MACE candidate — v1 worker

**Scope:** G05-T1/T2/T3 software checks pass; T4 and independent gate review pending.\
**Outcome:** software ready for scoped independent audit; full G05 blocked on
explicit M00 agreement and actual quantum data.\
**Snapshot:** unused child `m03-reference-g05` at exact accepted G04 handoff
`bc788aeeedb4dc45026ac1bff44bd4fb533b325a`. Only the child is edited/committed;
protected remote tips are recorded in [lineage evidence](evidence/G05_v1/setup-and-lineage.json).

## Changes

Pinned total `energy`, CPU float64, actual ASE CODATA-2014 unit factors and
measured architecture/card; guarded loader shared with the inherited example.
Direct-model oracle independently enumerates one joint nonperiodic radius
graph and differentiates total energy with autograd; it calls no ASE adapter
or neighbor helper. Mechanical builder adds the real provider through actual
OpenMM-ML ASE construction and the unchanged boundary sealer. Production
uses native virtual-site force redistribution exactly once.

PyTorch-object pickle round trips caused a real force-ledger identity failure.
The deterministic pinned ASE loading facade serializes only immutable verified
asset paths and recreates the same maintained calculator offline; the exact
ledger/ownership guards remain unchanged. Initial failures, test setup repairs
and successful numerical arrays are retained.

## Verification

Captured `model-adapter-v3`: 11 passes, exit 0. Independent raw energy/gradient
and cap Jacobian checks pass on Reference and CPU; all real forces include
independently evaluated retained MM. Checks include both parents, translation,
rotation, atom permutation, nonidentity final map, component FD steps
1e-3/1e-4/1e-5 nm (complete-MM additional 1e-6) and deliberate missing-parent,
factor-ten, wrong-order and stale-cap faults. Raw values and all FD samples are
under [numerical evidence](evidence/G05_v1/numerical-v3/finite-differences.json).

Earlier baseline/setup and preliminary asset/full/analytic/environment/upstream
captures are under [G05_v1](evidence/G05_v1/source-input-manifest.json). The last
full preliminary suite had 265 passes before real-provider code was added;
`task2-full` now passes all 276 tests (56.14 s, exit 0) on the current source.
No numerical tolerance,
scientific definition, weight or retained-MM term was changed.

## Handoff

Continue locality, approach/cutoff/counterfactual domain scans, actual ATM cap
checks and offline serialized reload. The exact M00 proposal awaits user
agreement and an independent Astra/high design review before T4 comparisons.
All eight stable assertions and the final exact-snapshot Astra/high audit are
required for full acceptance. G06/G07 remain later; M03 closes at G07.


## T3 continuation before chemical approval

`software-v4`: 15 passes / exit 0 (21.39 s), covering all six software stable
assertions plus cap/FD/fault cases. Disconnected ML-only additivity and the
incorrect split-graph negative pass. Domain evidence saves 36 actual raw
samples across both mappings: approach/compression, cap-parent rotation,
last actual intercomponent edge crossing, separation and extreme coincidence.
All admitted samples are finite and independently agree with the adapter;
coincidence remains an explicit diagnostic, with no physical adequacy claim.
The nested MACE ATM check compares full real forces with independent native
cap projection plus retained-MM evaluation at both endpoints and the middle.

Serialization testing found absolute asset paths depended on the previous
checkout. Initial denial missed pathlib's io.open and misleadingly passed;
the corrected denial reproduced a failed C++ XML unpickle. The repaired inert
facade resolves the bundled asset in the current installation, verifies before
weight loading and keeps deterministic force identities. `green-relocated-and-atm`
passes both tests (18.17 s); source/assets were moved to a fresh installation
root with original checkout opens, DNS/connect and caches denied. Numerical
identity is unchanged. All failed and inadequate attempts are retained.

Metadata candidate admission has a real RED/GREEN check; pinned parameters
are admitted only as metadata with qualified=false. Analytic admission and
common ATM/scientific contracts remain unchanged. New complete-source
regressions and final independent review are still required. M00's original
v2 review required a G07 geometry repair; corrected v3 and ten explicit
rotation-quadrature controls await fresh review and the user's scientific
choice. No chemical target results were generated.


## Review-ready current-source verification

| Capture | Actual result |
|---|---|
| final-partial-full | Exit1, **284 passed / 2 failed** in66.72s; both failures are the stable T4 missing-reviewed-quantum-data check before any model score |
| final-partial-analytic | Exit0, **265 passed / 21 deselected** in35.13s; model/chemical selection is not numerical qualification |
| inherited-g02 / inherited-g03 / inherited-admission / inherited-g04 | Exit0, **78 / 38 / 74 / 24 passed** |
| task3-environment | Exit0, **9/9 strict checks**, exact core/Amber versions separate |
| review-ready-upstream | Exit0, **1 passed** on upstream tests/test_uwham.py |
| review-ready-documentation | Exit0, **zero errors / eight self-tests**, whitespace clean |
| quantum-generation-unagreed | Exit1 before output directory/worker creation; actual decision has user_agreed=false |
| green-reference-metrics / green-force-metric-shape | Exit0, final3 metric/control tests; fixed-composition zeros, maximum localized error, missing data and atom-broadcast rejection; no quantum substitute |

The [tested source/input manifest](evidence/G05_v1/source-input-manifest-partial.json)
records269 exact current hashes before this frozen submission. These source
bytes were tested with parent HEADa825f5f and subsequently committed unchanged;
report-only updates do not alter the source/input identities. T4 generation
and comparison code is prepared but not runtime-qualified on actual target
references. The full suite remains red because the two genuine quantum inputs
are absent, not because an analytic placeholder was accepted. No target
comparison was inspected, no failed sample discarded, and no threshold changed.

The scoped independent software audit must identify any remaining code issue
and may accept only G00-T2/G05-T1/T2/T3 checks actually reviewed. Final full G05
review must follow completed T4. The [fresh-agent continuation](../../docs/project-0/handoffs/M03-G05-continuation.md)
contains the actual decision dependency, generation command and remaining
qualification obligations. User agreement remains the only present scientific
prerequisite to start generating target references; missing reference data
continues to block full gate acceptance.
