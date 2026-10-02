# M02 fresh-agent continuation

The user paused the original implementer after context compaction and requested a handoff for a fresh agent. **No audit repair has been applied. The new regression draft has never been collected, imported or run.** Reassess the findings and proposed work with a fresh look; do not treat the implementer's suggestions as reviewed requirements.

## Authorized objective and current state

The original task is to finish M02, G02 first then G03, inheriting independently accepted M01 on `core-analytic-cpu`; run applicable checks and the full available suite; arrange independent combined M02 review, resolve findings, update STATUS/evidence, and commit/push **only `m02-analytic-atm`**. Keep main and the development predecessor unchanged, preserve existing work, scientific contracts, exact environment locks and scoped loading safeguards. The latest user instruction stops this implementer before new regression execution and delegates continuation to a fresh agent.

Read `AGENTS.md`, `README.md`, `docs/DEVELOPMENT.md`, `docs/project-0/STATUS.md`, [the original M02 handoff](M02-implementation-and-audit.md), G02/G03 and their relevant S01–S07 sections. Accepted M01 is recorded in [Gate_01_v2_audit.md](../../../Worker_Log/Milestone_01/Gate_01_v2_audit.md); its R1/R2 policy/locality/evidence-reference repairs must remain intact.

| Identity | Exact value |
|---|---|
| Working/new branch | `m02-analytic-atm` |
| Fetched parent and matching new-branch starting commit | `87146b4cc7fbd0b58d6688903a5ba081b813ac13` on `m00-audit-m01-development` |
| Unchanged main | `2d7bcc94f901738e39f536f16de84699d4e8d631` |
| G02 implementation | `9f36ccbe94bbfacc358586be6510c62bfe58b331` |
| G03 implementation | `2c1acefdbe7cecdc67d8bcf4138008a6207d5143` |
| Completed tested source/input commit | `4c952dba5563572cf9e39527e64fe28ee201c385` |
| Independently reviewed submission | `a13019390f9770a42a5711bbb98025bd571ea40b` |

The branch was created first from the fetched parent; starting SHAs and empty diff matched, with the accepted M01 handoff as an ancestor. The checkout was initially clean. The submission and subsequent audit/handoff additions change no source, tests, fixtures or environment inputs relative to the tested code commit. The final publication commit can be obtained with `git rev-parse HEAD`; it carries this handoff and the unchanged implementation.

## What the original implementer did

- Installed the existing exact locked two-environment CPU bundle at `/workspace/.onboarding/atom-mlmm-m02`, keeping main NumPy 2 and Amber NumPy 1.26 separate. The default prefix had an interrupted bootstrap, so a fresh custom prefix was used. No dependency, archive, lock or checkpoint-loading policy changed.
- Repaired a baseline **test-only** hardcoded setup prefix: `tests/unit/test_environment.py` now derives the setup root from activated `sys.prefix`, preserving all strict assertions. Initial baseline: one failed/46 passed; repaired baseline: 47 passed, analytic selection 46 passed/one deselected.
- Implemented immutable physical/transfer/schedule/restraint/alchemical/raw-energy records, explicit real/final/model mappings and `oldToNew`, importable analytic callbacks, one native assembler/evaluator, exact nonlinear production scheduling, independent energy/force and FD checks, and trusted hash-checked offline reloads.
- Added the seven-real-atom abstract fixture: unequal noncontiguous complete ligand groups, selected order `[2,0]`, nonzero B-ligand forces, environment coupling, hand-written transfer maps and nonzero outside harmonic restraint. It is an architecture probe, not a chemical reference.
- Implemented recursive routing, reserved-group production export, separate all-active group-0 preparation and the narrow pinned AToM adapter. The adapter invokes actual upstream construction/integrator/state-setting methods, keeps upstream keys/units/files inside the adapter, and tests actual masks and marker-driven motion.
- Added mutation/loading safeguards and deliberate numerical/compiled/callback faults, then committed the completed implementation and worker evidence. The implementer did not declare independent acceptance.
- Assigned a clean-context independent reviewer `/root/m02_independent_audit`, who authored no implementation and independently found the admission defects below. At the user's stop request, no production repair or new regression execution had occurred.

## Completed verification, not M02 acceptance

Use [G02 worker](../../../Worker_Log/Milestone_02/Gate_02_v1_worker.md), [G03/combined worker](../../../Worker_Log/Milestone_02/Gate_03_v1_worker.md) and their evidence for exact commands, outputs, profiles and identities.

| Check on the completed source | Worker result | Independent v1 rerun |
|---|---|---|
| G02 gate selection | 78 passed | 78 passed |
| G03 gate selection | 38 passed | 38 passed |
| Full available project suite | 164 passed | 164 passed |
| Analytic selection | 163 passed, 1 deselected | 163 passed, 1 deselected |
| Strict locked environment validation | 9/9 checks passed | 9/9 checks passed |
| Upstream UWHAM regression | 1 passed, three datasets | 1 passed |
| Documentation self-tests | 8/8 passed, zero errors | 8/8 passed, zero errors |

Worker numerical evidence has 16 native/upstream cases, maximum energy error `5.684341886080802e-14 kJ/mol` and force-component error `1.1368683772161603e-13 kJ/mol/nm`. Independent numerical probes use their own oracle, perturbed geometry and nonidentity final mapping: 66 cases, eight FD sweeps and eight upstream history cases; maxima `5.706546346573305e-14`, `2.2737367544323206e-13`, and final FD error `7.487415132345632e-9`, respectively.

These passes establish the tested valid paths. **The independent admission probes demonstrate scientific-contract failures; combined M02 is not accepted.** Frozen Reference limits remain `1e-8 kJ/mol` and `1e-7 kJ/mol/nm` per force component; direct/ATM starting limits `1e-4`/`5e-3` are unchanged. FD steps are `1e-3`, `1e-4`, `1e-5 nm`, with final component limit `1e-5 kJ/mol/nm`.

## Independently reproduced concerns

The authoritative v1 reproducer/results are [probe_admission.py](../../../Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_admission.py) and [admission-results.json](../../../Worker_Log/Milestone_02/evidence/M02_v1_independent/admission-results.json). Its `--require-rejection` run exited 1 with **13 failed expected rejections**. The independent audit logs record the decision and source locations.

1. **Actual expression versus declared schedule.** `seal_alchemical` and `AtmEvaluator` admit a native/upstream ATM whose actual expression is replaced with `u0`, while the record still declares production softplus. On the audited sample total energy changes from `9.683029535204136` to `7.1175000000000015 kJ/mol`. Both fresh sealing and direct reconstructed-artifact admission bypass the semantic check. XML hashes alone establish byte identity, not agreement with the schedule contract.
2. **Fixed physical global parameter ownership.** PhysicalEvaluator and preparation admit direct or State-restored Context changes from a physical global 2 to 200, producing energy `5.4825 -> 26.2725 kJ/mol` with unchanged physical/snapshot identities. Native/upstream ATM already reject a noncolliding global mutation and correctly restore that global on explicit state handover. However, a physical child global named `Lambda1` is admitted by both routes; changing the schedule from 0 to .3 changes raw `u0` from `5.2725` to `5.3040` under the same physical identity. Global schedule and physical ownership need independent examination.
3. **Renamed duplicate physical content.** Same-name duplicate controls are rejected, but renaming an exact PythonForce copy bypasses export/native/upstream duplicate checks. Raw energies become `u0=7.3125`, `u1=10.8675` instead of `5.2725`, `7.4875`. The existing duplicate fingerprint includes the force's name, which is a label. Investigate group/name normalization without weakening sealed ownership identity.

## Unverified draft and proposed repair ideas

[regression-draft.py.txt](../../../Worker_Log/Milestone_02/handoff/regression-draft.py.txt) preserves **34 proposed parameterized cases**. It is deliberately outside `tests/` with a `.txt` suffix. It has never been imported, collected or run and may itself contain mistakes. Review, rewrite or discard it; do not count it as evidence or assume its proposed coverage is sufficient.

The implementer considered checking actual versus declared ATM expression after whitespace normalization (pinned upstream has a harmless whitespace difference), required ATM schedule globals, and collisions with physical child globals at sealing and reload. Another idea is to pin all non-schedule Context global parameters in the common runtime guard so preparation is covered. For duplicates, a separate name/group-independent duplicate fingerprint could retain the existing name-preserving routing-report digest, preserving valid v1 artifact compatibility. **These are proposals, not applied or reviewed repairs.** Independently determine the smallest correct design and applicable tests before implementation.

The original implementer's main concern is that a green numerical suite can hide admission paths which report the wrong physical/schedule identity. Ensure the repaired guard checks the actual executed objects and parameter ownership, with positive controls for legitimate state changes. Possible additional runtime-object consistency gaps were considered but not reproduced; they are not audit findings. Avoid expanding into unrelated molecular features or treating speculation as evidence.

## Environment and continuation

In this shared workspace, activate in every shell:

```bash
source /workspace/.onboarding/atom-mlmm-m02/activate.sh
```

For a fresh machine, use the repository's [CPU installer/guide](../../../environment/cloud-cpu/README.md) and a suitable writable prefix. Source is tested through `pytest.ini`; direct probes need `PYTHONPATH=src:.`. Pinned AToM distribution is 8.5.0b0, source v8.5.0 commit `9e26c5a3811038be1c98e3be6af4c78cd0dd57a7`; full installed sources are `<setup-prefix>/sources/AToM-OpenMM`. PythonForce XML is executable: preserve explicit trust and expected SHA-256 before external loading. Do not install editable project metadata into the exact inventory or silently fetch replacement weights.

Recommended fresh-agent sequence:

1. Verify branch/HEAD/source hashes and read the v1 audit plus specs. Establish your own baseline and independently inspect the actual reproducers; do not infer acceptance from the counts above.
2. Preserve submitted v1 worker/audit/evidence unchanged. Use new attempt numbers for repairs. Probe scripts default to outputs beside themselves: **always pass `--output` to a new path** when rerunning, so historical evidence is not overwritten.
3. Develop meaningful failing regressions for the confirmed findings, implement the smallest correct repairs and rerun affected checks, G02/G03 selections and the full available suite. Preserve successful state changes, valid serialization/reload, strict environment checks and scientific limits.
4. Commit a precise repaired snapshot, submit new worker evidence and obtain **independent closure of all findings plus combined G02/G03/M02** on that same snapshot. Self-review cannot close the milestone. Update STATUS and AcceptanceRecord only from the actual decision.
5. Commit/push only `m02-analytic-atm`; verify remote identity and main/predecessor preservation. Report the exact final commit, tests, audit decision, evidence and limitations.

Current scope remains nonperiodic seven-real-atom analytic Reference/CPU NVT with the conservative `0.0005 ps` timestep. The bundled real-weight MACE example passes in the full suite but does not qualify chemical accuracy. Caps, full pretrained-model/GPU qualification, actual electrostatic/periodic physics, molecular ABFE/RBFE, binding corrections and full asynchronous restart/replica exchange remain with their owning gates. M00 G05/G07 physical-reference decisions remain open. After accepted M02, G04 and the separate G08 analysis path can proceed under their prerequisites.
