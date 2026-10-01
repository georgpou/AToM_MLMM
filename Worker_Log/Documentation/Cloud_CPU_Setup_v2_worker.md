# Project 0 CPU cloud setup - attempt 2 - worker

**Scope:** Reusable CPU development installation only, on `m01-g00-cloud-environment-setup`. The branch uses M01/G00 as the environment-work locator; no gate is implemented or qualified.**Outcome:** ready_for_audit for the installation scope.**Model/version:** Codex, GPT-6 family; exact API/model version not exposed.**Reasoning setting:** not exposed.**Finished:** 2026-10-01T10:34:43.918143+02:00**Previous worker:** Cloud_CPU_Setup_v1_worker.md (preserved); no independent audit.

## Snapshot and references

Base commit `2d7bcc94f901738e39f536f16de84699d4e8d631`. Existing tracked files remain unchanged. This attempt adds only this log and generated setup/evidence files under `Worker_Log/Documentation/evidence/Cloud_CPU_Setup_v2/`. A full repository file hash manifest identifies the delivered files; no commit, push, independent review, scientific gate pass or publication is claimed.

Read AGENTS.md (all), README.md (current state and documentation check), ATM_MLMM_Environment.md (installation, packages, provenance, model-loading scope), ATM_MLMM_environment.yml (complete candidate), STATUS.md (current qualification scope), and worker-log template. Used the cloud-environment-onboarding setup and onboarding reference, systematic debugging and verification skills. Inspected upstream installed package metadata and source for actual dependency/API behavior. Linux x86_64; 5 visible CPUs, 33 GiB RAM; use 2 CPU threads. No production simulation or pretrained model asset was launched/downloaded.

## Changes and decisions

The first attempt's network restriction was resolved in the running instance: Conda-forge, PyPI and tagged Git reads succeeded. The micromamba bootstrap redirect still returned 403, so used Miniforge 26.7.2-0, verified against its official release SHA-256 `281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05`. Created the package manager's registry directory through approved sandbox escalation. Restored Git/pip TLS trust with the actual machine's system CA bundle, without disabling verification. The initial VCS installation's exact TLS failure remains in `full-install.log`.

The candidate Conda specification solved with its pinned core versions but included CUDA/ROCm dependencies via OpenMM. The user explicitly allowed those libraries; validation remains CPU only. The user also allowed version adjustments for operational stability, then accepted separating AmberTools from ML. No scientific specification, dependency declaration or tracked lockfile was modified.

Two Python environments live in the same cloud workspace:

- Main: `/workspace/.onboarding/atom-mlmm/env`, Python 3.11.16, NumPy 2.4.6, CPU PyTorch 2.8.0, OpenMM 8.6.1, OpenMM-ML 1.8, MACE 0.3.16/e3nn 0.4.4, TorchANI 2.9.0, MDTraj 1.11.1, PyMBAR 4.0.3, OpenFF toolkit 0.18.0, openmmforcefields 0.16.0 and AToM v8.5.0 source (package version 8.5.0b0).
- Preparation: `/workspace/.onboarding/atom-mlmm/amber-env`, Python 3.11, AmberTools 26.0 CPU build, NumPy 1.26.4 and Biopython 1.85, plus the missing declared utility dependencies. Bundled `ndfes`, `fetkutils`, `proprep` and `edgembar` require NumPy<2; MDTraj/matscipy in main require NumPy 2. This does not establish that compiled Amber programs require NumPy 1.

Main activation exports `AMBERHOME` and adds the preparation executable directory after the main interpreter directory. AmberTools scripts use their own interpreter. Cross-environment CLI and Python force-field generation were verified. openmmforcefields was installed from its exact 0.16.0 source commit rather than its Conda package, whose dependency would pull AmberTools back into main. Explicit runtime helpers include ParmEd, lxml, tinydb and validators. Three VCS identities and every resolved package are recorded in evidence.

MACE 0.3.16 sets a global unsafe-loading variable on top-level import. For weight-free smoke validation, cleared it immediately and allowed only the builtin `slice` during trusted e3nn packaged-constant loading with `torch.serialization.safe_globals([slice])`. No package loader was patched, no global unsafe override was saved, and pretrained checkpoint loading is still unqualified. A safe default import initially failed on `slice`; the narrowly scoped supported allowlist resolved that check.

Saved confirmed draft fields: `install_script` and `start_skill`. The draft installation calls the retained tested installer, which uses SHA-256 Conda locks and 51 hash-locked pip wheels. The installed snapshot retains all runtime files outside the checkout. Saved startup includes main/Amber activation, CPU checks, exact source identities, the existing documentation failure and the model-loading limits. Saving is not publication or validation in a new task.

## Checks

Exact commands, working directories, exit codes and complete stdout/stderr are in `evidence/Cloud_CPU_Setup_v2/validation-target-v2.json`.

| Check | Observed result |
|---|---|
| Main `python -m pip check` | exit 0, no broken requirements |
| Amber interpreter `python -m pip check` | exit 0, no broken requirements |
| `python -m openmm.testInstallation` | exit 0, Reference and CPU forces within tolerance |
| `python smoke_cpu.py` | exit 0; CPU tensor operation, random untrained MACE energy/forces, TorchANI descriptors/derivatives, direct ASE/OpenMM agreement, ASE PythonForce inside native ATMForce |
| `python smoke_prep.py` | exit 0; main OpenFF/GAFF 2.2.20 calls separate AmberTools and evaluates finite OpenMM CPU energy/forces for methane |
| Upstream AToM `python -m pytest -q tests/test_uwham.py` | exit 0; 1 test passed, exercising its 3 archived dataset assertions |
| CLI `antechamber`, `parmchk2`, `tleap`, then load Amber topology/coordinates into OpenMM CPU | exit 0; generated 5-particle methane system, finite energy/forces |
| Reapply `bash /workspace/.onboarding/atom-mlmm/install.sh` | exit 0; locks/wheel checks verified, both pip checks and OpenMM installation check passed |
| Activate main twice, then run validation | succeeded; main interpreter retained, Amber tools callable |
| `python tools/check_docs.py --self-test` | exit 1; all 8 checker self-tests passed, 2 existing broken source-register heading links remain |

Initial package checks revealed missing AmberTools utility requirements and NumPy/Biopython conflicts. Splitting environments and installing declared utility dependencies resolved them. Source openmmforcefields runtime checks additionally detected missing ParmEd/lxml; the final explicit dependencies and integration check passed. Tests using missing API defaults were corrected in smoke helper invocation, without production or scientific code changes. Optional GPU, trained potential loading, physical adequacy, protein production, numerical gates and independent audit were not run or claimed.

## Findings and next handoff

CPU dependency development is operational in the current machine and reusable configuration is saved. The documentation command remains failed due to the pre-existing absent `scientific-amendment-source-checks` heading referenced by ATM_MLMM_Environment.md and Worker_Log/Milestone_00/Documentation_v4_worker.md. This is a repository documentation defect, not an installation blocker; no protected file was repaired.

Main activation: `source /workspace/.onboarding/atom-mlmm/activate.sh`. For direct Amber Python work: `source /workspace/.onboarding/atom-mlmm/activate-amber.sh`. Keep those Python dependency sets separate on other machines. Exact locks and a portable wheel/setup bundle are retained outside the repository. User publication and validation in a new cloud task remain unperformed platform steps. Matching future audit filename: `Cloud_CPU_Setup_v2_audit.md`; none exists and no independent acceptance is claimed.

Delivered snapshot manifest: `evidence/Cloud_CPU_Setup_v2/repository-manifest.sha256` (all Git-visible files except the manifest itself).
