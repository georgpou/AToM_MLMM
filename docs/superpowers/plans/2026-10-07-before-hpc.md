# Before HPC implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` for your assigned packet. The user's chosen execution method is one orchestrator with sequential **gpt-6-luna / max** coding workers. No reviewer agents, independent audits or automatic review rounds are authorized. This instruction overrides workflows that normally add them.

**Goal:** Finish the feasible cloud development work, produce reproducible worker evidence, and leave a precise list of scientific and cluster obligations for the user to decide.

**Architecture:** Keep the common physical builder, protocol records, native ATM/AToM adapter, analysis and persistence boundaries. Strengthen the older restart paths, extend the existing collection-based input contracts, and add analysis and release tools around that engine. Preserve the admitted Hamiltonian and existing scientific thresholds.

**Tech stack:** Pinned Python/OpenMM/AToM/MACE/AmberTools CPU environments; pytest; dependency-light JSON records and CLI; existing locked artifacts.

**Spec:** S01–S07 and applicable G08–G13 in `docs/project-0/`; existing dense-solvent and multistate amendments. The completed review is `Worker_Log/Repository_Review/Repository_Review_v1_audit.md`, with its detailed `evidence/Repository_Review_v1/backlog.md` and `findings.md`. That review is local documentation, not a published gate decision.

## What completion means

This is a finite development checklist, not a promise to cover every imaginable input. Cloud can implement mechanisms, test small known-answer controls, prepare inputs, measure small CPU costs and build the cluster handoff. Cloud cannot supply unavailable hardware, adequate long sampling or the missing physical-reference qualification by writing more code.

New work ends as **implemented and worker-tested**, **blocked by a named input/definition**, or **deferred to HPC/resources**. Existing acceptance remains scoped to its original snapshot/profile. New gate or milestone GREEN decisions require a separately authorized independent review; none occurs under this plan. `binding_result=not_evaluated` remains the molecular pilot baseline.

## Orchestrator setup

- [ ] Read `AGENTS.md`, current `STATUS`, this plan and the [new-chat handoff](../../project-0/handoffs/BEFORE-HPC-ORCHESTRATOR.md). Read historical records only for an assigned claim.
- [ ] Record UTC, local branch/HEAD, dirty files and `origin/g10-engine-next` HEAD; fetch that published branch if network is available. Preserve user changes. Do not substitute `main` for the development branch.
- [ ] Create **`before_HPC`** as a child of the actual latest `origin/g10-engine-next`, preferably in an isolated worktree. Example: `git worktree add -b before_HPC /workspace/AToM_MLMM-before-HPC origin/g10-engine-next`. If that branch/path exists, inspect it and report the conflict; never reset or overwrite it.
- [ ] Compare the new base with reviewed HEAD `4ad8ee835809325ceec8a017222415043347967d`. At review time, the engine anchor `59c1be98b708e8d607a3af325660d3622d30c5ea` to that HEAD changed only two handoff documents. List any newer source/test/asset/lock/contract delta. Reuse evidence only for unchanged bytes and matching profiles; this comparison is implementation onboarding, not another audit.
- [ ] Locate the plan/packets and local review before switching worktrees; copy planning documents into the child if needed. Do not edit the sealed review/evidence. These planning files and the review were local, uncommitted files when this handoff was written; a fresh clone will need the supplied handoff files.
- [ ] Reuse an available validated CPU prefix with unchanged locks. Here `/workspace/repository-review-cpu-v3` passed all nine setup validations. The originally named `/workspace/m05-cpu-setup-v2` and old local G10 artifact roots were absent. Else install unchanged locks through `environment/cloud-cpu/install.sh` into a fresh external prefix.
- [ ] Dispatch only the global rules, assigned packet and concise previous-worker interface/result summary. Use exactly `model="gpt-6-luna"`, `reasoning_effort="max"`, **`fork_turns="none"`**, no nested agents. Pass the actual checkout path and packet explicitly; do not inherit the full conversation. If unavailable, report the limitation. Keep only one coding worker active at a time; use five workers total, one per batch. Reuse the owning worker for scoped fixes instead of spawning extra agents. A blocked part does not prevent independent later work.

## Global constraints

- Every scientific shell activates the chosen main prefix, then sets `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"`. Keep the main NumPy 2 and Amber NumPy 1.26 environments separate.
- Scientific jobs run serially, at most two CPU threads and within 8 GiB. New molecular runtime checks use the retained tiny pilot settings: three workers, two boundaries, one step, only existing preparation-count overrides. Fixed-coordinate checks may use several small frames; no long molecular sampling, new QM launch, GPU benchmark or cluster job.
- For a complete protein, first run declarative/input checks and a resource estimate. Fixed-coordinate evaluation proceeds only if it fits these limits. Do not turn a large protein run into an unlimited cloud task; preserve the reason and hand off the missing execution check.
- Retain H/C/N/O, neutral admitted ML components, mechanical embedding, existing fixed-length protein C–C boundary policy, full ligand transfers, fixed membership, full forces, orthorhombic admitted periodic accounting, CPU/float64 and NVT. Keep native cap force redistribution exactly once. Preserve the pinned adapter's Hamiltonian and exchange decision path.
- Do not introduce charged/metal/covalent/electrostatic profiles, new boundary chemistry, NPT, larger timestep, HMR/MTS, new weights/training, altered tolerances or budgets. Missing scientific definitions are a documented hold; do not invent them to finish a checkbox.
- Preserve all 46 accepted G05 records, original G07 force failures, seven sensitivity exceedances and the 29 missing-reference obligations. QM ledger remains `2325.6446500519996 / 86400 s`; its continuation screen is false. Writing an HPC plan is not permission to run it.
- Preserve the 18-crown-6/methanol ABFE input and the accepted 224/233-atom, 64-water plumbing fixtures. Their short pilots do not establish liquid solvent, chemical accuracy, mixing or affinity. No input from the abandoned unreviewed notebook branch.
- No merge/reset/rebase/force-push, changes to main/published predecessors, remote publication, release tag or deployment. Local commits on `before_HPC` are allowed. Source changes intentionally require fresh run directories and fresh preparations; do not migrate/resume sealed old bundles under changed code.
- Each worker writes one short `Worker_Log/Before_HPC/Batch_<letter>_vN_worker.md` and unique evidence directory. Record exact commands, UTC, source/tree identity, profile, exits/counts/skips and failures. Do not write `_audit.md` or call self-checking independent acceptance.

## Batches and ownership

| Order | Luna packet | Concrete output | Review backlog |
|---|---|---|---|
| A | [Restart safety](before-hpc/batch-a-restarts.md) | Complete source admission; actual restored-state/geometry checks before stepping; three defect regressions; live status reconciliation | B01–B04, part B09 |
| B | [General input and cap collections](before-hpc/batch-b-inputs-caps.md) | Zero/one/multiple admitted cuts; general one/two-ligand manifests through the common builder; full-force/reload controls | B10, input mechanism for B08/B11/B12/B13 |
| C | [Analysis and thermodynamic results](before-hpc/batch-c-analysis.md) | Explicit block/resampling development path; analytic qualification evidence; relative result/correction/covariance support; honest diagnostics | B05–B06, analytic part B13 |
| D | [Molecular inputs and preparation](before-hpc/batch-d-molecular-preflight.md) | Methanol→ethanol development input; protein input validator/preflight controls; solvated recipes and molecular-test run specifications | B08/B11/B12, preparation part B13 |
| E | [Release and HPC handoff](before-hpc/batch-e-release-hpc.md) | Installable technical package/offline bundle; scoped CLI/check driver; CPU costs; complete gate matrix; guarded HPC/QM handoff | B07/B09/B14/B15, small B16 convenience |

A precedes B and all public continuation use. B and C precede D's combined controls. E assembles outputs from all available batches. Keep this order to avoid overlapping edits to `schema.py`, `workflow.py` and the adapter. Do not create one agent per test or backlog row.

## Coverage: every backlog item has a destination

| Item | Finish on cloud | Explicit remainder |
|---|---|---|
| B01, B02, B03 | Repair and reproduce the older-path source/geometry/clock failures in A | New independent acceptance only if later authorized |
| B04 | Reconcile live documentation, preserve old v5/v7 RED and bounded v8 GREEN | No rewriting historical decisions |
| B05 | Implement and test dependence-aware analysis on predeclared analytic data in C | Adequate exchanging molecular data and later review |
| B06 | Relative result representation, complete obligation templates and covariance checks in C/D | Actual sampled releases/bridges and physical domain decisions |
| B07 | Freeze remaining-reference inventory, feasibility/budget calculation and guarded run plan in E | Missing QM, failed physical limits and any new scientific decision |
| B08 | Prepare reproducible solvent input/recipe and validation in D | Intended liquid density/equilibration/stability and ensemble qualification |
| B09 | Map each original G09/G10/M05 assertion to exact evidence or a specific hold in E | Physical/statistical dependencies and independent combined review |
| B10 | Common collections/general manifest code and small force tests in B | Broader chemistry or physical support is not inferred |
| B11 | Protein manifest importer/validator and matched-control harness in D; actual target when supplied | Missing reviewed target decisions, larger execution, physical assessment and sampling |
| B12 | Preferred host–guest RBFE development input and deterministic checks in D | Independent chemical/input qualification; no affinity claim |
| B13 | Analytic identity/reversal/covariance tests in C; matched molecular run definitions in D | Independently initialized adequately sampled molecular reversal/closure |
| B14 | Portable profile checker and guarded cluster-trial scripts in E | Actual cluster storage/device/parity/checkpoint trial |
| B15 | Local packaging/offline checks/support matrix/small CPU measurements in E | Independent reproduction, physical gates and any claimed GPU/hardware evidence |
| B16 | Thin multistate/analysis CLI and reusable check command in E | Optimization only after measurements and a separate decision |

## Checks: spend effort once where it matters

Retained baseline: v8 reported **631 CPU passes, zero skips, 1238.59 s**; the one-pass review verified byte applicability and ran **31 selected tests, zero skips**, plus the three small defect reproductions and arithmetic controls. Those results are prior evidence, not passes on the newly modified branch. Do not rerun the baseline before coding, reinstall an identical environment, repeat the clock arithmetic proof or regenerate unchanged chemical references.

- [ ] For each behavior change, establish a small independent expected answer/failure, implement, and run the packet's affected tests. Documentation-only edits need links/whitespace checks. Preserve first failures; normal coder fixes are authorized, repeated independent repair/audit rounds are not.
- [ ] After A–E, freeze code/assets/locks, record the final source identity, and run **one** consolidated `python -m pytest -q` on the admitted CPU profile. Real source changes justify this run. The CPU suite must contain only bounded tests; any new HPC/QM/large-sampling runner stays outside default pytest. Record omissions explicitly. Do not also rerun the four compatibility files separately if the suite includes them.
- [ ] Run `python tools/check_docs.py --self-test` and `git diff --check` once on the final documentation. Check the installed package/offline bundle in E; import/help success is not numerical validation.
- [ ] If consolidated checks fail, retain the failure and return the exact affected problem to its owning worker. Rerun the failed/affected tests. Repeat the complete suite only when the subsequent fix warrants it; never hide a failure or call an earlier pass the final result.
- [ ] Commit only intended code/tests/docs and small evidence. Large run artifacts stay in identified local directories with manifests. The final report names code commits/tree hashes and any documentation-only commits made afterward.

## Five failure classes the packets must cover

1. Hash-consistent but inconsistent restart artifacts must reject before executable loading/steps (A).
2. Multiple caps and nonidentity indexing must give every real parent's derivative at both maps, without double projection (B).
3. Exchanging walkers must not acquire independent-sample uncertainty from per-walker thinning or resampling labels apart from energies (C).
4. Missing chemistry decisions, full-map clearance or thermodynamic corrections must remain visible and block the affected result (C/D).
5. An installed/offline package must preserve exact assets and evidence limits; a short CPU timing cannot qualify other hardware or a release milestone (E).

These are implementation checks, not instructions to conduct an audit.

## End-of-chat report and stop

Create `Worker_Log/Before_HPC/Before_HPC_vN_summary.md` with: base and final branch/commits; A–E complete/partial/blocked; actual test counts/failures/skips; new interfaces and fixtures; accepted evidence reused with unchanged scope; resource measurements; remaining user/input/physical/HPC obligations. State explicitly that **no independent audit occurred**.

Separate the remaining list into: (1) unresolved code/definition/input blockers, (2) deferred scientific calculations, (3) actual cluster qualification, (4) optional later performance work. Give the smallest next action and resources for each. Do not say “all development complete” if a cloud task is still blocked.

**Then report to the user and wait.** Do not start an audit, dispatch a reviewer, close milestones, push, run QM, submit cluster jobs or begin another work campaign.
