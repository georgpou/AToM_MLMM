# Adding a model, embedding or protocol without duplicating the engine

## A second local model

Add one model adapter with explicit asset, units, chemical domain and locality metadata. Reuse the native-reference, cap, full-force, endpoint, serialization and model-domain contract suite. Do not require the transfer engine to import the new model. A supported-model name in an upstream library is not a qualified project profile.

Start on capped fragments and the solvated toy before repeating protein benchmarks. The new model is a new physical identity and needs new profile evidence. Check model licensing and checkpoint compatibility independently from the package code license.

## Actual electrostatic embedding

First write the electrostatic scientific specification: which field/potential the model sees; how it is computed under PBC; boundary charge treatment; long-range/self/background conventions; charge/spin inputs; additional coupling and double-counting rules; all real-coordinate derivatives; and, if needed, self-consistent convergence and state history. Do not equate a model having internal long-range interactions with electronic embedding by external MM charges.

Implement those details in the embedding/model components. Reuse the physical evaluator, protocol maps, ATM assembler, raw record schema, restraint/correction machinery and runner. The G02/G04/G07 environment probes make missing MM derivatives and stale mapped fields visible before this extension. Real field, periodic, response and model tests remain additional requirements; the probes do not settle them.

A local model's disconnected-additivity test becomes inapplicable for a justified nonlocal provider. Record that capability-specific applicability, while retaining universal energy/force/state/restart tests. Do not turn every failing old test into a skip without explaining whether its premise still applies.

## A new protocol or map

An ABFE/RBFE preset supplies MobileGroups, maps, endpoint meanings, restraints and observable/correction obligations. It should not change the physical builder. Whole-molecule RBFE is already represented in the initial records and analytic tests, so G12 is molecular qualification rather than a data-model rewrite.

A coordinate-dependent map, common-region swap or restrained rotation needs new derivatives and measure/constraint analysis. It may require a versioned transform contract extension. Such a change is different from adding another set of fixed translation vectors.

## The architecture review test

Before merging any extension, identify which files changed. Changes concentrated in a new backend, its declared capabilities and tests are expected. A need to add `if embedding == ...` inside ATM or raw-analysis code, drop environment forces from a shared result, or introduce another per-protocol physical pipeline indicates a boundary problem.

Do not promise literally zero future refactoring. Promise small reviewed extensions, stable contracts where justified, explicit migrations where necessary, and permanent evidence that earlier admitted mechanical ABFE/RBFE behavior still works.
