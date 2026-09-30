# S02: Which part of the code owns each job

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../../../README.md#roadmap) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

The energy builder should not need to know whether the calculation is ABFE or RBFE. The transfer code should not need to know how the embedding computes energy. This separation is what makes later additions manageable.

**When to read it:** Use the ownership table before adding a module or moving responsibility between components.

## Decision: compose independent parts, do not multiply complete pipelines

Three approaches were considered. Splitting the big document without changing its implicit interfaces is easy but leaves one-ligand and ML-only-force assumptions untested. Building a universal simulation-plugin framework would add considerable complexity before any physics works. The chosen middle path specifies a few concrete boundaries and uses analytic substitute implementations to test them early.

One physical-system builder owns the hybrid Hamiltonian. One protocol resolver defines a transfer problem. One ATM assembler combines their outputs. One workflow adapter translates into AToM's version-specific execution API. Model and embedding choices remain independent from ABFE/RBFE choices wherever the physics permits; a capability check rejects combinations that do not meet the required contracts.

```text
Prepared MM system + fixed partition + model + embedding
                           |
                           v
                    PhysicalBundle
                           |
Protocol request ----------+----> TransferDefinition
                           |
Schedule + restraints -----+----> shared ATM assembler
                                      |
                                      v
                              AlchemicalBundle
                                      |
                              AToM workflow adapter
                                      |
                           preparation / run / restart
                                      |
                         records + ThermodynamicSpec
                                      |
                               shared analysis
```

An embedding owns model-specific evaluation details. The ATM assembler is allowed to depend on OpenMM, since this project is OpenMM-based; it is not allowed to depend on a particular ML model, mechanical-embedding term selection, or the number of mobile ligands. The protocol resolver specifies geometry and thermodynamic meaning; it does not construct MACE graphs or remove classical interactions.

## Proposed implementation ownership

These are future source paths, not implemented files in this documentation package.

| Module | Responsibility | Must not own |
|---|---|---|
| `schema.py` | Versioned records, units, validation errors | Model imports, GPU initialization |
| `capabilities.py` | Declared capabilities and qualification-profile validation | Silent feature fallback |
| `identity.py`, `partition.py` | Stable identities, fixed selection, boundary graph | Alchemical schedules |
| `hybrid.py` | Shared physical-builder entry point and dispatch | Per-protocol or bound/bulk branches |
| `embeddings/mechanical.py` | Current retained-MM construction and boundary policy | ATM mixing or binding corrections |
| `models/mace.py` | Approved checkpoint, native adapter, units, model metadata | ABFE/RBFE logic |
| `protocols/abfe.py`, `protocols/rbfe.py` | Protocol-specific number of groups, maps, endpoint descriptions | Physical force construction |
| `geometry.py`, `routing.py`, `atm.py` | Map application, explicit force ownership, common ATM assembly | Model names, electrostatic approximations |
| `restraints.py`, `schedule.py` | Explicit bias terms and exact state expressions | Hidden corrections |
| `prepare.py` | Shared staged preparation on admitted bundles | Independent versions of the physical Hamiltonian |
| `adapters/atom.py` | Upstream AToM classes, keys, units, state handover | New scientific definitions |
| `endpoints.py`, `derivatives.py`, `model_reference.py`, `ledger.py` | Independent numerical and bookkeeping checks | Reusing the same implementation as its only reference check |
| `observables.py`, `analysis.py` | Raw records, reconstruction, estimation, corrections | Inference of endpoint meaning from a filename |
| `persistence.py`, `report.py`, `cli.py` | Reproducible artifacts and a thin user interface | Unrecorded model downloads |

One package namespace, `atm_mlmm`, is proposed. Keep simple functions and records rather than inheritance-heavy base classes. A small explicit registry of admitted embeddings/protocols is sufficient. Do not create independent runners for every combination.

## Dependency rules and ownership tests

`schema.py`, `identity.py`, and protocol records must import without OpenMM, MACE, PyTorch, a checkpoint, or CUDA. The implementation can use lightweight utilities where actually needed, but model imports stay lazy at adapter boundaries.

`protocols/*` must not import `models/*` or `embeddings/*`. `atm.py` must not import MACE or contain an embedding-name dispatch. `embeddings/*` must not import `protocols/*`. No general-purpose function accepts `is_rbfe` to choose its physics. Upstream class selection in `adapters/atom.py` is an allowed version-specific implementation detail, tested for equivalent observable behavior.

G01 owns `tests/contracts/test_architecture_boundaries.py`. The test checks disallowed imports and representative dependency-light imports. G02 owns the more important behavior tests: the same assembler accepts one-/two-group transfers and both local and environment-dependent analytic energies. Static import checks alone are not proof of extensibility.

## Force ownership and execution

Start with all physical potential-energy forces inside ATM; keep explicitly defined restraint/bias terms outside as specified by the thermodynamic design. A thermostat/integrator, disabled production barostat, and center-of-mass remover are not treated as ordinary translated physical child forces. Each term has an explicit identifier and disposition.

The physical preparation context uses a separate all-active copy, initially group 0. The production handover copy places admitted physical terms in a reserved group for AToM's explicit `VARIABLE_FORCE_GROUP` selection. The candidate reserved group is 1, but check that it is free before assigning it. Test recursive ownership, removal of originals, and the active integration mask after upstream construction. Do not rename a Python force to fool name-based routing.

Moving an invariant term outside ATM is a later optimization. It requires both coordinate invariance and the algebraic shift identity for the selected mixing expression. A term constant on one frame is not necessarily invariant.

## Extension promises and limits

Adding a second local model should require a model adapter plus the existing contract suite. Adding electrostatic embedding should require an embedding/model implementation, new coupling and convergence evidence, and a capability declaration; it should not require rewriting transfer, scheduling, raw-record storage, or binding-result assembly. Adding an ABFE or RBFE preset should require protocol/adapter changes, not another physical builder.

This is a design target, not a guarantee that every future method will fit without change. If a future method needs new physics inputs, extend the versioned contract deliberately. Do not conceal an incompatible requirement in a generic dictionary or misrepresent a fake implementation as supported physics.

## Proposed decision rationale

The following inherited decisions remain **proposed for M00 review**; this consolidation does not approve them.

### ADR-0001

**Context:** A first implementation may accidentally hard-code mechanical subtraction, ML-only force arrays or one-ligand inputs into common ATM logic. Extending it later would require changes across simulation, storage and analysis. Conversely, designing a universal backend framework before a correct small example would add unnecessary work.

**Alternatives:** A document-only split without explicit contracts is easiest but leaves the refactoring risk unresolved. Separate full pipelines for every model/embedding/protocol combination are locally convenient but duplicate physics and corrections. A general plugin/engine framework is more ambitious than Project 0 needs. The proposed small composition retains only the extension boundaries tested by concrete examples.

**Consequences:** Early structural and analytic tests cost some work before molecular examples, but expose incompatible assumptions cheaply. A future physical method may still need a reviewed contract extension; the project does not promise zero refactoring for arbitrary new physics. Existing admitted behavior must remain tested through any migration.


### ADR-0002

**Context:** Waiting until G12 to introduce the idea of two ligand groups can expose a one-ligand core too late. Waiting for a real electrostatic model before testing environment derivatives can similarly leave ML-only force outputs and stale field caching hidden inside the transfer engine.

**Proposed decision:** G01 admits tuple-based mobile groups and full-real-force result semantics. G02 tests one and two unequal groups through the same assembler, and an analytic energy depending on an MM coordinate. G04/G07 extend the latter to cap parents and the integrated pipeline. Actual molecular RBFE remains G12; actual electrostatic physics remains outside Project 0.

**Acceptance and boundaries:** The environment probe must change energy/forces when only MM coordinates change, rebuild its dependencies under both maps, and be independent of evaluation order. It must produce all influencing real-coordinate derivatives. The two-group probe must preserve unequal/noncontiguous identities without atom-pair mapping assumptions.

Passing these probes admits architectural behavior only. It does not establish external-field physics, charge response, self-consistent convergence, periodic electrostatics, model accuracy, or a production electrostatic backend. Those require a future scientific specification and profile evidence.


## The architecture review test

Before merging any extension, identify which files changed. Changes concentrated in a new backend, its declared capabilities and tests are expected. A need to add `if embedding == ...` inside ATM or raw-analysis code, drop environment forces from a shared result, or introduce another per-protocol physical pipeline indicates a boundary problem.

Do not promise literally zero future refactoring. Promise small reviewed extensions, stable contracts where justified, explicit migrations where necessary, and permanent evidence that earlier admitted mechanical ABFE/RBFE behavior still works.
