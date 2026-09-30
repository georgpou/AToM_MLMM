# G09: Add solvent and hand the prepared system to a worker

**Part of:** [M05](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

Water, periodic electrostatics, and saved input files introduce new ways to change a validated system unintentionally. The actual worker must load the same physical and thermodynamic definitions.

## Expected outcome

A self-contained solvated example whose preparation, exported files, worker state, energies, and forces agree.

**Not part of this gate:** A short pilot checks workflow behavior; it is not automatically a converged binding calculation.

## Before starting

Required earlier gates: [G07](../gates/G07-joint-cavity-ligand-atm.md), [G08](../gates/G08-thermodynamics-and-estimators.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G07 joint physical model; G08 thermodynamic/analysis definitions and known-answer checks.

**Outputs used by later gates:** Solvated capped-fragment bundle, project-owned preparation, pinned AToM export, and short multiwindow preflight evidence.

**Planned source/test paths:** `fixtures/solvated_fragment/`, `prepare.py`, `persistence.py`, `adapters/atom.py`, `tests/workflow/test_solvated_handover.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G09-T1` | Add solvent without changing the embedded model | `P0-TEST-G09-01` |
| `G09-T2` | Own the preparation sequence and export | `P0-TEST-G09-02`, `P0-TEST-G09-03` |
| `G09-T3` | Run a pilot without relabeling it convergence | `P0-TEST-G09-04`, `P0-TEST-G09-05` |

### G09-T1: add solvent without changing the embedded model

**Read:** [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting); [S04: The physical contract is broader than the first embedding](../specs/S04-embedding-and-model-contracts.md#the-physical-contract-is-broader-than-the-first-embedding).

Use the same neutral capped-fragment/ligand fixture and a declared classical solvent convention. Choose a box with two admitted physical ligand placements. Check the entire protein/fragment and periodic images, not only local model edges. Retain and test classical ligand-water/ion coupling in the separated state.

Declare NVT temperature, conservative timestep, constraints, PME and dispersion settings. Density equilibration, if used, is a separately checked preparation operation; fixed-volume production does not imply that untested pressure/virial behavior is supported.

### G09-T2: own the preparation sequence and export

**Read:** [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution); [S07: Planned artifact bundle](../specs/S07-artifacts-and-qualification.md#planned-artifact-bundle).

Use the all-active physical preparation copy for minimization and gradual thermalization. Then create the validated alchemical states from G08's exact expressions. Do not inherit hidden stock timesteps or intermediate-parameter assignments. Check that the initial topology/PDB coordinates are safe for any preliminary evaluation, even when the higher-precision State replaces them afterward.

The inherited pinned handover uses `<basename>.pdb`, `<basename>_sys.xml`, and `<basename>_0.xml`; verify the complete actual contract in the admitted AToM source. Include model and environment manifests, atom maps, ledger, schedules and restraint obligations. Load through the real worker construction path and compare observables before a single step.

### G09-T3: run a pilot without relabeling it convergence

**Read:** [S07: Required observable names](../specs/S07-artifacts-and-qualification.md#required-observable-names); [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility).

Run a small multiwindow schedule only after direct/worker parity. Save both raw endpoint energies and representative coordinates. Independently reevaluate states, check the directional connection, monitor counterfactual model domain and periodic separation, and record state labels.

This gate demonstrates complete solvated plumbing. Its duration is chosen for these checks, not by copying a publication's production length. A successful short pilot is not a converged affinity or an experimental-accuracy assessment.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G09-01 | `tests/workflow/test_solvated_handover.py::test_bulk_site_and_real_cross_forces` | Bulk placement clears the full solute and relevant images; ligand retains classical solvent interactions. | P0-REQ-003, P0-REQ-005 |
| P0-TEST-G09-02 | `tests/workflow/test_solvated_handover.py::test_same_hamiltonian_in_preparation` | Minimization/thermalization and production export share physical identity, constraints and all-active force semantics. | P0-REQ-012, P0-REQ-021 |
| P0-TEST-G09-03 | `tests/workflow/test_solvated_handover.py::test_worker_load_matches_direct_state` | Reload expected PDB/System/State handover, then compare coordinates, box, parameters, constraints, energies and real forces before stepping. | P0-REQ-015, P0-REQ-021 |
| P0-TEST-G09-04 | `tests/workflow/test_solvated_handover.py::test_saved_raw_records_reconstruct_states` | Every saved pilot record preserves unambiguous raw energies, direction and state ID and permits independent reevaluation. | P0-REQ-018 |
| P0-TEST-G09-05 | `tests/workflow/test_solvated_handover.py::test_both_mapped_geometries_remain_admitted` | Pilot frames check caps, periodic separation, graph edges and nonfinite alternate-state behavior; failures archive both geometries. | P0-REQ-020, P0-REQ-005 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_solvated_handover.py -v
```

**Stop and diagnose:** If preparation changes the physical identity or export/reload changes observables, reduce to the small fixture. Do not treat solvated noise as an explanation for a deterministic mismatch.

## Keep future changes possible

The preparation function consumes admitted bundles and shared phase settings. It must not become a separate pipeline per embedding or per ligand count.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_05/`\
**Worker:** `Gate_09_vN_worker.md`; **audit:** `Gate_09_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).
