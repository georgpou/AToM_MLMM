# M02 v2 worker evidence

Fresh continuation base: `a8098a43d46df76b981861aa8dec0522d31be966`. Repaired source/input commit: `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. Canonical submissions are [G02 worker](../../Gate_02_v2_worker.md) and [G03/combined M02 worker](../../Gate_03_v2_worker.md). Independent approval is separate.

- `baseline-input-check.json`: all 126 handoff input hashes matched; exact fetched branch tips and 28 preserved v1 file digests.
- `baseline-full.json.gz`, `baseline-admission.json.gz`, `baseline-admission-results.json`: fresh 164-test baseline and the independently reproduced 13 failed rejections.
- `regressions-red.json.gz`: aborted test-construction run; retained as an unsuccessful development attempt, not RED evidence.
- `regressions-red-corrected.json.gz`, `r1-additional-red.json.gz`: meaningful pre-repair failures and passing controls. New final collection totals 74 cases, with 49 missing rejection/early-diagnostic cases demonstrated before repairs and 25 positive/existing-rejection controls.
- `r1-green.json.gz`, `r1-g02.json.gz`, `r2-green.json.gz`, `r2-green-source-guard.json.gz`, `r2-g03.json.gz`, `r3-green.json.gz`, `regressions-green.json.gz`: actual step results; first R2 run retained with four collision failures before the source guard was corrected.
- `repaired-gates.json.gz`, `repaired-full.json.gz`, `repaired-analytic.json.gz`: final 190 gate/admission, 238 full, 237 analytic/one deselected results.
- `repaired-strict.json.gz`, `strict-validation.json.gz`, `environment-manifest.json.gz`, `repaired-upstream.json.gz`: exact environment and separate core/Amber identities; nine strict checks and upstream regression.
- `repaired-admission.json.gz`, `repaired-admission-results.json`: unchanged v1 probe rerun with explicit new output path; 18 negative rejections and both positive restores pass.
- `probe_numerics_v1_replay.py`: byte-identical copy of the preserved independent v1 numerical script (SHA-256 `dc80a105f82e7b7ea947ceea53bff6f1b3357d81e80e098736f7b8a56ded8c69`); its fixed output directory follows the copy, preserving v1 evidence. `repaired-numerics.json.gz` and `independent-numerics.json` retain the worker's replay of that independent oracle.
- `repaired-stale-reload.json.gz`: unchanged trusted digest-checked executable stale-artifact detection in a fresh process with empty cache and denied network.
- `source-input-manifest.json`: repaired tracked source/test/fixture/environment SHA-256 entries; report-only changes do not alter these inputs.
- `run_check.py`, `check-summary.json`: exact command/cwd/time/exit/raw output capture with overwrite refusal, and compact index. Precommit command HEAD is the handoff base; the manifest and tested source commit identify their changed inputs exactly.
- `repair-plan.md`: scope, root-cause assessment, constraints and review focus; final completion status belongs to STATUS and the canonical audit decision.

Activation in every shell: `source /workspace/.onboarding/atom-mlmm-m02-v2/activate.sh`. Direct probes use `PYTHONPATH=src:.`. No v1 worker/audit/reproducer/output, scientific contract, environment lock, upstream source or loading policy was overwritten.
