# G03 routing/integration and combined M02 — v2 independent audit

**Reviewed workers:** [G03 v2](Gate_03_v2_worker.md) and [G02 v2](Gate_02_v2_worker.md).\
**Reviewed snapshot:** branch `m02-analytic-atm`; exact submitted/reviewed HEAD `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`; repaired source/input commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`; handoff base `a8098a43d46df76b981861aa8dec0522d31be966`; development predecessor `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.\
**Scope/profile:** independent G03-T1/T2/T3 and **combined G02/G03/M02**, all nine G02 and seven G03 stable checks plus M02-R1/R2/R3 closure, on one `core-analytic-cpu` Reference/CPU snapshot.\
**Reviewer:** Codex `/root/m02_v2_independent_audit`, configured **gpt-6-astra**, reasoning **high**; deployed backend version **not exposed**. This reviewer authored no implementation or repair.\
**Finished:** 2026-10-02 13:34:30 UTC.\
**Verdict:** **G03 and combined G02/G03/M02: accepted_for_scope**. **M02-R1, M02-R2 and M02-R3: closed** on this exact snapshot.

## Evidence

[The companion G02 audit](Gate_02_v2_audit.md) is part of this same independent combined review. It records document/source/test inspection, snapshot and all-127-input equality, preservation of all 28 handoff milestone files, unchanged definitions/limits/locks/loaders, exact commands, numerical oracle provenance, complete findings and additional independent probes. Its evidence is incorporated here, not a different snapshot or self-approval. The inherited [M01 v2 independent audit](../Milestone_01/Gate_01_v2_audit.md) remains accepted for `core-analytic-cpu`; the current full/analytic suites reran the prerequisites, including prior M01 policy/locality/evidence-reference guards and environment/source identity checks.

All commands activate `/workspace/.onboarding/atom-mlmm-m02-v2/activate.sh`; direct scripts use `PYTHONPATH=src:.`. [Raw command evidence](evidence/M02_v2_independent/command-results.json.gz) includes cwd, exact command arguments, UTC times, exits and output. [The evidence guide](evidence/M02_v2_independent/README.md) locates supplemental probes, preserved tooling failures and final input checks.

| Independent rerun | Result |
|---|---|
| `python -m pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v` | Exit 0; **38 passed in 6.34 s** |
| Original G02 four-file command | Exit 0; **78 passed in 13.51 s** |
| Admission regressions | Exit 0; **74 passed in 3.05 s**; three selections total **190**, with no skips |
| Full suite | Exit 0; **238 passed in 41.83 s** |
| Analytic suite | Exit 0; **237 passed/1 deselected in 41.46 s** |
| Strict locked validation / separate upstream UWHAM | Exit 0 each; **9/9** checks / **1 test**, three datasets |
| Documentation/self-tests and whitespace | Exit 0; eight documentation self-tests pass |
| Preserved independent admission probe | Exit 0; **18 required rejections and 2 restoration positives** |
| Preserved independent numerical oracle, copied byte-identically | Exit 0; **66 comparisons, 8 all-coordinate FD sweeps, 8 upstream A-B-A cases** |
| Additional independently authored closure probe | Exit 0 after corrected instrumentation; **120 rejections, 9 positive controls** |
| Old trusted stale artifact, fresh process/empty cache/network denied | Exit 0; expected raw `u1` **0.5 kJ/mol** error detected |

The numerical replay has maxima **5.706546346573305e-14 kJ/mol** energy, **2.2737367544323206e-13 kJ/mol/nm** force component, and **7.487415132345632e-9 kJ/mol/nm** final FD error. Reference limits remain `1e-8`/`1e-7`; direct/ATM limits `1e-4`/`5e-3`; FD steps `1e-3`, `1e-4`, `1e-5 nm` and final component limit `1e-5`. Worker/test oracles, independently authored v1 replay, and the new admission/Cartesian-increment checks are identified separately. No tolerance or scientific contract changed.

## Routing, integration and combined contract review

Inspected actual pinned upstream `add_forces_to_atmforce`, both protocol `set_atmforce` paths, full-particle displacement construction, LangevinMiddle integration mask and `_worker_setstate`. Explicit group selection copies/removes every intended child; default name routing selects none of the honestly named PythonForces in the regression. The adapter uses the real upstream constructors and worker method. Its narrow initialization of an upstream worker object exercises state-setting behavior only; it grants no full asynchronous workflow qualification. Units, keys and filenames remain confined to the adapter. No upstream patch was needed.

| Stable G03 check | Assessment on the exact repaired snapshot |
|---|---|
| P0-TEST-G03-01 | Actual default-routing failure remains an executable rejected control. Explicit reserved-group routing places physical children exactly once under ATM and removes originals, with recursive ownership/report paths. |
| P0-TEST-G03-02 | Full versus actual integrator-selected forces agree with the large `k=2000` marker for preparation/ABFE/RBFE on Reference/CPU. Two real integration steps move the marker coordinate; omitted-mask controls reject. |
| P0-TEST-G03-03 | Separate group-0 all-active preparation and reserved-group export preserve original physical identity. Export cannot enter preparation; stock group-0 omission is detected. Common fixed-parameter guards now reject physical/preparation direct and State-restored mutations. |
| P0-TEST-G03-04 | Both upstream protocols reproduce native and independent full-real-force/raw-energy answers for local/environment providers, unequal complete groups and a shared physical builder. Physical globals cannot share any varying or fixed schedule name; moved-ligand global controls preserve both raw endpoints under state changes. |
| P0-TEST-G03-05 | Nonidentity final maps, 0.5 fs to 0.0005 ps, nm to Angstrom and kJ to kcal conversions remain checked exactly at the adapter boundary. Dependency-light/lazy import checks pass. |
| P0-TEST-G03-06 | Nested ATM under ATM/CustomCV, occupied reserved group and originals left outside reject. Exact duplicate content now rejects despite rename/regroup; same-name distinct parameters remain admitted. Name-preserving ownership/report identity and old trusted artifact compatibility remain intact. |
| P0-TEST-G03-07 | Full maps/membership, runtime/System/report/mask/timestep/temperature and parameter guards pass after native/upstream construction, legitimate schedule updates, explicit State restoration and trusted fresh reload. Actual expression/required globals and physical collisions reject at reconstructed admission before Context construction. |

Together with all nine G02 rows in the companion audit, these establish the required combined review: explicit `(u1,u0,expression)` raw ordering; physical/outside/total/softened separation; every influencing real derivative and common unit; selected-particle scatter and nonidentity real/final/model mapping; complete unequal noncontiguous ligands; a common physical builder/assembler for both protocol shapes; MM-only motion and A-B-A; exact nonlinear nested chain-rule/transition/offset behavior; component finite differences; deliberate wrong-index, omission, duplicate, stale-descriptor, missing-MM-gradient and factor-ten faults; trusted offline reload; distinct preparation/production force ownership and actual active integration masks. The repaired admission checks bind these numerical claims to declared physical/schedule identities.

## Findings and decision

| Finding | Independent closure for G03 and combined M02 |
|---|---|
| **M02-R1** | **Closed.** Executed ATM expression and required unique globals are bound at sealing and reconstructed artifact admission. Every production global was challenged as missing/duplicate on native/upstream artifacts before Context creation; canonical/whitespace/linear controls and nonlinear numerics pass. |
| **M02-R2** | **Closed.** Common fixed physical Context-global guards cover direct/preparation and externally restored State. All ten schedule names, including fixed soft-core/offset names, reject physical collisions before native/upstream construction and at sealing/reload after verified child/source matching. Requested schedule updates and explicit restoration of stale auxiliary values remain correct. |
| **M02-R3** | **Closed.** Duplicate-content admission ignores name/group while ownership/report hashes retain names. Renamed/regrouped PythonForce/CustomExternalForce copies reject in all routes; same-name distinct parameters, recursive ownership and old trusted artifacts pass their applicable checks. |

**Accept G02-T1/T2/T3, G03-T1/T2/T3, both complete gates and combined M02 for `core-analytic-cpu` on `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`, carrying independently accepted M01.** No remaining blocking finding was identified within this scope. The v1 audit decisions remain historical `changes_required` for their earlier snapshot; this v2 closure supersedes them only for the exact repaired source/input snapshot above.

Scope is seven-real-atom nonperiodic analytic Reference/CPU transfer architecture, float64 callbacks, fixed complete ligand membership/maps, NVT and timestep at most **0.0005 ps**. Molecular ABFE/RBFE, chemical/protein accuracy, caps, GPU/full pretrained-model, periodic/actual electrostatic physics, binding/corrections and full asynchronous preparation/restart/exchange remain deferred. The passing bundled MACE example and UWHAM regression do not extend that scope. M00 physical-reference choices remain open before G05/G07 chemical comparisons.

G04 and the separate G08 path may proceed under their own prerequisites after the integrator records this acceptance. The reviewer changed no production/test source, STATUS, refs or commits and performed no publication. The parent integrator owns acceptance records, STATUS and authorized branch publication. No remote preservation claim is inferred from the absent local predecessor remote-tracking ref.
