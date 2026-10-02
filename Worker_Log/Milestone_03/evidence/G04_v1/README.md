# G04 v1 worker evidence

These are fresh worker runs, not independent acceptance. [Worker](../../Gate_04_v1_worker.md) identifies scope and exact tested source `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The user paused immediately before Astra launch; [RESUME](RESUME.md) preserves the review instructions.

- `baseline-full.json.gz`, `baseline-analytic.json.gz`, `baseline-strict.json.gz` and full `baseline-strict-results.json.gz`: own 238/237+1/9-check baseline.
- `install-v1.log.gz`, `install-v2.log.gz`, `environment-manifest.json.gz`: unchanged bundle replay, retained registry failure and successful fresh core/Amber installation.
- `geometry-api-red.json.gz`, `ledger-api-red.json.gz`: absent API failures, separate from numerical RED.
- `nested-diagnosis.json.gz`, `diagnose_nested.py`: standalone/native nested-site evidence gathered before deciding a repair; parent redistribution already correct.
- `geometry-numeric-red.json.gz`, `fd-restoration-red.json.gz`, `cap-identity-red.json.gz`: actual geometry/state/identity failures and subsequent passing selections.
- `geometry-ledger-green.json.gz`, `first-full.json.gz`: despite their early capture names, these preserve failed development attempts (three FD component targets, then restoration and tuple/array instrumentation issues); they are **not passes**.
- `g04-green-v2.json.gz`, `g04-expanded-green.json.gz`: 20 then 24 successful cases during development.
- `final-g04.json.gz`, `final-full.json.gz`, `final-analytic.json.gz`, `final-g02.json.gz`, `final-g03.json.gz`, `final-admission.json.gz`, `final-upstream.json.gz`, `final-strict.json.gz`: final 24/262/261+1/78/38/74/1/9 results on the recorded source. Full strict nested outputs are preserved separately.
- `reproduce_numerics.py`, `g04-numerical-results.json`, `final-numerics.json.gz`: independent test-oracle component errors, complete required FD steps plus smaller convergence step, parents/environment and invariant balances.
- `inherited_numerics.py`, `copy-provenance.json`, `independent-numerics.json`, `inherited-numerics.json.gz`: byte-identical inherited independent oracle replay, 66 comparisons/eight sweeps/eight upstream histories. This is preserved independent-oracle provenance, executed by the worker.
- `inherited-admission-results.json`, `inherited-admission.json.gz`, `inherited-stale-offline.json.gz`: inherited admission and trusted stale-artifact checks with new outputs.
- `source-input-manifest.json`, `preservation.json`: all 151 tested source/fixture/environment hashes, and byte equality for 212 inherited inputs/evidence files. Protected main/M01/M02 values and child lineage are explicit.
- `run_check.py`: refusal to overwrite captures, exact commands/cwd/time/HEAD/output/exit. Submission documentation/whitespace captures accompany the frozen worker.

No old evidence, scientific specifications, environment lock, source archive, model asset or existing fixture was rewritten. Current source/inputs are sealed in the manifest; later audit/report/acceptance-only commits must prove equality before inheriting these results.
