# G08 thermodynamics implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` for inline implementation. The user supplied the engine-readiness design and explicitly requested autonomous continuation; GPT-6.1-sol/MAX is the independent auditor.

**Goal:** Implement the six G08 assertions without changing the physical Hamiltonian or promoting G07 physical qualification.

**Architecture:** Extend dependency-light schema records with explicit thermodynamic definitions and correction status. Reconstruct reduced potentials in `schedule.py`; put separable finite-wall volume in `restraints.py`, statistical analysis in `analysis.py`, and upstream UWHAM translation only in `adapters/atom.py`.

**Tech stack:** Locked Python 3.11 CPU profile, NumPy/SciPy, OpenMM Reference, PyMBAR 4.0.3, pinned AToM Python UWHAM.

**Spec:** [User handoff](../../docs/project-0/handoffs/ENGINE-READINESS-fresh-agent-v1.md), [G08](../../docs/project-0/gates/G08-thermodynamics-and-estimators.md), [S03](../../docs/project-0/specs/S03-data-and-interface-contracts.md), [S05](../../docs/project-0/specs/S05-protocol-and-thermodynamic-contracts.md), [S06](../../docs/project-0/specs/S06-validation-and-tolerances.md).

## Global constraints

- Continue `m04-engine-readiness` from `e24e880abcb0353b8f9c2f2e509d6cbb46174f3b`; preserve predecessor/main and all scientific evidence.
- Harmonic k=100, kr=50 kJ/mol/nm^2 and d=0.3 nm: F1-F0=+1.5 kJ/mol, reverse=-1.5, kr=0 gives zero.
- Known-answer sampling must satisfy both three standard errors and absolute error <=0.1 kJ/mol.
- Outside energy is included exactly once; execute the admitted nonlinear expression with explicit units, directions and offsets.
- Bound-minus-bulk correction is -RT ln(Veff/Vstandard); midpoint combination is D1-D0-deltaFm.
- Missing corrections, unsupported domains, nonfinite records and disconnected support cannot produce final standard binding results.
- Two CPU threads, 8 GiB cgroup RAM; serialize scientific workers. No QM or long production runs.

## Review focus

- Partial correction records or unsupported coupled/periodic restraints must withhold standard binding output (Task 1).
- Unknown/reordered states, duplicate samples and lost raw energy provenance must reject (Task 2).
- Reverse Direction with UOffset/W0 and active soft-core must agree with actual contexts (Task 2).
- Gauge shifts, covariance and unsupported state bridges must not silently change an observable (Tasks 2/3).
- Correlated histories must not be treated as independent; report contribution/overlap diagnostics and repeated-seed stability (Task 3).

## Task 1: G08-T1 deterministic answer and correction definitions

**Files:** Extend `src/atm_mlmm/schema.py`; create `src/atm_mlmm/restraints.py`, `src/atm_mlmm/analysis.py`, `tests/unit/test_restraint_volume.py`, `tests/sampling/test_analytic_free_energy.py`.

**Interfaces:** `CorrectionRecord`, `ThermodynamicSpec`, `BindingResult`; `finite_wall_volume_nm3(radius_nm, spring_kj_mol_nm2, temperature_K, *, domain) -> float`; `translational_standard_state_correction(volume_nm3, temperature_K, standard_volume_nm3) -> float`; `combine_free_energies(state_ids, free_energies_kj_mol, covariance_kj2_mol2, thermodynamics) -> BindingResult`.

- [ ] Write/run failing known-answer quadrature and finite-wall/correction tests. Sample independent Gaussians at all linear lambda states and compare a statistical estimate to the exact curve before MD.
- [ ] Implement finite-wall infinite-space integral, explicit supported domain and positive/finite parameter admission; test harmonic r0=0 and hard-wall limits against independent quadrature.
- [ ] Add explicit immutable endpoint weights, graph, domains, conventions, standard state and evidence-backed correction records. Missing required entries leave final value undefined; compute w.T covariance w for the restrained observable.
- [ ] Run focused tests and available full CPU suite; preserve RED/GREEN output and commit the task.

## Task 2: G08-T2 exact schedule and directional bridge

**Files:** Extend `src/atm_mlmm/schedule.py`, `src/atm_mlmm/schema.py`, `src/atm_mlmm/analysis.py`; create `tests/unit/test_schedule.py`.

**Interfaces:** `reduced_potentials(records: EvaluationRecords) -> ndarray[K,N]`; raw records carry complete schedule, ordered sample/state IDs, u0/u1/outside terms and declared identities. `directional_difference(leg0, leg1, bridge, covariance) -> (value, standard_error)` uses weights (-1,+1,-1).

- [ ] Write/run failing reconstruction tests for each declared state against actual native contexts, including Direction +/-1, UOffset, W0, nonlinear transition and outside terms.
- [ ] Implement stable exact expression reconstruction. Reject state/record mismatch, nonfinite values, duplicate sample identities and unsupported schedules.
- [ ] Deliberately use active, nonidentical directional midpoints. Independently integrate both ensembles; show omission and wrong bridge sign fail and the S05 combination restores -1.5 kJ/mol.
- [ ] Run focused checks and full CPU suite; commit.

## Task 3: G08-T3 independent estimators and bounded MD

**Files:** Extend `src/atm_mlmm/analysis.py`, `src/atm_mlmm/adapters/atom.py`, `tests/sampling/test_analytic_free_energy.py`; add reproducible example/evidence.

**Interfaces:** `analyze(records: EvaluationRecords, thermodynamics: ThermodynamicSpec) -> BindingResult`. Estimator operates on reconstructed dimensionless potentials with counts in declared state order. AToM adapter consumes identical potentials/counts and returns comparable free energies and covariance.

- [ ] Inspect the complete pinned Python UWHAM implementation/API and write/run failed tests on identical states/data, covariance and gauge/state offsets.
- [ ] Implement estimator adapter, correlation handling and overlap/effective-contribution checks with explicit diagnostics. Verify independent PyMBAR/UWHAM agreement before MD.
- [ ] Run short repeated-seed harmonic OpenMM Reference MD; report correlation, support, last-half stability, uncertainty of means separately from replicate spread, and both known-answer criteria.
- [ ] Run all six stable G08 nodes, full CPU suite and docs checker; record exact counts, resources and environment limitations.
- [ ] Commit the exact submission, request GPT-6.1-sol/MAX audit, preserve findings and perform focused repairs where required. Gate/M04 acceptance only follows the independent decision.

## Continuation

Execution ruling: Tasks 1/2/3 are being verified together on the final G08
submission. Their focused RED/GREEN runs remain separate, and the complete
available suite runs after the combined meaningful implementation. This avoids
repeating the unchanged expensive numerical audit; no task/gate is promoted
before combined evidence and independent review. Persistent evidence/worker logs
serve as this plan's ledger and are retained under the user's preservation policy.

Proceed to scoped G09/G10 only after relevant G08 acceptance/runtime prerequisites. Read their contracts when starting; do not infer molecular physical qualification. Ask for cluster configuration only when cluster work actually requires it.
