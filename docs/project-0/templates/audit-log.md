# Audit log template

Write the sibling `vN_audit.md` for the submitted worker attempt. Follow [AGENTS.md](../../../AGENTS.md#logs-and-handoff). Do not create an audit for a self-check or an unperformed review. Omit inapplicable subsections.

# [Task name] - attempt [N] - audit

**Worker log:** [path].\
**Audited scope:** [task/requirement IDs; full gate or milestone only if explicitly covered].\
**Snapshot:** [exact worker result commit or delivered manifest; distinguish later report-only changes].\
**Model/version; reasoning setting:** [actual exposed metadata or not exposed].\
**Finished:** [ISO 8601 timestamp with timezone].\
**Verdict:** [accepted_for_scope / changes_required / blocked].

## Independent checks

[Relevant specification paths/sections and revisions; inspected changes/callers; prior unresolved findings; exact commands, working directory, environment/input/profile, exit codes and observations. Link raw evidence. State what was not run and why. A newer checkout is not automatically the recorded snapshot.]

## Findings

For each finding record **A01**, **blocking / required / optional**, observed versus expected behavior, file/function, evidence or reproduction, smallest justified repair, regression test, and closure condition. Label unconfirmed explanations as hypotheses requiring a diagnostic. Optional improvements do not block otherwise correct work.

## Accepted scope and next action

[State precisely what is accepted, what remains, the next worker-attempt path, and any warranted STATUS.md update. Check gate coverage and combined milestone criteria only when in scope; identify profiles and earlier reviews. Do not infer whole-gate acceptance from one task, or model/GPU support from analytic CPU results.]
