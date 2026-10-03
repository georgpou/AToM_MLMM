# G05 prepared-reference provenance repair — v2 worker

**Scope:** respond to the independent v1 software review's prepared-T4 loader
finding. No quantum target or model-versus-quantum comparison is run.
**Base source:** exact published `a7768e375476667139db374dc0091999263a37de`
on child `m03-reference-g05`; only that child is changed.
**Outcome:** code repair and focused regressions pass; exact-snapshot independent
closure is accepted for scope; full G05 acceptance remains pending.

The reviewer reproduced acceptance of a reference bundle with the wrong or
missing approval plan hash, or a missing reviewed commit. The generator already
binds approval to the input manifest, but `load_references` did not retain that
check. The importer now compares the embedded approval's input-manifest digest
to the actual loaded file and requires an exact lowercase 40-hex review commit
before reading reference records. Existing agreement/reviewer/settings/geometry,
record hash and completeness checks remain in place.

`tests/unit/test_reference_provenance.py` uses only explicitly labelled temporary
synthetic file records. A matched fixture remains readable; six corrupt/missing
approval cases must raise `IdentityError`. These test-only boolean values and
zero arrays are not actual user agreement, quantum data, chemical evidence or a
substitute for the two stable G05-T4 checks. No MACE or quantum runtime is called.

| Capture in evidence/G05_v2 | Actual result |
|---|---|
| red-reference-approval-binding | Exit 1; six intended rejection failures, one matched positive control passed |
| green-reference-approval-binding | Exit 0; ten integrity/known-number metric checks passed |
| full-after-provenance-repair | Exit 1; 292 passed, two failed for missing quantum data before any model comparison; 72.05 s |
| analytic-after-provenance-repair | Exit 0; 272 passed, 22 deselected; 34.98 s |

The 270-file [source/input manifest](evidence/G05_v2/source-input-manifest.json)
records one changed production file and the new unit test. All scientific input
files, exact M00 v3 plan, quantum method/settings, limits, model bytes, locks,
retained-MM ledger and accepted earlier source are unchanged. Original RED and
reviewer findings remain preserved; no earlier capture is overwritten.

The user explicitly approved the presented exact plan and resource budget on
2026-10-03. The new `M00_v3_decision/decision-approved-20261003.json` preserves
the actual statement and reviewed manifest/audit digests; historical
`decision-pending.json` remains false and unchanged. Generate the exact
reviewed references after this recorded agreement, check numerical controls,
preserve every chemical result, then obtain complete fresh-context Astra/high
G05 review on the final frozen source/data snapshot. G06/G07 remain later.

The actual fresh-context gpt-6-astra/high reviewer
`/root/g05_provenance_repair_v2` closes R1 and accepts prepared-loading readiness
on exact committed `3124c6d275bf19a32ce364dfdb83b11115828ac5` in the
[v2 audit](Gate_05_v2_audit.md): ten focused tests, one independent positive/29
rejections before record access, 270 source/input hash matches and protected
scientific/model/lock preservation. It reviews no ongoing mutable quantum data.
