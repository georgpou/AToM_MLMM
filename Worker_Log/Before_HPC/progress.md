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

User steering after C checkpoint, recorded 2026-10-07 12:53 UTC: closure/reversal QA should strongly exercise model systems through host–guest controls, while larger molecular production systems may reach a sampling ceiling despite useful Pearson r/Kendall tau. Future approved workers must read [Scientific QA and production guidance](Scientific_QA_and_Production_Guidance_v1.md). Keep predictive quality separate from convergence and complete thermodynamic accounting; use predeclared bounded production budgets and report unresolved sampling diagnostics rather than require indefinite sampling or tune criteria after results. C3 metadata/refusal gap remains open. No worker, audit, production run or cluster submission was started by this steering.

Further user steering: follow the AToM developers' documented ABFE correction procedure, with the actual upstream protocol/version and our endpoint/restraint definitions recorded. No bespoke alternative is requested. The six template rows are obligations to classify, not six automatically nonzero extra calculations; retain evidence-backed cancellation/not-applicable handling and avoid double counting contributions already in the path. Some accounting remains relevant to RBFE. Guidance updated; D/E and audits remain paused.

D: user explicitly approved next worker, same style. Active /root/batch_d, gpt-6-luna/max, fork none, dispatched around 2026-10-07 13:44 UTC; recorded 2026-10-07T13:44:13.815335+00:00. Base 317a72e69391e9618b04d15b25c8b644b1e3221e. CPU v2 reused unchanged; no audit, nested workers or E. Stop/report at D completion. User scientific QA/AToM correction guidance is mandatory context. Complete protein target/prepared artifacts remain unselected; user asked asynchronously, generic importer/structural controls proceed meanwhile. Approximately two hours remain in the campaign wall window tracked from ~10:46 to ~15:46 UTC, including pauses.

D initial packet RED, reported 2026-10-07T13:53:00.791877+00:00: 8 failed/0 skipped, expected absent RBFE fixture/tools, protein proposal/importer and physical-solvent checker. Worker reports unique command/output receipts including exact argv, activation, source-patch identity, UTC and exit. Bounded upstream lookup retrieved U15 tag v8.5.0 source; cited U37 ABFE guide returned HTTP 403. Installed atom-openmm is 8.5.0b0; no upstream correction equivalence or molecular acceptance inferred.

D protein-target steering answered 2026-10-07T14:05:20.479788+00:00: user selected "Generic controls now; real target later." Worker notified. Complete-target preparation/execution is intentionally deferred; generic importer/transparent structural controls stay authorized.

D: worker complete. Source/tools/tests/fixtures/evidence e117a18ef253caa1bca354376c6d1badbd635515 (full tree e24d98ebc128b95290dff3c5243855adbde8a70e); worker report/STATUS 3d2f0c3d4395095ec6111cb1db119e779deb0af3. Required packet 9 passed/0 skipped/21.98 s; structural nodes 3 passed/0 skipped/0.18 s; final affected host metadata/control file 4 passed/0 skipped/20.81 s. Counts overlap. Final host metadata changed after 9/3 runs; affected file reran, unchanged protein proofs did not replay. Direct/native/common worker fresh-process export/restart passed only as bounded plumbing at three workers/two boundaries/one step.

Checkpoint 2026-10-07T14:13:49.873232+00:00: 386 supplied-file identities unchanged; all 21 latest receipt-listed tool/test/input hashes match; source/tool/test/fixture delta after worker source commit empty. src/atm_mlmm unchanged from C (41 modules, tree ff83c9e149502ae14c4d8571b84e18615a7b5b52). Receipt evidence/checkpoint-d-v1/identity.json. Original work checkout remains clean at 2d7bcc94f901738e39f536f16de84699d4e8d631.

D holds: physical crown/solvent parameters missing despite existing guest GAFF/AM1-BCC artifacts; U37 correction guide/index HTTP 403, exact applicable equations/domains/reference choices and numerical corrections unresolved; real protein target intentionally deferred; production ceilings/profile, adequate independent trajectories and matched molecular closure unperformed. C3 unmatched-state closure-refusal contract remains open. Small B cap derivative/worker proofs reused unchanged; no new real-protein proof. binding_result=not_evaluated. No scientific thresholds, QM ledger/continuation screen, historical failures, gate/milestone decisions or accepted fixtures changed.

STOP after D: E has not started and requires explicit user approval. Whole CPU suite/final docs self-test/installed-offline checks remain reserved after E. No independent audit or cluster job occurred. D about 28 minutes through worker completion/~30–35 through checkpoint; campaign ~3h30 wall time including pauses, ~1h30 remaining at checkpoint in the tracked five-hour window.
