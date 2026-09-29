# Documentation: start with the assigned task

Read [AGENTS.md](../AGENTS.md) for the project goal, hard rules, and worker/auditor responsibilities. Then use the path the user gave you. The task page tells you what to read, why the work matters, what to produce, and where to write the log.

## Pick the right entry point

| You were asked to... | Start here |
|---|---|
| Understand the project or find a task | [Project 0 roadmap](project-0/README.md) |
| Implement a gate or one part of it | [Gate index](project-0/gates/README.md), then that gate's **Read for this task** section |
| Review a whole milestone | [Milestone index](project-0/milestones/README.md) |
| Audit or repair earlier work | The assigned file under [Worker_Log](../Worker_Log/README.md), then its linked task and specification |
| Prepare an agent assignment | [Assignment examples](project-0/guides/assigning-work.md) |
| Change shared behavior | [Specifications](project-0/specs/README.md) and [change template](project-0/templates/spec-change.md) |

## How the folders connect

`milestones/` explains the larger results. `gates/` breaks each result into work and tests. `specs/` holds the shared scientific definitions and inputs/outputs; it is not duplicated inside every gate. `reference/` holds supporting explanations, source links, and the unchanged historical plan. `templates/` provides forms for assignments and reports. [Worker_Log](../Worker_Log/README.md) holds the actual work and audit history, outside the knowledgebase.

A **gate** is a testable piece of work. A **milestone** checks that related gate results fit together. A **task** is a smaller part a worker can finish in one assignment. An **attempt** is one numbered session on that task/gate; it can be partial or blocked.

## Example: Milestone 01, Gate 01

Read [M01](project-0/milestones/M01-reproducible-foundation.md) for the goal, then [G01](project-0/gates/G01-identity-partition-and-contracts.md) for the assigned work. Follow G01's named specification sections. Check the prerequisites and previous logs in [Milestone_01](../Worker_Log/Milestone_01/README.md). Work only on the requested part, such as `G01-T1`, and write the next `Gate_01_vN_worker.md`.

Do not read all reference material or implement the whole milestone just because you were given its path. The point of this structure is to make small, reviewable progress.

## What is authoritative

The user's current explicit scope and approved decisions control the assignment. Reviewed specifications define required behavior. Gate pages define work and checks. Logs record what actually happened; they do not silently change a specification. Historical notes explain origins and may contain superseded assumptions. [STATUS.md](project-0/STATUS.md) and [plan-index.json](project-0/plan-index.json) summarize evidence rather than replacing it.

This delivery updates documentation and handoff rules. It does not supply an implemented or numerically qualified simulation platform, and it does not describe any uninspected changes in the live repository.
