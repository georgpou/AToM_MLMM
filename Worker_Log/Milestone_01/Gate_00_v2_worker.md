# G00-T2 pinned asset/loading — v2 worker

**Scope:** bundled MACE-OFF23-small CPU float64 asset/loading prerequisites only.\
**Outcome:** preliminary checks pass; independent combined G05 review pending.\
**Snapshot:** `m03-reference-g05` from `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`; exact source hashes are recorded with G05 evidence.

## Changes and verification

`models/mace.py` verifies retained checkpoint bytes, manifest authorization,
academic licence/digest, pinned provenance and explicit total-energy/CPU/dtype
policy before trusted deserialization. Imports remain lazy. Scoped `slice`
allowance and removal of upstream MACE's unsafe environment override preserve
the initialized default PyTorch loading policy; arbitrary pickle still rejects.

The actual missing-authorization regression reached deserialization before
the repair (RED); it rejects first afterward (GREEN). Missing/wrong digest,
licence and incompatible manifest settings reject. Offline fresh-process
loading denies connect/DNS and uses empty caches, pinned asset and float64.
The initial overly strict safe-global comparison failed because standard
Torch lazy imports add standard types; the diagnosed test baseline initializes
those modules first and verifies no additional weakening by the loader.
All failed captures are preserved.

Baseline full/analytic suites: 262/261 passes (1 model deselected). Preliminary
asset result: 3 focused passes; full 265 passes; analytic 261 passes/4 deselected;
strict environment 9/9; upstream `tests/test_uwham.py` 1 pass. Exact commands,
exits and output are under
[G05 evidence](../Milestone_03/evidence/G05_v1/source-input-manifest.json).
Actual architecture is recorded in
[asset characterization](evidence/G00_v2/asset-characterization.json).
The unchanged installer was replayed into `/workspace/atom-mlmm-g05-v2`, with
main/Amber separate. Both initial failed setup and successful installer logs
are preserved. No replacement checkpoint or package-lock change was made.

## Handoff

G00-T2 acceptance is pending the independent exact-snapshot combined G05
review. This asset result does not accept a real molecular gate or GPU.
