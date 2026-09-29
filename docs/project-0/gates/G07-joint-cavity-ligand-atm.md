# G07: Combine the capped fragment, ligand, model, and ATM

**Part of:** [M03](../milestones/M03-mechanical-hybrid.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

The parts must still work when combined. The ligand must interact with the cavity in one geometry and separate correctly in the other without changing ML membership.

## Expected outcome

A small complete cavity-inclusive example that agrees between direct evaluation, native ATM, and the AToM-built route.

**Not part of this gate:** Keep this example small enough to debug. Do not move to a whole protein while a combined energy or force mismatch remains.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M03: outcome and dependencies](../milestones/M03-mechanical-hybrid.md) | See how this gate fits into the larger result. |
| [S04: The physical contract is broader than the first embedding](../specs/S04-embedding-and-model-contracts.md#the-physical-contract-is-broader-than-the-first-embedding) | Keep all real-coordinate forces available to the transfer machinery. |
| [S04: Early environment-dependent contract probe](../specs/S04-embedding-and-model-contracts.md#early-environment-dependent-contract-probe) | Check forces on MM atoms and reevaluation after a coordinate change. |
| [S06: Independent oracles and fault injection](../specs/S06-validation-and-tolerances.md#independent-oracles-and-fault-injection) | Use an independent answer and prove the tests catch known mistakes. |
| [This gate's log folder](../../../Worker_Log/Milestone_03/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G03](../gates/G03-atom-routing-and-integration.md), [G04](../gates/G04-link-boundary-and-derivatives.md), [G05](../gates/G05-local-model-adapter.md), [G06](../gates/G06-periodicity-and-interaction-ledger.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G03 validated AToM routing, G04 cap derivatives, G05 real model, G06 periodic/ledger checks.

**Outputs used by later gates:** Small nonperiodic and periodic joint fixtures, three-route agreement, extension-contract regression evidence, and a documented admitted mechanical profile.

**Planned source/test paths:** `fixtures/fragment_ligand/`, `endpoints.py`, `tests/integration/test_joint_hybrid_atm.py`, `tests/contracts/test_embedding_extension.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G07-T1` | Combine already qualified ingredients without solvent | `P0-TEST-G07-01`, `P0-TEST-G07-02`, `P0-TEST-G07-03`, `P0-TEST-G07-04` |
| `G07-T2` | Run extension-contract regressions against the integrated architecture | `P0-TEST-G07-05`, `P0-TEST-G07-02` |
| `G07-T3` | Introduce the admitted periodic version | `P0-TEST-G07-06` |

### G07-T1: combine already qualified ingredients without solvent

Assemble one stationary capped neutral fragment and one complete neutral ligand. Use the real local checkpoint and exact cap/ledger convention. Directly evaluate a contacting and a separated geometry. Repeat via native ATM and the explicit AToM adapter for endpoint and intermediate settings.

Check forces on every relevant kind of real coordinate, particularly an MM boundary parent. A ligand-only comparison would miss part of the new cavity-inclusive problem. Save hand-checked atom maps and confirm fixed ML membership; the joint ML energy should respond to contact geometry without any 'bound' branch.

**Finish this part with:** the relevant test results above and a worker log that states `G07-T1` as its scope. Completing this part alone does not complete G07.

### G07-T2: run extension-contract regressions against the integrated architecture

Reuse the analytic environment-dependent provider with the combined boundary fixture. Verify that full MM and parent forces still travel through the same assembler and checker. Run both one-/two-group protocol definitions from G02. These are small contract probes, not molecular RBFE acceptance and not actual electrostatic embedding.

Review common-module imports and signatures. If adding this provider requires editing the transfer engine, stop and correct the abstraction now. A capability rejection is appropriate for unsupported physics, but not an excuse to leave a shared ML-only-force assumption untested.

**Finish this part with:** the relevant test results above and a worker log that states `G07-T2` as its scope. Completing this part alone does not complete G07.

### G07-T3: introduce the admitted periodic version

Only after the nonperiodic comparison passes, add the G06 periodic convention and repeat geometry, graph, endpoint and derivative checks. Record caps, box and alternate geometries. Test near the relevant safety limits rather than one relaxed favorable frame.

This fixture should stay small enough for a colleague to understand every selected atom and boundary. It is the central correctness reproducer to preserve when later protein runs fail.

**Finish this part with:** the relevant test results above and a worker log that states `G07-T3` as its scope. Completing this part alone does not complete G07.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G07-01 | `tests/integration/test_joint_hybrid_atm.py::test_direct_native_and_atom_agree` | Direct physical, native ATM and AToM-built child/total energies and real forces match at both maps and intermediate states. | P0-REQ-013, P0-REQ-021 |
| P0-TEST-G07-02 | `tests/integration/test_joint_hybrid_atm.py::test_mm_boundary_parent_force` | An MM boundary parent receives its full cap-induced derivative at both coordinate maps; omitted propagation fails. | P0-REQ-004, P0-REQ-006 |
| P0-TEST-G07-03 | `tests/integration/test_joint_hybrid_atm.py::test_joint_contact_and_disconnected_graph` | Contacting input uses a joint graph; separated local-component behavior matches G05 without changing ML membership. | P0-REQ-002, P0-REQ-009 |
| P0-TEST-G07-04 | `tests/integration/test_joint_hybrid_atm.py::test_only_mobile_groups_translate` | Protein real atoms, cap parents and cap sites have zero explicit displacement while complete ligand IDs move. | P0-REQ-002, P0-REQ-013 |
| P0-TEST-G07-05 | `tests/contracts/test_embedding_extension.py::test_environment_provider_reuses_atm_and_protocols` | Swap only the analytic physical provider and reuse both protocols, assembler, records and checker; no embedding branch is added to common code. | P0-REQ-001, P0-REQ-028 |
| P0-TEST-G07-06 | `tests/integration/test_joint_hybrid_atm.py::test_joint_periodic_geometry_and_forces` | Repeat the small admitted periodic version after the nonperiodic oracle passes; preserve both geometries on failure. | P0-REQ-005 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/integration/test_joint_hybrid_atm.py tests/contracts/test_embedding_extension.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Return to the smallest failing lower gate for an energy, derivative, topology or periodic mismatch. Do not prepare a protein until this combined physical/transfer composition is demonstrated.

## Keep future changes possible

At this point architectural substitution is demonstrated with analytic providers while the one real mechanical provider is numerically exercised. Document these as different capability levels.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_03/`\
**Task stem:** `Gate_07`\
**Worker:** `Gate_07_vN_worker.md`\
**Matching audit:** `Gate_07_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
