# ADR-0002: analytic extension contracts before molecular generalization

**Status:** proposed for M00 review. **Source:** current requirement to avoid mechanical-to-electrostatic and ABFE-to-RBFE redesign.

## Context

Waiting until G12 to introduce the idea of two ligand groups can expose a one-ligand core too late. Waiting for a real electrostatic model before testing environment derivatives can similarly leave ML-only force outputs and stale field caching hidden inside the transfer engine.

## Proposed decision

G01 admits tuple-based mobile groups and full-real-force result semantics. G02 tests one and two unequal groups through the same assembler, and an analytic energy depending on an MM coordinate. G04/G07 extend the latter to cap parents and the integrated pipeline. Actual molecular RBFE remains G12; actual electrostatic physics remains outside Project 0.

## Acceptance and boundaries

The environment probe must change energy/forces when only MM coordinates change, rebuild its dependencies under both maps, and be independent of evaluation order. It must produce all influencing real-coordinate derivatives. The two-group probe must preserve unequal/noncontiguous identities without atom-pair mapping assumptions.

Passing these probes admits architectural behavior only. It does not establish external-field physics, charge response, self-consistent convergence, periodic electrostatics, model accuracy, or a production electrostatic backend. Those require a future scientific specification and profile evidence.

**Normative proposals:** [S04](../specs/S04-embedding-and-model-contracts.md), [S05](../specs/S05-protocol-and-thermodynamic-contracts.md). **Owners:** G01, G02, G04, G07; regression at G12/G13.
