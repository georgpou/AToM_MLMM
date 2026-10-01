# Next-agent audit handout - attempt 1 - worker

**Scope:** Create the requested handout files for a successor's independent
environment/baseline audit on a new child of the setup branch. No audit verdict,
dependency repair, scientific implementation or gate acceptance.\
**Outcome:** ready_for_audit for the documentation handoff.\
**Model/version:** GPT-6 / Codex; exact served version not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** 2026-10-01T15:49:08.696499+02:00.\
**Previous worker/audit:** Cloud_CPU_Reproduction_v2_worker.md; no independent
audit of its environment delivery has yet been performed.

## Snapshot and references

Base `dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`, clean initial checkout on
`m01-g00-cloud-environment-setup`. The commit adding this handoff/report identifies
the result; obtain it with `git log -1 --format=%H -- <this report path>`.
The user requires successor branches to start from the latest setup tip, never
main. Existing scientific specs, package artifacts and submitted logs are intact.

Read AGENTS.md, AGENT_HANDOFF.md, README.md, STATUS.md, the environment candidate
guide/YAML, source register, reproduction v2 report/evidence, audit template,
setup guide, installer, Cloud entrypoint/startup and validation/version helpers.
Inspected the historical Documentation_v4 report's relevant claims and the
OpenCL warning in the preserved replay output. Used cloud-environment-onboarding
setup/reference guidance for retained Cloud startup instructions.

## Changes and decisions

Added [NEXT_AGENT_AUDIT_PROMPT.md](../../NEXT_AGENT_AUDIT_PROMPT.md), an assignment
the user can give another agent, and
[NEXT_AGENT_AUDIT_HANDOUT.md](../../NEXT_AGENT_AUDIT_HANDOUT.md), the full procedure.
They identify the submitted result snapshot separately from later handout changes,
require a new branch from the current remote setup tip, and specify independent
reproduction, checks, findings, repair assignments and clean-baseline criteria.

The immediate assignment is now the user's independent setup/baseline audit,
followed by required repairs/review and then relevant M00 scientific review.
Updated AGENTS.md, AGENT_HANDOFF.md, README.md and setup/startup guides accordingly.
The main handoff now fetches a remote-tracking ref before branching, avoiding
reuse of a stale local parent; no local branch is forcibly rewritten.

Flagged questions include the two missing documentation anchors, absent U40/U41
source entries, historical/current provenance claims, first driver exit mismatch,
OpenCL repeat-install warning, status/handoff wording, complete source/package
identities and error propagation. These are audit questions, not invented audit
findings. Clean-baseline acceptance requires all applicable environment checks
and zero docs errors/eight self-tests plus issue disposition.

The successor must write the real reproduction v2 sibling audit, preserve older
reports, give concrete repairs to a worker on a descendant branch and independently
review repaired work. No empty audit file or acceptance statement was created.
This handoff does not authorize downloading weights or changing scientific meaning.

Only guide/startup hashes changed in environment/cloud-cpu/bundle.sha256; runtime
scripts, package/source archives, dependency versions and locks are unchanged.
The Cloud draft's start_skill was successfully saved from the updated CLOUD_START.md;
install_script, repository selection, network and credentials were preserved.
No Cloud snapshot publication is claimed.

## Checks

| Command/check | Working directory | Result |
|---|---|---|
| `python tools/check_docs.py --self-test` via main Python, before edits | repository root | Exit 1; two pre-existing anchors missing, all eight self-tests pass |
| Same documentation command after handout edits | repository root | Exit 1; identical two errors, all eight self-tests pass; no new broken links |
| `bash -n` on every Bash example in handout/main handoff/setup guide | repository root | 13 example blocks passed syntax validation |
| `sha256sum -c bundle.sha256` | environment/cloud-cpu | Exit 0; all replay artifacts match updated manifest |
| `git diff --check` | setup branch | Exit 0; whitespace checks passed |
| Diff against dcfd99d for candidate/specs/docs checker and runtime/package/source files | setup branch | Empty; no scientific/dependency changes |

Raw documentation results/status and Bash-example outcomes are in
[handoff evidence](evidence/Cloud_CPU_Audit_Handoff_v1/).
No package reinstall or CPU regression rerun was needed for these documentation
changes. The new agent is assigned the actual independent environment checks.
No self-check here is labeled an independent audit.

## Findings and next handoff

The existing documentation/provenance gaps and replay/status questions remain
for the auditor; this task only makes that assignment concrete and discoverable.
The broader repo is not declared clean. Scientific M00/G00 acceptance is unchanged.

Give the successor the prompt and latest setup branch. They create
`m01-g00-environment-audit-v1` or an unused suffix, record exact parent/snapshot,
follow the handout and write Cloud_CPU_Reproduction_v2_audit.md with independently
obtained evidence. Any required repair inherits that audit branch and receives
its own worker log and independent review. Report real blockers with evidence;
continue authorized independent checks. Main remains untouched.
