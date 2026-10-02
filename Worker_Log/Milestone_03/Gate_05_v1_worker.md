# G05 real MACE candidate — v1 worker

**Scope:** G05-T1/T2 software qualification in progress; T3/T4 and gate review pending.\
**Outcome:** partial.\
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
