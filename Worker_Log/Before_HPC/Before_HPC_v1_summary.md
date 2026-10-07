# Before HPC v1 — Batch A approval checkpoint

**Scope/outcome:** implementation campaign partial; Batch A implemented and worker-tested. **Checkpoint:** 2026-10-07T11:14:09.817251+00:00. **Orchestrator:** Codex GPT-6; precise version/reasoning setting not exposed. **Worker:** gpt-6-luna/max, one worker, no nested agents. No independent audit occurred.

The user explicitly required a report and pause after each Luna worker. Batch B has not been spawned and requires approval; B–E and the final consolidated checks remain unexecuted.

## Branch and preserved work

- Checkout: `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`.
- Fetched published `origin/g10-engine-next`: `4ad8ee835809325ceec8a017222415043347967d`, identical to the supplied reviewed base; no newer delta.
- Planning preservation: `42e3e318c2e90c09e16d9faa6461afd70df8c9cf`.
- Batch A code/STATUS: `8757c0e37cb7530eeb695b9db6576a6009a4debb`; worker/evidence: `516c06d4ed8e780ddb12c0542941fb789e3d291c`.
- This checkpoint and CPU setup receipts are documentation-only changes after those commits. No code/test delta followed the tested source commit.
- Original clean `/workspace/AToM_MLMM` checkout remains on `work` at `2d7bcc94f901738e39f536f16de84699d4e8d631`. No push, merge, reset, rebase, force-push, release, or deployment occurred.
- All 386 supplied files still match [the attachment identity receipt](evidence/setup-v1/handoff-identity.json); historical review/evidence is unchanged.

## Actual implementation and checks

Batch A added complete source-inventory admission and actual restored-state admission to fixed-window/pair continuation and trusted worker loading, using shared checks also exercised by multistate regressions. Both maps/cap parents are checked before refreshed energies/full forces and stepping. Public restart/loading APIs are preserved. STATUS reconciles the historical bounded v8 acceptance while keeping full M05 and these new changes' review status separate.

The new helper contracts and exact commands are in [Batch A's worker record](Batch_A_v1_worker.md). No A1–A3 code/input blocker is reported.

| Check | Actual outcome |
|---|---|
| Unchanged-lock CPU installation, `/workspace/before-hpc-cpu-v2` | Installer exit 0; all nine setup validation checks exit 0; [receipt](evidence/setup-v1/cpu-validation.json) |
| Meaningful initial regressions | 11 failed/1 passed, exit 1, 4.91 s; valid continuation was the pass; [retained output](evidence/batch-a-v1/focused-red-confirmed.log) |
| First post-fix packet run | 72 passed/12 failed, exit 1, 79.67 s; [retained output](evidence/batch-a-v1/focused-green-attempt1.log) |
| Focused admission run after corrections | 14 passed, exit 0, 4.57 s |
| Final prescribed four-file packet command | 84 passed, zero failures/skips, exit 0, 92.05 s; [output](evidence/batch-a-v1/focused-final.log) |
| Local documentation links | Exit 0, zero errors; 256 Markdown files and 1,655 local links; external links not fetched |
| Source/docs whitespace before worker code commit | Worker records exit 0; raw evidence log whitespace retained byte-for-byte |
| Consolidated full CPU suite/final docs self-test/installed-offline checks | Not run; scheduled after Batch E |

The packet command included affected multistate source/inert admission, restored clocks/geometry, refreshed-energy/full-total and portable-parameter checks in `test_persistent_exchange.py`. These results are coder verification; they do not create independent acceptance. No baseline suite or unchanged physical reference was rerun. Science remained serial CPU with two threads and an 8 GiB cgroup limit. No molecular pilot, QM, long sampling, GPU benchmark, or cluster job ran. No new resource benchmark is claimed.

The first setup attempt failed at the read-only standard Conda registry; its logs remain under `/workspace/before-hpc-cpu-v1/logs`. The required registry directory was created through approved escalation, then installation succeeded in fresh v2. The [setup identity receipt](evidence/setup-v1/cpu-setup-identity.json) locates and hashes both attempts.

Evidence limitations remain explicit: the initial test-collection SyntaxError output was overwritten before the meaningful RED run, and the exact early RED shell argument vector was not captured. The meaningful failure node IDs/tracebacks, final exact packet command, and final pass output are retained. These unavailable records were not regenerated.

## Remaining work at this checkpoint

1. **Code/definition/input:** B–E not started. After approval, B is the next action. Later packets still require complete protein/input decisions and explicit thermodynamic/correction definitions where absent; no chemistry is inferred here.
2. **Scientific calculations:** prior G07 physical failures, seven sensitivity exceedances, and 29 missing references remain open. Adequate molecular sampling/corrections/reversal/closure remain future work. The retained QM ledger is `2325.6446500519996 / 86400 s`, continuation authorization false; no reference is regenerated under this checkpoint.
3. **Cluster qualification:** actual hardware/storage/profile/parity/checkpoint trials remain unperformed and require the user's later instructions and the prepared handoff from E.
4. **Performance:** small CPU measurements are planned in E; later optimization and GPU performance require separate resources and decisions.

Prior bounded evidence applies only to its unchanged bytes/profile; it is not relabeled as a fresh result on this modified branch. The molecular baseline remains `binding_result=not_evaluated`. The original scientific thresholds, assets, locks and reference data are preserved.

Stop here and wait for the user's approval to start Batch B.
