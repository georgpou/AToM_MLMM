# ADR-0001: independent physical, transfer and workflow components

**Status:** proposed for M00 review. **Source:** current user request plus the original energy/transfer separation. This is a design addition, not a discovered property of the live repository.

## Context

A first implementation may accidentally hard-code mechanical subtraction, ML-only force arrays or one-ligand inputs into common ATM logic. Extending it later would require changes across simulation, storage and analysis. Conversely, designing a universal backend framework before a correct small example would add unnecessary work.

## Proposed decision

Use the S02/S03 composition: embedding/model produces a complete PhysicalBundle; protocol produces mobile-group maps and thermodynamic meaning; common ATM consumes those records; an AToM adapter owns upstream details. Data contracts carry full real-coordinate derivatives, fixed identity and explicit versions. Scope admission is a capability/profile decision, not a collection of global mode flags.

## Alternatives

A document-only split without explicit contracts is easiest but leaves the refactoring risk unresolved. Separate full pipelines for every model/embedding/protocol combination are locally convenient but duplicate physics and corrections. A general plugin/engine framework is more ambitious than Project 0 needs. The proposed small composition retains only the extension boundaries tested by concrete examples.

## Consequences

Early structural and analytic tests cost some work before molecular examples, but expose incompatible assumptions cheaply. A future physical method may still need a reviewed contract extension; the project does not promise zero refactoring for arbitrary new physics. Existing admitted behavior must remain tested through any migration.

**Normative proposals:** [S02](../specs/S02-architecture-and-dependencies.md), [S03](../specs/S03-data-and-interface-contracts.md). **First owners:** G01-G03.
