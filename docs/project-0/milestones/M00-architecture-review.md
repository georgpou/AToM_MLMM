# M00: Shared architecture and contract review

**Progress:** [STATUS.md](../STATUS.md). **Scope:** design approval, not numerical qualification. Review only the assigned sections; do not repeat an already accepted decision without a relevant amendment.

## What to read

Read [S01](../specs/S01-scope-and-invariants.md) for scope, [S02](../specs/S02-architecture-and-dependencies.md) for responsibilities, [S03](../specs/S03-data-and-interface-contracts.md) for shared records, [S04](../specs/S04-embedding-and-model-contracts.md) for energy and link rules, [S05](../specs/S05-protocol-and-thermodynamic-contracts.md) for thermodynamics, [S06](../specs/S06-validation-and-tolerances.md) for checks, and [S07](../specs/S07-artifacts-and-qualification.md) for evidence. These can be split into explicit review assignments.

## Combined review: what to check and why

Read S01-S05 together. Confirm that the physical builder owns all embedding physics, the transfer protocol owns geometry and result meaning, and the ATM assembler consumes both without model or ligand-count branches. Confirm full-real-atom force coverage, fixed membership, explicit units, and schema/version rules.

Walk through two future changes on paper. First, replace the local mechanical provider with an environment-dependent energy that exerts forces on MM atoms. Second, replace a one-ligand transfer with two unequal mobile groups. Identify the exact modules that change and those that must not change. The early analytic tests in G01-G03 must expose an implementation that violates these boundaries.

Review requirement ownership, proposed tolerances, candidate dependencies and the cap/periodic/thermodynamic definitions. Do not approve an actual electrostatic Hamiltonian by implication; only its extension boundary is being designed here. Identify scientific questions as explicit decisions rather than leaving agents to guess during coding.

## Acceptance condition

An identified reviewer records the scope, reviewed spec revisions, accepted/amended decisions and requirement ownership. No unresolved conflict in a public force/map/unit/correction contract remains. This is a design acceptance, not a numerical pass.

A review split across assignments needs a final recorded decision covering the combined scope. Analytic CPU approval does not approve model/GPU execution or actual electrostatic physics.

## Handoff

Use `Worker_Log/Milestone_00/Milestone_00_vN_worker.md` and matching `_audit.md`; documentation maintenance instead uses `Documentation_vN_worker.md`. Follow [AGENTS.md](../../../AGENTS.md#logs-and-handoff). No earlier milestone is required. After relevant design approval, assign G00/G01 work; later numerical gates still require evidence.
