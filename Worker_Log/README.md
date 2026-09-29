# Worker logs and audit handoffs

This folder is the working history of the project. It lets a new agent continue one small task without repeating the previous session. The current code and the reviewed specification remain the basis for checking a result; a log is not a substitute for either.

Read [AGENTS.md](../AGENTS.md) first. Use the [worker template](../docs/project-0/templates/worker-log.md) and [audit template](../docs/project-0/templates/audit-log.md). The [assignment guide](../docs/project-0/guides/assigning-work.md) shows what the user can send to each agent.

## Folder and filename rules

Each milestone has a folder named `Milestone_XX`. Gate logs go in their parent milestone folder. Do not make a separate copy under `docs/`, and do not create an extra `Gate_XX/` folder. The gate page gives the exact location.

```text
Worker_Log/
  Milestone_00/                 # Design review; documentation maintenance
  Milestone_01/                 # G00 and G01
    Gate_01_v1_worker.md
    Gate_01_v1_audit.md
    Gate_01_v2_worker.md
    Gate_01_v2_audit.md
  Milestone_02/                 # G02 and G03
  Milestone_03/                 # G04, G05, G06 and G07
  Milestone_04/                 # G08
  Milestone_05/                 # G09 and G10
  Milestone_06/                 # G11
  Milestone_07/                 # G12
  Milestone_08/                 # G13
```

These names illustrate the format; they are not evidence that any gate has run. Actual logs exist only after an assignment. Folder README files explain what belongs there.

Use `Gate_01_vN_worker.md` and `Gate_01_vN_audit.md` for G01. Use `Milestone_01_vN_worker.md` and `Milestone_01_vN_audit.md` for the milestone's combined review. M00 follows the same milestone rule. Documentation upkeep uses `Documentation_vN_worker.md` and its audit partner under `Milestone_00`, as assigned in [the maintenance page](../docs/project-0/guides/documentation-maintenance.md); it does not accept M00.

Use exact case, underscores, two digits in milestone/gate numbers, and a positive integer for N. Do not use dates or model names instead of the attempt number. Keep model and date information inside the file.

## How to choose the attempt number

Check both worker and audit filenames for this task in the target branch and any known pending assignment. Take the highest numeric attempt and add one. The first is v1. Count numbers numerically: v10 comes after v9, not before v2. A partial, blocked, or failed attempt still uses its number.

One worker owns one task attempt. Do not run two agents on the same gate at the same time unless the user has assigned distinct attempts and separate code areas. A local filename check cannot prevent collisions across branches. Confirm the reservation through the user's assignment or shared branch before writing. Parallel work on different gates is allowed only when their dependencies and shared interfaces permit it.

The attempt number identifies the work and its snapshot, not just a bug-fix round. For example, v1 can implement `G01-T1`; v2 can repair it; v3 can implement `G01-T2`. Every log states that exact scope. The next worker reads the relevant accepted scope records as well as the most recent pending audit; it must not assume that the last filename summarizes all earlier work.

## Worker: what to record

A worker log must be useful even to a colleague who has not seen the conversation. State the goal, why the change was needed, what was already present, and what changed. Include:

| Field | What to record |
|---|---|
| Assignment | Milestone, gate, smaller task IDs, attempt number, requested scope, and work deliberately left out |
| Agent | Actual model label, such as Luna, Sol or Astra; exact version when exposed; reasoning setting |
| Documents | Repository-relative paths, relevant headings/requirement IDs, and revision or file hashes |
| Completion time | An actual ISO 8601 timestamp with timezone; UTC with `Z` is preferred |
| Code snapshot | Base commit, reviewed result commit, branch, and any remaining changed/untracked files |
| Changes | Files and functions changed, with a plain explanation of their purpose |
| Checks | Commands, working directory, environment, exit codes, results, and small useful output excerpts |
| Limits | What failed, was skipped, was not run, or still needs a scientific decision |
| Next handoff | Prior audit findings addressed, the next concrete step, and files the next agent should read |

Use `not exposed` for unavailable model/reasoning information. A user-declared label must be marked as user-declared; do not turn a nickname into a verified runtime identity. The reasoning field records a setting, not hidden internal reasoning. Record resource usage only when actual usage is exposed.

Prefer a commit that contains the implementation and its tests, followed by a separate log commit. This avoids putting a commit's own hash inside itself. The report may be added after the recorded code snapshot, provided the later commit changes only handoff material. In the audit, distinguish those report-only changes from code changes.

When commits are unavailable, save a reproducible patch against a known base or a SHA-256 manifest of all delivered files, including untracked files, and provide their actual contents. A hash alone identifies bytes but does not supply missing files. Do not claim a clean snapshot from `HEAD` if uncommitted changes affect the result. Never include secrets or restricted model weights in a patch.

Use short command summaries in the log and point to larger output files when needed. Small text evidence may live under `Worker_Log/Milestone_XX/evidence/Gate_YY_vN/`. Large trajectories and weights remain outside Git, with location, hash, and access requirements recorded. A chat-only attachment that disappears is not durable repository evidence.

## Auditor: verify, then leave directions

Read the selected worker log and the exact implementation snapshot. Confirm its scope, documents, inputs, and previous unresolved findings. Do not audit a newer checkout and silently claim to have audited the recorded one. Use a matching worktree or clearly report that the original snapshot could not be recovered.

Inspect the changed code and affected callers. Rerun the relevant checks, then challenge likely mistakes: wrong indices, units, omitted forces, stale state, unsupported assumptions, or a test that shares the implementation's mistake. Confirm that the change still fits the assigned specification. Keep the audit proportional; do not turn a small schema fix into a new protein benchmark.

Write the sibling `Gate_YY_vN_audit.md`, even when no issue is found. Include the auditor's model/reasoning metadata, timestamp, worker-log link, audited snapshot, checks actually run, and limitations. Use one verdict:

| Verdict | Meaning |
|---|---|
| `accepted_for_scope` | The named task and test setup passed the required independent checks |
| `changes_required` | There is a supported defect or missing required work; supply repair directions |
| `blocked` | Necessary code, files, hardware, or a decision is missing; no acceptance is claimed |

For each finding, use an ID such as `A01`, mark it **blocking**, **required**, or **optional**, and describe the observed versus required behavior. Name the file/function, evidence or reproduction command, smallest justified repair, regression test, and condition for closing the finding. A hypothesis is labeled as a hypothesis and needs a diagnostic step before a prescribed fix. An optional improvement must not block correct assigned work.

Auditors do not quietly change production code and then approve their own repair. A diagnostic probe is allowed if clearly recorded and kept separate. Implementation fixes belong in a new worker attempt, unless the user explicitly changes the assignment. A worker's self-review is useful but is not an independent audit.

## Next worker: continue, do not restart

Read the prior worker log and matching audit. Check that the current code matches or includes their recorded baseline. Resolve every finding by ID: fixed with evidence, already fixed in an identified change, or blocked with a reason. Do not blindly follow a repair that contradicts the reviewed specification; document the conflict and stop that part.

Keep accepted work. Make the smallest needed corrections to the existing code. Do not rewrite the whole gate to make it your own. Rerun the new regression test and relevant earlier checks, then write the next worker log with links to the predecessor pair.

## Partial work and honest status

Worker outcomes are `ready_for_audit`, `partial`, or `blocked`. `ready_for_audit` means only the assigned scope is ready, not that the full gate is complete. An auditor may accept a useful completed subset, but must name that subset and leave the remainder open.

A full gate is accepted only when its required tasks and applicable tests have been checked for the stated setup. Accepted parts from different attempts can be combined only if they are present together in the reviewed code and the relevant combined regression tests still pass. A newer accepted tiny fix does not erase an older unresolved finding or qualify a different hardware/model setup.

[STATUS.md](../docs/project-0/STATUS.md) is the progress summary. [The index](../docs/project-0/plan-index.json) carries the same summary in machine-readable form. Actual logs, snapshots, and evidence support acceptance; status labels alone do not. Ordinary partial attempts need no gate-status promotion.

## Preserve the history

Once submitted, worker and audit logs are not edited or replaced. Correct a wrong report through a new numbered worker/audit cycle that names the earlier error. Even a documentation-only correction can use a new attempt; state that no implementation changed. Before submission, an in-progress worker log may be updated, but it must say it is a draft and is not evidence of completion.

There is one final worker report and at most one final audit report per attempt. Do not fabricate an audit file, accepted result, model label, timestamp, test output, or missing predecessor. The goal is a reliable handoff, not a folder that merely looks complete.
