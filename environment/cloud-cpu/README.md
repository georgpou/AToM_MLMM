# CPU development environment

This is the maintained Linux x86_64 setup for analytic CPU development. The branch includes two exact Conda locks, 51 hashed pip wheels, three full pinned upstream source archives, inventories, activation scripts and checks. Miniforge and Conda artifacts are downloaded during installation. The approved academic MACE-OFF23-small checkpoint is carried separately under `models/` for the link-atom example. GPU and complete model qualification are separate profiles.

## Install and record the result

Start from the current development branch as described in [README](../../README.md#start-here). Run in Bash from the repository root:

```bash
bash environment/cloud-cpu/install.sh
source /workspace/.onboarding/atom-mlmm/activate.sh
python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"
python -m pytest -q
```

The default prefix is external to the repository. To customize it:

```bash
ATOM_MLMM_SETUP_ROOT=/absolute/writable/path/atom-mlmm bash environment/cloud-cpu/install.sh
source /absolute/writable/path/atom-mlmm/activate.sh
python /absolute/writable/path/atom-mlmm/validate.py --repository "$PWD"
```

Use the same prefix on replay. The installer verifies `bundle.sha256` before installation, uses exact artifact locks without solving a replacement package set, and preserves each command's output/status in `<prefix>/logs/` plus `<prefix>/latest-validation.json`. Replaying the installer copies current maintained helpers into the prefix before checking them. It leaves repository files unchanged.

Requirements: Linux x86_64, glibc 2.28+, Bash, curl, tar, sha256sum, system CA certificates at `/etc/ssl/certs/ca-certificates.crt`, a writable prefix and Conda's standard `~/.conda` registry. Allow at least 16 GB free disk for installation/cache. Activation uses two CPU threads. A GPU/system CUDA installation is unnecessary for this profile.

Network: `github.com` and `release-assets.githubusercontent.com` for Miniforge 26.7.2-0, `conda.anaconda.org` for exact conda-forge artifacts. Bootstrap SHA-256: `281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05`. TLS, Conda SHA-256 URL hashes, bundle and wheel hashes remain checked. Replay needs no PyPI or model-hosting download.

## Two environments

| Prefix directory | Purpose | Selected locked versions |
|---|---|---|
| `env` | ML/AToM, OpenMM, preparation interfaces and analysis | Python 3.11.16; NumPy 2.4.6; CPU PyTorch 2.8.0; OpenMM 8.6.1; OpenMM-ML 1.8; MACE 0.3.16/e3nn 0.4.4; TorchANI 2.9.0; MDTraj 1.11.1; PyMBAR 4.0.3; OpenFF toolkit 0.18.0; openmmforcefields 0.16.0; AToM 8.5.0b0 |
| `amber-env` | AmberTools executables and Python utilities | Python 3.11.16; AmberTools 26.0 CPU; NumPy 1.26.4; Biopython 1.85 |

Amber's Python utilities need NumPy below 2 while the main MDTraj/matscipy stack needs NumPy 2. Keep the environments separate. Main activation retains main Python, sets `AMBERHOME=<prefix>/amber-env`, and exposes `antechamber`, `parmchk2`, `tleap` and `sqm` after main `bin`. Main OpenFF/openmmforcefields calls these executables. Amber Python scripts retain their own interpreter.

For direct Amber Python work and return to main:

```bash
source /workspace/.onboarding/atom-mlmm/activate-amber.sh
python -c 'import sys, numpy; print(sys.executable, numpy.__version__)'
source /workspace/.onboarding/atom-mlmm/activate.sh
python -c 'import sys, numpy; print(sys.executable, numpy.__version__)'
```

Use your custom prefix if applicable. Main activation applies the core pip constraints; Amber activation removes them. Keep incompatible backends in separate profiles. OpenMM's locks include CUDA/ROCm libraries; this does not make CPU PyTorch or GPU execution qualified.

## Versions and sources

`core-conda-linux-64.lock` and `amber-conda-linux-64.lock` identify every Conda build and SHA-256 artifact. The matching pip inventories list all Python distributions. `pip-wheels.lock` and `wheels.sha256` identify the 51 supplied main-env wheels. Amber's Python distributions come from its Conda lock, with no separate PyPI step.

| Upstream | Tag | Exact source commit | Package version |
|---|---|---|---|
| [AToM-OpenMM](https://github.com/Gallicchio-Lab/AToM-OpenMM) | v8.5.0 | `9e26c5a3811038be1c98e3be6af4c78cd0dd57a7` | 8.5.0b0 |
| [OpenMM-ML](https://github.com/openmm/openmm-ml) | 1.8 | `a7fb40ebecd031db3a5d1da08202cad6819c366f` | 1.8 |
| [openmmforcefields](https://github.com/openmm/openmmforcefields) | 0.16.0 | `3aa91626db3aeea8e8388c43c42a51bf1d99159e` | 0.16.0 |

Complete source archives and upstream licenses accompany these wheels. Installation extracts them under `<prefix>/sources/`; `upstream-sources.json` identifies them. AToM's tag and its package version are intentionally distinct. Its UWHAM test and three reference datasets are included. `package-identities.json` records original build provenance; wheel replay does not recreate VCS install metadata. `pip-requirements.lock` retains the original source-build inputs; installation uses `pip-wheels.lock`.

## Checks

Validation runs eight environment checks: both exact inventories, both pip dependency checks, OpenMM Reference/CPU installation, weight-free MACE/TorchANI/ASE/native ATM smoke, main OpenFF/GAFF preparation through separate Amber, and upstream AToM UWHAM. Its ninth check verifies local documentation and eight checker self-tests. Strict validation returns nonzero for any failure. Installer environment-only mode still runs and records documentation failures; its exit reflects environment checks. Use strict validation for the complete baseline.

The smoke uses a random untrained MACE model and TorchANI descriptors. The project regression also checks the loading policy after the complete smoke. CPU setup is development evidence; M00 and scientific gates require their own contract tests and reviews.

## Model assets and loading

The user-authorized academic MACE-OFF23-small weights, licence and pinned manifest are in [models/mace-off23-small](../../models/mace-off23-small/). Run [the link-atom example](../../examples/README.md) to evaluate a small local ML/MM system and verify its parent derivatives. Check the pinned digest before loading. The full-module checkpoint uses explicit `weights_only=False` only for those verified trusted bytes, then `MACECalculator(models=...)`; the global unsafe-loading override stays absent.

MACE 0.3.16 sets `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD` in both its top-level and calculator imports. Clear it after each import before later model use. The smoke narrowly allows `slice` via `torch.serialization.safe_globals([slice])` while importing trusted e3nn packaged constants, then restores the prior allowance. Preserve the safe default and never enable a global unsafe loader.

Real-model work in G00-T2/G05 requires an approved local checkpoint, digest, allowed use, architecture/elements/domain/output convention and a fresh-process loading test. Follow [S07](../../docs/project-0/specs/S07-artifacts-and-qualification.md#loading-restart-and-workers). The package license does not establish checkpoint permissions. Avoid silent downloads or replacement assets. A scoped compatibility change must apply to the identified trusted artifact and receive its own regression; the weight-free smoke does not qualify arbitrary checkpoints.

## GPU qualification

Create a separate GPU profile when hardware/model work needs it. Record the driver/device, OpenMM platform/precision and PyTorch runtime/build, then run the relevant energy/force, mapped-state, loading, restart and worker-device checks. Calibrate GPU precision against independent CPU references. GPU/model tests use the markers documented in [DEVELOPMENT](../../docs/DEVELOPMENT.md#commands). Current CPU passes leave that profile pending.

## Troubleshooting

- A bundle checksum failure means an incomplete or modified artifact; inspect the current branch and the exact failing file. Preserve hashes and restore the intended bytes.
- A network failure needs access to the destinations above. Preserve proxy/CA settings and inspect the failed URL/status.
- A sandbox write denial at `~/.conda` needs narrow access to Conda's standard registry in addition to the prefix. Preserve HOME and the failed log; use another empty prefix after an interrupted bootstrap.
- Check the active interpreter, `AMBERHOME`, Amber executable paths and pip constraints before scientific work. Activate through the supplied scripts in each shell.
- The replay `ocl-icd-system` existing-symlink warning and missing optional ML acceleration extensions were nonblocking for tested Reference/CPU work. Leave them alone unless a relevant CPU check fails or you qualify OpenCL/GPU. Keep warnings visible.

`cloud-install.sh` is the optional Cloud setup hook. Prefer configuring the checkout on the development branch; if setup files are absent, the hook obtains the current development branch's artifacts without changing the checkout. [CLOUD_START.md](CLOUD_START.md) is a short Cloud startup instruction.
