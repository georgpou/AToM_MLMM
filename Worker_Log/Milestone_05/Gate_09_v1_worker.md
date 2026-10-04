# G09/G10 cloud technical subsets — v1 worker

**Scope:** G09-T2/T3 vacuum analogues and G10-T1/T3 checkpoint/State/offline/journal
subsets; Reference double NVT, pinned MACE CPU float64.\
**Outcome:** ready_for_audit for these subsets; full G09/G10/M05 remain partial.\
**Finished:** 2026-10-04 16:43 UTC.\
**Snapshot:** `m04-engine-readiness`; accepted G08/report base
`8692138bac7d7324ac4d2ef13bfb58075b874202`; tested source/input/test commit
`34cc6ba0d3e618450128b4a679ffc64046c48733`. Submission adds reports/evidence/STATUS
only. Actual independent reviewer remains the user-requested GPT-6.1-sol/MAX.

## Changes

The user approves a tiny host–guest cloud system and prioritizes engine
correctness/easy system settings over current MLIP precision. T4 lysozyme L99A
and all Slurm questions are deferred to HPC. The
[amendment](../../docs/project-0/specs/G09-cloud-preflight-v1.md) proposes a neutral
complete static `host` role and scoped workflow admission; review is pending.

One [configuration/CLI](../../examples/cloud_engine/README.md) now runs 48-atom
18-crown-6/methanol (all ML, inert original MM, vacuum), inherited 32-atom capped
ABFE, and 41-atom capped unequal-ligand RBFE. Inputs, model and settings are
explicit and hashed. Preparation preserves physical identity/all-active forces
through bounded minimization and declared temperature phases. Seeds precede
Context initialization. Actual pinned OMMWorkerATMSync construction loads sealed
PDB/System/State, avoiding duplicate assembly and hidden zero-LJ repair. Energy
and every real force must match before stepping.

The pilot stores complete raw energy names, parameters/direction, positions,
velocities, full real forces and explicit sample/walker/state/sequence/time IDs.
Both complete maps use unchanged distance guards. Shared reconstruction is
checked against independent native evaluations at every state in tests. Each
immutable hash-bound journal chunk includes a State/checkpoint; same-profile RNG
continuation, portable-State observables and completed-prefix verification are
distinct checks. Fresh offline workers use bundled source/model/environment
files with original checkout/run/caches and networking denied.

Preserved failures include the rejected v1 host clash (0.02649224 nm), the first
test's unintended W0/UOffset defaults, seed assignment after Context creation,
raw total-field naming, and failure archiving that retriggered failed energy.
Each relevant defect has its failing check and repair evidence. V2 pose selection
uses full-host geometry only, with the same 0.65 Bondi threshold. A diagnostic
rerun captures both v1 mapped coordinates/full forces; it is explicitly a later
reproduction, not original raw output. One non-scientific artifact-copy helper
failed on an accidental placeholder import; its corrected copy succeeded without
changing source or results. No block currently needs user intervention.

## Verification

Commands ran from `/workspace/AToM_MLMM`, with scientific shells sourcing
`/workspace/atom-mlmm-g08-r2/activate.sh`, `OPENBLAS_NUM_THREADS=2`, `PYTHONPATH=src`.
Heavy scientific runs were serialized on the two-CPU/8-GiB/no-swap host.

| Check | Command/record | Actual outcome |
|---|---|---|
| Host/preparation RED and GREEN | New host-role/phases tests; [evidence](evidence/G09_v1/README.md) | Initial 3 failures/4 passes; affected checks 25 passes; seed reproducibility RED, then 16 affected passes in 6.15 s |
| Model/direct/native host parity | `pytest -q tests/workflow/test_cloud_host_guest.py` | 2 passes in 5.19 s, both endpoint energies and all 48 forces |
| Actual worker handover | `pytest -q tests/workflow/test_worker_handover.py` | Initial 2 missing-API failures; 2 passes in 0.60 s; checkpoint/State and cross-state checks later 6 passes in 17.92 s |
| Shared runner/restart | `pytest -q tests/workflow/test_engine_configuration.py tests/workflow/test_engine_restart.py` | RED missing APIs, then field-name failures; 4 passes in 43.27 s; interrupted/uninterrupted positions/velocities/raw/full forces exactly equal |
| Same capped ABFE/RBFE runner | Parametrized `test_same_runner_preserves_caps_and_multiple_complete_mobile_groups` | 2 passes in 16.92 s; full 32/41-force coverage, fixed cap/parents, whole mobile groups |
| Fresh relocated actual worker | `pytest -q tests/workflow/test_engine_fresh_process.py` | 1 pass in 20.69 s; child continues with network/original paths/caches denied |
| Failure retention | `test_failed_counterfactual_is_saved_without_retriggering_failed_energy` | RED 1 failure in 0.88 s; GREEN 1 pass in 0.56 s; original domain error and State/checkpoint survive |
| Initial full CPU suite | `python -m pytest -q --basetemp=/tmp/g09-root-full` | 0; 458 passes in 400.59 s |
| Final frozen full CPU suite | `python -m pytest -q --basetemp=/tmp/g09-final-root-full` | 0; **459 passes in 400.62 s**, no skips |
| Actual CLI pilot | `python -m atm_mlmm check /workspace/cloud-engine-pilots/host-config-v1.json`; `python -m atm_mlmm run /workspace/cloud-engine-pilots/host-config-v1.json --output /workspace/cloud-engine-pilots/host-v1 --trusted` | Both 0; **60 frames/300 worker steps**, 100 steps/0.05 ps per state, dt 0.0005 ps; complete 3x60 reconstruction |
| Docs/whitespace | `python tools/check_docs.py --self-test`; `git diff --check` | 0; no documentation errors/eight self-tests; clean diff |

The [pilot capture](evidence/G09_v1/host-pilot-diagnostics.json) preserves actual
observations, all States/checkpoints and sealed artifacts. All saved numerical
coordinates/velocities/forces are finite; minimum whole-map Bondi ratio is
**0.790349815** versus 0.65; minimum bulk/static clearance **2.539771094 nm**
versus 0.65. Largest absolute force component is **3153.237538 kJ/mol/nm**, not
a chemical force-accuracy result. Execution took **101.335 s**, preparation/
handover **10.897 s**, peak process RSS **987,168,768 bytes**. OOM/OOM-kill remain
zero. Full local attempt includes all exact bundled source/model/environment
files; tracked capture excludes duplicate payloads and identifies all hashes.

## Handoff

Audit the exact [110-file manifest](evidence/G09_v1/source-input-test-manifest.json),
amendment, construction path, raw records, checkpoint semantics and admission
faults. The worker log/evidence are frozen at submission; repairs require v2.
This does **not** accept solvent coupling (G09-T1), actual replica exchange
(G10-T2), GPU, hard-crash automatic repair, concurrent controllers, equilibrium,
standard binding corrections, molecular accuracy, protein preflight or combined
M05. No BindingResult/affinity is produced. G07/M03 physical failures, 29 missing
references and the cumulative quantum ledger remain unchanged; no QM ran.

After review, retain the common runner as the small cloud baseline. Solvent and
exchange need their explicit engineering/physics coverage before full M05;
physical/protein/HPC qualifications retain their earlier prerequisites. Do not
request Slurm details until the user starts cluster work.
