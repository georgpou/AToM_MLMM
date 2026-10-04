# G09/G10 cloud technical subsets — v1 audit

**Reviewed worker/snapshot:** [v1 worker](Gate_09_v1_worker.md), branch `m04-engine-readiness`, submission `9e7a84c91e8c252c33221b8e2331e595d54315ca`; tested scientific source `34cc6ba0d3e618450128b4a679ffc64046c48733`, accepted G08/report base `8692138bac7d7324ac4d2ef13bfb58075b874202`.\
**Scope/profile:** Partial G09-T2/T3 vacuum preparation/export/pilot and G10-T1/T3 worker/restart/journal subsets; Reference double NVT, pinned MACE CPU float64, two CPUs/8 GiB/no configured swap.\
**Reviewer and finished time:** Independent dispatched **GPT-6.1-sol / MAX**, actual model/effort requested by the user; `/root/g08_audit_sol61_max`, 2026-10-04 17:00 UTC. No further delegation.\
**Verdict:** **changes_required** — G09-R1. Full G09/G10 and combined M05 remain unaccepted.

## Evidence

Reviewed AGENTS, G09/G10, relevant S02/S06/S07, the proposed [cloud amendment](../../docs/project-0/specs/G09-cloud-preflight-v1.md), configuration examples, production source and actual pinned AToM constructor. The scientific checks ran serially from fresh detached checkout `/tmp/atm-mlmm-g09-independent-readonly` at the exact submission. Every scientific shell activated `/workspace/atom-mlmm-g08-r2/activate.sh`, `OPENBLAS_NUM_THREADS=2`, `PYTHONPATH=/tmp/atm-mlmm-g09-independent-readonly/src:/tmp/atm-mlmm-g09-independent-readonly`. Root remained idle on science and preserved the submission.

Independent evidence is under [G09_v1_independent_sol61_max](evidence/G09_v1_independent_sol61_max/README.md). The command runner preserves exact argv, timestamps, exit codes, stdout/stderr and resource observations.

| Command/check | Exit and actual outcome |
|---|---|
| `python snapshot_probe.py` and `python snapshot_probe.py closing` | 0; all **8,008 tracked blobs** match the exact submission in both checkouts; all **110 scientific manifest files** match source and submission; all prior M04 artifacts, including frozen G08 reports/evidence, unchanged. |
| `python -m pytest -q --basetemp=/tmp/g09-independent-focused tests/unit/test_host_role.py tests/workflow/test_cloud_host_guest.py tests/workflow/test_engine_configuration.py tests/workflow/test_engine_fresh_process.py tests/workflow/test_engine_restart.py tests/workflow/test_preparation_phases.py tests/workflow/test_worker_handover.py` | 0; **22 passed in 78.65 s**, no skips. Includes seed reproducibility, real constructor parity, all three fixture sizes, checkpoint/State distinction, uninterrupted/interrupted equality and actual relocated offline continuation. |
| `python admission_probe.py` | 0, 0.741 s; **49 deliberate rejections**, valid 48/32/41 declarations, actual unequal-group worker and seed check. Challenges chemistry/settings, immutable indices, missing/reordered/duplicate journal records, artifact corruption/pending/unknown entries, trust, ordered atom/state/parameter/identity mismatches and wrong-state checkpoint. Rejections preserve inspected artifacts. |
| `python numerical_probe.py` | 0, 15.998 s; independently checks all 60 pilot frames and six capped-control frames for finite full arrays and both manual real maps. Direct physical evaluations at 12 selected frames reproduce both raw energies and **36 actual worker cross-state evaluations**. Largest full-real-force error **2.274e-13 kJ/mol/nm**; reconstructed energy error **4.657e-10 kJ/mol**, within existing 1e-7/1e-8 limits. Useful control raw artifacts retained. |
| `python integration_failure_probe.py` | **1**, 0.709 s; required retention assertion fails after an actual worker integrator advances one step and raises the injected domain exception. No production failure archive exists. Auditor separately preserves the advanced State/checkpoint, explicitly labeled as auditor captures. |
| `python tools/check_docs.py --self-test` | 0; zero local documentation errors, eight self-tests pass. |
| Frozen worker full CPU evidence, `python -m pytest -q --basetemp=/tmp/g09-final-root-full` | Worker-recorded exit 0; **459 passed in 400.62 s**, no skips. Log and source manifest independently verified; full suite not repeated, following the economical review dispatch. |

The initial independent numerical harness used an incorrect restraint field name, exiting 1 before assertions. Its original script/logs remain as `numerical-probe-harness-error.*` / `numerical_probe_initial.py`; only the independent harness was corrected. This is not a source finding. No OOM/OOM-kill increase occurred.

The exact PDB/System/State export uses actual `OMMWorkerATMSync` construction, including preliminary PDB evaluation and high-precision State loading. The sealed loader avoids duplicate assembly and disables stock zero-LJ repair. The evaluator adopts that same Context. Independent physical maps and the outside harmonic oracle reproduce every real force in the selected crown/ABFE/RBFE frames, including static cap parents and MM coordinates. Independently measured crown minimum Bondi ratio **0.790349815** and bulk clearance **2.539771094 nm** agree with the frozen pilot. No estimator or BindingResult is produced.

The fresh-process test uses relocated bundled source/model assets with Python socket and file-open denial for original checkout/run/caches. This demonstrates the declared CPU/software profile; it is not an OS isolation or cross-platform checkpoint claim. Carry forward unchanged accepted G06/G07 numerical and G08 evidence without reopening physical qualification.

## Findings

| Finding and importance | Evidence/location | Required repair and closure check |
|---|---|---|
| **G09-R1 — blocking: integration-origin failures lose the failed configuration.** Force/domain exceptions can originate during integration before the post-step validation handler. | `src/atm_mlmm/workflow.py:256` calls `integrator.step` outside the `try` beginning at line 257. The [independent reproducer](evidence/G09_v1_independent_sol61_max/integration_failure_probe.py) advances the actual LangevinMiddle integrator once, then injects `NumericalDomainError` inside that call. The original error propagates, but [report](evidence/G09_v1_independent_sol61_max/integration-failure-report.json) records zero failure archives and zero committed samples. The preserved independent State/checkpoint prove the advanced coordinates existed. The submitted retention regression only injects a post-step `_domain` failure. This violates the required failed-sample preservation boundary; the successful pilot does not close it. | Extend the cached-State retention handler to cover integration and subsequent State acquisition. Preserve attempted sample/walker/state/index and the original exception without requesting failed energy/forces again; do not append a successful sample. Add a regression that fails inside actual integration, compares the archived advanced State/checkpoint, and forbids energy/force reentry. Rerun this probe, affected tests and full CPU suite on a new frozen v2 submission. **Open on v1.** |

## Decision and handoff

The amendment's neutral complete static-host role and explicitly bounded vacuum technical definition are **accepted_for_scope** as a design amendment. The v1 implementation is **changes_required** solely for G09-R1. Preparation/seed semantics, real sealed constructor, complete raw/full-real-force records, independent map/state reevaluation, immutable journal rejection, checkpoint/portable-State distinction and relocated offline continuation have supporting independent evidence on this snapshot; they do not remove the retention requirement.

The admitted target remains the shared 48-atom crown/methanol, 32-atom capped ABFE and 41-atom capped unequal-ligand RBFE CPU vacuum path. This does not accept G09-T1 solvent, G10-T2 exchange, GPU/hardware placement, automatic hard-crash recovery, concurrent controllers, equilibrium, standard binding corrections, molecular accuracy, protein/HPC preflight or full G09/G10/M05. G07/M03 physical qualification remains blocked; accepted combined M04/G08 and the quantum ledger remain unchanged. No QM/GPU/installation/long production work ran.

Preserve this v1 audit/evidence, repair G09-R1 in v2 and independently close it on the new exact submission. Parent owns the corresponding scoped STATUS update; the auditor made no source/test/spec/worker/STATUS/ref/commit changes.
