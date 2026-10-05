# G09-R1 cloud retention repair — v2 audit

**Reviewed worker/snapshot:** [v2 worker](Gate_09_v2_worker.md), branch `m04-engine-readiness`, exact submission `9fe93357f0852d7c018ab41923cc0d58cb0615e1`; scientific source `3246f0cbd6f66702e4b196bace593efba776a25e`, report-only v1 audit base `3fc194dc84bc3711a21ec88812fa7442e4d84d0e`.\
**Scope/profile:** G09-R1 closure; inherited partial G09-T2/T3 vacuum analogues and G10-T1/T3 worker/checkpoint/State/offline/journal subsets. Reference double NVT, pinned MACE CPU float64, two CPUs/8 GiB/no configured swap.\
**Reviewer and finished time:** Actual independent dispatched **GPT-6.1-sol / MAX**, `/root/g08_audit_sol61_max`, as explicitly requested by the user; 2026-10-04 17:33 UTC. No further delegation.\
**Verdict:** **accepted_for_scope** — G09-R1 closed. Full G09/G10/M05 remain unaccepted.

## Evidence

Reviewed the complete source diff, repair plan, new regressions, corrected restart oracle, worker and frozen evidence against the [v1 audit](Gate_09_v1_audit.md) and unchanged cloud amendment. The sole production change widens the failure boundary and adds attempted-record provenance; normal full-force refresh remains. No Hamiltonian, map, model, environment, tolerance or scientific definition changed.

Independent commands ran serially in fresh detached exact checkout `/tmp/atm-mlmm-g09-v2-independent-readonly`, after sourcing `/workspace/atom-mlmm-g08-r2/activate.sh`, with `OPENBLAS_NUM_THREADS=2` and `PYTHONPATH=/tmp/atm-mlmm-g09-v2-independent-readonly/src:/tmp/atm-mlmm-g09-v2-independent-readonly`. Root remained idle on science. Exact commands, exit codes, resources and raw captures are in [independent evidence](evidence/G09_v2_independent_sol61_max/README.md).

| Check/command | Actual outcome |
|---|---|
| `python snapshot_probe.py`; `python snapshot_probe.py closing` | Both 0; all **8,150 tracked blobs** exact in both checkouts, **111 scientific files** match the tested source, **507 prior artifacts** unchanged. V1 audit/evidence and all M04 artifacts remain frozen. |
| `python -m pytest -q --basetemp=/tmp/g09-v2-independent-focused tests/workflow/test_engine_failure_retention.py tests/workflow/test_engine_restart.py tests/workflow/test_worker_handover.py tests/workflow/test_engine_fresh_process.py` | 0; **9 passed in 44.96 s**, no skips. Covers both advanced faults, strict identical-start continuity, actual worker handover, checkpoint versus portable State, and fresh relocated offline continuation. |
| `python integration_failure_probe.py` | 0, **0.698 s**; byte-identical copy of the original v1 reproducer now obtains the production archive. V1 failed output remains unchanged. |
| `python prefix_failure_probe.py` | 0, **1.573 s**; **six independent actual-worker cases**: guard/integration/final-State failure for ABFE and RBFE after one committed sample. Exact archived State/checkpoint, original exception object, all attempted IDs/sequence/index and actual step/time verified; no energy/force reentry, no failed sample append, prefix bytes unchanged. Analytic toy geometry admission is explicitly stubbed for this boundary oracle. |
| `python artifact_probe.py` | 0, **0.146 s**; new nine-frame pilot capture matches the complete local attempt and journal; all full 48-atom arrays/raw values finite. Physical/alchemical identities match the frozen v1 pilot. Independently verified the six earlier pre-sampling artifact hashes differ as diagnosed. |
| `python tools/check_docs.py --self-test`; `git diff --check` | 0; zero documentation errors/eight self-tests, clean tracked diff. |
| Frozen worker full suite: `python -m pytest -q --basetemp=/tmp/g09-v2-root-full` | Worker-recorded 0; **461 passed in 399.38 s**, no skips. Exact source/log independently verified; not represented as an auditor full-suite rerun. |

The restart-oracle correction is justified: the preserved snapshot, State and bundle hashes already differ between independently prepared starts. The new uninterrupted reference uses the identical exported System/State/seed and keeps exact raw/position/velocity/full-force equality. No tolerance was relaxed.

Carry forward the v1 independent **22-test pass, 49 admission rejections and 12-frame/36-cross-state physical/full-real-force oracle** on their original exact source `34cc6ba0d3e618450128b4a679ffc64046c48733`. Their implementation paths and scientific definitions are unchanged; they were not rerun or relabeled as v2 results. The v2 CLI nine-frame/18-step check is separate from the frozen v1 60-frame/300-step pilot. No OOM/OOM-kill increase occurred in these independent commands.

## Findings

| Finding | Evidence/location | Closure |
|---|---|---|
| **G09-R1 — closed.** Integration-origin failures previously bypassed preservation. | `src/atm_mlmm/workflow.py:255` now encloses guard, integration, domain/evaluation and final State acquisition. The handler captures cached coordinates/velocities/parameters and checkpoint, with complete attempted-record provenance. [Original reproducer](evidence/G09_v2_independent_sol61_max/integration-failure-report.json) and [six prefix challenges](evidence/G09_v2_independent_sol61_max/prefix-failure-report.json) pass; production failure artifacts are retained. | Original error propagates, failed energy/forces are not reevaluated, committed prefix remains unchanged, and no rejected step becomes a successful record. Nine affected checks and the worker full suite pass on the frozen v2 source. No remaining blocking finding within the assigned scope. |

## Decision and handoff

Accept the cloud amendment and shared **48-atom crown/methanol, 32-atom capped ABFE and 41-atom capped unequal-ligand RBFE CPU vacuum path for the declared technical scope**: preparation/seed semantics, sealed actual worker export, raw/full-real-force records and state reevaluation, immutable single-controller journal, failure preservation, checkpoint/portable-State distinction and relocated offline continuation. V2 closes the sole v1 blocker.

This does not accept G09-T1 solvent, G10-T2 exchange, GPU/multigpu, automatic hard-crash repair, concurrent controllers, equilibrium, standard binding corrections, affinity or molecular accuracy, protein/HPC preflight, or full G09/G10/combined M05. G07/M03 physical qualification remains blocked; accepted G08/combined M04 and quantum accounting remain unchanged. No new QM, GPU, installation or long production work occurred.

Freeze this audit/evidence, record the scoped acceptance in STATUS and stop at this reviewed cloud baseline, as requested. Parent owns integration/publication and the continuation handoff. The auditor made no production/test/spec/worker/STATUS/ref/commit changes.
