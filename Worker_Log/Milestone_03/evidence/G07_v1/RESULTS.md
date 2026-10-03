# G07 v1 physical-description sensitivity

**Outcome: blocked for physical acceptance.** All 50 saved hybrid single points agree with the independent numerical evaluator. Seven of all 40 region-pair comparisons exceed the unchanged 0.05 eV/angstrom net ligand force limit. The maximum energy sensitivity is 0.9744628863435872 kcal/mol, below its unchanged 1.0 kcal/mol limit.

Inputs and all boundary ledgers were frozen before these scores were evaluated. The 20 rows include four separated controls and 16 contacts; the threonine series has baseline/uncut choices, and the isoleucine series also has alternative-ethane. All pairs are included, including baseline versus alternative-ethane and every separated control. Historical names `ethanol` and `butane` describe capped fragments; their complete parents are threonine and isoleucine.

For each description, energy is contact minus its own separated control. Energy sensitivity is the difference of these within-description values. Force sensitivity is the norm of the difference of net complete-ligand force vectors at identical real coordinates. Net vectors sum every `a:` real ligand force, then convert using the exact admitted ASE CODATA 2014 factor. No absolute energies of different compositions are compared.

| Row | Region pair | Energy sensitivity (kcal/mol) | Net force sensitivity (eV/angstrom) |
|---|---|---:|---:|
| ethanol-acetamide-d3-r60 | baseline / uncut | 0.974462886 | 0.121650163 |
| ethanol-acetamide-d3-r0 | baseline / uncut | 0.017402136 | 0.095805422 |
| ethanol-methanol-d2.6-r0 | baseline / uncut | 0.253876446 | 0.083638209 |
| ethanol-acetamide-d2.6-r0 | baseline / uncut | 0.760122382 | 0.083060340 |
| ethanol-methanol-d3-r0 | baseline / uncut | 0.733441075 | 0.080921277 |
| ethanol-methanol-d3-r60 | baseline / uncut | 0.501025847 | 0.054518439 |
| butane-acetamide-d3.4-r0 | baseline / alternative-ethane | 0.206046417 | 0.050091316 |

For the worst row, `ethanol-acetamide-d3-r60`, the baseline-minus-uncut force difference has these contributions. Cap parents belong only to the protein, so summing raw model ligand forces introduces no further cap projection. Retained-MM force is the full real force minus the model contribution. Vector contributions add; their norms do not.

| Contribution | x | y | z | Norm (eV/angstrom) |
|---|---:|---:|---:|---:|
| Total hybrid | 0.099238871 | 0.068031979 | 0.017945986 | 0.121650163 |
| Model | 0.074469035 | 0.008651193 | 0.057849680 | 0.094694592 |
| Retained MM | 0.024769836 | 0.059380785 | -0.039903695 | 0.075709493 |

Both physical contributions matter. Independent all-real numerical agreement is at most 4.656612873077393e-10 kJ/mol in energy and 2.7853275241795927e-12 kJ/mol/nm in force components across the 50 descriptions. The routing, unit and derivative tests pass, including native ATM/AToM and finite differences; those results do not qualify the physical Hamiltonian.

**Reference limitation:** This is a hybrid region-sensitivity screen, not a quantum partition-error measurement. The 20 Qfull and ten alternative-cap DFT references are absent. The uncut MACE description is not asserted to be quantum truth. The required attribution `hybrid − Qfull = (MACE − Qcap) + (Qcap + retained MM − Qfull)` therefore remains unmeasured. Both the observed force failures and missing references independently prevent G07-T4/M03 physical closure.

No threshold, geometry, cut, force-field parameter, model or accepted G05 reference was changed in response to these results. No new reference DFT/Psi4 calculation was launched. AM1-BCC preparation for the frozen MM charges used AmberTools before model scoring.

Reproduce the evidence calculation after activating the main environment: `python Worker_Log/Milestone_03/evidence/G07_v1/analyze_region_sensitivity.py`. It verifies every source/numerical hash and rejects missing/nonfinite input; it creates `region-sensitivity.json` exclusively, so use a separate copied evidence directory when reproducing. [All 40 comparisons and hashes](region-sensitivity.json), [numerical single points](fifty-description-single-points/summary.json), and [analysis source](analyze_region_sensitivity.py) are preserved.

Next: independently review this finding and the frozen design using GPT-6.1-sol/MAX before deciding whether to investigate a scientifically justified narrower profile or authorize further reference work. The earlier feasibility-pilot proposal is conditional on this review; no compute budget or new physical choice is inferred from the software passes.
