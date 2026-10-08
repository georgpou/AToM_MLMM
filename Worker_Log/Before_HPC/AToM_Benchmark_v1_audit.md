# AToM FKBP benchmark and cleanup — v1 audit

**Reviewed worker:** [AToM_Benchmark_v1_worker.md](AToM_Benchmark_v1_worker.md),
`hpc-atom-benchmark`, base `590cb5258696042b29856df37f6053ba820d2f56`.
**Scope:** Source-checkout AToM benchmark workflow, narrow adapter and cleanup;
CPU/Reference profile, no scientific gate review.
**Reviewer:** Fresh-context `/root/final_review` subagent, read-only. Model/effort
values are not exposed. Initial review 2026-10-07; repair review 2026-10-08 UTC.
This record is transcribed by the implementing agent from the independent report.
**Verdict:** No material findings remain in the reviewed repairs.

## Independent evidence

The reviewer reran all three new focused test files: **26 passed in 0.43 s**.
Installed upstream source hashes passed. All 18 support-matrix evidence paths
exist; their 17 distinct files and quantum recovery history/approval bytes match
base. No source edits, MD/QM or full-suite run were performed by the reviewer.
The implementing agent's broader/run validation is recorded separately.

| Finding | Independent evidence | Repair and closure |
|---|---|---|
| Important: interrupted preparation could overwrite partial outputs | A KeyboardInterrupt stub left `_min.xml` without a final state/failure marker; retry called preparation again and overwrote bytes | Fsynced preparation-attempt marker before upstream; reject all re-entry; record/re-raise BaseException. Independent `os._exit(17)` stub left marker and partial bytes; retry refused before upstream |
| Minor: initial centroid offset used equal weights | Stock AtomUtils leaves group weights implicit, so OpenMM uses masses. Original offsets differed by 0.055–0.076 Å | Actual system masses used. Independent stock-restraint zero-energy test passes |
| Additional verified repair: stock preparation resets timestep to 1 fs | Pinned `massage_keywords` unconditionally overwrites TIME_STEP | Scoped hook preserves requested timestep. Independent massage/actual preparation integrator check gives **0.0005 ps**; both upstream hooks restore |

The reviewer found no other material force-count, NVT, source, complete-ligand/
cap mapping or cleanup issue. The exact source/test/input inventory is in
[evidence/atom-benchmark-v1/reviewed-files.json](evidence/atom-benchmark-v1/reviewed-files.json).
The later input metadata edit removes an unverified PDB citation; it changes no
chemical or execution settings. No gate, milestone, affinity, GPU, cluster parity,
or long production acceptance is granted by this review.
