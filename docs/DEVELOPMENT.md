# Development guide

Start with the assigned gate's assertions and the current [status](project-0/STATUS.md). The first implementation scope is M00's relevant design decisions followed by M01's analytic CPU G00/G01 work. Scientific modules are planned under `src/atm_mlmm/`; implement them as their gates need them. Current tests cover CPU loading policy and Cloud setup fallback under `tests/environment/`, plus the local-weight [MACE link example](../examples/README.md) under `tests/integration/`.

## Environment and imports

Install and activate using the [CPU guide](../environment/cloud-cpu/README.md). Main Python has NumPy 2, OpenMM, PyTorch CPU, MACE, TorchANI, ASE, OpenMM-ML, OpenFF, openmmforcefields, AToM and PyMBAR. AmberTools has its own Python/NumPy 1.26 prefix; main activation exposes its preparation executables without switching main Python.

| Work | Installed imports/tools | Boundary |
|---|---|---|
| G00 APIs; G01 records and identity | Python standard library, `numpy`, `importlib.metadata`; `openmm` for API checks | Schema/identity/protocol records import without OpenMM or ML libraries. |
| G02 native ATM and G03 routing | `import openmm as mm`; `from openmm import app, unit`; `mm.ATMForce`, `mm.PythonForce`; pinned `atom_openmm` source | Keep AToM-specific classes, keys and conversions in `adapters/atom.py`. |
| G04 caps and G06 MM ledger/PBC | OpenMM `System`, virtual sites, `XmlSerializer`, NumPy | Validate energy derivatives on real coordinates and enumerate retained/removed terms. |
| G05 model adapter | `from openmmml import MLPotential`; ASE `Atoms`; PyTorch autograd; pinned MACE calculator or TorchANI | Import inside model adapters. The approved academic MACE-OFF23-small checkpoint is bundled for the link example; full real-model qualification still belongs to the gates. |
| G07 composed physical/ATM evaluation | Earlier physical builder, protocol and ATM modules | Reuse their records and checker for one/two groups; add no separate engine. |
| G08 thermodynamics and estimators | NumPy/SciPy; `from pymbar import MBAR`; pinned AToM UWHAM | Compare to quadrature and independent samples; keep signs and corrections explicit. |
| G09 preparation | `from openff.toolkit import Molecule`; `from openmmforcefields.generators import GAFFTemplateGenerator`; OpenMM `app`; Amber `antechamber`, `parmchk2`, `tleap`, `sqm` | Use main OpenFF with separate Amber executables; call Amber Python tools through its interpreter. |
| G10-G12 workflows | Pinned AToM sources, OpenMM State/checkpoint APIs, MDTraj, the common physical/protocol/analysis modules | Preserve physical identity, active forces, raw records and correction obligations. |
| G13 release | `pytest`, timing/profiling tools, saved manifests and fixtures | Benchmark the admitted profile; qualify any optimization against the same Hamiltonian. |

Inspect installed APIs and the full pinned sources under `<setup-prefix>/sources/` when integrating upstream code. [S02](project-0/specs/S02-architecture-and-dependencies.md) defines module ownership; [S03](project-0/specs/S03-data-and-interface-contracts.md) defines records and units. Package versions alone do not establish numerical behavior.

## Source and test layout

Create implementation modules under `src/atm_mlmm/` according to S02 and the gate's paths. `pytest.ini` adds `src` to Python's test import path, so testing source code does not require changing the locked package inventory. For direct development commands use:

```bash
PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}" python your_script.py
```

When packaging the implemented project later, add its package metadata in the release scope. An editable project install adds a distribution beyond the baseline inventory; account for that explicitly rather than weakening the dependency locks.

Use `tests/unit/` for small pure checks, `tests/contracts/` for shared invariants, `tests/integration/` for backends, `tests/workflow/` for preparation/routing/restart and `tests/sampling/` for estimators/sampling. Put hand-inspected small inputs and frozen reference data under `fixtures/`. Keep fixture identities, chemical states and reference provenance with the data. Compare calculations to independent expectations rather than copying the function under test into the expected value.

## Commands

Run from the repository root after main activation:

```bash
# All available project tests, including the bundled academic MACE example.
python -m pytest -q

# CPU work without deferred weights, GPUs or long sampling.
python -m pytest -m "not gpu and not model_assets and not slow" -q

# After implementation, use the precise node listed in your assigned gate.
# Example: python -m pytest tests/unit/test_identity.py::test_chain_insertion_and_permutation_identity -v

# Complete environment, preparation, upstream regression and documentation checks.
python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"

# Local links/headings; useful after documentation changes.
python tools/check_docs.py --self-test
```

Substitute a custom setup prefix in validation commands. Register model/GPU/extended-sampling tests with `model_assets`, `gpu` or `slow`. A deselected or skipped test leaves its profile unqualified. Verify actual collection and test counts; planned gate nodes become executable only when implemented. The full CPU suite includes new unit/contract/integration tests as you add them.

The installed upstream AToM regression can be run separately:

```bash
cd /workspace/.onboarding/atom-mlmm/sources/AToM-OpenMM
python -m pytest -q tests/test_uwham.py
```

It is one test covering three reference datasets; preserve upstream collection configuration. Passing it does not qualify the new ML/MM code.

## Scientific work and records

Freeze the relevant M00 decisions before implementation: Hamiltonian, cap rule, units, force ownership, maps, supported chemistry, ensemble, corrections and numerical/reference limits. Keep the existing cap Jacobian, midpoint bridge and restraint-volume definitions. Run structural and analytic tests before a real-model or protein calculation. [S06](project-0/specs/S06-validation-and-tolerances.md) supplies numerical and chemical-reference checks; each gate owns its planned assertions.

Keep one short [worker log](project-0/templates/worker-log.md) per task with exact commands/statuses and the tested profile/snapshot. Update STATUS, then continue from the completed predecessor. Review the implemented gate/milestone on its combined snapshot; do not create another documentation-audit cycle. Earlier documentation and environment-audit artifacts remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368` if a specific historical investigation needs them.
