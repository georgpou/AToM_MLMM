# Fresh-agent continuation from the G06/G07 branch

**Superseded operational handoff.** Use the
[engine-readiness handoff](ENGINE-READINESS-fresh-agent-v1.md), which includes the
completed G07 pilot, current environment paths, cleanup outcome and already
prepared `m04-engine-readiness` branch. The older branch/worktree instructions,
30-missing count and activation prefix below describe the earlier snapshot.

**Prepared:** 2026-10-04, UTC.\
**Published predecessor:** `m03-g06-g07` in `georgpou/AToM_MLMM`. Use the exact final published commit reported with this handoff.\
**Reviewed submission:** `ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b`; implementation/source `c584086da68654b07f1a477d7ce1e48da42a9838`; accepted G05 ancestor `08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`.

## Assignment and lineage

Create a new child branch from the published predecessor and proceed with M04/G08 analytic thermodynamics and estimators. Do not start from main or the older G05 branch. Preserve the predecessor and existing user changes; do not merge, reset, rebase or force-push it.

From an existing clone, fetch the predecessor and use a new worktree if the current checkout belongs to another task:

```bash
git fetch origin m03-g06-g07
git rev-parse origin/m03-g06-g07
git worktree add -b m04-g08-thermodynamics ../AToM_MLMM-m04-g08 origin/m03-g06-g07
cd ../AToM_MLMM-m04-g08
git merge-base --is-ancestor ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b HEAD
```

Check that the fetched SHA matches the exact publication SHA in the user's handoff message before proceeding. If either proposed worktree/branch name already exists, use an unused suffix; preserve the existing work. An already isolated, clean checkout may use `git switch -c m04-g08-thermodynamics origin/m03-g06-g07` instead.

## Required reading and audit disposition

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md), [G08](../gates/G08-thermodynamics-and-estimators.md), and the relevant [S05](../specs/S05-protocol-and-thermodynamic-contracts.md), [S06](../specs/S06-validation-and-tolerances.md), and [S03](../specs/S03-data-and-interface-contracts.md) sections. Read the [CPU guide](../../../environment/cloud-cpu/README.md) and [development guide](../../DEVELOPMENT.md) for environment and commands. Existing schedule, schema, native ATM and AToM adapter records are starting points, not proof that G08 is already implemented.

The independent **GPT-6.1-sol/MAX** audit is complete on the exact reviewed submission above. [G06](../../../Worker_Log/Milestone_03/Gate_06_v1_audit.md) accepts all six numerical assertions; [G07/M03](../../../Worker_Log/Milestone_03/Gate_07_v1_audit.md) accepts G07-T1/T2/T3 and its seven numerical assertions separately. No mathematical/coding defect requiring repair was found in the admitted small-system **OpenMM Reference double / MACE CPU float64** single-point profile. This does not qualify OpenMM CPU PME precision, GPU, dynamics or protein/binding accuracy. Independent results were 381 full-suite passes, 45 focused passes, 9/9 environment checks, 24 added periodic route comparisons and five added force sweeps. All 1,924 initially tracked files stayed byte-identical during the audit.

**G07-T4/G07-08/09 and combined M03 physical acceptance remain blocked:** seven of 40 comparisons among MACE-based descriptions exceed the unchanged 0.05 eV/angstrom project limit (maximum 0.12165016265111903), and 30 new quantum references are absent. These are not measured full-QM-versus-ML/MM errors; both the model region and retained MM contribute. Keep the known findings and every control. The auditor explicitly confirms M04/G08 can independently proceed. This review supersedes the earlier deferred-audit statement in the [2026-10-03 interpretation note](M04-after-M03-numerical-handoff-v1.md).

G08 explicitly allows development alongside G04-G07 once G02/G03 pass. Its prerequisites are accepted M02 analytic CPU work. M03 physical acceptance must not be inferred from this permission; G09/M05 and later molecular claims retain their own prerequisites. Do not run a new reference pilot or batch without the separate reference budget. The old G05 budget is not an authorization for G07's thirty new reference jobs.

## Work to complete

Implement G08-T1/T2/T3, following its six stable assertions and reviewed definitions:

1. Independently integrate the specified harmonic problem and generate independent analytic samples. Check the entire lambda curve, `F1-F0 = +1.5 kJ/mol`, reversed `-1.5`, and zero-restraint `0`. The specified constants are `k=100`, `kr=50 kJ/mol/nm^2`, and `d=0.3 nm`; use the S05 exact formula, not a newly fitted target.
2. Make endpoint meanings, observable weights, signs and correction obligations explicit. A missing required translation/orientation/release/state-counting correction must prevent a final standard binding result. A documented zero needs evidence.
3. Reconstruct dimensionless reduced potentials from actual raw endpoint, softened and outside energies for every state; compare selected rows against actual OpenMM contexts, including direction, offsets and active soft-core/softplus settings. Keep upstream unit/key conventions within the existing adapter boundary.
4. Deliberately make the directional midpoints differ. Check that the required bridge restores the known result with the S05 sign. Equal lambda labels or a shared restraint name do not demonstrate equal states or cancellation.
5. Implement and independently check the finite-wall translational integral, zero-radius harmonic and hard-wall limits, and the standard-state sign. Keep orientation/pose/symmetry assumptions explicit.
6. Run the pinned PyMBAR and AToM Python UWHAM analyses on the same mathematical states/data. Check solver agreement, energy offsets, covariance and uncertainty. Only after deterministic checks and independent analytic sampling pass, use short CPU MD samples with repeated seeds, correlation, overlap and effective-contribution diagnostics.

Use planned modules under `src/atm_mlmm/`, including `restraints.py`, `schedule.py`, and `analysis.py`, and planned tests `tests/unit/test_schedule.py`, `tests/unit/test_restraint_volume.py`, and `tests/sampling/test_analytic_free_energy.py`. Preserve shared physical-builder/protocol/adapter boundaries and fixed ML membership. Keep scientific definitions and limits unchanged. A new dependency or scientific definition requires explicit provenance and appropriate validation, rather than replacing the pinned implementations.

## Verification and resource limits

In this existing workspace activate `/workspace/atom-mlmm-g05-v2/activate.sh` in every scientific shell. On a fresh machine install the unchanged locked CPU profile following the guide and activate its actual prefix. Keep main NumPy 2 and AmberTools NumPy 1.26 separate; do not install or use a quantum reference backend for G08.

Use failing focused tests before implementing behavior, independent quadrature/probes and meaningful faults. After implementation run all required G08 checks and the available full CPU suite:

```bash
python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v
python -m pytest -q
python tools/check_docs.py --self-test
git diff --check
```

Analytic sampled free energy must satisfy both within three reported standard errors and an absolute error of at most 0.1 kJ/mol after adequate sampling. Use the S06 deterministic/solver limits. Increasing an error bar, skipping a required assertion, or silently changing a tolerance is not acceptance.

The current machine has about 8 GiB RAM, no swap and two CPU quota. Serialize heavy OpenMM/model jobs and retain two-thread limits. Do not run long MD, new QM, GPU, protein binding or G09 automatically. Preserve the 46 accepted G05 records, frozen model/checkpoint, earlier audit evidence, physical cuts/settings and all sensitivity rows. G08 does not require changing them.

## Required delivery

Use an unused attempt under `Worker_Log/Milestone_04/Gate_08_vN_worker.md`, with exact base/source/result commits, environment identity, commands/results, deterministic and sampling evidence, uncertainty/support diagnostics, correction status, scope limits and next action. Update STATUS with actual results. Commit only this new branch and hand over the exact snapshot.

The user's reviewer choice is **GPT-6.1-sol/MAX**. Prepare the completed G08 submission for its required combined G08/M04 independent review on the same snapshot; successful worker tests alone do not close the milestone. Do not repeat the accepted G06/G07 numerical audit unless a new relevant change or failure justifies reopening it.
