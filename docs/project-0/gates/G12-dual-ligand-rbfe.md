# G12: Run the first two-ligand RBFE example

**Part of:** [M07](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

The shared architecture already allows two mobile groups. This gate checks the molecular result, both ligand identities, and the meaning of comparisons against ABFE.

## Expected outcome

A nontrivial ligand-pair example, an identity control, a sign-reversal check, and a careful comparison of matching thermodynamic states.

**Not part of this gate:** Do not create an RBFE-specific energy engine. Do not interpret a finite-box spectator-ligand effect as a code defect without checking the state definitions.

## Before starting

Required earlier gates: [G11](../gates/G11-protein-abfe.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G11 protein ABFE baseline; G02/G03 early two-ligand contracts; G10 worker reliability; a reviewed ligand-pair manifest.

**Outputs used by later gates:** One nontrivial RBFE profile, A-to-A and reversal controls, graph/identity evidence and a matched-state closure report.

**Planned source/test paths:** `fixtures/protein_two_ligands/`, `tests/workflow/test_rbfe_transforms.py`, `tests/sampling/test_binding_closure.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G12-T1` | Qualify molecular two-ligand geometry on the small fixture | `P0-TEST-G12-01`, `P0-TEST-G12-02`, `P0-TEST-G12-06` |
| `G12-T2` | Run identity, reversal and nontrivial-pair controls | `P0-TEST-G12-03`, `P0-TEST-G12-04`, `P0-TEST-G12-06` |
| `G12-T3` | Interpret closure against matched states | `P0-TEST-G12-05` |

### G12-T1: qualify molecular two-ligand geometry on the small fixture

**Read:** [S05: One protocol contract, two initial presets](../specs/S05-protocol-and-thermodynamic-contracts.md#one-protocol-contract-two-initial-presets); [S03: Identity and transformation rules](../specs/S03-data-and-interface-contracts.md#identity-and-transformation-rules).

Add a second complete ligand first to the small solvated fixture. Use explicit opposite fixed maps and hand-checked final identities. Test both coordinate states, cap-parent derivatives and unexpected ligand-ligand/image contacts. The architecture already admitted two groups in G02; this gate adds molecular evidence rather than introducing the concept for the first time.

Keep one cavity, model, cap, embedding and classical convention across comparable calculations. Do not change the receptor model per ligand while expecting exact cancellation. Re-run fresh-process and two-worker checks with the larger joint model input.

### G12-T2: run identity, reversal and nontrivial-pair controls

**Read:** [S05: Shared analysis and molecular closure](../specs/S05-protocol-and-thermodynamic-contracts.md#shared-analysis-and-molecular-closure); [S05: Binding definition and correction completeness](../specs/S05-protocol-and-thermodynamic-contracts.md#binding-definition-and-correction-completeness).

Use a symmetric A-to-A calculation with matched restraints. Its equilibrium free-energy difference should be zero, but its instantaneous perturbations can be nonzero because environments and conformations differ. Evaluate zero-consistency using the declared uncertainty criteria and adequate overlap.

Then run a nontrivial A-to-B pair and reverse the endpoint labeling. Apply the explicit relative sign convention from S05. Check that identity/name ordering and upstream-specific keys never change the selected ligand set or reverse a correction silently.

### G12-T3: interpret closure against matched states

**Read:** [S05: Shared analysis and molecular closure](../specs/S05-protocol-and-thermodynamic-contracts.md#shared-analysis-and-molecular-closure); [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility).

Compare an RBFE with corresponding ABFE differences and, where useful, a small closed cycle. The two-ligand box has a spectator molecule: simple subtraction of independent one-ligand ABFEs is not automatically an exact closure relation. Use matched spectator controls or quantify the contribution, alongside restraint, finite-box and model-region differences.

Keep covariance where calculations share data or corrections. A mismatch first triggers an audit of thermodynamic definition, restraints, identity and spectator effects; it is not immediate evidence of faulty ML chemistry.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G12-01 | `tests/workflow/test_rbfe_transforms.py::test_opposite_group_maps_and_cap_identity` | Complete A/B groups receive the prescribed opposite translations; protein/cap maps and identities remain unchanged. | P0-REQ-022, P0-REQ-002 |
| P0-TEST-G12-02 | `tests/workflow/test_rbfe_transforms.py::test_correct_bound_component_and_no_spurious_contact` | Each endpoint connects the intended local-model ligand to the cavity and excludes unintended other-ligand/image contacts. | P0-REQ-005, P0-REQ-009 |
| P0-TEST-G12-03 | `tests/sampling/test_binding_closure.py::test_symmetric_a_to_a_free_energy` | Symmetric A-to-A equilibrium difference is compatible with zero under predeclared uncertainty criteria, without requiring instantaneous perturbation zero. | P0-REQ-016 |
| P0-TEST-G12-04 | `tests/sampling/test_binding_closure.py::test_reversed_pair_sign` | Reversed endpoint labels negate the intended relative observable while preserving the same physical model and correction accounting. | P0-REQ-016, P0-REQ-031 |
| P0-TEST-G12-05 | `tests/sampling/test_binding_closure.py::test_abfe_rbfe_comparison_matches_states` | Account for spectator-ligand, restraint, cavity/model/constraint and finite-box differences before interpreting closure. | P0-REQ-031, P0-REQ-019 |
| P0-TEST-G12-06 | `tests/workflow/test_rbfe_transforms.py::test_shared_pipeline_and_restart` | The larger joint input uses the same physical builder, ATM assembler, observable schema and restart contracts without per-RBFE physics forks. | P0-REQ-001, P0-REQ-022, P0-REQ-015 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_rbfe_transforms.py tests/sampling/test_binding_closure.py -v
```

**Stop and diagnose:** A graph/map/identity failure returns to the existing small two-group oracle. A closure failure requires state matching before code or model changes. Do not create a second simulation engine to make one RBFE example run.

## Keep future changes possible

This milestone tests the benefit of designing multiple-group protocols early. Actual electrostatic RBFE will need a new physical profile, not a duplicate pipeline.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_07/`\
**Worker:** `Gate_12_vN_worker.md`; **audit:** `Gate_12_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M07 combined review

**Review scope:** G12. **Earlier milestone reviews:** M06. These are combined-review conditions, not additional implementation prerequisites.

Inspect opposite complete-ligand maps, cap identity, correct bound-component graphs and unintended ligand/image contacts. Re-run reload/exchange checks for the larger joint input.

Review symmetric A-to-A and nontrivial reversed-pair results with explicit sign and correction conventions. Compare against ABFE differences only after matching cavity/model/constraint/restraint and spectator-ligand definitions. A finite-box mismatch is not automatically a code defect, and apparent closure does not excuse an identity error.

G12 accepted for the declared molecular RBFE profile with identity/reversal controls, matched-state closure interpretation and no separate RBFE physical engine.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_07_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
