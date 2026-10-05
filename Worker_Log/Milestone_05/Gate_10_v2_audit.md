# G10 persistent exchange and solvated restart — v2 combined independent audit

**Reviewed workers:** [G10 v2](Gate_10_v2_worker.md) and [G09 v5](Gate_09_v5_worker.md).  
**Snapshot:** `m05-colab-workflows`; base `fab6388b041acc4362f30b5ff7d3789a33fc536f`; frozen submission `bc6fd520308fba7e7448929138eb91e80ca6f063`; tested scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.  
**Reviewer:** independent agent `/root/m05_combined_review`, one combined scientific/code review; 2026-10-05 UTC.  
**Verdict:** **accepted_for_scope** — combined bounded G09/G10 CPU technical increment. This is not full G09/G10/M05 or M03 closure.

## Scientific and implementation decision

Accept the [persistent pair-exchange definition](../../docs/project-0/specs/m05-dense-exchange-amendment.md) together with the [G09 scientific decision](Gate_09_v5_audit.md). Same-temperature label exchange leaves configurations/velocities with stable walkers; the actual AToM adapter computes fresh four-entry complete potentials and owns the Metropolis decision. The controller adds supervision, not another physical Hamiltonian or acceptance implementation. Correlated records retain the full schedule for exact reconstruction without claiming an exchanging-walker uncertainty estimator.

The immutable round prefix, before/after states, sample/walker sequences, phase reports, two checkpoints/States and both Python/NumPy RNG streams are consistent with the stated transaction. Default pending-round rejection and explicit archived rollback/replay preserve the boundary semantics. Published rounds remain authoritative after later errors. Failed/uncommitted work is replayed from the last complete boundary; it is not admitted as an observed sample.

## Independent verification

Environment, the **41-pass** shared affected command, scientific/hash verification and complete raw evidence location are recorded in [G09 v5](Gate_09_v5_audit.md). The reviewer additionally ran, serially with the same activation and `PYTHONPATH=$PWD/src:$PWD`:

```bash
python -m pytest /workspace/m05-evidence/reviewer-v1/test_extra.py tests/workflow/test_replica_exchange.py -q --basetemp=/workspace/m05-evidence/reviewer-v1/additional --junitxml=/workspace/m05-evidence/reviewer-v1/additional.xml
```

**11 passed, 0 skipped; 42.03 s, exit 0.** Total fresh review pytest coverage is **52 passes**. Three reviewer-written cases inject (1) decision persistence failure before any decision bytes, (2) second-worker checkpoint capture failure, and (3) `KeyboardInterrupt` before decision persistence. Each rejects normal resume, retains the incomplete tree, restores the caller's global RNG streams and, after explicit recovery, reproduces exact complete transaction records and both RNG states at every boundary. Every previously written pending file remains byte-identical in the rollback archive. The other eight checks challenge independent exchange exponents/accepted and rejected outcomes, stale caches, solvated post-swap labels and incompatible-worker rejection through the real adapter.

The shared 41-pass run separately exercised phase failures, refresh failure without evaluation reentry, journal/publish/report failures, locking/tampering, saved-boundary energy freshness, actual guard settings, and both ABFE/RBFE fresh offline processes. The offline checks deny original source/run/cache paths and network, compare full observables, verify actual CPU float64 model tensors and Reference contexts, and distinguish exact same-checkpoint continuation from portable-State fixed-coordinate agreement.

Additional independent retained-data probes:

| Command / result | Actual outcome |
|---|---|
| `python /workspace/m05-evidence/reviewer-v1/check_evidence.py` | Verified both dense exchange prefixes, four rounds/eight samples each. A separately written scalar soft-core/softplus calculation reconstructs all **32 matrix entries** from the saved raw endpoints/outside energies and current labels: maximum discrepancy **0.0**. |
| `python /workspace/m05-evidence/reviewer-v1/reference_probe.py` → `reference-check.json` | Admitted the exact **108-row** CPU reference by SHA `8a625d5bdcbac5cc1ddeb244ff12d095b14f811a287ca18732f86c943dba8d73` and current source hashes. Independently recalculated four base-frame cap-parent force projections, **16 three-step real-coordinate FD sweeps**, zero ordinary-solvent ML forces, and changed graph counts. All checks passed without changing S06 thresholds. |

All commands above exited 0. The immutable reference identifies clean source `424a859`; approved model bytes and CPU locks remain unchanged. Submitted full CPU evidence is **543 passes/no skips**, independently hash/JUnit-verified, not redundantly rerun. Earlier accepted scopes are carried only where unchanged.

## Findings and required closure checks

**No Critical or Important defect found; no required CPU repair.** The five requested review risks are addressed within the bounded scope: environment/source/weight isolation, complete-copy rejection, round/RNG/history recovery, both-map solvent/parent derivatives, and explicit TPU admission gates.

The separate TPU probe is accepted as **unqualified experimental tooling**, not as a TPU implementation result. Inspection confirms actual backend checks, synchronized arithmetic precision probing, hash-bound real-model comparisons, full cap-parent projection, ATen fallback rejection, retained numerical/operator failures, and timing qualification only after admission. Lightweight negative/admission tests passed. Actual TPU arithmetic, operator coverage, fallback reporting reliability on hardware and speed remain **not_run / declined to judge**. A CPU reference or requested float64 dtype is not hardware evidence.

The exact user-run fallback is in the notebooks and [run instructions](../../notebooks/README.md): select the runtime, use the immutable reviewed source and reference identities, repeat isolated setup, restore/verify complete exports, run the actual probe, and return all reports/negative diagnostics. Actual Colab CPU/TPU qualification requires those returned artifacts and verification. No additional user permission or external service is needed to finish this local audit.

## Combined acceptance and handoff

Accept G09-01..05 and G10-01..04/06 for the declared bounded CPU controls and transaction behavior; G10-05 device claims extend only to the inspected Reference/CPU tensors. Accept the new scientific amendment within these limits. The source/profile-specific checkpoint guarantee does not extend to arbitrary hosts or libraries; a portable State does not preserve thermostat RNG. Local transaction tests do not establish mounted-storage atomicity or recovery from arbitrary hardware/filesystem damage.

Full milestone, M03, molecular accuracy, affinity, protein, density/equilibrium, pressure/virial, long production, statistical exchanging-walker analysis, GPU/multigpu and actual Colab/TPU remain unqualified. The seven G07 sensitivity failures, 29 missing references and QM ledger **2325.644650052/86400 s** remain unchanged. External OpenMM repair is outside this review's assigned action scope.

Next action: root may record this bounded acceptance, preserve the reviewer evidence and publish the authorized child-branch handoff; no implementation repair is requested. Actual hardware execution remains the explicitly documented user-run dependency. No implementation edits, commits, pushes, subagents or external messages were made by this reviewer.
