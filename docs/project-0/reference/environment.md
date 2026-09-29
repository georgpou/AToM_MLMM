# Candidate environment and installation gate

**Provenance:** inherited from revised-plan Section 5. This restructuring task did not reverify upstream releases or run installation. These are deliberately selected qualification candidates, not claims about the newest available version or a solved interoperable lock.

| Component | Candidate | Action in G00 |
|---|---|---|
| OS | Linux x86-64 for initial GPU profile | Record distribution/kernel; do not imply macOS GPU parity |
| Python | 3.11, resolved patch version | Freeze exact interpreter and dependency builds |
| OpenMM | 8.6.1 | Confirm the API/version floor inherited from the OpenMM-ML 1.8 audit |
| OpenMM-ML | tag 1.8 | Freeze resolved full source commit and package build |
| AToM-OpenMM | tag v8.5.0 | Record source commit separately from package-reported version; qualify its composition with OpenMM 8.6.1 |
| MACE | mace-torch 0.3.16 | Confirm dependencies, including the recorded e3nn 0.4.4 constraint |
| First model | MACE-OFF23-small, local approved checkpoint | Check allowed use, exact digest, elements, locality, dtype and loader |
| PyTorch | 2.8.0 | Separate CPU and CUDA runtime profiles; test actual checkpoint deserialization |
| Independent analysis | PyMBAR 4.0.3 | Qualify reduced-potential, overlap and timeseries use |
| Comparison analysis | Python UWHAM bundled in the pinned AToM source | Do not add R solely for historical workflow compatibility |
| Optional template preparation | openmmforcefields 0.16.0 | Separate preparation qualification; explicitly choose force field |
| Test/data utilities | pytest, NumPy, SciPy, PyYAML | Solve and freeze exact versions; no invented tested lock |

The first analytic tests need no ligand parameterization pipeline. Reuse deterministic checked-in fixtures and an independently prepared MM input. ff14SB/TIP3P with GAFF2 was a proposed continuity choice, not a mandatory new scientific optimization; archive actual parameter files and charge vectors. Record any AmberTools or OpenFF build actually used. Chemical structure repair is preparation work, not a hidden action of the hybrid builder.

## Candidate CPU recipe to test during G00

This recipe is inherited design material and is not executed or validated by this documentation package. Use a clean environment and preserve the actual error if resolution fails.

```bash
python3.11 -m venv .venv-p0-cpu
. .venv-p0-cpu/bin/activate
python -m pip install --upgrade pip
python -m pip install "openmm==8.6.1"
python -m pip install "torch==2.8.0" --index-url https://download.pytorch.org/whl/cpu
python -m pip install "mace-torch==0.3.16" "pymbar==4.0.3" pytest pyyaml
python -m pip install "openmmml @ git+https://github.com/openmm/openmm-ml.git@1.8"
python -m pip install "atom-openmm @ git+https://github.com/Gallicchio-Lab/AToM-OpenMM.git@v8.5.0"
python -m pip check
python -m openmm.testInstallation
python -m pip freeze --all > environment-cpu.resolved.txt
```

For a separately created GPU environment, the inherited candidate substitutions are `openmm[cuda12]==8.6.1` and the PyTorch 2.8.0 `cu126` index. Confirm actual driver/runtime/GPU compatibility and plugin availability. Do not install an arbitrary CUDA toolkit as a guessed fix. A CPU package solve does not qualify this GPU combination.

After successful qualification, replace mutable tag-only identity with full commits or archived source wheels, complete transitive builds and hashes. Keep model assets local/offline with exact digests. Do not install the historical standalone ATM plugin when using native `openmm.ATMForce`.

## Specific inherited source risks to test

The earlier audit corrected the OpenMM floor to 8.6.1 for OpenMM-ML 1.8 and distinguished PythonForce introduction from later selected-particle support. It also noted AToM source-tag/package-metadata differences. G00 confirms these against the actual checkout instead of assuming memory is a lock.

The MACE checkpoint loaders inspected in the revised plan called `torch.load` without an explicit `weights_only` policy. PyTorch's changed default can affect complete Python-model checkpoints. Test the trusted approved file in a fresh process and record loader/environment behavior. Any necessary patch must be narrow, reviewed and hashed, not a global unsafe-loading override.

The model's `interaction_energy` label must not be interpreted as a ligand-protein pair decomposition. The proposed baseline explicitly uses `energy` and the same convention in the native reference. Verify the unit factors, dtype and generic-versus-named-model `mlLongRange` option behavior in the admitted adapter.

MACE-OFF model weights have their own usage license. Do not redistribute weights or assume a permissive package license covers them. A supported model identifier, successful load and licensed use are distinct prerequisites from force/thermodynamic qualification.

## Completion evidence

G00 saves installation output, dependency checks, exact source/build/model identities, actual platform test results and unresolved profiles. Later gates add compatibility and numerical evidence. The authoritative inherited upstream locations are collected in [sources.md](sources.md).
