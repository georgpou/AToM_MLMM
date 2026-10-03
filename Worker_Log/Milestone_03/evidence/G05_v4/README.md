# G05 continuation evidence

Calculation source: `419b64f7bd79199a0bf999e456f1564fc184cf75` on
`m03-reference-g05`. The [worker log](../../Gate_05_v4_worker.md) owns the scope
and decisions; this directory carries raw evidence, not another status index.

- `quantum-resume-launch.json` binds the actual command and source hashes.
- `calculation-source-input-manifest.json` freezes 116 calculation source,
  test and reference-plan file hashes.
- Installed-package identities include the exact 105 reference packages plus
  the separate 255-package core and 201-package Amber environments.
- `g05-prelaunch-source-tests.log`: 310 passed, exactly two absent-reference
  chemical failures. `g05-recovery-launch-checks.log`: 18 recovery passes.
- Earlier RED, intermediate cache-guard failures and later GREEN evidence are
  preserved. Synthetic recovery test records never enter the chemical fixture.
- `strict-environment-results.json`: 9/9 strict environment/documentation checks.
- [New QM attempt](../../../Milestone_00/evidence/M00_reference_v3/quantum-attempt-v2/)
  holds atomically updated progress, original-record copies, immutable worker
  orders/logs/receipts and one-second RSS/cgroup/disk samples. Each successful
  worker's private scratch is removed after saving its record and receipt.
- `monitor_quantum.py` reads the authoritative progress/samples without
  launching any calculation. Coordinator output is retained separately.

The first resumed contact, `butane-acetamide-d3.8-r0`, completed with a 3 GiB
internal Psi4 allocation, two threads, verified frozen provenance and a measured
worker RSS peak about 4.1 GiB. A runtime allocation is not a new scientific
method/grid setting. All 46 records and all 12 numerical controls are now
validated, and both actual chemical comparisons pass. See [the complete
report](RESULTS.md), [per-row metrics](chemical-row-metrics.csv), [job table](quantum-job-summary.csv),
[cap/parent force evidence](cap-parent-force-evidence.json) and
[audit handoff](AUDIT_HANDOFF.md). Final full source result is 312 passed.

Independent audit is deferred by explicit user instruction. A GitHub push was
rejected by automatic approval review because explicit source/history export
authorization to that destination was required. Work remains local until that
authorization; no remote publication is claimed.
