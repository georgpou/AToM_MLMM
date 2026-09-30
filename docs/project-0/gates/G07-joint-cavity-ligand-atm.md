# G07: Combine the capped fragment, ligand, model, and ATM

**Part of:** [M03](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

The parts must still work when combined. The ligand must interact with the cavity in one geometry and separate correctly in the other without changing ML membership.

## Expected outcome

A small complete cavity-inclusive example that agrees between direct evaluation, native ATM, and the AToM-built route.

**Not part of this gate:** Keep this example small enough to debug. Do not move to a whole protein while a combined energy or force mismatch remains.

## Before starting

Required earlier gates: [G03](../gates/G03-atom-routing-and-integration.md), [G04](../gates/G04-link-boundary-and-derivatives.md), [G05](../gates/G05-local-model-adapter.md), [G06](../gates/G06-periodicity-and-interaction-ledger.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G03 validated AToM routing, G04 cap derivatives, G05 real model, G06 periodic/ledger checks.

**Outputs used by later gates:** Small nonperiodic and periodic joint fixtures, three-route agreement, extension-contract regression evidence, and a documented admitted mechanical profile.

**Planned source/test paths:** `fixtures/fragment_ligand/`, `endpoints.py`, `tests/integration/test_joint_hybrid_atm.py`, `tests/contracts/test_embedding_extension.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G07-T1` | Combine already qualified ingredients without solvent | `P0-TEST-G07-01`, `P0-TEST-G07-02`, `P0-TEST-G07-03`, `P0-TEST-G07-04` |
| `G07-T2` | Run extension-contract regressions against the integrated architecture | `P0-TEST-G07-05`, `P0-TEST-G07-02` |
| `G07-T3` | Introduce the admitted periodic version | `P0-TEST-G07-06` |

### G07-T1: combine already qualified ingredients without solvent

**Read:** [S04: The physical contract is broader than the first embedding](../specs/S04-embedding-and-model-contracts.md#the-physical-contract-is-broader-than-the-first-embedding); [S06: Independent oracles and fault injection](../specs/S06-validation-and-tolerances.md#independent-oracles-and-fault-injection).

Assemble one stationary capped neutral fragment and one complete neutral ligand. Use the real local checkpoint and exact cap/ledger convention. Directly evaluate a contacting and a separated geometry. Repeat via native ATM and the explicit AToM adapter for endpoint and intermediate settings.

Check forces on every relevant kind of real coordinate, particularly an MM boundary parent. A ligand-only comparison would miss part of the new cavity-inclusive problem. Save hand-checked atom maps and confirm fixed ML membership; the joint ML energy should respond to contact geometry without any 'bound' branch.

### G07-T2: run extension-contract regressions against the integrated architecture

**Read:** [S04: Early environment-dependent contract probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe); [S02: Dependency rules and ownership tests](../specs/S02-architecture-and-dependencies.md#dependency-rules-and-ownership-tests).

Reuse the analytic environment-dependent provider with the combined boundary fixture. Verify that full MM and parent forces still travel through the same assembler and checker. Run both one-/two-group protocol definitions from G02. These are small contract probes, not molecular RBFE acceptance and not actual electrostatic embedding.

Review common-module imports and signatures. If adding this provider requires editing the transfer engine, stop and correct the abstraction now. A capability rejection is appropriate for unsupported physics, but not an excuse to leave a shared ML-only-force assumption untested.

### G07-T3: introduce the admitted periodic version

**Read:** [S04: Periodic and long-range accounting](../specs/S04-embedding-and-model-contracts.md#periodic-and-long-range-accounting); [S06: Starting numerical thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds).

Only after the nonperiodic comparison passes, add the G06 periodic convention and repeat geometry, graph, endpoint and derivative checks. Record caps, box and alternate geometries. Test near the relevant safety limits rather than one relaxed favorable frame.

This fixture should stay small enough for a colleague to understand every selected atom and boundary. It is the central correctness reproducer to preserve when later protein runs fail.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G07-01 | `tests/integration/test_joint_hybrid_atm.py::test_direct_native_and_atom_agree` | Direct physical, native ATM and AToM-built child/total energies and real forces match at both maps and intermediate states. | P0-REQ-013, P0-REQ-021 |
| P0-TEST-G07-02 | `tests/integration/test_joint_hybrid_atm.py::test_mm_boundary_parent_force` | An MM boundary parent receives its full cap-induced derivative at both coordinate maps; omitted propagation fails. | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G07-03 | `tests/integration/test_joint_hybrid_atm.py::test_joint_contact_and_disconnected_graph` | Contacting input uses a joint graph; separated local-component behavior matches G05 without changing ML membership. | P0-REQ-002, P0-REQ-009 |
| P0-TEST-G07-04 | `tests/integration/test_joint_hybrid_atm.py::test_only_mobile_groups_translate` | Protein real atoms, cap parents and cap sites have zero explicit displacement while complete ligand IDs move. | P0-REQ-002, P0-REQ-013 |
| P0-TEST-G07-05 | `tests/contracts/test_embedding_extension.py::test_environment_provider_reuses_atm_and_protocols` | Swap only the analytic physical provider and reuse both protocols, assembler, records and checker; no embedding branch is added to common code. | P0-REQ-001, P0-REQ-028 |
| P0-TEST-G07-06 | `tests/integration/test_joint_hybrid_atm.py::test_joint_periodic_geometry_and_forces` | Repeat the small admitted periodic version after the nonperiodic oracle passes; preserve both geometries on failure. | P0-REQ-005 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_joint_hybrid_atm.py tests/contracts/test_embedding_extension.py -v
```

**Stop and diagnose:** Return to the smallest failing lower gate for an energy, derivative, topology or periodic mismatch. Do not prepare a protein until this combined physical/transfer composition is demonstrated.

## Keep future changes possible

At this point architectural substitution is demonstrated with analytic providers while the one real mechanical provider is numerically exercised. Document these as different capability levels.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Worker:** `Gate_07_vN_worker.md`; **audit:** `Gate_07_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M03 combined review

**Review scope:** G04, G05, G06, G07. **Earlier milestone reviews:** M02. These are combined-review conditions, not additional implementation prerequisites.

Inspect the cap-parent Jacobian evidence and the complete retained/removed boundary ledger. Verify caps are derived sites with the intended classical treatment. An energy-only check is not sufficient.

Review native-model agreement, units/energy convention, local-component tests, counterfactual contact scans and offline identity. Inspect the exact retained PME convention, mask diagnostics and periodic geometry/seam tests; do not call all classical cavity-ligand electrostatics missing by definition.

Finally inspect the small capped-cavity/ligand fixture through direct, native ATM and AToM paths. Include MM-parent derivatives and the early extension-contract regressions. The combined fixture remains the reproducible reference for later protein failures.

G04-G07 accepted for the declared local mechanical profile; no unexplained identity, derivative, interaction-ledger, image or counterfactual-domain failure remains.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_03_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
