# G09 v4 failure-archive repair evidence

Tested source is `027f8173babc13606afb24d96f58148704e38b1b`; the
[snapshot](snapshot.json) binds commands/results to the unchanged locked CPU
profile. The [worker](../../Gate_09_v4_worker.md) records exact commands.

- `red.log`: all 12 new actual-worker boundary/CLI regressions fail on the v3 submission.
- `affected.log`: 19 affected checks pass after repair.
- `full-cpu.log`: 501 CPU tests pass, no skips, in 498.74 s.
- `map1-write-failure/`: actual full-suite primary metadata, cached State,
  checkpoint and map0 survive an injected map1 write failure. Primary error is
  `NumericalDomainError: original scientific trigger`; the explicit archive
  error is `OSError: archive trigger: map1-state.xml`. No sample was appended.
- `scientific-source-input-manifest.json`: 49 frozen production/input/regression
  hashes. Only `workflow.py`, `__main__.py` and the new regression differ from
  the v3 scientific snapshot. The physical inputs, adapter and numerical limits
  remain unchanged.
- `file-manifest.sha256`: hashes all captures except the manifest itself.

V3 workers, audits and captures stay frozen. Their complete local portable water
attempts remain under `/workspace/cloud-engine-pilots/water-v3/`; this repair
does not silently migrate those source-bound bundles. The full repair suite
builds fresh actual workers and reruns all solvent/exchange numerical tests.
No additional CLI production trajectory, QM or environment replacement ran.

The original independent RED/CLI evidence remains at
[cloud_v3_independent](../cloud_v3_independent/README.md). Root verification is
not independent closure; that requires the actual new review.
