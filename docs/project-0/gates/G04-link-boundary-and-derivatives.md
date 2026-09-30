# G04: Check one link atom and the forces on its real parents

**Part of:** [M03](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A link hydrogen has no independent motion. Its position depends on real atoms, so its force must reach those parents exactly once. A small test makes missing or double force transfer visible.

## Expected outcome

One capped test system with correct cap position, real-parent forces, atom maps, and decisions for every boundary MM term.

**Not part of this gate:** Use one simple boundary and an analytic model substitute first. Do not add a protein or a new boundary chemistry to hide a failure.

## Before starting

Required earlier gates: [G01](../gates/G01-identity-partition-and-contracts.md), [G02](../gates/G02-analytic-force-in-native-atm.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G01 boundary/identity records; G02 analytic ATM oracle and full-force contract.

**Outputs used by later gates:** Analytic `build_physical` path, LinkRecord construction, real/final/model maps, cap-Jacobian independent expected answer and exact boundary ledger.

**Planned source/test paths:** `hybrid.py`, `embeddings/mechanical.py`, `ledger.py`, `derivatives.py`, `fixtures/one_cut_alkane/`, `tests/integration/test_link_geometry.py`, `tests/integration/test_boundary_ledger.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G04-T1` | Exercise the actual link builder without MACE | `P0-TEST-G04-01`, `P0-TEST-G04-03`, `P0-TEST-G04-04` |
| `G04-T2` | Validate geometry and both real-parent forces | `P0-TEST-G04-02`, `P0-TEST-G04-06` |
| `G04-T3` | Repeat under ATM and across reload | `P0-TEST-G04-05`, `P0-TEST-G04-02`, `P0-TEST-G04-06` |

### G04-T1: exercise the actual link builder without MACE

**Read:** [S04: Mechanical baseline and boundary policy](../specs/S04-embedding-and-model-contracts.md#mechanical-baseline-and-boundary-policy); [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules).

Construct a simple alkane-like covalent fixture with one reviewed carbon-carbon cut and a chemically closed capped fragment. Add a dedicated small bonded graph when a particular angle/torsion predicate needs isolation. Use distinctive parameters so removal cannot be inferred merely from a force count.

Use a registered analytic model substitute while retaining the real OpenMM-ML boundary-building path. Obtain final topology and index mapping, initialize real positions through the map, and compute derived sites before evaluating energy. Derive cap identities from actual system/topology differences and virtual-site parents, not residue labels.

### G04-T2: validate geometry and both real-parent forces

**Read:** [S04: Mechanical baseline and boundary policy](../specs/S04-embedding-and-model-contracts.md#mechanical-baseline-and-boundary-policy); [S06: Starting numerical thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds).

Record the actual cap distance from the constructed system, rather than assuming a remembered default. Verify zero mass and no unintended MM nonbonded center. Use the S04 cap Jacobian for a known analytic cap potential and compare forces while perturbing each parent along and perpendicular to the boundary bond.

Recompute virtual sites after every perturbation and restore the complete saved state. Do not reproject onto constraints when testing ordinary Cartesian derivatives. Sum parent force contributions as an additional diagnostic, but do not let that replace component-level Jacobian tests.

### G04-T3: repeat under ATM and across reload

**Read:** [S04: Early environment-dependent contract probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe); [S07: Loading, restart, and workers](../specs/S07-artifacts-and-qualification.md#loading-restart-and-workers).

Place the stationary boundary in the analytic ATM fixture while translating a separate whole ligand. Test both coordinate states and an intermediate. Numerical evidence decides whether the existing virtual-site machinery redistributes correctly; do not copy internal virtual sites or redistribute cap forces manually as a speculative repair.

Add the cap-environment analytic term to exercise a future environment-sensitive force path. Serialize, reload in a fresh process, and repeat positions/parent derivatives. Periodic image handling is expanded in G06, but preserve an explicit coordinate convention already here.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G04-01 | `tests/integration/test_link_geometry.py::test_cap_position_and_zero_mass` | Construct the stated fixed-length cap from its actual parents; verify virtual-site type, mass, parameters and final count. | P0-REQ-008 |
| P0-TEST-G04-02 | `tests/integration/test_link_geometry.py::test_cap_parent_chain_rule` | For axial/perpendicular real-parent perturbations, the analytic Jacobian and energy finite differences agree with returned real forces. | P0-REQ-004 |
| P0-TEST-G04-03 | `tests/integration/test_boundary_ledger.py::test_each_boundary_term_disposition` | Distinct bond, angle, proper/improper torsion, exception and constraint fixtures have exactly the reviewed retained/removed disposition. | P0-REQ-003, P0-REQ-008 |
| P0-TEST-G04-04 | `tests/integration/test_link_geometry.py::test_actual_and_nonidentity_index_maps` | Consume current appended-site mapping and a synthetic nonidentity map; cap and ligand identities remain correct. | P0-REQ-002 |
| P0-TEST-G04-05 | `tests/integration/test_link_geometry.py::test_stationary_cap_force_under_atm` | Both real parents receive exactly one cap contribution inside ATM; energy agreement alone cannot satisfy this check. | P0-REQ-004, P0-REQ-013 |
| P0-TEST-G04-06 | `tests/integration/test_link_geometry.py::test_cap_environment_cross_derivative` | A harmonic cap-MM environment term produces both parent derivatives and the real environment derivative without double redistribution. | P0-REQ-004, P0-REQ-006 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_link_geometry.py tests/integration/test_boundary_ledger.py -v
```

**Stop and diagnose:** A cap-position, boundary-ledger, or derivative mismatch blocks real model integration. Isolate whether the error is geometry, virtual-site force propagation, duplicated contributions, constraints, or indexing before changing a cap rule.

## Keep future changes possible

Cap force propagation is independent of model brand and transfer protocol. The environment-sensitive cap probe protects future full-coordinate derivatives without claiming electronic embedding support.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Worker:** `Gate_04_vN_worker.md`; **audit:** `Gate_04_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).
