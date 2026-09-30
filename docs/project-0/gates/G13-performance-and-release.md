# G13: Measure cost and decide what the release actually supports

**Part of:** [M08](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

The project needs a usable and reproducible release, not just a successful notebook. Measure performance without mixing speed improvements with changes in the energy model or integration method.

## Expected outcome

A reproducible release package with measured costs, explicit supported setups, untested limits, and a Project-1 handover.

**Not part of this gate:** Do not optimize before correctness or advertise untested model, hardware, or embedding combinations.

## Before starting

Required earlier gates: [G11](../gates/G11-protein-abfe.md), [G12](../gates/G12-dual-ligand-rbfe.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** Accepted G11 ABFE and G12 RBFE evidence plus dependency profiles; complete documented model and environment artifacts.

**Outputs used by later gates:** Clean-environment regression report, scoped support matrix, performance measurements, known limitations and reviewed Project-1 handover.

**Planned source/test paths:** `report.py`, benchmark scripts, qualification documentation, release manifests and regression tests for any admitted optimization.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G13-T1` | Benchmark the correct implementation | `P0-TEST-G13-03` |
| `G13-T2` | Admit optimizations one at a time | `P0-TEST-G13-04` |
| `G13-T3` | Release only the qualified claims | `P0-TEST-G13-01`, `P0-TEST-G13-02`, `P0-TEST-G13-05` |

### G13-T1: benchmark the correct implementation

**Read:** [performance arithmetic](#performance-arithmetic); [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested).

Measure context/model loading, first evaluation, and steady-state stepping separately, synchronizing accelerators appropriately. Compare all-MM, ligand-only ML/MM, cavity-inclusive ML/MM, native ATM and AToM worker paths on the same hardware and relevant common settings. Record real/ML/cap counts, graph size, dtype, OpenMM precision, timestep, force evaluations, memory per worker and synchronization/transfer overhead.

Start with one worker. Measure nested model copies and process costs before assuming ATM is exactly twice as expensive. Throughput with a changed timestep is not a pure backend speedup. Use the explicit unit formulas and distinguish wall time from aggregate GPU hours.

### G13-T2: admit optimizations one at a time

**Read:** [S02: Force ownership and execution](../specs/S02-architecture-and-dependencies.md#force-ownership-and-execution); [S02: Extension promises and limits](../specs/S02-architecture-and-dependencies.md#extension-promises-and-limits).

Profile before changing behavior. First reduce avoidable transfers or repeated immutable work, then consider context/model reuse and approved precision. Excluding rigorously invariant terms from ATM requires a coordinate and mixing-expression proof plus numerical regression. A new timestep, HMR, MTS, pressure ensemble or multigpu configuration is not a free optimization; it requires its own admission.

Do not design a GPU neighbor-list kernel or train a smaller model before demonstrating that it addresses the measured bottleneck. The unoptimized correct reference remains available for regression.

### G13-T3: release only the qualified claims

**Read:** [S07: Review and reporting](../specs/S07-artifacts-and-qualification.md#review-and-reporting); [Project 1 handover](#path-to-project-1).

Run the complete applicable suite from a clean environment. Have a colleague reproduce the smallest correct example and inspect an intentional fault-injection failure. Record independent review only if it happened. Produce a matrix by model/embedding/protocol/hardware/precision/ensemble, with unsupported and unexecuted combinations clearly marked.

Handover includes source/asset identity, requirements, gate reports, ABFE/RBFE examples, known-answer analysis, restart/exchange evidence, performance and scientific limitations. The decision may be qualified for stated Project-1 trials, qualified for a narrower configuration, or not qualified. A partial hardware profile is not a reason to claim universal completion.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G13-01 | `tests/workflow/test_release_bundle.py::test_clean_offline_reproduction` | A clean admitted environment and offline asset bundle reproduce deterministic checks and required workflow evidence. | P0-REQ-025, P0-REQ-029 |
| P0-TEST-G13-02 | `tests/contracts/test_release_evidence.py::test_claimed_profiles_have_required_evidence` | Every claimed capability references accepted gate/profile evidence; absent GPU or extended sampling results cannot be promoted. | P0-REQ-025, P0-REQ-032 |
| P0-TEST-G13-03 | `tests/unit/test_benchmark_metrics.py::test_time_and_resource_units` | Distinguish startup and steady state; ns/day=0.0864*dt_fs/step_seconds; aggregate resource estimates do not double-count replicas. | P0-REQ-027 |
| P0-TEST-G13-04 | `tests/integration/test_optimization_equivalence.py::test_optimized_scope_preserves_hamiltonian` | Any admitted routing/precision/invariant-term change passes endpoint, force, known-answer and affected regression checks. | P0-REQ-027, P0-REQ-011 |
| P0-TEST-G13-05 | `tests/contracts/test_release_evidence.py::test_implementation_sampling_physics_separate` | Release statements distinguish implemented, smoke-tested, sampled, physically assessed and explicitly unsupported combinations. | P0-REQ-025, P0-REQ-028, P0-REQ-032 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_release_bundle.py tests/contracts/test_release_evidence.py tests/unit/test_benchmark_metrics.py tests/integration/test_optimization_equivalence.py -v
```

**Stop and diagnose:** Without reproducible evidence for the claimed profile, do not tag it as qualified. Fix a reproducibility or regression failure before performance promotion; retain partial supported scope honestly.

## Keep future changes possible

The release matrix keeps future electrostatic and model additions separate while preserving the common contracts. A later extension reruns affected profiles instead of retroactively expanding old evidence.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_08/`\
**Worker:** `Gate_13_vN_worker.md`; **audit:** `Gate_13_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M08 combined review

**Review scope:** G13. **Earlier milestone reviews:** M07. These are combined-review conditions, not additional implementation prerequisites.

Review a clean offline reproduction and the complete applicable regression suite. Ensure accepted claims reference exact model/embedding/protocol/platform/precision/ensemble profiles. Skipped hardware and unrun long sampling stay visibly unqualified.

Review startup versus steady-state performance, model/worker memory, actual throughput units and any optimization-equivalence evidence. Record independent colleague review only when performed.

Decide whether the framework is qualified for named Project-1 trials, only a narrower configuration, or not yet qualified. Preserve the smallest fixtures, exact manifests, analysis/sign/correction documentation and limitations in the release.

G13 accepted and a release review explicitly states supported, unqualified and deferred combinations. Both ABFE and RBFE claims have their own molecular evidence.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_08_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.

## Performance arithmetic

Separate context construction, model loading, first evaluation and steady-state stepping. Synchronize accelerator timing. For timestep dt in fs and step time t in seconds:

$$\mathrm{ns/day}=0.0864\,dt/t.$$

For Nw windows, Nr independent repetitions, Tns nanoseconds per window and effective throughput s ns/day per occupied GPU:

$$\mathrm{GPU\ hours}\approx 24 N_wN_r T_{\mathrm{ns}}/s.$$

Do not double-count windows if measured throughput already aggregates them. Wall time and total GPU use differ. A larger timestep is not a pure backend speed improvement. Profile before implementing a new neighbor kernel, reducing the ML region, or training a smaller model.

## Path to Project 1

Project 0 establishes the declared numerical and thermodynamic platform. Project 1 evaluates ordinary noncovalent systems and the physical usefulness of cavity-inclusive ML/MM. Start with matched all-MM, ligand-only and cavity-inclusive comparisons on a small well-characterized series. Keep cavity, caps and model definitions fixed where cancellation is intended.

Experimental disagreement can arise from sampling, preparation, protonation, force-field cross interactions, embedding or model chemistry. Experimental agreement cannot prove that an implementation has the right gradients or correction signs. Later fine-tuning should test ligand-only versus cavity-plus-ligand training with appropriate independent data, not tune hidden corrections to match affinities.

Actual electrostatic embedding, metals and covalent reactions require new physical definitions and possibly new thermodynamic cycles. The current contracts make the transfer engine reusable; they do not solve those future chemistry problems.
