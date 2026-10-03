# G07 joint cavity/ligand composition — v1 worker

**Scope:** G07-T1/T2/T3 numerical implementation and seven stable assertions; G07-T4 frozen physical preparation and sensitivity screen.\
**Outcome:** blocked for G07-T4 and combined M03 physical acceptance.\
**Finished:** 2026-10-03, UTC.\
**Snapshot:** child `m03-g06-g07`, accepted G05 base `08ccee74d0da900ffb1bd98d076e6e87e9df1b0c`; [immutable source and hashes](evidence/G07_v1/snapshot.json). Subsequent worker/STATUS/verification records change reporting only. No independent review was performed; the requested reviewer is GPT-6.1-sol/MAX.

One capped neutral protein fragment plus one complete ligand, and two unequal complete ligands (methanol/acetamide), now pass direct/native ATM/AToM comparisons at both maps and intermediate softplus settings. Fixed ML membership, stationary protein/cap maps, contact/disconnected graphs, MM boundary-parent derivatives and periodic finite-difference step sweeps are checked. The all-ML uncut reference uses the same physical builder with zero caps. AToM's topology previously omitted the cap particle, making its displacement map one particle short; it now includes every real and derived particle in final-particle order. The intended integrated guard failure and repair evidence are preserved.

Analytic local/environment providers run through the same assembler, endpoint checker and both protocol definitions. Executable omitted cap/environment and doubled-parent force faults fail the checker. These ten contract cases exercise architectural substitution; they do not qualify an actual electrostatic molecular provider. No embedding branch was added to shared transfer code.

Actual **GAFF 2.2.20/AM1-BCC** preparation freezes charges, exact atom order/stereochemistry, original MM XML and templates for four complete neutral molecules and six compositions. [Preparation](../../fixtures/fragment_ligand/prepared-mm-v1/manifest.json) uses the unchanged M00 v3 nuclear coordinates before model scoring. AM1-BCC's AmberTools calculation ran; **no new reference DFT/Psi4 calculation ran**. The reference prefix is absent and was not rebuilt. All **50 physical descriptions** on **20 immutable rows**, including real coordinates/maps/caps and complete retained/removed ledgers, are [frozen](../../fixtures/fragment_ligand/descriptions-v1/manifest.json).

The exact [reference matrix](../../fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json) reuses 20 hash-verified G05 capped records and identifies **30 new jobs**: 20 full-parent contacts/controls (32–40 atoms) and ten alternative ethane caps (14–17 atoms). Method, basis/settings, 105-package reference lock, model and all limits are unchanged. The G05 budget does not cover this new batch. The [conditional execution proposal](../../docs/project-0/reference/G07-reference-execution-proposal-v1.md) records a review-first feasibility pilot and budget choices; no choice or budget has been inferred.

## Scientific blocker

Across all 50 saved hybrid single points, independent energy agreement is at most **4.656612873077393e-10 kJ/mol**, and all-real force component agreement is at most **2.7853275241795927e-12 kJ/mol/nm**. This numerical agreement does not establish physical acceptance.

**Seven of all 40 region-pair comparisons exceed the frozen 0.05 eV/angstrom net complete-ligand force sensitivity limit.** Maximum is **0.12165016265111903** for threonine/acetamide `ethanol-acetamide-d3-r60`, baseline versus uncut. Six failures involve threonine contacts; the seventh is isoleucine/acetamide `butane-acetamide-d3.4-r0`, baseline versus alternative-ethane (**0.05009131648916323**, not rounded to a pass). Maximum within-description contact-energy sensitivity is **0.9744628863435872 kcal/mol**, below its 1.0 limit. Every separated control and region pair is retained.

The [full report](evidence/G07_v1/RESULTS.md), [all pairs/vectors/hashes](evidence/G07_v1/region-sensitivity.json) and independent saved-record analysis preserve model and retained-MM attribution. Both terms contribute to the worst force difference. No input, cut, threshold, parameter, model or existing reference was tuned in response. Uncut MACE is not quantum truth: Qfull and alternative-cap references are absent, so `hybrid − Qfull = (MACE − Qcap) + (Qcap + retained MM − Qfull)` remains unmeasured. Missing physical references independently block stable assertions **G07-08/09**; their planned boundary-reference test module is not represented as a pass or skip.

## Verification

All scientific shells activated `/workspace/atom-mlmm-g05-v2/activate.sh`, from `/workspace/AToM_MLMM-m03-g06-g07`, with two threads and serialized heavy checks.

| Check | Actual command/result |
|---|---|
| Uncut and matrix RED | [Uncut missing-cap-count path](evidence/G07_v1/red-uncut.log) and [missing matrix implementation](evidence/G07_v1/red-matrix.log) reproduced before changes |
| First composed native/AToM run | [4 intended cap-map failures, 5 passes](evidence/G07_v1/first-joint-integration.log); after topology repair [9 passed](evidence/G07_v1/joint-integration-green.log) |
| Composition/extension/geometry focused GREEN | `python -m pytest tests/contracts/test_embedding_extension.py tests/integration/test_periodic_geometry.py tests/integration/test_joint_hybrid_atm.py -q`: [28 passed in 29.09 s](evidence/G07_v1/composition-focused-green.log); later periodic FD case is included in the final full suite |
| Fifty actual full-real single points | `PYTHONPATH=src:. python tools/collect_joint_evidence.py --output Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points`: [50 numerical comparisons passed](evidence/G07_v1/fifty-description-single-points/summary.json); zero new DFT jobs |
| All region comparisons | `python Worker_Log/Milestone_03/evidence/G07_v1/analyze_region_sensitivity.py`: 20 geometries / 50 descriptions / 40 pairs / **7 physical force failures**; analysis exits 0 to preserve the complete blocked result |
| Final available CPU suite | `python tools/monitor_cpu_check.py --output Worker_Log/Milestone_03/evidence/G07_v1/final-cpu-suite -- python -m pytest -q`: **381 passed in 253.35 s**, exit 0; [command output](evidence/G07_v1/final-cpu-suite/command.log), [receipt and resources](evidence/G07_v1/final-cpu-suite/result.json) |
| Strict environment | `python /workspace/atom-mlmm-g05-v2/validate.py --root /workspace/atom-mlmm-g05-v2 --repository "$PWD"`: **9/9 passed**, exit 0; [output](evidence/G07_v1/final-environment.json) |
| Documentation | `python tools/check_docs.py --self-test --output Worker_Log/Milestone_03/evidence/G07_v1/documentation-final.json`: **0 errors / 8 self-tests passed**, exit 0; [final output](evidence/G07_v1/documentation-final.json) |
| Accepted-data preservation | `python Worker_Log/Milestone_03/evidence/G07_v1/check_preservation.py`: 1,733/1,740 base files identical, only seven intended existing source files changed. **46** original QM records and all prior scientific artifacts/evidence unchanged; **75** new fixture-file hashes verify. [Result](evidence/G07_v1/reference-preservation.json) predates the report-only STATUS update. |

Initial periodic-oracle and extension fault setup errors remain preserved separately from intended scientific RED evidence: first periodic test mismatched its PME box/parameters; the corrected test reproduced the missing native periodic interface. The extension harness first tried SWIG pickled-function conversion, then read the same trusted function from verified XML. One exploratory SWIG ownership probe segfaulted after taking a Force from a temporary System; retaining the owner fixed the probe. These are not passed numerical checks or resource/OOM events.

The final suite sampled 1.632 GiB maximum process-tree RSS and 1.562 GiB child maximum RSS. Cgroup usage reached its 8 GiB cap including cache; 1,944 `max` events and zero OOM/OOM-kill deltas. Minimum sampled free disk was 20.10 GiB. Larger new-reference runtime/RSS are unmeasured; internal Psi4 allocation is not an RSS ceiling.

## Handoff

Review the observed sensitivity failures and frozen design using **GPT-6.1-sol/MAX** before any new reference pilot/batch or scientifically justified scope change. The user was offered a concrete conditional budget decision; no answer has been received, no budget granted and no independent auditor spawned. All covered local implementation, preparation, numerical calculations and reports are complete. Remaining G07-T4 references, physical qualification and combined M03 acceptance are blocked. G08, protein/GPU/dynamics/electrostatic/binding qualification were not started.
