# G06 periodic ledger and geometry — v1 independent audit

**Reviewed worker:** [Gate_06_v1_worker.md](Gate_06_v1_worker.md), branch `m03-g06-g07`.\
**Exact reviewed HEAD:** `ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b`.\
**Tested implementation/source:** `c584086da68654b07f1a477d7ce1e48da42a9838`; later submitted commits change reporting only.\
**Accepted predecessor:** `08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`.\
**Reviewer:** independent GPT-6.1-sol, MAX reasoning; audit only, no implementation or delegated reviewers.\
**Finished:** 2026-10-04, UTC; exact final preservation time is in [final-state.json](evidence/G06_G07_v1_independent_sol61_max/final-state.json).\
**Verdict:** **accepted_for_scope**, G06-T1/T2/T3 and all six stable assertions on the narrow numerical profile below.

The supported profile is CPU-executed small fixed-volume single points, **OpenMM 8.6.1 Reference double** and pinned MACE-OFF23-small on CPU float64, with one ordinary PME NonbondedForce, orthorhombic boxes, the recorded cutoff/switch/mesh, no offsets, LJPME, custom mixing or analytical dispersion correction. This does not qualify the OpenMM CPU PME precision profile, GPU, molecular dynamics, variable-volume/virial behavior, protein physics, actual electrostatic embedding or binding free energies. Existing G04/G05 decisions are inherited for their stated scopes.

## Independent evidence

Every scientific shell sourced `/workspace/atom-mlmm-g05-v2/activate.sh` from `/workspace/AToM_MLMM-m03-g06-g07`; heavy checks were serialized with the inherited two-thread settings. All new evidence is under [G06_G07_v1_independent_sol61_max](evidence/G06_G07_v1_independent_sol61_max/README.md). Source, tests, fixtures, locks, model and submitted scientific evidence were frozen throughout.

| Command/check | Actual result |
|---|---|
| `python tools/monitor_cpu_check.py --output …/full-cpu-suite -- python -m pytest -q` | Exit 0; **381 passed in 259.67 s**, no skipped/deselected tests. [Output](evidence/G06_G07_v1_independent_sol61_max/full-cpu-suite/command.log), [receipt/resources](evidence/G06_G07_v1_independent_sol61_max/full-cpu-suite/result.json). |
| Focused `pytest` over the three G06 modules, joint G07, extension and matrix modules, `-v` | Exit 0; **45 passed in 70.03 s**, including **23 G06 cases**, ten joint, ten extension and two matrix cases. [Exact command/result](evidence/G06_G07_v1_independent_sol61_max/focused/result.json), [nodes](evidence/G06_G07_v1_independent_sol61_max/focused/command.log). |
| `PYTHONPATH=src:. python …/verify_inputs_and_arithmetic.py` | Exit 0; all **181 submission hashes**, **1,924 frozen tracked files (byte-identical)**, **75 new fixture hashes**, **46 accepted G05 records** and actual term dispositions for all 50 joint descriptions independently verified. [Result](evidence/G06_G07_v1_independent_sol61_max/inputs-and-arithmetic.json). The earlier invocation without `PYTHONPATH` failed before evaluation; its setup log is retained. |
| `PYTHONPATH=src:. python tools/monitor_cpu_check.py --output …/additional-probes -- python …/independent_probes.py` | Exit 0; independent cross-face Ewald/exception and switched-LJ checks, winding and second-ligand clearance rejection, 24 alternative-cap periodic route comparisons and five directional FD sweeps. [Measurements](evidence/G06_G07_v1_independent_sol61_max/independent-probes.json), [receipt](evidence/G06_G07_v1_independent_sol61_max/additional-probes/result.json). |
| `python tools/monitor_cpu_check.py --output …/strict-environment-capture -- python …/strict_environment.py` | Exit 0; unchanged installed validator, **9/9 checks passed**. Only new log/preparation/result destinations were redirected; prior environment outputs are hash-identical. [Full result](evidence/G06_G07_v1_independent_sol61_max/strict-environment-result.json). |

The independent full-suite process-tree RSS peak was **1.618 GiB**, child maximum RSS **1.561 GiB**. Cgroup usage including cache peaked at **7.999 GiB** under the 8 GiB limit; `max` increased by 36, OOM/OOM-kill deltas were zero. Minimum free disk was **20.095 GiB**. These are measurements for this run, not bounds for larger systems or reference calculations.

## Stable assertions and numerical interpretation

| Stable assertion | Independent scope and evidence |
|---|---|
| **G06-01** real ML-MM interactions retained; inert cap | The actual builder preserves every real charge/LJ parameter, keeps real ML-MM cross terms under probe movement, and adds a zero-charge/zero-epsilon cap. Original/retained masks agree for the expected real cross terms; explicit Lorentz–Berthelot pairs check LJ. The complete artifact ledger includes original exceptions replaced by exclusions, added ML exclusions and the changed exception-distance convention. |
| **G06-02** four-charge-mask PME identity | Lattice Ewald independently includes reciprocal, self and uniform-background terms for nonneutral subsets. All four energies and the cross identity pass at fixed realized alpha/mesh; negative charge scaling obeys the quadratic relation. The new cross-face exception probe independently checks **both** periodic and nonperiodic exception distances. Maximum absolute Ewald/PME discrepancy is **9.163e-5 kJ/mol**, within the unchanged 1e-4 limit; explicit switched-LJ errors are <=4.5e-15 kJ/mol. |
| **G06-03** image/cap/bulk reconnection detection | Exhaustive image enumeration checks minimum-image vectors; setup clearance catches primary-box-hidden image contact and complete-protein MM contact. The new probe catches contact with another complete ligand. Caps are included as obstacles. The 0.2 nm setup margin supplies no trajectory guarantee or free-energy correction. |
| **G06-04** wrapping and admitted seam behavior | Bond-connected molecules are reconstructed before native sites. Real-model energies and all real forces agree for whole-molecule/individual-atom wrapping and face crossings. Box A–B–A restores the first result; the new unequal-ligand alternative-cap case repeats this through direct/native ATM/AToM. Half-box bonds and winding cycles explicitly reject; the new cycle probe verifies the latter. |
| **G06-05** actual model graph and shifts | Tests inspect actual ASE/MACE edges and periodic shifts, including the actual cap input, against separate image enumeration. Both sides of the local cutoff are retained and satisfy energy/force continuity limits. Native MACE uses independently enumerated graph tensors rather than the production ASE graph. Evidence covers the safe tested boxes with a unique short-range image. |
| **G06-06** unsupported physics/boxes reject | Actual construction rejects particle/exception charge offsets, LJPME, custom forces/mixing, triclinic cells, dispersion correction and two NonbondedForces. Runtime triclinic/unsafe-cutoff boxes reject. The inert analytic substitute is the only admitted periodic analytic ledger probe. |

The ledger is the difference of the actual original and retained OpenMM force objects (`ledger.py:85–163`), not a separately parametrized capped-MM energy. The model is added once. All real charge/LJ parameters remain; short-range ML pair exclusions do **not** erase the entire periodic ML-subset electrostatics. The retained cavity-ligand image contribution is measurably nonzero. The upstream switch to periodic exception distances is explicitly recorded at `ledger.py:119–127`, rather than hidden inside a claimed unchanged MM description.

The original tiny fixture's deliberately large internal exception energy, **104399503.22785223 kJ/mol**, is a synthetic removal stress case; retained energy is **9.271173436763092 kJ/mol**. It is not a physical molecular preparation. The saved original/retained XML, ledger and diagnostics are hash-checked and independently replayed in [final-state.json](evidence/G06_G07_v1_independent_sol61_max/final-state.json).

Force checks use native derived sites and one native parent redistribution. The separate formula oracle and FD sweeps test both parents. Deliberately omitting unwrapping fails the wrapped-cap force comparison. Integrated fresh tests also detect omitted cap/environment derivatives and doubled parent propagation. No generic long-range or cap free-energy repair is introduced.

## Findings

**No mathematical or coding defect requiring repair was found within the reviewed numerical scope.** No gate tolerance or scientific input was changed. The remaining physical G07 findings belong to [its audit](Gate_07_v1_audit.md).

| Finding/importance | Evidence/location | Required closure |
|---|---|---|
| Scope boundary, not a defect: periodic production remains unqualified | `geometry.py:75–110`, `embeddings/mechanical.py:110–114`, G06-T3 and S04/S06 | Before widening the profile, separately establish trajectory excursions, seam/domain safety, relevant restraints and thermodynamic obligations, larger-system/platform precision and any new box/dispersion policy. No such unrun checks are counted as passes here. |

## Decision and handoff

Accept **G06-T1/T2/T3 and G06-01 through G06-06 for the stated Reference-double/MACE-CPU numerical single-point profile**. This is actual independent approval of that scope, not approval of periodic protein production or combined M03. No source repair is required by this audit. Parent integration should update STATUS with this exact scope; the auditor did not change STATUS or publish a branch.
