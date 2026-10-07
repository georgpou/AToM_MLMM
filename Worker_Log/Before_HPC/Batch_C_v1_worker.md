# Batch C v1 worker report

**Outcome:** implemented and synthetically qualified scope are separate. The
opt-in exchange-history analyzer, relative-binding records, and correction
template are implemented. The frozen synthetic dependence-aware controls
passed. This is not a molecular uncertainty result, G08 acceptance, scheduler
mixing evidence, or convergence evidence.

The analyzer validates complete raw reduced-potential reconstruction before
selection, verifies retained/excluded windows against synthetic manifests or
persistent multistate journal boundaries, and preserves complete synchronized
walker/state/raw/outside-energy bundles in block or whole-run draws. It reports
failed draws without silently dropping them and withholds sampling covariance
if any draw fails. It reports iid weight contributions separately from
resampling units, across-run spread separately from mean standard error, and
dependent full/last-half diagnostics without calling them convergence tests.
The legacy `analyze` and fixed-state behavior remain available. Relative
`B_minus_A` records preserve version-1 serialization, signed corrections, and
complete `BindingResult` admission; final value/error remain withheld while
any correction or required covariance is unresolved.

The 12-seed frozen design used 4096 synchronized frames per run, 32-frame
blocks, 64 draws, AR(1) rho 0.5, and shared innovation fraction 0.5. Both
PyMBAR and UWHAM returned `1.540292044537` kJ/mol (standard error
`0.024280745297`) against the `+1.5` answer; the absolute error was
`0.040292044537` kJ/mol. Estimator difference was `5.33e-15` kJ/mol. The
block-bootstrap variance ratio to independent-run mean variance was
`0.9944036622`, within the frozen `[0.5, 2.0]` interval; the whole-run ratio
was `0.8231580172`. Correlation, marginal, reverse-answer, zero-restraint,
and estimator-agreement checks also passed. The exact controls and criteria
are in [the frozen design](../../fixtures/analytic/exchange-analysis-v1/design.json)
and [the command receipt](evidence/batch-c-v1/command-receipt.md).

The [D/E handoff](../../fixtures/analytic/exchange-analysis-v1/README.md)
contains a concrete `ExchangeAnalysisInput` / `ExchangeResamplingSpec` /
`analyze_exchange` example and the persistent-window sidecar contract. The
[relative-binding template](../../fixtures/analytic/exchange-analysis-v1/relative-binding-template.json)
uses schema version 1.0, `Gbind(B)-Gbind(A)`, weights `B=+1`, `A=-1`, and six
`required_uncomputed` correction rows: translation standard state, bound
release, orientation, conformation, state counting, and midpoint bridge. Its
description and standard-volume placeholders are not evidence or resolved
corrections.

**C3 hold:** matched analytic A→A zero compatibility with a nonzero
instantaneous perturbation and B−A reversal are tested. The general refusal
contract for an unmatched-physical-state closure comparison is not implemented
or qualified: there is no endpoint physical-metadata schema or closure
comparison service. Shared `ThermodynamicSpec` descriptions do not establish
matching endpoint physical states, and this report makes no such closure claim.
All six molecular corrections remain unresolved in the example; no linked
correction covariance was supplied. The persistent-journal adapter was not
exercised on a molecular history. No production molecular data were sampled.

Qualification: one slow frozen synthetic test passed in 54.01 s. Final focused
check: 43 passed, one separately qualified slow test deselected, in 30.94 s;
the affected prior analysis/schedule/result/restraint check passed 21 tests.
No full CPU suite was run. Exploratory failures and fixes are retained as
unique logs in [the evidence directory](evidence/batch-c-v1/); the early
wrappers did not preserve argv/start metadata, which is disclosed in the
receipt. The final tested file hashes, frozen design identities, command
results, and output locations are listed there.

Batch C ran for roughly 21 minutes from dispatch through the final focused
check (`2026-10-07 12:18–12:39 UTC`). The coding and test patch is recorded in
the local commit history; the pre-commit tested source identity is HEAD
`911acc0909c7b43ac620b8bd5508f94f08f3f26b` plus the file identities in the
receipt. The parent-owned shared `progress.md` was left unstaged.
