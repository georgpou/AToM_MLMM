# G03 routing/integration and combined M02 — v1 independent audit

**Reviewed worker/snapshot:** [Gate_03_v1_worker.md](Gate_03_v1_worker.md) and [Gate_02_v1_worker.md](Gate_02_v1_worker.md), branch `m02-analytic-atm`, exact submitted/reviewed HEAD `a13019390f9770a42a5711bbb98025bd571ea40b`; completed worker-tested source/input SHA `4c952dba5563572cf9e39527e64fe28ee201c385`; fetched parent/diff base `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.\
**Scope/profile:** independent G03-T1/T2/T3 and explicit **combined G02/G03/M02** review, all nine G02 and seven G03 stable checks on one `core-analytic-cpu` Reference/CPU snapshot, inheriting accepted M01.\
**Reviewer and finished time:** independent Codex `/root/m02_independent_audit`, GPT-6 family; exact runtime model/backend version and reasoning setting are not exposed. This reviewer authored no implementation or repairs. Finished 2026-10-02 12:40:59 UTC.\
**Verdict:** `changes_required` for G03 and combined M02.

## Evidence

The [companion G02 audit](Gate_02_v1_audit.md) records the full document/diff review, unchanged input identities, exact environment and command results, nine G02 assertions, independent numerical/FD controls and complete reproducible findings. It is part of this same independent combined review. The accepted [M01 v2 audit](../Milestone_01/Gate_01_v2_audit.md) is inherited for `core-analytic-cpu`; source and dependency prerequisites were rerun in the full suite and fresh nine-check strict validation.

All shell commands activated `/workspace/.onboarding/atom-mlmm-m02/activate.sh`; direct probes used `PYTHONPATH=src:.`. The exact pinned AToM source methods were inspected, including explicit group selection/child removal, both ligand/displacement/ATM construction paths, LangevinMiddle masks and worker state setting. No upstream patch was made. The adapter's narrow use of upstream methods through a partially constructed upstream object is consistent with the declared analytic scope; it does not qualify full upstream molecular preparation or asynchronous workers.

| Independently rerun checks | Observed result |
|---|---|
| Full G03 command: `python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v` | Exit 0; **38 passed in 3.55 s**, no skips |
| Full G02 command recorded in companion audit | Exit 0; **78 passed in 8.15 s**, no skips |
| `python -m pytest -q` | Exit 0; **164 passed in 27.20 s** |
| `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0; **163 passed, 1 deselected in 20.67 s** |
| Strict locked `validate.py --repository "$PWD"` | Exit 0; **all nine checks passed**, core NumPy 2.4.6 / separate Amber NumPy 1.26.4 |
| Separate pinned upstream `python -m pytest -q tests/test_uwham.py` | Exit 0; **1 passed in 2.09 s**, three datasets |
| Documentation/self-tests; whitespace | Exit 0 each; eight documentation self-tests passed |
| New review numerical probe | Exit 0; **66** comparisons, eight all-coordinate FD sweeps, eight upstream A-B-A cases; maximum energy/force errors **5.706546346573305e-14 / 2.2737367544323206e-13**, final FD **7.487415132345632e-9** in common units |
| New review admission probe with `--require-rejection` | Exit **1**; **13 expected rejection failures** among 20 observations; five rejection controls and two restoration positive controls pass |
| Preserved executable stale-artifact fresh offline replay | Exit 0; detects raw `u1` **7.987500000000001 vs 7.487500000000001**, error **0.5 kJ/mol** |

The [independent evidence guide](evidence/M02_v1_independent/README.md), [raw commands](evidence/M02_v1_independent/command-results.json.gz), [numerical cases](evidence/M02_v1_independent/independent-numerics.json), [admission results](evidence/M02_v1_independent/admission-results.json) and [snapshot check](evidence/M02_v1_independent/snapshot-check.json) preserve this review. All 126 source/input hashes match. Worker evidence and the independently replayed worker numerical script remain identified separately from the newly written review oracle. Initial worktree was clean; only audit logs and independent evidence were added.

| Stable check / requirements | Independent assessment |
|---|---|
| G03-01 / P0-REQ-011/021 | Actual pinned default route selects zero honestly named PythonForces and leaves originals; regression rejects it. Explicit group 1 routes all intended child forces once with originals removed and explicit report paths. |
| G03-02 / P0-REQ-012 | Actual LangevinMiddle masks, full versus selected forces, large `k=2000` marker and two real integration steps pass for preparation/ABFE/RBFE on Reference/CPU; omitted-mask controls reject. New numerical cases also check the actual integrator mask. |
| G03-03 / P0-REQ-012 | All-active group-0 preparation and reserved-group export are separate; physical original remains unchanged; export cannot be preparation input; stock group-0 omission reproduces/rejects. Preparation's fixed physical global-parameter guard remains open under M02-R2. |
| G03-04 / P0-REQ-021/022 | Both upstream protocol paths match direct/native/independent observables for local/environment providers, unequal complete groups and a shared physical builder. Child/schedule name collision violates physical independence outside the existing controls, M02-R2. |
| G03-05 / P0-REQ-010/021 | 0.5 fs -> 0.0005 ps, nm -> Angstrom and kJ -> kcal occur once; nonidentity final indices pass; upstream classes/keys/file conventions are confined to the adapter. Dependency-light/lazy import architecture tests pass. |
| G03-06 / P0-REQ-011/023 | Occupied reserved group, same-name duplicate, originals outside, and recursive ATM under ATM/CustomCV reject. Renaming an exact duplicate defeats content rejection, M02-R3. |
| G03-07 / P0-REQ-002/013/021 | Fixed full maps after construction/state changes/trusted fresh reload, immutable membership, runtime profile, System, mask, timestep, temperature, routing report and ordinary ATM auxiliary/schedule mutations reject. Portable State restores declared/auxiliary parameters; actual expression binding and colliding physical parameter ownership remain open, M02-R1/R2. |

All prefixes above are the full stable IDs `P0-TEST-G03-01` through `P0-TEST-G03-07`. Admission gaps prevent full-gate acceptance despite the passing existing nodes.

Combined M02 review establishes positive evidence for full `(u1,u0,expression)` tuple/raw/outside/total separation, complete real derivatives and units, `[2,0]` subset scatter, nonidentity real/final/model maps, unequal noncontiguous complete ligands, one physical builder/native assembler, MM-only motion, A-B-A/fresh reload, exact nonlinear production weights/directions/offsets/transitions and all-coordinate FD convergence. Real omission/double-child, stale descriptors, environment-gradient and factor-ten faults are detected by independent expected values; trusted digest-checked PythonForce loading rejects untrusted/corrupt bytes. Force ownership and actual integration masks are separately checked in all three stages. These positive controls are retained; the remaining findings concern admission/identity enforcement and physical content duplication.

## Findings

The same **M02-R1/R2/R3** findings, source locations, actual reproducers and minimal repair/closure requirements are fully recorded in [G02's findings](Gate_02_v1_audit.md#findings). They are not additional findings or a separate snapshot.

| Finding and importance | G03/combined implication | Required repair and closure check |
|---|---|---|
| **M02-R1 — blocking actual-expression/schedule mismatch** | Native and upstream artifacts are both admitted with actual `u0` and declared production softplus. Correct routing, fixed maps and hashes do not prevent a **2.565529535204135 kJ/mol** total-energy error. | Bind actual ATM expression/required globals at sealing and reload. Require all four wrong-expression admission probes to reject before evaluation while canonical native/upstream schedules, whitespace differences and trusted reloads pass. |
| **M02-R2 — blocking fixed physical global-parameter ownership** | Direct and preparation context/State mutation changes physical energy by **20.79 kJ/mol** under unchanged identities. Ordinary native/upstream auxiliary mutation already rejects and State restoration works, but a child `Lambda1` collides with schedule ownership in both routes, silently changing raw `u0` by **0.0315 kJ/mol**. | Common fixed-parameter guard for physical/preparation evaluation; reject physical/schedule global-name collisions in native/upstream construction and reload. Require all six new failure probes to reject; preserve both existing ATM mutation controls and both explicit restore positives. |
| **M02-R3 — blocking name-sensitive duplicate admission** | Export/native/upstream admit the exact duplicated PythonForce after only a rename; raw child energies double-count its contribution, despite recursive reports. Same-name controls reject. | Introduce a name/group-independent duplicate content fingerprint, retaining separate identity/report digests if needed. Reject all three renamed-duplicate probes and group-only variants, admit distinct physical parameters, and preserve recursive nesting/default-route/State/stale-artifact regressions. |

Use `PYTHONPATH=src:. python Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_admission.py --require-rejection --output /tmp/m02-admission-closure.json` for the preserved independent closure assertions. On v1 it exits 1; after repairs the required failure cases must become rejections without weakening the positive controls or numerical tolerances. Rerun applicable G02/G03/full/analytic checks and independently close the repairs on their exact new HEAD. No source repair was performed here.

## Decision and handoff

**Do not accept G03 or combined M02 on `a13019390f9770a42a5711bbb98025bd571ea40b`.** The prescribed tests and broader independent numerical controls pass, but the three reproduced findings violate declared-expression, fixed-Hamiltonian and one-owner contracts. The overall verdict is **`changes_required`**, carrying M01's accepted analytic prerequisite. Preserve these v1 audit/evidence artifacts; minimal repairs and their worker evidence require independent closure on a new exact snapshot before acceptance/publication or downstream gate claims.

Remaining profile limits are unchanged: analytic Reference/CPU transfer architecture only, nonperiodic all-real seven-particle fixtures, NVT, float64 analytic callbacks and at most 0.0005 ps. Caps, chemical/protein accuracy, full pretrained-model/G00-T2 qualification, GPU/G00-T3, periodic/actual electrostatic physics, molecular ABFE/RBFE/binding corrections and full asynchronous restart/replica exchange remain deferred; M00 physical-reference decisions still precede real chemical comparisons. No unsupported scope is accepted by the bundled MACE regression or installation smoke. The parent integrator owns STATUS, repairs, commits and publication; this reviewer added only the two audit logs and supporting audit evidence.
