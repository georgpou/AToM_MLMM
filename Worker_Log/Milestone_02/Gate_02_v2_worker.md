# G02 admission repairs and gate closure — v2 worker

**Scope:** M02-R1/R2/R3 repair and all G02-T1/T2/T3 assertions, reviewed together with G03/combined M02; `core-analytic-cpu`, Reference/CPU.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-02 13:11:56 UTC.\
**Snapshot:** branch `m02-analytic-atm`; published continuation base `a8098a43d46df76b981861aa8dec0522d31be966`; original development predecessor `87146b4cc7fbd0b58d6688903a5ba081b813ac13`; repaired/tested source commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. Subsequent worker/evidence/STATUS submission changes are report-only.\
**Author:** Codex / GPT-6 family; exact deployed model/backend version and reasoning setting not exposed.

## Reassessment and changes

Read AGENTS, README, DEVELOPMENT, STATUS, both M02 handoffs, both v1 worker/audit pairs, G02/G03 and relevant S01–S07 contracts; inherited M00 analytic design and M01 v2 acceptance. Independently inspected the actual admission reproducer, unexecuted draft, production code, existing tests/oracles and pinned upstream ABFE/RBFE expression construction. All 126 handoff input hashes matched, the checkout was clean, the handoff was present and the fetched remote tips matched the recorded main/predecessor. Existing branch work and all 28 submitted v1 milestone files are preserved byte-for-byte.

The fresh workspace lacked the previous installation. Rebuilt the unchanged exact core/Amber locks at `/workspace/.onboarding/atom-mlmm-m02-v2`. The first attempted prefix hit the documented read-only Conda registry restriction; the authorized installer then succeeded with filesystem access. No dependency lock, loader, model or upstream source changed. Main remains Python 3.11.16/NumPy 2.4.6; Amber remains separate with NumPy 1.26.4.

Fresh baseline: **164 passed**. The preserved independent admission probe reproduced all **13 failed required rejections**, including the v1 energy changes and unaffected controls. The draft remains unchanged and outside tests; it was not executed. New independently reassessed regressions are in [test_m02_admission.py](../../tests/contracts/test_m02_admission.py).

| Finding | Minimal repair and regression coverage |
|---|---|
| M02-R1 | `atm.py` checks actual expression tokens and unique required ATM globals before sealing or Context creation. Whitespace between tokens is allowed, including pinned upstream formatting; split identifiers are rejected. Wrong expressions, missing/duplicate globals and linear/production schedules exercise sealing and direct reconstructed-artifact admission. |
| M02-R2 | The common runtime guard pins every nonschedule Context global, covering direct and preparation evaluation plus externally restored State. Native/upstream construction, sealing and reload reject physical/schedule name collisions. Routing proves children match the sealed physical source before its globals are examined: OpenMM child access returns base `Force` wrappers without the concrete accessors. Positive controls independently check both endpoints/all real forces with a transferred-atom physical global and permuted final map, both platforms, valid schedule changes and explicit State restoration. |
| M02-R3 | `routing.py` normalizes name/group only for duplicate-content admission; existing name-preserving ownership/report hashes remain unchanged. PythonForce and CustomExternalForce copies with rename, regroup or both reject in export/native/upstream. Same-name distinct physical parameters remain admitted and numerically correct. |

Changed production files: `atm.py`, `adapters/atom.py`, `routing.py`. No scientific definition, schema, tolerance, fixture, force/map contract, environment lock or trusted loading policy changed. This enforces existing S01/S02 ownership, S03 fixed physical identity and S05 executed-schedule contracts; no specification amendment is needed.

## Verification

Commands ran from the repository root after `source /workspace/.onboarding/atom-mlmm-m02-v2/activate.sh`; direct probes used `PYTHONPATH=src:.`. [Raw command captures](evidence/M02_v2/check-summary.json), [source/input manifest](evidence/M02_v2/source-input-manifest.json), [environment identity](evidence/M02_v2/environment-manifest.json.gz) and [strict raw validation](evidence/M02_v2/strict-validation.json.gz) identify the tested inputs. [Evidence guide](evidence/M02_v2/README.md) locates every output.

| Check | Actual result |
|---|---|
| Initial new-test run | Aborted in test construction, exit -11: a temporary OpenMM System owner was released before copying its borrowed force. Retained the owner and reran; this aborted run is preserved and is not RED evidence. |
| Corrected new-test RED, `python -m pytest tests/contracts/test_m02_admission.py -q` | Exit 1; **45 failed, 25 passed** on 70 initial cases. Failures are missing rejection/early diagnostic, with positive controls passing. Four additional independent cases failed before their repair; the six-node R1 selection includes two already failing cases. |
| R1 focused GREEN / existing G02 selection | Exit 0; **26 passed** / **78 passed**. |
| R2 first focused run | Exit 1; four bypassed-constructor collisions exposed base child wrappers. Source inspection after verified routing fixed this; final focused run **27 passed**. |
| R3 focused GREEN | Exit 0; **21 passed**. |
| All new regressions | Exit 0; **74 passed**. |
| Final six original gate files plus `test_m02_admission.py`, `-v` | Exit 0; **190 passed**, including original 78 G02/38 G03 and 74 admission cases. |
| `python -m pytest -q` | Exit 0; **238 passed in 43.75 s**. |
| `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; **237 passed, 1 deselected in 34.01 s**. |
| Strict `python /workspace/.onboarding/atom-mlmm-m02-v2/validate.py --repository "$PWD"` | Exit 0; **9/9 passed**. |
| Upstream directory, `python -m pytest -q tests/test_uwham.py` | Exit 0; **1 passed**, three datasets. |
| Preserved `probe_admission.py --require-rejection --output .../M02_v2/repaired-admission-results.json` | Exit 0; **18 rejection cases reject**, both restoration positives retained; none of the 13 v1 failures remains. |
| Unchanged copied v1 independent numerical script | Exit 0; **66 comparisons**, **8 all-coordinate FD sweeps**, **8 upstream A-B-A cases**. Maximum energy/force/final-FD errors `5.706546346573305e-14`, `2.2737367544323206e-13`, `7.487415132345632e-9` in common units. This is worker replay of an independently authored v1 oracle, not a new independent audit. |
| Preserved executable stale-artifact, fresh process/empty cache/network denied | Exit 0; correctly detects raw `u1` error **0.5 kJ/mol**. Valid offline native/upstream reloads and trusted digest rejection pass in the full suite. |
| Documentation/self-tests and whitespace | Strict validation passed eight documentation self-tests; `git diff --check` exit 0. |

All nine stable G02 assertions remain represented by their original gate nodes and new admission coverage: endpoints/units/tuple/outside separation, complete one/two-group maps, environmental motion and real derivatives, A-B-A, deliberate faults and fresh reload, independent harmonics and exact nonlinear chain rule/FD. Frozen Reference limits stay `1e-8 kJ/mol` / `1e-7 kJ/mol/nm`; direct/ATM limits stay `1e-4` / `5e-3`; FD steps stay `1e-3`, `1e-4`, `1e-5 nm` with final component limit `1e-5`. No sample or nonfinite value was suppressed.

## Handoff

Submit this exact repaired source/input snapshot with [G03/combined v2 worker](Gate_03_v2_worker.md) for independent closure of all findings and complete G02/G03/M02. Worker self-checking does not approve a gate. Preserve the historical v1 `changes_required` decision for its own snapshot.

Scope stays nonperiodic seven-real-atom analytic Reference/CPU NVT, float64 callbacks and timestep at most 0.0005 ps. Molecular ABFE/RBFE, caps, chemical/protein accuracy, full pretrained-model and GPU qualification, periodic/actual electrostatic physics, binding corrections and full asynchronous preparation/restart/replica exchange remain deferred. M00 physical-reference decisions remain open before G05/G07 chemical comparisons. The bundled academic MACE example passes only as its existing integration regression.
