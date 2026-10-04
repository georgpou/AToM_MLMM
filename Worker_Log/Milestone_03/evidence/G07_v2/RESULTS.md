# G07 reference continuation: one validated pilot, batch checkpointed

The exact frozen pilot **`ethanol-methanol-d3-r0--full-parent`** completed an energy and 32-row gradient with explicit SCF convergence. **One of 30 new references is validated: one of 20 full-parent jobs, zero of ten alternative-cap jobs.** The other 29 were never launched. The matrix's **20 exact G05 baseline references** are available by unchanged hashes; **all 46 accepted G05 records** remain byte-identical. The numerical G06/G07 scopes retain their prior acceptance, while G07-T4 and M03 physical closure remain blocked.

The pilot ran on source `4e2cb06b0e5e0b3b081e379969428ec93a807866`, directly descended from published `34388d2b70d8fc032238cbf0dfa28e3290cc14e8`, on the existing `m03-g06-g07` branch. Exact locked reference environment: **Psi4 1.10.2 / LibXC 7.0.0**, all 105 frozen packages, unchanged `wb97m-d3bj/def2-tzvppd`, coordinates/order/neutral singlet/convergence/grid/basis hashes. No optimization or scientific substitution occurred.

## Actual calculation and recovery

| Item | Actual result |
|---|---|
| Energy | −726.579702009341 Hartree |
| Final SCF | Iteration 18; energy change 1.14824e−11, RMS residual 5.77813e−11; both below frozen 1e−10 criteria |
| Worker outcome | Exit 0; finite complete gradient; no scientific failure/interruption |
| Worker receipt wall time | 2,325.623395559 s |
| Current cumulative charged time | **2,325.644650052 s / 0.646012403 h**; includes conservative bookkeeping overhead |
| Remaining same batch allowance | **84,074.355349948 s / 23.353987597 h** |
| Peak supervised group RSS | **3.190 GiB**, below 6 GiB guard |
| Peak private scratch / minimum free disk during pilot | **9.015 / 9.921 GiB** |
| OOM events | Zero OOM/OOM-kill/group-kill deltas; cgroup current reached 8 GiB from cache pressure |
| Samples and allocation | 2,315 approximately one-second samples; two threads, 3 GiB internal Psi4 allocation |
| Post-stop state | No live supervised/matching worker; no private quantum scratch |

An initial parser expected `SCF has converged.` while this Psi4 output says `Energy and wave function converged.`. The successful worker's original parser-rejection receipt remains unchanged. After meaningful RED/GREEN tests, **416 full CPU tests** and independent GPT-6.1-sol/MAX [v3 recovery acceptance](../../Gate_07_v3_audit.md), source `fcc1de9619f58934ff0c5835e01ecf3848a8a48c` created a durable, explicitly **validation-only** `attempt-0002` and recovered the existing bytes. No new QM was run. Original time remains charged, with only 0.001427411 s added coordinator overhead. Coordinator exit 1 means the 30-job queue remains incomplete.

- [Original scientific record](quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0001/record.json), [SCF/gradient log](quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0001/record.psi4.txt), [original rejection receipt](quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0001/receipt.json).
- [Published validated record](quantum-attempt-v1/records/ethanol-methanol-d3-r0--full-parent.json), [validation-only receipt](quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0002/receipt.json), [correction statement](quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0002/revalidation.json).
- [Persistent progress](quantum-attempt-v1/progress.json), [actual recovery identity](actual-revalidation-result.json), [final preservation checks](final-preservation-validation.json), [exact commands](post-pilot-commands.md).

Original record SHA-256: `c1e34ea209bf4949c0f200859a75a35072ee5cf6e1750f8d7a9044a7259f0eed`. Original receipt: `b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f`. Validation-only receipt: `2b8ea63e59a1806bdec9af1c9867ab31de526d009c9a95f93c97c9984bef03ef`.

## Measured pilot assessment and continuation constraint

The hash-bound [assessment](pilot-assessment.json) sets continuation false. Its reviewed remaining-time screen is **34.1646 h**, above **23.3540 h** left. Largest-job scratch screening is **16.7615 GiB**; with the required **5 GiB** reserve it needs **21.7615 GiB** free against **18.3704 GiB** observed at assessment. Projected group RSS is **4.8332 GiB**, below its guard. These are conservative estimates from measured pilot data and exact frozen basis sizes, not verified bounds or measured future-job requirements. No runtime, RSS, disk or scientific limit was relaxed. A read-only [true-flag envelope probe](continuation-envelope-rejection.json) rejects the batch without changing the ledger or launching anything.

The user's five-hour session quota was reset after a graceful pause. That did not reset the cumulative 24-hour quantum budget or one-hour pilot ceiling. [The current handoff](../../../../docs/project-0/handoffs/G07-reference-remaining-v2.md) requires a concrete resource/budget review before further launch, preserving this ledger and admitted pilot.

## Limited physical findings from the one contact

The [saved-array comparison](pilot-force-comparison.json) separately measures same-cap MACE/QM error and the cap/partition plus retained-MM approximation relative to complete-parent QM. It projects the cap onto **p5 and p4 once** and retains all real MM forces. All raw/real arrays and source hashes are included. No additional model or QM calculation was run.

| Force difference (eV/angstrom) | Component RMS | Maximum atom vector | Net ligand vector |
|---|---:|---:|---:|
| Projected MACE − QM on the same cap | 0.0127151 | 0.0759817 | 0.0341827 |
| Capped QM + all retained MM − complete-parent QM | **0.3942092** | **2.0543877** | 0.0174609 |
| Baseline hybrid − complete-parent QM | **0.3951254** | **2.0543877** | 0.0461980 |
| Complete-parent MACE − same-structure QM | 0.0400127 | **0.1716568** | **0.1147311** |
| Unchanged limits | 0.05 | 0.15 | 0.05 |

For this contact, the cap/partition plus retained-MM approximation dominates the full-real error; its largest error is at MM-region carbonyl oxygen **p9**. Both baseline hybrid and that approximation exceed the fixed component RMS and maximum atom-vector limits. Complete-parent MACE exceeds its maximum atom-vector and net-ligand limits. This is limited evidence for one contact, not a 20-row qualification.

The same capped description's own contact-minus-separated energies are **−2.488599 MACE / −2.753778 QM kcal/mol**, error **0.265180 kcal/mol**. Complete-parent separated QM is missing, so no full-parent contact-energy or energy partition attribution is possible. No absolute cross-composition energies were subtracted.

Independent GPT-6.1-sol/MAX [v4 review](../../Gate_07_v4_audit.md) accepts these partial data/arithmetic and the decision to stop. It independently verifies cap Jacobians with three finite-difference steps, recomputes all force arrays/metrics and directly evaluates the frozen retained-MM XML. MM force agreement is 1.50e−15 eV/angstrom and the vector attribution residual is 2.78e−17. Scalar RMS values are not additive shares. This review does not accept G07-T4 or M03 and does not repeat the prior numerical audit.

Every existing control and **all seven original region-sensitivity exceedances** remain unchanged (maximum 0.12165016265111903 eV/angstrom, limit 0.05). The new pilot does not make those failures pass. G07-T4 and M03 are not accepted; M04/G08 was not started.

## Safe cleanup

The coordinator removed only private temporary scratch after verified whole-group shutdown and durable diagnostics/receipt. No code, log, accepted record, model, frozen setting, active environment or prior attempt was deleted. [Cleanup strategy](cleanup-strategy.md) and [path/size inventory](cleanup-candidate-inventory.json) identify 328 reconstructible package-download archives totaling **1.325 GiB** and narrowly conditional bootstrap candidates. Those files were not deleted. Lossless archival must retain original resume paths and verify round-trip hashes. Disk cleanup cannot solve anonymous worker RAM or the remaining runtime-screen deficit.
