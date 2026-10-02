# Resume at the Astra high review launch

The user explicitly requested a temporary stop before launching Astra because their usage limit is nearly exhausted. **No reviewer has been launched and no audit/acceptance is claimed.** G04 implementation and required worker verification are ready. Continue the original goal after the user resumes: independent full-G04 review, findings/repair closure, acceptance evidence/STATUS, publish only child, then stop.

Repository: `https://github.com/georgpou/AToM_MLMM`. Child: `m03-link-boundary`. Working tree: `/workspace/AToM_MLMM-m03-link-boundary`. Original `/workspace/AToM_MLMM` on `work` was preserved. Parent/handoff exact SHA: `c63634ca7567428e294a73fa432d42026f9fd38a`. Tested source/inputs: `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The frozen submission is **the commit adding this file and `Gate_04_v1_worker.md`**; obtain the full SHA with `git log -1 --format=%H -- Worker_Log/Milestone_03/Gate_04_v1_worker.md`. The final chat supplies that actual SHA. Do not review a moving branch tip.

Activate `/workspace/atom-mlmm-g04-v2/activate.sh` in every shell. If resuming on a different machine, fetch the published child and replay its unchanged `environment/cloud-cpu/install.sh` into a new writable prefix; use actual activation path and keep main NumPy 2 / Amber NumPy 1.26 separate. Do not require the previous agent's installation. Preserve all old outputs; new audit outputs belong in a new `G04_v1_independent` directory. The worker's evidence directory is immutable once submitted.

Before launch, verify source/input manifest equality and exact frozen HEAD. All earlier evidence/contracts/locks/models remain preserved (212 files), all tested inputs are listed (151 files). Worker results: G04 24, full 262, analytic 261/1 deselected, G02 78, G03 38, admission 74, strict environment 9/9, upstream 1, inherited numerical 66/eight/eight, admission replay 18/2, stale offline 0.5 error detected. See raw captures and numeric JSON for actual commands and errors.

The **next substantive action** is the authorized independent reviewer launch, using the available collaboration API:

```text
spawn_agent(
  task_name="g04_v1_astra_audit",
  model="gpt-6-astra",
  reasoning_effort="high",
  fork_turns="none",
  message=<self-contained request below, with actual frozen SHA and paths>
)
```

Supply: exact repository/worktree and frozen submission SHA; tested source SHA; activation path; `Worker_Log/Milestone_03/Gate_04_v1_worker.md`, evidence README/manifest/preservation/plan/numerics; AGENTS/README/DEVELOPMENT/STATUS; `docs/project-0/handoffs/M03-G04-fresh-agent.md`; G04 and all seven stable assertions; relevant S01–S07 contracts; inherited M00/M01/M02 v2 audits and acceptance. Require independent source/oracle/numerical/rejection inspection on the exact frozen snapshot, relevant own executions and all applicable G04 checks together. Review cap geometry/both parents, exact boundary ledger, nonidentity maps, cap-MM forces, invariant force/torque, full particle maps, mapped ATM and trusted offline reload. Check M02 expression/global/fixed-physical/collision/duplicate repairs and legacy identity preservation.

The reviewer must **author no implementation, repairs, scientific specification changes, STATUS changes, commits or pushes**. It may author independent probe/evidence scripts and `Worker_Log/Milestone_03/Gate_04_v1_audit.md` only. Record actual configured **gpt-6-astra/high**, deployed version if exposed, exact snapshot, profile, commands/results, findings/closure conditions and explicit full-G04 verdict. Do not substitute another model or self-review. If unavailable, keep acceptance pending and preserve the review-ready submission.

The initial nested diagnostic already measured correct native single projection; no production redistribution repair was made. The actual missing recomputation, FD restoration and alias checks have RED/GREEN evidence. FD steps include required 1e-3/1e-4/1e-5 plus 1e-6 for steep retained GAFF; limits are unchanged. Model-only Jacobian maximum error is 1.38778e-16; final full-ATM FD maximum is 1.23460e-6. Some early filenames contain `green` despite failed runs; evidence README explicitly distinguishes them.

After the actual audit, inspect findings, repair with meaningful failing regressions and an unused attempt/snapshot, and obtain independent full-G04 closure as the user required. Do not overwrite v1 submissions. Create schema-valid acceptance evidence using the actual Astra decision and seven stable checks. Update STATUS to accepted only from that decision; verify report-only source/input equality. Commit/push only the child and verify protected remote tips remain: main `2d7bcc94f901738e39f536f16de84699d4e8d631`, M01 predecessor `87146b4cc7fbd0b58d6688903a5ba081b813ac13`, M02 parent `c63634ca7567428e294a73fa432d42026f9fd38a`.

Stop after G04 acceptance. G05 requires model loading prerequisites and M00 predeclared physical references; G06/G07 follow actual dependencies and G07 closes M03. G08 is a separate M04 path. Molecular/chemical/protein, GPU/full-model, periodic/actual electrostatic and full asynchronous workflow qualification remain deferred. Finish with child branch link, exact publication commit, actual test results, Astra high decision, open issues and next dependencies.
