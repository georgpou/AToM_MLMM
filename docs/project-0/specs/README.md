# Shared specifications: the rules used by more than one task

A specification fixes expected behavior, units, and shared inputs/outputs. Read only the sections linked by your task unless you are reviewing the architecture as a whole. Each page begins with a plain-language explanation before its precise definitions.

| Specification | Question it answers |
|---|---|
| [S01](S01-scope-and-invariants.md) | What belongs in Project 0, and what does not |
| [S02](S02-architecture-and-dependencies.md) | Which part of the code owns each job |
| [S03](S03-data-and-interface-contracts.md) | The data that components pass to each other |
| [S04](S04-embedding-and-model-contracts.md) | How ML, MM, and link atoms form one energy model |
| [S05](S05-protocol-and-thermodynamic-contracts.md) | What the free-energy result means |
| [S06](S06-validation-and-tolerances.md) | How we check correctness, and how close is close enough |
| [S07](S07-artifacts-and-qualification.md) | What must be saved before we claim something works |

These definitions remain proposed until the relevant M00 review or later recorded approval. A task log cannot silently change them. Use [the change template](../templates/spec-change.md) for a genuine change of scientific meaning or shared behavior. Editing wording alone does not imply new model or hardware support.
