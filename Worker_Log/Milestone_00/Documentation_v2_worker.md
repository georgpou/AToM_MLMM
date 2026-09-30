# Documentation cleanup - attempt 2 - worker

**Scope:** user-approved repository cleanup; no numerical gate, scientific implementation or M00 design approval.\
**Outcome:** ready_for_audit for the documentation cleanup only.\
**Model/version:** Astra; session-declared GPT-6 Astra Pro; underlying build not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** 2026-09-30T09:31:53+00:00.\
**Previous report:** [Documentation v1](Documentation_v1_worker.md), preserved unchanged. No matching independent audit was fabricated.

## Snapshot and references

Input: `AToM_MLMM.zip`, SHA-256 `475c47d99e05ea3acf230ba13f28a640a8ee188c7c74c2c3e89a971630778301`; its recorded Git HEAD is `e662a442641367f8056d0254166b49c4803f1f7c`. Work used an isolated copy of those bytes, not the live GitHub branch. No push or project commit was made.

The [historical snapshot](evidence/Documentation_v2/snapshot_before_cleanup.zip) contains the original 84 project files under `AToM_MLMM/` plus the supplied `cleanup-audit.md`. It excludes Git/Finder metadata. References actually used: the user's cleanup request, that audit, original AGENTS/log rules, all gate tasks and test tables, shared specifications, milestone review criteria, environment guides/YAML, indexes, templates and historical report/checker. External sources were not refetched.

The [result manifest](evidence/Documentation_v2/result-manifest.sha256) identifies all delivered files except itself. [File dispositions](evidence/Documentation_v2/changes.json) identify additions, edits and removals against the supplied tracked snapshot. Later scientific work must not update these historical cleanup records to make them describe a newer checkout.

## What changed

One root README now owns navigation. AGENTS.md owns global work/logging rules; each of the 42 tasks has a focused reading line. All 14 gate files, 82 exact planned test rows, 32 requirement meanings/owners and direct dependencies remain. S01-S07 remain the scientific authority; no contract version or proposed decision was silently promoted.

Milestone M01-M08 combined reviews moved verbatim into their closing gates. M00 remains a separate design review. Unique scientific notes, the numeric environment-force example, extension cautions and proposed ADR rationale moved into their owning specifications/gates. The duplicate test catalog, planning JSON, qualification page, intermediate indexes, placeholder log READMEs and redundant templates/guides were retired. STATUS.md is the sole live progress summary.

One Conda guide replaces competing setup instructions; the YAML's dependency values are unchanged. Filenames and references are corrected, and inherited environment claims remain qualification candidates rather than freshly verified facts. Finder metadata is removed/ignored. Existing Git history is omitted from the source ZIP, not deleted from the user's clone.

Two short historical pointer pages were retained solely for links in the unchanged v1 report. The report, five old evidence files and both old plans remain byte-identical. A compressed original snapshot makes removed material recoverable without requiring agents to read it.

## Checks and limits

From the delivered repository root:

```bash
python tools/check_docs.py --self-test
python Worker_Log/Milestone_00/evidence/Documentation_v2/check_cleanup.py
```

The first is the small ongoing local-link/heading checker. It permits source code, real audit logs and advancing status; the old frozen checker remains historical. [Documentation results](evidence/Documentation_v2/documentation-checks.json) record actual output and eight self-tests. The second is a **snapshot-specific cleanup regression**, not ongoing CI; [preservation results](evidence/Documentation_v2/preservation-checks.json) compare requirements, tasks, test rows, expressions, dependencies and immutable history against the archived input.

[Baseline failures](evidence/Documentation_v2/baseline-checks.json) show the expected missing consolidation before edits. [Six deliberate-error probes](evidence/Documentation_v2/mutation-checks.json) detect a deleted assertion, changed force expression, altered dependency pin, edited historical log, removed gate prerequisite and changed task instruction. The 80 files in the original historical manifest matched their hashes before editing. An independent Markdown parser also checked local destinations during delivery preparation.

These are editing-worker checks, not an independent audit. No scientific tests exist in this snapshot; no molecular installation, model/GPU execution, sampling, package-release verification or external-URL availability check was performed. All numerical gate and milestone states remain unaccepted. Packaging validation is performed separately against the supplied snapshot and final delivered bytes; the archive is not a claim about later remote changes.

## Next handoff

Audit this log and its result manifest; write `Worker_Log/Milestone_00/Documentation_v2_audit.md`. Start with the root README, AGENTS.md, G01's task-specific routes and the preservation results. Consult the archive only to check a disputed removal. No further documentation form or full-project reread is required for routine implementation work.
