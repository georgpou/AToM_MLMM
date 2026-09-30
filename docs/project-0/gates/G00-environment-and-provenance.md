# G00: Check the software and record exactly what is installed

**Part of:** [M01](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

Later tests are only reproducible if we know the software, source versions, and model files they used. A successful installation is the starting point, not proof that ML/MM works inside ATM.

## Expected outcome

A CPU environment report with exact versions and check results. Model and GPU reports are separate and appear only when those resources are available.

**Not part of this gate:** Do not require a checkpoint or GPU merely to start the analytic CPU work. Do not call an installed package a validated molecular method.

## Before starting

Required earlier gates: none after the required M00 design review. Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** Reviewed M00 boundaries; the inherited candidate environment; one explicitly approved model asset or a recorded reason it is not yet available.

**Outputs used by later gates:** Environment and source manifests, candidate CPU profile, an approved model manifest, and a reproducible import/API-check report. GPU qualification remains a separate profile.

**Planned source/test paths:** `environment/cpu.in`, `environment/gpu.in`, `schema.py`, `persistence.py`, `tests/unit/test_environment.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G00-T1` | Characterize the clean CPU environment | `P0-TEST-G00-01`, `P0-TEST-G00-02` |
| `G00-T2` | Approve and characterize the model asset | `P0-TEST-G00-03`, `P0-TEST-G00-04` |
| `G00-T3` | Create the optional hardware profile only when available | `P0-TEST-G00-05` |

### G00-T1: characterize the clean CPU environment

**Read:** [Environment: installation](../../../ATM_MLMM_Environment.md#install-and-record-the-result); [S07: Capability-specific applicability](../specs/S07-artifacts-and-qualification.md#capability-specific-applicability).

Start from the candidate recipe in [the environment note](../../../ATM_MLMM_Environment.md), not a guessed latest combination. Create a separate CPU environment. Write and run the API/version checks; failures must identify an unavailable API or inconsistent version rather than silently disabling that check. Resolve dependencies, run `python -m pip check` and `python -m openmm.testInstallation`, and save their full outputs.

Pin the resolved Python patch version, transitive dependency builds, source commits, and downloaded artifact hashes after a successful solve. AToM's source tag and package metadata can disagree; record both. Do not force an older OpenMM installation below the reviewed OpenMM-ML floor to reproduce a historical tutorial. Do not install the old standalone ATM plugin for the native-ATM route.

### G00-T2: approve and characterize the model asset

**Read:** [Environment: assets and loading](../../../ATM_MLMM_Environment.md#model-assets-and-loading); [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested).

Select the one candidate local checkpoint for the first fixtures, document allowed use, and freeze a local digest. The package license and checkpoint license are different obligations. Asset presence, model identity, architecture/element/domain metadata, and numerical qualification are separate states.

Test actual loading with the proposed PyTorch version before building a mixed System. The inherited audit identified default `weights_only` compatibility as a specific risk. A required adapter patch must be narrowly scoped to an approved trusted artifact, recorded as a source change, and retested; no global monkey-patch of `torch.load` is acceptable.

### G00-T3: create the optional hardware profile only when available

**Read:** [Environment: GPU qualification](../../../ATM_MLMM_Environment.md#gpu-qualification); [S07: Loading, restart, and workers](../specs/S07-artifacts-and-qualification.md#loading-restart-and-workers).

Use a separate GPU environment and record OpenMM and PyTorch runtime builds, driver, GPU architecture, precision and visible-device settings. Import success alone does not demonstrate nested-force correctness or device placement. Schedule those checks in their owning gates. Do not replace packages repeatedly in the CPU environment and call its final state a lock.

The deliverable is an installation/provenance report. Terms such as compatible, stable, qualified, or production-ready are reserved for subsequent evidence.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G00-01 | `tests/unit/test_environment.py::test_required_apis_and_versions` | Confirm native ATMForce, PythonForce selected-particle support, mixed-system info API, serialization APIs, and reported versions; missing requirements fail clearly. | P0-REQ-014 |
| P0-TEST-G00-02 | `tests/unit/test_environment.py::test_environment_manifest_complete` | Record package builds, full source commits, platform, Python patch version and dependency result; tag and reported package version remain separate. | P0-REQ-014 |
| P0-TEST-G00-03 | `tests/unit/test_environment.py::test_model_asset_hash_and_policy` | A wrong digest or absent authorization record is rejected before deserialization; an approved local asset is identifiable without network. | P0-REQ-014, P0-REQ-029 |
| P0-TEST-G00-04 | `tests/integration/test_checkpoint_loading.py::test_trusted_checkpoint_loads_in_fresh_process` | Exercise the actual PyTorch/checkpoint loading policy in a fresh process; never globally weaken loading policy to admit arbitrary files. | P0-REQ-014 |
| P0-TEST-G00-05 | `tests/unit/test_environment.py::test_unavailable_platform_is_unqualified` | Absent CUDA records not_run/unsupported profile, never a successful GPU qualification. | P0-REQ-032 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/unit/test_environment.py tests/integration/test_checkpoint_loading.py -v
```

**Stop and diagnose:** An unresolved dependency, license, source identity, or checkpoint loader prevents the relevant profile from advancing. Structural documentation work can continue, but a missing model cannot be treated as passed model qualification.

## Keep future changes possible

The common schema stays importable without loading a model or initializing a GPU. Backend dependencies remain at their adapters, so adding another backend does not change protocol imports.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_01/`\
**Worker:** `Gate_00_vN_worker.md`; **audit:** `Gate_00_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).
