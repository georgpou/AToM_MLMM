# G09 bounded explicit-water controls — v3 audit

**Reviewed worker:** [Gate_09_v3_worker.md](Gate_09_v3_worker.md).\
**Snapshot:** branch `m04-engine-readiness`, exact HEAD `b11c16750ad111a2fcafcda7a2d51c6690254e97`, against base `8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1`; tested implementation `5645db24f707adbdaff34dc7de6ac04b518d7d6b`. The submission's additional commit contains reports/status/evidence only.\
**Scope/profile:** G09-T1/T2/T3 technical subsets for sparse rigid TIP3P ABFE/RBFE controls (56/65 real atoms), orthorhombic PME, preparation/export, live State/restart, full real-force/raw records and failure preservation. Reference double, pinned MACE CPU float64, NVT 300 K, 0.0005 ps, two CPUs.\
**Reviewer:** independent `gpt-6.1-sol`, MAX dispatch setting; no delegated reviewers.\
**Finished:** 2026-10-05T10:45:16+00:00.\
**Verdict:** **changes_required** — one Important finding, G09-R2.

## Evidence

Reviewed AGENTS, the two current worker logs, current STATUS, the implementation plan, [proposed amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md), G09-T1/T2/T3 and G10-T2, and applicable S04/S05/S06/S07 contracts. Inspected the source diff and relevant geometry, physical builder/ledger, force routing, preparation, actual worker, State/checkpoint and observable code. No unrelated historical audits were used.

All scientific commands ran serially from `/workspace/AToM_MLMM` after `source /workspace/atom-mlmm-g09-v3/activate.sh`, with `OPENBLAS_NUM_THREADS=2` and `PYTHONPATH=/workspace/AToM_MLMM/src`. [Independent evidence and exact probes](evidence/cloud_v3_independent/README.md) retain commands, outcomes and the failing artifact/CLI capture.

| Independent command/check | Actual result |
|---|---|
| `python -m pytest -q tests/workflow/test_solvated_handover.py tests/workflow/test_replica_exchange.py tests/workflow/test_failure_geometries.py --basetemp=/tmp/atom-mlmm-cloud-independent-affected` | Exit 0; **28 passed in 92.83 s**, no skips |
| `python -m pytest -q Worker_Log/Milestone_05/evidence/cloud_v3_independent/probes.py --basetemp=/tmp/atom-mlmm-cloud-independent-final` | Exit 1; **7 passed, 1 failed in 5.72 s**. The sole failure is the expected original-error preservation contract reproducing G09-R2. One overflow warning comes from the deliberate finite-input/nonfinite-energy challenge. |
| `python Worker_Log/Milestone_05/evidence/cloud_v3_independent/verify_manifests.py` | Exit 0; 48 scientific source/input hashes match HEAD and the tested implementation; 114 G09 and 11 G10 capture hashes match; both complete local portable workers have 48 matching payload files |
| Submitted CLI captures and reconstructed records | Nine frames per control, finite 56/65-real-atom force arrays, 6.4 nm boxes, 3-by-9 potential matrices; captured exchange matrices/exponents agree with their separate raw records |

The worker's **489 passed in 481.86 s** full CPU result is submitted evidence, not an independently repeated full suite. Earlier M03/M04 scientific evidence, chemical-reference inputs, model assets and environment paths have no diff against the base; the G07 physical failures and QM ledger remain unchanged. No installation, QM, GPU or long production job ran.

Deliberate review checks covered each requested risk:

- Periodic ligand/static-solute, cap and other-ligand distances use minimum images for both maps; every molecule pair is checked for real-atom clashes. An independently enumerated 27-image oracle agrees with both controls' preliminary PDB geometry and bulk-clearance diagnostics, and independently confirms PDB box units.
- Solvent stays outside fixed ML membership; inherited particles/exceptions and 24 rigid-water constraints are preserved. Actual retained-MM/native-model force oracles, ligand charge/LJ masking at both maps and solvent O/H derivative step sweeps pass unchanged S06 limits. Recursive routing and all-active preparation preserve each physical force once.
- Exact worker State positions/velocities/parameters and constraints pass reload checks. An additional deliberately changed live Context cell is extracted exactly and survives checkpoint and portable-State restoration with coordinates, velocities and parameters unchanged. This diagnostic injection does not qualify a new variable-cell profile.
- Fresh full-context exchange potentials, original-assignment refreshes and fixed walker labels are independently covered by the matching [G10 audit](Gate_10_v1_audit.md).
- Actual nonfinite child output and unadmitted outside-force mutations reject before a decision; all eight exchange evaluation stages propagate injected errors. Ordinary integration/final-State failures and nonfinite coordinate States retain both maps without energy/force reentry or sample insertion. A mapped-artifact write failure exposes G09-R2.

## Findings

| Finding and importance | Evidence/location | Required repair and closure check |
|---|---|---|
| **G09-R2 — Important: an archival error hides the original scientific error in the normal CLI.** | `src/atm_mlmm/workflow.py:315` writes cached State, checkpoint and both map files before `error.json`. Failure at `_archive_map_states` (`workflow.py:326`, map write at `:268`) replaces the primary `NumericalDomainError` with `OSError`. Python retains exception chaining, but `src/atm_mlmm/__main__.py:30` prints only the final exception. The exact probe injects an actual one-step worker failure and then a `map1-state.xml` write failure. CLI exit is 2 and stderr is only `OSError: independent mapped State archive trigger`; original-error metadata is absent. State/checkpoint/map0 survive; no failed sample is inserted. See [capture](evidence/cloud_v3_independent/archive-failure/cli-characterization.json) and [RED probe](evidence/cloud_v3_independent/probes.log). | Preserve and surface the original failure even when any archive operation fails; record secondary archive errors explicitly and retain every artifact that can safely be saved, without evaluation reentry. Write primary error metadata before supplementary maps where possible. Add a regression for the demonstrated map-write failure and the equivalent cached-State/checkpoint failure boundaries. Closure requires the CLI to expose the original scientific error and the archive failure, primary metadata whenever writable, preserved available artifacts and no sample insertion/reentry. Rerun affected checks on a new frozen repair snapshot. |

No Critical or other Important/Minor findings were identified. The defect concerns failure diagnosis and retained scientific evidence; successful Hamiltonian/force/exchange numerical results remain valid.

## Amendment decision and handoff

**Accept the amendment's scientific definition for these bounded controls:** eight classical rigid TIP3P waters, the declared unchanged PME/dispersion ledger, fixed complete-ligand maps and minimum-image harmonic periodic static anchors away from half-box seams. The independent anchor energy/force image oracle passes; vacuum anchors retain their definition. Sparse controls and comparison against the exported high-precision State are justified, with exact State parity and independent physical/image checks. Frozen source and asset identities prevent silent migration of prior attempts.

**Do not accept the amendment's failure-preservation implementation or the full submitted G09 subset until G09-R2 closes.** G09-R1 remains closed. Repair R2 with a regression and obtain closure review on the new snapshot; preserve these submitted logs and artifacts. STATUS is left unchanged under the review-only assignment.

This audit declines to judge homogeneous liquid/density equilibration, equilibrium or affinity, molecular/MLIP physical accuracy or model coverage, broad periodic restraint excursions/half-box seams, state-dependent outside-force models, implicit solvent, pressure/virial, GPU, new solvated offline/cache-removal qualification, persistent exchange/RNG/history supervision or exchanging-walker statistics. It closes neither full G09/G10 nor M05; G07 physical blockers and the 2325.644650052/86400-second QM ledger remain unchanged.
