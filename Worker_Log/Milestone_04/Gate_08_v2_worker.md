# G08-R1 and combined M04 — v2 worker

**Scope:** G08-R1 closure; G08/M04 analytic CPU scope carrying forward the frozen
v1 independent numerical evidence.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-04 15:09 UTC.\
**Snapshot:** `m04-engine-readiness`; base `89eb8b9` (v1 audit/report-only commit);
tested source `8cf2494424d796fc3fc393e25b00e05b6281a85f`; submission adds only
this report, evidence and STATUS. Parent backend model/reasoning metadata is not
exposed. Independent reviewer is requested as actual GPT-6.1-sol/MAX.

## Changes

The [v1 audit](Gate_08_v1_audit.md) confirmed the numerical expressions, estimators
and MD evidence, but found that a caller/JSON could admit final BindingResult
values with absent or uncomputed corrections. The [repair plan](G08-R1-repair-plan.md)
and [v2 amendment](../../docs/project-0/specs/G08-record-admission-v2.md) record
the migration and scope; amendment approval remains pending review.

BindingResult now carries an optional typed thermodynamic definition. Final
values require its matching identity, standard observable and complete ordered
resolved correction ledger; contradictory unresolved metadata and final-value
arithmetic reject. The sole producer supplies the definition. Legacy partial
encoding remains byte-identical; definition-free legacy final values reject.
The verified producer still owns joint-covariance validation and final uncertainty.

Only schema admission/encoding, the producer's result construction and a new
four-node regression file changed scientifically. The [83-file manifest](evidence/G08_v2/source-test-manifest.json)
identifies all source/tests; v1 logs, audit, raw MD/reference data and failures
remain intact. No Hamiltonian, model, environment, estimator, threshold or
quantum accounting change occurred.

## Verification

Commands ran from `/workspace/AToM_MLMM`, scientific shells sourced
`/workspace/atom-mlmm-g08-r2/activate.sh` and set `OPENBLAS_NUM_THREADS=2`.
Reference double NVT and locked PyMBAR 4.0.3/AToM 8.5.0b0 remain the profile.

| Check | Command | Exit and observed outcome |
|---|---|---|
| Admission RED | `PYTHONPATH=src python -m pytest -q /tmp/test_binding_result_admission.py` before implementation | 1; **4 failed in 0.13 s**, including admitted invalid finals and missing typed definition |
| G08/R1 focused | `python -m pytest -q tests/unit/test_binding_result_admission.py tests/unit/test_restraint_volume.py tests/unit/test_schedule.py tests/sampling/test_analytic_free_energy.py` | 0; **21 passed in 34.16 s** |
| Full available CPU | `python -m pytest -q --basetemp /tmp/g08-v2-root-full` | 0; **437 passed in 322.62 s**, no skips |
| Documentation/whitespace | `python tools/check_docs.py --self-test`; `git diff --check` | 0; zero errors/eight self-tests; clean diff |

[Evidence](evidence/G08_v2/README.md) preserves actual outputs and exact source
hashes. New tests exercise direct and serialized empty/missing/uncomputed,
duplicate/reordered/mismatched ledgers, wrong identity/observable/final arithmetic,
legacy partial encoding, and deterministic/uncertain-covariance producer round
trips. Runs were serialized on the two-CPU/8-GiB/no-swap profile; OOM/OOM-kill
remain zero. No scientific run or dependency problem remains for this repair.

## Handoff

Independent v2 closure must verify both original admitted invalid payloads now
reject and legitimate partial/final values round-trip on this exact snapshot,
with affected G08 checks. Carry forward unchanged v1 numerical evidence rather
than repeating prior G06/G07 reviews. Full G08/M04 acceptance remains pending.
G07/M03 physical qualification, GPU profiles, molecular affinity and correlated
exchanging-walker analysis remain open/unqualified. Continue scoped G09/G10
technical preparation/restart after accepted G08 closure. User input on the later
protein target and HPC settings has been requested asynchronously; it does not
block this local repair.
