# One-pass repository review — 7 October 2026 UTC

**Conclusion:** The small, declared CPU engine has substantial evidence that its energy and force calculations work as intended. It is **not yet ready to support trusted protein binding results**. This review found three gaps in the older restart checks, and the existing physical failures remain unresolved. No whole-program GREEN is issued.

**Reviewer:** one gpt-6.1-sol/max reviewer, as explicitly confirmed by the user. No agents or other workers. This was one review pass; no repairs or follow-up audit were performed.

**Snapshot:** published `g10-engine-next`, HEAD `4ad8ee835809325ceec8a017222415043347967d`, initially clean. The difference from engine anchor `59c1be98b708e8d607a3af325660d3622d30c5ea` contains only two handoff documents. Source, tests, scientific definitions, inputs, models and locks did not change. Review files are on the unused child branch `repository-review-20261007-v1` in `/workspace/AToM_MLMM-g10`; no publication or protected-branch changes.

## What works within the checked limits

- The program keeps atom identities, moves complete ligands, and uses the same main calculation path for one or two ligands. Selected model atoms stay fixed.
- The standard force-field and learned-model energy terms are counted once. Forces include every atom that influences the model, including both atoms beside a cut bond capped with an added hydrogen. Forces from that hydrogen are passed back once.
- The connection to the fixed AToM version uses current energies and the correct exchange acceptance rule. Saved energies include all parts needed to reconstruct the analysis table.
- Analysis handles known small examples, energy offsets, correction signs and shared sources of error. It withholds a final binding value when required corrections or their error accounting are missing.
- The newer controller supports the accepted serial CPU schedule of 3–8 settings. Its complete simulation saves, both random-number streams, histories, failure preservation and explicit rollback retain the final v8 acceptance.

These statements apply to the admitted definitions and small controls. They do not establish accurate chemistry, equilibrated solvent, effective mixing or converged affinity.

## New confirmed findings

| ID / priority | What is wrong | Demonstrated consequence |
|---|---|---|
| RR-01 / high | Older fixed-window and pair restart paths do not compare the actual restored clock with the saved sample and portable State. | Both continued to completion after only checkpoint time was changed and its hash updated. One 0.0005 ps step was reported as 1.0005 ps elapsed. |
| RR-02 / high | Fixed-window restart checks restored geometry after entering integration. | A restored atom exactly overlapping another molecule reached the step call. A diagnostic sentinel stopped it; no invalid dynamics were executed. |
| RR-03 / medium | Fixed-window restart checks only the source files listed in the manifest. | A manifest naming 37 of the current 38 source modules passed source admission. |

These reproductions deliberately supplied inconsistent artifacts with coherent hashes. They demonstrate missing consistency checks; they do not show that an untouched accepted run spontaneously corrupts itself. They concern older public restart APIs, not the already closed v8 multistate clock repair. [Exact locations, proofs and smallest repair recommendations](evidence/Repository_Review_v1/findings.md) are saved separately.

**Documentation drift:** the lower [STATUS](../../docs/project-0/STATUS.md) “Next work” section and M05 support row still call v5 repairs/multistate acceptance pending or RED. The top status and final v8 audit supersede them. The old RED audits remain valid historical records. This review does not rewrite them.

## Separate conclusions

**Mathematics:** the traced energy counting, forces, units, exchange rule and small analysis controls agree with the declared equations. This is limited evidence, not a proof for every possible input. Error estimates for simulations that exchange settings are unfinished and correctly rejected by the current analysis path.

**Physics and chemistry:** the small neutral-molecule references remain useful within their original scope. The larger model with cut bonds is still physically blocked. The retained contact pilot's typical force error is about eight times the allowed limit; its largest atom error is about fourteen times the limit. Seven original boundary-sensitivity failures remain. These are failures of physical qualification, not proof that the code differentiates its energy incorrectly. Exact measures and limits are in the scientific record.

**Computation:** accepted small CPU coupling and multistate transactions have strong retained evidence. The older restart checks need repair before their broader continuation guarantees can be trusted. General protein execution, cluster parity, GPU placement and release performance are not qualified.

## Prioritized remaining work

The [full backlog](evidence/Repository_Review_v1/backlog.md) gives dependencies, evidence, smallest completion checks and required resources for each item.

1. **B01–B03: close RR-01–RR-03.** Check actual restored state before stepping and require a complete source inventory across older restart entry points. Preserve existing failure/rollback behavior.
2. **B04: reconcile live status.** Update the stale lower claims and link each accepted scope to its final evidence, preserving historical decisions.
3. **B05–B06: qualify analysis before reporting binding results.** Account for dependence between exchanged samples; document which physical states are compared and complete every required correction and shared-error term.
4. **B07: resolve the physical-reference block.** Preserve all 46 accepted G05 records, the seven exceedances and original pilot failures. Establish a feasible continuation decision before any further reference work: 29 new references are missing, and the current resource screen is false. The ledger remains **2325.6446500519996 / 86400 seconds**; no reset or relaxed limits.
5. **B08–B09: finish the full solvated runtime obligations.** Establish a declared physical solvent/preparation profile and close remaining full G09/G10/M05 requirements. The accepted small subsets and scheduler do not close those milestones.
6. **B10–B11: prepare general inputs and cap collections for a complete protein example.** Review chemistry, parameters, identities and every boundary; then qualify the common engine with all-MM, ligand-only and cavity-inclusive controls.
7. **B12–B13: qualify molecular two-ligand work.** Preserve 18-crown-6/methanol ABFE; independently prepare the preferred methanol→ethanol starter. Later check identity, independently sampled reverse direction and properly matched closure. The methanol→acetamide toy is not a substitute for that input or a finished G12 result.
8. **B14–B15: qualify the intended cluster and release profiles.** Run an exact-profile parity/checkpoint/restart trial before demanding jobs. Complete clean packaging, support claims and measured CPU resources; require actual hardware for GPU claims.
9. **B16: consider convenience and optimization later.** Profile first. New timesteps, pressure sampling, electrostatic embedding, broader chemistry or extra hardware require separate definitions and evidence.

**Recommended next batch:** B01–B04 only: repair the three older-path consistency checks, add the small rejection regressions described in the findings, and reconcile status. That is a concrete next implementation batch for the user to authorize separately. It needs no new chemistry, quantum calculations or long sampling. This review did not implement it.

## Evidence and limits of this review

- Fresh numerical checks: **31 passed, zero skips**, 16.80 s; four preselected diagnostics completed and reproduced the three findings. Independent unit/sign arithmetic also passed. Commands, UTC times, exits, logs and measured memory are in the [evidence index](evidence/Repository_Review_v1/README.md).
- All **105** v8 source/test hashes match: **38 source modules and 67 files under tests**. The retained full-suite log reports **631 passes, zero skips, 1238.59 s**; its raw/compressed bytes agree. That suite was reused, not rerun. The final eight independent v8 passes and four high-precision clock controls are also retained evidence, not fresh results of this review.
- The named old prefix and local pilot roots were absent. The unchanged installer built `/workspace/repository-review-cpu-v3`; its nine setup checks passed, with NumPy 2 in the main environment and NumPy 1.26 in separate AmberTools. Earlier setup failures and one diagnostic import-path failure are preserved; none is presented as a numerical source failure.
- The 224/233-atom fixtures have 64 waters. Prior pilots used three workers, two boundaries and one step, with only the four admitted preparation-count overrides. They test execution and coupling; they do not qualify liquid solvent or affinity. **`binding_result=not_evaluated` remains the baseline.**
- No fresh molecular pilot, full-suite run, long trajectory, quantum job, GPU benchmark or cluster trial was performed. Old local pilot bundles could not be rehashed here; their previously recorded independent verification is explicitly reused. No evidence is silently migrated or resumed under another source.
- Every source module, fixture family, public entry point and G00–G13 claim is covered by the [coverage map](evidence/Repository_Review_v1/coverage.md). Detailed equations and workflow traces are in the [scientific record](evidence/Repository_Review_v1/scientific-trace.md). Unimplemented and unavailable checks remain open.

The source remains frozen. Only review reports, diagnostic scripts and their evidence were added. The stopping point is this report and backlog; the user decides the next implementation or scientific work.
