# G10 v8 worker evidence

- Contract: `assignment.md` (SHA-256 `d55ed1413ae37d1036b29d0c9ad94daece195535727224c7ac322436ce3a2866`); initial Luna capacity-selection failure and same-model retry: `capacity-retry.txt`.
- Base `263a4199a8835b9eef59fc8e33c463cb6ddd669d`; frozen code/test commit `3f93efa079ae36514d86d34f9dbc263722bcd1cd`; final audit pending.
- Public RED finished 2026-10-06 15:05:25 UTC, exit 1: `public-clock-red.log` (SHA-256 `b159cf9c49a7da20082dc825e3b1da1ac9a5e355b77423b3249e47947156c577`). Two coherent public histories each loaded 3 workers, evaluated 25 times, stepped 3 times, and published a changed tree.
- Focused GREEN finished 2026-10-06 15:10:47 UTC, exit 0: `clock-focused-green-final.log` (SHA-256 `35a4c913317c59dfcf8ebe3cbe210627dd7dbdae96333420793afa6ce3bb5c32`); 7 passed, 58 deselected, 8.11 s.
- Fresh exact v2 pilots finished 2026-10-06 15:17:45 UTC, exit 0: `v2-pilots.log` (SHA-256 `e797d9151e979c682616657302ab30ef00abe2e7de01e22bc7c54a850e07b2fa`); 2 passed in 235.94 s, no skip text.
- Complete pilot artifacts: `/workspace/G10_v8_artifacts/v8-attempt-001`; 958 files / 87 MiB. `pilot-artifact-sha256.txt` contains all hashes (SHA-256 `1b48eeae1b69d4e615f8dcb66aa3d98f50f5f8bc3a854f5d29a15cd22361b952`).
- Focused command: `python -m pytest -s -q tests/workflow/test_persistent_exchange.py -k 'multistate_public_backward_clocks_reject_inertly or multistate_clock_'`; pilot command: `G10_PILOT_EVIDENCE=/workspace/G10_v8_artifacts G10_PILOT_RUN_ID=v8-attempt-001 python -m pytest -q tests/workflow/test_multistate_exchange_pilots.py`.
- One final `python -m pytest -q` finished 2026-10-06 15:39 UTC on frozen code/tests: exit 0, 631 passed, no skip text, 1238.59 s. Uncompressed output is `full-cpu-suite.log`, SHA-256 `55747b697c1fae7558058c2d2938dd717b49fd2dc57b6bd5c2f7f8f7f54dfd14`; byte-identical copy: `/workspace/g10-v8-raw-inputs/full-cpu-suite.log`.
- Frozen 105-file source/test manifest: `/workspace/g10-v8-suite-frozen-source.json` (SHA-256 `57889411d7df973e8fe1cafc30902f7bd66ba6b7958aec9b9032bb7896a4a48b`).
- Every scientific command sourced `/workspace/m05-cpu-setup-v2/activate.sh` and exported `OPENBLAS_NUM_THREADS=2`, `PYTHONPATH="$PWD/src"`; runs were serial CPU2/8 GiB.
- `python tools/check_docs.py --self-test`: exit 0, 234 Markdown files, 1552 local links, 0 errors; raw output `docs-selftest.log` (SHA-256 `3b32801867834bfd6794634e7b574aec0b1650b5002d3abba32401dbd55c11b8`). `git diff --check` exits 0.
- Base-to-code diff is limited to `src/atm_mlmm/exchange_journal.py` and `tests/workflow/test_persistent_exchange.py`; no protected fixture/model/package/reference paths changed.
- Raw logs remain beside deterministic gzip copies. `sha256-manifest.txt` covers the assignment, capacity retry, raw/compressed logs, pilot artifact hash list, and external byte-identical suite log (SHA-256 `6774c6453263e137800541ec142436912d03db32bb4b15e09decd740d8906a08`).
- Report: `../../Gate_10_v8_worker.md`. Only one combined Sol 6.1/max audit remains; no worker acceptance is claimed.
