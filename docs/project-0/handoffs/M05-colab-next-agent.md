# M05 continuation: Colab CPU, then TPU benchmarks

**Requested:** 2026-10-05 UTC. **Branch:** `m04-engine-readiness`.\
**Published scientific checkpoint:** `7b41213e87bfcc3ce76def7ffb64565110bbafec`.\
**Assignment:** Continue the remaining M05 / G09-G10 technical work. Create a
root `notebooks/` folder and use Google Colab for the more demanding validation
calculations. Start with CPU; then attempt TPU compatibility and benchmarks.

> **For agentic workers:** Use `superpowers:executing-plans` inline. Preserve
> the user's economical workflow: serialize scientific jobs, use one independent
> reviewer when a submission is ready, and stay idle while that reviewer works.
> This handoff assigns future implementation; its checkboxes are not executed results.

**Goal:** Reproducible Colab execution of the shared engine, broader solvated
workflow evidence and persistent exchange/restart coverage, followed by an
honest assessment of whether the actual MACE calculation benefits from TPU use.

**Architecture:** Notebooks orchestrate repository functions and CLI commands.
Scientific code remains in `src/atm_mlmm/`, with one physical builder and ATM
adapter. Colab CPU uses the existing locked environment. TPU experiments use a
separate execution profile and cannot silently change the accepted CPU path.

**Tech stack:** Existing OpenMM/AToM/MACE CPU locks; Jupyter/Colab `.ipynb`
wrappers; a separately pinned PyTorch/XLA profile if the TPU probe can run.

**Spec:** [G09](../gates/G09-solvent-preparation-and-export.md),
[G10](../gates/G10-restart-and-replica-exchange.md), the
[accepted solvent amendment](../specs/cloud-solvent-control-amendment.md), and
the user's CPU-first/TPU-second instructions in this handoff.

## Starting evidence and minimal onboarding

Read `AGENTS.md`, the current/next-work portions of [STATUS](../STATUS.md),
the [checkpoint handoff](CLOUD-ENGINE-after-G09-v4.md), the
[runner guide](../../../examples/cloud_engine/README.md), G09/G10 and their
relevant S04-S07 sections. Use the
[CPU setup guide](../../../environment/cloud-cpu/README.md) as installation
authority. Unrelated historical audits are not onboarding prerequisites.

- Tested implementation: `027f8173babc13606afb24d96f58148704e38b1b`;
  frozen reviewed submission: `09a85d979fe9fce2ceca23da74509846254df9b1`.
- **501 CPU tests passed**, no skips. The
  [G09 v4 audit](../../../Worker_Log/Milestone_05/Gate_09_v4_audit.md) independently
  passed 21 focused checks/six probes and closed G09-R1/R2.
- Sparse rigid TIP3P/PME ABFE and RBFE controls have 56/65 real atoms. Both CLI
  pilots saved nine frames/18 sampling steps plus six preparation steps.
- Bounded G09 subsets and the
  [G10 single-pair boundary](../../../Worker_Log/Milestone_05/Gate_10_v1_audit.md)
  are accepted. Full G09/G10/M05 remains open.
- The CLI currently samples fixed windows. `attempt_pair_exchange()` supplies
  one actual-worker decision; it is not a persistent exchange controller.
- No Colab execution or TPU result exists at this checkpoint. A notebook that
  has merely been written or validated locally is not Colab qualification.

Use the existing development branch and normal commits/pushes. Preserve main,
`m03-g06-g07`, submitted workers/audits and every earlier scientific artifact.
Do not reset/rebase/force-push. Inspect actual HEAD and local changes first.
This handoff/status arrive in a reporting-only descendant of `7b41213`;
continue the published HEAD containing this file rather than resetting to
the earlier checkpoint. Colab baseline reproduction may pin `7b41213`.

## Global scientific and resource constraints

- Retain complete ligands, fixed ML membership, cap-parent derivatives, the
  same physical Hamiltonian at both maps and full influencing-real-atom forces.
- Preserve declared MM/PME/constraint/dispersion accounting, raw/outside/total
  energy distinctions, exact identities and established S06 numerical limits.
- Start with Reference double / MACE CPU float64, NVT 300 K, timestep
  0.0005 ps and two CPU threads. Another backend/dtype is a separate profile.
- Existing periodic anchors use minimum-image harmonic distances away from
  half-box seams. Preserve both-map geometry/domain and failure checks.
- Freeze new solvent/preparation definitions and tolerances before examining
  results; obtain scientific review for changes. Do not infer NPT/pressure or
  virial support from NVT success.
- This assignment permits bounded M05 technical validation on Colab and TPU
  feasibility/benchmark experiments. It does not start protein production, new
  QM/reference calculations, training or a separately provisioned GCP service.
- Before each heavier batch, record atom/worker counts, CPU/RAM/free disk,
  seeds, steps, wall-time limit and persistence interval. Scale from a measured
  small pilot; Colab CPU is not guaranteed to exceed this workspace's resources.
- Seven G07 sensitivity failures, pilot force errors and 29 missing references
  remain. Preserve the QM ledger at **2325.644650052/86400 s**. Changing machines
  or resetting Colab does not reset that ledger or establish M03 acceptance.
- T4 lysozyme L99A and Slurm/HPC work remain reserved for user initiation.

## Review focus

1. A fresh Colab kernel/source checkout silently uses different packages or weights.
2. A disconnect or partial persistent copy loses/duplicates samples or exchange history.
3. A resumed exchange uses stale energies, wrong walker/state labels or lost RNG state.
4. Denser solvent exposes missed image clashes, lost coupling or repeated force ownership.
5. An XLA/TPU runtime falls back to CPU, changes precision or omits force derivatives.

## Task 1: create and run the Colab CPU notebook

**Create:** `notebooks/README.md`, `notebooks/m05_colab_cpu.ipynb`. Add an
Open-in-Colab link and a brief run order. Keep notebooks free of secrets and
large committed outputs; save scientific evidence separately.

**Interfaces:** Call the existing `python -m atm_mlmm check/run/resume` CLI,
repository tests and later reviewed controller entry point. Reuse
`atm_mlmm.adapters.atom.attempt_pair_exchange(workers, snapshots, state_ids,
walker_ids)`; do not duplicate energy, force or Metropolis logic in cells.

- [ ] Pin the exact source commit in a visible parameter; verify actual checkout
  SHA and model/input hashes before trusted loading. Use the published starting
  checkpoint for baseline reproduction, then explicitly pin new implementation
  commits for later experiments. Never silently run moving `main`/latest packages.
- [ ] Select Colab CPU first: **Runtime → Change runtime type → no accelerator**.
  Record actual OS/architecture, processor count, RAM/disk, Python/package
  identities and OpenMM/model devices. Verify Linux x86_64/setup requirements.
- [ ] Install the two unchanged locks into a writable isolated prefix. For
  `/content/AToM_MLMM`, a Bash cell can use:

  ```bash
  cd /content/AToM_MLMM
  ATOM_MLMM_SETUP_ROOT=/content/atom-mlmm-colab-cpu bash environment/cloud-cpu/install.sh
  source /content/atom-mlmm-colab-cpu/activate.sh
  export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
  python /content/atom-mlmm-colab-cpu/validate.py --repository "$PWD"
  python -m atm_mlmm check fixtures/solvated_fragment/v1/abfe/config.json
  ```

  Repeat activation in each computation cell/subprocess: activating one Bash
  cell does not change later notebook-kernel Python. Keep Colab's kernel and
  Amber's NumPy 1.26 separate from the main NumPy 2 environment. Installation
  failures retain their logs; incompatible hosts need a reported profile
  decision rather than an unpinned `pip install --upgrade` workaround.
- [ ] Run strict setup checks and the meaningful CPU suite, then both existing
  water configurations in unused output directories. Capture commands/exit
  codes, exact inputs, raw energies/full forces, box, preparation, restart and
  resource summaries. Establish the real Colab baseline before heavier work.
- [ ] Keep active calculations/journals on local `/content` storage. At bounded
  safe points, export complete hash-verified bundles to a user-authorized durable
  location or download them. Copy and verify before deleting anything. A saved
  notebook is not a saved runtime/model/checkpoint. Do not assume mounted Drive
  has the same atomic-transaction semantics as the local sample journal.
- [ ] After interruption, verify hashes and the committed prefix before resume.
  Preserve incomplete transactions. Test checkpoint continuation within the
  same supported profile and portable-State continuation separately; do not
  promise bitwise trajectories across changed hosts/hardware/libraries.
- [ ] If no authorized Colab execution tool is available, deliver the notebook,
  Open-in-Colab link and exact user-run instructions. The user selects the
  runtime and authenticates any required access. Import returned evidence and
  verify it before claiming a Colab pass; otherwise record execution as pending.

## Task 2: finish the next bounded G09/G10 workflow increments

**Relevant source:** `prepare.py`, `workflow.py`, `persistence.py`,
`adapters/atom.py` under `src/atm_mlmm/`; existing solvent, fresh-process,
restart, exchange and archive tests under `tests/workflow/`.

- [ ] Write a focused implementation plan with exact interfaces before changes.
  Define a denser classical-water control in a new fixture version: box/water
  count or density construction, both safe ligand sites, constraints, PME and
  preparation phases. Preserve original solute parameters and ML membership.
  Fixed-volume preparation does not itself prove equilibrated liquid density.
- [ ] Establish failing independent geometry/coupling/force/export tests, then
  implement the smallest changes. Reevaluate real forces at both maps, cap
  parents and solvent coordinates; use S06 finite-difference step sweeps.
  Any faster neighbor/image guard must agree with a small brute-force oracle.
- [ ] Use the CPU notebook for the demanding dense-solvent validation and
  bounded multiwindow pilots after numerical preflight. Preserve all failures
  and representative raw records; report timings and memory, not affinity claims.
- [ ] Complete solvated fresh-process/offline/cache-independent reconstruction
  and restart evidence for G10-T1/T3. All executable model/source assets needed
  by the worker must be bundled and hash-bound; a cache hit is not portability.
- [ ] Build persistent exchange scheduling around the existing pair adapter,
  with explicit state/walker histories, current energies, unique sample IDs,
  host RNG state and interruption semantics. Define decision/refresh/journal
  failure recovery first: the current pair adapter is not transactional and
  postdecision errors must not silently become rejections or successful swaps.
- [ ] Test prefix interruption/resume against the same prepared workers/seeds,
  accepted and rejected decisions, failures before/after the decision and
  journal boundaries. Verify fresh cross-state energies and analysis continuity.
  Preserve both mapped failed geometries without energy/force reentry.
- [ ] Run affected tests and the available full CPU suite on the final source.
  Submit one frozen G09/G10 technical review with actual evidence. Earlier
  acceptance is carried forward only where source/definitions remain unchanged.

## Task 3: then attempt TPU compatibility and benchmarks

**Create:** `notebooks/m05_colab_tpu_benchmarks.ipynb` and a documented separate
experimental dependency/profile manifest. The CPU notebook remains the reference.

The current worker/model deliberately admit Reference / CPU float64 only.
OpenMM's standard platforms do not include TPU. PyTorch TPU execution uses
PyTorch/XLA; selecting a TPU runtime alone does not move MACE, PME, integration
or the worker onto it. Initial TPU work therefore tests the actual ML component;
full-engine acceleration requires a separately validated integration design.

- [ ] After CPU reproduction, select an available Colab TPU runtime and pin a
  compatible PyTorch/PyTorch-XLA/libtpu stack in a separate profile. Verify the
  actual backend/device is TPU; an `xla` device can also represent CPU. If no
  TPU is available, retain the runnable notebook and mark hardware work pending.
- [ ] Load the same verified academic MACE checkpoint in the experimental
  path. Probe real energy and coordinate-gradient execution, required operators,
  graph/shape changes and actual arithmetic precision. Keep existing CPU
  dtype/device guards and locks intact. Do not substitute an untrained model,
  different weights or silent lower precision to claim success.
- [ ] Compare saved identical admitted ABFE/RBFE configurations at both maps
  against CPU float64 references: energies, all relevant forces including cap
  projection, coordinate step sweeps and changed-coordinate reevaluation.
  Record numerical errors and unsupported operations/fallbacks explicitly.
- [ ] Only after numerical checks, measure compile/startup time separately from
  synchronized steady-state timings. Include host↔TPU transfer, graph-building,
  force-gradient and return-to-OpenMM costs. Report problem sizes/dtypes and
  compare equivalent work; an isolated tensor benchmark is not engine throughput.
- [ ] Preserve a negative compatibility or speed result. If operators/precision
  fail or no useful speedup is measured, document why and continue M05 on CPU.
  TPU feasibility is an extension, not a prerequisite for accepting a CPU scope.
  No automatic CUDA substitution or broad TPU-support claim is assigned here.

## Evidence, acceptance and finish

Use next unused attempts in `Worker_Log/Milestone_05/` (G09 v5 / G10 v2 if still
unused) and separate evidence directories. Record actual Colab runtime dates,
source/model/input/profile hashes, notebook revision, seeds, commands, exit
codes, force/error metrics, resource samples, journals, States/checkpoints and
TPU diagnostics. Preserve failures and explicitly mark unrun/skipped checks.

Check notebook JSON/schema and clear secrets/large cell outputs; test orchestration
failure propagation and scientific checks where behavior changes. Check local
documentation with `python tools/check_docs.py --self-test`. Do not repeat the
full numerical suite solely for reporting edits.

The closing G10 document defines M05's combined review. Finish the applicable
declared CPU scope, but do not turn task acceptance into full milestone or
protein/affinity acceptance: M03 physical prerequisites and other unqualified
profiles remain visible. Update STATUS from actual results and leave a new
handoff with the exact published commit and next dependency.

## External references checked for this assignment

- [Colab FAQ](https://research.google.com/colaboratory/faq.html): CPU/accelerator
  use, variable resources, runtime loss and exporting results.
- [OpenMM platforms](https://docs.openmm.org/latest/userguide/application/02_running_sims.html#platforms):
  standard platform choices; consult the pinned build's actual available platforms.
- [PyTorch/XLA devices](https://docs.pytorch.org/xla/master/learn/pytorch-on-xla-devices.html):
  XLA device placement, TPU versus CPU, lazy execution and synchronization.

Recheck external setup details when executing; pin the actual versions used.
