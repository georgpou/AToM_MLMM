# Audit log template

Copy this template beside the selected worker log, with the same task and attempt number: `Gate_YY_vN_audit.md`. Do not create a second audit for the same attempt or overwrite an existing one. This template is not audit evidence.

# [Task name] - attempt [N] - audit

## Audit at a glance

| Field | Actual value |
|---|---|
| Worker log | [Exact repository-relative path] |
| Task page and smaller scope | [Document heading and task IDs] |
| Auditor model | [Luna, Sol, Astra, or actual reported label; identify source] |
| Exact model version | [Reported value or not exposed] |
| Reasoning setting | [Reported setting or not exposed] |
| Finished at | [Actual ISO 8601 timestamp with timezone] |
| Independence | [Separate audit session; disclose any involvement in implementation] |
| Audited code snapshot | [Commit, or base plus patch/full-file manifest] |
| Snapshot matches worker report? | [Yes, or exact discrepancy and its effect] |
| Verdict | [accepted_for_scope / changes_required / blocked] |
| Accepted scope and setup | [Exact task/profile, or none] |
| Whole gate accepted? | [No, or yes with complete gate/test evidence references] |

## 1. What I checked against

[Assigned behavior, relevant requirement IDs, specification paths/headings/revisions, earlier open findings, and intended results. Do not infer the specification from the code under review.]

## 2. Checks actually performed

| Check | Command / inspection and working directory | Inputs / setup | Exit code | Observed result and evidence |
|---|---|---|---|---|
| [Check] | [Actual command or precise code inspection] | [Actual setup] | [Actual code or not applicable] | [Result, not an expectation] |

[Include relevant reruns, independent spot checks, likely edge cases, and checks not run with reasons. A worker's output can be cited as worker evidence, not relabeled as your own execution.]

## 3. Findings and directions for the next worker

### A01 - [Specific issue]

**Priority:** [blocking / required / optional]\
**Location:** [File, function, and stable code context; line numbers alone are not enough]\
**Requirement:** [ID and reference section]

**Observed:** [What actually happens and supporting evidence. Label an untested hypothesis.]\
**Required:** [What the specification requires instead.]\
**Why it matters:** [Concrete consequence.]

**Next worker should:** [Smallest justified repair. For a hypothesis, first specify the diagnostic that decides whether a repair is needed. Do not ask for unrelated rewrites.]\
**Regression test:** [Test name/path and exact behavior it must assert.]\
**Close this finding when:** [Observable acceptance condition, including affected earlier tests.]\
**Preserve:** [Existing behavior or files that must remain unchanged.]

[Repeat for each finding. When there are no findings, say so explicitly and still state audit limits. Do not leave an empty A01 section.]

## 4. Earlier findings

[State which earlier findings are closed, still open, or outside this audit's scope, with reasons. Acceptance of a small repair does not silently close the rest of a gate.]

## 5. Decision and next handoff

[Explain the verdict for the exact assigned scope. Name the next worker-log filename, baseline snapshot, findings to address, required tests, and remaining limitations. Accept a whole gate only when all applicable tasks and combined checks support it. State the justified status update; do not claim a review qualifies untested models or hardware.]
