# G07 actual pilot admission and partial physical evidence — v4 audit

**Reviewed worker/snapshot:** [Gate_07_v2_worker.md](Gate_07_v2_worker.md), branch `m03-g06-g07`, execution source `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`.\
**Scope/profile:** completed validation-only admission, one contact's saved force/energy arithmetic, plain retained-MM XML, and the decision to stop. OpenMM Reference double; no new MACE or QM evaluation. Numerical G06/G07 acceptance remains inherited.\
**Reviewer and finished time:** independent GPT-6.1-sol / MAX, actual parent spawn configuration confirmed; 2026-10-04 12:45:09 UTC.\
**Verdict:** **accepted_for_scope** — these partial data and their arithmetic are verified. **Physical G07-T4 and combined M03 remain blocked; continuation is rejected.**

## Exact reviewed artifacts

The prior [v3 execution audit](Gate_07_v3_audit.md) remains unchanged at SHA `102f678257013779989ca400a4a1fb42645f55e154af685e319ff81894b15ff5`. All six reviewed source/authorization hashes still match v3. The new reviewed artifacts are preserved separately with [review-state.json](evidence/G07_v2_pilot_partial_independent/review-state.json).

| Artifact | SHA-256 |
|---|---|
| Actual corrected receipt | `2b8ea63e59a1806bdec9af1c9867ab31de526d009c9a95f93c97c9984bef03ef` |
| Admitted full-parent record | `c1e34ea209bf4949c0f200859a75a35072ee5cf6e1750f8d7a9044a7259f0eed` |
| `pilot-force-comparison.json` | `becf5c2b0511343965b07c5e29988a7b4892fe00401d4cac0871d3d38143217a` |
| Comparison script | `142f6500eb90e6e91842fc7911c9787294d266b7d3a74dc9db11bfea1ff40c9e` |
| `pilot-assessment.json` | `8296da765bfb7444c5654a2b0a253a2a3c7d5c9898d6a5bcc96aae14627dc9b5` |

Every comparison input hash was checked, including accepted capped contact/separated records, both saved MACE descriptions, frozen geometries/maps/settings, the quantum matrix and unchanged reference proposal. The independently evaluated baseline artifact is SHA `fa2070023763c56bd89438221e6e5f35d6161acd5710fe4cc0e356379a5aec22`; its retained-MM XML is SHA `b614825e113321efc0d1327fbee6cda86e074e2c516690ea3ff339f69f5e44e5`.

## Actual admission

The corrected receipt equals the original receipt with only the documented validation-only correction fields and diagnostic manifest changed. Every copied input, record, log, resource sample and historical worker identity is byte-identical to the original. The original receipt retains its parser rejection at SHA `b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f`.

The actual checkpoint admits **1/30**, leaves **29 remaining**, and points to the exact corrected receipt/source hashes. Published record and both SCF logs match the correction source. Both sessions are closed; the second stops at `pilot_assessment_pending`. The cumulative debit is **2325.644650052 seconds**, comprising the original **2325.643222641 seconds** plus **0.001427411 seconds** of coordinator time. There is one actual quantum worker attempt and one validation-only attempt, with no live group or remaining scratch. The auditor changed no actual receipt, ledger or original file. All **46 accepted G05 records** remain exact base bytes.

## Independent force and energy arithmetic

After activating `/workspace/atom-mlmm-g07/activate.sh`, the auditor ran [verify_partial_pilot.py](evidence/G07_v2_pilot_partial_independent/verify_partial_pilot.py), exit **0**. [Results](evidence/G07_v2_pilot_partial_independent/independent-result.json) and [command output](evidence/G07_v2_pilot_partial_independent/independent-run.log) preserve actual values. No heavy model/QM module was imported, and no model or QM call occurred.

An independently constructed coordinate Jacobian projects the fixed 0.109 nm cap once to both parents, **p5 and p4**, with central-difference checks at `1e-5`, `1e-6` and `1e-7` nm. Maximum Jacobian error at `1e-6` nm is **2.35e-11**. Quantum gradients were matched to saved model coordinates/elements and converted to forces with the frozen Hartree/bohr constants; all 32 real rows are retained. All reported force arrays and metrics reproduce within **1e-12 eV/angstrom**.

Plain OpenMM Reference evaluation of the exact frozen retained-MM XML contains only standard MM forces. It agrees with `hybrid − projected MACE` to **1.50e-15 eV/angstrom** across all real coordinates. Those already-real MM forces are added once, without another cap projection. The vector identity

`hybrid − Qfull = (projected MACE − projected Qcap) + (projected Qcap + retained MM − Qfull)`

holds to **2.78e-17 eV/angstrom**. RMS values summarize the vector terms; their scalar values do not define additive error shares.

All force values below are eV/angstrom. The unchanged limits are **0.05 component RMS**, **0.15 maximum atom vector**, and **0.05 net ligand vector**.

| One-contact diagnostic | Component RMS | Maximum atom vector | Net ligand vector | Existing-limit outcome |
|---|---:|---:|---:|---|
| Projected same-cap MACE − Qcap | 0.012715 | 0.075982 | 0.034183 | All three below limits for this row |
| Projected Qcap + all retained MM − Qfull | 0.394209 | 2.054388 | 0.017461 | RMS and maximum fail |
| Baseline hybrid − Qfull | 0.395125 | 2.054388 | 0.046198 | RMS and maximum fail |
| Full-parent MACE − Qfull | 0.040013 | 0.171657 | 0.114731 | Maximum and ligand fail |

The maximum baseline/remainder error is on **p9**, an MM-region carbonyl oxygen; the projected same-cap model maximum is on p6 and full-parent MACE maximum on p4. This contact demonstrates a large partition/retained-MM reference discrepancy alongside the smaller same-cap model discrepancy. It does not establish a general cause or a repaired physical profile. A small net ligand error does not qualify the failing all-real force conditions.

For the baseline's **own capped contact-minus-separated** zero, saved MACE gives **−2.488598858 kcal/mol**, capped QM **−2.753778370 kcal/mol**, and their error **+0.265179512 kcal/mol**. The full-parent separated QM reference is absent. Full-parent energy attribution and the complete contact/region physical comparison therefore remain incomplete; no absolute cross-composition energy subtraction was made.

## Measured decision to stop

The assessment binds the exact admitted record, corrected receipt, original resource samples, matrix and checkpoint SHA `8e5fee37b95288137d9c6b5a7cefe1307a9435a2ef33d03be0f560d8c2f2c0c6`; `continue_authorized` is **false**.

The auditor independently parsed the exact hash-verified orbital and auxiliary Gaussian basis files, without importing Psi4. Counts match all 30 frozen jobs; the pilot has **836 orbital / 1386 auxiliary functions**. Recomputed screens agree with the assessment:

- Remaining runtime: **34.164590 hours**, versus **23.353988 hours** left in the same cumulative 24-hour budget.
- Largest RSS screen: **5,189,601,468 bytes**, below the 6 GiB guard; this remains an estimate.
- Largest scratch screen: **17,997,534,324 bytes**. With the mandatory 5 GiB reserve, **21.761510 GiB** is required versus **18.370361 GiB** free at assessment.

These screens estimate future jobs; they are not measured upper bounds or completion guarantees. The actual false assessment is rejected by the continuation validator. A separate auditor-owned copy with only its flag changed to true is also rejected for exceeding the remaining resource/budget envelope. Both checks preserve actual ledger and original bytes.

## Decision and handoff

The actual no-QM correction/admission, this single-contact arithmetic, and the hash-bound decision to stop are accepted as partial evidence. They do not pass the physical gate: this contact already fails the existing full-real force conditions, **29 new references remain missing**, the full-parent separated energy zero is missing, and all **seven inherited sensitivity failures** remain preserved. G07-T4 and combined M03 physical closure remain **blocked**. The prior numerical acceptance was not re-audited.

Do not continue or rerun the batch under the present budget. Session-quota reset does not reset its ledger. The cleanup inventory remains optional and no auditor deletion occurred; its 1.325 GiB archive total cannot remedy either this time screen or the observed scratch deficit. A later resource/profile decision must retain these failures, hashes, controls and cumulative debit.
