# Project 0 ATM-ML/MM Conda Environment

**File:** `Project_0_ATM_MLMM_environment.yml`  
**Purpose:** reproducible starting environment for the Project 0 ATM + ML/MM + link-atom development and qualification work  
**Research/verification date:** 29 September 2026  
**Initial qualification platform:** Linux x86_64, Python 3.11  
**Status:** environment specification; the combined stack still has to pass the Project 0 software qualification gates

## 1. What this environment is for

This environment is intentionally designed for the first Project 0 implementation rather than for every future ML/MM problem.

The project needs one environment in which we can:

1. build and inspect ordinary OpenMM molecular systems;
2. replace a selected molecular region with an ML potential using OpenMM-ML;
3. construct link atoms at protein ML/MM boundaries;
4. evaluate the resulting hybrid system through the native OpenMM `ATMForce` machinery;
5. hand the validated system to AToM-OpenMM for ABFE and RBFE workflows;
6. evaluate MACE potentials, beginning with MACE-OFF23-small;
7. analyse the resulting free-energy data independently with PyMBAR; and
8. run the deterministic/unit/integration tests needed to prove that each layer is behaving correctly.

This follows the architecture of Project 0: the ML/MM layer should define a valid potential-energy function and ATM should operate on that function, rather than the ML model having special ATM logic. The original plan explicitly defined Project 0 around a local/short-range MLIP, mechanical embedding, a complete ML ligand, selected protein atoms, link atoms, explicit solvent, ABFE/RBFE, and OpenMM execution. [Original plan, lines 74-110](./Project_0_ATM_MLMM_Design_and_Validation_Plan.md#L74)

## 2. The important version choices

### OpenMM 8.6.1

`openmm=8.6.1` is the molecular-dynamics engine used by the first qualification stack. This is deliberate rather than merely using the version named by older AToM examples.

OpenMM 8.6.1 is currently available from conda-forge. More importantly for this project, the OpenMM-ML 1.8 source requires OpenMM >=8.6.1, so OpenMM 8.5 should not be used as the baseline for the OpenMM-ML 1.8 configuration. OpenMM 8.6.1 was released on 11 September 2026. [OpenMM conda packages](https://anaconda.org/channels/conda-forge/packages/openmm/files) [OpenMM 8.6.1 on PyPI](https://pypi.org/project/OpenMM/8.6.1/)

### OpenMM-ML 1.8

The Project 0 design depends on the recently added mechanical-embedding/link-atom machinery. The environment therefore installs the `1.8` source tag directly from the OpenMM-ML repository.

This is installed through pip because the project needs the exact tagged source while we qualify the behavior. We do **not** use the moving `main` branch.

The original plan already identified OpenMM-ML 1.8 as the component providing link atoms as virtual sites and the `oldToNew` atom-index mapping. fileciteturn0file0L424-L435

### AToM-OpenMM v8.5.0

The environment installs the `v8.5.0` Git tag rather than whatever happens to be on the default branch when the environment is created.

This distinction matters because AToM is still active research software. Its published PyPI history currently exposes `8.5.0b0` as a pre-release, while the Project 0 plan is specifically built around the inspected `v8.5.0` source tree. The exact Git commit must therefore be captured after installation and stored with every qualification result. [AToM-OpenMM PyPI](https://pypi.org/project/atom-openmm/8.5.0b0/)

The environment is intentionally not claiming that AToM v8.5.0 + OpenMM 8.6.1 + OpenMM-ML 1.8 have already been runtime-qualified together. That is one of the first Project 0 gates.

### PyTorch 2.8.0

PyTorch provides the tensor backend used by MACE. Version 2.8.0 is the candidate baseline specified in the Project 0 plan.

The portable Conda file uses the PyTorch Conda package and does not embed a particular CUDA runtime. This makes the file useful for CPU qualification and avoids forcing one GPU runtime onto every machine.

For GPU work, the same Python-level environment should be created first, then the CUDA-enabled PyTorch/OpenMM packages appropriate to the target NVIDIA/AMD stack should be selected and separately qualified. Do not silently change CUDA packages in an already qualified environment.

### MACE 0.3.16

`mace-torch==0.3.16` is the first MLIP implementation being qualified. The package is the reference PyTorch implementation of the MACE equivariant neural-network potential. Its PyPI release 0.3.16 is a pure-Python wheel/source release and supports Python >=3.9. [MACE 0.3.16 on PyPI](https://pypi.org/project/mace-torch/)

MACE is included because Project 0 needs one real local ML model after the analytic/`PythonForce` tests pass. We start with a single approved model instead of supporting every OpenMM-ML backend at once.

### e3nn 0.4.4

`e3nn` supplies the equivariant tensor operations on which MACE relies. The project pins `0.4.4` because that is the compatibility point used by the selected MACE 0.3.16 qualification path. The exact build must be retained in the resolved environment.

Conda-forge still provides e3nn 0.4.4, so there is no reason to let the solver silently move to the current 0.5/0.6 series while we are testing a specific MACE integration. [e3nn conda-forge files](https://anaconda.org/conda-forge/e3nn/files)

### AmberTools 26.0

AmberTools is not part of the ML force itself. It is included because the AToM-OpenMM ecosystem uses Amber-style preparation tools and because later Project 0/Project 1 fixtures are expected to start from conventional biomolecular systems.

The current conda-forge package is AmberTools 26.0. It supports Linux x86_64 and other platforms. [AmberTools on conda-forge](https://anaconda.org/conda-forge/ambertools)

The core deterministic tests should not depend on AmberTools. That keeps software failures in topology preparation separate from the ATM/ML/MM force-composition tests.

### openmmforcefields 0.16.0

This package supplies force-field and small-molecule parameterization utilities used around OpenMM. It is included for preparing realistic Project 1 systems without introducing a second molecular-dynamics engine.

Version 0.16.0 is currently available from conda-forge. Its recent behavior also makes explicit force-field selection important, which is why the Project 0 documentation should always record the exact force-field identity rather than accepting a package default implicitly. [openmmforcefields 0.16.0](https://anaconda.org/conda-forge/openmmforcefields/manage)

### configobj 5.0.9

AToM uses ConfigObj-style configuration handling. `configobj` is a small dependency, so including it directly makes the environment's intended configuration layer explicit instead of relying on a transitive dependency to happen to be installed. [configobj on conda-forge](https://anaconda.org/conda-forge/configobj)

### setproctitle

This is a small convenience dependency used by AToM to make worker process names easier to identify. It is not scientifically required and should not be involved in any numerical test.

### NumPy and SciPy

NumPy provides the basic array and numerical data structures used by OpenMM-ML, MACE adapters, geometry checks, and analysis.

SciPy is included for numerical utilities and, importantly, for independent validation tasks such as quadrature of known analytical free-energy examples. This allows us to test the free-energy analysis independently of the same code used to generate a molecular result.

### PyYAML

Project 0 uses YAML for human-readable configuration and manifests. PyYAML is therefore included so configuration can be loaded by the future project-owned CLI without bringing in another configuration language.

### packaging

The `packaging` module is a small utility for reliable version comparisons. It is useful in the environment/provenance checker, where we want clear version failures rather than string comparisons such as `"8.10" < "8.6"`.

### psutil

`psutil` is included only for diagnostics and benchmarking: resident memory, process information, and worker resource checks. It has no role in the physical Hamiltonian.

### PyMBAR 4.0.3

PyMBAR is included as the independent free-energy analysis implementation.

The key reason to have it in Project 0 is independence. AToM's workflow and analysis should not be the only implementation capable of turning the saved reduced potentials into a free-energy estimate. We need a second implementation for known-answer and cross-check tests. PyMBAR 4.0.3 remains available from conda-forge. [PyMBAR on conda-forge](https://anaconda.org/conda-forge/pymbar)

The Project 0 plan also makes clear that uncertainty must account for correlated molecular-dynamics data and that the same raw state energies should be reusable by independent estimators.

### MDTraj

MDTraj is included for trajectory inspection and simple frame-level diagnostics. It is deliberately not the source of any important thermodynamic calculation. Its role is to make it easy to inspect distances, contacts, periodic wrapping, and saved trajectories during debugging.

### pytest and pytest-cov

The test suite is part of the scientific deliverable, not just software hygiene. `pytest` runs the deterministic and integration tests, while `pytest-cov` helps identify untested code paths. A coverage number is not itself a scientific correctness metric; it is only a development aid.

### git, setuptools, and wheel

`git` is required because OpenMM-ML 1.8 and AToM-OpenMM v8.5.0 are installed from Git tags.

`setuptools` and `wheel` are kept in the environment so source builds/installations do not depend on whatever unrelated versions happen to exist in a user's base environment.

## 3. Why some things are deliberately NOT in this file

### No R / legacy UWHAM

The older AToM setup documentation installs an R environment for its legacy UWHAM workflow. Project 0 instead uses the bundled Python-side analysis plus an independent PyMBAR implementation. This is intentional: it reduces the environment size and avoids making an R runtime a prerequisite for the initial scientific qualification.

If later work explicitly requires the legacy R estimator for regression comparison, add it as a separate compatibility environment rather than silently changing the core environment.

### No `espaloma` by default

AToM's installation instructions list `espaloma` among tools useful for system preparation, not as a core requirement of the ATM force itself. Project 0 should begin from a fixed, already prepared MM fixture. Adding another parameterization ML model would otherwise create an additional source of model/version differences before the ATM-ML/MM mechanics have been qualified.

When an actual system-preparation workflow needs `espaloma`, it can be installed in a preparation-specific environment or added after the core environment is stable.

### No general model zoo

We do not install TorchANI, AIMNet2, Orb, FeNNix, TorchMD-Net, or other MLIP stacks simply because OpenMM-ML supports them. Each introduces additional model interfaces, dependencies, serialization behaviors, and scientific assumptions.

Project 0 first proves the architecture with one local MACE model. A second model is added only as a later compatibility qualification.

### No CUDA toolkit in the portable file

There are two different questions:

1. which Python libraries are being used; and
2. which accelerator runtime is installed on a particular compute node.

Those should not be coupled in one portable environment specification until the intended hardware is known. OpenMM 8.6.1 provides CUDA and other accelerator extras, and PyTorch provides hardware-specific builds. The actual GPU combination must therefore be chosen and tested for the target cluster rather than guessed here. [OpenMM 8.6.1 PyPI](https://pypi.org/project/OpenMM/8.6.1/) [PyTorch previous versions](https://pytorch.org/get-started/previous-versions/)

## 4. Installation procedure

### 4.1 Create the environment

Use a current Conda implementation such as Miniforge/Conda or Mambaforge. Mamba is preferable for solving speed, but standard `conda` is sufficient.

```bash
conda env create -f Project_0_ATM_MLMM_environment.yml
conda activate atm-mlmm-p0
```

For subsequent updates:

```bash
conda env update -f Project_0_ATM_MLMM_environment.yml --prune
```

Do not update an already qualified environment blindly. Clone the environment or rebuild it from the specification and re-run the qualification suite.

### 4.2 Verify the core installation

First check package versions:

```bash
python - <<'PY'
import sys
import openmm
import torch
import e3nn
import pymbar
import yaml

print("Python:", sys.version)
print("OpenMM:", openmm.version.version)
print("PyTorch:", torch.__version__)
print("e3nn:", e3nn.__version__)
print("PyMBAR:", pymbar.__version__)
print("PyYAML: OK")
PY
```

Then run the OpenMM installation test:

```bash
python -m openmm.testInstallation
```

Then verify the model packages:

```bash
python - <<'PY'
import importlib.metadata as md
for name in ["mace-torch", "openmmml", "atom-openmm", "openmmforcefields"]:
    try:
        print(f"{name}: {md.version(name)}")
    except md.PackageNotFoundError:
        print(f"{name}: NOT INSTALLED AS A DISTRIBUTION")
PY
```

Finally run:

```bash
python -m pip check
```

The exact output should be saved into the Project 0 environment manifest.

## 5. Important qualification issue: source tags versus resolved commits

The YAML file pins **release/tag identities**, but a scientific reproducibility record should go one step further.

After installation, record:

```bash
git ls-remote https://github.com/openmm/openmm-ml.git refs/tags/1.8

git ls-remote https://github.com/Gallicchio-Lab/AToM-OpenMM.git refs/tags/v8.5.0
```

Then record the exact installed commit identifiers and the complete resolved dependency list:

```bash
conda list --explicit > conda-explicit.txt
conda env export > environment-resolved.yml
python -m pip freeze > pip-freeze.txt
```

Do not replace the original environment specification with these files. Keep both:

- `environment.yml`: the intended top-level environment definition;
- the resolved/explicit files: the actual environment used for a particular qualification run.

This distinction becomes important whenever a tag remains stable but a transitive dependency releases a new compatible build.

## 6. Model checkpoint provenance

Installing `mace-torch` does **not** install the exact MACE-OFF23-small model checkpoint used in Project 0.

The checkpoint must be stored separately, for example:

```text
models/
  mace_off23_small/
    MACE-OFF23-small.model
    MODEL_MANIFEST.yaml
```

The model manifest should contain:

```yaml
asset_id: mace_off23_small
model_name: MACE-OFF23-small
source: <exact source URL>
source_revision: <commit/tag if applicable>
sha256: <64-character SHA256 digest>
energy_output: energy
precision: <actual precision used>
device: <cpu/cuda device>
cutoff_A: <value extracted from model>
license: <exact model-weight license>
```

The code and the model weights are different research objects. A reproducible environment without the exact model asset is not sufficient to reproduce an ML/MM result.

## 7. GPU environment strategy

The first file deliberately establishes the portable Python/software environment. GPU qualification should be a separate, explicit step.

For NVIDIA systems, determine the supported CUDA runtime from the target machine and then install the compatible OpenMM and PyTorch builds. OpenMM 8.6.1 currently exposes `cuda12` and `cuda13` extras through its PyPI distribution; PyTorch also publishes versioned hardware builds. [OpenMM 8.6.1](https://pypi.org/project/OpenMM/8.6.1/) [PyTorch previous versions](https://pytorch.org/get-started/previous-versions/)

Do not infer compatibility from the fact that both packages mention CUDA. The following four items have to be compatible:

```text
NVIDIA driver
       |
       v
CUDA runtime expected by PyTorch
       |
       +---- CUDA/OpenMM build
       |
       +---- GPU architecture
```

After installing a GPU variant, run the same Project 0 deterministic tests used on CPU. Then run a direct native-MACE versus OpenMM-ML force comparison before allowing AToM worker execution.

For multiprocess CUDA execution, preserve the AToM worker's explicit process-start behavior and test the device placement of both OpenMM and PyTorch independently. Do not assume that an OpenMM `DeviceIndex` setting automatically moves a PyTorch model created in the same process.

## 8. What this environment supports immediately

Once the packages are successfully installed, the environment should be capable of supporting development of:

```text
OpenMM analytical test forces
        |
        v
native ATMForce tests
        |
        v
OpenMM-ML 1.8 mechanical embedding
        |
        +---- link atoms / virtual sites
        |
        v
MACE local ML potential
        |
        v
hybrid cavity + ligand ML/MM system
        |
        v
AToM-OpenMM ABFE / RBFE workflow
        |
        v
PyMBAR independent analysis
```

This diagram describes the intended software path. It is not evidence that every arrow has already passed numerical qualification.

## 9. What still has to be tested after installation

Installing the environment is only Gate G00. The following later gates from the Project 0 plan remain necessary:

| Gate | Environment-related question |
|---|---|
| G00 | Do the packages install and report the intended identities? |
| G02 | Can an analytical `PythonForce` be evaluated correctly through native ATM? |
| G03 | Does the actual AToM force-routing path include the ML force exactly once? |
| G04 | Do OpenMM-ML link sites and their real-parent forces behave correctly? |
| G05 | Does native MACE agree with the OpenMM-ML MACE implementation? |
| G06 | Does periodic mechanical embedding preserve the intended interactions? |
| G09 | Can a complete solvated system be prepared, exported, loaded, and evaluated in the worker? |
| G10 | Can the system survive fresh processes, restart, and replica exchange? |
| G11 | Can the first real protein ABFE be run without violating the lower-level gates? |
| G12 | Can the corresponding two-ligand RBFE transformation use the same ML partition? |

The key principle is that **environment installation is a prerequisite, not a qualification result**.

## 10. Why the environment intentionally stays narrow

Project 0 is infrastructure work. Its first task is not to discover the best neural potential, the best GPU configuration, the fastest timestep, or a universal preparation pipeline.

Every extra package can introduce:

- another version compatibility question;
- another model or parameterization choice;
- another source of numerical differences;
- another piece of software that can fail during debugging.

The environment therefore contains the components required to establish the first architecture and its controls, while leaving optional model families, long-range ML, electrostatic embedding, and specialized chemistry for later qualified environments.

## 11. Relevant external documentation

- OpenMM 8.6.1: https://pypi.org/project/OpenMM/8.6.1/
- OpenMM conda packages: https://anaconda.org/channels/conda-forge/packages/openmm/files
- OpenMM-ML repository: https://github.com/openmm/openmm-ml
- OpenMM-ML tag 1.8: https://github.com/openmm/openmm-ml/tree/1.8
- AToM-OpenMM repository: https://github.com/Gallicchio-Lab/AToM-OpenMM
- AToM-OpenMM release information: https://github.com/Gallicchio-Lab/AToM-OpenMM/releases
- AToM-OpenMM PyPI: https://pypi.org/project/atom-openmm/
- MACE / `mace-torch`: https://pypi.org/project/mace-torch/
- e3nn conda-forge: https://anaconda.org/conda-forge/e3nn/files
- AmberTools conda-forge: https://anaconda.org/conda-forge/ambertools
- openmmforcefields 0.16.0: https://anaconda.org/conda-forge/openmmforcefields/manage
- PyMBAR conda-forge: https://anaconda.org/conda-forge/pymbar
- PyTorch installation matrix: https://pytorch.org/get-started/previous-versions/

## 12. Recommended repository layout

Keep the environment files separate from model assets and project code:

```text
Project_0_ATM_MLMM/
  environment/
    Project_0_ATM_MLMM_environment.yml
    Project_0_ATM_MLMM_Environment.md
    conda-explicit.txt                 # generated after qualification
    environment-resolved.yml           # generated after qualification
    pip-freeze.txt                     # generated after qualification
  models/
    mace_off23_small/
      MODEL_MANIFEST.yaml
      MACE-OFF23-small.model
  src/
  tests/
  fixtures/
  docs/
```

Do not put model checkpoint files directly into Git unless the repository's licensing and file-size policy explicitly permit it. A manifest with a checksum and source location is the minimum reproducibility record.

## 13. Final qualification rule

A developer should be able to take this environment specification, create a clean Conda environment, load the exact approved model asset, and reproduce the deterministic G02-G07 tests without changing package versions manually.

Only after that condition is met should we call the environment the **Project 0 qualified environment**.

Until then, call it the **Project 0 candidate environment**.
