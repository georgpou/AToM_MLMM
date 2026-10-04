# G08 v1 worker evidence

This is worker evidence, not independent acceptance. The source/test manifest
identifies the exact scientific implementation and assertions; report-only
updates are distinguished in the worker/audit records.

- `environment-validation.json`: unchanged locked main/Amber reconstruction,
  nine checks with actual commands/exit codes. Failed bootstrap is preserved
  externally at `/workspace/atom-mlmm-g08-install-console.log`; successful
  replay is `/workspace/atom-mlmm-g08-r2-install-console.log`.
- `baseline-pytest.txt`: 416 passes on the recovered predecessor.
- `t1-red.txt`, `t2-red.txt`, `t3-red.txt`, `md-red.txt`: absent APIs/example
  before implementation. These are structural failures, not numerical proofs.
- `t1-green.txt`: the first hard-wall test fails because k=1e18 leaves a finite
  tail just above the unchanged limit. The complete finite-wall quadrature
  checks pass. The limiting spring is increased to 1e20, retaining the tolerance.
- `t1-t2-green.txt`: 12 deterministic tests pass, including actual contexts.
- `t3-green.txt`: original UWHAM default normalization failure.
- `t3-refined-green.txt`: objective roundoff stalls canonical trust-exact at
  gradient 1.638e-10; independent exact-Hessian refinement resolves it.
- `t3-newton-green.txt`: 14 estimator/deterministic checks pass.
- `md-green.txt`: example package collision preserved. `md-file-import-green.txt`:
  explicit-path loading resolves it and the three-seed MD test passes.
- `md-focused-attempt/`: original immutable native harmonic bundles, complete
  recorded positions/full real forces/raw energies, schema records, analyses
  and summary from the passing focused MD attempt. Each of five windows has
  5 ps warmup, then 400 ps recorded at 0.1 ps spacing. Seeds 41/73/109 are
  independent. Their mean is 1.4813958 +/-0.0437064 kJ/mol; replicate spread is
  0.0409745 kJ/mol, a different quantity. All individual and mean criteria pass.
- `md-file-manifest.json`: hashes of the nine original MD artifacts before
  report-only result/summary additions.
- `midpoint-ensembles.txt`, `midpoint-independent-ensembles/`: independent
  inverse-CDF draws from all four deliberately unequal directional potentials;
  both midpoint expressions are cross-evaluated on both midpoint ensembles.
  Independent quadrature checks the bridge and endpoint result; sampled overlap
  and bridge uncertainty also pass. Original sample coordinates are preserved.
- `full-pytest.txt`: 433 passes including all code changes. The supplemental
  midpoint sampling assertions were added afterward; `full-pytest-final.txt`
  records the repeat on that exact complete submission.
- `docs-check-final.txt`: zero local documentation errors/eight self-tests.

The analytic known-answer fixture is not a molecular binding calculation. The
UWHAM and correlation numerical scope, additive schema admission and unresolved
G07 physical limits are explicit in the worker and specification amendment.
