# Worker log template

Copy to the folder/stem named by the task; use the next `vN_worker.md`. This is a template, not evidence. Replace brackets with facts, and omit inapplicable subsections rather than filling empty tables. Follow [AGENTS.md](../../../AGENTS.md#logs-and-handoff).

# [Task name] - attempt [N] - worker

**Scope:** [task path/heading, milestone/gate/task IDs, requirements, exclusions].\
**Outcome:** [ready_for_audit / partial / blocked; whether the whole gate is in scope].\
**Model/version:** [actual label and source; exact version or not exposed].\
**Reasoning setting:** [exposed setting or not exposed; no private reasoning].\
**Finished:** [ISO 8601 timestamp with timezone].\
**Previous worker/audit:** [paths or none].

## Snapshot and references

[Base/result commits and branch; relevant dirty/untracked files. Without Git, provide a known base and delivered file manifest/patch. Identify any report-only changes. List documents actually read, their sections and revision/hash; external retrieval dates only when fetched. Record applicable profile, inputs and resource limits.]

## Changes and decisions

[What changed, why, files/functions affected, and any scientific/specification amendment with affected evidence, migration/rejection policy and review status.]

## Checks

| Requirement/test | Command; working directory | Profile/input | Exit code; result |
|---|---|---|---|
| [ID] | [actual command] | [exact setup] | [observed result or not run with reason] |

[Show the expected failing check and later passing result where applicable; link larger raw output. Distinguish failed, skipped, unrun and nonapplicable checks.]

## Findings and next handoff

[Account for prior finding IDs; identify outstanding issues and the smallest next step. Name the matching audit path and few necessary references. Gate/milestone scope needs combined-snapshot evidence, not just individual accepted attempts. No independent acceptance is claimed here.]
