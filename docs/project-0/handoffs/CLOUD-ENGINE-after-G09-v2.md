# Cloud engine pause and continuation

**Drafted:** 2026-10-04 UTC. **Finalized:** 2026-10-05 UTC.\
**Branch:** `m04-engine-readiness`.
The user requested a graceful stop near the session limit. Resume from this
existing branch when the limit is restored; preserve main and the published
`m03-g06-g07` predecessor. No new feature or simulation should start merely to
complete this handoff.

The engine runs a small host–guest example and two smaller mixed ML/MM controls
through one settings-driven workflow. Mathematical checks, energy/force records,
short trajectories, restart and failed-state preservation have been checked.
Solvent, exchange and accurate molecular binding predictions remain future work.

## Current checkpoint

G08 and combined M04 are independently accepted for analytic CPU thermodynamic
accounting; [G08 v2 audit](../../../Worker_Log/Milestone_04/Gate_08_v2_audit.md)
is the authority. The common cloud runner now covers preparation, sealed actual
AToM worker export, fixed-window sampling, full real-force records, reduced-
potential reconstruction and checkpoint continuation for these examples:

| System | Real atoms | Role |
|---|---:|---|
| 18-crown-6 + methanol | 48 | Neutral all-ML host–guest in vacuum |
| Capped-fragment ABFE | 32 | Mixed ML/MM and cap-force control |
| Capped-fragment RBFE | 41 | Unequal complete-ligand control |

The [v1 audit](../../../Worker_Log/Milestone_05/Gate_09_v1_audit.md) accepted the
bounded host/vacuum design and found G09-R1: integration exceptions could bypass
failed-state archiving. Tested repair source is
`3246f0cbd6f66702e4b196bace593efba776a25e`; frozen submission is
`9fe93357f0852d7c018ab41923cc0d58cb0615e1`. The
[v2 worker](../../../Worker_Log/Milestone_05/Gate_09_v2_worker.md) and
[actual GPT-6.1-sol/MAX v2 audit](../../../Worker_Log/Milestone_05/Gate_09_v2_audit.md)
record **accepted_for_scope, G09-R1 closed**: nine fresh affected passes and six
independent actual-worker prefix/failure challenges. Their submitted artifacts
and earlier attempts are frozen; subsequent reports/publication change no
tested source.

Root verification: **461 CPU tests passed, no skips**, in 399.38 s; five affected
checks passed. The frozen v1 host pilot saved **60 frames/300 integration steps**,
with finite coordinates, velocities and all 48 forces, both map guards passing,
and peak process RSS about **0.94 GiB**. A fresh v2 CLI smoke saved nine frames/
18 steps with unchanged physical/alchemical identities. These short trajectories
establish bounded execution checks, not equilibrium or molecular accuracy.
No binding estimate or new QM calculation was produced.

## Environment and saved attempts

Use `/workspace/AToM_MLMM` and the unchanged locked environment:

```bash
source /workspace/atom-mlmm-g08-r2/activate.sh
export OPENBLAS_NUM_THREADS=2
export PYTHONPATH="$PWD/src"
python -m atm_mlmm check fixtures/cloud_host_guest/v2/config.json
```

The [runner guide](../../../examples/cloud_engine/README.md) explains settings,
new output directories, trusted loading and relocation. Full local portable
attempts are `/workspace/cloud-engine-pilots/host-v1` and `host-v2` under the same
parent directory. Tracked [v1 evidence](../../../Worker_Log/Milestone_05/evidence/G09_v1/README.md)
and [v2 evidence](../../../Worker_Log/Milestone_05/evidence/G09_v2/README.md)
include raw records, States/checkpoints and manifests; their captures omit
duplicate source/model/environment payloads and are not standalone installations.
Checkpoint comparisons must use the exact same saved System/State and seed;
independent minimizations can differ at floating-point roundoff before sampling.
Serialize scientific jobs on the two-CPU/8-GiB/no-swap cloud machine.

## Remaining work after resumption

Read [STATUS](../STATUS.md), the runner guide and v2 audit before making changes.
Retain this small-system baseline while adding explicitly specified solvent
coupling and actual exchange coverage in subsequent unused attempts. Full
G09/G10/M05, implicit solvent, solvated PME, GPU, equilibrium and affinity
qualification remain open. MACE training coverage and precision for the
host–guest example are unqualified; the user's priority is a reusable engine
that accepts systems and settings cleanly.

T4 lysozyme L99A remains the later HPC target. Wait for the user to initiate
cluster work and provide Slurm settings; do not ask for them during cloud work.
G07/M03 physical blockers remain: seven sensitivity exceedances and 29 missing
new quantum references. Preserve all 46 G05 records, existing force failures
and the unchanged cumulative QM ledger (2325.644650052 / 86400 seconds).
This technical checkpoint does not authorize further QM or production runs.
