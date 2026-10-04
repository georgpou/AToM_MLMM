# G08 v1 independent evidence — GPT-6.1-sol / MAX

Exact submission `29847120ec99c472580ce23c7b1b317c690c3784`; source `966a8d61347f65a69f8ba7e6750c4379d4e0503f`. The canonical decision is [Gate_08_v1_audit.md](../../Gate_08_v1_audit.md): **changes_required**, G08-R1 open.

- `snapshot_probe.py`, `snapshot-check.json`, `frozen-tracked-manifest.json`: independent exact submission/ancestry/manifests and 7,567 tracked-file checks. `closing-preservation.json` confirms unchanged submitted bytes.
- `command_runner.py`, `*.result.json`, `*.stdout`, `*.stderr`: actual command arguments, UTC times, statuses, maximum child RSS and cgroup events. `full-cpu-outside` is the corrected 433-pass run; `g08-focused` has 17 passes. `reload-outside` diagnoses both first-run harness failures.
- `independent_probes.py`, `independent-probe-results.json`: independently authored numerical/admission probes. Exit 1 records two final-result admission defects; nine positive groups and 33 required rejections pass. No worker test helper is imported.
- `admitted-final-uncomputed.json`, `admitted-final-empty-ledger.json`: invalid final records admitted by the reviewed constructor/reader. These are failure evidence, not valid binding results.
- `native-context-records.json`, `native-context-frames.npz`: raw independent native context data and independent expression comparisons, including both directions and active soft-core/offsets.
- `new-midpoint-records.json`, `new-midpoint-ensembles.npz`: new independent samples from both unequal midpoint ensembles and all cross-state energies, with independent quadrature reference.
- `uwham_objective_probe.py`, `uwham-objective-results.json`: independent log-sum-exp objective and gradient/Hessian finite-difference sweep, without MBAR initialization.
- `full-pytest-temp.tar.gz`, `focused-pytest-temp.tar.gz`, their `*.manifest.json`: lossless closed temporary trees, including initial failing reload artifacts and native seed frames. Every file hash, directory mode, symlink and tar hard-link payload was verified before removing only those temporary originals. Archive hashes/counts are in `closing-preservation.json`. Restore into this evidence directory with `tar -xzf <archive>` if needed. Passing outside-repository pytest temp trees are regenerable and are not publication artifacts.

Preserved reviewer tooling failures have `.unavailable-time` or `.hardlink-preflight` suffixes. Initial snapshot enumeration also encountered a tracked directory symlink; the final probe checks link targets explicitly. No scientific source or submitted evidence was repaired during this review.
