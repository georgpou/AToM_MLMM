# G05 local model adapter implementation plan

> **For agentic workers:** Use superpowers:executing-plans for inline implementation. The user authorizes setup and G05-T1/T2/T3 while M00 choices are discussed; only the specified independent reviewers are delegated. Preserve this record across continuations.

**Goal:** Qualify the bundled MACE-OFF23-small checkpoint through the accepted mechanical builder, including independently reviewed frozen quantum checks before full G05 acceptance.

**Architecture:** Keep physical construction in `hybrid.py` and the inherited mechanical boundary sealer. Put trusted asset/calculator loading at `models/mace.py`; use a separate direct-model reference with independently enumerated nonperiodic edges and autograd of `energy`. Reuse unchanged real-force/map/ATM/ledger contracts.

**Tech stack:** Locked core/Amber CPU environments; PyTorch 2.8.0, MACE 0.3.16, OpenMM 8.6.1, OpenMM-ML 1.8; a separate frozen Psi4 reference environment only after the user's resource choice.

**Spec:** [G05](../gates/G05-local-model-adapter.md), [G00](../gates/G00-environment-and-provenance.md), accepted S01–S07 contracts, and the proposed [M00 reference plan](M00-neutral-reference-plan-v2.md). M00-dependent tasks remain blocked until the exact plan is agreed and independently reviewed.

## Global constraints

- Base `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`; only child `m03-reference-g05` may be committed/pushed. Preserve protected refs and submitted logs/evidence.
- Checkpoint SHA-256 `165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`; academic noncommercial permission; CPU float64; output `energy`.
- Same retained-MM plus model Hamiltonian at both maps; complete neutral ligands; fixed ML membership; neutral singlet capped components; ordinary protein C–C cuts.
- Caps remain derived sites; native OpenMM projects their raw forces exactly once. All real forces and full final-particle maps remain mandatory.
- Preserve S06 energy/force/FD tolerances and inherited locks. Chemical limits are separately predeclared and reviewed.
- No downloads/replacement weights, global unsafe loader, residual repulsion, force clipping, discarded failing samples or model branches in common ATM.
- Reviewer: actual gpt-6-astra/high, fresh context, exact frozen snapshot; no implementation or repairs by the reviewer. Missing quantum evidence means pending G05-T4/full physical acceptance.

## Review focus

- A valid checkpoint with an absent authorization/licence record must reject before deserialization (Task 1).
- Identical-element permutations can conceal wrong ordering; compare complete vectors under a nonidentity permutation and final-particle map (Task 2).
- A raw cap slot can conceal an omitted MM parent; independently project and check each real component, including mapped/perturbed inputs (Task 2).
- Two graphs mistakenly batched at contact can agree at separation; inspect cross-component edges and run a deliberate split-graph fault (Task 3).
- An offline XML callback can contain stale model settings; reload with network denied and empty caches, then compare exact raw/full results and identities (Task 3).

## Task 1: G00-T2 and G05-T1 trusted asset characterization

**Files:** create `src/atm_mlmm/models/mace.py`, `models/mace-off23-small/qualification-card.json`, `tests/integration/test_checkpoint_loading.py`; extend `tests/unit/test_environment.py`; reuse/refine `examples/mace_link_cpu.py` loading entry point.

**Interfaces:** `verify_asset(checkpoint, manifest_path=None) -> dict`, `load_model(checkpoint, manifest_path=None) -> torch.nn.Module`, `make_calculator(checkpoint, manifest_path=None) -> MACECalculator`, `model_spec() -> ModelSpec`. Heavy imports occur only inside loading functions. Verify retained bytes before explicitly trusted deserialization.

- [ ] Write and run the actual existing-loader missing-authorization regression; record its intended pre-deserialization failure. Wrong digest/absent file/missing licence/settings also reject.
- [ ] Implement verification of pinned checkpoint/licence/manifest authorization and metadata; preserve scoped e3nn `slice` allowance and clear MACE's global override after imports.
- [ ] Freeze measured ScaleShiftMACE architecture, supported elements, 4.5 angstrom edge cutoff, two interaction layers, 96 scalar features, dtype/output/units/domain. Record actual admitted ASE conversion, not a rounded assumption.
- [ ] Run G00 asset and fresh-process loading checks with DNS/connect denied, empty cache and no replacement asset; run affected/full suite and record exact outputs.
- [ ] Commit the independently testable asset deliverable on the child; G00-T2 acceptance remains an independent-review decision.

## Task 2: G05-T2 independent native/adapter and cap derivatives

**Files:** create `src/atm_mlmm/model_reference.py`, `tests/model_oracle.py`, `tests/integration/test_model_adapter.py`; extend `src/atm_mlmm/hybrid.py`/`capabilities.py` only for the admitted real provider. Preserve the analytic path.

**Interfaces:** `NativeMACE(checkpoint, manifest_path=None).evaluate(numbers, positions_nm) -> dict` returns total energy, raw forces/gradients, directed edges and native units. `build_physical(..., probe=None, cap_distance_nm=..., checkpoint=...)` adds one real-model dispatch while retaining the existing analytic call. The inherited sealer owns all links/maps/ledger.

- [ ] Write native/OpenMM, raw cap, both-parent/all-real and builder-admission assertions; run them before implementation, identifying structural missing-feature failures separately from numeric faults.
- [ ] Build an independent brute-force nonperiodic radius graph, a single graph's direct tensor inputs, and autograd of the declared total `energy`. Do not call the adapter, ASE calculator or shared graph helper for native expectations.
- [ ] Add the real checkpoint through the existing OpenMM-ML ASE route and inherited mechanical sealer. Reject incompatible asset/spec/chemistry/settings before construction.
- [ ] Check Reference and CPU, joint rigid transformations, atom permutations, a nonidentity final map, mapped coordinate inputs and full component FD sweeps at 1e-3/1e-4/1e-5 nm (additional smaller steps only for measured convergence).
- [ ] Run deliberate missing-cap-parent, factor-of-ten force conversion, wrong-order and stale-cap faults; preserve failing captures and prove the independent comparisons detect each.
- [ ] Run affected/full suite, capture numerical arrays, then commit. No chemical pass follows from these checks.

## Task 3: G05-T3 locality, domain and offline serialization

**Files:** create `tests/integration/test_locality.py`, `tests/integration/test_model_domain.py`; save exact scan coordinates/edges/energy/forces in `Worker_Log/Milestone_03/evidence/G05_v1/`; use shared `atm.save_bundle/load_bundle` unchanged.

**Interfaces:** Task 2's native evaluator and real physical bundle. Compatible component outputs include the same `energy` convention. Scan evidence distinguishes admitted samples from predeclared extreme diagnostic samples.

- [ ] Write/run contacting joint-graph and disconnected ML-only additivity checks; deliberately split the contact graph and verify failure.
- [ ] Run approach, compression, cap-adjacent rotation, 4.5 angstrom edge crossing and separated-state scans, including the alternate ATM geometry. Save every input/output/edge and exception/nonfinite sample.
- [ ] Diagnose numerical/mapping/graph issues independently of model-domain failures. Do not alter the Hamiltonian or thresholds to improve a score.
- [ ] Reload trusted hash-checked checkpoint and serialized physical/ATM bundles offline in a fresh process, with no original cache; check raw output convention, maps, cap geometry and all real forces.
- [ ] Run affected/full suite and commit the software qualification evidence. All G05-T1/T2/T3 claims stay scoped to actually tested chemistry/geometries.

## Task 4: M00 freeze and G05-T4 chemical comparisons

**Files:** exact full-precision fixtures and hash manifest under `fixtures/chemical_reference/`; separate generation scripts/environment/provenance; `tests/integration/test_chemical_reference.py`; unused M00 worker/audit attempt.

**Interfaces:** exact reviewed M00 inputs, method, metrics and numerical limits; Task 2 native evaluator; independently frozen energies/gradients. No quantum runtime dependency enters main.

- [ ] Agree the proposed molecules, settings, chemical limits and resource cap with the user; prepare exact G05/G07 conformer/contact/separated/uncut/alternative-region inputs, metadata and hashes without model scores.
- [ ] Confirm reference execution on a quantum-only feasibility molecule, freeze and commit the plan/input snapshot, and obtain the required independent Astra/high design audit.
- [ ] Only after acceptance, generate and freeze all applicable quantum energies/gradients. Preserve failed convergence/missing data and stop at the authorized compute cap.
- [ ] Implement/run both stable G05-T4 checks against the exact reviewed limits. Report by-family energies, raw and projected force errors, contact/monomer/separation conventions and every failure.
- [ ] Exceeded limits require a justified reviewed narrowing/physical change; missing data leave full acceptance pending. G07 comparisons remain future work.

## Task 5: exact-snapshot acceptance and publication

**Files:** unused G00/G05 worker/audit attempts, evidence/acceptance records, STATUS and fresh-agent handoff. Keep all inherited records unchanged.

- [ ] Run all applicable G00/G05 checks; G04, G02/G03/admission regressions; full/analytic suites; strict environment, upstream and documentation checks. Save commands, exits, identities and raw numerics.
- [ ] Freeze and commit the review-ready complete snapshot and source/input manifest; independently review using gpt-6-astra/high/fresh context. If blocking findings arise, repair with RED/GREEN and obtain a new exact-snapshot review as the user's instructions require.
- [ ] Record only the actual reviewed scope in STATUS/acceptance, verify protected tips and inherited hashes, commit report-only closure and push only the child.
- [ ] Deliver branch/commit, M00 choices/audit, actual G05 audit/test outcomes and fresh-agent G06/G07 handoff. Stop at G05 acceptance; M03 closes at G07.
