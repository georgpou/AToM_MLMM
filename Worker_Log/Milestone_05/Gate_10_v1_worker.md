# G10 actual-worker pair exchange — v1 worker

**Scope:** G10-T2 bounded actual-worker two-state decision, fresh energy/state history and checkpoint/portable-State checks; inherited fixed-window restart/failure evidence. This is not a production exchange controller or full G10/M05.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-05T10:29:52.960407+00:00.\
**Model/version:** GPT-6-based Codex; exact model/version and reasoning setting not exposed.\
**Snapshot:** `m04-engine-readiness`, base `8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1`; tested implementation `5645db24f707adbdaff34dc7de6ac04b518d7d6b`. The matching frozen submission adds reports/evidence only.\
**Previous scope:** [G09 v2 audit](Gate_09_v2_audit.md) accepted vacuum worker/restart subsets; [G09 v3 worker](Gate_09_v3_worker.md) submits the new explicit-water profile.

## Changes and checks

`adapters.atom.attempt_pair_exchange` requires two distinct sealed actual workers, common complete Hamiltonian/schedule/runtime, two admitted state labels and distinct walker IDs. It obtains all four full context energies through actual worker refreshes, including outside contributions. The pinned AToM `pairwise_metropolis_sampling` performs the decision using `v_i(y)+v_j(x)-v_i(x)-v_j(y)`. The adapter restores original assignments before the decision and refreshes accepted state energies; walker/configuration/velocity identities stay fixed. Evaluation failures propagate without a returned decision/history. Incompatible Hamiltonians and ambiguous labels are rejected before sampling.

The report records before/after state and fixed walker labels, full raw energies, reduced-energy matrix/exponent, refreshed accepted energies and physical/alchemical/runtime identities. Host RNG supervision, persistent exchange journals and correlated exchanging-walker estimators are later work; this adapter does not duplicate AToM scheduling.

Read G10-T2, S05 raw physical/alchemical energy, S07 worker/artifact/observable contracts and the [amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md). Environment, unchanged numerical limits, exact source hashes and serial execution commands are recorded in the [G09 worker](Gate_09_v3_worker.md).

| Check | Actual result |
|---|---|
| Initial exchange tests | Failed on absent API before implementation |
| Analytic ABFE/RBFE four-energy oracles | Passed; nonlinear softplus/soft-core, offsets, both directions, nonzero outside term; cached reports deliberately poisoned before fresh evaluation |
| Pinned Metropolis threshold challenges | Passed; controlled only the random variate above/below independently calculated threshold, ran actual upstream decision |
| `python -m pytest -q tests/workflow/test_replica_exchange.py` | 0; **eight passed in 30.92 s**, including both real-water controls and incompatible-worker rejection |
| Water state/history checks | Passed; four-entry matrix matches independently reconstructed saved records, fixed walker IDs, accepted state changes and exact velocity preservation; checkpoint and portable-State reload return current parameters/energies |
| Shared affected suite | 0; 35 passed in 86.36 s; separate final clearance regression passed |
| Final full CPU suite | 0; **489 passed in 481.86 s**, no skips |

[Exchange evidence](evidence/G10_v1/README.md) preserves actual ABFE/RBFE reports and their input raw observations/records, summaries and metadata. Worker/full-suite output and environment evidence are shared with G09 v3; no duplicate full installation is claimed.

## Handoff

Submit for one independent review with G09 v3. The proposed periodic/water amendment remains pending until that review. Full G10/M05, a persistent exchange controller, host RNG restart guarantees, exchanging-walker correlation analysis, new solvated offline/profile challenges, dense liquid, GPU and molecular binding accuracy remain open. Established G08/M04 acceptance and G07/M03 blockers are unchanged. No independent acceptance is claimed here.
