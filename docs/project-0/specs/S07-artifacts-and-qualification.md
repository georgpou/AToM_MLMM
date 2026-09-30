# S07: What must be saved before we claim something works

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../../../README.md#roadmap) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

A result applies to the exact code, model, inputs, hardware, and settings that were checked. A profile is the short name for that complete setup. A log must make the tested setup recoverable.

**When to read it:** Use it when writing results, loading saved work, reviewing status, or accepting a gate.

## Evidence must identify what was tested

A qualification profile includes physical/thermodynamic contract versions, component source commits, full environment lock, model digest and permitted use, embedding parameters, protocol/map kind, fixture identity, box/constraint/mass convention, platform and device, model/OpenMM precision, integrator/timestep, and ensemble. A shorthand such as 'MACE + ATM supported' is insufficient.

A component may declare a capability, an analytic substitute may demonstrate an interface, and a complete molecular combination may be qualified. These are different evidence levels. Qualification of mechanical ABFE on CPU does not qualify mechanical RBFE on GPU, actual electrostatic embedding, or all available checkpoints.

## Capability-specific applicability

Start with the `core-analytic-cpu` profile. It requires no licensed neural weights or GPU. Real-model loader checks are mandatory for a `mechanical-mace-cpu` or corresponding GPU candidate, not the analytic-only profile. G01-G04 can proceed on core evidence; G05 additionally requires approved model-asset/loading prerequisites. A dependency is satisfied only by evidence covering the features the consuming gate actually needs, not by an unrelated accepted profile with the same gate ID.

Record test applicability as a separate decision from test outcome. A documented nonapplicable model/GPU test does not block a narrower analytic claim, but cannot contribute to a model/GPU claim. Mandatory applicable tests cannot be skipped into acceptance. Keep the capability matrix and evidence record explicit about that scope.

## Gate and milestone state

Use `not_started`, `in_progress`, `blocked`, `ready_for_review`, `changes_requested`, `accepted`, and `invalidated` for gate or milestone status. Worker attempts separately use `ready_for_audit`, `partial`, or `blocked`; an audit separately records `accepted_for_scope`, `changes_required`, or `blocked`. A small accepted task is not automatic whole-gate acceptance. Tests separately record `not_run`, `failed`, `passed`, or `skipped`. Specifications separately record proposed/reviewed/superseded. M00 is a design-review milestone; all numerical gates still require their own evidence afterward.

An accepted gate has requirement coverage, required tests run on its declared profile, raw results/logs, a reviewer identity, and a documented acceptance decision. A milestone requires all of its gate profiles and dependencies accepted for the claimed capability, plus its own combined review. An accepted CPU profile may coexist with a blocked GPU profile; use separate records rather than overwriting one status.

A relevant change to contracts, model, force-field/constraints, platform, precision, or versions invalidates affected evidence until rerun. State the dependency impact rather than rerunning everything blindly or pretending nothing changed.

## Planned artifact bundle

```text
run-or-qualification-bundle/
  manifest.json
  environment.lock
  model-manifest.json
  atoms.tsv
  links.json
  force-ledger.json
  constraints.json
  physical-system.xml
  atm-system.xml
  topology.pdb
  initial-state.xml
  checkpoint.chk
  protocol.json
  schedule.json
  restraints.json
  raw-observables.*
  coordinates.*
  analysis.json
  evidence/
    test-results.json
    commands.log
    reviewer-decision.md
```

The exported `reviewer-decision.md` should identify the canonical audit log and its snapshot, not introduce a second independent acceptance record.

This list states required content, not a requirement to create empty files before they have meaning. Choose actual data formats during their owning gate and record units and schema. Do not treat PDB coordinates as the only high-precision state archive. Record hashes for external large artifacts and their retrieval location. Model weights, licenses, large trajectories, secrets, and personal data are not automatically suitable for Git.

## Required observable names

Save sample/step/time, replica ID, thermodynamic state ID, direction, temperature, box, complete schedule parameters, and separately named `u0_raw_kJ_mol`, `u1_raw_kJ_mol`, `delta_u_raw_kJ_mol`, `delta_u_softcore_kJ_mol`, `atm_expression_energy_kJ_mol`, `outside_energy_kJ_mol`, and `system_total_energy_kJ_mol`.

Preserve enough high-precision snapshots for independent cross-state reevaluation and failure reproduction. The reporting interval is a run parameter. Translate upstream ambiguous field names at the adapter boundary rather than importing their ambiguity into this schema. Stale sample/state records invalidate an exchange or estimator check.

## Loading, restart, and workers

Only load approved trusted model/System artifacts. Pickle-based model or PythonForce XML deserialization can execute code. Record checkpoint hashes and loading policy. Test with networking disabled and the original cache unavailable so a hidden download cannot rescue an incomplete bundle.

Save both a checkpoint and a portable State when useful. A binary checkpoint can preserve internal continuation state but is platform/system/version/hardware-specific. A State provides portable observables but does not establish identical random-number continuation. Compare fixed-coordinate energies, forces, parameters, constraints, and box before claiming a successful restart; do not require bitwise-identical trajectories on unqualified hardware.

For CUDA workers, preserve the admitted process-start method and verify both OpenMM device assignment and the model tensors' actual device after reload. OpenMM `DeviceIndex` does not itself prove the PyTorch model moved. A physical GPU may appear as local index zero under a restricted visible-device list. Single-GPU scheduling is the first qualification; multigpu use is a separate profile.

## Review and reporting

Use the [worker](../templates/worker-log.md) and [audit](../templates/audit-log.md) templates under the task's milestone folder. [AGENTS.md](../../../AGENTS.md#logs-and-handoff) owns attempt naming, role boundaries, required metadata and immutable submitted logs. No separate gate, milestone or PR report is required for a routine assignment; a combined review records its explicitly broader scope in the same handoff format.

[STATUS.md](../STATUS.md) is the only live progress summary, linked to actual logs and profile evidence. Gates own planned assertions; [REQUIREMENTS.md](../REQUIREMENTS.md) locates stable IDs. A status edit cannot create an accepted result. Runtime manifests, schema versions, raw records and evidence validation defined above remain required even though the redundant documentation planning index has been retired.

Scientific raw data may be stored externally, with inspectable checksums and access requirements. Empty evidence means unexecuted, not failed or passed. A future CI job may separate structural/analytic CPU checks from model/GPU/sampling profiles; no always-green placeholder is provided. Documentation checks are not molecular qualification.

Whole-gate acceptance must cover every applicable task and unresolved finding on the combined snapshot. A milestone adds the closing gate's combined review and its earlier milestone dependencies. A partial accepted task does not erase earlier open findings or qualify a different profile.
