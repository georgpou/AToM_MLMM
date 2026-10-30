# Repository refresh - attempt 2 - worker

**Scope:** User-authorized full folder backup, replacement with the latest project branch, checkout verification, and deletion of the backup after successful verification. No engine changes or scientific qualification.
**Outcome:** ready_for_audit: folder replacement, checkout verification and requested backup deletion completed.
**Model/version:** GPT-6-based Codex per session instructions; exact version not exposed.
**Reasoning setting:** not exposed.
**Finished:** 2026-10-30T13:50:39+01:00.
**Previous worker/audit:** Repository_Refresh_v1_worker.md and its verified SHA-256 sidecar preserved from the original folder. No independent audit performed.

## Snapshot and references

Original: supplied non-Git folder at `/lunarc/nobackup/projects/snic2019-35-66/George/AToM_MLMM`. Backup contained 102 entries, including 77 regular files. The alternate `/home/geopou/lu2024-12-50/George/AToM_MLMM` path identifies the same folder.

Loaded: `https://github.com/georgpou/AToM_MLMM.git`, branch `hpc-atom-benchmark`, commit `70ad284745617122627f217cd86d58237a2435ee`. GitHub connector and `git ls-remote --symref` identified five branches; their head dates were main September 30, cloud-engine-continuation October 5, g10-engine-next and before_HPC October 7, hpc-atom-benchmark October 8, 2026. Thus the newest branch, not the older default main, was selected under the user's latest-branch request.

Read original and loaded AGENTS.md, README.md, relevant STATUS.md, worker template, docs/DEVELOPMENT.md, pytest.ini, pyproject.toml and tests/conftest.py. Skills: using-superpowers, systematic-debugging, verification-before-completion. No scientific handoff assignment was executed. Source and model assets came from the exact requested project source; no serialized model was loaded.

## Changes and decisions

The default Bubblewrap sandbox fails because `/proc/sys/user/max_user_namespaces` is zero; a minimal `unshare --user --map-root-user /usr/bin/true` reproduces ENOSPC despite ample disk/inodes. Reviewed outside-sandbox commands succeeded; no system setting was changed.

A Python `shutil.copytree(..., symlinks=True, copy_function=shutil.copy2)` backup was written to `/tmp/atom-refresh-watol5kz/backup`. Per-entry type, permissions, symlink target and regular-file SHA-256/size were compared between source and backup, then checked again before deletion. A fresh shallow clone was staged, its commit and Git objects verified, and original contents removed only after those checks. The staged checkout was copied into the existing folder; all 1,771 entries, including Git metadata, matched the staged manifest exactly, and the checkout was initially clean.

Only administrative additions modify the fetched snapshot: this log, preserved v1 report/sidecar, evidence manifests and the refresh note in STATUS.md. No source, tests, model, environment recipe, scientific definitions or acceptance evidence were edited. Git history was neither rewritten nor pushed. The clone is shallow and contains only the selected branch; historical commits remain available remotely.

## Checks

All checkout checks ran outside the failing sandbox. Working directory was the staged checkout for initial Git inspection, then the project root for final checks.

| Command or operation | Actual result |
|---|---|
| `git ls-remote --symref https://github.com/georgpou/AToM_MLMM.git HEAD 'refs/heads/*'` | Retrieved five branch heads and default main. |
| `du -sh .`; `df -h /tmp .` | Original 1.4 MB; /tmp had 30 GB available. |
| Inline Python backup and SHA-256/type/mode/symlink comparison | Passed: 102 entries, 77 regular files; source unchanged before replacement. |
| `git clone --depth 1 --single-branch --branch hpc-atom-benchmark https://github.com/georgpou/AToM_MLMM.git /tmp/atom-refresh-watol5kz/checkout` | Exit 0. |
| `git rev-parse HEAD`; `git status --porcelain`; `git fsck --full` | Exact expected SHA; clean checkout; object verification passed. Critical checks repeated using Python subprocess check=True. |
| Inline Python copied-entry manifest comparison | Passed: all 1,771 staged/loaded entries equal. Source inventory retained in evidence/Repository_Refresh_v2/loaded-file-manifest.json; original inventory in backup-manifest.json. |
| `python3 tools/check_docs.py --self-test` | Exit 0; 175 Markdown files, 1,183 local links, zero errors, eight self-tests passed. |
| `python3 -m pytest -q tests/unit/test_identity.py tests/contracts/test_schema.py` | Exit 0: 6 passed, zero skipped, 0.07 s. |
| Inline Python ast.parse with tokenize.open over src/tools/scripts/tests | Exit 0: 156 Python files parsed. |

Python used the existing `/sw/easybuild_milan/software/Anaconda3/2024.06-1/bin/python3`; no project environment activation or installation was claimed. OpenMM is unavailable there. Full numerical/model/GPU/benchmark runs were not performed: this is checkout integrity and lightweight verification, not environment or physical-profile qualification. No simulations or installations ran.

## Cleanup and handoff

Backup cleanup: completed after final documentation checks, git fsck, git diff --check, allowed-file checks and byte verification of all unchanged tracked files passed. The task-created /tmp/atom-refresh-watol5kz directory (backup, staging clone and temporary manifests) was deleted; its absence was verified. Original and loaded inventories are retained in the evidence folder. Final documentation check output is retained in final-docs-check.json. No independent acceptance, scientific gate pass, commit or push is claimed. Matching independent review, if requested, would use Repository_Refresh_v2_audit.md.

**Cleanup completed:** 2026-10-30T13:51:11+01:00.
