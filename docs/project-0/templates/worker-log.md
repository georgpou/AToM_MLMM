# Worker log template

Use the folder/stem in the assigned gate and an unused attempt number. Keep one record for the task; omit inapplicable fields. This template is not evidence.

# [Task] — v[N] worker

**Scope:** [milestone/gate/task and tested profile].\
**Outcome:** [ready_for_audit / partial / blocked].\
**Finished:** [timestamp with timezone].\
**Snapshot:** [branch, base commit, tested code commit; identify report-only changes].

## Changes

[What changed and why; relevant files/specification decisions. Scientific changes include affected requirements, tests and review status.]

## Verification

| Check | Command and working directory | Profile/input identity | Exit and observed result |
|---|---|---|---|
| [requirement/test] | [exact command] | [environment/fixture/model] | [actual outcome] |

[For a bugfix, record the intended failing check and subsequent pass. Link larger output when needed. Skipped/unrun checks remain explicit.]

## Handoff

[Remaining issues, limitations and next action. Update STATUS. Name the sibling audit only if an independent review is assigned/performed; self-checks do not approve a gate or milestone.]
