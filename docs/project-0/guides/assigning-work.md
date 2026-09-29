# How to assign a small piece of work

The user controls the task size. An assignment needs a task path, a small scope, and the intended role: worker, auditor, or repair worker. The agent reads [AGENTS.md](../../../AGENTS.md) and follows the task page's reading route. It does not need the entire project history.

## First worker: Milestone 01, Gate 01

Use this after the required M00 review and the relevant G00 checks are recorded:

```text
Read AGENTS.md and docs/project-0/gates/G01-identity-partition-and-contracts.md.
Work only on G01-T1: stable atom identities and fixed selections.
Check the recorded prerequisites first. Do not implement the rest of G01.
Follow the failing-test -> implementation -> regression-check cycle.
Read any existing G01 worker/audit records in Worker_Log/Milestone_01/.
Write the next Gate_01_vN_worker.md there; use v1 only if none exists.
Stop at this task boundary and report the log path and any unfinished work.
```

An assignment can instead name one concrete test or repair within G01-T1. Record the narrower boundary in the log. A resource limit, when provided, is a limit on the assignment, not permission to weaken its correctness criteria.

## Auditor

```text
Read AGENTS.md and Worker_Log/Milestone_01/Gate_01_v1_worker.md.
Audit the exact code snapshot and G01-T1 scope recorded there.
Use the linked task/specification sections and rerun the relevant checks.
Do not edit production code or claim checks you could not run.
Write Worker_Log/Milestone_01/Gate_01_v1_audit.md.
Turn each supported finding into clear directions and a regression test
for the next worker. State what is accepted, blocked, or still required.
```

This example assumes v1 exists and has no final audit yet. For a later attempt, change both paths to its number. An audit can be done by the same model family in a separate session; it must still be an independent check, not the original worker's self-review.

## Repair worker

```text
Read AGENTS.md, the G01 task page, and both Gate_01_v1 logs in
Worker_Log/Milestone_01/.
Address the required audit findings on the existing code, not a rewrite.
Record each finding ID and its resolution. Stop if a direction conflicts
with the reviewed specification, and document the needed decision.
Use the next available attempt number, normally Gate_01_v2_worker.md.
Do not overwrite either v1 log. Finish with tests and a precise handoff.
```

## Milestone review

Point to the milestone page and ask for its **combined review**, not automatic implementation of all its gates. For M01 this checks that G00 and G01 work together on the declared setup. Use `Milestone_01_vN_worker.md` for the review preparation and the matching audit file for the independent decision.

M00 is different: it reviews the design before numerical implementation. It can be reviewed in smaller sections across attempts. Mark it accepted only after all its required design questions are resolved; a documentation rewrite alone does not accept it.

## What a new agent needs to read

Read the assigned task, its named specification sections, relevant earlier accepted results, and the latest unresolved audit. Read the whole shared architecture only when changing a shared boundary. Read the original archive or a research source only when the task depends on it. Do not repeat an expensive source search or installation merely to recreate context already captured in a trustworthy log.

The exact code and current specification still need checking. A saved log saves investigation; it does not remove the need to confirm that the same inputs and implementation are being used.
