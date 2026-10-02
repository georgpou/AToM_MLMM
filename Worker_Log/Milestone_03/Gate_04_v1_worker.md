# G04-T1/T2/T3 and all seven checks — v1 worker

**Scope:** full G04 analytic boundary implementation and worker verification for `core-analytic-cpu`, nonperiodic Reference/CPU; independent acceptance pending.\
**Outcome:** `ready_for_audit`.\
**Finished:** 2026-10-02 14:52 UTC.\
**Worker:** Codex `/root`; deployed model label/version and reasoning setting not exposed.\
**Branch/base:** `m03-link-boundary`, created unused at exact published handoff `c63634ca7567428e294a73fa432d42026f9fd38a`; accepted M02 publication verified as ancestor.\
**Tested source/input commit:** `55df6a7d25e7a4de607a13b7d87c327feddecb34`. The submission commit adds only this worker/evidence and STATUS. Resolve its exact SHA with `git log -1 --format=%H -- Worker_Log/Milestone_03/Gate_04_v1_worker.md`.\
**Independent reviewer:** required `gpt-6-astra`, `high`, `fork_turns="none"`; **not launched**, at the user's explicit temporary-stop request. No independent audit or G04 acceptance is claimed.

## Changes and scientific decisions

Read AGENTS, README, DEVELOPMENT, STATUS, the exact G04 handoff/gate, relevant S01–S07 contracts, inherited M00/M01 and M02 v2 audits/acceptance and CPU guide. This assignment covers G04-T1/T2/T3 and P0-TEST-G04-01 through 07; M03 closes later at G07. The [implementation plan](evidence/G04_v1/implementation-plan.md) records inline execution and scope.

`hybrid.py`, `embeddings/mechanical.py` and `models/analytic_boundary.py` implement a narrow registered weight-free substitute through actual pinned OpenMM-ML `MLPotential.createMixedSystem` mechanical construction. The builder rechecks inherited partition/connectivity admission, consumes `oldToNew` and final topology differences, and derives cap identity/parents/type/distance from the actual System. The [neutral ethane/methane fixture](../../fixtures/one_cut_alkane/README.md) inherits the original GAFF bytes, closes the selected methyl with one massless H cap, and transfers the whole separate methane. The explicitly requested 0.117 nm distance distinguishes constructed parameters from upstream defaults; it is a parameter of the unchanged S04 fixed-length rule, not a chemical-reference decision.

`schema.py` adds `LinkRecord` and optional `PhysicalBundle.links`, complete cap/model mapping and final-particle coverage, alias/mass/version rejection. Empty links are omitted from canonical encoding, preserving old schema-1.0 real-only identities, including the inherited stale artifact. Capped records require boundary-builder version 1. There is no unit/energy/force/ensemble/sign/periodic change; scientific specifications and tolerances are unchanged. `geometry.py` creates derived placeholders and validates actual site definitions; `atm.py` recomputes sites after every position assignment. No production manual parent projection or internal-site copying was added. Routing validates site identity while preserving all M02 expression/global/collision/duplicate guards.

`ledger.py` compares original and actual retained MM parameters, including duplicate terms, real charges/LJ, exceptions, added exclusions/inert cap and constraints. The manifest preserves original and retained XML plus exact dispositions. The Hamiltonian remains actual retained MM + model; removed MM is the full-minus-retained diagnostic. Dedicated distinctive bonded graphs separately pin wholly-ML and central/connectivity predicates for proper/improper torsions and angles, boundary bonds, exceptions and constraints.

The [pre-repair nested diagnostic](evidence/G04_v1/diagnose_nested.py) found correct standalone and native-ATM parent redistribution on Reference/CPU, maximum error 1.1102230246251565e-16. No nested propagation repair is warranted. The meaningful geometry RED exposed the common evaluator's missing site recomputation (cap stayed at its zero placeholder; maximum coordinate error 0.04219033199491509 nm). A one-line recomputation fixed it. Separate real failures covered FD restoration and cap-ID/MM-ID alias admission. Initial absent-builder/ledger API failures are recorded separately and do not constitute numerical evidence.

`tests/link_oracle.py` independently derives S04 cap position/Jacobian/negative gradients; it calls no production callback, map or mixer for expected values. Component FD sweeps cover every real coordinate, axial/perpendicular parents, environment, ligand, invariant force/torque and mapped ATM states. Full retained-GAFF FD exhibited second-order truncation: maximum component errors 1.22755, 0.0122755 and 0.000122754 at required 1e-3/1e-4/1e-5 nm. Adding 1e-6 nm reaches 1.23460e-6 without changing the strict 1e-5 component target; required-step RMS already satisfies S06 at 1e-5. Initial failed strict-component runs are preserved. One initial rerun also exposed a test-helper tuple/array conversion error, corrected without changing limits. Executable negatives omit raw cap propagation, pre-project then let native machinery project again, omit the real environment force, and freeze cap inputs. Nonidentity controls move the cap to final index 5 and repeat capped ATM/FD. Trusted hash-checked fresh-process reload denies connect/DNS and uses a new empty cache.

## Verification

All commands activate `/workspace/atom-mlmm-g04-v2/activate.sh`, from `/workspace/AToM_MLMM-m03-link-boundary` except the separately stated upstream directory. Direct scripts use `PYTHONPATH=src:.`. [Raw captures](evidence/G04_v1/README.md) preserve command arguments, cwd, timestamps, HEAD, complete output and exits; the [151-input manifest](evidence/G04_v1/source-input-manifest.json) identifies the tested source/fixtures/environment. Main Python 3.11.16/NumPy 2.4.6 and Amber NumPy 1.26.4 remain separate, with OpenMM 8.6.1 and OpenMM-ML 1.8. The unchanged bundle was freshly replayed: v1 hit the standard Conda-registry sandbox restriction, v2 succeeded with authorized registry access. Both installation logs are preserved; no earlier filesystem was required.

| Check | Actual command/result |
|---|---|
| Own unchanged baseline | `python -m pytest -q`: **238 passed**; analytic selection **237 passed / 1 deselected**; strict validation **9/9**, all exit 0 |
| Full G04 | `python -m pytest tests/integration/test_link_geometry.py tests/integration/test_boundary_ledger.py -v`: **24 passed**, all seven stable nodes and extra controls, exit 0 |
| Full available suite | `python -m pytest -q`: **262 passed**, exit 0 |
| Analytic selection | `python -m pytest -m 'not gpu and not model_assets and not slow' -q`: **261 passed / 1 deselected**, exit 0 |
| G02 inherited | Four-file G02 command in `final-g02.json.gz`: **78 passed**, exit 0 |
| G03 inherited | `python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v`: **38 passed**, exit 0 |
| M02 admission safeguards | `python -m pytest tests/contracts/test_m02_admission.py -v`: **74 passed**, exit 0 |
| G04 numeric capture | `python Worker_Log/Milestone_03/evidence/G04_v1/reproduce_numerics.py`: six independent cap/environment/balance comparisons and three full mapped-ATM sweeps; maximum force error **1.38778e-16**, final FD error **1.23460e-6**, exit 0 |
| Preserved independent M02 numerics | Byte-identical copied oracle: **66 comparisons / 8 all-coordinate FD sweeps / 8 upstream A-B-A**, maximum errors unchanged at 5.70655e-14 energy, 2.27374e-13 force and 7.48742e-9 final FD, exit 0 |
| Preserved admission replay | Explicit new output: **18 rejections / 2 restoration positives**, exit 0 |
| Trusted offline stale replay | Inherited artifact detects expected **0.5 kJ/mol u1** error, exit 0; old outputs unchanged |
| Strict environment | `python /workspace/atom-mlmm-g04-v2/validate.py --repository /workspace/AToM_MLMM-m03-link-boundary`: **9/9 passed**, exit 0 |
| Separate upstream | `python -m pytest -q tests/test_uwham.py`, cwd `/workspace/atom-mlmm-g04-v2/sources/AToM-OpenMM`: **1 passed**, three datasets, exit 0 |
| Preservation | **212 inherited evidence/spec/environment/model/example/fixture files byte-identical** to handoff; original clean `work` checkout remains untouched; protected remote tips recorded |

Documentation/self-test and whitespace submission checks are captured after writing these report-only files. No skip qualifies an unavailable model/GPU profile.

## Handoff and stopping point

The user requested a temporary stop **immediately before launching Astra**. [Resume instructions](evidence/G04_v1/RESUME.md) specify the exact fresh-context reviewer call, frozen snapshot resolution, source/input checks and outstanding closure work. Reserve `Gate_04_v1_audit.md` for the actual independent reviewer; do not create a self-authored or placeholder audit. Submitted v1 evidence must remain immutable; substantive repairs need unused attempts and independent full-G04 closure.

No confirmed blocker remains in the worker's tested G04 scope, but **acceptance is pending independent Astra high review**. After review, resolve findings with meaningful regressions, obtain full-G04 closure, record acceptance/STATUS and publish only the child. Stop at accepted G04. G05 model-asset/loading and predeclared physical references, G06 periodic/interaction ledger, then G07 combined M03 follow their actual prerequisites; G08 is separate M04 analysis. M00 physical-reference decisions remain open before chemical comparisons. Molecular/chemical/protein, GPU/full-model, periodic/actual electrostatic and full asynchronous workflow qualification remain deferred.
