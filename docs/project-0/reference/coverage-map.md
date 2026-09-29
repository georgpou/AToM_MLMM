# Coverage map: revised plan to working documents

This is a subject-level reorganization of the preceding revised plan, not a claim of byte-identical file splitting. Gate IDs G00-G13 are retained. Proposed public interfaces, requirement IDs, M00-M08, early extension probes, and spec/test governance are new additions requested for this repository. [Provenance](../PROVENANCE.md) explains the raw-artifact limitation.

| Revised-plan material | Current home |
|---|---|
| Section 1: assessment, corrections, three meanings of success | S01, provenance, environment note, G00/G03/G06/G08 |
| Section 2: atom sets and operational Hamiltonian | S03, S04, G01, G06 |
| Section 3: link geometry, derivatives, constraints, boundaries | S04, G04, G07 |
| Section 4: PME and physical approximation diagnostics | S04, G06, scientific notes |
| Section 5: candidate software/model/preparation strategy | environment note, S07, G00, G05 |
| Section 6: ATM energy, routing, preparation and thermodynamics | S02, S05, G02, G03, G08, G09 |
| Section 7: repository design and interfaces | S02/S03; reorganized to isolate models, embeddings, protocols and the AToM adapter |
| Section 8: numerical validation methods | S06, G02-G07 |
| Section 9: model counterfactual domain and data | S06, G05, scientific notes |
| Section 10: work packages G00-G13 | One gate Markdown file per unchanged ID |
| Section 11: thresholds, sampling and sensitivity budgets | S06, G08, G11-G13 |
| Section 12: raw observables, reduced potentials, uncertainty, restart | S05-S07, G08-G10 |
| Section 13: performance and optimization order | G13, scientific notes |
| Section 14: second model, long-range/electrostatic, new maps, metals | S01-S05, extension guide, qualification matrix |
| Section 15: completion, handover and colleague review | M08, G13, status/evidence workflow |
| Appendix A: relationship to original brainstorming | This file and unchanged original archive |
| Appendix B: upstream sources | sources.md, keeping the earlier source locations |
| Appendix C: glossary | glossary.md |

## Important changes rather than silent edits

The prior implementation sketch used one broad set of helper modules and discussed future extension. The current version makes the physical/protocol/ATM/runner boundaries explicit proposed rules and adds typed record semantics, full-environment-force probes, dependency tests, multiple mobile-group records and early two-ligand tests. These additions address the user's explicit concern about mechanical-to-electrostatic and ABFE-to-RBFE refactoring.

G01 now includes lightweight schema, capability and evidence contracts. G02 introduces both protocol shapes and an analytic environment-coupled provider. G04/G07 extend that probe to link-parent derivatives and the integrated pipeline. G12 remains the full molecular RBFE gate. No gate was renumbered, and no actual electrostatic implementation was added to Project 0.

M00 adds design review before implementation. M01-M08 group gates into capability acceptance. M03 and M04 may proceed in parallel after M02; their dependencies join before G09/M05. This makes the original possible parallel analytic-analysis work explicit.

Shared specifications are the proposed behavioral authority after review. Gate documents contain implementation tasks and planned assertions. Milestone documents review the meaning of a group of passing gates. This separation avoids copying large theory sections into each task while keeping every agent linked to its relevant definition.

## Original brainstorming material retained

The uploaded original file is archived unchanged. Its initial OpenMM 8.5 baseline, stronger implication of real-atom renumbering, and simplified missing-tail narrative are historical, not instructions to override the revised source-aware plan. No original source was deleted to hide those changes.
