# CPU development setup

This machine has two Python environments, both Linux x86_64/Python 3.11. The main AToM/ML environment uses NumPy 2.4.6 and CPU PyTorch 2.8.0. AmberTools 26 and its Python utilities use a separate NumPy 1.26.4 environment. Both passed pip check. Main activation exposes AmberTools executables without changing the main Python interpreter.

In this cloud workspace:

```bash
source /workspace/.onboarding/atom-mlmm/activate.sh
```

For direct AmberTools Python utilities:

```bash
source /workspace/.onboarding/atom-mlmm/activate-amber.sh
```

Activate main again to return to AToM/ML. Keep the environments separate. Do not install AmberTools into main or let a plain PyPI Torch reinstall replace the CPU Conda build. The main activation sets core pip constraints, writable caches and system CA trust. CUDA/ROCm libraries supplied with OpenMM are allowed, but only CPU execution was checked.

For another Linux x86_64 machine, extract the setup bundle into a temporary directory and use a new installation directory:

```bash
ATOM_MLMM_SETUP_ROOT=/your/chosen/atom-mlmm-directory bash install.sh
source /your/chosen/atom-mlmm-directory/activate.sh
python /your/chosen/atom-mlmm-directory/smoke_cpu.py
python /your/chosen/atom-mlmm-directory/smoke_prep.py
```

The installer downloads the fixed Miniforge release over verified TLS, checks its official SHA-256, installs exact Conda artifacts with their SHA-256 URLs, verifies all archived pip wheel hashes, and installs 51 pinned pip distributions from those local wheels. AmberTools' bundled Python distributions are already contained in its Conda artifact; they must not be independently fetched from PyPI. Internet access to GitHub release assets and conda-forge is needed on a fresh machine. Current-cloud refresh was tested with both environments passing pip check and OpenMM's Reference/CPU installation check; reproduction in a different machine/new cloud task was not performed.

The bundle includes package code, locks and smoke helpers, not pretrained weights. The three source-based packages were built from exact upstream commits recorded in package-identities.json and pip-requirements.lock. MACE 0.3.16/e3nn 0.4.4 has a PyTorch loading compatibility issue: the weight-free smoke helper clears MACE's import-time unsafe-loading override, then uses a scoped builtin slice allowlist to import trusted e3nn constants. This does not qualify loading a pretrained checkpoint. No application or scientific gate was implemented.

Validated: CPU tensors, random untrained MACE energy/forces, TorchANI descriptors/derivatives, direct ASE/OpenMM energy and force agreement, PythonForce inside native ATMForce, main OpenFF/GAFF preparation through separate AmberTools, and the existing AToM UWHAM regression (one test covering three datasets). The repository documentation checker still reports two existing missing source-register anchors; all eight self-tests pass. See the worker log and validation-target-v2.json for exact outcomes.
