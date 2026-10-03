# G06 periodic ledger and geometry — v1 worker

**Scope:** G06-T1/T2/T3 and all six stable assertions; fixed-volume small-system mechanical PME single points, OpenMM Reference double and pinned MACE CPU float64.\
**Outcome:** ready_for_audit; no independent periodic acceptance claimed.\
**Finished:** 2026-10-03, UTC.\
**Snapshot:** child `m03-g06-g07`, accepted G05 base `08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`; exact tested source and artifact hashes are in the shared [snapshot](evidence/G07_v1/snapshot.json). Subsequent worker/STATUS/verification records change reporting only.

The mechanical builder now admits one standard PME NonbondedForce in a positive orthorhombic box and records the exact retained/removed boundary terms. Unsupported force classes, charge offsets, LJPME, dispersion correction, triclinic cells and unsafe cutoffs are rejected. Caps retain zero classical charge/LJ and native real-parent derivatives. The ledger explicitly records the upstream change to periodic exception distances. No electrostatic tail repair or free-energy correction is added.

Separate charge and LJ diagnostics resolve PME once and use identical realized alpha/mesh for all four masks. Charge exceptions are masked consistently, including nonneutral subsets and OpenMM's uniform-background convention. Independent lattice Ewald, quadratic charge scaling, explicit switched Lorentz–Berthelot pairs and the actual builder ledger check these results.

Bond-connected molecules are reconstructed before native cap sites. Ambiguous half-box bonds and winding graphs are outside the admitted domain. Tests exercise primary-box faces, a wrapped cap, A–B–A box changes, actual ASE/MACE edges and periodic shifts, cutoff crossings, and deliberate omitted-unwrapping force faults. Initial bulk clearance includes the complete protein, caps and other ligands with the specified cutoff-plus-0.2 nm setup margin; no trajectory safety or thermodynamic restraint is inferred.

The [periodic fixture](../../fixtures/periodic_ledger/manifest.json) preserves original/retained XML, complete ledger, coordinates, box, inventories and mask results. Its synthetic internal exception deliberately has sigma 1 nm and epsilon 0.025 kJ/mol, producing a large original stress energy (104399503.22785223 kJ/mol versus retained 9.271173436763092). This distinctive removed term is a diagnostic, not a chemical preparation. A mistakenly included empty self-hash was removed from the new manifest; the initial manifest is retained in [evidence](evidence/G06_v1/manifest-before-self-entry-fix.json). All seven final fixture hashes verify.

## Verification

Every scientific shell activated `/workspace/atom-mlmm-g05-v2/activate.sh`; working directory was `/workspace/AToM_MLMM-m03-g06-g07`. Main/Amber were rebuilt under unchanged locks. Scientific/model threads were two and heavy checks were serialized.

| Check | Actual command/result |
|---|---|
| Accepted-base baseline | `python -m pytest -q`: 336 passed in 180.08 s; [log](evidence/G06_v1/baseline.log) |
| Intended missing-feature RED | [Mask/ledger](evidence/G06_v1/red-ledger.log) and [builder/geometry](evidence/G06_v1/red-builder-geometry.log) failures preserved |
| Initial G06 full CPU suite | `python -m pytest -q`: 356 passed in 183.71 s; [log](evidence/G06_v1/full-suite.log) |
| Final G06 stable assertions and controls | `python -m pytest tests/integration/test_mechanical_pme.py tests/integration/test_masked_interactions.py tests/integration/test_periodic_geometry.py -q`: **23 passed in 7.83 s**, exit 0; [log](evidence/G06_v1/final-focused.log) |
| Final available CPU suite | `python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v1/final-cpu-suite -- python -m pytest -q`: **381 passed in 253.35 s**, exit 0; [receipt/resources](evidence/G07_v1/final-cpu-suite/result.json) |
| Strict environment | `python /workspace/atom-mlmm-g05-v2/validate.py --root /workspace/atom-mlmm-g05-v2 --repository "$PWD"`: **9/9 passed**, exit 0; [actual output](evidence/G07_v1/final-environment.json) |
| Documentation | `python tools/check_docs.py --self-test --output Worker_Log/Milestone_03/evidence/G07_v1/documentation-final.json`: **0 errors / 8 self-tests passed**, exit 0; [final result](evidence/G07_v1/documentation-final.json) |
| Preservation | [Check/result](evidence/G07_v1/reference-preservation.json): 1,733 of 1,740 accepted-base files byte-identical; seven intended existing source changes only. All 46 accepted reference records, model, frozen scientific inputs, locks and previous evidence unchanged. All 75 newly declared fixture-file hashes verify. |

The first integration runs preserved a tuple/NumPy-coordinate comparison error and an over-strict A–B–A exact-equality assertion (5.68e-14 rounding). Geometry now supplies tuple coordinates; the assertion uses the already approved S06 numerical limits, with no scientific relaxation. Both failed runs remain in the evidence directory.

Final sampled process-tree RSS peaked at 1.632 GiB; child maximum RSS was 1.562 GiB. Total cgroup usage, including file cache, reached the 8 GiB cap with 1,944 additional `max` events; OOM and OOM-kill deltas were zero. Minimum sampled free disk was 20.10 GiB. This is CPU-suite telemetry, not a memory bound for larger reference jobs.

## Handoff

Independent review should inspect the exact snapshot, all six G06 assertions, actual exception-distance ledger, nonneutral PME oracle and wrapped native-cap graph/force evidence. Reviewer choice is **GPT-6.1-sol/MAX**. No reviewer was spawned and no G06 audit is fabricated. Protein, GPU, triclinic, variable-volume dynamics, electrostatic embedding and binding qualification remain outside this demonstrated scope. G07 software composition is recorded separately; its physical sensitivity failures prevent combined M03 closure.
