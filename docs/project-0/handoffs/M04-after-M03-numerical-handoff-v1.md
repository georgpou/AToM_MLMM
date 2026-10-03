# Continue analytic thermodynamic validation while physical qualification is deferred

**Recorded:** 2026-10-03, UTC.\
**Predecessor:** `m03-g06-g07` at `5c4887a`; tested source `c584086da68654b07f1a477d7ce1e48da42a9838`.\
**Purpose:** Preserve the interpretation of the M03 findings and identify independent next work. This note does not accept G06/G07, change a scientific threshold, or authorize new QM or an audit.

The user considers investigation of cut/region sensitivity a lower priority than continuing engine development. Independent review remains deferred to conserve the remaining session quota; when requested, the reviewer is GPT-6.1-sol/MAX. No new G07 reference-compute budget has been selected.

## What is established and what remains unknown

The [G06 worker](../../../Worker_Log/Milestone_03/Gate_06_v1_worker.md) and [G07 worker](../../../Worker_Log/Milestone_03/Gate_07_v1_worker.md) record 381 passing CPU tests, independent native/adapter force agreement, finite-difference checks, explicit retained-MM accounting, periodic geometry checks and direct/native ATM/AToM integration. These support implementation correctness for the tested small-system CPU profile. Independent acceptance of G06/G07 is pending.

The [sensitivity report](../../../Worker_Log/Milestone_03/evidence/G07_v1/RESULTS.md) compares different MACE-based partitions, including an all-ML uncut description. It does not compare those seven exceedances against full QM, and all-ML MACE is not a quantum reference. Seven of 40 region-pair net-ligand-force differences exceed the predeclared 0.05 eV/angstrom project budget, maximum 0.12165016265111903. Energy sensitivity remains below 1.0 kcal/mol. Preserve every row, cut, threshold and saved result.

These are physical-description sensitivity measurements, not demonstrated failures of link-force redistribution or unexplained numerical inconsistencies. Threonine has six contact exceedances at the C-alpha–C-beta cut. For isoleucine, the same cut is closer to uncut MACE than the alternative C-beta–C-gamma1 cut in all eight contacts; changing the cut also changes the ML-region size. The current matrix cannot isolate backbone involvement as the cause.

The planned matched quantum/MM references and complete-parent quantum references are required to separate model error from cap/partition/MM approximation. Thirty new references remain absent. The current physical profile remains unqualified; the sensitivity budget is project-specific and cannot be treated as a universal literature requirement. Deferring this investigation neither erases the exceedances nor establishes an inaccurate engine.

## Independent next work

[M04 / G08](../gates/G08-thermodynamics-and-estimators.md) requires G02/G03, accepted in [M02](../../../Worker_Log/Milestone_02/Gate_03_v2_audit.md). G08 explicitly states: “This gate can be developed alongside G04-G07 once G02-G03 pass.” It can therefore advance without new G07 QM or M03 physical acceptance.

Use the reviewed analytic known-answer problem to check the nonzero free-energy difference, endpoint signs, restraint corrections, directional midpoint bridge, reduced-energy reconstruction and independent PyMBAR/UWHAM analyses. These tests validate thermodynamic machinery without making protein or binding-accuracy claims and do not require expensive quantum calculations. Read G08 and its relevant S05/S06 sections before implementation, preserve the child lineage and use an unused worker attempt.

[M05 / G09](../gates/G09-solvent-preparation-and-export.md) currently requires G07 and G08. Its molecular preparation/pilot qualification and later binding claims must retain their stated prerequisites; this note does not mark M03 complete or waive them. A separately scoped engineering prototype is not an accepted physical demonstration.

An energy/force derivative mismatch, missing or duplicated interaction, bad mapping, nonfinite result or unexplained discontinuity would reopen an implementation blocker immediately. No such unresolved defect is established by the saved cut-sensitivity comparisons.
