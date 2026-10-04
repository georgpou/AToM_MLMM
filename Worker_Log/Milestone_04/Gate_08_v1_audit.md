# G08 and combined M04 — v1 independent audit

**Reviewed worker/snapshot:** [v1 worker](Gate_08_v1_worker.md), branch `m04-engine-readiness`, exact submission `29847120ec99c472580ce23c7b1b317c690c3784`; scientific source `966a8d61347f65a69f8ba7e6750c4379d4e0503f`; base `e24e880abcb0353b8f9c2f2e509d6cbb46174f3b`.\
**Scope/profile:** G08-T1/T2/T3, all six stable assertions, [additive admission amendment](../../docs/project-0/specs/G08-record-admission-v1.md), and combined M04; nonperiodic analytic NVT, OpenMM Reference double, pinned CPU PyMBAR/UWHAM.\
**Reviewer and finished time:** Codex `/root/g08_audit_sol61_max`, explicitly dispatched **GPT-6.1-sol / MAX**; deployed backend version not exposed; 2026-10-04 15:00 UTC. The reviewer authored no implementation or submitted tests.\
**Verdict:** **G08 and combined M04: changes_required. Amendment: changes_required. G08-R1 remains open.** Numerical T1/T2/T3 evidence is confirmed within the stated profile, but final-result record admission does not enforce correction completeness.

## Evidence

Read AGENTS, handoff, worker, G08, S03/S05/S06, amendment, production implementation and tests. Inherited [M02 acceptance](../Milestone_02/Gate_03_v2_audit.md) on `6015a652c4a9a9c968ab7933c07ac7bbb4573e12` is carried forward. Unchanged accepted G06/G07 single-point numerics were not reopened. G07/M03 physical qualification remains blocked.

[Independent evidence](evidence/G08_v1_independent_sol61_max/README.md) includes authored probes, original outputs, command arguments/exit codes/resources, invalid admitted JSON and raw numerical artifacts. [Snapshot verification](evidence/G08_v1_independent_sol61_max/snapshot-check.json) confirms branch/HEAD/tree, required ancestry, all **82** scientific manifest entries against both source and submission, nine original MD artifacts, and **7,567** tracked files against Git. [Closing verification](evidence/G08_v1_independent_sol61_max/closing-preservation.json) confirms every tracked byte remains unchanged. Source-to-submission differences are reports/evidence/STATUS only.

Every scientific shell activated `/workspace/atom-mlmm-g08-r2/activate.sh`, set `OPENBLAS_NUM_THREADS=2`, and used `PYTHONPATH=/workspace/AToM_MLMM/src` where required. Runs were serialized on the two-CPU, 8-GiB, no-configured-swap profile. OOM/OOM-kill counts remained zero. No QM, installation, GPU or long production work was performed.

| Fresh independent command | Exit and actual outcome |
|---|---|
| `python snapshot_probe.py` from the independent evidence directory | 0; exact snapshot/manifests/ancestry verified |
| `python -m pytest -q --basetemp /tmp/g08-independent-sol61-max-full-v2` | 0; **433 passed in 323.21 s** |
| `python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v --basetemp <independent-evidence>/focused-pytest-temp` | 0; **17 passed in 34.15 s** |
| `python -m pytest tests/integration/test_model_adapter.py::test_local_asset_fresh_process_reload -v --basetemp /tmp/g08-independent-sol61-max-reload-v1` | 0; **2 passed in 13.25 s** |
| `python independent_probes.py` from the independent evidence directory | 1; **nine positive groups, 33 correct rejections, two admitted invalid final records**, no numerical/probe failures |
| `python uwham_objective_probe.py` from the independent evidence directory | 0; independent objective and gradient/Hessian step sweep pass |
| `python close_evidence.py` from the independent evidence directory | 0; closed temporary trees archived with every member verified; all tracked files unchanged |
| `python tools/check_docs.py --self-test`; `git diff --check` | 0 each; zero local documentation errors, eight checker self-tests pass, no whitespace errors |

The first full run used an in-repository basetemp: **431 passed/two failed**, exit 1. Both inherited offline-reload tests deliberately deny the old checkout prefix, including that basetemp's artifact. The outside-repository two-node and full reruns above establish this as reviewer harness interference. Original failures are preserved. Missing `/usr/bin/time`, initial symlink enumeration and tar hard-link validation were also reviewer tooling issues, corrected without source changes.

| Stable assertion | Independent evidence and decision |
|---|---|
| P0-TEST-G08-01 | Independent quadrature and nine-state Gaussian samples confirm +1.5, reverse -1.5 and zero-restraint limit; maximum original-constant curve error **0.00909 kJ/mol**, within 3 SE and 0.1. An additional 317-K case passes. |
| P0-TEST-G08-02 | **498** state/frame comparisons against actual native contexts, independently written nonlinear expressions, both directions, nonzero offsets and active soft-core; maximum energy error **1.42e-14 kJ/mol**. State reordering/interleaving preserve analysis; unknown states, duplicates, lost identities/provenance and raw scope faults reject. |
| P0-TEST-G08-03 | New independent samples from both unequal midpoint ensembles, cross energies and quadrature give bridge **-0.332715 kJ/mol**; sampled **-0.332891 +/-0.003613**. Correct S05 sign restores endpoint **-0.5**, estimated **-0.506734 +/-0.022472**; omitted/reversed bridge fails. Preserved worker midpoint data also agree across estimators. |
| P0-TEST-G08-04 | **18** independent scaled radial integrals, harmonic/hard-wall limits and standard-state sign pass; maximum relative error **1.96e-15**. Periodic/coupled/unspecified finite-wall domains reject. |
| P0-TEST-G08-05 | Producer correctly withholds all six incomplete ledger variants, unresolved statuses and missing correction covariance. **Shared `BindingResult` constructor/JSON admission bypasses that protection: G08-R1.** |
| P0-TEST-G08-06 | Generic 2/3/6-state Gaussian inputs with unequal counts agree between PyMBAR/UWHAM to **4.62e-14 dimensionless**; weighted covariance and large state/observation gauges agree. Joint correction covariance matches an independent linear oracle. AR(1) histories retain 3,486/54,000 observations and increase SE from **0.01670 to 0.06546**; contribution flags and exchanging-history rejection work. |

Independent replay of all preserved MD coordinates verifies every raw endpoint/outside/total and full real force (maximum force error **1.42e-14 kJ/mol/nm**). Seeds 41/73/109 reproduce **1.508155 +/-0.071954**, **1.501808 +/-0.079007**, **1.434225 +/-0.075979 kJ/mol**. All satisfy both known-answer limits and adequate contributions. Last-half estimates **1.545579/1.494263/1.433586** are compatible using the documented conservative covariance bound. Mean **1.481396 +/-0.043706** and replicate spread **0.040975** are distinct quantities.

The pinned UWHAM path refines its own objective from zero, then its exact-Hessian Newton step and pinned core compute weights/Fisher covariance; no MBAR initialization is used. An independently coded log-sum-exp objective matches exactly; finite-difference gradient/Hessian errors are **2.02e-11/4.16e-12**. Acceptance remains limited to sampled states, admitted density range and connected measured support. A disconnected finite-range example rejects via upstream `LinAlgError('Singular matrix')` before the shared support diagnostic; no result is returned. This diagnostic limitation is nonblocking for the demonstrated connected numerical profile. Correlated exchanging histories, periodic/coupled volume approximations, molecular standard binding, GPU and physical accuracy remain unqualified. Correction evidence semantics still require actual scientific justification.

## Findings

| Finding and importance | Evidence/location | Required repair and closure check |
|---|---|---|
| **G08-R1 — blocking: incomplete final-result records are admitted.** A caller can supply an empty `unresolved_corrections` tuple and obtain a final result while a correction is `required_uncomputed`, or while the entire correction ledger is absent. This contradicts S05/G08-05 and the amendment. | [BindingResult._validate](../../src/atm_mlmm/schema.py), lines 699–716, checks the caller's unresolved tuple but has no declared-obligation context or ledger-completeness check. Independent [reproducer](evidence/G08_v1_independent_sol61_max/independent_probes.py), lines 321–333; [uncomputed payload](evidence/G08_v1_independent_sol61_max/admitted-final-uncomputed.json), [empty-ledger payload](evidence/G08_v1_independent_sol61_max/admitted-final-empty-ledger.json). Both constructor and `from_json` admit a final **1.5 +/-0.2**. | Bind declared obligations/spec and identity to result admission; require a complete matching resolved ledger before any final pair. Reject contradictory/missing obligation metadata and ledger/status mismatches while preserving legitimate partial records. Add constructor and serialized negatives plus complete deterministic/uncertain-covariance producer round-trip positives; independently rerun these, affected G08 checks and available CPU suite on the repair snapshot. **Open on this submission.** |

## Decision and handoff

The scientific expressions, signs, finite-wall formula, independent estimator agreement and bounded analytic sampling are supported by this review. The additive record proposal requires G08-R1 repair before acceptance; passing producer tests do not validate serialized result admission. Therefore **complete G08-T1/T2/T3, G08 and combined M04 are not accepted on this snapshot**.

Repair and submit a new exact worker/source/evidence snapshot for independent closure. Preserve this v1 decision and evidence. The parent integrator owns STATUS/publication; this reviewer changed neither, and changed no submitted source, tests, worker evidence, specification, branch or commit. G07/M03 physical blockers and prior acceptance boundaries remain unchanged.
