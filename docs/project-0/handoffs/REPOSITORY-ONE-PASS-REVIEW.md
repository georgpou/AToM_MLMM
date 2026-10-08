# One-pass repository review and remaining-work inventory

Prepared 2026-10-07 UTC. This is an assignment for a future reviewer, **not a new audit result**. The user requests one thorough pass over the published engine, a deep check of mathematical, physics/chemistry and computational correctness, and a prioritized list of remaining work. Do not start an implementation or repeated repair/re-audit cycle.

## Reviewer, snapshot and scope

Use exactly **`gpt-6.1-sol` with reasoning effort `max`**. One reviewer only; no subagents or parallel workers. If that model is unavailable, report the limitation rather than substituting. This handoff does not authorize repairs, new scientific definitions, expensive calculations or publication of review findings.

Repository: `https://github.com/georgpou/AToM_MLMM.git`, published branch **`g10-engine-next`**. The completed engine/publication anchor is **`59c1be98b708e8d607a3af325660d3622d30c5ea`**. Main and the predecessor were verified unchanged: main `2d7bcc94f901738e39f536f16de84699d4e8d631`, `cloud-engine-continuation` `3952a9b36a92e37f0f98fdf3981c9320368a18b3`.

Record actual branch HEAD and clean/dirty status before reviewing. This handoff is a documentation-only addition after the engine anchor. Check the anchor-to-HEAD diff before carrying forward its evidence. If scientific source, tests, assets, locks or contracts have changed, identify that exact delta and do not assume old test results qualify it. Preserve user changes; keep the reviewed source frozen. Write the eventual report/evidence on an unused child branch if commits are needed; no merge, reset, rebase, force-push or changes to main/published predecessors.

Review the **whole implemented program**, including its declared limits and unfinished gates. The G10 GREEN below is narrow acceptance, not a whole-program certificate. Assess actual code and evidence against contracts; planned gate tests are not executed tests. Avoid a full-history onboarding exercise: consult earlier records only for the claim or equation you are checking.

## Starting facts and relevant reading

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md), [DEVELOPMENT](../../DEVELOPMENT.md), the [CPU setup guide](../../../environment/cloud-cpu/README.md), and the [final G10 handoff](G10-MULTISTATE-FINAL-HANDOFF.md). Use S01–S07 in `docs/project-0/specs/` as the scientific/architecture/validation authority, then the relevant G00–G13 gate definitions. Include the dense-solvent/pair-exchange and multistate amendments; do not expand their accepted profiles.

- Scientific lineage: accepted ancestor `2c02cc2713924140a82aefda37fd5885747e5837`, retained scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`, earlier reviewed submission `bc6fd520308fba7e7448929138eb91e80ca6f063`.
- Latest engine source `3f93efa079ae36514d86d34f9dbc263722bcd1cd`; worker submission `8bc2ced1d7f88e6503ec0b809e309456c307d786`; exact reviewed snapshot `2be9334aea5c8fc34a4bb7ca0ebf6c46802aee27`.
- [Final G10 v8 audit](../../../Worker_Log/Milestone_05/Gate_10_v8_audit.md), commit `c28c04bc4d7507998044168f1a123bba1a4d23c3`: **GREEN for bounded Tasks 1–4 plus repairs**, all 20 assertions/R1–R7 closed. Reviewer was `gpt-6.1-sol/max`; implementation/repairs were `gpt-6-luna/max`.
- Final worker verification: **631 CPU tests passed, zero skips**, one full run in 1238.59 s; seven focused checks and two fresh solvated pilots. Independent final checks: eight pytest passes and four Decimal120 arithmetic controls. Use the [worker evidence](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v8/README.md), [review packet](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_05/evidence/G10_v8_review_packet/README.md) and [independent evidence](../../../Worker_Log/Milestone_05/evidence/G10_v8_independent/README.md).
- Retained runtime: original pair API plus explicit **3–8-state bounded serial CPU schedules**, stable walkers/full permutations, fresh four-entry pair energies including outside terms, unique samples/full histories, all-worker checkpoints and both host RNG streams committed together. Incomplete resume rejects; explicit rollback preserves failures and replays without duplicate/lost records.
- Initial v5 and v7 combined audits were RED; their failures/repairs remain immutable. The final clock repair rejects backward time inertly and uses a finite, outward-rounded floating-point envelope, preserving negative origins and valid large-origin stagnation. Review the latest disposition rather than treating the old RED as still open.
- **Known documentation discrepancy to reconcile:** lower `STATUS` sections (`Next work` and the M05 support-table row) still describe v5 repairs/multistate acceptance as pending/RED. The top status and final v8 audit supersede them. List this as documentation drift; verify code/evidence separately.

## One-pass method

1. Inventory all `src/atm_mlmm/` modules, public entry points, tests, admitted fixtures, scientific contracts and gate claims. Map each subsystem to evidence and supported profiles. Note missing/stubbed features and claims that exceed evidence.
2. Trace each major calculation/workflow once from input admission to saved results. Derive the expected mathematics/physical accounting from the contracts before comparing it with code; an expected value copied from the function under test is not independent evidence.
3. Select one small set of high-value independent checks based on concrete risks found in that trace. Prefer existing analytic controls, fixed coordinates and saved records. Reuse byte-identical, scoped prior proofs after checking their applicability. Do not rerun whole accepted reviews or the full CPU suite merely to obtain another pass count.
4. Finish one report and dependency-ordered backlog. A concrete defect needs a minimal reproduction or a precise proof, not a repair. Stop after the planned coverage/probes; record remaining uncertainty explicitly. No speculative edge-case campaign, feature implementation, optimizations, tolerance changes or second audit round.

Cover every source module in a compact coverage/evidence map, including modules checked by justified reuse. Depth belongs in the equations, force accounting and workflow traces, not in repetitive prose. Prioritize consequences for admitted calculations and documented guarantees. If stuck on one issue, state the specific blocker and use a smaller diagnostic instead of looping.

## Required technical coverage

| Area / principal source | What to establish |
| --- | --- |
| Identity/admission: `identity.py`, `schema.py`, `partition.py`, `capabilities.py`, `environment.py` | Stable atom identities, supported chemistry/model/ensemble/precision, complete ligand transfer, fixed ML membership, cap collections, manifests and rejection of unsupported combinations. |
| Hamiltonian/forces: `ledger.py`, `hybrid.py`, `routing.py`, `atm.py`, `geometry.py`, `derivatives.py`, `models/`, `embeddings/` | Derive the admitted Hamiltonian; reconcile every MM/ML/cap/outside contribution exactly once. Verify forces on every influencing real atom and cap parent, mapped geometry/neighbor refresh, native virtual-site redistribution and periodic/exclusion/cutoff accounting. |
| Protocols/units: `protocols/`, `endpoints.py`, `restraints.py`, `schedule.py`, `adapters/atom.py` | Complete ABFE/RBFE mobile groups/maps, endpoint and midpoint connections, full both-map clearance, thermodynamic domains/signs/corrections, and the pinned AToM routing/decision path. |
| Sampling/analysis: `analysis.py`, `schedule.py`, `evidence.py` | Correct complete reduced-energy reconstruction, sample/state/walker identities and counts, estimator normalization, constants/covariance/corrections, correlation treatment, overlap diagnostics and honest uncertainty/convergence claims. |
| Preparation/runtime: `prepare.py`, `solvent.py`, `workflow.py`, `persistence.py`, `exchange.py`, `exchange_journal.py`, CLI | Consistent prepared/production force ownership, fresh energies after parameter changes, actual restored-state admission, all-worker/both-RNG atomicity, complete histories, failures/rename/derived-report behavior, default rejection and explicit rollback/replay. |
| References/release: `chemical_reference.py`, `model_reference.py`, `joint_reference.py`, fixtures, locks, gate reports | Chemical-reference provenance and applicability, preserved failures/budgets, reproducible source/model/package identities, actual support matrix and remaining release/resource/hardware obligations. |

Useful independent expectations (apply only to the admitted definitions):

- Forces satisfy `F = -grad(E)` on all real coordinates. Check unit conversions, finite-difference step sweeps at existing S06 tolerances, and cap chain-rule/Jacobian ownership. Inspect endpoint/mapped/outside derivatives; do not manually project a force already redistributed by native machinery.
- With energies in kJ/mol at 300 K, `beta = 1/(R*T)` is approximately `0.4009078501424201 mol/kJ`. Trace dimensionless reduced energies and their complete outside terms into analysis and exchange.
- For admitted exchange, independently derive `Delta = u_i(x_j) + u_j(x_i) - u_i(x_i) - u_j(x_j)` and `p = min(1, exp(-Delta))`, including any declared weighting terms. Check sign/extreme-value handling against the **existing pinned adapter**; do not implement another Hamiltonian/Metropolis path.
- Derive binding signs and standard-volume/restraint/midpoint/state-counting corrections from S05. Missing or uncomputed obligations must withhold a final binding result; correlated correction/estimator errors require the admitted joint covariance treatment.
- Pair-kernel stationarity does not prove whole-sweep detailed balance, finite-trajectory mixing or convergence. The fixed-state thinning profile does **not** qualify exchanging correlated walkers; inspect whether software claims/results enforce that limit.
- Exact saved/restored clocks and integer steps differ from the finite roundoff envelope for elapsed time. Reuse the final clock proof where unchanged; valid repeated addition at 100,000/999,999 steps is pure arithmetic, not a reason to run long MD.

Separate a defect in this repository's coupling/routing/validation from an upstream OpenMM/AToM issue. Attribute upstream defects only with a minimal upstream-only reproduction or equivalent evidence. Keep scientific model error separate from a mathematically incorrect implementation of the admitted model.

## Known unfinished work to verify and prioritize

This is a starting list, **not the review's completed conclusion**:

- **M03/G07-T4 physical qualification remains blocked:** seven boundary-sensitivity exceedances, original pilot force failures, 29 missing new references. Preserve all 46 accepted G05 records and original receipts/failures. Quantum ledger charged `2325.6446500519996 s` of `86400 s`; continuation screen is false. No reset, budget increase, tolerance relaxation or expensive QM launch.
- **G08 exchanging-walker statistics:** complete raw-energy reconstruction exists; correlation/resampling and uncertainty qualification for exchanging walkers remain required before reporting their uncertainty.
- **Full G09/G10/M05:** bounded technical subsets are accepted; check the original full-milestone requirements and enumerate each remaining obligation instead of inferring closure from the new scheduler.
- **G11/G12:** general admitted manifests/partitions/cap collections and one/two complete ligands through the common engine, with reviewed supported chemistry and protein definitions. Distinguish already-present tiny controls from complete protein implementation and physical acceptance.
- **Host–guest input:** preserve 18-crown-6/methanol ABFE. The preferred methanol→ethanol host–guest RBFE starter still needs independently qualified chemistry/parameters/atom identities/both-map clearance. The abandoned unreviewed notebook branch is not an accepted input source.
- **G13:** CPU resource measurements, reproducible packaging/support matrix and full release requirements remain to be assessed. GPU/device/performance claims need real hardware evidence.
- **HPC:** exact cluster-profile parity/checkpoint/restart trial before demanding calculations. Cluster details/resources, long QM/solvent/protein sampling and production scripts are deferred. No cluster authorization is needed to prepare this review.

The retained 224-atom solvated ABFE and 233-atom unequal methanol→acetamide RBFE fixtures use 64 waters. The latest pilots use three workers, two boundaries/one step and only four existing preparation-count overrides. They establish coupling/runtime behavior, not equilibrated liquid solvent, converged affinity or chemical accuracy. `binding_result=not_evaluated` remains the baseline.

## Environment, evidence and verification limits

Here the validated prefix is `/workspace/m05-cpu-setup-v2`; the reviewed checkout is `/workspace/AToM_MLMM-g10`. In **every scientific shell**:

```bash
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

A replacement machine installs the unchanged locks through `environment/cloud-cpu/install.sh` into its own external prefix. Preserve the main NumPy2/AmberTools NumPy1.26 separation and exact model/package bytes. Do not assume these prefixes or local outputs exist elsewhere. Missing local evidence/hardware is an availability limit, not automatically a source defect or a pass.

Run scientific jobs **serially, at most two CPU threads and within 8 GiB**. Use small analytic/fixed-coordinate controls; any fresh molecular check is bounded by the existing tiny pilot settings. No long sampling, expensive QM, GPU benchmarks or production runs. Choose probes before executing; do not broaden after each result.

Local preserved evidence roots include `/workspace/G10_v5_artifacts`, `/workspace/G10_v7_artifacts/v7-attempt-001`, and `/workspace/G10_v8_artifacts/v8-attempt-001`; these are not guaranteed on a fresh clone. Inspect/reconstruct old evidence with its exact frozen source. Do not silently resume/migrate an old sealed bundle under another checkout. New runtime attempts require fresh preparations/unique directories and current source identities.

If a targeted runtime baseline is needed, the retained compatibility files are:

```bash
python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q
python tools/check_docs.py --self-test
```

Do not also run those tests separately if a justified full-suite run already includes them. A full `python -m pytest -q` run is permitted once if an actual source/profile delta, new failure or unreliable baseline warrants it; state the reason. Missing dependencies, skipped/deselected tests, empty collections or import success alone are not numerical evidence. Record exact commands/UTC/exits/counts/skips/source/profile and preserve all failed/nonfinite output; do not silently fix the reviewed code or test harness and erase an original failure.

## Deliverables and stopping point

Use the next unused `Worker_Log/Repository_Review/Repository_Review_vN_audit.md` and matching evidence directory **only when this independent review actually occurs**. Produce:

1. A plain-language summary: what works, what is incomplete/unsafe, and what can proceed next. Keep the main report concise (aim at 100 lines); structured evidence holds detailed derivations/reproductions.
2. Coverage/claim matrix for every subsystem and G00–G13: reviewed snapshot/profile, relevant evidence, and disposition **verified within scope / confirmed defect / not implemented / physically blocked / not assessed**. Give separate mathematical, physics/chemistry and computational conclusions; do not issue whole-program GREEN while physical/reference failures remain.
3. Prioritized backlog: ID, concrete task, reason/impact, supporting file/contract/evidence, dependencies, smallest completion check, resource/reference/hardware need. Separate blockers before trusting results, implementation prerequisites, scientific qualification and optional later improvements. Include one short recommended next batch; do not implement it.
4. Each confirmed defect: affected admitted path, actual consequence, exact location, minimal reproducer or proof, independent expected versus actual behavior, severity, and minimal repair/regression recommendation. Unproven concerns are questions, not confirmed failures.
5. Exact source/asset/evidence identities and test/probe results; provenance for reused claims, preserved old GREEN/RED decisions and explicit unavailable checks. Reconcile stale status claims without rewriting historical audit decisions.

Finish the report/evidence and any report-only documentation/whitespace checks once. No new worker, repair, review round, changed threshold or extra exploratory campaign follows this pass. The user will decide the next implementation/scientific work from the report. End with the prioritized remaining-work list and actual review limits, not a promise of universal correctness.
