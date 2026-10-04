# Independent G06/G07 v1 review evidence

Reviewer: **GPT-6.1-sol / MAX**, audit only. Reviewed HEAD
`ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b`, tested source
`c584086da68654b07f1a477d7ce1e48da42a9838`, accepted G05 base
`08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`.

This new directory contains actual independently run output. Submitted source,
fixtures, model, settings/limits, locks, prior evidence and all 46 accepted G05
records are unchanged. No DFT/reference job, model download, repair, publication
or further reviewer was launched.

- [Audit start](audit-start.json) freezes SHA-256 for all 1,924 tracked files.
- [Full CPU output](full-cpu-suite/command.log) and [receipt](full-cpu-suite/result.json):
  381 passed in 259.67 s, exit 0, one-second resource telemetry.
- [Focused output](focused/command.log) and [receipt](focused/result.json):
  45 passed in 70.03 s: 23 G06, ten joint, ten extension, two matrix.
- [Independent byte/ledger/arithmetic script](verify_inputs_and_arithmetic.py),
  [output](inputs-and-arithmetic-rerun.log) and [results](inputs-and-arithmetic.json):
  all 181 submission hashes, 75 new fixture hashes, 46 G05 records, exact ledgers
  for all 50 descriptions, all 40 sensitivities and all seven failures retained.
  [Initial setup failure](inputs-and-arithmetic.log) records the first invocation
  without `PYTHONPATH`; it failed at import before evaluation and is not scientific
  evidence of an implementation failure.
- [Additional probes](independent_probes.py), [measurements](independent-probes.json),
  [exception measurements](exception-probe-observed.json), [output](additional-probes/command.log)
  and [receipt](additional-probes/result.json): two exception conventions, independent
  Ewald and switched LJ, winding/other-ligand rejection, 24 alternative-cap periodic
  three-route comparisons, five total intermediate directional FD sweeps and five
  counterfactual force/map checks. Operative physical faults are also exercised by
  the maintained extension tests in the focused run.
- [Strict environment runner](strict_environment.py), [result](strict-environment-result.json)
  and [capture](strict-environment-capture/command.log): unchanged validator, 9/9.
  [Before](strict-outputs-before.json)/[after](strict-outputs-after.json) hashes prove
  that prior validator outputs were preserved. Only logs/preparation/result output
  destinations are redirected into this directory.
- [Final state](final-state.json) verifies all frozen bytes, exact periodic
  artifact ledger/energies and new audit artifact hashes. The
  [documentation check](documentation-check.json) records the final link/self-tests.

All commands run from `/workspace/AToM_MLMM-m03-g06-g07`, after:

```bash
source /workspace/atom-mlmm-g05-v2/activate.sh
```

Exact test commands are in the receipt JSON. To reproduce the arithmetic or
additional probes, use a new evidence directory, copy the relevant audit script
and `audit-start.json` there, and run with `PYTHONPATH=src:.`. Result files are
opened exclusively to preserve prior attempts. The arithmetic script uses
the unchanged submitted records and performs no model/quantum evaluation; the
additional probe uses the pinned local model and no QM. The strict runner also
opens its evidence exclusively and needs its own unused directory.

Verdicts are in [G06 audit](../../Gate_06_v1_audit.md) and
[G07/M03 audit](../../Gate_07_v1_audit.md): narrow G06 and G07 numerical scopes
accepted; G07-T4 and M03 physical closure blocked. G08 may proceed on its accepted
G02/G03 prerequisites.
