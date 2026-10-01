# M02 implementation and audit handoff

Implement M02 on a new branch copied from `m00-audit-m01-development`, then obtain an independent combined audit of G02 and G03 on the completed snapshot. Start with G02; G03 depends on its native ATM oracle. Continue the accepted M01 implementation and scientific contract version 1.

This handoff records the predecessor as of 2026-10-01. [STATUS](../STATUS.md) is the live progress summary. The gate documents remain the authority for requirements and acceptance.

## Create the continuation branch first

Repository: [georgpou/AToM_MLMM](https://github.com/georgpou/AToM_MLMM). Required parent: [m00-audit-m01-development](https://github.com/georgpou/AToM_MLMM/tree/m00-audit-m01-development).

The accepted M01 handoff commit is `5db63872f18f807ab0d7746c0430f175891a378d`. This document is added by a later documentation-only commit on that same branch. Fetch the current parent tip so the new branch includes this handoff as well as the implementation, fixtures and evidence.

Use the existing checkout when suitable. Inspect its status and preserve any existing changes before switching. Use isolation if unrelated changes prevent a clean continuation; do not discard them or silently include them in M02. Choose an unused child branch name; `m02-analytic-atm` is the suggested name. From the repository root, run each command and stop if it fails:

```bash
git status --short --branch
git fetch origin refs/heads/m00-audit-m01-development:refs/remotes/origin/m00-audit-m01-development
git rev-parse origin/m00-audit-m01-development
git switch --no-track -c m02-analytic-atm origin/m00-audit-m01-development
git rev-parse HEAD
git merge-base --is-ancestor 5db63872f18f807ab0d7746c0430f175891a378d HEAD
git diff --exit-code origin/m00-audit-m01-development HEAD --
git status --short --branch
```

The two printed commit IDs must match at creation. The ancestor and diff checks must exit 0. Record that exact starting commit in the worker log. Branch from the fetched development parent; `main` and the original `m01-g00-environment-audit-v1` do not contain this completed successor work. Preserve the lineage through Git history.

If there is no checkout, clone the required parent, enter the clone and perform the child-branch steps above:

```bash
git clone --branch m00-audit-m01-development --single-branch https://github.com/georgpou/AToM_MLMM.git
cd AToM_MLMM
```

Publish only the child branch when handing over completed work:

```bash
git push -u origin m02-analytic-atm
```

Use the actual chosen name if it differs. Keep the parent and main unchanged during M02 work.

## Read before implementation

1. [AGENTS](../../../AGENTS.md), [README](../../../README.md), [DEVELOPMENT](../../DEVELOPMENT.md) and [STATUS](../STATUS.md).
2. [CPU setup guide](../../../environment/cloud-cpu/README.md).
3. [M00 analytic design audit](../../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md), [M01 repair worker](../../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) and [M01 combined v2 audit](../../../Worker_Log/Milestone_01/Gate_01_v2_audit.md). The v2 audit incorporates the unchanged v1 review and closes both findings.
4. [G02](../gates/G02-analytic-force-in-native-atm.md) and [G03, including M02 combined review](../gates/G03-atom-routing-and-integration.md#m02-combined-review).
5. Their linked sections in [S01 scope](../specs/S01-scope-and-invariants.md), [S02 ownership](../specs/S02-architecture-and-dependencies.md), [S03 records/maps/signatures](../specs/S03-data-and-interface-contracts.md), [S04 environment-dependent probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe), [S05 maps/mixing](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy), [S06 checks/tolerances](../specs/S06-validation-and-tolerances.md) and [S07 qualification/evidence](../specs/S07-artifacts-and-qualification.md).

Use the [requirement locator](../REQUIREMENTS.md) and [upstream references](../reference/sources.md) as needed. Apply the recorded M00 decisions and review any additional scientific decision or contract amendment needed for G02/G03 before implementing it. Full M00 physical-reference closure remains open for later chemical comparisons; it does not block the declared analytic CPU work.

## What the predecessor established

| Item | Recorded result |
|---|---|
| M00 | Independently accepted version 1 design for the stated analytic CPU scope; full physical-reference closure remains open. |
| M01 | G00-T1 and G01-T1/T2/T3, with combined acceptance for `core-analytic-cpu`. |
| Independently reviewed M01 snapshot | `04944c67fc04c1667723f5292a07f8401cb94184`. |
| Worker-tested implementation snapshot | `141c7fbcf2c5407e7880512d5481639bdc81bf57`; subsequent M01 handoff changes are reports/evidence only. |
| Full project suite | 47 passed. |
| Analytic selection | 46 passed, 1 model-asset test deselected. |
| Strict setup validation | All 9 checks passed. |

These are inherited results, not fresh results for your machine or future changes. Establish your own baseline after activation and rerun applicable checks after implementation. Test counts will increase as G02/G03 tests are added.

The one deselected test is [test_local_mace_link_calculation](../../../tests/integration/test_mace_link_example.py). It uses the bundled pretrained MACE checkpoint and passed in the full 47-test run. Keep its `model_assets` marker: it is intentionally outside the analytic subset and remains part of the full suite when that asset profile is available. The small example is integration evidence; it does not establish chemical/protein accuracy or full G00-T2 qualification.

M01 review findings **M01-R1** and **M01-R2** are closed. Preserve the explicit rejection of unsupported policy/version/energy/locality fields and the rejection of every blank or whitespace-only fixture/log/reviewer reference. The original `changes_required` audit remains history for its earlier snapshot.

Useful saved evidence:

- [G00 worker](../../../Worker_Log/Milestone_01/Gate_00_v1_worker.md), [environment manifest](../../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) and [repair validation output](../../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz).
- [Original-MM inventory](../../../Worker_Log/Milestone_01/evidence/M01_v2/original-mm-inventory.json) and [M01 acceptance record](../../../Worker_Log/Milestone_01/evidence/M01_v2/acceptance.json).

## Reuse the implemented code

All project source belongs under [src/atm_mlmm](../../../src/atm_mlmm/). Inspect the existing functions and tests before adding records or helpers.

| Existing code | Reuse and preserve |
|---|---|
| [schema.py](../../../src/atm_mlmm/schema.py) | Owned immutable records, common units, schema 1.0 JSON, explicit errors, all-real `EnergyForces`, evidence/acceptance validation. |
| [identity.py](../../../src/atm_mlmm/identity.py), [partition.py](../../../src/atm_mlmm/partition.py) | Stable IDs, current-index resolution, complete ligand groups, fixed neutral components and supported-cut rejection. |
| [protocol descriptions](../../../src/atm_mlmm/protocols/) | ABFE one-group and RBFE two-group presets. `make_protocol` currently describes requests; coordinate-map resolution belongs to G02. |
| [capabilities.py](../../../src/atm_mlmm/capabilities.py) | Admission of reviewed analytic metadata; successful admission explicitly remains `qualified=False`. |
| [ledger.py](../../../src/atm_mlmm/ledger.py) | Read-only original-MM inventory. Preserve the original System and its force/constraint/box/offset provenance. |
| [environment.py](../../../src/atm_mlmm/environment.py), [persistence.py](../../../src/atm_mlmm/persistence.py) | Checked CPU APIs/source identities and finite deterministic atomic JSON persistence. |

M01 fixtures are in [fixtures/contracts](../../../fixtures/contracts/); their guide distinguishes abstract connectivity graphs from chemical references. Existing checks live in [tests/unit](../../../tests/unit/) and [tests/contracts](../../../tests/contracts/), with setup and MACE regressions in the other test folders.

G02/G03 numerical assemblers and evaluators are not yet implemented. Add their needed `PhysicalBundle`, transfer/schedule/restraint/alchemical/raw-energy records using S03 semantics and the existing schema machinery. Planned paths include `atm.py`, `geometry.py`, `endpoints.py`, `derivatives.py`, `routing.py`, `prepare.py`, `adapters/atom.py` and `fixtures/analytic/`. Keep future real-model and cap construction in their owning gates.

## Activate and establish your baseline

For a fresh Linux x86_64 environment, run the maintained installer from the repository root:

```bash
bash environment/cloud-cpu/install.sh
```

Reuse a verified installation where available. The default setup prefix is `/workspace/.onboarding/atom-mlmm`; a custom writable prefix is supported by the CPU guide. Installation needs the documented network destinations, free disk and writable Conda registry. A new machine must install its own environment; the previous agent's runtime directory is not part of the branch.

Activate main in every new shell, then run:

```bash
source /workspace/.onboarding/atom-mlmm/activate.sh
python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"
python -m pytest -q
python -m pytest -m 'not gpu and not model_assets and not slow' -q
```

Substitute your custom prefix when applicable. Main uses Python 3.11.16/NumPy 2.4.6; separate AmberTools uses NumPy 1.26.4. Keep the exact locks, hashes, source archives and scoped checkpoint-loading policy. Inspect pinned upstream APIs/sources under `<setup-prefix>/sources/`; AToM source tag v8.5.0 corresponds to distribution 8.5.0b0. Package versions alone do not qualify the new numerical route.

Current analytic metadata admits mechanical policy version `1`, `protein_c_c`, `nonperiodic`, `declared_relative_energy`, and backend-specific locality: `analytic-local`/`local` or `analytic-environment`/`environment_dependent`. Reference/CPU use double/float64, NVT and the admitted integrators; the initial timestep ceiling is 0.0005 ps (0.5 fs). Follow the validation code and specs for complete applicability.

## Implement M02 in this order

First write a concrete plan against the gate assertions. Establish independent expected results, run focused failing tests, implement the smallest change, and rerun affected checks plus the available CPU suite after meaningful code changes.

| Stage | Required work and evidence |
|---|---|
| G02-T1 | Importable analytic PythonForce callback; independently hand-transformed coordinates/forces; fresh-process serialization; linear ATM at lambda 0, 0.37 and 1; selected order `[2, 0]`; independent units/scatter; nonzero outside harmonic term; exact nonlinear production-expression derivatives. Covers G02-01/02/03/08/09. |
| G02-T2 | One shared physical bundle, assembler and checker for one complete ABFE group and two unequal, noncontiguous RBFE groups. Produce fixed maps for every final particle. Covers G02-04. |
| G02-T3 | Analytic ML/MM environment coupling, nonzero forces on both real sides, MM-only motion, transformed motion, A-B-A history independence, fresh reload, and deliberate faults that the oracle detects. Covers G02-05/06/07. |
| G03-T1 | Explicit recursive force ownership, separate export copy, free reserved group (candidate 1), AToM explicit group selection, originals removed after copying, duplicate/nested/occupied-group rejection. Reproduce insufficient default routing in a regression. Covers G03-01/06. |
| G03-T2 | Group-0 all-active physical preparation copy; separately checked production export; large marker force and actual integrator-mask checks for ABFE, RBFE and preparation. Covers G03-02/03. |
| G03-T3 | Narrow `adapters/atom.py` owns upstream keys/classes/unit conversion and state handover. Both protocol paths match G02 native observables; preserve/check full maps and parameter state after construction, changes and reload. Covers G03-04/05/07. |

The full IDs are `P0-TEST-G02-01` through `P0-TEST-G02-09` and `P0-TEST-G03-01` through `P0-TEST-G03-07`. Their exact assertions and planned pytest nodes are in the gates. Extend architecture checks to new modules as needed.

Preserve these rules throughout:

- Use nm, kJ/mol, kJ/mol/nm, ps and K. Forces are negative gradients on every influencing real coordinate in declared order, including MM environment atoms. Derivative gaps are explicit failures.
- Keep real ML membership fixed, transfer whole ligands, and keep protein/caps at zero explicit transfer shift. Support generic group collections and separate real/final/model maps, consuming any upstream `oldToNew` map explicitly.
- Use the same physical Hamiltonian at both coordinate maps. Recompute geometry-dependent inputs at each mapped state. Physical construction stays independent of ABFE/RBFE selection.
- Name raw `u0`, raw `u1`, expression, outside, softened perturbation and total energy separately. Verify the admitted `getPerturbationEnergy()` tuple as `(u1, u0, energy)` against independent contexts. Include a nonzero outside term exactly once.
- Differentiate the exact admitted nonlinear mixing expression. Linear lambda weights establish only the linear oracle. Do not relax scientific definitions or tolerances to hide a mismatch.
- Keep all intended physical potential forces inside ATM, with explicit outside restraint ownership. Force routing and actual integration masks require separate evidence. Preserve the group-0 preparation copy; check the reserved export group is free; keep PythonForce's true identity.
- Keep OpenMM/model imports out of common records and protocol descriptions. Upstream AToM keys, class selection and conversions belong in its adapter. A narrowly needed upstream fix requires an exact patch/commit and reproducer.

Use [S06's thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds): starting small Reference errors are at most 1e-8 kJ/mol and 1e-7 kJ/mol/nm per force component; starting small double-precision direct/ATM limits are 1e-4 kJ/mol and 5e-3 kJ/mol/nm. Characterize and freeze the admitted precision profile before acceptance. Use the finite-difference step sweep (initially 1e-3, 1e-4, 1e-5 nm); inspect components and recompute derived coordinates after perturbation.

A routing, ownership, direct/ATM or derivative mismatch blocks downstream integration. Keep the smallest failing sample and diagnose it with the analytic fixture.

## Test, record and audit the completed snapshot

After implementing the planned nodes, run the G02 and G03 commands from the repository root:

```bash
python -m pytest tests/integration/test_pythonforce_atm.py tests/contracts/test_transfer_protocols.py tests/contracts/test_physical_evaluator.py tests/contracts/test_fault_injection.py -v
python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v
python -m pytest -m 'not gpu and not model_assets and not slow' -q
python -m pytest -q
python tools/check_docs.py --self-test
git diff --check
```

The first two commands describe future tests, not evidence already collected. Missing modules, empty collection or skipped mandatory checks cannot satisfy a gate. Repeat strict setup validation when environment changes or unresolved setup concerns warrant it. Preserve actual command output, exit codes, environment/input identities, numerical thresholds and failure reproducers in inspectable evidence artifacts.

Use [the worker template](../templates/worker-log.md) and [the independent audit template](../templates/audit-log.md). Put records under `Worker_Log/Milestone_02/`, using unused attempts:

- `Gate_02_vN_worker.md` and matching `Gate_02_vN_audit.md` for G02.
- `Gate_03_vN_worker.md` and matching `Gate_03_vN_audit.md` for G03; its final review can include combined M02 acceptance. Alternatively use a `Milestone_02_vN_worker.md` / `_audit.md` pair for a separately assigned combined review, as G03 permits.

An implementation author can self-check but cannot supply independent approval. Arrange a separate reviewer who did not author the changes. Give that reviewer the exact code commit, worker log, requirements, fixture identities and raw results. Preserve submitted attempts and findings; repairs require failing/passing regressions and independent closure on the repaired snapshot. Distinguish reviewed code from later report-only commits.

The **M02 combined audit must cover G02 and G03 together on one recorded snapshot**, carrying the accepted M01 prerequisite. Require direct/native/AToM agreement for both protocol shapes, outside-term scope/tuple order, complete real derivatives, subset/maps/units, the nonlinear chain rule, fresh reload, environment motion/A-B-A, recursive force ownership, active integration in each stage and deliberate-error detection. Individual task passes alone do not close M02.

Update [STATUS](../STATUS.md) with the actual reviewed profile and links. Finish with the child branch/commit, worker/audit paths, exact test results, open findings and next action. Verify the push and a clean worktree. Advance only after applicable findings are closed and combined acceptance is recorded.

## Scope that remains pending

M02 qualifies an analytic CPU transfer kernel. G00-T2 full model-asset/loader qualification, G00-T3/GPU hardware, chemical/protein reference accuracy, physical cap construction, periodic physics, actual electrostatic embedding and molecular ABFE/RBFE remain with their owning gates. Before G05/G07 physical-reference comparisons, close the open M00 reference-method/input/limit decisions through review before inspecting results.

After accepted M02, hand over [M03 beginning with G04](../gates/G04-link-boundary-and-derivatives.md) and the separately eligible [M04/G08 analysis work](../gates/G08-thermodynamics-and-estimators.md) according to the roadmap and their actual prerequisites. Each continuation branches from the completed M02 successor.
