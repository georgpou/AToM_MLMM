# Cloud solvent and pair-exchange checkpoint

**Historical snapshot.** Use the [current engine continuation](CLOUD-ENGINE-CONTINUATION.md).
Dense local-water controls and persistent pair exchange described below as next
work have since been accepted for their bounded CPU scope.

**Finalized:** 2026-10-05 UTC. **Branch:** `m04-engine-readiness`.
Continue this branch with normal commits/pushes; preserve main and the published
`m03-g06-g07` predecessor. This completes the bounded implementation resumed
from [G09 v2](CLOUD-ENGINE-after-G09-v2.md), with serial scientific work/reviews.

## Reviewed outcome

The common runner now admits sparse rigid-TIP3P/orthorhombic-PME controls:
56 real atoms for capped ABFE and 65 for unequal-ligand RBFE. Complete ligands,
fixed ML membership, protein caps, inherited solute MM terms and all influencing
real forces are preserved. Both-map minimum-image guards include the complete
static solute, caps and other ligands. Live boxes survive worker export,
sampling, checkpoint and portable-State checks.

The adapter provides one actual-worker pair decision with four fresh full
cross-state potentials, the pinned AToM Metropolis routine, refreshed state
energies and fixed walker/configuration/velocity identities. The CLI runner
still samples fixed windows; persistent exchange scheduling is a later task.

Failure archives retain cached original/mapped States and checkpoint wherever
available, without energy/force reentry or failed sample insertion. Independent
review found G09-R2: an archive error could hide the original scientific error.
The repair preserves the exact original exception, writes primary provenance
first, attempts artifacts independently and surfaces secondary errors through
metadata and CLI exception notes. Existing failure directories are preserved.

| Snapshot/evidence | Recorded result |
|---|---|
| Solvent/exchange source `5645db24f707adbdaff34dc7de6ac04b518d7d6b`; v3 submission `b11c16750ad111a2fcafcda7a2d51c6690254e97` | 489 full CPU passes; both CLI controls save nine frames/18 sampling steps, six preparation steps, full forces/boxes; peak RSS below 0.85 GiB |
| Repair source `027f8173babc13606afb24d96f58148704e38b1b`; frozen review `09a85d979fe9fce2ceca23da74509846254df9b1` | 12 RED regressions, 19 affected passes, **501 full CPU passes in 498.74 s**, no skips |
| [G09 v4 audit](../../../Worker_Log/Milestone_05/Gate_09_v4_audit.md) | **21 independent focused passes/six probes**, 49 hashes matched; R1/R2 closed, bounded G09 subsets accepted |
| [G10 v1 audit](../../../Worker_Log/Milestone_05/Gate_10_v1_audit.md) carried forward by v4 | Single actual-worker pair scope accepted; full G10/M05 open |

The [scientific amendment](../specs/cloud-solvent-control-amendment.md) is accepted
for scope. Key rulings: sparse waters establish coupling/runtime only; worker
parity is exact against exported high-precision State after periodic
reconstruction; periodic static anchors use minimum-image harmonic distance
away from half-box seams, while vacuum anchors retain their definition. No
tolerance was relaxed. Old sealed bundles retain their own frozen source and
cannot silently migrate. No Minor review findings were deferred.

Final root verification matched all 49 source/input/regression hashes and 135
captured artifact hashes; documentation checks passed with zero errors/eight
self-tests. Changes after the frozen review are reporting/audit/evidence only.

## Environment and use

The replacement cloud machine rebuilt unchanged CPU/main and Amber locks at
`/workspace/atom-mlmm-g09-v3`; all nine setup checks passed. Activate in every
new shell, from `/workspace/AToM_MLMM`:

```bash
source /workspace/atom-mlmm-g09-v3/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python -m atm_mlmm check fixtures/solvated_fragment/v1/abfe/config.json
```

See the [runner guide](../../../examples/cloud_engine/README.md) for new outputs,
trusted runs/resume, both water configurations and the pair API. Serialize jobs
on the two-CPU/8-GiB/no-swap machine. Complete local v3 portable attempts are
`/workspace/cloud-engine-pilots/water-v3/abfe` and `rbfe`; they stay frozen and
source-bound. Tracked [v3](../../../Worker_Log/Milestone_05/evidence/G09_v3/README.md)
and [v4](../../../Worker_Log/Milestone_05/evidence/G09_v4/README.md) captures retain
raw records/failures/hashes; they omit duplicate source/model/environment
payloads and are not standalone installations.

## Next dependencies

Read [STATUS](../STATUS.md), the runner guide and current v4 audit. Design a
bounded dense-solvent preparation profile and persistent exchange/RNG/history
controller in new attempts, with explicit scientific contracts and independent
numerical/restart/failure evidence. Sparse water does not establish homogeneous
liquid, equilibrium, affinity or molecular/MLIP physical accuracy. Implicit
solvent, GPU, broad periodic restraint excursions, general state-dependent
outside terms, solvated offline/process qualification and exchanging-walker
statistics remain unqualified. Full G09/G10/M05 remains open.

T4 lysozyme L99A and Slurm settings remain reserved for user-initiated HPC work.
G07/M03 physical blockers remain: seven sensitivity failures, pilot force
exceedances and 29 missing new quantum references. All 46 G05 references and
prior scientific artifacts remain unchanged. QM accounting is still
2325.644650052/86400 s; this technical work authorized no further QM/production
calculation. Preserve that ledger and its reviewed resource conditions.
