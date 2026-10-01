# Audit log template

Use for an actual independent review of the worker's recorded snapshot. Match its folder/stem and attempt number. This template is not evidence.

# [Task] — v[N] audit

**Reviewed worker/snapshot:** [log, branch and commit].\
**Scope/profile:** [task, gate or milestone combined scope].\
**Reviewer and finished time:** [identity; timestamp with timezone].\
**Verdict:** [accepted_for_scope / changes_required / blocked].

## Evidence

[Relevant requirements and independently rerun commands, inputs, exit codes and outcomes. Distinguish available CPU/model/GPU evidence.]

## Findings

| Finding and importance | Evidence/location | Required repair and closure check |
|---|---|---|
| [actual issue] | [reproducer] | [smallest correct change/test] |

## Decision and handoff

[Exactly what is accepted or remains unqualified; next action. A small-task result does not accept a whole gate. Update STATUS with the real reviewed scope.]
