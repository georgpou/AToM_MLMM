# S03: The data that components pass to each other

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../../../README.md#roadmap) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

A shared contract is an agreement about names, units, ordering, and meaning. The records below make those agreements explicit, so two agents do not create incompatible versions of the same data.

**When to read it:** Read the relevant record rows and signatures for your task. Do not implement every possible future field at once.

## Shared units and array conventions

Common interfaces use nm for positions, kJ/mol for energy, kJ/mol/nm for forces, ps for time, and K for temperature. A user-facing field named `timestep_fs` can be accepted in a configuration schema, but conversion to the common `timestep_ps` happens once and is tested. Forces use the negative energy gradient convention. Box vectors are a 3-by-3 array of Cartesian row vectors in nm; nonperiodic input has an explicit `None`, not a zero box.

A `Snapshot` contains real-atom coordinates. A compiled OpenMM system additionally contains derived particles. The resolver constructs their coordinates in the specified order and returns forces projected onto the real atoms once. The common result contains every real atom in declared order. Adapter-level sparse force output must be scattered, validated, and completed before entering the common API; zero is correct only for a proven nondependent coordinate.

Do not treat a frozen dataclass containing mutable arrays as inherently immutable. Copy or protect arrays, prohibit mutation after sealing a bundle, and use separate mutable runtime contexts. A change to model parameters, embedding, partition, or constraint list creates a new physical identity, not an unrecorded edit to an accepted bundle.

## Records, required fields, and ownership

All names in the signatures below are defined here. Implement only fields required by an admitted capability. Unknown mandatory fields and unsupported schema versions cause explicit errors.

| Record | Minimum content |
|---|---|
| `AtomIdentity` | Stable unique ID, element, original chain/residue/insertion code/atom-name metadata; no reliance on PDB serial uniqueness |
| `TopologyView` | Real identities, bonds, molecule membership, required chemical metadata; dependency-light inspection view |
| `SystemInput` | Prepared MM system handle/artifact, TopologyView, real positions/box, masses, constraints, force-field provenance |
| `PartitionSpec` | Fixed real ML IDs, protein ML IDs, permitted cuts, chemically expected component states; no bound/bulk condition |
| `ResolvedPartition` | Sorted unique resolved sets, boundary edges, component identities, rejected conditions, source map |
| `ModelSpec` | Backend, approved asset digest, output-energy convention, elements, chemical-state support, locality/long-range declaration, dtype |
| `EmbeddingSpec` | Versioned kind and policy, periodic/boundary convention, documented additional parameters; initially mechanical only |
| `MobileGroup` | Group ID, tuple of real atom IDs, role labels, molecule identity; any number of groups supported by its protocol |
| `ProtocolSpec` | Protocol kind, tuple of MobileGroups, geometry requests, endpoint descriptions, desired observable; ABFE validates one group, dual-ligand RBFE validates two |
| `CapabilitySet` | Declared input/derivative/periodicity/serialization features of a component; not proof of qualified use |
| `CalculationRequest` | ModelSpec, EmbeddingSpec, PartitionSpec, ProtocolSpec, runtime/ensemble request, schema version |
| `LinkRecord` | Both real parent IDs, final particle index, model-input index, virtual-site type, actual cap distance in nm |
| `PhysicalBundle` | Opaque physical system handle, topology, real/final/model index maps, links, masses, constraints, ledger, physical manifest and content identity |
| `Snapshot` | Real atom IDs and positions, box, optional velocities; no embedded alchemical parameter or cached field |
| `RuntimeSpec` | Platform, precision, device allocation, integrator settings and explicitly declared supported ensemble |
| `EnergyForces` | Energy, forces for all real atoms, units/order, physical/snapshot identity, validation diagnostics; no hidden model mutation |
| `TransferDefinition` | Two full final-particle displacement maps, endpoint IDs/descriptions, mapping convention, contributing protocol identity |
| `ScheduleSpec` | Explicit ordered state IDs, complete expression parameters and units, temperature, direction and offset definitions |
| `RestraintSpec` | Reference IDs, expressions/parameters, domain/orientation convention, inside/outside ownership, correction obligations |
| `AlchemicalBundle` | Physical identity, transfer/schedule/restraint identities, ATM system, routing report, named raw-observable schema |
| `ThermodynamicSpec` | Endpoint free-energy weights, sign convention, state graph connection, standard state and explicit required correction records |
| `EvaluationRecords` | Raw data and metadata sufficient for reduced-potential reconstruction, state/replica histories and provenance |
| `BindingResult` | Restrained estimate, midpoint bridge, each correction and status, final value only when defined, covariance-aware uncertainty and limitations |
| `RawAtmEnergies` | Explicit u0/u1 raw child energies, raw/softened perturbation, ATM-expression energy, outside and total energy in the S07 units; no ambiguous tuple fields |
| `AtmEvaluation` | Total EnergyForces plus RawAtmEnergies, state ID and physical/transfer/schedule/restraint/snapshot identities |
| `ValidationReport` | Check ID, requirement IDs, evaluated profile/fixtures, measured values, thresholds, status, logs and reviewer references |

Optional electronic charge/spin and electrostatic-control information belongs in a reviewed model/embedding-specific subrecord, not a reinterpretation of classical partial charges. Omission means absent/unsupported, not an implicit default charge or spin. The shared physical evaluator remains unchanged as long as the compiled physical energy depends only on its declared state and real coordinates/box.

## Proposed signatures

These are contracts to implement in the assigned gates, not callable functions shipped here.

```text
validate_request(request: CalculationRequest,
                 capabilities: CapabilitySet) -> ValidationReport
resolve_partition(topology: TopologyView,
                  spec: PartitionSpec) -> ResolvedPartition
build_physical(mm: SystemInput, partition: ResolvedPartition,
               model: ModelSpec, embedding: EmbeddingSpec) -> PhysicalBundle
resolve_protocol(bundle: PhysicalBundle,
                 protocol: ProtocolSpec) -> TransferDefinition
build_atm(bundle: PhysicalBundle, transfer: TransferDefinition,
          schedule: ScheduleSpec, restraints: RestraintSpec) -> AlchemicalBundle
evaluate_physical(bundle: PhysicalBundle, snapshot: Snapshot,
                  runtime: RuntimeSpec) -> EnergyForces
evaluate_atm(bundle: AlchemicalBundle, snapshot: Snapshot,
             state_id: str, runtime: RuntimeSpec) -> AtmEvaluation
analyze(records: EvaluationRecords,
        thermodynamics: ThermodynamicSpec) -> BindingResult
```

`build_physical` is introduced in G04 for an analytic embedding substitute and refined for the real mechanical builder in G05-G06. G02 uses an analytic PhysicalBundle factory implementing the same documented output; it does not require the future neural model. `resolve_protocol`, `build_atm`, and analytic evaluators first appear in G02. G08 implements `analyze`. Earlier gates may serialize a subset record through a reviewed schema version, but must not invent conflicting field semantics.

## Identity and transformation rules

Real atom IDs are the source of truth. Resolve final OpenMM indices only after link construction. Maintain three separate maps: original real IDs to final particles, real/cap identities to model inputs, and final particles to transfer vectors. Explicitly consume `oldToNew` even when the current library appends sites and therefore preserves real-atom indices.

All current maps are fixed translations. For ABFE, one map is the identity and the other translates one complete ligand. For RBFE, two complete groups receive opposite vectors under the prescribed exchange. Real groups can have unequal atom counts and noncontiguous particle indices. In both cases the final maps have entries for every final particle, including zero explicit shifts on initial caps. Do not assume a one-to-one atom mapping between different ligands.

All masses and constraints remain identical between alchemical states within a calculation. A change in constraints creates a different ensemble and must be distinguished from an exact energy-equivalence control. Selected ML bond constraints are removed according to the reviewed builder policy; remaining boundary/MM/water constraints are recorded.

## Errors, capabilities, and schema evolution

Use explicit error categories: malformed input, unsupported capability combination, inconsistent identity/geometry, numerical domain failure, and qualification failure. Each names the relevant atom, force, field, or profile. Missing a required force derivative is not a zero-force result. A disabled capability is not `passed` or an automatically substituted model.

Validate known incompatibilities before expensive model deserialization or context construction where the required metadata is available. Runtime-dependent checks still execute at startup and during validation.

A saved schema carries `schema_version`. Reject unknown future versions. Additive optional fields need explicit semantics; changing units, force scope, identity meaning, or correction signs is a breaking change and requires migration or explicit rejection of the old format. G01 keeps small versioned JSON fixtures and round-trip tests. A model weight hash is not a substitute for a schema version, and a schema version is not a model identity.
