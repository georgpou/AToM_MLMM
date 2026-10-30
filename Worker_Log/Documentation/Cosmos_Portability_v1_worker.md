# Cosmos portability prerequisite — v1 worker

**Scope:** Bounded COSMOS CPU software-portability prerequisite; no scientific gate or milestone acceptance.  \
**Outcome:** ready_for_audit.  \
**Finished:** 2026-10-30, Europe/Stockholm (CET, UTC+01).  \
**Worker:** Luna 6, xhigh.  \
**Snapshot:** branch `cosmos/portability-repair`, base `4d5b266d982e5e72596e475712eafbbe110e001f`. The tested implementation/accessory snapshot is recorded in `.runtime/cosmos-cpu/portability-repair/source-freeze-sha256.txt`; report-only additions are listed separately in `.runtime/cosmos-cpu/portability-repair/delivered-files-sha256.txt`. No commit was created because local `user.name` and `user.email` are unset; root will review and publish.

## Changes

- `tools/resume_neutral_quantum.py` now measures disk free space on the nearest existing directory for the actual attempt/output path. Every measurement call supplies that path. The cgroup-v2 reader resolves `/proc/self/cgroup` through the cgroup mount root, verifies the Slurm `job_<id>` boundary, and collects `memory.max`, current usage, pressure inputs and OOM events from the process leaf through the job scope only. It selects the tightest finite inherited limit and records process/job/selected-scope provenance. Unsupported or malformed layouts reject with a diagnostic.
- The existing pressure formula, numeric thresholds, wall and memory authorization, ledger, frozen two-thread quantum limits and physical definitions are unchanged. There is no cgroup-v1 pressure implementation or host-RAM fallback. Read-only check-resume does not request cgroup execution measurements.
- `tests/workflow/test_engine_fresh_process.py` retains the complete original checkout denial. It permits the exact resolved relocated bundle and resolved `sys.prefix` required for installed dependency metadata (`opt_einsum-3.4.0.dist-info/METADATA`); original source, fixtures, configs, old run/cache roots, other `.runtime` paths, prefix-name siblings and network access remain denied. The test asserts the bundled workflow source identity and keeps runtime temp/cache output within the relocated bundle.
- Root-provided `AGENTS.md` skill discovery and `.agents/skills/cosmos-execution/SKILL.md` are preserved and included in the source snapshot.

## Verification

All Slurm timestamps below use Europe/Stockholm (CET, UTC+01); allocations used one task, 8 CPUs, 12 GiB and a 30-minute limit. The existing two-thread quantum approval/test cap was retained. No speedup is inferred from the allocation size.

| Check | Command and working directory | Profile/input identity | Exit and observed result |
|---|---|---|---|
| Pre-fix baseline, job 4065600 | Four-file recovery/workflow pytest batch; repository root | COSMOS CPU environment, synthetic records | Failed as expected: `/workspace` absent in disk measurement; 50 failed, 16 passed, 12 errors in 70.32s. Log: `.runtime/cosmos-cpu/logs/portability-baseline-pytest-4065600.log`. |
| Intended filesystem regression red, job 4065848 | `test_measurements_uses_existing_attempt_filesystem_for_disk_headroom` | Target output is a not-yet-created attempt directory | Observed intended red against pre-fix helper: `TypeError: measurements() got an unexpected keyword argument 'filesystem_path'`. The offline worker also identified the blocked installed `opt_einsum` METADATA path. |
| Cgroup scope regression red, job 4066647 | Focused cgroup-v2 and G07 guard cases | Synthetic job/step/leaf hierarchies | 9 failed in 4.71s on the missing v2 resolver, read-only check-resume execution-resource call, and ancestor-scope pressure/OOM assertions. |
| Focused implementation iteration, job 4066708 | Four-file focused batch | COSMOS CPU, synthetic/recovery fixtures | 86 passed, 2 failed in 244.02s. Failures exposed loss of the frozen 24-hour check-resume wall calculation and OpenMM temp output under denied repository `.tmp`; both were repaired while keeping one shared joint policy. |
| Focused green, job 4066756 | `python -m pytest -q tests/unit/test_joint_quantum_execution.py tests/unit/test_quantum_interruptions.py tests/unit/test_quantum_recovery.py tests/workflow/test_engine_fresh_process.py --basetemp="${TMPDIR}/pytest-focused-${SLURM_JOB_ID}"` | COSMOS CPU, synthetic fixtures; no real QM | COMPLETED 0:0 in 4:08 scheduler elapsed; **88 passed in 236.76s**. Cgroup diagnostic and filesystem durability probe exited 0. `git diff --check` also passed before the full-suite run. |
| Full available CPU suite, job 4066801 | `python -m pytest -m 'not gpu and not model_assets and not slow' -q --basetemp="${TMPDIR}/pytest-${SLURM_JOB_ID}"` | COSMOS CPU profile | COMPLETED 0:0 in 11:58 scheduler elapsed; **727 passed, 57 deselected in 706.07s**, no failures/errors. Full output: `.runtime/cosmos-cpu/logs/portability-full-pytest-4066801.log`. |
| Documentation/skill validation | `python tools/check_docs.py --self-test`; main Python running `quick_validate.py` on `.agents/skills/cosmos-execution/SKILL.md` | Repository docs and root-provided skill | Results recorded in the task report and compact evidence file. |

The observed runtime was cgroup v2 at `/sys/fs/cgroup`; `/proc/self/cgroup` resolved to `/system.slice/slurmstepd.scope/job_<id>/step_batch/user/task_0`. In job 4066284, the task leaf was unlimited, while the user and job ancestors carried the 12 GiB `memory.max`; the unrelated `slurmstepd.scope` and host ancestors showed much larger totals. Job 4066756 reproduced the same layout and 8-CPU cpuset. The repair therefore reads each applicable scope through the job boundary and does not use the system ancestors. File fsync, staged-directory fsync, rename, parent-directory fsync and cleanup-directory fsync all succeeded on the tested filesystem.

## Handoff

The full CPU suite is software regression evidence only. Actual QM resource admission, real executions, GPU qualification and scientific gate acceptance remain pending. Unsupported cgroup-v1 layouts reject; this task did not add v1 pressure semantics. Root should perform the independent review and authenticated publication. See `Worker_Log/Documentation/evidence/Cosmos_Portability_v1/evidence.md` and `.runtime/cosmos-cpu/portability-repair/task-1-report.md`. Self-checking here is not independent approval.
