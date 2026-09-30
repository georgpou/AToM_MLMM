# G10: Check restart, process boundaries, and replica exchange

**Part of:** [M05](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A result is not reproducible if a fresh process loads a different model, loses a parameter, or swaps states using stale energies. Test these risks on the small solvated system.

## Expected outcome

Fresh-process, restart, and small replica-exchange evidence, with stable sample identities and verified device assignment.

**Not part of this gate:** Single-GPU success does not qualify multiple GPUs. A portable State is not a promise of identical random-number continuation.

## Before starting

Required earlier gates: [G09](../gates/G09-solvent-preparation-and-export.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G09 complete solvated worker handover and raw-record schema.

**Outputs used by later gates:** Offline reconstruction, same-profile checkpoint continuation, portable-State checks, two-state exchange evidence and device/restart audit.

**Planned source/test paths:** `persistence.py`, `observables.py`, `tests/workflow/test_fresh_process.py`, `tests/workflow/test_restart.py`, `tests/workflow/test_replica_exchange.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G10-T1` | Challenge all process-boundary assumptions | `P0-TEST-G10-01`, `P0-TEST-G10-02` |
| `G10-T2` | Check the exchange decision independently | `P0-TEST-G10-03`, `P0-TEST-G10-04` |
| `G10-T3` | Test interrupted execution and hardware placement | `P0-TEST-G10-05`, `P0-TEST-G10-06` |

### G10-T1: challenge all process-boundary assumptions

**Read:** [S07: Loading, restart, and workers](../specs/S07-artifacts-and-qualification.md#loading-restart-and-workers); [S07: Planned artifact bundle](../specs/S07-artifacts-and-qualification.md#planned-artifact-bundle).

Write system, State and checkpoint artifacts from the admitted toy. Reload the system plus State in a new process with network disabled and cache unavailable. Verify model digest, code identity, coordinates, box, masses, constraints, alchemical parameters and full real forces. An importable callback and a local cache hit are not sufficient evidence of a portable bundle.

Use a same-profile checkpoint continuation for internal state continuity. Use a portable State continuation as a separate test with its different random-number guarantee. Do not promise bitwise trajectories across different hardware or library builds.

### G10-T2: check the exchange decision independently

**Read:** [S07: Required observable names](../specs/S07-artifacts-and-qualification.md#required-observable-names); [S05: Raw physical energies and alchemical energy](../specs/S05-protocol-and-thermodynamic-contracts.md#raw-physical-energies-and-alchemical-energy).

Start with two thermodynamic states and the actual worker mechanism. For configurations x and y assigned to states i and j, the proposed swap exponent uses `v_i(y)+v_j(x)-v_i(x)-v_j(y)`. Compare the acceptance calculation to independent evaluation; include outside contributions when state-dependent.

After every parameter change or state load, force a fresh appropriate energy evaluation. Record both walker identity and thermodynamic state identity. An exchange acceptance rate can appear reasonable even when stale energies are used, so acceptance rates are not the independent reference check.

### G10-T3: test interrupted execution and hardware placement

**Read:** [S07: Loading, restart, and workers](../specs/S07-artifacts-and-qualification.md#loading-restart-and-workers); [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility).

Test interruption/resume, unique sample IDs, append policy, state history and analysis continuity. Preserve the admitted CUDA process-start method. Inspect the model's tensor device after deserialization as well as the OpenMM context's device; one does not prove the other.

Begin on one GPU when available. Multiple GPUs are separately admitted and may require a small explicit worker/model initialization change. A local device index of zero can refer to different physical devices in different restricted workers; record both identities.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G10-01 | `tests/workflow/test_fresh_process.py::test_offline_cache_independent_reload` | The trusted bundle reconstructs with networking disabled and original model cache absent; exact asset identity remains unchanged. | P0-REQ-029, P0-REQ-015 |
| P0-TEST-G10-02 | `tests/workflow/test_restart.py::test_checkpoint_and_state_semantics` | Fixed-coordinate energy, forces, constraints, box and parameters agree; checkpoint and State guarantees are distinguished. | P0-REQ-015 |
| P0-TEST-G10-03 | `tests/workflow/test_replica_exchange.py::test_acceptance_uses_actual_reduced_energies` | For a proposed swap, compare the actual exponent with independently evaluated cross-state reduced energies and state labels. | P0-REQ-018, P0-REQ-015 |
| P0-TEST-G10-04 | `tests/workflow/test_replica_exchange.py::test_parameter_update_and_state_history` | After each state change and restart, raw parameters/energies and state/replica histories are current, not stale or inferred from directories. | P0-REQ-015, P0-REQ-018 |
| P0-TEST-G10-05 | `tests/workflow/test_fresh_process.py::test_model_and_openmm_worker_device` | Admitted GPU worker uses the intended OpenMM device and model-tensor device; unavailable multigpu evidence stays unqualified. | P0-REQ-015, P0-REQ-032 |
| P0-TEST-G10-06 | `tests/workflow/test_restart.py::test_interruption_resume_without_duplicate_records` | Interrupt/resume preserves sample identity and avoids duplicated output or silently discarded records. | P0-REQ-015, P0-REQ-019 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_fresh_process.py tests/workflow/test_restart.py tests/workflow/test_replica_exchange.py -v
```

**Stop and diagnose:** An unexplained reload, state-label, energy-freshness, or device mismatch blocks larger replicas and protein jobs. Isolate serialization or scheduling rather than increasing worker count.

## Keep future changes possible

State and raw-record handling are independent of embedding. Any future model with hidden iterative state must pass the same evaluation-order and restart contracts.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_05/`\
**Worker:** `Gate_10_vN_worker.md`; **audit:** `Gate_10_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M05 combined review

**Review scope:** G09, G10. **Earlier milestone reviews:** M03, M04. These are combined-review conditions, not additional implementation prerequisites.

Inspect the actual worker export and reload at fixed coordinates before dynamics: atom map, constraints, box, active forces, parameters, energy and full real forces must agree. Review both mapped geometries, not only the statistically favorable one.

Recreate the bundle in a fresh offline process with the original cache unavailable. Distinguish checkpoint continuation from portable-State guarantees. Review two-state exchange energies independently and verify thermodynamic-state versus walker histories after restart.

Check worker device placement where GPU evidence is claimed. Multiple GPUs are separately qualified. A short multiwindow pilot demonstrates execution and record integrity, not converged affinity.

G09 and G10 accepted for the declared solvated runtime profile with explicit raw records, no hidden asset dependency, and valid exchange/restart behavior.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_05_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
