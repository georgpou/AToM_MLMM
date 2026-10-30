# Cosmos environment installation - attempt 1 - worker

**Scope:** Install the existing exact CPU and separate AmberTools environments, keep all writes inside this repository, inspect supplied allocation examples, and provide reusable bounded Slurm scripts. No molecular run or GPU qualification.
**Outcome:** partial: CPU and AmberTools installation complete; all nine installation checks pass; full CPU regression remains red due to repository portability defects.
**Model/version:** GPT-6-based Codex per session instructions; exact model version not exposed.
**Reasoning setting:** not exposed.
**Updated:** 2026-10-30T14:07:21+01:00.
**Previous worker/audit:** No prior Cosmos_Environment attempt. Refresh v1/v2 logs and the user's Slurm examples are preserved; no independent audit is claimed.

## Snapshot and references

Base: hpc-atom-benchmark at 70ad284745617122627f217cd86d58237a2435ee. Pre-existing changes: refresh STATUS note, Worker_Log/Documentation refresh records, and Slurm_example/parameterize.sh plus atm_production.sh. They were not overwritten. No commit or push was made.

Read current AGENTS.md, relevant STATUS, environment/cloud-cpu README/installer/activation/validation/version checks/bundle, environment/hpc/run-guide.md and profile template, development/benchmark usage, Slurm examples, and narrowly selected Conda initialization lines from the user's shell files. The old root ATM_MLMM_Environment.md is absent; the current CPU guide is authoritative. Skills used: using-superpowers, systematic-debugging, test-driven-development and writing-plans; portability decisions follow the user's explicit repository-only installation scope and delegated script cleanup. Plan: docs/superpowers/plans/2026-10-30-cosmos-environment.md.

Primary references: LUNARC Cosmos system and GPU/execution guides, https://www.lunarc.lu.se/systems/cosmos/ and https://lunarc-documentation.readthedocs.io/en/latest/manual/manual_gpu/, accessed 2026-10-30; Conda envs_manager source and existing system Conda source. Source/package/model versions remain pinned in the checked-in CPU bundle. The system Conda 24.5.0 only parses MD5 explicit fragments; it is used solely to bootstrap the local Conda 26.7.2 tool client, not to interpret scientific SHA-256 locks.

## Changes and decisions

All environments, caches and temporary outputs are in .runtime/cosmos-cpu, ignored by Git. HOME is unchanged. CONDA_REGISTER_ENVS=false prevents global environment registration. The pinned Miniforge bootstrap was downloaded and hash-verified but not executed: header inspection showed forced global registration and a home .conda creation command. The local client instead uses the existing site Conda, with disabled registration and repository-local caches; its explicit inventory is recorded.

Added Cosmos settings/activation/install wrappers, CPU installation/validation jobs and an unsent GPU diagnostic. Account LU2025-2-123 and gpua100i came from supplied samples; lu48 came from actual sinfo output and Slurm preflight. Two cores/one task fits threaded Python. No sample script was edited. No GPU allocation or production was launched.

Made installer/main activation accept ATOM_MLMM_CA_BUNDLE, since Cosmos uses /etc/pki/tls/certs/ca-bundle.crt instead of the missing Ubuntu path. Added optional Conda backend so registration can be disabled. Updated bundle checksums only for the changed helpers; all scientific Conda/wheel locks, upstream archives, wheels and model assets remain unchanged. The documentation walker prunes .runtime before descending, so installed third-party Markdown is not treated as repository documentation. No scientific energy, force, unit, timestep, chemistry, model or acceptance definition changed.

## Checks and current execution

- `TMPDIR="$PWD/.runtime/tmp" python3 -m pytest -q tests/unit/test_cosmos_activation.py --basetemp="$PWD/.runtime/test-tmp"`: first expected failure showed the explicit certificate overridden by the Ubuntu path; after repair, 1 passed. Added a deliberate third-party broken-link regression: expected failure showed .runtime being scanned; after repair, 2 passed, zero skipped.
- `TMPDIR="$PWD/.runtime/tmp" python3 tools/check_docs.py --self-test`: exit 0, zero errors and eight self-tests passed before final handoff additions.
- `bash -n environment/hpc/cosmos/*.sh environment/hpc/cosmos/*.sbatch`: passed.
- `python3` inspection of Conda context under settings: register_envs=False.
- `sinfo -h -o '%P %l %a'`: lu48 default/up; gpua100i up.
- `sbatch --test-only environment/hpc/cosmos/install.sbatch`: accepted the account/resource request without submission.
- `sbatch --parsable environment/hpc/cosmos/install.sbatch`: submitted job 4063958, 2 CPUs/12 GB/1 hour; initially RUNNING on cn024. Exact commands, installer checks and CPU-suite outputs are retained under .runtime/cosmos-cpu/logs/.

## Limits and next action

Installation and full CPU results pending. No environment pass, GPU support, scientific gate/milestone acceptance or binding result is claimed. Compare relevant outside-file hashes with evidence/Cosmos_Environment_v1/outside-file-baseline.json, inspect final Slurm status and logs, finish strict validation evidence, record hashes and update STATUS. Independent review, if requested, would use Cosmos_Environment_v1_audit.md.

## Runtime path repair and retained first-run evidence

The installer completed with exit 0 and all nine checks passed. Main activation reported Python 3.11.16, NumPy 2.4.6 and OpenMM 8.6.1; separate Amber activation reported Python 3.11.16 and NumPy 1.26.4, and return to main succeeded. JSON activation evidence is retained alongside this log.

The first full CPU run showed failures/errors and was deliberately interrupted/cancelled rather than counted as a pass. A direct standard-library `multiprocessing.connection.Listener()` probe under the initial 81-character TMPDIR reproduced `OSError: AF_UNIX path too long`. A focused regression failed for exactly that reason before the repair. Moved only temporary files to the short repository-local `.tmp/` path and ignored it in Git; the real socket probe and all three focused tests then passed. No numerical or scientific criterion was relaxed. Initial failing progress remains in `.runtime/cosmos-cpu/logs/pytest-4063958.log`; cancellation prevented a complete final failure summary, so individual first-run failures are not independently all attributed to this cause.

Job 4063958 was CANCELLED after 00:19:48 (batch 0:15; maximum RSS 4,133,164 K), after successful installation. A precisely scoped SIGINT to its pytest process did not terminate the entire suite, so the owned job was cancelled explicitly. No unrelated job was signalled. Submitted validation-only retry 4064390, 2 CPUs/12 GB/30 minutes, using `sbatch --parsable environment/hpc/cosmos/validate.sbatch`. No packages are reinstalled by the retry. Its initial state is PENDING (Priority). Relevant outside-file hashes were checked after installation and remained unchanged.

## Final results and classification

Both environments are installed and usable at the exact prefixes in main-activation.json and amber-activation.json. All nine strict environment checks passed on cn024 in retry 4064390, with full results copied to environment-validation.json. Prefixes, local caches, and job outputs are under .runtime/cosmos-cpu; short temporary files are under .tmp. Both are inside this repository. Relevant home startup/config/registry files remained byte-identical to their recorded baseline. No outside directory was intentionally modified, no shell startup file was edited, and no GPU job or actual quantum reference calculation was launched.

Retry 4064390 completed with scheduler FAILED/1:0 after 00:09:50; its full CPU suite result was **654 passed, 50 failed, 12 errors, 57 deselected in 492.24 s**. All failure/error identities are in cpu-regression-summary.txt. Forty-nine failures and twelve setup errors are in test_joint_quantum_execution.py, test_quantum_interruptions.py and test_quantum_recovery.py. The first failure was separately reproduced in the allocation and reports missing /workspace; tracebacks identify hard-coded resource checks, including tools/resume_neutral_quantum.py:275. These are synthetic recovery/authorization/durability tests, not failed energy/force accuracy comparisons. The remaining failure, tests/workflow/test_engine_fresh_process.py:63, denies all reads under ROOT while the relocated attempt is now inside ROOT/.tmp; its guard rejects its own relocated metadata.json. These failures preclude a full CPU-suite pass and require a separate portable-path/recovery-test repair. No frozen authorization, budget ledger, quantum tool, engine source, numerical tolerance or test expectation was changed to bypass them.

The earlier socket-path defect was real and its focused regression was repaired, but it did not explain the later full-suite failures. The retry preserved them and identified the actual /workspace/read-denial causes. All three focused Cosmos setup tests pass. No additional installation or full-suite retry was launched after these causes were identified. Existing install/validate Slurm templates include the broad CPU suite and will return nonzero while these repository portability failures remain; the README records that limitation. The GPU diagnostic template remains unsubmitted and adds no GPU qualification.

Final handoff: installation scope is usable; broader cluster/workflow regression qualification remains incomplete. Use source environment/hpc/cosmos/activate.sh for main or activate-amber.sh for Amber Python. No commit, push or independent approval occurred. Remaining work is a narrowly scoped repository-portability repair, preserving the frozen scientific records and checking synthetic recovery behavior plus offline restart isolation. This assignment does not approve a scientific gate or establish binding accuracy. The status update records the mixed result without upgrading existing scientific/hardware holds.

**Finished:** 2026-10-30T14:40:24+01:00.

The final documentation check additionally exposed copied third-party Markdown inside the shortened .tmp test tree. Extended the existing generated-tree test to .tmp: expected failure observed, then pruned .tmp alongside .runtime before traversal. This does not suppress active project documentation. Final focused test count is four (the docs case is parametrized for both generated trees). No broad numerical rerun was needed for this documentation-only follow-up; the recorded full-suite red result remains unchanged.

Final documentation, all eight checker self-tests, four focused Cosmos regressions, Bash syntax and git diff --check pass. source-snapshot.sha256 identifies the complete tracked/untracked non-ignored source snapshot, excluding itself, against the recorded Git base. It includes preserved user files; ignored installed prefixes and temporary trees are identified separately by exact environment/client locks.
Final verification time: 2026-10-30T14:42:03+01:00.
