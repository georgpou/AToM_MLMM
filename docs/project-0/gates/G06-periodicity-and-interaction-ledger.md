# G06: Check periodic images and which classical interactions remain

**Part of:** [M03](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

An apparently distant ligand can contact a periodic image. Also, replacing some classical terms with ML can remove or duplicate interactions. Both errors may produce a trajectory without an obvious crash.

## Expected outcome

A term-by-term periodic interaction report and geometry checks that detect unintended image contacts and boundary problems.

**Not part of this gate:** An energy diagnostic is not automatically a free-energy correction. Do not add an unreviewed long-range repair.

## Before starting

Required earlier gates: [G04](../gates/G04-link-boundary-and-derivatives.md), [G05](../gates/G05-local-model-adapter.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G04 cap/boundary oracle; G05 real model graph and adapter; fixed candidate periodic force settings.

**Outputs used by later gates:** Periodic interaction ledger, independent mask diagnostics, model-graph/distance checks and safe-domain rejection reports.

**Planned source/test paths:** `ledger.py`, `geometry.py`, `tests/integration/test_mechanical_pme.py`, `tests/integration/test_periodic_geometry.py`, `tests/integration/test_masked_interactions.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G06-T1` | Audit the exact builder result on a tiny periodic fixture | `P0-TEST-G06-01`, `P0-TEST-G06-06` |
| `G06-T2` | Build independently checked interaction diagnostics | `P0-TEST-G06-02` |
| `G06-T3` | Validate coordinates and graphs under periodicity | `P0-TEST-G06-03`, `P0-TEST-G06-04`, `P0-TEST-G06-05`, `P0-TEST-G06-06` |

### G06-T1: audit the exact builder result on a tiny periodic fixture

**Read:** [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting); [S04: The physical contract is broader than the first embedding](../specs/S04-embedding-and-model-contracts.md#the-physical-contract-is-broader-than-the-first-embedding).

Start with an analytic model substitute and a small charged system, not a protein. Save the original-MM and retained-MM energies on identical coordinates and box. Inspect changed exceptions and every boundary term. Verify ordinary ML-MM interactions survive while artificial cap classical interactions do not appear.

The candidate short-range path retains a periodic electrostatic contribution according to the inherited audit. Measure it under the admitted version rather than calling the entire original cavity-ligand MM interaction 'missing'. Keep cutoff, switching, PME tolerance/realized parameters and dispersion correction explicit. Start the transparent ledger fixture without analytical dispersion correction; any later enabling is a reviewed change.

### G06-T2: build independently checked interaction diagnostics

**Read:** [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting); [S04: A diagnostic energy is not a free-energy correction](../specs/S04-embedding-and-model-contracts.md#a-diagnostic-energy-is-not-a-free-energy-correction).

Implement the charge-mask identity from S04. Disable LJ for the electrostatic diagnostic, update exception charge products, and fix realized PME settings consistently. Include nonneutral subsets to expose a background-convention mistake. Test quadratic charge scaling as an independent relation. Implement a separate LJ mask only for supported mixing/switching rules.

These measurements establish what was removed, not an automatic free-energy correction. The optional physical approximation assessment must define the alternative Hamiltonian first. An average energy difference alone is not that correction.

### G06-T3: validate coordinates and graphs under periodicity

**Read:** [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting); [S06: Independent oracles and fault injection](../specs/S06-validation-and-tolerances.md#independent-oracles-and-fault-injection).

Use orthorhombic image enumeration to check the admitted minimum-image helper. Test a cap boundary near a box face, whole-molecule wrapping, box changes, a bulk ligand near a periodic cavity copy, and two ligand components where relevant. Compare the independent geometry with actual model neighbor edges, including caps and periodic shifts.

Scan across image-choice seams and model cutoffs. Define any restricted admissible domain explicitly; adding a restraint to keep it safe creates a thermodynamic obligation. A 0.2 nm beyond-cutoff margin is a starting setup guard, not a proof covering all trajectory excursions. Record checks on representative pilot frames once available.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G06-01 | `tests/integration/test_mechanical_pme.py::test_ml_mm_cross_interactions_retained` | Moving an MM probe changes expected real ML-MM Coulomb/LJ interactions; the cap creates no new classical interaction center. | P0-REQ-003, P0-REQ-006 |
| P0-TEST-G06-02 | `tests/integration/test_masked_interactions.py::test_pme_charge_mask_cross_identity` | Four charge-mask evaluations reproduce the cross contribution with consistent mesh, exceptions and nonneutral-background convention. | P0-REQ-003 |
| P0-TEST-G06-03 | `tests/integration/test_periodic_geometry.py::test_images_caps_and_bulk_separation` | Catch a periodic cavity/cap/ligand reconnection missed by primary-box distances, including full-protein clearance. | P0-REQ-005 |
| P0-TEST-G06-04 | `tests/integration/test_periodic_geometry.py::test_cap_wrapping_and_image_seam_continuity` | Whole-molecule wrapping and admitted image-choice seams preserve the specified energy/force behavior or are explicitly excluded from the admitted domain. | P0-REQ-005 |
| P0-TEST-G06-05 | `tests/integration/test_periodic_geometry.py::test_backend_graph_matches_independent_geometry` | Actual model edges, including periodic shifts, agree with the admitted independent distance/image search. | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G06-06 | `tests/integration/test_mechanical_pme.py::test_nonstandard_forces_and_box_rejected` | Charge offsets, LJPME, unqualified custom mixing or triclinic cells are rejected rather than approximated silently. | P0-REQ-023 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_mechanical_pme.py tests/integration/test_masked_interactions.py tests/integration/test_periodic_geometry.py -v
```

**Stop and diagnose:** Unexplained periodic discontinuity, cross-force loss, or image reconnection blocks periodic production. Fix the exact convention or narrow its allowed range of configurations; do not invent a generic PME correction first.

## Keep future changes possible

The complete physical bundle owns periodic behavior. The transfer assembler never implements a mechanical-only tail removal or assumes a long-range model factorizes.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Worker:** `Gate_06_vN_worker.md`; **audit:** `Gate_06_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).
