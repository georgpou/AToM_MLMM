# Cloud agent startup

Use the existing repository checkout; Cloud tasks already have isolated
workspaces. Do not create a worktree unless explicitly requested by the user.
Never do project work on main. The next agent must fetch
`m01-g00-cloud-environment-setup` and create an unused milestone/gate/task branch
directly from its latest tip. Later branches retain reviewed predecessor work
and remain descendants of this setup lineage. Preserve existing user changes.
Read AGENT_HANDOFF.md and AGENTS.md on the setup branch before starting; if they
are missing from the initial checkout, use git show on the fetched setup ref.

For dependencies read environment/cloud-cpu/README.md, ATM_MLMM_Environment.md
and ATM_MLMM_environment.yml. The operational setup is two separate Python 3.11
environments, with all replay wheels and pinned source archives in the branch.
From the repository root run `bash environment/cloud-cpu/install.sh` if needed.
No separate tarball or filesystem snapshot is required. The saved Cloud install
script can obtain these files from the side branch when the initial checkout
lacks them, without changing tracked files or main. Copying a Git branch and
publishing a Cloud snapshot are distinct operations.

In every new Bash session activate the main environment with
`source /workspace/.onboarding/atom-mlmm/activate.sh` (substitute the chosen
ATOM_MLMM_SETUP_ROOT prefix if customized). Main: Python 3.11.16, NumPy 2.4.6,
CPU PyTorch 2.8.0, OpenMM 8.6.1, OpenMM-ML 1.8, MACE 0.3.16/e3nn 0.4.4,
TorchANI 2.9.0, PyMBAR 4.0.3 and AToM tag v8.5.0/package 8.5.0b0.
Exact full package inventories and Conda builds are in the setup directory.

AmberTools 26.0 uses a SEPARATE environment with NumPy 1.26.4. Main activation
sets AMBERHOME to its prefix and exposes antechamber/parmchk2/tleap/sqm after
main Python in PATH. Amber's scripts keep their own interpreter; main Python
does not change to NumPy 1. For AmberTools Python work source the prefix's
activate-amber.sh; source activate.sh again to return to ML/MM. Do not merge
the environments or replace the CPU Torch build with a PyPI GPU distribution.
Keep the core constraints when adding compatible packages; use a separate
profile for incompatible backends and record new qualification evidence.

Installer logs and latest-validation.json are under the installation prefix.
Both exact inventories, both pip checks, OpenMM Reference/CPU installation,
weight-free MACE/TorchANI/ASE/native ATM smokes, separate Amber preparation
and upstream AToM UWHAM regression passed in an empty-prefix reproduction.
The original bootstrap and package cache were not reused. Documentation
self-test still exits 1 for two existing scientific-amendment-source-checks
anchors; all eight self-tests pass. Report the defect separately and preserve
all exit codes. Strict validate.py fails on docs too; installer environment-only
mode still executes, prints and records docs failures. No services must restart.

No scientific gate or model/GPU profile is accepted by installation. M00 review
is the first unfinished prerequisite unless newer accepted evidence exists.
Read STATUS.md and the assigned task's actual prerequisites. Preserve scientific
specifications and historical worker logs. Do not download any pretrained
model weights unless explicitly authorized. MACE's unsafe import-time loading
override must be cleared; use only the documented scoped safe_globals handling
for trusted e3nn constants. Checkpoint loading was not qualified. Preserve TLS,
artifact hashes and platform Git authentication; never embed credentials.

For any blocker report its exact command, exit code, reason and smallest action
to resolve it, and complete independent authorized work. See the reproduction
worker log for evidence; smoke checks do not substitute for scientific gates.
