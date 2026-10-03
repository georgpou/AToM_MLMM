# G07 reference execution proposal v1

**State:** prepared for review and a new compute-budget decision; no new G07 QM is authorized or launched. This preserves the accepted M00 v3 geometries, scientific method, checkpoint and numerical/chemical limits.

**Subsequent evidence blocks the submitted profile:** the frozen 50-description hybrid evaluation has seven of 40 region-pair force comparisons above the predeclared 0.05 eV/angstrom limit (maximum 0.12165016265111903). Maximum contact-energy sensitivity is 0.9744628863435872 kcal/mol, below its 1.0 limit. See the complete [sensitivity report](../../../Worker_Log/Milestone_03/evidence/G07_v1/RESULTS.md). This is hybrid region sensitivity, not the still-missing quantum partition-error measurement. Independently review the finding before any pilot or batch; the execution choices below are conditional proposals. New reference data alone cannot make an already failing sensitivity screen pass.

The [actual prepared MM](../../../fixtures/fragment_ligand/prepared-mm-v1/manifest.json) now freezes GAFF 2.2.20 and AM1-BCC charges on each complete neutral molecule through the locked AmberTools 26.0 environment. The exact M00 v3 conformer is supplied for charge assignment; its nuclear coordinates are unchanged. The corrected threonine orientation remains score-free. Separate systems for each parent/ligand composition include no cap MM parameters, constraints or dispersion correction.

The [physical descriptions](../../../fixtures/fragment_ligand/descriptions-v1/manifest.json) freeze all 50 descriptions on the unchanged 20 contact/control rows, including full real coordinates/maps, cap records, original-MM XML and every retained/removed boundary term. Generated preparation artifacts preserve actual charges and force-field templates. Model energy/DFT scores do not enter this freeze.

The [exact quantum matrix](../../../fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json) contains:

| Jobs | Count | Atom count | Treatment |
|---|---:|---:|---|
| Baseline capped joint contacts | 20 | 15–23 | Reuse exact hash-verified accepted G05 records |
| Full neutral parent plus complete ligand | 20 | 32–40 | New energies and gradients; also Qcap for the all-ML uncut description |
| Alternative capped ethane plus complete ligand | 10 | 14–17 | New energies and gradients |

Every job uses restricted omega-B97M-D3(BJ)/def2-TZVPPD with the unchanged 105-package reference lock, Psi4 1.10.2/LibXC 7.0.0, fixed basis hashes, density-fitting auxiliary basis, SCF limits, C1/no-reorient/no-COM and 99/590 grid in the approved reference settings. No paid service, geometry optimization, alternate functional or basis is proposed. The absent reference environment will be rebuilt under the unchanged lock only when needed.

For each description use its own contact-minus-separated energy zero. Independently project Qcap raw forces once and combine them with every retained-MM real force. Report the identity `hybrid − Qfull = (MACE − Qcap) + (Qcap + retained MM − Qfull)` separately for energy differences and real-coordinate forces. Keep the model, cap/partition and retained-MM contributions separate. No absolute cross-composition subtraction or binding correction is defined.

The existing chemical limits remain: maximum contact/region sensitivity 1.0 kcal/mol and net ligand force difference 0.05 eV/angstrom; full-real force component RMS 0.05 eV/angstrom and maximum atom-vector error 0.15 eV/angstrom. Preserve all rows, signs, failed attempts and nonfinite results. Missing or failed references leave G07-T4 and combined M03 physical acceptance blocked.

## Proposed execution choices

1. **Recommended first step: independently review the sensitivity failure and prepared plan using GPT-6.1-sol/MAX.** Only after a reviewed decision supports further reference work, authorize a one-hour feasibility pilot. Exact pilot job: `ethanol-methanol-d3-r0--full-parent` (32 atoms). Use one worker, two threads and 3 GiB internal Psi4 allocation; stop safely if process-group RSS exceeds 6 GiB or other measured resource guards leave inadequate headroom. Retain the job/order, one-second process-group and cgroup samples, actual exit receipt, scratch identity and cumulative charged time. Review its actual time/RSS/disk/convergence before authorizing the remaining batch.
2. **Full matrix option:** the same review followed by a separate cumulative 24-hour G07 ceiling for the 30 new jobs, still starting with that pilot and pausing if its resource/timing evidence does not support continuing. This is a requested ceiling, not a measured completion estimate. Preserve cumulative accounting across retries; do not reset a budget. Stop at the ceiling, a guard failure or a scientific limit failure.
3. **Hold new QM:** finish the software verification/handoff, leaving this concrete matrix, references, MM artifacts and ledgers ready for a later resource decision.

The machine's limits are 8 GiB cgroup RAM, no swap, a two-CPU quota and approximately 21 GiB free disk after CPU setup. Psi4 allocation is not an RSS ceiling. Serialize all QM and model-heavy tests, retain the R1/R2/R3 receipt/lease/process-group/durability protections and clean/verify the whole worker group before publishing or scheduling another job. The larger full-parent RSS and runtime remain unmeasured. The completed G05 12-hour budget is not authorization for this new batch.

An independent reviewer must inspect the exact recorded source/artifact snapshot and must not launch QM. Its model is GPT-6.1-sol with MAX reasoning, as requested. Combined M03 acceptance remains a later review after the applicable G06/G07 evidence, including the physical comparisons, exists.
