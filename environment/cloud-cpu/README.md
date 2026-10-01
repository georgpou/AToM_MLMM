# Reproduce the working ML/MM and AmberTools environments

This is the operational **core-analytic-cpu** development setup. Everything that
was missing from the previous handoff is now carried by the Git branch: all 51
pip wheels, full pinned upstream source archives (including AToM regression
inputs), both exact Conda locks, both Python version inventories, constraints,
activation scripts and checks. No separate setup tarball or original workspace
is required. Conda packages and the fixed Miniforge bootstrap are downloaded.
There are no pretrained model weights in these artifacts.

## First: create your branch from the setup branch

Read [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md). The user requires the next agent
to start from `m01-g00-cloud-environment-setup`, never `main`. In a clean checkout:

```bash
git fetch origin m01-g00-cloud-environment-setup
git switch --no-track -c m00-architecture-review origin/m01-g00-cloud-environment-setup
git merge-base --is-ancestor origin/m01-g00-cloud-environment-setup HEAD
test "$(git branch --show-current)" != main
```

Choose an unused milestone/gate/task branch name if that name already exists.
Preserve existing changes. Later branches inherit the reviewed predecessor and
remain descendants of this setup lineage. Do not create a worktree unless the
user explicitly requests one; Cloud tasks already have isolated checkouts.

## One-command setup

From the repository root in Bash:

```bash
bash environment/cloud-cpu/install.sh
source /workspace/.onboarding/atom-mlmm/activate.sh
```

The default installation prefix is `/workspace/.onboarding/atom-mlmm`. To choose
a fresh prefix elsewhere on a Linux machine:

```bash
ATOM_MLMM_SETUP_ROOT=/absolute/writable/path/atom-mlmm bash environment/cloud-cpu/install.sh
source /absolute/writable/path/atom-mlmm/activate.sh
```

Always invoke the installer from this branch's `environment/cloud-cpu` directory
as shown, rather than the historical evidence directory. It installs into the
chosen external prefix and leaves repository files unchanged. Run it again to
replay the same locks and checks. It stops on installation failure and preserves
the exact output and exit status; it never solves a replacement package set.

Requirements: Linux x86_64, glibc 2.28 or newer, Bash, curl, tar, sha256sum, system
CA certificates at `/etc/ssl/certs/ca-certificates.crt`, a writable prefix and
Conda's standard `~/.conda` registry. Allow at least 16 GB free disk space for a
fresh installation and its package cache. The checks use two CPU threads.
Neither a GPU nor system CUDA is needed. OpenMM's locked packages include
CUDA/ROCm libraries, as permitted by the user; PyTorch remains its CPU build.

Network destinations: `github.com` and `release-assets.githubusercontent.com`
for Miniforge 26.7.2-0, and `conda.anaconda.org` for exact conda-forge artifacts.
Fetching this repository also uses GitHub. PyPI and model-hosting services are
not needed during replay. Existing platform HTTPS Git authentication suffices
for the repository; no new token is part of this setup.

The bootstrap SHA-256 is
`281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05`.
TLS, Conda SHA-256 URL hashes, the complete bundle manifest and pip wheel hashes
are checked. Do not disable verification to repair a download failure.

## Two environments, one preparation workflow

| Environment under the prefix | Purpose | Selected versions |
|---|---|---|
| `env` | Main AToM, ML potentials, OpenMM and analysis | Python 3.11.16; NumPy 2.4.6; CPU PyTorch 2.8.0; OpenMM 8.6.1; OpenMM-ML 1.8; MACE 0.3.16; e3nn 0.4.4; TorchANI 2.9.0; MDTraj 1.11.1; PyMBAR 4.0.3; OpenFF toolkit 0.18.0; openmmforcefields 0.16.0; AToM 8.5.0b0 from tag v8.5.0 |
| `amber-env` | AmberTools preparation executables and its Python utilities | Python 3.11.16; AmberTools 26.0 CPU; NumPy 1.26.4; Biopython 1.85 |

The complete versions/builds are in `core-conda-linux-64.lock` and
`amber-conda-linux-64.lock`. `core-pip-inventory.txt` and
`amber-pip-inventory.txt` list every installed Python distribution, including
those supplied by Conda. `pip-wheels.lock` specifies the 51 additional main-env
distributions with hashes; there is no separate Amber PyPI installation step.
Amber's bundled Python distributions are supplied by its locked Conda artifact.
Do not try to fetch those distribution names independently from PyPI.

Main activation sets `AMBERHOME=<prefix>/amber-env` and appends its `bin` directory
after the main environment's `bin`. Main `python` therefore remains NumPy 2,
while `antechamber`, `parmchk2`, `tleap` and `sqm` run from AmberTools. Amber's
Python scripts use their own interpreter. This is how OpenFF/openmmforcefields
in the main environment calls the separate preparation tools.

For work with AmberTools Python utilities, explicitly switch:

```bash
source /workspace/.onboarding/atom-mlmm/activate-amber.sh
python -c 'import sys, numpy; print(sys.executable, numpy.__version__)'
source /workspace/.onboarding/atom-mlmm/activate.sh
python -c 'import sys, numpy; print(sys.executable, numpy.__version__)'
```

Use your chosen prefix in those commands if you changed the default. Do not
install AmberTools into the main environment: its bundled Python utilities
require NumPy below 2, while this main stack's MDTraj/matscipy requires NumPy 2.
This is a Python dependency conflict, not evidence that all Amber executables
require NumPy 1. Main activation sets `PIP_CONSTRAINT` to the core constraints;
Amber activation removes it. Use a separate profile for incompatible ML extras
and qualify compatible additions before updating these reproducible locks.

The repository's original candidate YAML and scientific specifications remain
unchanged. The two-environment arrangement is the user's agreed operational
setup; formal M00/G00 review must account for it. Installation is not acceptance
of any scientific gate, model or GPU profile.

## Sources and package provenance

These archives are unmodified `git archive` outputs from the exact commits used
to build the three supplied source wheels. `upstream-sources.json` and
`bundle.sha256` identify them. Their upstream licenses remain inside the archives
and wheels; AToM's corresponding complete source is supplied alongside its wheel.

| Upstream repository | Selected tag | Full commit | Distribution version |
|---|---|---|---|
| [AToM-OpenMM](https://github.com/Gallicchio-Lab/AToM-OpenMM) | v8.5.0 | `9e26c5a3811038be1c98e3be6af4c78cd0dd57a7` | 8.5.0b0 |
| [OpenMM-ML](https://github.com/openmm/openmm-ml) | 1.8 | `a7fb40ebecd031db3a5d1da08202cad6819c366f` | 1.8 |
| [openmmforcefields](https://github.com/openmm/openmmforcefields) | 0.16.0 | `3aa91626db3aeea8e8388c43c42a51bf1d99159e` | 0.16.0 |

The installer extracts these under `<prefix>/sources/`. The AToM checkout
includes `tests/test_uwham.py`, its three reference datasets and the upstream
pytest configuration; the test function is named `_test_uwham_analysis`.
Use the supplied source and configuration, not a similarly named test from a
moving branch. `pip-requirements.lock` records original source-install inputs;
replay uses the supplied wheels and `pip-wheels.lock`, without rebuilding.
`package-identities.json` records provenance of the original successful build.

If a Git checkout is needed for development, fetch the full commit from the
listed upstream URL into a separate directory and verify `git rev-parse HEAD`
equals that commit. Tags alone and package-reported versions are insufficient.

## Checks and recorded outcomes

The installer automatically runs both complete version/build comparisons, both
`python -m pip check` commands, OpenMM's installation test, CPU MACE/TorchANI/
ASE/native ATM smoke checks, main OpenFF/GAFF preparation through separate
AmberTools, the upstream AToM UWHAM regression, and the documentation self-test.
It retains all individual command outputs and exit codes in `<prefix>/logs/`
and writes `<prefix>/latest-validation.json`.

To run the checks again after main activation, from the repository root:

```bash
python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"
```

This strict validation command exits nonzero for any failing check. The
installer invokes it with `--environment-only`: all checks still run and all
failures are printed/recorded, but the installer's status reflects environment
checks. The repository has two existing missing
`scientific-amendment-source-checks` anchors; the docs command exits 1 while its
eight self-tests pass. That separate repository defect is not suppressed or
described as a pass. Any dependency, CPU, preparation or upstream-test failure
still fails installation.

The CPU smoke uses a random untrained MACE model and TorchANI descriptors.
MACE 0.3.16 sets `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD` at import; the helper clears
it and narrowly allows the builtin `slice` for trusted e3nn packaged constants
via `torch.serialization.safe_globals([slice])`. Do not enable global unsafe
loading. Pretrained checkpoint loading remains unqualified and weights must
not be downloaded without the user's authorization.

Fresh-install evidence and exact commands are recorded in
[the reproduction worker log](../../Worker_Log/Documentation/Cloud_CPU_Reproduction_v1_worker.md).
Historical setup evidence describes the earlier local installation; it does
not replace this branch-contained installer.

## If setup fails

Read the exact failing command in `<prefix>/logs/install-*.log` and the individual
validation logs. Preserve the failure rather than guessing new versions.

- Missing wheels or archives: confirm you fetched this setup branch's latest
  tip, not `main` or an older child. There must be 51 actual `.whl` files, not
  Git LFS pointer files. `sha256sum -c bundle.sha256` from this directory must pass.
- HTTPS 403: check Cloud egress access to the three required destinations above;
  allowlist settings and actual runtime access are separate. Retest the failed
  destination before claiming a network change applied.
- A write denial for `~/.conda`: the standard Conda environment registry needs
  access in addition to the installation prefix. In a sandboxed task, request
  the narrow filesystem escalation for the installer through the command tool;
  do not change `HOME` or disable the sandbox as a workaround.
- An interrupted bootstrap can leave a partial `conda` directory. Preserve its
  log and choose another empty prefix for a clean reproduction.
- Both environments must be activated through the supplied scripts. A bare
  system Python, missing `AMBERHOME`, or a GPU PyPI Torch reinstall is a different
  environment. Check `which python`, `python -m pip check`, `which antechamber`
  and the exact-version check before attempting scientific work.

Report genuine blockers with the failing command, exit status, reason and the
smallest action needed to resolve them; continue independent authorized work.
