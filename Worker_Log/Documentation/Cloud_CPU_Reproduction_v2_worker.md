# Branch-contained CPU environment reproduction - attempt 2 - worker

**Scope:** Complete the user's reproducible setup handoff: exact branch-contained
packages, both environments, fresh installation proof, remote retrieval,
Cloud startup and successor branch instructions. No scientific implementation,
gate acceptance or pretrained weights.\
**Outcome:** ready_for_audit for environment reproduction; all eight environment
checks passed. The documentation command retains two diagnosed existing errors.\
**Model/version:** GPT-6 / Codex; exact served version not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** 2026-10-01T15:12:27.821275+02:00.\
**Previous worker/audit:** [v1 provisional record](Cloud_CPU_Reproduction_v1_worker.md),
published during this task and preserved unchanged; no independent audit.

## Snapshot and references

Original task base `f4cdb59f380f89bb267a3a3f5532f61905593fb0`; artifact snapshot
`be26b7c25e9a30f67f6d3a884001084fa710bd8c`, published on
`m01-g00-cloud-environment-setup` and retrieved in a separate HTTPS clone.
This completion commit adds final evidence and clarifies documentation; it
does not change the scientific code or package versions/artifacts. Its exact
identity is the commit adding this report (`git log -1 --format=%H -- <report>`).
The complete final setup is identified by `environment/cloud-cpu/bundle.sha256`.

Read AGENTS.md, ATM_MLMM_Environment.md, ATM_MLMM_environment.yml,
AGENT_HANDOFF.md, the old/new installers, locks, evidence and worker-log
template; inspected both screenshots. Used cloud-environment-onboarding setup
and its onboarding reference, systematic debugging and verification instructions.
Profile: Linux x86_64, Python 3.11.16 in both environments, two CPU threads;
no model weights. The user requires every successor to inherit the setup branch
and never do project work on main. Remote main remains
`2d7bcc94f901738e39f536f16de84699d4e8d631`.

## Changes and decisions

Root cause: the old committed checksum list referred to 51 wheel files that
only existed in the original workspace. The historical installer had been
replayed on existing environments, leaving fresh-workspace reproduction untested.

`environment/cloud-cpu/` now contains all 51 actual wheels, both exact SHA-256
Conda locks, complete Python inventories, constraints, provenance, full pinned
upstream source archives, installer, activation helpers and validation. Source
archives match the commits used to build AToM, OpenMM-ML and openmmforcefields;
full sources/licenses and AToM's three reference datasets are supplied.

Prominent AGENTS.md, README.md and AGENT_HANDOFF.md links lead to the maintained
setup guide. The old installer/external tarball is retired as an entrypoint.
The fetch example uses a full refspec, including for single-branch clones.
The user's agreed main NumPy 2 / separate AmberTools NumPy 1 arrangement is
retained; original candidate YAML and scientific specifications are unchanged.

The Cloud entrypoint can fetch/archive the setup files from the side branch
when the initial checkout lacks them, without changing tracked files or main.
Cloud install_script and start_skill were successfully saved from cloud-install.sh
and CLOUD_START.md. Network, repository selection and credentials were preserved.
Saving a draft does not publish a Cloud filesystem snapshot.

## Checks

`/workspace/.onboarding/atom-mlmm-fresh-proof` was absent before installation
(`test ! -e ...`, exit 0). It received a freshly downloaded and SHA-256-verified
Miniforge bootstrap and its own package cache. The original installed
environments/cache were not reused. Installer escalation allowed Conda's normal
~/.conda registry; HOME and trust/checksum requirements were preserved.

| Check/command | Working directory/profile | Exit; observed result |
|---|---|---|
| `sha256sum -c wheels.sha256` before repair | historical committed evidence directory | 1; all 51 wheels missing, reproducing the reported failure |
| `bash -n` on install.sh/cloud-install.sh; compile new Python helpers | repository root | 0; syntax valid |
| `sha256sum -c bundle.sha256` | new setup directory and separate remote checkout | 0; all hashes match, 51 actual wheels, no LFS pointers |
| `ATOM_MLMM_SETUP_ROOT=/workspace/.onboarding/atom-mlmm-fresh-proof bash environment/cloud-cpu/install.sh` | repository root, empty prefix | 0; exact installs and complete environment checks finished |
| Main `check_versions.py <prefix> core` | fresh prefix | 0; Python 3.11.16, 156 exact Python distributions, 255 exact Conda URL/SHA-256 artifacts |
| Amber `check_versions.py <prefix> amber` | fresh prefix | 0; Python 3.11.16, 80 exact Python distributions, 201 exact Conda URL/SHA-256 artifacts |
| `python -m pip check` | main and separate Amber interpreters | 0 for both; no broken requirements |
| `python -m openmm.testInstallation` | main CPU | 0; Reference/CPU forces within tolerance, median difference 6.31602e-06 |
| `python <prefix>/smoke_cpu.py` | main CPU | 0; untrained MACE E/F, TorchANI descriptors/derivatives, ASE/OpenMM E/F agreement, PythonForce inside native ATMForce |
| `python <prefix>/smoke_prep.py` | isolated validation prep directory | 0; main OpenFF/GAFF 2.2.20 calls separate AmberTools; five-particle methane has finite CPU E/F |
| `python -m pytest -q tests/test_uwham.py` | pinned extracted AToM sources | 0; **1 test passed**, covering three reference datasets |
| `python tools/check_docs.py --self-test` | repository root | **1**; the same two existing missing anchors; all **8 self-tests pass** |
| Main → Amber → main activation; interpreter, NumPy, antechamber paths | fresh prefix | 0; main 2.4.6 → Amber 1.26.4 → main 2.4.6; Amber executable remains separate |
| Remote clone/fetch, child branch creation, ancestry and bundle verification | `/tmp/atom-mlmm-remote-proof` | 0; child starts at be26b7c, original main was clean and unchanged |
| Cloud entrypoint without setup files, explicit captured child status | separate clone detached at original base | 0; GitHub fetch/archive, exact replay and all eight environment checks passed |
| `git diff --check`; candidate/spec/tool/historical-evidence preservation | setup branch | 0; no scientific changes |

Fresh-run outputs are in [v1 evidence](evidence/Cloud_CPU_Reproduction_v1/),
including fresh-validation.json, individual logs and fresh-install.log.gz.
Remote/Cloud replay outputs are in [v2 evidence](evidence/Cloud_CPU_Reproduction_v2/),
including cloud-entrypoint-validation.json, complete replay logs, explicit
status and remote bundle verification. Gzip preserves exact raw output bytes.

The first clone/replay driver reported exit 1 after its captured installer
reported exit 0 and all environment checks passed. Its complete log is retained
as cloud-entrypoint-first.log.gz. A separate run explicitly captured entrypoint
status 0 and repeated all functional checks successfully, without changing
versions. This does not relabel the first driver status as a pass. Replay
emitted an existing OpenCL symlink warning; inventories and CPU workflows passed.

The installer still executes/prints/records documentation failures; its
environment-only mode bases install status on eight environment checks. Strict
validate.py exits 1 for docs errors too. No scientific assertion, tolerance or
test was changed to obtain a pass.

## Findings and next handoff

The missing-artifact blocker is resolved by branch-contained files and verified
remote retrieval. No dependency, credential or network blocker remains for this
CPU setup on the tested Cloud host. No separate new Cloud task or other machine
was launched; fresh-prefix installation and remote-clone retrieval were tested
on this Linux host.

The source-register anchor scientific-amendment-source-checks is still missing,
referenced by ATM_MLMM_Environment.md and historical M00 Documentation_v4_worker.md.
Repair that repository defect in a separate documented task. Historical reports
and scientific specifications remain unchanged here.

Successors fetch the latest setup branch, create an unused milestone/gate/task
child from its tip, read the handoff and setup guide, run the installer and
activate main. Relevant M00 review is the first unfinished prerequisite before
G00/G01 acceptance. Pretrained loading, GPU execution and additional backend
qualification remain unrun; no weights were downloaded. Suggested independent
audit: Cloud_CPU_Reproduction_v2_audit.md. No independent acceptance is claimed.
