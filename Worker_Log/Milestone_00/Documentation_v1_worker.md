# Documentation revision - attempt 1 - worker

## Handoff at a glance

| Field | Actual value |
|---|---|
| Task page and section | [Documentation maintenance](../../docs/project-0/guides/documentation-maintenance.md), entire assigned revision |
| Milestone / gate / smaller task IDs | Documentation upkeep under M00; no numerical gate and no M00 design acceptance |
| Attempt | 1 |
| Assigned scope | Update AGENTS.md, add worker/auditor handoff rules, make task navigation and language clearer |
| Outcome | ready_for_audit |
| Whole gate complete? | No; no gate implementation or acceptance claimed |
| Model | Astra; session-declared label from GPT-6 Astra Pro |
| Exact model version | GPT-6 Astra Pro as declared by this session; underlying build not exposed |
| Reasoning setting | not exposed |
| Finished at | 2026-09-29T15:01:32Z |
| Previous worker / audit | None for this documentation task's logging cycle; edition-1 package is the content baseline |
| Assigned budget and usage | Small-task, credit-conscious handoffs requested; numerical credit usage not exposed |

## 1. What this assignment was for

Make the existing documentation usable in small worker sessions, followed by a separate audit and a targeted repair. A new agent should find the task's purpose, relevant documents, required outputs, earlier work, and next log filename without rereading the entire project.

This assignment did not implement the molecular platform, approve its scientific design, recheck external releases, or change the live repository.

## 2. Starting point and exact result snapshot

The input was `AToM_MLMM_project0_docs.zip`, SHA-256 `8afe11e881be9eca9f473a0366cb2846e3356c3e8a341172c88a4f4730c7ca06`. The ZIP was extracted and retained unchanged as the comparison baseline. Its per-file hashes and original requirement/test definitions are in [baseline-summary.json](evidence/Documentation_v1/baseline-summary.json).

No project Git checkout or project commit was available in this task. The delivered full ZIP contains the actual revised files. Its [file manifest](evidence/Documentation_v1/file-manifest.sha256) identifies every delivered file except the manifest itself. That exclusion avoids a self-referential hash. The accompanying `AToM_MLMM_project0_docs_v1_to_v2.patch` is a delta from the exact supplied package, not a claim about the live repository's current branch. Local disposable Git repositories used for packaging are not project commits or a remote push.

## 3. Documents used

| Document or source | Relevant parts | Revision / identity | Use |
|---|---|---|---|
| User's current request | Folder names, log fields, audit repair directions, small sessions, readable language | Current conversation instruction | Define the required handoff behavior |
| Supplied `AGENTS.md` and `PROJECT_PLAN.md` | Project purpose, constraints, navigation | Edition-1 hashes in baseline-summary.json | Preserve scope and replace incomplete handoff rules |
| Supplied gates G00-G13 and milestones M00-M08 | Tasks, dependencies, tests, combined review | Edition-1 hashes in baseline-summary.json | Preserve IDs and scientific work while adding reading routes and smaller task IDs |
| Supplied specifications S01-S07 | Energy/protocol separation, shared records, physics, validation, evidence | Edition-1 hashes in baseline-summary.json | Keep the agreed scientific definitions and interfaces visible |
| Supplied requirements, test catalog, status, and plan index | Coverage, names, work state | Edition-1 hashes in baseline-summary.json | Maintain one consistent task/test map without inventing execution |
| Supplied guides, templates, and reference notes | Existing workflow and scientific explanations | Edition-1 hashes in baseline-summary.json | Simplify prose and remove competing report/status locations |

External source links were inherited, not fetched or independently reverified. The original brainstorming archive was preserved byte-for-byte; it is historical context, not the controlling implementation specification.

## 4. What changed

`AGENTS.md` now states the project goal, hard scientific rules, architecture boundaries, minimal reading route, test-first development, resource limits, and required logs. `Worker_Log/README.md` defines attempts, snapshots, metadata, audit findings, retries, partial work, and scope-specific acceptance. The nine milestone log folders contain navigation READMEs, not invented gate logs.

Every gate now has a purpose, expected outcome, limits, named reading sections, three separately assignable task IDs, planned tests, and its exact log folder. Every milestone explains how its gates fit together and what its combined review needs. A task can be narrowed further to one test or repair.

The shared specifications remain the source of scientific definitions. Their headings and mathematical expressions were preserved while prose was simplified. Status is summarized in one page and the matching index instead of repeated as independent claims across task pages.

The 32 original requirements and 81 original planned test entries were retained. I added **P0-TEST-G01-07**, an explicit original-MM force-inventory test, because G01 already required that inventory but did not name a matching check. Its expected behavior is now listed in G01, the catalog, and the index. It is a test specification, not implemented code.

The documentation checker and its small baseline record are review evidence only. They do not install simulation dependencies or implement any molecular test.

## 5. Checks and evidence

Working directory for the following command is the delivered repository root. The checker uses Python 3.13.5 and only the standard library.

```bash
python Worker_Log/Milestone_00/evidence/Documentation_v1/check_docs.py --self-test
```

See [the actual output](evidence/Documentation_v1/check-output.json) and [the readable QA report](../../docs/project-0/DOCUMENTATION_QA.md). The verification command returned exit code 0: 825 local link occurrences checked, 42 smaller tasks and 82 planned tests mapped, all five deliberate-error checks detected their defects. The 81 original mathematical expressions in the checked shared specifications and notes were unchanged. The check covers local links and headings, task and test identities, log destinations, dependency cycles, status consistency, retained scientific expressions, and the unchanged archive. Its disposable-copy checks deliberately introduce broken links, an incorrect log folder, a changed equation, a false acceptance claim, and an invalid attempt filename; each must be detected.

The draft-metadata check first failed as intended because the in-progress report lacked completed metadata. The final report replaces that draft before submission. An earlier authoring check also caught a mistaken draft task/test mapping; the mapping was corrected against the supplied registry before delivery. The first Git whitespace check rejected Markdown hard-break spaces in newly edited lines; these were replaced by explicit Markdown line breaks, preserving the text and rendering intent.

Packaging is verified separately against the exact baseline: apply the delta patch in a disposable repository, compare reconstructed bytes, reject a conflicting existing AGENTS.md, and compare ZIP members with the revised tree. The final delivery-check report is supplied alongside the ZIP, rather than embedding a ZIP's own hash inside itself. On the supplied baseline, `git apply --check`, `git apply`, and `git diff --check` returned exit code 0; reconstructed files matched byte-for-byte. The deliberate conflicting AGENTS.md check returned exit code 1 and changed no files. ZIP integrity, member-byte comparisons, and the file manifest also passed.

Molecular tests, GPU tests, installations, convergence studies, and external-link availability checks were **not run**. No numerical result is inferred from documentation checks.

## 6. Response to a previous audit

No independent audit was supplied for this documentation attempt. These are editing-worker checks, not an independent audit or approval.

## 7. What remains for the auditor

Check that the small-task boundaries are useful in practice, the reading routes contain enough context, and the logging rules cover partial work without allowing a partial pass to accept a whole gate. Inspect G01's added inventory test against its existing scope. Challenge any wording that appears to promise electrostatic or RBFE physics beyond the actual qualification plan.

The live repository was not inspected. Existing code, accepted work, and previous logs there must be preserved and reconciled during integration. The included patch is valid only for the supplied edition-1 files. The package includes no actual numerical worker logs and no audit report.

## 8. Next handoff

Audit `Worker_Log/Milestone_00/Documentation_v1_worker.md` against the supplied full snapshot and manifest. Write `Worker_Log/Milestone_00/Documentation_v1_audit.md`. Start with AGENTS.md, Worker_Log/README.md, docs/README.md, G01, and the two log templates. Read the detailed specifications only where needed to check that the rewrite preserves their meaning.

A repair uses `Documentation_v2_worker.md` and must account for each audit finding. Do not overwrite this submitted log. No M00 or G00-G13 status promotion is justified by this documentation revision.
