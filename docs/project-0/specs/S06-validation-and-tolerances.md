# S06: How we check correctness, and how close is close enough

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../README.md) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

Small tests with known answers come before long simulations. Numerical limits help reveal errors, but they must be checked for the actual precision and system size rather than relaxed to hide a failure.

**When to read it:** Use the relevant test layer and numerical limits. A documentation check is not a molecular test.

The detailed names and equations below are kept precise because they define the behavior the tests must check. Unfamiliar terms are explained in [the glossary](../reference/glossary.md).

## Specification-driven and test-driven are complementary

A specification states which behavior is scientifically intended and which combinations are supported. A test supplies evidence that a particular implementation satisfies that behavior on an admitted input. Neither can substitute for the other: tests can faithfully implement a wrong Hamiltonian, while prose can describe a correct Hamiltonian that code does not evaluate.

Each task links requirement IDs, an input example, an expected independent result, its tolerance or statistical decision, a test identifier, and evidence. Run the test before implementation to establish a meaningful failure. Import failures can establish an absent API but do not replace numerical failure injection after the feature exists. Refactor only with the same contract tests in place. A new scientific behavior requires a specification amendment, not an arbitrary change to an expected value.

## Four test layers

**Structural tests** cover identities, schemas, capability rejection, imports, ownership, and dependency rules without GPU or model weights. **Analytic contract tests** cover one-/two-ligand maps, full derivatives, environment dependence, units, and state ordering with known formulas. **Backend integration tests** qualify OpenMM-ML, MACE, virtual sites, PME, AToM routing, and serialization. **Sampling/workflow tests** cover known-answer estimators, restraints, restart/exchange, and molecular pilots.

Planned test roots are `tests/unit`, `tests/contracts`, `tests/integration`, `tests/workflow`, and `tests/sampling`. Assign explicit markers for model assets, GPU, and extended sampling. No marker skip counts as a pass. On a machine without CUDA, run the meaningful CPU suite and leave the GPU profile unqualified.

The same contract suite is parameterized over admitted providers and protocols. Initially use analytic-local and analytic-environment providers with ABFE and dual-ligand RBFE definitions. Add the real mechanical model provider later. Do not add a row labeled 'electrostatic supported' merely because the analytic-environment provider passes.

## Independent oracles and fault injection

Hand-write tiny coordinate expectations independently from the map helper under test. Compare the native model with the OpenMM adapter using the same approved checkpoint through a genuinely independent path. Test link-parent Jacobians analytically and by finite differences. Check formula-level thermodynamics by quadrature and independent samples before testing MD sampling.

Deliberately omit the ML child force, translate the wrong atom, reverse endpoint order, omit an environment derivative, reuse a stale field, double-count a physical force, remove cap redistribution, and inject a factor-of-ten force conversion error. Each corresponding test must fail with a diagnostic that locates the discrepancy. Keep these fault-injection tests lightweight and deterministic.

## Starting numerical thresholds

These are inherited proposed tolerances, not empirical results. Characterize the admitted reference precision and freeze the final profile before acceptance. A reviewed change must explain measured numerical noise; passing by arbitrary tolerance relaxation is prohibited.

| Check | Starting acceptance value |
|---|---|
| Identity, ownership, constraints, map number of groups | Exact equality |
| Small analytic Reference energy | Absolute error <= 1e-8 kJ/mol |
| Small analytic Reference force component | Absolute error <= 1e-7 kJ/mol/nm |
| Small double-precision direct/ATM energy | Absolute error <= 1e-4 kJ/mol |
| Small double-precision direct/ATM force component | Absolute error <= 5e-3 kJ/mol/nm |
| ML finite differences | Step-size convergence; RMS error <= 1e-3 kJ/mol/nm + 1e-4 times RMS reference force |
| Analytic sampled free energy | Within 3 reported standard errors AND within 0.1 kJ/mol of the known value after adequate sampling |
| Same mathematical estimator inputs | Agreement within the stated solver tolerances |
| Admitted model-domain values | No unexplained nonfinite energy or force |

For finite differences use $F_i(h)=-[U(x_i+h)-U(x_i-h)]/(2h)$ and initially sweep 1e-3, 1e-4, and 1e-5 nm. Recompute virtual sites after every perturbation. Include ligand, cavity, both boundary parents, nearby MM atoms, and solvent. Examine components, not only an RMS that might hide one bad boundary.

Large-solvent and GPU settings need their own precision characterization. Do not divide errors by the enormous total energy of a protein to make binding-scale discrepancies look small. Inspect perturbation energies and local forces. OpenMM precision and model dtype are separate controls.

## Model admissibility before long trajectories

Scan approach, modest compression, severe overlap for diagnosis, rotations near caps, cutoff crossing, and both mapped geometries from ATM pilots. Save graph edges, model/total energy, maximum forces, and exact coordinates. Soft-core mixing requires finite endpoint evaluations and cannot repair an unphysical attractive collapse in the learned potential. Do not discard such frames from a final estimator to hide a failure.

Separate causes: units/indices, graph construction, cap coordinates, precision, model training domain, and sampling. Fine-tuning is justified only after identifying an actual model limitation. A new residual repulsion would define a new Hamiltonian and needs new validation.

## Sampling, covariance, and reproducibility

Evaluate overlap, effective contribution counts, correlation, state visits, independent seeds, and estimate stability versus retained time. A connected overlap graph is necessary in the chosen analysis but not sufficient evidence of all relevant conformations. A practical initial flag is fewer than 100 effectively contributing samples or incompatible full/last-half estimates; these are investigation triggers, not universal convergence laws.

For a Project-1 readiness pilot, the inherited planning targets are <=0.5 kcal/mol statistical uncertainty and a separately considered 0.2 kcal/mol sensitivity budget. These do not replace deterministic tolerances or justify a known missing interaction.

For $X-Y$, include covariance: $\mathrm{Var}(X-Y)=\mathrm{Var}(X)+\mathrm{Var}(Y)-2\mathrm{Cov}(X,Y)$. Use block or independent-run resampling appropriate to replica/state histories. Report uncertainty of a mean separately from spread across replicates. A thermostat holding temperature does not prove force correctness; use conservative integration and suitable timestep/energy-drift diagnostics after derivative checks.

## Planned commands and what they mean

Gate files list future `pytest` commands and test paths. These commands are not executable against this documentation-only package because simulation/test code has not yet been implemented. During implementation, capture command, environment/profile, exit code, and test outcome. A documentation link checker is not an OpenMM qualification test. The [evidence contract](S07-artifacts-and-qualification.md) defines acceptance records.
