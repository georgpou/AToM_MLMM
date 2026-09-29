# Documentation upkeep: one small, reviewable task

**Task stem:** `Documentation`.\
**Folder:** `Worker_Log/Milestone_00/`.\
**Reports:** `Documentation_vN_worker.md` and `Documentation_vN_audit.md`.\
**Meaning:** documentation maintenance only; this does not approve M00 or any molecular gate.

## Why this task exists

The knowledgebase should let a worker find the goal, required reading, expected result, tests, and handoff location without rereading the entire project. Changing the workflow must not silently change the scientific definitions.

## Current requested work

Update AGENTS.md with the project purpose, hard constraints, deliverables, and the user's worker/auditor log scheme. Give every gate and milestone a clear reading route and log destination. Make the prose accessible while retaining precise equations, units, interface names, and test expectations.

Read the supplied documentation, the user's current instructions, and the affected shared specifications. Preserve scientific numbering and history. Do not install molecular packages or claim live repository changes as part of this task.

## Expected deliverables

A revised AGENTS.md; a clean documentation entry point; task-specific pages; worker and audit templates; matching milestone log folders; consistent status/index records; safe update instructions; and a real documentation worker log. A full package and a patch against the known supplied baseline should be checked before delivery.

## Checks

Check relative file links and heading links. Check the gate/milestone dependency graph, task IDs, task-to-test mapping, requirement coverage, and log naming. Compare existing scientific test definitions, units, equations, and historical archive with the baseline. Label any added check and explain the existing requirement it covers. Check that no numerical gate was accepted accidentally.

Exercise the delivery itself: apply the patch to the known baseline, compare the resulting tree with the revised tree, and check ZIP integrity. A missing or conflicting target must not be silently overwritten. Record the exact commands, outputs, and actual limitations in the worker log.

## Stop and hand off

Stop after this documentation scope. Give a separate auditor the worker log and snapshot. That agent should check the usability and consistency of the documents, not claim to have tested molecular software. Repairs use the next documentation attempt number and preserve submitted reports.
