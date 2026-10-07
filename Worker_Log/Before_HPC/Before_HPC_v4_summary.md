# Before HPC v4 — Batch D approval checkpoint

**Outcome:** D's authorized generic input/preflight work is implemented and worker-tested, with physical-input and thermodynamic holds. Campaign remains partial. **Snapshot receipt:** 2026-10-07 14:13:49 UTC. **Worker:** gpt-6-luna/max, sequential, no nested agents. No independent audit occurred.

The user approved D only and confirmed **generic protein controls now; real target later**. D has finished. E has not started and needs explicit user approval. The consolidated CPU suite, final documentation self-test and installed/offline checks remain reserved for after E.

## Snapshot and implemented scope

Checkout `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`; published base `4ad8ee835809325ceec8a017222415043347967d`. D started at `317a72e69391e9618b04d15b25c8b644b1e3221e`. Source/tools/tests/fixtures/evidence commit: `e117a18ef253caa1bca354376c6d1badbd635515`, full Git tree `e24d98ebc128b95290dff3c5243855adbde8a70e`. Worker report and STATUS commit: `3d2f0c3d4395095ec6111cb1db119e779deb0af3`.

D changes tools, fixtures and tests; `src/atm_mlmm` is unchanged from C, retaining tree `ff83c9e149502ae14c4d8571b84e18615a7b5b52` and 41 Python modules. [The checkpoint receipt](evidence/checkpoint-d-v1/identity.json) records all core module digests, the 21 final receipt-listed tool/test/input digests and final command/log identities. They match the last tested bytes; no source/tool/test/fixture delta exists after the worker commit. All 386 supplied files remain unchanged. Accepted host–guest v2, 64-water fixtures, locks, assets and sealed evidence were preserved. Original `work` remains clean at `2d7bcc94f901738e39f536f16de84699d4e8d631`. No remote publication or history rewrite occurred.

`tools/prepare_host_guest_rbfe.py` generates a separate deterministic 18-crown-6/methanol A→ethanol B development fixture with complete unequal guests, stable IDs, opposite full-molecule maps, neutral-singlet declarations, provenance and loadable configuration. Admission examines the entire host and guest clearances at both maps. Direct/native mechanics and a fresh-process common-worker export/restart were exercised at the retained tiny settings: three workers, two boundaries, one step. Its inert zero-charge/LJ MM ledger is plumbing, not physical solvent or an affinity model.

`tools/prepare_protein_input.py` implements generic prepared-input admission and readable missing-decision rejection. The transparent B structural control exercises common configuration import, the original all-MM inventory reference, zero-cut ligand-only mixed assembly and cavity-inclusive two-cap assembly. Real masses/constraints/box/source coordinates are matched; cap masses/sites/parents are checked separately. Byte-identical B derivative/parent-force/worker proofs were reused. No real-protein fixed-coordinate, derivative or worker execution occurred; the target is deliberately deferred.

`tools/validate_solvent_recipe.py` checks explicit NVT preparation definitions and rejects missing physical-liquid choices or implicit unsupported integration/ensemble changes. The old 64-water data remain a synthetic reference. The new physical-solvent proposal is not an admitted equilibrated liquid.

Concrete tools, configurations, missing-field requirements and execution scope are in [the worker report](Batch_D_v1_worker.md). The host fixture under `fixtures/host_guest_rbfe/v1/` contains correction accounting and proposed run definitions. A→A, forward A→B and independently initialized reverse B→A seeds/conventions are recorded as `proposed_not_run`. The matched ABFE/RBFE cycle is blocked by incomplete physical definitions. Production retention ceilings and measured wall-time estimates remain future inputs; no molecular closure expression or result is asserted.

## Actual checks

| Check | Actual outcome |
|---|---|
| Initial required packet RED | 8 expected failures, exit 1; raw output and exact invocation retained |
| Required host–guest/protein-input command | 9 passed, 0 skipped, exit 0, 21.98 s; 14:07:41–14:08:05 UTC |
| Bounded protein structural/correction-ledger nodes | 3 passed, 0 skipped, exit 0, 0.18 s; 14:08:19 UTC |
| Affected host file after final parameter-route metadata regeneration | 4 passed, 0 skipped, exit 0, 20.81 s; 14:09:18–14:09:41 UTC |
| Whole CPU suite/final docs self-test/installed-offline checks | Not run; reserved for after E |

The 4-test host run overlaps the 9-test packet. The 9/3-pass runs preceded the final host metadata change; the affected host file was then rerun, while unchanged protein behavior was not replayed. These counts are not added as independent evidence totals. Exact argv, UTC intervals, activation/source/patch identities, exits and preserved failures are in [the evidence index](evidence/batch-d-v1/README.md) and JSON receipts.

The worker corrected unequal-array/broadcast assumptions, existing API/field names, a valid sibling-fixture path and real-versus-cap particle comparisons after recorded failures. Its index identifies the subsequent changes that warranted each rerun. Scientific thresholds were not changed. CPU v2 was reused unchanged, scientific execution stayed serial with two threads and 8 GiB; no setup/baseline replay, QM, long trajectory or GPU/cluster job ran. These checks establish input admission and mechanism behavior, not physical usefulness, molecular accuracy, sampling adequacy, G11/G12 acceptance or independent input qualification.

## Physical and definition holds

1. **Host/solvent preparation:** existing GAFF 2.2.20 / AM1-BCC methanol and ethanol artifacts are identified, but their prepared-MM manifest contains no 18-crown-6 parameters. A genuine parameterized host/solvent route remains missing. No new parameter or QM calculation was launched.
2. **AToM correction procedure:** U15 `abfe_structprep.py` was retrieved from tag v8.5.0 and matches the installed 8.5.0b0 file byte-for-byte. It defines restraint preparation, not postprocessing correction equations. The cited U37 ABFE guide and targeted source index returned HTTP 403; URLs/headers are preserved. The exact applicable upstream equations, physical domains/reference atoms and numerical corrections remain unresolved. Six rows are applicability/accounting obligations, not six automatic extra calculations; no bespoke replacement or assumed zero was introduced.
3. **Protein execution:** intentionally deferred by the user. The real target, complete prepared artifacts and scientific decisions remain future inputs. Generic/structural checks do not complete that execution path.
4. **Thermodynamic/statistical scope:** no adequate independent forward/reverse molecular samples, physical corrections/joint covariance, matched molecular ABFE/RBFE closure or production ceiling/profile is established. `binding_result=not_evaluated`. C3's general unmatched-physical-state closure-refusal contract remains unimplemented/unqualified. The user's bounded-sampling and separate Pearson r/Kendall tau guidance remains in force.
5. **Prior obligations:** G07 failures, seven sensitivity exceedances, 29 missing references and the unchanged QM continuation screen remain open. No historical scientific hold or gate/milestone was closed.

D took about 28 minutes through worker completion, and approximately 30–35 minutes including checkpoint work. Campaign wall time from approximately 10:46 UTC is about 3 hours 30 minutes, including user pauses, leaving roughly 1 hour 30 minutes in the tracked five-hour window at this checkpoint.

Stop here and wait for the user's instructions before worker E. E packaging/performance/HPC handoff and the final consolidated checks remain pending. No audit, release, push or cluster submission occurred.
