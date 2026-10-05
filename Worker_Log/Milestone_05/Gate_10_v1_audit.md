# G10 actual-worker pair exchange — v1 audit

**Reviewed worker:** [Gate_10_v1_worker.md](Gate_10_v1_worker.md).\
**Snapshot:** `m04-engine-readiness`, exact HEAD `b11c16750ad111a2fcafcda7a2d51c6690254e97`, against `8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1`; tested code `5645db24f707adbdaff34dc7de6ac04b518d7d6b`.\
**Scope/profile:** G10-T2 single actual-worker pair decision and current energy/state history, including fixed-coordinate checkpoint/portable-State refreshes; analytic ABFE/RBFE and the two sparse classical-water controls on pinned AToM 8.5.0b0, Reference double/MACE CPU float64, NVT 300 K.\
**Reviewer:** independent `gpt-6.1-sol`, MAX dispatch setting; no delegated reviewers.\
**Finished:** 2026-10-05T10:45:16+00:00.\
**Verdict:** **accepted_for_scope** for the specified G10-T2 pair boundary. This does not accept the G09 failure-archive implementation or a complete G10/M05 scope.

## Evidence

Read G10-T2, S05 raw/outside/total potentials and S07 worker/observable contracts, the plan and [amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md). Reviewed the adapter diff and actual `WorkerRun.evaluate`, state setters/restorers, sealed force ownership and pinned upstream `pairwise_metropolis_sampling` source. Shared exact commands, profiles and verification are in the [G09 audit](Gate_09_v3_audit.md) and [independent evidence](evidence/cloud_v3_independent/README.md).

Independently reran the affected files: **28 passed in 92.83 s**, including all eight submitted exchange cases. Analytic oracles explicitly cover nonlinear softplus/soft-core parameters, offsets, both directions and a nonzero outside term; cached reports are poisoned before the real fresh evaluations. Draws on both sides of the independent Metropolis threshold exercise the actual pinned decision. Water matrices match independently reconstructed saved records, accepted state labels swap, fixed walker/configuration/velocity identities stay attached to their workers, and checkpoint/portable-State reloads refresh current energies/parameters.

Additional independent probes passed:

- Failure at each of the four cross-state evaluations and both original-assignment refreshes propagates without reaching Metropolis. Failure at either postdecision refresh propagates without a returned report. The upstream routine has already drawn in those latter cases; the adapter does not promise transactional rollback or failure recovery.
- A finite but overflowing coordinate produces a genuinely nonfinite actual child evaluation and rejects before Metropolis. An injected unadmitted `Lambda1`-dependent outside-force mutation rejects through the sealed System guard before a decision.
- A live-box injection survives actual checkpoint and portable-State restoration with exact positions, velocities and parameters. This tests preservation, not a variable-cell ensemble.
- All 48 scientific source/input hashes and 125 submitted capture hashes match; both local full workers' 48 payload hashes match. Captured ABFE/RBFE exchange matrices and exponents agree with their own raw records; reports retain fixed walker IDs and before/after state IDs.

The shared independent probe suite yielded **7 passed, 1 failed in 5.72 s**; its sole failure reproduces G09-R2, outside this accepted pair-decision boundary. The submitted 489-test full-suite result was not rerun independently. No skipped/model-unavailable test was treated as numerical evidence.

## Findings

No Critical, Important or Minor finding blocks this bounded G10-T2 boundary. The adapter checks complete sealed Hamiltonian/schedule/runtime identities before evaluation, obtains four fresh complete context potentials divided by the common RT, restores original assignments with fresh evaluation, calls the pinned routine with the correct matrix orientation/exponent, then applies and refreshes accepted labels. It does not swap walker/configuration identities.

**Shared unresolved Important finding:** [G09-R2](Gate_09_v3_audit.md) hides an original scientific failure when mapped-State archival fails. It blocks acceptance of the submitted G09 failure-preservation scope and any combined claim requiring that behavior. It does not invalidate the independently verified pair potentials/decisions.

## Decision and handoff

Accept the amendment's bounded pair-exchange definition and its sparse-water/minimum-image-anchor scientific definition described in the G09 audit. General state-dependent outside terms are not admitted: current routing permits the declared static harmonic force only, and unsealed alternatives/mutations reject. Their full exchange implementation is expressly unqualified rather than inferred from the generic total-energy arithmetic.

Repair G09-R2 and review the new frozen snapshot before accepting the joint submitted technical scope. STATUS is unchanged under this review-only assignment. Persistent scheduling/journals, host RNG restart guarantees, postfailure rollback/recovery, exchanging-walker correlations, dense liquid, equilibrium/affinity, GPU and new solvated offline/process qualification remain open. No full G10/M05 or G07 physical acceptance is granted; earlier physical failures and QM accounting are unchanged.
