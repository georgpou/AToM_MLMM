# COSMOS portability task 1 evidence

All scheduler wall times use Europe/Stockholm (CET, UTC+01). The full CPU suite ran on cn135 with one task, 8 allocated CPUs and 12 GiB for 11:58; 727 tests passed and 57 were deselected. The cgroup diagnostic observed cgroup v2 and the actual Slurm task path; the focused storage probe completed all file/directory fsync and rename operations successfully.

## Baseline and regression evidence

- Job 4065600: `.runtime/cosmos-cpu/logs/portability-baseline-pytest-4065600.log` records the original `/workspace` `FileNotFoundError` and baseline counts (50 failed, 16 passed, 12 errors).
- Job 4065848: `.runtime/cosmos-cpu/logs/portability-red-pytest-4065848.log` records the intended red: `measurements()` did not accept `filesystem_path`. It also records denial of installed dependency metadata at `.runtime/cosmos-cpu/env/lib/python3.11/site-packages/opt_einsum-3.4.0.dist-info/METADATA`.
- Job 4066647: `.runtime/cosmos-cpu/logs/portability-cgroup-red-pytest-4066647.log` records nine intended failures before the cgroup-v2 resolver and read-only check-resume integration.
- Job 4066708: `.runtime/cosmos-cpu/logs/portability-focused-pytest-4066708.log` records the two intermediate regressions (86 passed, 2 failed), both corrected in the final focused snapshot.

## Green runs

- Focused green job 4066756: `.runtime/cosmos-cpu/logs/portability-focused-pytest-4066756.log` and `.runtime/cosmos-cpu/logs/portability-focused-4066756.out`; **88 passed in 236.76s**, job completed 0:0.
- Full CPU job 4066801: `.runtime/cosmos-cpu/logs/portability-full-pytest-4066801.log`; **727 passed, 57 deselected in 706.07s**, job completed 0:0.
- Eight tested source/accessory files and their SHA-256 values are in `.runtime/cosmos-cpu/portability-repair/source-freeze-sha256.txt` and were all verified after the full run.

The full run does not qualify actual quantum calculations, scientific acceptance or GPU execution. No cgroup-v1 implementation, threshold change, authorization change, environment installation or dependency change was made.
