# Resumed independent G05 software review evidence

Reviewer `/root/g05_software_audit_v1_r2`, dispatched as gpt-6-astra/high/fresh context. Exact frozen source: **a7768e375476667139db374dc0091999263a37de**, detached `/workspace/AToM_MLMM-g05-review-v2`. Reports: [G05 v1](../../Gate_05_v1_audit.md) and [G00 v2](../../../Milestone_01/Gate_00_v2_audit.md). Only their explicitly stated scopes are accepted. The open T4 finding is G05-v1-R1; no target quantum or model-versus-quantum calculation was performed.

All command captures use [capture.py](capture.py), recording argv, cwd, reviewed HEAD, timestamps, interpreter, thread/import settings, output and exit. Every shell activated `/workspace/atom-mlmm-g05-v2/activate.sh`; numerical commands used `PYTHONPATH=src` and OMP/MKL/OpenBLAS threads=2. `PYTHONDONTWRITEBYTECODE=1` and disabled pytest caching preserve the review checkout.

| Capture | Meaning |
|---|---|
| [software.json](software.json) | 29 focused passes: all 16 real model adapter/locality/domain cases plus checkpoint/environment/candidate/metric checks. Full raw arrays are in [software-numerics/](software-numerics/). |
| [inherited.json](inherited.json) | 214 inherited G02/G03/admission/G04 passes (78/38/74/24). |
| [coordinates-v2.json](coordinates-v2.json) | Reviewer [corrected coordinate probe](probe_coordinates_v2.py), 138/138 checks; [raw results](coordinate-results.json), 117 FD sweeps, complete physical forces, generic rotation, both boundary parents and nonidentity full map. |
| [coordinates.json](coordinates.json) | Preserved initial exit 1 and [initial script](probe_coordinates.py): reviewer incorrectly expected independent Snapshot ID reordering to be admitted; production correctly rejects it. No source repair followed. |
| [domain-total.json](domain-total.json) | [Reviewer supplement](probe_domain_total.py) adds complete total energy/full real forces to all 36 existing scan rows; [raw results](domain-total-results.json), 34 admitted finite rows, two diagnostic extremes retained. |
| [reference-provenance.json](reference-provenance.json) | [Synthetic loader probe](probe_reference_provenance.py), [results](reference-provenance-results.json): wrong/missing embedded approved-plan digest and missing reviewed commit incorrectly accepted. Exit 0 denotes completed diagnosis, not T4 success. Synthetic zero arrays are explicitly labelled non-reference data; final fixture manifest is unagreed. No real decision was changed. |
| [pending-guard.json](pending-guard.json) | [Guard-only probe](probe_pending_guard.py) rejects the actual pending decision before coordinator/worker execution. |
| [snapshot.json](snapshot.json) | [Verifier](verify_snapshot.py), [full identities](snapshot-results.json): clean exact HEAD, 269 source/input hashes, 333 inherited files and 48 exact M00 v3 files match. Includes installed adapter hash, versions and actual pending decision. |
| [upstream.json](upstream.json) | One upstream UWHAM test passes. |
| [documentation.json](documentation.json) | Frozen-tree docs: zero errors/eight self-tests. |
| [report-documentation.json](report-documentation.json) | Preserved initial report-link check: one relative link and two references to not-yet-written evidence failed. Corrected report links are checked by `report-documentation-v2.json` using the frozen checker; no mutable repair source is reviewed. |
| [final-verification.json](final-verification.json) | Final immutable snapshot, recorded result assertions and report/evidence hashes. |

The prior independent reviewer was quota-interrupted without a verdict. Its [full](../G05_v1_independent/frozen-full.json), [analytic](../G05_v1_independent/frozen-analytic.json) and [strict](../G05_v1_independent/strict-environment.json) captures are attributed prior-run evidence: 285 passes/two missing-quantum failures; 265 passes/22 deselected; 9/9 strict checks. Their exact hashes are in `snapshot-results.json`. They were not rerun merely for context restart and do not supply an inferred acceptance. Prior raw evidence remains unchanged.

Reproduction commands are the exact `command` arrays in each JSON capture. Probe scripts write results exclusively into this directory using new output names; choose a fresh evidence directory when replaying. Full G05 still requires actual agreement, repaired provenance, complete reference generation/numerical controls and independent chemical review on a new frozen snapshot.
