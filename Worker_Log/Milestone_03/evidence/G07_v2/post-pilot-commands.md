# Commands after the pilot and session-quota resume

All commands ran from `/workspace/AToM_MLMM`. The actual quantum launch remains in `pilot-command.json`, and its child/supervisor argv is in the original receipt/launch files. The commands below never launch another quantum worker.

```bash
source /workspace/atom-mlmm-g07/activate.sh
python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v2/post-pilot-full-cpu-suite -- python -m pytest -q
```

Exit 0, 409 passed in 266.34 s, before the subsequent independent safety findings.

```bash
source /workspace/atom-mlmm-g07/activate.sh
python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v2/post-pilot-full-cpu-suite-final -- python -m pytest -q
```

Exit 1, 413 passed / one inherited genuine-retry regression failed; failure output is preserved.

```bash
source /workspace/atom-mlmm-g07/activate.sh
python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v2/post-pilot-retry-repaired-full-cpu-suite -- python -m pytest -q
```

Exit 0, 414 passed in 267.70 s, before the subsequent interrupted-publication durability finding.

```bash
source /workspace/atom-mlmm-g07/activate.sh
python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v2/post-pilot-durable-revalidation-full-cpu-suite -- python -m pytest -q
```

Exit 0, **416 passed in 272.69 s**, exact final source `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`. Focused commands also used `python -m pytest tests/unit/test_joint_quantum_execution.py -q` or its maintained `-k` selections (`correction_cannot`, `removing_markers`, `retry_keeps or removing_markers`, `fsyncs_renamed`); their RED/GREEN outputs remain separately named in this directory. The independent audit records its own exact probe and 35-case commands.

After exact-source independent acceptance:

```bash
source /workspace/atom-mlmm-g07/activate-reference.sh
export PYTHONPATH=/workspace/AToM_MLMM/src
python tools/resume_joint_quantum.py --plan-root fixtures/chemical_reference_v3 --approval Worker_Log/Milestone_03/evidence/G07_v2/authorization.json --matrix fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json --reference-python /workspace/atom-mlmm-g07/reference-env/bin/python --output Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1 --revalidate-pilot > Worker_Log/Milestone_03/evidence/G07_v2/actual-revalidation-coordinator.log 2>&1
```

Exit **1** means the 30-job queue remains incomplete: the existing pilot was recovered successfully, with no worker launch, and stopped at `pilot_assessment_pending`. The record, corrected receipt and resource hashes, original byte preservation, exact new debit and audit identity are in `actual-revalidation-result.json`. Do not repeat this command just to obtain exit 0.

```bash
source /workspace/atom-mlmm-g07/activate.sh
python Worker_Log/Milestone_03/evidence/G07_v2/compare_pilot_forces.py --output Worker_Log/Milestone_03/evidence/G07_v2/pilot-force-comparison.json
```

Exit 0. This is saved-array arithmetic; no model or QM is run. The result includes every input/script hash, real-coordinate force arrays, both cap parents and unchanged limits. The output is exclusive and must not be overwritten.

Assessment used the activated main interpreter with `PYTHONPATH=tools:src python` and the maintained `validate_authorization`, `pilot_evidence`, `execution_policy`, `measurements`, and read-only `validate_assessment` functions. `pilot-assessment.json` preserves all exact measured values, hashes, current resources and formulas: runtime is twice measured receipt wall time times the sum of remaining nuclear-charge composition ratios cubed; RSS scales measured peak by maximum exact orbital-basis ratio squared; scratch scales by maximum exact `Naux*Norb^2` ratio. An otherwise identical probe with `continue_authorized=True` was passed to `validate_assessment` without calling `run`; it correctly raised `pilot projections exceed the remaining resource/budget envelope`. `continuation-envelope-probe-input.json` and `continuation-envelope-rejection.json` preserve that exact check and unchanged ledger/original-receipt hashes. No batch CLI was launched.

The session's five-hour quota reset did not reset the quantum-worker ledger. Publication commands and remote verification are recorded separately in the final publication receipt.
