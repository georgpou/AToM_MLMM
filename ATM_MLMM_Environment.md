# Project 0 Conda environment

**Specification:** [ATM_MLMM_environment.yml](ATM_MLMM_environment.yml). **Candidate target:** Linux x86_64, Python 3.11. **Status:** qualification candidates, not a solved platform lock. The 30 September 2026 scientific amendment preserves the package versions and corrects the PyTorch source/build choice. The conda-forge listing was checked, but this revision did not solve or install the complete environment. [G00](docs/project-0/gates/G00-environment-and-provenance.md) still owns that evidence.

This environment supports the intended OpenMM physical builder, OpenMM-ML mechanical embedding and links, one local MACE model, native ATM, the AToM workflow and independent PyMBAR analysis. Installation alone does not establish that these components work together. [S01](docs/project-0/specs/S01-scope-and-invariants.md) defines the admitted initial science.

## Packages and purpose

The YAML is the executable package specification. These explanations are not a second version lock.

| Packages | Purpose and inherited candidate choice |
|---|---|
| Python 3.11; pip; git; setuptools; wheel | Interpreter, tagged-source installation and packaging. Freeze the resolved patch/build versions. |
| OpenMM 8.6.1 | Molecular engine and native ATMForce/PythonForce. The inherited source audit identified this floor for OpenMM-ML 1.8; confirm the actual API/build during G00. |
| OpenMM-ML tag 1.8 | Mixed-system construction, mechanical embedding, caps and mapping. Record the resolved commit, not only the tag. |
| AToM-OpenMM tag v8.5.0 | Production workflow and bundled Python UWHAM. Record source commit separately from package-reported version; qualify its composition with the newer OpenMM baseline. |
| PyTorch 2.8.0, conda-forge CPU variant | MACE tensor backend. The YAML now constrains the build with `pytorch=2.8.0=cpu*`. Record the resolved build and verify the installed backend; GPU use needs a separate profile. |
| mace-torch 0.3.16; e3nn 0.4.4 | Initial local-model implementation and its inherited equivariant-library compatibility point. Test the approved asset and adapter, not just imports. |
| AmberTools 26.0; openmmforcefields 0.16.0 | Biomolecular preparation. Keep these out of the basic records/analytic tests' import path. Explicitly select and record force fields and charges. |
| configobj 5.0.9; setproctitle | Workflow configuration and process labeling, respectively. |
| NumPy; SciPy | Arrays and independent numerical checks, including analytic-example quadrature. |
| PyYAML; packaging; psutil | Structured settings, version handling and process/resource information. |
| PyMBAR 4.0.3; MDTraj | Independent free-energy analysis and trajectory utilities. |
| pytest; pytest-cov | Tests and coverage; neither substitutes for an independent expected result. |

Use one approved local MACE-OFF23-small checkpoint initially. Other model stacks, real electrostatic embedding, reactive chemistry and GPU acceleration need their own admitted profiles. Do not install the historical standalone ATM plugin when using native `openmm.ATMForce`, or add R merely because older UWHAM workflows used it.

The YAML includes preparation tools for later fixtures. Core analytic CPU work does not require licensed neural weights or a parameterization pipeline. Reuse small deterministic fixtures first. The inherited ff14SB/TIP3P with GAFF2 option is a continuity proposal, not a new mandatory optimization; archive the actual parameter files and charge vectors. Chemical repair belongs in documented preparation, not hidden in the hybrid builder.

## Why the PyTorch channel changed

Official PyTorch Conda publication stopped starting with version 2.6. The upstream announcement directs Conda users to conda-forge as one alternative. Its package listing includes Linux x86_64/Python 3.11 CPU builds of 2.8.0. Therefore the candidate YAML uses conda-forge, excludes default channels with `nodefaults`, and constrains the PyTorch build to `cpu*`. It no longer implies that the discontinued official channel supplies this version. See [U40 and U41](docs/project-0/reference/sources.md#scientific-amendment-source-checks).

A published package is not proof that this complete environment solves or that MACE, OpenMM-ML and AToM work together. G00 must preserve the actual solver result and check that pip has not replaced the intended Torch distribution during installation.

## Install and record the result

Run from the repository root in a clean environment:

```bash
conda env create -f ATM_MLMM_environment.yml
conda activate atm-mlmm-p0
python -m pip check
python -m openmm.testInstallation
```

If solving fails, save the error. Do not silently change versions or bypass required dependencies and then call the original specification qualified. The conda-forge channel and CPU build choice require actual G00 evidence. Do not repair a solve by silently reintroducing the discontinued PyTorch channel or an unrecorded wheel.

Inspect installed identities:

```bash
python - <<'PYCODE'
import sys
from importlib import metadata
print('Python:', sys.version)
for name in ('openmm', 'torch', 'e3nn', 'mace-torch', 'openmmml',
             'atom-openmm', 'pymbar', 'openmmforcefields'):
    try:
        dist = metadata.distribution(name)
        print(name, dist.version)
        origin = dist.read_text('direct_url.json')
        if origin:
            print(origin)
    except metadata.PackageNotFoundError:
        print(name, 'NOT INSTALLED AS A DISTRIBUTION')

import torch
print('Torch CUDA runtime:', torch.version.cuda)
print('Torch HIP runtime:', getattr(torch.version, 'hip', None))
assert torch.version.cuda is None, 'Expected the candidate CPU Torch build'
assert getattr(torch.version, 'hip', None) is None, 'Expected no HIP runtime'
print('Explicit test tensor device:', torch.ones(1, device='cpu').device)
PYCODE
```

Preserve output and resolved builds in the actual G00 evidence folder:

```bash
conda list --json > conda-packages.json
conda list --explicit > conda-explicit.txt
conda env export > environment-resolved.yml
python -m pip freeze > pip-freeze.txt
```

These are generated qualification artifacts, not existing files or replacements for `ATM_MLMM_environment.yml`. Capture source commits from the installed VCS metadata or admitted checkout and hash approved assets. A query of the current remote tag alone does not identify what was installed. Replace tag-only identities with exact commits or archived source artifacts in a qualified lock.

For an intentional unqualified-environment update, the correct filename is:

```bash
conda env update -f ATM_MLMM_environment.yml --prune
```

Do not update an already qualified environment in place. Rebuild separately and re-run affected checks. Read [S07](docs/project-0/specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested) for the exact evidence/profile definition.

## Model assets and loading

Installing MACE does not identify or install the exact approved checkpoint. Store the trusted asset separately and record its source, revision, SHA-256, license, elements, formal charge/spin domain, locality/cutoff, tensor precision, device and energy-output convention. Do not commit restricted weights. A model-weight license is separate from its package-code license.

The inherited audit identified a `torch.load`/`weights_only` compatibility risk for complete Python-model checkpoints. G00/G05 must test the approved file in a fresh process, including offline execution without the original cache. Record relevant loader settings. Any required loader patch must be narrow, reviewed and hashed, not a global unsafe-loading override. Successful loading is not force or thermodynamic qualification.

The proposed output is `energy`, used consistently in the native reference and adapter. The MACE label `interaction_energy` is not a ligand-protein pair decomposition. Verify energy/length/force conversion, dtype and generic-versus-named-model `mlLongRange` handling in the actual adapter. Extract the cutoff from the approved model rather than silently modifying it.

## GPU qualification

Create a separate environment/profile for the target hardware; do not repeatedly swap CPU and GPU packages in a qualified environment. Record the driver, GPU architecture, PyTorch runtime and OpenMM plugin/build together. Naming CUDA in both packages does not establish compatibility. Do not install an arbitrary toolkit as a guessed repair.

The earlier pip-based alternative and its CUDA candidates remain in the historical snapshot, not a second active setup recipe. Use the actual target's supported builds only after G00 checks availability and compatibility. CPU success cannot qualify GPU results, and single-GPU success cannot qualify multiple GPUs.

Run the admitted deterministic checks, then native-MACE versus OpenMM-ML comparisons before worker execution. Preserve the admitted subprocess-start method. Verify the tensors' actual device separately from OpenMM `DeviceIndex`, including local device zero under a restricted visible-device list. See [G10](docs/project-0/gates/G10-restart-and-replica-exchange.md).

## What installation does not prove

G00 establishes a named environment/asset profile. G02-G03 qualify force composition, the actual fixed maps and routing; G04-G07 add caps, real models, periodicity and small-system chemical references; G08 checks thermodynamic meaning; G09-G10 check preparation/reload/exchange; G11-G12 demonstrate molecular ABFE/RBFE; G13 admits only supported release claims. These remain planned tests, not results of this amendment. Quantum-reference data for G05/G07 may be generated in a separately approved environment and archived with its calculation settings; no quantum-chemistry package is silently added to this runtime recipe.

Upstream references and the specifically rechecked pages are distinguished in [the source register](docs/project-0/reference/sources.md), especially U04, U12-U13, U19, U21-U27 and U39-U41. The preserved [pre-cleanup snapshot](Worker_Log/Milestone_00/evidence/Documentation_v2/snapshot_before_cleanup.zip) contains both previous environment guides. Unfetched exact-tag files remain G00 source-inspection work; moving online documentation is not proof of the installed API.
