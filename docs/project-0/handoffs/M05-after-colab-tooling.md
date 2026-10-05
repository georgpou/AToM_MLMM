# M05 after the bounded CPU/Colab-tooling increment

**Branch:** `m05-colab-workflows`, child of published M04 HEAD
`fab6388b041acc4362f30b5ff7d3789a33fc536f`. Main and predecessors are unchanged.\
**Exact executable source:** `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.\
**Frozen independently reviewed submission:** `bc6fd520308fba7e7448929138eb91e80ca6f063`.
Later commits record acceptance/handoff only. All these commits are published on
the child branch; use its current HEAD to read reports and the exact source pin
for new execution. Do not reset/rebase/force-push or silently migrate old bundles.

## Accepted result

[G09 v5](../../../Worker_Log/Milestone_05/Gate_09_v5_audit.md) and
[G10 v2 combined](../../../Worker_Log/Milestone_05/Gate_10_v2_audit.md) accept the
bounded combined CPU scope and
[scientific amendment](../specs/m05-dense-exchange-amendment.md). **543 full CPU
passes**, no skips,606.45s; one fresh Astra/high reviewer passed **52 checks**,
no skips, plus independent image/roundoff/derivative/exchange/recovery probes.
No material findings/repairs or deferred minors. Official notebook schema and
all eight documentation self-tests passed. No implementation changes followed
review; only reporting changes. Large logs and complete sealed archives are in
[worker evidence](../../../Worker_Log/Milestone_05/evidence/M05_v1/README.md), with
[review evidence](../../../Worker_Log/Milestone_05/evidence/M05_v1_review/README.md).

The common engine retains the two CPU locks, approved MACE bytes, Reference
double / CPU float64, fixed complete-ligand ML membership, cap-parent derivatives,
PME/constraints/accounting and S06 limits. New64-water local controls have224/233
real atoms, both-map full-force/coupling/FD proof and serial nine-frame/18-step
fixed-window pilots. Solvated offline/cache-denied reconstruction and distinct
checkpoint-vs-portable-State guarantees pass. Both actual dense pair pilots have
four committed rounds/eight unique samples; the controller preserves phases,
current energies, labels, stable walkers, two host RNG streams and archived
explicit rollback/replay. Correlated energy reconstruction is qualified;
exchanging-walker statistical uncertainty is not.

## Next dependency (superseded by later user steering)

The user now defers TPU and requests unattended CPU MD/QM notebooks. Follow
[the new assignment](M05-colab-long-runs.md); the original CPU-then-TPU sequence
below is retained as history, not the current task.

### Original CPU-then-TPU sequence

No authorized Colab executor or TPU hardware was available here. Notebook
creation, local tests and a selected runtime are not Colab/TPU qualification.
Use [the notebook guide](../../../notebooks/README.md) and its exact run order:

1. Select a Colab CPU runtime; reproduce the visible immutable M04 baseline
   `7b41213e87bfcc3ce76def7ffb64565110bbafec` with unchanged locks. Activate the
   isolated main environment in every computation subprocess. Check resources
   before full tests (this workspace's full suite peak process RSS was about5GiB).
   Preserve complete stopped attempts/logs before changing runtimes.
2. Use a fresh checkout/evidence directory and exact reviewed source
   `424a859732b77b2f91cd03b12bb3f0b8adf3f541` for the denser numerical/restart
   preflight and serial bounded pilots. No moving branch/main source selection.
   Preserve resource/exit/profile/source/model/input hashes, States/checkpoints,
   raw energies/full forces and all failed pending trees. Export complete stopped
   local trees to unused storage authorized by the user; verify their seals.
3. On the same exact source, run `tools/m05_tpu_probe.py cpu-reference --output
   UNUSED`. Alternatively restore the complete reviewed CPU reference archive:
   **SHA `8a625d5bdcbac5cc1ddeb244ff12d095b14f811a287ca18732f86c943dba8d73`**.
   It contains108 actual-MACE ABFE/RBFE both-map configurations, cap projection,
   changed coordinates/graph shapes, three-step real-parent/ligand/solvent FDs and
   equivalent CPU startup/steady timings. Model-input counts are15/24 including
   caps; full-real counts are224/233.
4. Explicitly select a TPU runtime and restore verified reference assets/source.
   Follow [the separate experimental profile](../../../environment/colab-tpu/README.md):
   clone the unchanged CPU main prefix, then add only hash-pinned XLA2.8.0,
   libtpu0.0.17 and absl-py2.3.1. Keep CPU locks/guards unchanged. Run the actual
   MACE probe; preserve unsupported arithmetic/operators/fallbacks as negative
   results. Timing qualification requires actual TPU/double arithmetic and all
   numerical checks; OpenMM/PME/integration remain CPU. No CUDA substitution or
   full-engine TPU-support/throughput claim.
5. Return complete exports. Verify inert seals and exact source/profile/model
   identities before acceptance. Resume a separate local working copy with its
   exact bundled source and matching profile. Default pending exchange rounds
   block continuation; inspect and use explicit archived rollback/replay.
   Portable States do not preserve thermostat RNG. Durable mounts are export-only.

If hardware is unavailable, leave execution **not_run** and continue only
within newly assigned CPU scope. Do not provision GCP, start training or
substitute weights/precision. Serialize science, use bounded resource preflight
and preserve attempts. One reviewer should audit each ready submission; idle
while it works, following the user's economical workflow.

## Boundaries and preserved blockers

The stock six-atom Reference pair artifact is recorded and not repaired.
OpenMM/general runtime geometry are unchanged. The independently accepted
fixture-only box-face roundoff representation changed at most1.6653e-17nm;
failed original inputs/raw records remain frozen. General seams/long-time
stability require owning-profile evidence if they later threaten method work.
External engine issues are examined/reported but are not the main development
priority unless they seriously block ATM ML/MM.

Full G09/G10/M05 and M03 are open. No equilibrated density/NPT/virial, molecular
accuracy, affinity, protein, long production, statistical exchanging-walker,
GPU/multigpu or actual Colab/TPU result is claimed. Keep seven G07 sensitivity
failures, pilot force exceedances,29 missing references and the quantum ledger
**2325.644650052/86400s** unchanged. No new QM, protein, Slurm/HPC or GCP work
was started; T4 lysozyme/HPC remain reserved for user initiation.
