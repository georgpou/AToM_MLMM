# COSMOS portability: fresh-agent audit handoff

## Scope and review authority

Audit `cosmos/portability-repair` against base `COSMOS` commit `4d5b266d982e5e72596e475712eafbbe110e001f`. This branch contains the first bounded software-portability repair from [COSMOS-HANDOFF](COSMOS-HANDOFF.md), plus root's user-authorized repair of two audit findings. It accepts no scientific gate/milestone. PR base must be `COSMOS`; do not merge until the user's required review.

The user chooses the reviewing model and whether review is by the orchestrator or a spawned agent. Never choose Luna as reviewer. The implementation worker was Luna 6 xhigh; root performed the subsequent audit and F01/F02 repairs. Root's tests/self-checks are not independent approval of root's repairs. The fresh reviewer should report findings and ask before changing implementation or making scientific/executive decisions.

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md), [v1 root audit](../../../Worker_Log/Documentation/Cosmos_Portability_v1_audit.md), and [v2 repair worker](../../../Worker_Log/Documentation/Cosmos_Portability_v2_worker.md). Earlier Cloud audits remain historical evidence; do not repeat unrelated onboarding or start another gate. Review all runtime/test changes against the base, with particular attention to root's final F01/F02 edits.

## Environment and exact snapshot

Source `environment/hpc/cosmos/activate.sh` in every shell/job. Cosmos has `/proc/sys/user/max_user_namespaces=0`; use reviewed `require_escalated` as explained in the [repository-local skill](../../../.agents/skills/cosmos-execution/SKILL.md). All writes, caches, logs and temporary files must remain inside this repository. Do not alter HOME, installations or frozen scientific artifacts. Use bounded Slurm CPU allocations and timed waits.

Publication is delegated to the user's other Codex account because this academic account cannot connect to GitHub. Until published, use base plus the [tested source manifest](../../../Worker_Log/Documentation/evidence/Cosmos_Portability_v2/tested-source.sha256) and the complete delivered manifest/patch/payload in `.runtime/cosmos-cpu/portability-repair/repair-v2/publication-handoff.zip`. The packet also contains the publication-only prompt, PR body and expected Git tree. No commit, push or PR has been performed here. Verify hashes before relying on results. The branch has no local Git author/authentication configured; do not invent identity or request/expose tokens. When published, verify the actual PR head and tree against the recorded source hashes.

## Assertions to audit

- Disk headroom is measured on the actual attempt/output filesystem, including a not-yet-created output via its existing parent. No `/workspace` creation or fabricated production disk readings.
- The cgroup-v2 resolver stops at the verified Slurm job boundary, respects finite inherited limits and raw per-scope provenance, and rejects malformed/unsupported data. Unrelated host totals are excluded. The existing pressure formula and group cleanup remain intact.
- **F01:** neutral empty-policy thresholds remain 7 GiB; G07 retains its separately defined RSS/pressure margins. Regressions use finite 8-/6-GiB synthetic readings and exercise the actual coordinator. Check that both policy branches and ancestor OOM/pressure controls remain correct.
- **F02:** the accepted historical correction records validator `67372fbe9c8083aebfa77886240608fcadacba930a1d7c643d6ae9f11938f61f`. Read admission permits exactly that known approved identity or the actual current verifier source hash; new correction creation retains its actual source hash. Unknown identities must reject. Every original record/receipt/diagnostic/canonical-path/lease/budget check must remain. Historical receipts and the cumulative debit must not be rewritten. Actual Cosmos execution-path migration remains a separate reviewed obligation.
- The offline worker test denies the whole original checkout except its exact relocated bundle and installed interpreter prefix. Old run/cache roots override both exceptions. Source/config/fixture/runtime-sibling/network negative controls, bundled-source identity, unique samples and unchanged original samples remain. Temp/Matplotlib cache output belongs inside relocation.
- Physical source, units, forces, tolerances, frozen approvals, chemical-reference records, package locks and model artifacts are unchanged. Preserve 46 accepted G05 references and the charged QM ledger (2325.6446500519996/86400 seconds). Missing G07 references/boundary sensitivity, chemistry/thermodynamic corrections, GPU and broader cluster parity remain open.

## Validation and report

The earlier Luna snapshot passed focused 88 tests and full CPU 727/57, but root audit found F01/F02; those counts do not approve the repaired snapshot. New regression red job 4067784 gave exactly 3 failures/3 passes. Repair validation job 4067914 completed `0:0` on cn131: **13 targeted/tamper tests passed in 18.80s**, followed by **733 CPU tests passed / 57 deselected in 767.44s**, 13:12 total scheduler elapsed, one task/8 CPUs/12 GiB. All eight source hashes verified, and 1160 protected base blobs remain unchanged. See [the validation summary](../../../Worker_Log/Documentation/evidence/Cosmos_Portability_v2/validation-summary.json).

Review the exact recorded outputs and source hashes. Run bounded independent probes for F01/F02, malformed/unknown identities and isolation; do not automatically repeat a full suite already run on the identical snapshot. Use the available CPU suite when code changes or evidence warrants it:

```bash
python -m pytest -m 'not gpu and not model_assets and not slow' -q \
  --basetemp="${TMPDIR}/audit-${SLURM_JOB_ID}"
```

Write `Worker_Log/Documentation/Cosmos_Portability_v2_audit.md` after checking it is unused. Include exact head/base or manifest, reviewer model/effort as exposed, timezone timestamp, commands/outcomes, substantive findings and closure conditions. Report rather than silently repairing. No new gate should start here. After user-reviewed merge, the next bounded task is an applicability/evidence mapping that reuses this CPU evidence and identifies uncovered checks/scientific gaps, not a blanket replay of every gate.
