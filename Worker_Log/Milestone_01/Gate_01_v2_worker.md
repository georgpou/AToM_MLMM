# G01 review repairs and M01 analytic CPU — v2 worker

**Scope:** closure of M01-R1/R2 from [the v1 combined audit](Gate_01_v1_audit.md), retaining G00-T1/G01-T1/T2/T3 and M01 `core-analytic-cpu` scope.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-01 18:12:22 UTC.\
**Snapshot:** `m00-audit-m01-development`; original base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`; reviewed predecessor `c649deea395344c197e33f9628a02a045992dca6`; tested repair code `141c7fbcf2c5407e7880512d5481639bdc81bf57`. Subsequent evidence/status/report changes are report-only.\
**Author:** Codex / GPT-6; exact model version and reasoning setting not exposed.

## Repairs

- **M01-R1:** `validate_request` now explicitly admits policy version 1, the reviewed neutral protein C–C boundary policy and the analytic relative-energy convention. Analytic-local declares local dependence; analytic-environment explicitly declares MM environment dependence. Unknown values or a mismatched backend/locality fail before context construction. The development guide records these names; no physical energy, units or numerical limit changed.
- **M01-R2:** acceptance evidence requires every fixture, log and reviewer reference to identify a nonblank string. Whitespace-only tuples cannot satisfy a required reference. Existing profile/snapshot/result/coverage checks remain intact.

The v1 worker, audit and raw evidence are preserved. The new tests cover each rejected policy/model field, a valid environment-dependent description, and each blank-reference field separately and together. README's next-branch example now inherits this development successor.

## Verification

Commands ran at the repository root after main activation. [Repair evidence](evidence/M01_v2/validation.json.gz) preserves exact commands, outputs and exit codes.

| Check | Actual result |
|---|---|
| New R1/R2 focused regressions before repair | Exit 1; 11 intended failures, including a mismatched environment-locality declaration |
| R1: `python -m pytest tests/contracts/test_capabilities.py -q` | Exit 0; 13 passed |
| R2 blank fields, individually and together, before repair | Exit 1; 4 intended failures |
| R2: `python -m pytest tests/contracts/test_evidence_schema.py -q` | Exit 0; 5 passed |
| `python -m pytest -q` | Exit 0; **47 passed** |
| `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; **46 passed, 1 deselected** |

The unchanged G00 APIs, exact locks, source archives, installed dependencies and two-environment setup retain [their provenance evidence](evidence/M01_v1/environment-manifest.json.gz); the v1 independent audit freshly passed all nine strict setup checks. This repair changes request/evidence validation and its tests, so affected checks plus the full CPU suite were rerun. No dependency or model-loading change requires a new installation.

## Handoff

Request independent closure of M01-R1/R2 on this exact repair snapshot and combined M01 acceptance with the unchanged v1 review evidence. Full M00 physical-reference decisions, G00-T2/T3 and all later molecular gates remain pending. Next implementation after acceptance: G02.
