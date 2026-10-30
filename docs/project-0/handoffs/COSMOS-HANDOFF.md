# COSMOS continuation handoff

Prepared 2026-10-30. This is the active handoff for work on LUNARC Cosmos.

## Start here and keep the scope small

Use **[georgpou/AToM_MLMM, branch COSMOS](https://github.com/georgpou/AToM_MLMM/tree/COSMOS)**.
`COSMOS` is the integration and main working branch for this project on Cosmos.
All new implementation, repair and qualification branches must descend from its
current head; their PRs must target `COSMOS` and be merged there. `main`,
`hpc-atom-benchmark` and the earlier Cloud branches retain their own lineage.
This instruction does not change GitHub's repository-wide default branch.

The Cloud development used a different filesystem/execution layout. Existing
Cloud acceptance stays attached to its original snapshot and profile. Reproduce
applicable checks on Cosmos and record new evidence; do not erase the original
results or assume every Cloud pass transfers to this cluster.

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md), this handoff and the
assigned gate/task's specific reading links. Use [the roadmap](../../../README.md#roadmap)
to locate the next task. Earlier Cloud handoffs explain scientific lineage; their
old active assignments, `/workspace` commands and orchestration policies do not
replace this Cosmos assignment or current user instructions.

The **first task** is a bounded Cosmos portability repair: fix the two known
workflow/path failure classes below, verify the repaired behaviors, then obtain a
complete CPU regression result. Do not start a molecular production campaign or
reimplement the engine. After that prerequisite, work through the gate sequence
below one explicit task at a time, starting with relevant M00 applicability and
G00-T1. A milestone-only assignment means its first unblocked unfinished task,
unless a combined review is explicitly requested.

## Activate the installed environments

The physical checkout is:

```bash
cd /lunarc/nobackup/projects/snic2019-35-66/George/AToM_MLMM
source environment/hpc/cosmos/activate.sh
python -c 'import sys, numpy, openmm; print(sys.executable); print(numpy.__version__, openmm.__version__)'
```

Main is `.runtime/cosmos-cpu/env`: Python **3.11.16**, NumPy **2.4.6**,
OpenMM **8.6.1**, CPU PyTorch **2.8.0**, and the pinned AToM/OpenMM-ML/MACE stack.
To use AmberTools' Python, then return to main:

```bash
source environment/hpc/cosmos/activate-amber.sh
python -c 'import sys, numpy; print(sys.executable, numpy.__version__)'
source environment/hpc/cosmos/activate.sh
```

Amber is `.runtime/cosmos-cpu/amber-env`, with Python **3.11.16**, AmberTools
**26.0**, and NumPy **1.26.4**. Main activation exposes Amber executables while
keeping main Python/NumPy 2 active. Source the wrapper in every new shell and job.

Prefixes, caches and logs are inside `.runtime/cosmos-cpu/`; temporary files use
the shorter `.tmp/` path inside the repository so Python Unix sockets fit the
OS path limit. Both are ignored by Git. Keep their absolute installation location;
a fresh clone needs its own install, not copied/moved Conda prefixes.

The system Conda at `/sw/easybuild_milan/software/Anaconda3/2024.06-1` bootstrapped
a local Conda **26.7.2** client. Its older **24.5.0** client does not interpret the
project's SHA-256 URL locks. The old client's `.*` version-pattern warnings were
metadata deprecations; they were not the regression failures. No system module,
user Conda environment or shell startup file was changed. Global environment
registration is disabled; these prefixes need not appear as named environments
in `conda env list`. RHEL TLS certificates are selected through
`ATOM_MLMM_CA_BUNDLE`; hash/TLS verification stays enabled.

See [Cosmos setup and scripts](../../../environment/hpc/cosmos/README.md).
Installation already succeeded; do not reinstall or solve replacement scientific
packages merely to repair the workflow tests.

## What passed, failed and remains untested

The source predecessor was `hpc-atom-benchmark` at
`70ad284745617122627f217cd86d58237a2435ee`. The nine installation checks below
passed on Slurm node **cn024**; each recorded exit code **0**:

| Check | What the pass establishes |
|---|---|
| `core_exact_versions` | Main Python distributions and Conda artifact identities match the locks |
| `amber_exact_versions` | Separate Amber distributions and artifact identities match the locks |
| `core_pip_check` | Main Python dependency consistency |
| `amber_pip_check` | Amber Python dependency consistency |
| `openmm_installation` | Available OpenMM installation/platform check |
| `cpu_potentials_and_atm` | Weight-free ML potential/native ATM smoke |
| `separate_ambertools_integration` | Main preparation interfaces call the separate Amber executables |
| `atom_uwham` | Pinned upstream UWHAM regression |
| `repository_documentation` | Local documentation and checker self-tests at that snapshot |

Main-to-Amber-to-main activation was verified. The final focused Cosmos checks
passed **4 tests**: explicit CA override, pruning installed `.runtime` and
`.tmp` documentation, and actual creation of a multiprocessing Unix socket.
Final documentation checked **181 Markdown files**, with zero errors and all
eight checker self-tests passing before this handoff was added. Handoff-only
checks are recorded in the matching worker report; these are separate snapshots.

The full CPU command was:

```bash
python -m pytest -m 'not gpu and not model_assets and not slow' -q   --basetemp="${TMPDIR}/pytest-${SLURM_JOB_ID}"
```

Its completed Cosmos result was **654 passed, 50 failed, 12 errors,
57 deselected**, in **492.24 s**. Do not call the full suite green. Later edits
added a parametrized documentation case; use actual future collection counts,
not a target count obtained by deselecting failures.

| Failing area | Count | Observed cause and preserved assertion |
|---|---:|---|
| `tests/unit/test_joint_quantum_execution.py` | 17 failures, 12 setup errors | Recovery/resource checks encounter missing `/workspace` before exercising authorization, budgets, pilot/receipt admission or durability |
| `tests/unit/test_quantum_interruptions.py` | 17 failures | The same old filesystem assumption prevents synthetic interruption/child cleanup/recovery checks |
| `tests/unit/test_quantum_recovery.py` | 15 failures | The same old layout blocks synthetic recovery, reuse and receipt/budget checks |
| `tests/workflow/test_engine_fresh_process.py` | 1 failure | The offline guard denies all of the original repository, including its own relocated attempt now under `.tmp/`; it rejects relocated `metadata.json` |

These reported failures are workflow/filesystem portability failures. They are
not failed energy/force tolerances or chemical-reference comparisons. They still
matter: recovery, resource accounting, independent continuation and durable
records must work before relevant cluster workflows can be accepted.

Job **4063958** installed both environments and passed all nine checks. Its
initial full-suite attempt was cancelled after failures, preserving the log.
Job **4064390** repeated strict environment validation successfully, then
finished **FAILED, exit 1**, because of the completed full-suite result above.
No jobs from this setup remain running. No GPU allocation or actual quantum
reference calculation was launched.

Evidence:

- [Environment worker](../../../Worker_Log/Documentation/Cosmos_Environment_v1_worker.md).
- [Nine-check results](../../../Worker_Log/Documentation/evidence/Cosmos_Environment_v1/environment-validation.json).
- [All failed/error node names](../../../Worker_Log/Documentation/evidence/Cosmos_Environment_v1/cpu-regression-summary.txt).
- [Reproduced first traceback](../../../Worker_Log/Documentation/evidence/Cosmos_Environment_v1/first-failure-workspace.log).
- [Scheduler accounting](../../../Worker_Log/Documentation/evidence/Cosmos_Environment_v1/slurm-accounting.txt).
- Local full stdout/stderr: `.runtime/cosmos-cpu/logs/validate-4064390.out` and `.err`.
- Installed environment/client locks, activation receipts and original/final home-file hashes are in the same evidence folder; the original setup snapshot is identified by `source-snapshot.sha256`.

GPU, deferred model/slow checks, full cluster/storage/restart parity and molecular
physical qualification were not established by these passes. The approved model
bytes were preserved; this setup did not perform new real-model acceptance.

## First child branch: portability repair

Create a child such as `cosmos/portability-repair` from the published `COSMOS`
head. Capture the current failures before implementation. Work on the actual
helper/test behavior, preserving independent assertions:

1. Inspect `tools/resume_neutral_quantum.py`, especially `measurements()` and its
   `shutil.disk_usage('/workspace')` call. Trace callers in
   `tools/resume_joint_quantum.py`, the three failing quantum test files, and
   their resource/authorization policies. Measure the filesystem containing the
   actual attempt/output rather than an invented Cloud directory. Test the path
   without a `/workspace` directory. Do not create `/workspace`, write outside
   the repository, fake disk readings or remove headroom checks.
2. Distinguish hard-coded host paths from frozen approval/evidence identities.
   Synthetic tests should build self-contained fixture approvals and fake
   executable boundaries under their test directories. Do not alter accepted
   quantum records, historical `attempt_path` approvals, lease semantics or
   cumulative budgets to make relocated tests pass. Any actual execution-path
   migration needs an explicit reviewed policy with the original identity and
   ledger preserved; it is not an automatic string replacement.
3. Repair `tests/workflow/test_engine_fresh_process.py` so a relocated bundle can
   live inside the allowed repository while the original source/run and caches
   remain denied. Permit only the declared relocated bundle where needed.
   Add deliberate probes proving the old source, old run and caches are still
   unreadable and network access still fails. Keep the sample uniqueness,
   unchanged original samples and actual bundled-source assertions. Do not
   disable the deny guard or use the original checkout as fallback.
4. Preserve the short `.tmp/`, certificate override, disabled global Conda
   registration and generated-tree documentation exclusions. Run the focused
   failing nodes first; then the three quantum workflow files and offline worker
   test together. These tests use synthetic executables: do not launch real QM
   as a substitute for software recovery tests.
5. Review resource measurement on actual Cosmos job steps: cgroup v1/v2 paths,
   `/proc/self/cgroup`, step/job memory limits, child RSS/process-group identity,
   wall-time signals and shared storage. Do not treat host-wide free RAM as the
   job allocation or relax safeguards to match a new filesystem.
6. When focused repairs pass, run the complete available CPU suite once on the
   stable repaired snapshot. Preserve failures and all deselections. Audit the
   finished scoped repair independently before acceptance/merge; self-checking
   is not independent review. Do not start the next gate in this repair task.

This is a software portability batch. If a proposed fix changes shared field
meaning, masses, constraints, units, caps, periodic rules, signs, corrections or
scientific resource/authorization contracts, record the required specification
amendment and review instead of slipping it into setup cleanup.

## Slurm and Cosmos operating rules

Only modify files **inside this repository**. Read-only inspection elsewhere,
including system modules, the home shell setup and scheduler information, is
allowed. Do not change HOME, user startup files, shared Conda or global caches.
Use one agent by default and compact evidence; do not inherit an old Cloud
handoff's delegation mandate. Respect the user's Plus-plan usage constraint:
use timed waits while jobs queue/run, avoid frequent polling and repeated full
suite reruns, and allow new user input to interrupt waiting.

The user's examples are preserved under [Slurm_example](../../../Slurm_example/).
Account **LU2025-2-123**, CPU partition **lu48**, and GPU partition **gpua100i**
were checked during setup. Recheck current allocation/partition access before
submission. Existing install/validate scripts request **one task, two cores,
12 GB RAM**; validation has a **30-minute** limit and install a **one-hour** limit.
Submit from the repository root so the output paths resolve correctly:

```bash
mkdir -p .runtime/cosmos-cpu/logs
sbatch --test-only environment/hpc/cosmos/validate.sbatch
sbatch --parsable environment/hpc/cosmos/validate.sbatch
# Wait in timeout; query only when useful:
squeue -j JOBID
sacct -j JOBID --format=JobID,State,ExitCode,Elapsed,MaxRSS
```

The validation template runs all nine checks and the full CPU suite, so its
current expected scheduler result is nonzero until the known failures close.
For a focused gate, derive a small job script with that gate's command and
explicit resource/time budget; retain real outputs and scheduler exit status.
Run CPU simulations/heavy checks on allocations rather than the login node.
Do not launch large production, missing-reference campaigns or GPU runs simply
because a script exists.

The GPU diagnostic template is **unsubmitted**. CPU PyTorch and the current MACE
callback are CPU-only; an OpenMM CUDA plugin or visible A100 does not qualify
GPU ML/MM. Create a separate locked GPU profile only in an explicitly assigned
hardware task. Keep the working CPU environment intact.

`environment/hpc/profile-template.json` remains incomplete. The current profile
contract documented in [the HPC guide](../../../environment/hpc/run-guide.md)
accepts scheduler `none`; merely inserting `slurm` would not establish admission.
Record Slurm execution evidence separately until scheduler/profile support has
a reviewed contract amendment. Measure storage locks, atomic rename and fsync on
the actual output filesystem; a Cloud/local filesystem pass is not Cosmos parity.

## Reproduce gates and milestones in order

Start from the existing implementation and prior scoped findings. Use current
STATUS/support evidence and each gate's explicit direct prerequisites. Do not
repeat accepted design decisions unless the Cosmos adaptation changes them.
Keep Cloud and Cosmos results distinct, and inspect actual test nodes: gate pages
can name planned nodes that do not exist. Implement a missing assertion when
assigned; do not count absence as a pass.

| Order | Cosmos work and review boundary |
|---|---|
| [M00](../milestones/M00-architecture-review.md) | Establish which reviewed contracts cover the CPU reproduction. Review only operational amendments needed for Cosmos; preserve approved physical definitions and predeclared chemical limits. Record unresolved applicability explicitly. |
| M01: [G00](../gates/G00-environment-and-provenance.md), [G01](../gates/G01-identity-partition-and-contracts.md) | First numerical task is G00-T1 after applicable M00 evidence: regenerate exact API/provenance reports on Cosmos. Then identity/partition/contracts; complete their combined M01 review. G00-T2/model and T3/GPU are separate applicable scopes. |
| M02: [G02](../gates/G02-analytic-force-in-native-atm.md), [G03](../gates/G03-atom-routing-and-integration.md) | Reproduce analytic energies/forces at both maps, full real-coordinate forces, unequal mobile groups and native/AToM routing, then combined M02 evidence. Preserve FD steps and tolerances. |
| M03: [G04](../gates/G04-link-boundary-and-derivatives.md), [G05](../gates/G05-local-model-adapter.md), [G06](../gates/G06-periodicity-and-interaction-ledger.md), [G07](../gates/G07-joint-cavity-ligand-atm.md) | Reproduce cap-parent derivatives, safe trusted-model loading, MM ledger/PBC and composed ligand/cavity checks. Keep G05/G07 independent chemical-reference and boundary-sensitivity requirements. Missing references remain physical holds. |
| M04: [G08](../gates/G08-thermodynamics-and-estimators.md) | Reproduce independent known-answer thermodynamics, reduced potentials, signs, domains, restraints and correction admission. M03 and M04 have their actual shared prerequisites; execute serially within the user's resource budget. |
| M05: [G09](../gates/G09-solvent-preparation-and-export.md), [G10](../gates/G10-restart-and-replica-exchange.md) | Reproduce preparation, all-force activation, persistence, worker failures and transactional exchange on actual Cosmos storage/allocations. Cover checkpoint and portable-State limits, process cleanup, locks/fsync and resource accounting. Combine only after M03/M04 prerequisites. |
| M06: [G11](../gates/G11-protein-abfe.md) | Reproduce the admitted protein ABFE profile only after scientific prerequisites. Start with bounded evidence, not a long production run. Complete domains, midpoint connection, corrections and convergence before binding claims. |
| M07: [G12](../gates/G12-dual-ligand-rbfe.md) | Reproduce complete two-ligand RBFE, shared engine/AToM routing and molecular thermodynamic obligations after M06. |
| M08: [G13](../gates/G13-performance-and-release.md) | Benchmark and release only specifically admitted profiles; include licensing, source/model identities and combined prior reviews. GPU stays separate until its own checks pass. |

For each task: write the expected assertion, observe its intended failure when
repairing a defect, implement the smallest change, run focused tests and required
combined checks, and record the exact source/profile/scheduler evidence. Use the
next unused worker/audit attempt in the gate's prescribed folder. One accepted
task is not a gate pass; milestone closure requires its closing combined review
plus earlier applicable reviews. Update **STATUS.md**, the only live progress
summary. This handoff is a starting procedure, not a second acceptance index.

Current physical holds remain: **29 missing G07 quantum references**, boundary
sensitivity, C3 unmatched-physical-state closure, protein chemistry, corrections/
convergence, licensing, GPU and cluster restart/storage parity. Preserve the
**46 accepted G05 neutral references** and the charged QM ledger
**2325.6446500519996 / 86400 seconds**, leaving **84074.355349948 seconds**.
This handoff authorizes no new QM campaign or reset of those counters.
`binding_result=not_evaluated` remains unchanged.

## Branch creation, publication and future PRs

This assignment creates and publishes `COSMOS` from the preserved current
checkout, including setup helpers, logs and this handoff. No independent gate
acceptance is implied by publication. The setup predecessor is the exact
`70ad284745617122627f217cd86d58237a2435ee` commit above. Verify the resulting
published head rather than assuming the predecessor is still COSMOS's head:

```bash
git branch --show-current
git rev-parse HEAD
git ls-remote --heads origin refs/heads/COSMOS
git status --short --branch
```

There were uncommitted setup/report changes and user-provided Slurm examples at
handoff preparation. Preserve and include the intended files explicitly; never
reset, clean or overwrite them to create the branch. `.runtime/` and `.tmp/`
must remain untracked. Branch creation/publication is performed as this task's
final delivery, not left as work for the next agent. See the matching
[handoff worker](../../../Worker_Log/Documentation/Cosmos_Handoff_v1_worker.md)
for the publication method and exact snapshot verification.

For each later task, start with a clean preserved checkout and fetch the explicit
integration ref (the initial clone was shallow/single-branch):

```bash
git fetch origin refs/heads/COSMOS:refs/remotes/origin/COSMOS
git switch COSMOS
git merge --ff-only origin/COSMOS
git switch -c cosmos/portability-repair
# Work, verify, and commit explicit source/evidence files.
git push -u origin cosmos/portability-repair
```

Use a fresh descriptive child name for each task. Create its PR with **base
`COSMOS`**, include the bounded scope, actual checks and open scientific holds,
obtain the required review, then merge into `COSMOS`. Fetch that merged head
before starting the next child. Do not merge only between children or use
`main`/`hpc-atom-benchmark` as a new Cosmos child's parent or PR base. Do not
force-push or rewrite accepted history. Fetch/deepen only the history needed.
Use configured Git authentication or the connected GitHub tools; never request
or expose access tokens. No branch protection/default-branch setting change is
implied by this working-branch policy.
