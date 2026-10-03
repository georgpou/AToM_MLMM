# Independent R1 closure evidence

Exact reviewed source: detached `/workspace/AToM_MLMM-g05-review-v3` at `3124c6d275bf19a32ce364dfdb83b11115828ac5`; base `a7768e375476667139db374dc0091999263a37de`. Decision: [Gate_05_v2_audit.md](../../Gate_05_v2_audit.md). This is only prepared-loader integrity evidence, not quantum data or chemical qualification.

- `capture.py` records exact argv/cwd/HEAD, clean status before/after, timestamps, exit code, interpreter, selected environment values and complete output without replacing prior evidence.
- `focused.json`: independent ten-test provenance/metric run.
- `probe_binding.py`, `binding.json`, `binding-results.json`: independently authored synthetic fixture, 1 positive/29 negative controls, mutations/messages and record-access observations. Full synthetic fixture fields are preserved in the results for reproduction. Temporary probe files were removed; nothing was written to the scientific fixtures.
- `verify_snapshot.py`, `snapshot.json`, `snapshot-results.json`: all 270 source/input hashes, protected file comparisons, 48 exact M00-v3 comparisons, actual approval/audit binding and retained worker capture identities/summaries.
- `final-verification.json`: final read-only evidence/output checks and digest inventory.

All test/probe commands ran after sourcing `/workspace/atom-mlmm-g05-v2/activate.sh`, with `PYTHONPATH=src OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2`. Example replay from the immutable review cwd: `python probe_binding.py` using this directory's absolute script path. Scripts deliberately use exclusive output creation; replay needs a new unused evidence directory containing the script so prior artifacts cannot be overwritten. No broad model/analytic baseline, target quantum run or model-versus-quantum evaluation was executed by this reviewer.
