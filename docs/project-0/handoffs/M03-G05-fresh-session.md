# Fresh-session handoff: continue G05 on the existing branch

The user requested a stop on 2026-10-03 and a fresh session on the **same
branch, `m03-reference-g05`** in https://github.com/georgpou/AToM_MLMM.
Reuse `/workspace/AToM_MLMM-m03-reference-g05` if present. Fetch and inspect the
published child; preserve unrelated local changes. Do not copy this work to a
new development branch merely to restart context. Publish only this child;
leave main and the three accepted predecessor branches unchanged.

The checkpoint commit containing this file descends from published
`0935fd1213813e388a5dcc7e689998e907111e13`. Its scientific source is unchanged
from the independently reviewed `3124c6d275bf19a32ce364dfdb83b11115828ac5`.
The accepted G04 predecessor is
`bc788aeeedb4dc45026ac1bff44bd4fb533b325a`. Read [STATUS](../STATUS.md),
[G05](../gates/G05-local-model-adapter.md), this handoff and the relevant
[exact reference plan](../reference/M00-neutral-reference-plan-v3.md).
Historical audits need not be replayed for onboarding.

## Actual acceptance and remaining scope

**Full G05 is pending.** No model-versus-quantum comparison has run. The user
stopped the assignment during reference generation; the pause does not imply
chemical acceptance. Continue G05 first. G06/G07 are later dependencies; M03
closes at G07. Protein binding, periodic, GPU, electrostatic embedding and the
complete ABFE/RBFE workflow remain unqualified.

| Review | Exact snapshot | Actual decision |
|---|---|---|
| [M00 v3](../../../Worker_Log/Milestone_00/Milestone_00_v3_audit.md) | `a825f5f1c2d8cf4146133c2049ef1c4eca550e93` | Astra/high/fresh accepted design; 965 geometry and 131 provenance checks |
| [G05 v1 software](../../../Worker_Log/Milestone_03/Gate_05_v1_audit.md) | `a7768e375476667139db374dc0091999263a37de` | G00-T2 and six G05 software assertions accepted; importer R1 required repair |
| [G05 v2 repair](../../../Worker_Log/Milestone_03/Gate_05_v2_audit.md) | `3124c6d275bf19a32ce364dfdb83b11115828ac5` | R1 closed; prepared-loading readiness accepted; no chemical/full-gate verdict |

The first software reviewer was interrupted by the quota pause and supplied
no verdict; its saved evidence remains historical. Actual fresh-context
gpt-6-astra/high reviews above supply the scoped decisions. The repair binds
embedded approval to the actual input-manifest SHA and an exact review commit
before reading records. Its synthetic tests are software evidence only.

Last recorded source-suite result: **292 passed, two failures for absent full
quantum references**; analytic **272 passed, 22 deselected**. Inherited
G02/G03/admission/G04 checks passed **78/38/74/24**, strict environment **9/9**,
upstream **1**. These are earlier saved runs, not new runs at this pause.
The checkpoint verifies **270 source/input hashes**, all **46 frozen-plan
file hashes**, the **105-package reference lock**, and the eight saved records.
See [v3 worker](../../../Worker_Log/Milestone_03/Gate_05_v3_worker.md) and
[checkpoint evidence](../../../Worker_Log/Milestone_00/evidence/M00_reference_v3/README.md).

## Approved scientific choices

The user explicitly approved the exact plan, limits and compute budget before
the target batch. The [approved decision](../../../Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-approved-20261003.json)
contains the actual statement and exact reviewed manifest/audit digests.
Authorization persists; do not ask again for these same choices. The old
`decision-pending.json` and proposal's pending-language are historical.

The queue has 34 neutral-singlet C/H/N/O targets: capped ethanol and n-butane
conformers, complete methanol and acetamide configurations, and four joint
contact/separated families. Ten rotated monomers and two finer-grid rows are
mandatory numerical controls. Restricted omega-B97M-D3(BJ)/def2-TZVPPD uses
Psi4 1.10.2/LibXC 7.0.0, exact basis hashes and settings in
`fixtures/chemical_reference_v3/`. The approved cap is **12 wall-hours,
two threads and 5 GiB Psi4 memory**. Account for previous attempt time when
resuming; do not silently reset the whole compute budget for every retry.

Preserve conformer energy RMS/max limits **1/2 kcal/mol**, contact limits
**0.5/1 kcal/mol**, raw/projected per-structure force RMS/max-vector
**0.05/0.15 eV/angstrom**, net ligand force maximum **0.05 eV/angstrom**,
and the declared attraction/repulsion sign checks. Numerical controls use
**0.02 kcal/mol**, force RMS/max-vector **0.002/0.005 eV/angstrom**.
Do not omit rows, tune thresholds or replace physics after seeing scores.
Missing, nonfinite, unconverged or out-of-limit evidence blocks the proposed
profile. The named training-reference level does not establish identical
training numerics or that inputs were absent from training.

## Saved calculations and the interruption

Original evidence is in
`Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v1/`.
Preserve it; do not overwrite any records, orders or logs. [Stop state](../../../Worker_Log/Milestone_00/evidence/M00_reference_v3/stop-state-20261003.json)
lists all 38 remaining names and the eight completed SHA-256 values.

| Saved target | Wall time |
|---|---:|
| `acetamide--20` | 109.3 s |
| `acetamide-0` | 101.5 s |
| `acetamide-20` | 101.2 s |
| `butane--60` | 242.7 s |
| `butane-120` | 231.8 s |
| `butane-180` | 231.8 s |
| `butane-60` | 218.3 s |
| `butane-acetamide-d3.4-r0` | 695.5 s |

All eight contain finite energy/full-gradient arrays, exact coordinates,
settings/input/basis hashes and a worker completion receipt. Their summed
worker wall time is **1932.0 s (32.2 min)**, excluding coordinator/setup time.
Only seven coordinator exit-zero receipts were observed. The eighth record
appeared during/after connection recovery and its Psi4 log finished at
10:50:02 UTC; no eighth coordinator exit receipt was received.

Remaining: four ethanol plus three methanol isolated targets, **19 contacts**
(four butane/acetamide and five each of the other three families), **ten
rotations**, and **two finer-grid calculations**. Total **38**, including
26 chemical targets. No current quantum process was visible at the checkpoint.
There is **no coordinator `manifest.json`** and no complete bundle in
`fixtures/chemical_reference_v3/quantum/`.

Execution session `34246` lost its transport; recovery timed out after 25 s.
The connection failure is confirmed, but its cause is unknown. The final
calculation did save its output; a failed SCF or OOM kill has not been shown.
[Interruption record](../../../Worker_Log/Milestone_00/evidence/M00_reference_v3/interruption.json)
preserves the error and the distinction between worker completion and missing
coordinator progress.

## Cloud resources and recovery requirements

At the final check the workspace had **14.28 GiB free**. The saved attempt is
about **0.40 MiB** after scratch cleanup. Storage is adequate for these small
saved records; monitor transient quantum scratch during the resumed run.

The authoritative cgroup RAM cap is **8.0 GiB**, with about **1.3 GiB** in use
at checkpoint verification and **no swap**. Its lifetime high-water reached
the cap and `memory.events` reports many cap hits, but **zero OOM/OOM-kill
events**. The peak has no job timestamp or culprit, so it does not prove the
last calculation caused the interruption. Psi4's 5 GiB setting is an internal
allocation budget, not a total process-RSS limit. Native/Python overhead,
cache and the executor also consume RAM. Memory pressure and an independent
transport/infrastructure interruption are possible explanations.

Treat the current allocation as requiring more headroom before the next
larger/finer-grid job. Evaluate a smaller runtime allocation within the
approved upper cap, retain one quantum worker, and capture job-specific
RSS/cgroup peaks. Record actual runtime allocations honestly; do not edit
the frozen scientific manifest/settings or pretend an untested allocation is
already validated. A larger RAM environment is an alternative if measured
peaks require it. No lower-memory run has been implemented or tested here.

The current `tools/generate_neutral_quantum.py` **has no resume mode**, insists
on a new output directory and writes the coordinator manifest only at the
end. Blindly rerunning it would repeat completed work. Implement, test and
review a recovery path that verifies/reuses the eight exact completed
records, schedules the remaining 38, preserves all attempt histories, records
durable progress and enforces the remaining budget. Do not invent missing
exit receipts or set readiness true for the partial attempt.

## Environments and next actions

Activate `/workspace/atom-mlmm-g05-v2/activate.sh` in every scientific shell.
Reference Python is
`/workspace/atom-mlmm-reference-pilot-v2/env/bin/python`; Amber stays in its
separate NumPy 1.26 environment. If prefixes are absent in a new cloud machine,
use the maintained locked installers/bundles and verify hashes, rather than
assuming the old paths exist. Do not reinstall working prefixes unnecessarily.

1. Inspect the same branch, recorded approval, saved records and current
   resources. Recheck that no old worker is active before restarting.
2. Resolve resume/durable-progress and RAM headroom as described above;
   complete the remaining quantum-only queue within authorized resources.
3. Validate every reference and numerical control before creating the complete
   hashed bundle under `fixtures/chemical_reference_v3/quantum/`.
4. Run both `tests/integration/test_chemical_reference.py` checks. Preserve
   every row/error, signs, within-composition energy zeros and independent
   cap-Jacobian/full-parent and ligand-force metrics. Report actual failures.
5. Run applicable source/environment checks, then obtain an actual
   **gpt-6-astra/high/fresh** full-G05 review on an immutable source/data
   snapshot. Reviewers perform no implementation. Record exact scope and
   publish only the child. The current assignment stops at accepted G05.

Preserve the pinned MACE-OFF23-small SHA
`165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`,
licence guards, lazy/scoped trusted loading, CPU float64/Default head and
total `energy`. ASE factors are 96.48533288249877 kJ/mol per eV and
964.8533288249877 kJ/mol/nm per eV/angstrom. Preserve fixed ML membership,
the same Hamiltonian at both maps, complete mobile ligands, full real forces,
both cap-parent derivatives and the retained-MM ledger. Native nested cap
redistribution works; do not add a second manual projection. A contacting
pair requires one joint graph. Metadata remains distinct from chemical
qualification; do not flip it to qualified merely because software passed.

For later G07, reuse the corrected score-free threonine parent orientation,
20 frozen joint rows and 50 cut descriptions. Actual GAFF 2.2.20/AM1-BCC
charges, XML and retained/removed ledger still need freezing before G07-T4.
Keep identical-input model error separate from capped-versus-uncut quantum
and retained-MM changes. G06 must qualify periodic conventions before any
periodic G07 claim. These are future tasks, not completed evidence.
