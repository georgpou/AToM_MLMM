# G10: Check restart, process boundaries, and replica exchange

**Part of:** [M05](../milestones/M05-solvated-workflow.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

A result is not reproducible if a fresh process loads a different model, loses a parameter, or swaps states using stale energies. Test these risks on the small solvated system.

## Expected outcome

Fresh-process, restart, and small replica-exchange evidence, with stable sample identities and verified device assignment.

**Not part of this gate:** Single-GPU success does not qualify multiple GPUs. A portable State is not a promise of identical random-number continuation.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M05: outcome and dependencies](../milestones/M05-solvated-workflow.md) | See how this gate fits into the larger result. |
| [S07: Loading, restart, and workers](../specs/S07-artifacts-and-qualification.md#loading-restart-and-workers) | Check fresh-process loading, parameters, continuation, and device placement. |
| [S07: Required observable names](../specs/S07-artifacts-and-qualification.md#required-observable-names) | Preserve unambiguous endpoint, outside, and total energy records. |
| [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility) | Separate sampling uncertainty, correlation, and physical sensitivity. |
| [This gate's log folder](../../../Worker_Log/Milestone_05/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G09](../gates/G09-solvent-preparation-and-export.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G09 complete solvated worker handover and raw-record schema.

**Outputs used by later gates:** Offline reconstruction, same-profile checkpoint continuation, portable-State checks, two-state exchange evidence and device/restart audit.

**Planned source/test paths:** `persistence.py`, `observables.py`, `tests/workflow/test_fresh_process.py`, `tests/workflow/test_restart.py`, `tests/workflow/test_replica_exchange.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G10-T1` | Challenge all process-boundary assumptions | `P0-TEST-G10-01`, `P0-TEST-G10-02` |
| `G10-T2` | Check the exchange decision independently | `P0-TEST-G10-03`, `P0-TEST-G10-04` |
| `G10-T3` | Test interrupted execution and hardware placement | `P0-TEST-G10-05`, `P0-TEST-G10-06` |

### G10-T1: challenge all process-boundary assumptions

Write system, State and checkpoint artifacts from the admitted toy. Reload the system plus State in a new process with network disabled and cache unavailable. Verify model digest, code identity, coordinates, box, masses, constraints, alchemical parameters and full real forces. An importable callback and a local cache hit are not sufficient evidence of a portable bundle.

Use a same-profile checkpoint continuation for internal state continuity. Use a portable State continuation as a separate test with its different random-number guarantee. Do not promise bitwise trajectories across different hardware or library builds.

**Finish this part with:** the relevant test results above and a worker log that states `G10-T1` as its scope. Completing this part alone does not complete G10.

### G10-T2: check the exchange decision independently

Start with two thermodynamic states and the actual worker mechanism. For configurations x and y assigned to states i and j, the proposed swap exponent uses `v_i(y)+v_j(x)-v_i(x)-v_j(y)`. Compare the acceptance calculation to independent evaluation; include outside contributions when state-dependent.

After every parameter change or state load, force a fresh appropriate energy evaluation. Record both walker identity and thermodynamic state identity. An exchange acceptance rate can appear reasonable even when stale energies are used, so acceptance rates are not the independent reference check.

**Finish this part with:** the relevant test results above and a worker log that states `G10-T2` as its scope. Completing this part alone does not complete G10.

### G10-T3: test interrupted execution and hardware placement

Test interruption/resume, unique sample IDs, append policy, state history and analysis continuity. Preserve the admitted CUDA process-start method. Inspect the model's tensor device after deserialization as well as the OpenMM context's device; one does not prove the other.

Begin on one GPU when available. Multiple GPUs are separately admitted and may require a small explicit worker/model initialization change. A local device index of zero can refer to different physical devices in different restricted workers; record both identities.

**Finish this part with:** the relevant test results above and a worker log that states `G10-T3` as its scope. Completing this part alone does not complete G10.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G10-01 | `tests/workflow/test_fresh_process.py::test_offline_cache_independent_reload` | The trusted bundle reconstructs with networking disabled and original model cache absent; exact asset identity remains unchanged. | P0-REQ-029, P0-REQ-015 |
| P0-TEST-G10-02 | `tests/workflow/test_restart.py::test_checkpoint_and_state_semantics` | Fixed-coordinate energy, forces, constraints, box and parameters agree; checkpoint and State guarantees are distinguished. | P0-REQ-015 |
| P0-TEST-G10-03 | `tests/workflow/test_replica_exchange.py::test_acceptance_uses_actual_reduced_energies` | For a proposed swap, compare the actual exponent with independently evaluated cross-state reduced energies and state labels. | P0-REQ-018, P0-REQ-015 |
| P0-TEST-G10-04 | `tests/workflow/test_replica_exchange.py::test_parameter_update_and_state_history` | After each state change and restart, raw parameters/energies and state/replica histories are current, not stale or inferred from directories. | P0-REQ-015, P0-REQ-018 |
| P0-TEST-G10-05 | `tests/workflow/test_fresh_process.py::test_model_and_openmm_worker_device` | Admitted GPU worker uses the intended OpenMM device and model-tensor device; unavailable multigpu evidence stays unqualified. | P0-REQ-015, P0-REQ-032 |
| P0-TEST-G10-06 | `tests/workflow/test_restart.py::test_interruption_resume_without_duplicate_records` | Interrupt/resume preserves sample identity and avoids duplicated output or silently discarded records. | P0-REQ-015, P0-REQ-019 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_fresh_process.py tests/workflow/test_restart.py tests/workflow/test_replica_exchange.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** An unexplained reload, state-label, energy-freshness, or device mismatch blocks larger replicas and protein jobs. Isolate serialization or scheduling rather than increasing worker count.

## Keep future changes possible

State and raw-record handling are independent of embedding. Any future model with hidden iterative state must pass the same evaluation-order and restart contracts.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_05/`\
**Task stem:** `Gate_10`\
**Worker:** `Gate_10_vN_worker.md`\
**Matching audit:** `Gate_10_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
