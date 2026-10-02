# G03 routing/integration and combined M02 — v1 worker

**Scope:** G03-T1/T2/T3 and combined G02/G03/M02, inheriting independently accepted M01; `core-analytic-cpu` on Reference/CPU.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-02 12:19:48 UTC.\
**Snapshot:** `m02-analytic-atm`; copied parent/base `87146b4cc7fbd0b58d6688903a5ba081b813ac13`; G03 implementation `2c1acefdbe7cecdc67d8bcf4138008a6207d5143`; completed tested code `4c952dba5563572cf9e39527e64fe28ee201c385`. The submitted evidence/report commit changes no source/test/fixture/environment input.\
**Author:** Codex / GPT-6; exact runtime model version and reasoning setting not exposed.

## Changes

[G02's worker](Gate_02_v1_worker.md) records the preceding native implementation and baseline. G03 adds a separate reserved-group production export, recursive force ownership checks, an all-active group-0 preparation copy and a narrow [AToM adapter](../../src/atm_mlmm/adapters/atom.py). The pinned upstream commit is `9e26c5a3811038be1c98e3be6af4c78cd0dd57a7` (v8.5.0, distribution 8.5.0b0); no upstream patch is made.

The adapter invokes actual upstream ABFE/RBFE ligand/displacement/ATM/integrator methods using explicit `VARIABLE_FORCE_GROUP=1`. The real default name-based route selects no honestly named PythonForce and leaves originals active; a regression reproduces and rejects that result. The corrected route places every physical force once under ATM and the separately declared harmonic restraint outside once. Recursive checks reject occupied group 1, duplicated physical content, nested ATM under ATM/CustomCV and originals left outside. Masses and constraints are preserved.

The adapter contains upstream classes, protocol keys, nm-to-Angstrom/kJ-to-kcal/fs-to-ps conversions and State filenames. Tiny upstream floating-point displacement roundoff is checked before replacing it with the exact declared fixed map; index/sign errors remain fatal. Shared physics and records contain no upstream or model-selection branches. The adapter reuses the actual upstream worker state-setting method; restoring State explicitly reinstates and checks all requested/auxiliary parameters and fixed full-particle maps.

Large physical marker forces are checked against the **actual integrator's** group mask in physical preparation, ABFE and RBFE. Tests also run two actual steps and observe marker-driven motion. Preparation uses LangevinMiddle at **0.0005 ps**, NVT 300 K and group 0; the separate reserved-group export is rejected as preparation input. System/map/parameter/membership/profile, integrator-mask/timestep/temperature and saved routing-report mutation fail before evaluation.

## Verification

Commands ran at the repository root after `source /workspace/.onboarding/atom-mlmm-m02/activate.sh`, except the upstream regression in `<setup-prefix>/sources/AToM-OpenMM`. [Raw validation](evidence/M02_v1/validation.json.gz), [environment identity](evidence/M02_v1/environment-manifest.json.gz), [strict validation](evidence/M02_v1/strict-validation.json.gz), [numerical evidence](evidence/M02_v1/numerical-results.json) and [source/input hashes](evidence/M02_v1/source-input-manifest.json) identify the completed snapshot.

| Check | Actual result |
|---|---|
| Initial G03 file selection with `-q` | Exit 1; **20 intended absent-API failures** |
| New mask/routing-metadata/time-conversion guards before implementation | Exit 1; **one intended failure each** |
| Bundle/profile replacement before guard | Exit 1; **4 intended failures, 25 deselected** |
| `python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v` | Exit 0; **38 passed in 6.58 s** |
| Full G02 command in its worker | Exit 0; **78 passed in 11.06 s** |
| `python -m pytest -q` | Exit 0; **164 passed in 27.88 s** |
| `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; **163 passed, 1 deselected in 21.36 s** |
| Strict `validate.py --repository "$PWD"` | Exit 0; **all nine checks passed**, including upstream UWHAM and eight documentation self-tests |
| Separate upstream `python -m pytest -q tests/test_uwham.py` | Exit 0; **1 passed in 2.17 s**, covering three datasets |
| Fresh complete environment characterization | Five dependency checks and four required API checks passed; exact inventories, artifacts, sources and lock hashes match |
| Documentation and whitespace | `python tools/check_docs.py --self-test` / `git diff --check`: see submitted validation; no errors |

| Stable test ID | Established assertion |
|---|---|
| P0-TEST-G03-01 | Explicit group route owns every physical PythonForce once; real default route rejected |
| P0-TEST-G03-02 | Full force equals actual selected force with a large physical marker, preparation/ABFE/RBFE on both platforms |
| P0-TEST-G03-03 | Group-0 preparation and reserved-group export remain separate; stock group-0 omission reproduced |
| P0-TEST-G03-04 | Both protocol paths match native and independent nonlinear observables for local/environment substitutes |
| P0-TEST-G03-05 | 0.5 fs -> 0.0005 ps and nm -> Angstrom exactly once; protocol keys only in adapter; explicit nonidentity final mapping |
| P0-TEST-G03-06 | Occupied group, duplicate physical content, nested ATM and double ownership rejected recursively |
| P0-TEST-G03-07 | Full fixed maps after construction, state changes and fresh reload; map/parameter/membership/profile mutation rejected |

## Combined M02 submission and limitations

Submit **all nine G02 and all seven G03 checks on this same snapshot**, including direct/native/upstream comparisons with nonzero outside terms, tuple order, full-real forces, unit/subset/final-map conversions, both unequal ligand groups, MM-only motion, A-B-A, exact nonlinear derivatives, deliberate compiled/executable faults, offline reloads and active integration masks. Worker self-checks establish readiness, not independent acceptance. The reviewer must inspect the full implementation/test diff and write matching G02 and G03 audit logs; the G03 decision must explicitly cover combined M02.

The narrow adapter qualifies analytic construction, actual integrator masks and State parameter handover. Full upstream molecular preparation, asynchronous worker lifecycle, checkpoint restart and replica exchange remain G09/G10 work. The environment-dependent substitute qualifies full-gradient plumbing, not actual electrostatic embedding. No caps, chemical/protein accuracy, periodic physics, molecular ABFE/RBFE or GPU claim is made. M00 physical-reference decisions and G00-T2/T3 owning profiles remain pending. After independent acceptance, the next physical gate is G04 and the independent analysis path begins at G08.
