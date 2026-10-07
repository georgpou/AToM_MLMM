# Implementation ledger — docs/superpowers/plans/2026-10-07-before-hpc.md

User steering: stop and report after each Luna batch; next batch needs explicit user approval. No audit/reviewer agents. Exactly five gpt-6-luna/max workers, sequential, no nested workers.

Setup: fetched published g10-engine-next at 4ad8ee835809325ceec8a017222415043347967d; before_HPC isolated in /workspace/AToM_MLMM-before-HPC. Original clean work checkout preserved. Reviewed-base delta empty. Supplied files retained verbatim; identities in evidence/setup-v1/handoff-identity.json.

Plan interfaces: A preserves restart/loading APIs and establishes shared admission; B extends cap/input collections consumed by D; C extends analysis/result records consumed by D/E; D prepares inputs consumed by E; E packages results and hands final frozen code to consolidated checks. Shared edits run in A–E order. Scientific holds stay holds. No known task/global-rule conflict in these packets.

A: active — /root/batch_a, gpt-6-luna/max, fork none, started 2026-10-07T10:49:27.534184+00:00. Worker instructed to await CPU setup before science. B–E pending explicit user approval at each preceding boundary.

Environment: v1 installer failed at read-only /home/agent/.conda after verified bootstrap unpack. Preserved /workspace/before-hpc-cpu-v1/logs. mkdir of the standard registry succeeded through approved escalation. Fresh unchanged-lock install v2 active at /workspace/before-hpc-cpu-v2; no dependency/profile substitution.

CPU setup completed exit 0: /workspace/before-hpc-cpu-v2, nine validation exits 0, receipt evidence/setup-v1/cpu-validation.json. /root/batch_a notified ready. No baseline pytest run.

A: complete, implemented and worker-tested; source 8757c0e37cb7530eeb695b9db6576a6009a4debb, evidence 516c06d4ed8e780ddb12c0542941fb789e3d291c. Packet check 84 passed, zero failures/skips, 92.05 s. Local docs check exit 0. No scientific source/test delta after tested source commit. Supplied 386 file identities unchanged.

Checkpoint 2026-10-07T11:14:09.817251+00:00: /root/batch_a finished. No other worker has been spawned. B–E not started; Batch B requires explicit user approval. Final consolidated CPU suite and final documentation self-test remain reserved for after E. No independent audit occurred.

Evidence limits: first collection-error output was overwritten; exact early RED shell argv not captured. Meaningful RED output and final packet command/output preserved. Raw log whitespace retained. No A code/input blocker reported.

B: user approved at the next turn; active /root/batch_b, gpt-6-luna/max, fork none, started 2026-10-07T11:18:58.647036+00:00. Base 9dc4758caa7e51efc1df76c59688d739098a422c. CPU v2 reused unchanged, no reinstall/setup replay. Stop/report after B; C–E require later explicit approval.

B: complete, implemented and worker-tested; /root/batch_b finished. Combined source/evidence commit 63cdaffaedee01891b50bfc08358b552ec8c5fa1; source Git tree d5cc16ef725df2f08fb14675038b3294ad957593. Packet-focused command 30 passed/0 skipped/16.74 s; affected single-cap/worker compatibility 28 passed/0 skipped/15.13 s; MACE derivative, fresh reload, and common restart passed. Counts overlap across isolated checks and are not summed. No upstream construction blocker for the bounded case; synthetic geometry is derivative/architecture evidence only.

Checkpoint 2026-10-07T11:55:41.460159+00:00: Batch C has not been spawned. C–E and final consolidated checks pending approval/execution. No independent audit occurred. All 386 supplied file identities unchanged. Tested current source/test bytes have no delta after worker commit; receipt evidence/checkpoint-b-v1/identity.json.

C: user approved at the next turn; active /root/batch_c, gpt-6-luna/max, fork none, started 2026-10-07T12:20:35.430021+00:00. Base 07454097b0a1c9dafa9e0ce704f0c0a3e07b4b9a. CPU v2 reused. Stop/report after C; D/E need later approval. Campaign wall-clock allowance from ~10:46 UTC is about 3h28 remaining at dispatch; worker informed.

C design frozen before synthetic estimator calculations: ac86c1c, design/seeds/expected under fixtures/analytic/exchange-analysis-v1. 12 seeds; 4096 frames/run; AR rho 0.5/shared variance fraction 0.5; block 32; draws 64; known answers +/-1.5/0; estimator agreement 1e-6 kJ/mol; bootstrap/between-run-mean variance ratio [0.5, 2.0]. Reported 2026-10-07T12:24:36.024800+00:00.

C: worker finished around 12:42 UTC. Source/evidence/handoff commit 0de7cc887adc77863d8bc3b9b888f6239c8c8687; src/atm_mlmm Git tree ff83c9e149502ae14c4d8571b84e18615a7b5b52. Final focused 43 passed/0 skipped/1 deselected, exit 0, 30.94 s; the deselected frozen qualification passed separately (1 passed/0 skipped, 54.01 s). Earlier 21-pass affected check overlaps final coverage. Synthetic block/run covariance ratios 0.9944/0.8232 and known-answer controls passed; no molecular or convergence qualification follows.

C3 uncovered requirement: general refusal contract for unmatched physical-state closure comparisons is not implemented/qualified. Endpoint physical metadata schema and comparison service are absent; matched analytic A→A/reversal controls do not close this requirement. All six example molecular corrections and linked covariance remain unresolved. Persistent-journal adapter was not tested on a molecular history.

Checkpoint 2026-10-07T12:44:04.009781+00:00: all 386 supplied files unchanged; tested source/test/template digests match, no source/test/fixture delta after worker commit. README digest in worker receipt is stale after final hold text; actual committed digest captured in evidence/checkpoint-c-v1/identity.json. Early attempt argv/start metadata gaps remain disclosed. Actual C dispatch was 12:20:35 UTC, final test completion 12:39:19 UTC; worker about 22 minutes, C turn about 25 minutes including checkpoint. Campaign wall time about two hours including pauses, about three hours remaining.

STOP: C reported; D/E not started and require explicit user approval. Full CPU suite, final documentation self-test and installed/offline checks remain reserved for after E. No independent audit occurred. Campaign remains partial; C3 is partly held.
