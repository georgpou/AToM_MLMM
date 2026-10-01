# G01-T1/T2/T3 and M01 analytic CPU — v1 worker

**Scope:** G01-T1/T2/T3, P0-TEST-G01-01 through 07, plus combined G00/G01 M01 review on `core-analytic-cpu`.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-01 17:22 UTC.\
**Snapshot:** branch `m00-audit-m01-development`; base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`; tested code `e3303000e187e9d03fb0e2fa53d0a22a709feb80`. Subsequent worker/evidence/status edits are report-only.\
**Author:** Codex / GPT-6; exact model version and reasoning setting not exposed.

## Changes

- `identity.py` and `partition.py`: stable real-ID maps, explicit ambiguous metadata errors, whole-ligand group checks, connectivity-based hydrogen completion, every crossing edge, neutral formal component states and ordinary single C–C protein cuts. Ring/peptide/ligand cuts, repeated MM cap parents, multiple cuts per fragment, unknown elements and inconsistent molecule metadata fail explicitly.
- `schema.py`: immutable owned version 1 data for M01 inputs, topology/selection/model/embedding/protocol/runtime descriptions, all-real forces, inventory and validation/acceptance evidence. Strict versions/fields/units, exact force ordering and nonfinite failures. An accepted evidence record requires requirement/test/profile/fixture/log/reviewer coverage and a matching immutable tested snapshot.
- `capabilities.py` and `protocols/`: one/two-group presets remain dependency-light; actual electrostatic, unknown model, incomplete derivatives, unqualified ensemble/runtime/precision and unsupported geometry requests fail without substitution. A passed metadata check explicitly reports `qualified=False`.
- `ledger.py`: read-only complete inventory of admitted standard forces, masses, constraints, box, virtual sites, exceptions and offsets; unknown forces fail. The frozen four-particle input uses independently distinctive parameters. Structural graph inputs are explicitly distinguished from physical-reference chemistry.

No public scientific definition, tolerance, package lock or model policy changed. Later-gate engines/records are not stubbed into M01.

## Verification

Commands ran from the repository root after main activation. [Validation evidence](evidence/M01_v1/validation.json.gz) preserves outputs, fixture hashes and the strict nine-check report. G00 provenance is recorded by [Gate_00_v1_worker.md](Gate_00_v1_worker.md).

| Scope | Exact command | Observed result |
|---|---|---|
| G01-T1/T2 red | `python -m pytest tests/unit/test_identity.py tests/unit/test_partition.py tests/contracts -q` before implementation | 4 failures / 10 setup errors for absent project records/modules; installed dependency baseline already passed |
| G01-T3 red | `python -m pytest tests/unit/test_force_inventory.py tests/contracts/test_evidence_schema.py -q` before implementation | 3 failures for absent inventory/evidence API |
| Deliberate guard regressions | Focused new group/cut/runtime/map/evidence tests, commands in saved development output | 6 expected failures before guards; later passed |
| G01 assertion files | `python -m pytest tests/unit/test_identity.py tests/unit/test_partition.py tests/contracts/test_schema.py tests/contracts/test_architecture_boundaries.py tests/contracts/test_capabilities.py tests/contracts/test_evidence_schema.py tests/unit/test_force_inventory.py -v` | All 24 tests pass within the final 35-test suite |
| Full available CPU suite | `python -m pytest -q` | Exit 0; 35 passed |
| Analytic profile | `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; 34 passed, 1 model test deselected |
| Strict environment baseline | `python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"` | Exit 0; all nine checks pass |
| Documentation | `python tools/check_docs.py --self-test` | Exit 0; no errors, eight self-tests pass |

The checks use hand-written expected IDs, arrays and inventory parameters. Module/record absence establishes new structural APIs, while deliberate post-implementation faults establish malformed-map/runtime/provenance rejection. There is no claimed neural or molecular derivative qualification.

## Handoff

Independent combined review must cover [G00-T1](Gate_00_v1_worker.md), all G01 assertions and the [M00 analytic decision](../Milestone_00/Milestone_00_v1_audit.md) on one snapshot. Request independent acceptance only for core analytic CPU. Full M00 physical-reference decisions, G00 model/GPU tasks and all later numerical gates remain pending. After acceptance the next implementation is G02's native analytic ATM evaluation, under its own gate.
