# G13: Measure cost and decide what the release actually supports

**Part of:** [M08](../milestones/M08-project-1-handover.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

The project needs a usable and reproducible release, not just a successful notebook. Measure performance without mixing speed improvements with changes in the energy model or integration method.

## Expected outcome

A reproducible release package with measured costs, explicit supported setups, untested limits, and a Project-1 handover.

**Not part of this gate:** Do not optimize before correctness or advertise untested model, hardware, or embedding combinations.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M08: outcome and dependencies](../milestones/M08-project-1-handover.md) | See how this gate fits into the larger result. |
| [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested) | Tie a result to the actual code, checkpoint, input, and hardware. |
| [S07: Review and reporting](../specs/S07-artifacts-and-qualification.md#review-and-reporting) | Make release claims only for the tested and reviewed setup. |
| [S02: Extension promises and limits](../specs/S02-architecture-and-dependencies.md#extension-promises-and-limits) | Keep extension points without claiming all future physics already fits. |
| [Scientific notes](../reference/scientific-notes.md) | Diagnostic-versus-correction meaning or performance units, as relevant. |
| [This gate's log folder](../../../Worker_Log/Milestone_08/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G11](../gates/G11-protein-abfe.md), [G12](../gates/G12-dual-ligand-rbfe.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** Accepted G11 ABFE and G12 RBFE evidence plus dependency profiles; complete documented model and environment artifacts.

**Outputs used by later gates:** Clean-environment regression report, scoped support matrix, performance measurements, known limitations and reviewed Project-1 handover.

**Planned source/test paths:** `report.py`, benchmark scripts, qualification documentation, release manifests and regression tests for any admitted optimization.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G13-T1` | Benchmark the correct implementation | `P0-TEST-G13-03` |
| `G13-T2` | Admit optimizations one at a time | `P0-TEST-G13-04` |
| `G13-T3` | Release only the qualified claims | `P0-TEST-G13-01`, `P0-TEST-G13-02`, `P0-TEST-G13-05` |

### G13-T1: benchmark the correct implementation

Measure context/model loading, first evaluation, and steady-state stepping separately, synchronizing accelerators appropriately. Compare all-MM, ligand-only ML/MM, cavity-inclusive ML/MM, native ATM and AToM worker paths on the same hardware and relevant common settings. Record real/ML/cap counts, graph size, dtype, OpenMM precision, timestep, force evaluations, memory per worker and synchronization/transfer overhead.

Start with one worker. Measure nested model copies and process costs before assuming ATM is exactly twice as expensive. Throughput with a changed timestep is not a pure backend speedup. Use the explicit unit formulas and distinguish wall time from aggregate GPU hours.

**Finish this part with:** the relevant test results above and a worker log that states `G13-T1` as its scope. Completing this part alone does not complete G13.

### G13-T2: admit optimizations one at a time

Profile before changing behavior. First reduce avoidable transfers or repeated immutable work, then consider context/model reuse and approved precision. Excluding rigorously invariant terms from ATM requires a coordinate and mixing-expression proof plus numerical regression. A new timestep, HMR, MTS, pressure ensemble or multigpu configuration is not a free optimization; it requires its own admission.

Do not design a GPU neighbor-list kernel or train a smaller model before demonstrating that it addresses the measured bottleneck. The unoptimized correct reference remains available for regression.

**Finish this part with:** the relevant test results above and a worker log that states `G13-T2` as its scope. Completing this part alone does not complete G13.

### G13-T3: release only the qualified claims

Run the complete applicable suite from a clean environment. Have a colleague reproduce the smallest correct example and inspect an intentional fault-injection failure. Record independent review only if it happened. Produce a matrix by model/embedding/protocol/hardware/precision/ensemble, with unsupported and unexecuted combinations clearly marked.

Handover includes source/asset identity, requirements, gate reports, ABFE/RBFE examples, known-answer analysis, restart/exchange evidence, performance and scientific limitations. The decision may be qualified for stated Project-1 trials, qualified for a narrower configuration, or not qualified. A partial hardware profile is not a reason to claim universal completion.

**Finish this part with:** the relevant test results above and a worker log that states `G13-T3` as its scope. Completing this part alone does not complete G13.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G13-01 | `tests/workflow/test_release_bundle.py::test_clean_offline_reproduction` | A clean admitted environment and offline asset bundle reproduce deterministic checks and required workflow evidence. | P0-REQ-025, P0-REQ-029 |
| P0-TEST-G13-02 | `tests/contracts/test_release_evidence.py::test_claimed_profiles_have_required_evidence` | Every claimed capability references accepted gate/profile evidence; absent GPU or extended sampling results cannot be promoted. | P0-REQ-025, P0-REQ-032 |
| P0-TEST-G13-03 | `tests/unit/test_benchmark_metrics.py::test_time_and_resource_units` | Distinguish startup and steady state; ns/day=0.0864*dt_fs/step_seconds; aggregate resource estimates do not double-count replicas. | P0-REQ-027 |
| P0-TEST-G13-04 | `tests/integration/test_optimization_equivalence.py::test_optimized_scope_preserves_hamiltonian` | Any admitted routing/precision/invariant-term change passes endpoint, force, known-answer and affected regression checks. | P0-REQ-027, P0-REQ-011 |
| P0-TEST-G13-05 | `tests/contracts/test_release_evidence.py::test_implementation_sampling_physics_separate` | Release statements distinguish implemented, smoke-tested, sampled, physically assessed and explicitly unsupported combinations. | P0-REQ-025, P0-REQ-028, P0-REQ-032 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_release_bundle.py tests/contracts/test_release_evidence.py tests/unit/test_benchmark_metrics.py tests/integration/test_optimization_equivalence.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Without reproducible evidence for the claimed profile, do not tag it as qualified. Fix a reproducibility or regression failure before performance promotion; retain partial supported scope honestly.

## Keep future changes possible

The release matrix keeps future electrostatic and model additions separate while preserving the common contracts. A later extension reruns affected profiles instead of retroactively expanding old evidence.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_08/`\
**Task stem:** `Gate_13`\
**Worker:** `Gate_13_vN_worker.md`\
**Matching audit:** `Gate_13_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
