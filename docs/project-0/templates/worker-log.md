# Worker log template

Copy this template to the task's `Worker_Log/Milestone_XX/` folder. Name it `Gate_YY_vN_worker.md` or use the task stem stated on the assigned page. Replace every instruction below with an actual value. Use `not exposed`, `not run`, or `not applicable` with a reason where appropriate. This template is not a completed log.

# [Task name] - attempt [N] - worker

## Handoff at a glance

| Field | Actual value |
|---|---|
| Task page and section | [Repository-relative Markdown path and heading] |
| Milestone / gate / smaller task IDs | [For example M01 / G01 / G01-T1] |
| Attempt | [Positive integer] |
| Assigned scope | [What this session was asked to finish] |
| Outcome | [ready_for_audit / partial / blocked] |
| Whole gate complete? | [No, or complete work claimed and awaiting full-gate audit] |
| Model | [Luna, Sol, Astra, or actual reported label; identify source of label] |
| Exact model version | [Reported value or not exposed] |
| Reasoning setting | [Reported setting or not exposed; no private reasoning transcript] |
| Finished at | [Actual ISO 8601 timestamp with timezone] |
| Previous worker / audit | [Paths, or none: first attempt] |
| Assigned budget and usage | [Actual limits; usage only if available, otherwise not exposed] |

## 1. What I was trying to achieve

[Explain the requested result and why it matters. State what was outside this session's scope. Name relevant requirement IDs.]

## 2. Starting point and exact result snapshot

[Repository/branch, base commit, implementation-result commit, and any uncommitted or untracked files that affect the result. Explain later report-only commits. Without Git, identify the base and delivered patch or full file manifest. Provide actual files, not only hashes.]

## 3. Documents used

| Document path or source | Heading / requirement | Revision or hash | How it was used |
|---|---|---|---|
| [Reference] | [Relevant section] | [Actual identity] | [Decision or expected behavior] |

[For external sources, record URL and retrieval date only when actually consulted. Do not list unread references.]

## 4. What changed

| File / function | Change | Why it was needed |
|---|---|---|
| [Actual path] | [Specific change] | [Reason] |

[Explain any important choice that affects review, without an internal reasoning transcript.]

## 5. Test evidence

| Test or check | Command and working directory | Environment / inputs | Exit code | Outcome and observed result |
|---|---|---|---|---|
| [Name / ID] | [Exact command] | [Actual setup] | [Actual code, or not run] | [passed / failed / skipped / not_run, with measurement or reason] |

[For new behavior, show the intended failing test and the later passing result. Name regression tests. Link raw output or small evidence files. Explain why a check was not applicable rather than treating it as a pass.]

## 6. Response to the previous audit

| Finding ID | Action | Evidence | Remaining issue |
|---|---|---|---|
| [A01, or none for first attempt] | [Fix, diagnostic, or reason blocked] | [Test / file] | [Open item or none] |

## 7. What remains and what the auditor should challenge

[Known limits, missing checks, risks, specification conflicts, and any partial work. Distinguish a code failure from missing resources. List unresolved findings even when they came from an older attempt.]

## 8. Next handoff

[Exact worker log to audit, matching audit filename, tested snapshot, smallest next action, and the few files the next agent needs. State whether a status change is justified. Do not declare independent acceptance.]
