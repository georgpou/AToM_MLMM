# Apply this documentation update safely

This is a documentation package for `georgpou/AToM_MLMM`, not a clone of the full live repository. This revision was made from the supplied edition-1 ZIP. No live code or existing remote worker logs were inspected or modified.

## Two ways to use the delivery

The full `AToM_MLMM_project0_docs_v2.zip` contains the complete revised documentation tree. Use it as a reference snapshot or for a repository that has not yet received the earlier package. Compare existing files before copying. Do not overwrite a real project's `AGENTS.md`, status, or worker logs blindly.

The `AToM_MLMM_project0_docs_v1_to_v2.patch` contains changes from the exact supplied edition-1 package. It is intended for a checkout that already contains that version. From a clean branch of that checkout:

```bash
git status --short
git apply --check /path/to/AToM_MLMM_project0_docs_v1_to_v2.patch
git apply /path/to/AToM_MLMM_project0_docs_v1_to_v2.patch
git diff --stat
git diff --check
```

Run the second `git apply` only if the check succeeds. A context mismatch can mean that the live documents have already changed. Compare and merge deliberately rather than forcing application or resetting the repository. The patch is not an authorization to delete unrelated work or push to the remote.

## Preserve existing work

Keep the repository's actual code, tests, root README, licenses, and prior work history. In particular, do not replace real status or acceptance records with this package's initial unexecuted state. Merge new fields and routes into the live status where needed. If `Worker_Log/` already contains attempts, keep them unchanged and choose the next free documentation attempt number for any imported maintenance report.

The supplied `Documentation_v1_worker.md` records this package-editing session only. It is not a remote commit, M00 design approval, or a numerical gate pass. No corresponding independent audit is supplied.

## What changed in the plan index

The documentation index uses schema version 2. Existing gate/milestone IDs and dependencies remain. It adds task IDs, task-to-test mapping, log folders/stems, optional latest-log pointers, and workflow rules. Existing scientific runtime records are not being changed to schema 2 by this edit; this version applies only to `plan-index.json`.

The original 81 acceptance-test definitions remain, and one explicit original-MM inventory test was added under G01 to cover an existing deliverable. All molecular tests remain unexecuted. The actual source code and test-suite status must be checked in the live checkout.

## Check the resulting tree

Confirm that every task points to the right log folder, linked files/sections exist, the status/index agree, and old logs survive. Run the documentation checker recorded in [the documentation work log](../../../Worker_Log/Milestone_00/Documentation_v1_worker.md) for this delivered snapshot. Its historical count assertions describe this edition; deliberate future changes need an updated check baseline.

After review, commit only the intended documentation changes according to the user's workflow. No remote publication is implied by this package.
