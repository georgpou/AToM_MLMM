# Engine handoff orchestration policy — v1 worker

**Scope:** user's explicit serial delegation and completed-audit instructions.\
**Outcome:** documentation updated; no engine/scientific changes or new acceptance.\
**Prepared:** 2026-10-05 UTC.\
**Base:** `cloud-engine-continuation` at `29af52c960152acaf840755543681fe53f0da548`.

The [current handoff](../../docs/project-0/handoffs/CLOUD-ENGINE-CONTINUATION.md)
now requires a chat orchestrator, detailed `gpt-6-luna`/max implementation and
repair assignments, and `gpt-6.1-sol`/max audits. At most one side agent may run;
workers/auditors cannot spawn agents. Audit only completed task batches, wait for
the auditor's full report, then repair serially and re-audit until the declared
coding, physics/chemistry and mathematical scope receives explicit GREEN.
Required design review is a separate completed design task. Existing physical
blockers cannot be waived or relabeled as accepted by a scoped code audit.

Verification from the repository root: `python tools/check_docs.py --self-test`
passed with zero local errors and all eight self-tests; `git diff --check` passed.
No numerical tests were repeated for an instruction-only edit. No independent
audit was performed for this documentation task; prior cleanup acceptance remains
tied to its reviewed snapshot. The shareable Markdown copy uses exact-commit GitHub
links so references work when the file is handed to a new agent outside the repo.
