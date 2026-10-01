# Project 0: handoff to the next agent

## Mandatory branch rule

**Create your first working branch FROM `m01-g00-cloud-environment-setup`. Never start from `main`. Never commit, merge, rebase, reset, or push work to `main`.** This is an explicit user requirement and takes precedence over generic branch workflows.

The setup records are committed on `m01-g00-cloud-environment-setup` at `4c835e0a25cbfa7c178b1b0333873d1e9cce93c9`. This handoff is added by a subsequent commit on that same branch. Use the branch's current tip, which includes this file. The original `origin/main` reference was `2d7bcc94f901738e39f536f16de84699d4e8d631`; it has not been changed. This cloud checkout has no local `main` branch, and there is no need to create one.

In the prepared cloud checkout, run these commands before changing files:

```bash
cd /workspace/AToM_MLMM
git status --short --branch
git show-ref --verify refs/heads/m01-g00-cloud-environment-setup
git merge-base --is-ancestor 4c835e0a25cbfa7c178b1b0333873d1e9cce93c9 refs/heads/m01-g00-cloud-environment-setup
atom_mlmm_parent_commit="$(git rev-parse refs/heads/m01-g00-cloud-environment-setup)"
git switch --no-track -c m00-architecture-review refs/heads/m01-g00-cloud-environment-setup
test "$(git rev-parse HEAD)" = "$atom_mlmm_parent_commit"
test "$(git branch --show-current)" != main
git merge-base --is-ancestor "$atom_mlmm_parent_commit" HEAD
```

Expected: the new branch is `m00-architecture-review`, its starting commit exactly equals the setup branch's tip, and all checks succeed. If that name already exists, inspect it and choose an unused attempt suffix such as `m00-architecture-review-v2`; do not overwrite a branch. Inspect and preserve any existing user changes. Do not clean or reset files to make the checkout appear clean.

All later working branches must remain descendants of this setup branch. Name them for their actual milestone/gate/task. Start a follow-on gate branch from the reviewed predecessor branch so it retains prerequisite work; do not restart the lineage from `main`. Verify ancestry with `git merge-base --is-ancestor`. Leave the setup branch as the handoff parent while doing new work on child branches.

### If the setup branch is missing in another checkout

The branch is local; it has not been pushed to GitHub. A complete Git bundle is provided separately as `atom-mlmm-agent-handoff.bundle`. In an existing checkout, import just its side-branch reference:

```bash
git bundle verify /path/to/atom-mlmm-agent-handoff.bundle
git fetch /path/to/atom-mlmm-agent-handoff.bundle refs/heads/m01-g00-cloud-environment-setup:refs/heads/m01-g00-cloud-environment-setup
```

Then execute the branch-creation checks above. If a local branch of that name already exists, inspect its identity before importing; do not force-update it. Do not silently substitute `main` when the parent branch is unavailable. Report the missing parent branch or bundle and continue independent read-only inspection. Remote publication is a separate action, not something this handoff claims was performed.

## Scope and immediate next assignment

Continue Project 0 in the prepared CPU environment, completing the relevant prerequisite review and then progressing through M01's G00/G01 tasks. Use [AGENTS.md](AGENTS.md) and [STATUS.md](docs/project-0/STATUS.md) as the controlling procedure and progress record. The repository currently contains planning documents and documentation tooling; planned `src/`, `tests/`, `fixtures/` and `environment/` paths are not already implemented.

**The installation is complete, but M00 and G00 have not been accepted. Do not interpret the setup branch's M01/G00 name or its passing smoke checks as gate approval.** The first task is the relevant [M00 architecture/contract review](docs/project-0/milestones/M00-architecture-review.md), unless a newer recorded review on the inherited branch already satisfies it.

| Order | Assignment and suggested branch | Required outcome before advancing |
|---|---|---|
| 1 | M00 review, `m00-architecture-review` | Review the relevant S01–S07 design, the environment decisions below, and one-group/two-group and environment-force extension boundaries. Record reviewed revisions, decisions, scope and identified reviewer. Follow M00's combined-review condition. |
| 2 | [G00-T1](docs/project-0/gates/G00-environment-and-provenance.md), `m01-g00-t1-cpu-qualification` | After relevant M00 review, implement the prescribed CPU API/version checks and complete environment/source evidence, reusing the installed dependencies and exact locks. Missing APIs must fail clearly. |
| 3 | [G01-T1](docs/project-0/gates/G01-identity-partition-and-contracts.md), `m01-g01-t1-identity-partition` | After applicable G00 evidence and relevant design review, implement stable identities and complete fixed selections using the reviewed S03 records. |
| 4 | G01-T2, `m01-g01-t2-shared-records` | Complete the common records, schema round trips, capability rejection and lightweight import boundaries. |
| 5 | G01-T3, `m01-g01-t3-mm-inventory` | Preserve the original MM inventory and implement the required evidence validation. |
| 6 | M01 combined review, `m01-combined-review` | Review G00 and G01 together on the same snapshot with required M00 evidence. Individual passing tasks do not automatically accept the milestone. |

These are ordered assignments, not permission to report them as implemented. Start with the first unblocked unfinished task and record the choice. Read its exact gate/spec sections, then follow the focused failing-test → smallest implementation → affected-checks cycle in AGENTS.md. Obtain the required review evidence before advancing. Only proceed to M02/G02/G03 when their actual prerequisites are satisfied; do not turn a small assignment into the whole project in one unreviewed change.

For M00 use `Worker_Log/Milestone_00/Milestone_00_vN_worker.md` and its matching audit. For G00/G01 use `Worker_Log/Milestone_01/Gate_00_vN_worker.md` / `Gate_01_vN_worker.md` and matching audits. Inspect all prior attempts, reserve the next number, preserve historical submissions, and distinguish self-checking from independent acceptance. Update STATUS.md with actual task/profile evidence as development progresses. No progress labels were changed by onboarding.

## Prepared runtime and agreed environment decisions

Activate the main environment in each new Bash session:

```bash
source /workspace/.onboarding/atom-mlmm/activate.sh
cd /workspace/AToM_MLMM
```

| Environment | Purpose and installed baseline |
|---|---|
| `/workspace/.onboarding/atom-mlmm/env` | Python 3.11.16, NumPy 2.4.6, CPU PyTorch 2.8.0, OpenMM 8.6.1, OpenMM-ML 1.8, MACE 0.3.16/e3nn 0.4.4, TorchANI 2.9.0, MDTraj 1.11.1, PyMBAR 4.0.3, OpenFF toolkit 0.18.0, openmmforcefields 0.16.0 and AToM source tag v8.5.0. AToM's installed package version is 8.5.0b0; keep tag and package version distinct. |
| `/workspace/.onboarding/atom-mlmm/amber-env` | AmberTools 26.0 CPU build, Python 3.11, NumPy 1.26.4, Biopython 1.85 and required utility dependencies. |

The user explicitly accepted **two Python environments in one cloud workspace**, and intends to maintain a separate AmberTools environment on other machines. AmberTools' bundled Python utilities have NumPy<2 requirements; current main MDTraj/matscipy require NumPy 2. Keep these dependency sets separate. This does not establish that AmberTools' compiled executables intrinsically require NumPy 1.

Main activation exports AMBERHOME and exposes `antechamber`, `parmchk2`, `tleap` and `sqm` from the separate preparation environment, while retaining the main Python interpreter. The main OpenFF/GAFF → separate AmberTools → CPU OpenMM pathway passed. Direct AmberTools Python work uses:

```bash
source /workspace/.onboarding/atom-mlmm/activate-amber.sh
# Return to the main environment when finished:
source /workspace/.onboarding/atom-mlmm/activate.sh
```

The user permitted compatible version changes and CUDA libraries where needed. Core repository-pinned versions were retained; CUDA/ROCm dependencies from OpenMM are present, but PyTorch is CPU-only and GPU execution was not qualified. Do not replace CPU PyTorch with a plain PyPI Torch reinstall. Main activation sets core pip constraints, writable caches, system CA trust and two CPU threads. Preserve TLS/checksum verification. Never embed credentials in scripts or logs.

The candidate `ATM_MLMM_environment.yml` and scientific specifications were left unchanged. The operational split is documented in [setup evidence](Worker_Log/Documentation/evidence/Cloud_CPU_Setup_v2/README.md) and must be explicitly accounted for during formal review/qualification; do not claim the original single-environment recipe was qualified unchanged. openmmforcefields 0.16.0 was installed from its exact source commit because its Conda package would pull AmberTools into main.

## Evidence and checks to reuse

Read the [setup worker log](Worker_Log/Documentation/Cloud_CPU_Setup_v2_worker.md) and [exact validation results](Worker_Log/Documentation/evidence/Cloud_CPU_Setup_v2/validation-target-v2.json). Historical logs describe their submission-time state; their pre-commit statements are not a description of this now-committed handoff.

- Both environments passed `python -m pip check`.
- `python -m openmm.testInstallation` passed on Reference and CPU platforms.
- A random untrained MACE model produced finite CPU energy/forces; TorchANI CPU descriptors and coordinate derivatives worked. No pretrained weights were downloaded.
- Direct ASE and OpenMM energy/forces agreed, including an ASE PythonForce wrapped inside native ATMForce. This is a smoke check, not the future gate's force/routing/thermodynamic qualification.
- AmberTools CLI and main OpenFF/openmmforcefields preparation produced a methane system with finite CPU OpenMM energy/forces.
- The existing upstream AToM UWHAM regression passed: one test covering three reference datasets.
- Reapplying the exact locked installer passed. Activation was verified across repeated sourcing.
- `python tools/check_docs.py --self-test` exits 1 for two existing missing `scientific-amendment-source-checks` anchors in the source register; all eight checker self-tests pass. Treat this as a documented repository defect, not a dependency failure, and do not suppress it.

Run relevant checks against the current snapshot rather than treating historical passes as current gate evidence. The recorded full gate pytest commands refer to future tests; a zero-test or missing-test run is not acceptance.

MACE 0.3.16 sets an unsafe-loading variable on top-level import. The weight-free smoke helper clears it immediately, then imports trusted e3nn constants within `torch.serialization.safe_globals([slice])`. Do not add a global unsafe-loading override or monkey-patch `torch.load`. Approved pretrained checkpoint loading remains separate work.

## Reproducing the setup in another cloud task or machine

The prepared cloud filesystem retains `/workspace/.onboarding/atom-mlmm`, including the installed environments, verified bootstrap, exact SHA-256 Conda locks, 51 hash-locked pip wheels and tested installer. Saved cloud draft fields contain install/startup instructions; saving them does not itself publish a snapshot or validate a newly spawned task.

Git contains the handoff, locks, scripts and evidence. **Git does not contain installed packages or the wheel archive.** Another machine needs the prepared cloud snapshot or the separately supplied `atom-mlmm-setup-linux-64.tar.gz` bundle. The Git bundle and setup bundle serve different purposes: the former transfers the required parent branch, the latter recreates dependencies.

Extract the setup bundle and follow its README. Install into a new directory with `ATOM_MLMM_SETUP_ROOT=/your/chosen/directory bash install.sh`, then source that directory's `activate.sh`. The installer reuses exact artifact hashes; do not guess replacement versions when an artifact or API is unavailable. Test a new runtime before claiming it is usable. Maintain Linux x86_64 for these locks; other platforms need their own recorded environment solve.

## Blockers, dependencies and reporting to the user

The user wants autonomous progress in cloud and explicit explanations of any blockage. Do all useful authorized independent work first. Distinguish unfinished work, prerequisite reviews, unavailable resources and confirmed failures. For each blocked task report its ID/scope, observed evidence, reason, remaining independent work and the smallest concrete action that resolves it. Do not label an unattempted later task blocked merely because it might be costly.

| Item | Current state and what resolves it |
|---|---|
| M00 | Unfinished review work that can progress in cloud; record the review/decisions required by its page. Installation alone is not design acceptance. |
| G00-T1 / G01 | Depend on the relevant recorded M00 review and applicable earlier CPU evidence. These are development prerequisites, not demonstrated cloud access failures. |
| G00-T2 / later real-model checks | No approved checkpoint or loading evidence was produced. The user's instruction **not to download model weights yet** still applies. An explicitly approved asset, permitted use, digest and the prescribed loading checks are needed before real-model claims. This does not block core analytic CPU work. |
| G00-T3 | Optional GPU profile is unrun; this machine's validated workflow is CPU. CUDA library installation is not proof of available GPU hardware or correct placement. |
| Documentation checker | Two reproducible existing anchor failures. Report them and repair only in an appropriate documented task; never convert the failing check into a claimed pass. |

The user has not cancelled the scientific invariants, trusted-asset rules or review requirements. There is no known external blocker to preparing the next CPU task on this branch lineage. Do not stop at a plan or package inventory; carry the assigned task through its required checks and worker/audit handoff. Do not push or merge to main, and do not imply that remote publication, model qualification or gate acceptance happened without evidence.
