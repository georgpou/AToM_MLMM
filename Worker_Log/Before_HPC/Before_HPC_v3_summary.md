# Before HPC v3 — Batch C approval checkpoint

**Outcome:** campaign partial. A and B are implemented and worker-tested; C's worker has finished with bounded synthetic qualification and an explicit uncovered C3 requirement. **Checkpoint:** 2026-10-07 12:44 UTC. **Worker:** gpt-6-luna/max, sequential, no nested agents. No independent audit occurred.

The user approved C and required a report/stop before another worker. D and E have not started. The consolidated CPU suite, final documentation self-test and installed/offline checks remain reserved for after E.

## Snapshot and implementation

Checkout `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`; published base `4ad8ee835809325ceec8a017222415043347967d`. C started from B's checkpoint `07454097b0a1c9dafa9e0ce704f0c0a3e07b4b9a`. Design and criteria were frozen in `ac86c1cef6974201910708ffffb9fb62a065f9c0`, `f9fe1cb4ece34548b4bfba106ab8683e935bf50c` and `911acc0909c7b43ac620b8bd5508f94f08f3f26b` before qualification. Source/tests/handoff/evidence are committed as `0de7cc887adc77863d8bc3b9b888f6239c8c8687`.

The `src/atm_mlmm` Git tree is `ff83c9e149502ae14c4d8571b84e18615a7b5b52`, containing 41 Python modules. [The checkpoint receipt](evidence/checkpoint-c-v1/identity.json) records every module digest, final receipt hashes and the preserved supplied-file identities. All 386 supplied files remain unchanged. Source/test/template bytes match the worker's final receipt; no source/test/fixture delta exists after the worker commit. Original `work` remains clean at `2d7bcc94f901738e39f536f16de84699d4e8d631`. No remote publication or history rewrite occurred.

C adds serializable `ExchangeAnalysisInput` and `ExchangeResamplingSpec`, plus opt-in `analyze_exchange`. It reconstructs original raw energies before selection, groups retained synchronized frames against declared synthetic manifests or persistent journal boundaries, and resamples whole blocks or independent runs with state/walker/raw records kept together. Draws refit the existing estimators, retain failure diagnostics and withhold covariance when draws fail. Diagnostics separate mean uncertainty, run spread and resampling units. Legacy `analyze`, fixed-state behavior and old record serialization remain available.

Relative `B_minus_A` thermodynamic records use `Gbind(B)-Gbind(A)` and preserve signed corrections and final-result admission. The [D/E handoff](../../fixtures/analytic/exchange-analysis-v1/README.md) contains concrete API/JSON examples and the persistent-window sidecar contract. The [molecular correction template](../../fixtures/analytic/exchange-analysis-v1/relative-binding-template.json) leaves translation standard state, bound release, orientation, conformation, state counting and midpoint bridge as `required_uncomputed`. Placeholder descriptions and volume are not physical evidence.

## Actual checks and bounded qualification

| Check | Actual outcome |
|---|---|
| Initial regression attempts | 2 expected failures, then 17 expected failures; outputs preserved |
| Earlier affected analysis/schedule/result/restraint command | 21 passed, exit 0; overlaps the final focused command |
| Frozen synthetic qualification | 1 passed, 0 skipped, exit 0, 54.01 s |
| Final packet-focused regression | 43 passed, 0 skipped, 1 deselected, exit 0, 30.94 s; deselected test passed separately above |
| Whole CPU suite/final docs self-test/installed-offline checks | Not run; reserved for after E |

Exact commands and retained exploratory failures are in [the command receipt](evidence/batch-c-v1/command-receipt.md). The final command covered both new test files and the affected analytic free-energy, schedule, result-admission and restraint-volume files. The earlier 19-/21-pass checks are not added to a unique-test total. The worker reused unchanged CPU v2 locks/dependencies, serial scientific execution, two threads and the 8 GiB limit; no setup replay or expanded chemistry ran.

The frozen design used 12 seeds, 4096 synchronized frames per run, 32-frame blocks and 64 draws, with iid and AR(1) rho 0.5/shared-noise controls. PyMBAR and UWHAM estimated `1.540292044537 kJ/mol`, SE `0.024280745297`, against the independent `+1.5` answer. The `0.040292044537 kJ/mol` error met both three-SE and 0.1 kJ/mol limits. Estimator difference was `5.33e-15 kJ/mol`. Block-bootstrap variance / independent-run mean variance was `0.9944036622`; the whole-run ratio was `0.8231580172`, both inside the predeclared `[0.5, 2.0]` interval. Correlation, marginal, independent-baseline, reverse and zero-restraint controls also passed. No analyzer/schema/design change followed qualification; later additions were handoff text and a template-admission test covered by the final command.

These qualify only the specified synthetic analytic controls. They do not qualify scheduler mixing, MD convergence, molecular uncertainty, molecular affinity or G08. The persistent-journal adapter was not exercised on a molecular history. Prior A/B checks retain their recorded snapshot scope and are not relabeled as fresh combined-branch passes.

Evidence limits: early wrappers omitted exact argv/start metadata; their failed outputs remain intact. The qualification wrapper omitted its start timestamp; its receipt distinguishes the file completion time. The worker receipt lists an earlier handoff README digest; this checkpoint records the actual committed README digest `504ac5a788d5adc2208850dfa9f55a213604683db0bb8e34e13529859943c0c4`, including the final C3 hold. Source/test/template digests match. The worker's duration text starts at 12:18; the coordination ledger records actual dispatch at `12:20:35.430021 UTC`, final focused completion at `12:39:19 UTC`, and worker completion around 12:42. Thus worker C used about 22 minutes; this checkpoint brings C's turn to about 25 minutes. Campaign wall time since approximately 10:46 UTC is about two hours, including approval pauses, leaving about three hours of the five-hour allowance.

## Remaining blockers and stop

1. **Uncovered C3 requirement:** matched analytic A→A zero compatibility with nonzero instantaneous perturbation and B−A reversal are tested. A general contract refusing closure comparisons for unmatched endpoint physical metadata is absent, with no endpoint metadata schema or closure-comparison service. Shared thermodynamic descriptions do not prove matching physical states. C3 is not fully closed; the requirement remains an implementation/definition hold.
2. **Molecular obligations:** all six template corrections and linked correction covariance remain unresolved. No production molecular history, uncertainty, affinity or closure is established. Target/preparation/physical decisions and short preflight work remain D obligations.
3. **Existing scientific obligations:** G07 physical failures, seven sensitivity exceedances, 29 missing references, adequate sampling and physical corrections remain open. The QM ledger and false continuation authorization are unchanged; no QM or long sampling ran.
4. **Later execution:** D/E, final consolidated checks, E performance measurements and actual cluster/hardware/storage/parity/restart trials remain pending. Statistical code has worker tests only; independent review awaits explicit authorization.

Stop here and wait for the user's instructions before worker D. No independent audit, gate closure, push, release or deployment occurred.
