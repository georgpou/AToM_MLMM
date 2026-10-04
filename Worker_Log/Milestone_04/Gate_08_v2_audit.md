# G08-R1 closure and combined M04 — v2 independent audit

**Reviewed worker/snapshot:** [v2 worker](Gate_08_v2_worker.md), branch `m04-engine-readiness`; exact submission `c0280818ad18fa5e95a022eccc892e2310a41721`; tested source `8cf2494424d796fc3fc393e25b00e05b6281a85f`; base `89eb8b97a854b4b8f96d8e9cd80d711f9a9b717f`.\
**Scope/profile:** G08-R1 closure, G08-T1/T2/T3, all six stable assertions, [v1 admission amendment](../../docs/project-0/specs/G08-record-admission-v1.md) as refined by [v2](../../docs/project-0/specs/G08-record-admission-v2.md), and combined M04; nonperiodic analytic NVT, OpenMM Reference double and pinned CPU PyMBAR/UWHAM.\
**Reviewer and finished time:** Codex `/root/g08_audit_sol61_max`, explicitly dispatched **GPT-6.1-sol / MAX**; deployed backend version not exposed; 2026-10-04 15:27 UTC. The reviewer authored no implementation or submitted tests.\
**Verdict:** **G08-T1/T2/T3, complete G08, refined admission amendment and combined M04: accepted_for_scope. G08-R1: closed.**

## Evidence

Read the v2 worker/amendment and complete source/test diff. Only `BindingResult` validation/encoding, the producer's attached typed definition and four new regression nodes changed scientifically. [Independent snapshot verification](evidence/G08_v2_independent_sol61_max/snapshot-check.json) confirms exact branch/HEAD/tree, all **83** scientific manifest entries against source and submission, required ancestry and **7,649** tracked Git blobs. Source-to-submission changes are reports/evidence/STATUS only. Frozen v1 audit, numerical probes, seed frames, failures and worker evidence are unchanged; [closing verification](evidence/G08_v2_independent_sol61_max/closing-preservation.json) confirms all submitted tracked bytes remain unchanged.

The [v1 independent numerical review](Gate_08_v1_audit.md) is incorporated on its unchanged implementation: independent quadrature/Gaussian known answers, both-direction active nonlinear context comparisons, unequal midpoint ensembles/bridge sign, finite-wall integration/domain rejection, independent UWHAM objective/Fisher covariance, gauge shifts, correlated fixed-state histories, contribution diagnostics and three native seeds/last-half stability. Its **1.481396 +/-0.043706 kJ/mol** mean and **0.040975** replicate spread remain distinct. Previously accepted [M02](../Milestone_02/Gate_03_v2_audit.md) on `6015a652c4a9a9c968ab7933c07ac7bbb4573e12` is carried forward. Prior G06/G07 numerical scopes are unchanged.

Every scientific shell activated `/workspace/atom-mlmm-g08-r2/activate.sh`, set `OPENBLAS_NUM_THREADS=2`, and used `PYTHONPATH=/workspace/AToM_MLMM/src` for direct probes. Runs were serialized under the two-CPU/8-GiB/no-configured-swap profile; OOM/OOM-kill remained zero. [Command records and outputs](evidence/G08_v2_independent_sol61_max/README.md) preserve exact arguments, exits, timestamps and resources.

| Fresh independent command | Exit and observed outcome |
|---|---|
| `python snapshot_probe.py` in independent evidence | 0; exact manifests/Git blobs and v1 preservation verified |
| `python admission_probe.py` in independent evidence | 0; **72 required rejections, 23 positive round trips**, no failures |
| `python -m pytest -q --basetemp /tmp/g08-v2-independent-sol61-max-full` | 0; **437 passed in 324.86 s**, no skips/failures |
| `python -m pytest tests/unit/test_binding_result_admission.py tests/unit/test_restraint_volume.py tests/unit/test_schedule.py tests/sampling/test_analytic_free_energy.py -v --basetemp /tmp/g08-v2-independent-sol61-max-focused` | 0; **21 passed in 33.96 s** |
| `python snapshot_probe.py closing` in independent evidence | 0; all 7,649 tracked files remain unchanged |
| `python tools/check_docs.py --self-test`; `git diff --check` | 0 each; zero local documentation errors, eight checker self-tests pass, clean diff |

## Findings

| Finding and importance | Evidence/location | Repair and closure check |
|---|---|---|
| **G08-R1 — closed.** Final result admission now has verifiable obligation context. | [BindingResult](../../src/atm_mlmm/schema.py), line 699; canonical encoding, line 921; [sole producer](../../src/atm_mlmm/analysis.py), line 199. Independent [probe](evidence/G08_v2_independent_sol61_max/admission_probe.py) and [results](evidence/G08_v2_independent_sol61_max/admission-results.json). | Both original v1 invalid payloads now reject. Constructor and JSON paths reject each/all missing obligations, hidden uncomputed statuses, duplicate/reordered/mismatched ledgers, wrong identity, a nonstandard observable with a matching identity, inconsistent unresolved metadata and corrected-value arithmetic. Valid matching ledger/spec reordering and additional declared obligations work. Complete deterministic and independently checked joint-covariance producer results round-trip. Actual v1 seed-result canonical bytes/content identities remain identical; legacy partials remain readable, while unverifiable legacy finals reject. All affected and full CPU checks pass on this exact snapshot. |

No remaining blocking finding was established within scope. G08-01/02/03/04/06 retain their independently confirmed v1 numerical evidence and pass the fresh affected suite; **G08-05 now satisfies both producer and serialized-record completeness**.

## Decision and handoff

Accept the v1 scientific admission decisions as refined by v2: the optional typed definition, matching identity/ordered ledger, explicit unresolved obligations, corrected-value consistency and deliberate legacy-final rejection provide the missing record guard. Omitting the absent optional field preserves legitimate legacy partial encoding. The `1e-12` arithmetic consistency check is a serialization/record guard; it changes no scientific accuracy tolerance. Joint-covariance validation and scientific uncertainty provenance remain the verified producer's responsibility.

**Accept all six G08 assertions, G08-T1/T2/T3 and combined M04 on the exact submission above**, carrying inherited M02 acceptance. Scope remains the demonstrated analytic CPU engine/accounting and fixed-state correlation profile; every estimator state must be sampled, connected measured overlap is required, and the pinned UWHAM finite-range limits remain. Correlated exchanging walkers, coupled/periodic translation approximations, GPU, molecular affinity and protein/conformational accuracy remain unqualified. G07/M03 physical qualification remains blocked.

Scoped G09/G10 technical preparation/export/restart may proceed under their own prerequisites and the unchanged G07 numerical limits. The parent integrator owns STATUS/publication. This reviewer changed no submitted source, tests, worker/evidence, specification, branch or commit; v1 remains the historical `changes_required` decision for its earlier snapshot.
