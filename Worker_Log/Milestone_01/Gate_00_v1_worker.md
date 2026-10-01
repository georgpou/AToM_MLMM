# G00-T1 CPU APIs and provenance — v1 worker

**Scope:** G00-T1 / P0-TEST-G00-01/02, `core-analytic-cpu`.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-01 17:22 UTC.\
**Snapshot:** branch `m00-audit-m01-development`; base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`; tested code `e3303000e187e9d03fb0e2fa53d0a22a709feb80`. Subsequent worker/evidence/status edits are report-only.\
**Author:** Codex / GPT-6; exact model version and reasoning setting not exposed.

## Changes

Added `src/atm_mlmm/environment.py` API/provenance characterization, finite atomic JSON persistence, and `tests/unit/test_environment.py`. Native ATM serialization, selected-particle PythonForce energy/forces and an actual OpenMM-ML mixed-system info result are exercised. Missing maps/APIs, version drift, malformed/incomplete manifests and failed dependency checks fail clearly. Source tag and distribution version remain separate.

The maintained installer reused unchanged locks/artifacts at `/workspace/.onboarding/atom-mlmm`. Its first bootstrap failed at the documented read-only `~/.conda` registry; narrow access created the registry and replay passed. The interrupted bootstrap was preserved separately. Main Python 3.11.16, 255 Conda builds / 156 distributions; Amber Python 3.11.16, 201 builds / 80 distributions. No package lock or loading policy changed.

Exact inventories, lock/artifact hashes, three source commits, verified extracted source files and dependency results are in [environment evidence](evidence/M01_v1/environment-manifest.json.gz). Larger output and development failures are in [validation evidence](evidence/M01_v1/validation.json.gz).

## Verification

All commands used the repository root after `source /workspace/.onboarding/atom-mlmm/activate.sh`.

| Check | Command | Actual result |
|---|---|---|
| Existing baseline | `python -m pytest tests/environment tests/integration -q` | Exit 0; 5 passed |
| G00 red | `python -m pytest tests/unit/test_environment.py -q` before implementation | 4 failed for absent project modules, with dependencies installed |
| API fault | `python -m pytest tests/unit/test_environment.py::test_mixed_system_info_is_exercised_and_missing_mapping_fails -q` before repair | Failed: a missing upstream `oldToNew` was not detected; subsequent pass |
| Manifest fault | `python -m pytest tests/unit/test_environment.py::test_environment_manifest_complete -q` before final validation guards | Exit 1: invalid archive digest was accepted; subsequent pass |
| G00 | `python -m pytest tests/unit/test_environment.py -q` | 6 tests pass in the final full suite |
| Full CPU suite | `python -m pytest -q` | Exit 0; 35 passed |
| Analytic profile | `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; 34 passed, 1 deselected |
| Strict setup | `python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"` | Exit 0; all nine checks pass, including both exact inventories/pip checks, OpenMM installation, preparation and upstream UWHAM |

## Handoff

Review G00-T1 together with G01/M01 on the tested snapshot. G00-T2 asset/loader assertions and G00-T3 hardware qualification remain pending for their respective profiles. The existing bundled MACE example passes as a regression; it does not qualify a real-model gate or chemical adequacy. M00's [analytic-scope audit](../Milestone_00/Milestone_00_v1_audit.md) permits this work; full physical-reference closure remains open.
