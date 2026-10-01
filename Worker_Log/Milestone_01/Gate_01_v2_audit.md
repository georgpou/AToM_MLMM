# G01 review closure and M01 analytic CPU — v2 audit

**Reviewed worker:** [Gate_01_v2_worker.md](Gate_01_v2_worker.md).\
**Reviewed snapshot:** branch `m00-audit-m01-development`, exact HEAD `04944c67fc04c1667723f5292a07f8401cb94184`; worker-tested repair code `141c7fbcf2c5407e7880512d5481639bdc81bf57`; reviewed predecessor `c649deea395344c197e33f9628a02a045992dca6`; original base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`.\
**Scope/profile:** independent closure of M01-R1/R2 and combined G00-T1/G01-T1/T2/T3/M01 acceptance on `core-analytic-cpu`, incorporating the unchanged review evidence in [Gate_01_v1_audit.md](Gate_01_v1_audit.md).\
**Reviewer:** independent Codex reviewer `/root/m01_review_fallback`, GPT-6 family; exact runtime model/version and reasoning settings are not exposed. This reviewer authored neither implementation nor repairs.\
**Finished:** 2026-10-01 18:13:36 UTC.\
**Verdict:** `accepted_for_scope`.

## Evidence

Read the v2 worker and repair evidence; inspected the entire source/test diff from the v1 reviewed snapshot, plus the development-guide metadata names. Only `capabilities.py`, the acceptance-reference check in `schema.py`, and their two affected test files changed in the implementation/test/fixture/environment scope. No physical definition, numerical tolerance, dependency, input fixture or trusted loader policy changed. The v1 independent review of identities, selections, record immutability/units/order, architecture boundaries, MM inventory and G00 provenance remains applicable.

Commands ran at the repository root after `source /workspace/.onboarding/atom-mlmm/activate.sh`; direct Python probes additionally used `PYTHONPATH=src`.

| Independent closure check | Actual result |
|---|---|
| `git rev-parse HEAD`; `git status --short` | Exact reviewed HEAD above; initially clean. |
| `git diff 141c7fbcf2c5407e7880512d5481639bdc81bf57 HEAD -- src tests fixtures environment` | Exit 0, empty. Reviewed and worker-tested repair code/inputs match. |
| `python -m pytest tests/contracts/test_capabilities.py tests/contracts/test_evidence_schema.py -q` | Exit 0; **18 passed in 0.07 s**. |
| Standalone R1 probes using the v1 reproducer's admitted request and capabilities, allowing both analytic backends | **7 unsupported requests rejected** with `UnsupportedCapability`: unknown policy version, disulfide/charged boundary, eV energy convention, reactive locality, environment locality on analytic-local, and local locality on analytic-environment. Both valid backend/locality descriptions pass metadata admission with `qualified=False`. |
| Standalone R2 probes using valid report/acceptance records, replacing each required reference tuple | **10 invalid cases rejected** with `QualificationError`: each of fixture/log/reviewer references separately containing `(' ',)`, `('valid', '')` or `('valid', '\t\n')`, plus all three fields blank together. The valid evidence control still constructs as accepted. |
| Recompute SHA-256 of the preserved v1 gzip environment manifest and compare with the v2 evidence digest | Exit 0; unchanged environment evidence digest matches. |

Inspected [v2 raw repair evidence](evidence/M01_v2/validation.json.gz): focused pre-repair regressions failed as intended (11 failures, and four isolated R2 failures); post-repair capability/evidence suites passed 13/5 tests. The worker's full suite passed **47 tests**, and its analytic selection passed **46 with one model test deselected** on the repair code above. Those full-suite runs are worker evidence, not independent reruns. This focused closure deliberately reuses the v1 independent analytic 34-test pass and fresh nine-check strict environment validation for unchanged behavior and installation evidence.

## Findings and closure

| Finding | Independent closure decision |
|---|---|
| **M01-R1:** unsupported embedding/model policy fields admitted | **Closed.** `validate_request` explicitly admits mechanical policy version `1`, `protein_c_c`, `declared_relative_energy` and backend-appropriate `local`/`environment_dependent` locality. Unknown and mismatched values fail with field-specific errors before context construction. Positive controls preserve the environment-dependent architectural description without qualifying physics. |
| **M01-R2:** whitespace evidence references admitted | **Closed.** Acceptance checks every fixture/log/reviewer-reference entry for a nonblank string, including mixed valid/blank tuples. Existing unit/round-trip/profile/snapshot/result/coverage checks remain intact and pass the affected suite. |

No remaining blocking finding was identified within this repair review and the incorporated unchanged v1 scope. The v1 `changes_required` decision remains the historical decision for its exact snapshot; this v2 decision applies only to the repaired snapshot above.

## Decision and handoff

Accept **G00-T1, G01-T1/T2/T3 and combined M01 for `core-analytic-cpu`** on this reviewed snapshot, using the v1 independent review plus this independent repair closure. G02 analytic native-ATM implementation may proceed under its own gate and tests.

G00-T2 model-asset/loader qualification, G00-T3 hardware qualification and full M00 physical-reference closure remain pending for their owning profiles. This audit grants no neural chemistry, molecular ABFE/RBFE, actual electrostatic physics, periodic physical evaluation or G02+ qualification. No installation or production/STATUS edit was performed; this reviewer added only the v2 audit. The parent integrator owns STATUS and commits.
