# COSMOS portability audit repairs — v2 worker

**Scope:** Root's user-authorized repair of F01/F02 in [the v1 audit](Cosmos_Portability_v1_audit.md); no next gate.**Outcome:** ready_for_audit for the repaired CPU software and publication handoff; publication delegated to the user's GitHub-connected Codex account.**Author:** Root Codex orchestrator; GPT-6-based, exact model/version and reasoning setting not exposed. No agent was spawned for this repair.**Record created:** 2026-10-30T17:30:45+01:00 (Europe/Stockholm). **Finished:** 2026-10-30T17:47:33+01:00 (Europe/Stockholm).**Snapshot:** `cosmos/portability-repair`, base/HEAD `4d5b266d982e5e72596e475712eafbbe110e001f`, currently uncommitted. Eight tested source/accessory hashes are in [the preserved source manifest](evidence/Cosmos_Portability_v2/tested-source.sha256). The complete delivered manifest, patch, full payload and expected Git tree are in `.runtime/cosmos-cpu/portability-repair/repair-v2/publication-handoff.zip`; this transport packet is not part of the Git commit.

## Changes and authority

The user requested root to repair both audit findings directly, publish the child/PR and leave a fresh-agent audit handoff. Future reviewer model and orchestrator-versus-spawned choice belong to the user; this is now recorded in AGENTS. No post-repair independent audit or merge is claimed.

F01 restores the original neutral empty-policy 7-GiB RSS/pressure thresholds. The G07 policy retains its inherited-limit RSS/pressure headroom margins. Both profiles keep correct job-scoped cgroup data and ancestor monitoring.

F02 treats `validator_source_sha256` as the actual source identity of the validator that created a correction. The verifier now accepts exactly the previously approved validator `67372fbe9c8083aebfa77886240608fcadacba930a1d7c643d6ae9f11938f61f` or its own actual current source hash. New correction creation still writes the actual executing source hash. Unknown identities reject. This narrow historical admission repair does not rewrite a receipt, correction, reference, canonical path, diagnostic checksum, prior rejection or budget. Original byte/receipt/lease/ledger validations remain intact. User authorization follows the reproduced v1 audit finding; fresh review must assess this identity policy before merge.

Six new integration-style software regressions distinguish neutral/G07 behavior under finite limits and test historical/unknown validator identity with unchanged original evidence/debit. The existing tamper checks remain part of the targeted validation.

## Verification

| Check | Actual result |
|---|---|
| Pre-fix new regressions, Slurm 4067784 (8 CPUs, 12G, 5min) | FAILED 1:0; **3 failed, 3 passed in 6.79s**, exactly neutral RSS, neutral pressure and historical-validator rejection. Scheduler elapsed 20s. |
| Syntax compile and `git diff --check` after repair | Passed before submitting 4067914. |
| Targeted regressions/tamper checks, then full CPU suite, Slurm 4067914 (8 CPUs, 12G, 30min) | **13 passed in 18.80s**, then **733 passed / 57 deselected in 767.44s**. Slurm COMPLETED `0:0`, 13:12 elapsed, cn131. Source hashes checked before and after the full run. |

Exact submitted script: `.runtime/cosmos-cpu/portability-repair/repair-v2/check.sbatch verified`. Output: `check-4067914.out`/`.err` in that directory. All mutable files remain inside the repository. No real QM, installation, GPU or new molecular campaign occurred.

## Reporting correction and handoff

The v1 worker/report sentence saying every job had eight CPUs was inaccurate: baseline 4065600 had two; later jobs had eight. The skill validator takes the skill directory, not SKILL.md. The original submitted records are preserved; these errata do not alter actual test results. The v1 727/57 pass applies to its earlier source snapshot, not a post-repair claim.

Use [the fresh-auditor handoff](../../docs/project-0/handoffs/COSMOS-PORTABILITY-AUDIT.md). F01/F02 are repaired in code but remain unapproved until the user's chosen fresh review. The academic account cannot connect to GitHub. The user explicitly delegated publication to another Codex account; use the prepared transport packet/prompt. No commit, push or PR was performed here, no author identity was invented, and no global config changed. Stop before another gate; do not merge.

Final verification independently compared 1160 protected Git blobs with the base; all scientific code/specification/reference/lock/model files matched. [Validation summary](evidence/Cosmos_Portability_v2/validation-summary.json) and [scheduler accounting](evidence/Cosmos_Portability_v2/slurm-accounting.txt) preserve actual outcomes. Final documentation self-test output is [recorded separately](evidence/Cosmos_Portability_v2/docs-check.json). No scientific profile/gate or merge approval is claimed.
