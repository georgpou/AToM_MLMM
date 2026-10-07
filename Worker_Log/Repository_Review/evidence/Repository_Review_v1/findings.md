# Confirmed findings and limits

Frozen source: `4ad8ee835809325ceec8a017222415043347967d`. Profile: pinned CPU environment, OpenMM Reference double, LangevinMiddle 300 K, 0.0005 ps; fresh seven-real-atom analytic RBFE controls using actual exported AToM workers. The same model-independent continuation flow serves ABFE; fresh ABFE numerical controls are in the separate selected tests. The reproducer never changes reviewed source or tests.

Run from the repository root, with the environment activation and thread settings in [probe-plan.md](probe-plan.md):

```bash
python -c "import runpy; runpy.run_path('Worker_Log/Repository_Review/evidence/Repository_Review_v1/reproduce_restart.py', run_name='__main__')"
```

The attempt directory is exclusive: a rerun requires a new, explicitly named attempt in a future task. Do not delete or silently overwrite the preserved attempt. The initial direct-script command failed to locate repository test helpers before preparation; [its log](restart-diagnostics.log) remains. Only invocation changed for the successful command, not script/source bytes. [Successful command receipt](restart-diagnostics-invocation.json), [raw output](restart-diagnostics-invocation.log), [results](restart-results.json) and [script](reproduce_restart.py) are the complete reproduction.

## RR-01 — older continuation accepts an inconsistent actual clock

**Severity:** high / P1, because saved history and actual continuation disagree despite acceptance. This is an admission/provenance defect, not a claim that the force expression is wrong or an intact checkpoint corrupts itself.

**Affected paths and locations:** public `workflow.resume_run` → `_execute`, [workflow.py](../../../../src/atm_mlmm/workflow.py), lines 328–410, especially checkpoint restoration at 357 and stepping at 364; public `exchange.resume_exchange` → `_execute_exchange`, [exchange.py](../../../../src/atm_mlmm/exchange.py), lines 220–255. [WorkerRun.restore_checkpoint](../../../../src/atm_mlmm/adapters/atom.py), lines 389–400, validates parameters but not agreement with the saved sample/State. The old inert [pair journal reader](../../../../src/atm_mlmm/exchange_journal.py), lines 75–126, does not validate clocks.

**Minimal reproduction:** create a fresh analytic worker bundle and stop after one fixed-window sample, or one pair round. Load its committed checkpoint in the identical profile; change only Context time from 0.0005 to 1.0005 ps. Verify unchanged step count, positions, velocities and parameters. Save the checkpoint and update only its declared digest in the chunk/boundary manifest. Keep the saved row and portable State unchanged. Resume through the public API.

**Independent expectation:** actual restored time must equal the saved boundary time. If admitted, one further 0.0005 ps integration step should give elapsed time 0.0005 ps from step 1 to step 2. A 1 ps disagreement is not a floating-point envelope question.

**Actual:** both paths return `complete`; the next sample time is 1.001 ps, so elapsed time is 1.0005 ps. The fixed-window journal and pair inert journal accept the coherently hashed inconsistency. Original and altered checkpoints and original manifests are preserved under `restart-attempt-001/`.

**Consequence:** the software can publish a history that does not correspond to the restored clock. The pair energy refresh does not detect it because a time-only change leaves fixed-coordinate potential energies unchanged. A hash proves bytes are unchanged after sealing; it does not prove different saved representations agree.

**Smallest future repair/check:** use the existing verified-restoration design for both older controllers. Compare exact saved/restored clocks and integer steps, parameters, coordinates, velocities and box; refresh and compare saved raw energies and full forces where required before stepping. Keep the elapsed-time envelope separate. Regress the two time-only cases with zero integration calls on rejection and retain a valid same-profile continuation case. No new clock campaign or tolerance changes are needed.

**Scope distinction:** the v8 multistate `_fresh_multistate_check` and final clock validator already perform the stronger admission. Their R2 remains closed; this finding is not a reversal of that historical decision.

## RR-02 — fixed-window restored geometry reaches integration before admission

**Severity:** high / P1. The hard molecular-domain guard is too late on this continuation path.

**Location:** [workflow.py](../../../../src/atm_mlmm/workflow.py), `_execute`, lines 353–368. `_guard()` at line 363 checks System/maps/parameters; it does not check coordinate clearance. `_domain()` is called only after `integrator.step()` at 364 and `_snapshot()`.

**Minimal reproduction:** fresh fixed-window prefix; restore its checkpoint, put real atom `b1` exactly at the stationary `protein` coordinate, save and rehash the checkpoint. This is zero intermolecular separation. Call the declared geometry guard directly to establish rejection: `map0 intermolecular Bondi ratio 0 < 0.65 at ['b1', 'protein']`. Replace only the diagnostic's native integrator step method with a sentinel that records entry and raises immediately. Resume through the public API.

**Expected versus actual:** geometry admission must reject before integration. Instead the sentinel records one call with `count=1` and raises `StepSentinel: integration reached before restored geometry admission`. Zero invalid-geometry steps execute. The normal failure archive is retained, including saved states and both map diagnostics.

**Consequence:** without the diagnostic stop, the restored invalid coordinates would enter a force/integration operation before the intended domain rejection. This violates the ordering needed to preserve a failing restored state inertly. It is not evidence of an upstream OpenMM/AToM defect.

**Smallest future repair/check:** snapshot and validate actual restored geometry, both complete maps, cap parents and finite coordinate/velocity/box state before the first step or energy evaluation that depends on admission. Reuse the existing common guard and stronger multistate ordering. Test the zero-separation checkpoint with zero step calls, alongside an admitted checkpoint. Preserve the original invalid input and failure records.

## RR-03 — fixed-window source inventory can be incomplete

**Severity:** medium / P2. Reproducibility admission is incomplete; no numerical Hamiltonian error was demonstrated.

**Location:** [workflow.py](../../../../src/atm_mlmm/workflow.py), `resume_run`, lines 505–510. The loop validates entries present in `manifest['files']`, but does not require equality with the complete current Python tree. The general [worker loader](../../../../src/atm_mlmm/adapters/atom.py), lines 307–313, requires six main artifacts, not every source module.

**Minimal proof:** fresh fixed-window prefix; remove only `runtime/source/atm_mlmm/chemical_reference.py` from the worker manifest's declared files, rehash the manifest, update its metadata binding and metadata digest. The current source tree still has all 38 modules. Use an `_execute` sentinel to observe admission order without loading or running a malformed bundle.

**Expected versus actual:** 37 declared source modules must reject before execution. `resume_run` reaches `_execute` and returns the sentinel. This is a precise control-flow proof of source admission, not a claim of completed numerical continuation from that bundle.

**Consequence:** a saved run can be labeled as matching exact bundled source while omitting part of the required source identity. Pair and multistate controllers already require complete inventory equality; the fixed-window check is weaker.

**Smallest future repair/check:** share the complete inventory comparison and artifact/path/hash validation used by the exchange controller; perform it before executable loading. Regress missing, added and changed source entries and the byte-identical positive case. Do not relax relocation support.

## Documentation drift and unresolved questions

**D01:** [STATUS](../../../../docs/project-0/STATUS.md), lines 435–445 and 472, still treats v5 multistate repairs as open. Lines 3–24 and [final v8 audit](../../../Milestone_05/Gate_10_v8_audit.md) supersede that claim. Update the live summary in a future documentation task, retaining original RED/GREEN records. No new scientific defect is inferred from the stale text.

The generic “proposed” headings on specifications/amendments are not themselves acceptance decisions; use their linked scoped audits. Hardware parity, complete protein manifests/cap collections, correlation qualification and physical references are missing work or availability limits, not newly proved runtime defects. This pass did not test every failure mode, filesystem type, chemistry or long trajectory.
