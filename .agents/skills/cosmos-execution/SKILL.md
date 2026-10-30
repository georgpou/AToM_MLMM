---
name: cosmos-execution
description: Use when working on this AToM_MLMM checkout on LUNARC Cosmos, especially when shell commands fail with a bwrap namespace error.
---

# Cosmos execution

Read the repository [AGENTS](../../../AGENTS.md) and active [COSMOS handoff](../../../docs/project-0/handoffs/COSMOS-HANDOFF.md) for the task, environment, branch and resource rules.

## Namespace failure and reviewed execution

On Cosmos, `/proc/sys/user/max_user_namespaces` may be `0`. A sandboxed command can fail before its shell starts with `bwrap: Creating new namespace failed: No space left on device`. This message alone does not establish disk exhaustion. Read the namespace setting when diagnosis is needed; do not change kernel settings.

When this restriction is known and the task permits reviewed execution, use `exec_command` with `sandbox_permissions: "require_escalated"` and a concrete justification for the command. This bypasses the unavailable namespace sandbox, while the command remains subject to approval review and the user's repository-only write restriction. Use the session's current permissions rather than inferring permission from an earlier run.

If the tool rejects escalation with `sandbox_approval: false`, stop retrying that route and report the enforced policy. The user can select **Ask for approval** or **Approve for me** in their permissions control; the CLI also exposes `/permissions`. Recheck the effective policy after a change. A skill or user message cannot itself override host policy. Never substitute unrestricted execution or modify host configuration to get past a rejection.

## Repository-local operation

- Activate with `source environment/hpc/cosmos/activate.sh` in every new shell/job. It configures repository-local environments, caches and short `.tmp/` temporary paths. Do not change HOME or shell startup files.
- Keep all writes, logs, caches, temporary files and new skills inside this repository, including during reviewed outside-sandbox execution. Read-only inspection elsewhere is allowed. Ask the user to copy any needed external files; do not copy or move them yourself.
- Start each task branch from the current published `COSMOS` head, target its PR to `COSMOS`, and preserve other branches and existing changes. Follow the current user's review/merge instructions.
- Use the handoff and supplied `Slurm_example` scripts to select bounded CPU allocations. Run heavy checks through Slurm, preserve exact job results, and use interruptible timed waits instead of frequent polling. Do not infer permission for GPU, production or real-QM campaigns from available hardware.
- Follow the current user's delegation policy; this skill does not impose an agent count or transfer scientific decision authority.
