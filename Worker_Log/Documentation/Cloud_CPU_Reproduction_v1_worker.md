# Branch-contained CPU environment reproduction - attempt 1 - worker

**Scope:** Repair the environment handoff so another agent can reproduce both
environments using this side branch alone. Dependency installation and setup
documentation only; no scientific gate implementation or model weights.\
**Outcome:** partial; fresh-install verification in progress.\
**Model/version:** GPT-6 / Codex; exact served version not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** not yet complete.\
**Previous worker/audit:** Cloud_CPU_Setup_v2_worker.md,
Cloud_CPU_Handoff_v1_worker.md, Cloud_CPU_Publish_v1_worker.md; no independent
audit of this reproduction task.

## Snapshot and references

Base `f4cdb59f380f89bb267a3a3f5532f61905593fb0`, branch
`m01-g00-cloud-environment-setup`. User explicitly requires successors to create
branches from this setup lineage and forbids work on `main`. Initial checkout
was clean. Remote main remains `2d7bcc94f901738e39f536f16de84699d4e8d631`.

Read AGENTS.md, ATM_MLMM_Environment.md, ATM_MLMM_environment.yml,
AGENT_HANDOFF.md, existing setup helpers/locks/evidence and the worker-log
template. Inspected both user screenshots. Used cloud-environment-onboarding
setup/reference instructions and systematic debugging. Linux x86_64 CPU;
two computational threads; no weights downloaded.

## Changes and decisions

Root cause reproduced: running `sha256sum -c wheels.sha256` in the committed
historical setup evidence directory exits 1 because all 51 wheel artifacts are
absent. The former successful installer tested an existing local installation,
not reproduction from an empty prefix. Historical reports remain unchanged.

Added `environment/cloud-cpu/` with those exact 51 wheels, both explicit Conda
SHA-256 locks, version inventories, provenance, full pinned source archives,
installer, activation and validation helpers. The new installer does not solve
or substitute packages. It records documentation failures separately from
installation checks and preserves all raw statuses. The user-agreed main
NumPy 2 / separate AmberTools NumPy 1 split is retained.

## Checks

Bundle checksums and shell/Python syntax checks passed. Fresh-prefix installation
and full readiness checks are in progress; no fresh-install success is claimed
by this provisional record.

## Findings and next handoff

Keep M00/G00 acceptance separate from installation. Preserve/report the existing
documentation-anchor failures and no-weights instruction. Final check evidence,
snapshot and remote publication will be recorded after verification.
