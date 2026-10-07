# User guidance for C3 and production sampling

Recorded 2026-10-07 after the Batch C checkpoint. This is user steering for subsequent approved work; it does not authorize worker D/E, an independent audit, cluster submission, or additional sampling.

Alchemical closure/reversal checks are scientific consistency diagnostics. A failure can indicate sampling problems, but passing closure alone does not establish convergence. Physical-state compatibility must be established before interpreting a closure comparison. C3's missing general metadata/refusal contract remains an implementation requirement; this guidance does not close that gap.

Use analytic and small molecular systems, extending through the host–guest controls, to establish that the implementation and physical accounting behave properly under controlled conditions. Preserve the already frozen synthetic criteria and results. Any further qualification design and numerical criteria must be declared before its calculations.

For larger molecular systems, recognize that available compute may impose a sampling ceiling. Useful Pearson correlation and Kendall rank correlation can be obtained before individual free-energy calculations are fully converged. Report such predictive performance with its dataset, reference values, uncertainty and sampling limitations. Good correlation or ranking does not establish absolute energetic accuracy or convergence; common biases and unresolved slow modes can coexist with useful predictions.

For later production tests, assess predictive performance and sampling adequacy separately. Retain closure/reversal, independent-repeat and time-window diagnostics where meaningful, and report unresolved disagreements. Set the sampling budget and stopping criteria before running. If the ceiling is reached, preserve and report the bounded result and its limitations rather than extend sampling indefinitely to force consistent energetics or tune acceptance limits after seeing the results. Do not impose universal full-convergence/closure acceptance on every large-system ranking result without a separately agreed production criterion.

This guidance leaves thermodynamic accounting intact: unresolved physical corrections or required joint covariance still prevent a complete final binding result under the existing admission contract. Hardware/software correctness, known-answer controls, predictive utility, sampling adequacy and physical-result completeness are separate claims supported by their respective evidence.

Future D/E workers and the later cluster handoff should read this guidance together with the supplied task packets and the actual Batch C limitations. Cluster budgets, production acceptance criteria and any additional authorization remain to be established before those runs.
