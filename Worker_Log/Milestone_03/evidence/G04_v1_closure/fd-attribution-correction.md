# G04 v1 finite-difference attribution correction

The frozen test-helper comment at `tests/integration/test_link_geometry.py:61` attributes the additional 1e-6 nm step to the retained GAFF Lennard-Jones term. Independent reviewer measurements identify retained **bonded** terms as the dominant truncation error. The worker log describes the retained-GAFF result without making that term-specific attribution.

The Astra-authored [independent cap probe](../G04_v1_independent_r2/probe_cap_independent.py) evaluates the retained force classes separately. Its [saved decomposition](../G04_v1_independent_r2/cap-independent-results.json) gives maximum Cartesian component errors in kJ/mol/nm:

| Retained force class | 1e-3 nm | 1e-4 nm | 1e-5 nm | 1e-6 nm |
|---|---:|---:|---:|---:|
| HarmonicBondForce | 1.2483743 | 0.01248423 | 0.0001248417 | 0.00000125394 |
| HarmonicAngleForce | 0.1292026 | 0.001292128 | 0.00001292130 | 0.000000127699 |
| PeriodicTorsionForce | 0.02375830 | 0.0002376659 | 0.000002376704 | 0.0000000238747 |
| NonbondedForce | 0.01751715 | 0.0001751343 | 0.000001751294 | 0.0000000169520 |

The required 1e-3/1e-4/1e-5 nm sweeps show second-order convergence, and the full-fixture RMS at 1e-5 nm meets the unchanged S06 limit. The extra 1e-6 nm step additionally meets the test helper's stricter 1e-5 component target. It does not relax S06 or change the Hamiltonian, cap rule or fixture. The analytic cap-only errors are independently small at the required steps.

This report corrects the explanatory attribution while preserving the exact reviewed source, all submitted worker evidence and the original failing samples. Independent gate acceptance is determined by the matching Astra audit, rather than by this worker-authored clarification.
