# M00 corrected physical-reference proposal — v3 worker

**Scope:** M00-v2-R1 geometry repair and explicit rotational quadrature controls.\
**Outcome:** exact corrected proposal ready for fresh Astra/high design review;
user agreement on scientific choices remains pending.\
**Snapshot:** child `m03-reference-g05`; predecessor exact plan
`321d7e3764a46eb5359a8d96bcab9124dccbc5f5`, with actual v2 independent
`changes_required` decision preserved. The commit containing this report freezes
v3. No G05-T4/G07-T4 target comparison results were generated or inspected.

## Changes and evidence

The [v2 audit](Milestone_00_v2_audit.md) independently reproduced unintended
G07 retained-parent O–H 0.998831 and O–C 1.729074 angstrom overlaps.
The worker independently confirmed the same geometry from frozen coordinates.
The [score-free repair](../../tools/repair_neutral_reference_controls.py) tries
twelve retained-peptide rotations around the fixed threonine C-alpha–C-beta
axis, with Bondi-radius steric criteria over all ten future threonine rows.
It selects 120 degrees: worst retained-parent/ligand ratio 1.03557, internal
nonbonded ratio 0.69886. Connectivity, all source identities and cap parent
positions remain fixed. Every raw G05 coordinate, composition and scientific
limit is exactly unchanged from v2. Isoleucine is unchanged. All attempts and
new hashes are in the [v3 manifest](../../fixtures/chemical_reference_v3/input-manifest.json).

The [v3 plan](../../docs/project-0/reference/M00-neutral-reference-plan-v3.md)
also freezes ten distinct monomer orientation controls with the already
declared convergence budget (energy 0.02 kcal/mol, force RMS 0.002 and max atom
vector 0.005 eV/angstrom). These must pass before baseline quantum monomers are
reused under rigid rotations. Main 34 targets, 10 rotation controls and 2
denser-grid confirmations remain inside the proposed resource cap. The exact
training-match claim is qualified by the cited release/training-data DOI and
archived SPICE level/sample; no exact replication of training numerics or
out-of-training-set guarantee is claimed.

`python tools/repair_neutral_reference_controls.py`: locked core environment,
exit 0, 34 unchanged raw G05 geometries, 20 G07 rows / 50 descriptions, ten
orientation-control files. No model or quantum imports/evaluations in repair.
V2 plan, fixtures, audit and all failed evidence remain preserved.

## Handoff

Actual fresh-context gpt-6-astra/high [v3 audit](Milestone_00_v3_audit.md)
accepts the exact `a825f5f1c2d8cf4146133c2049ef1c4eca550e93` proposal for
scope, conditional on explicit user agreement. Independent results are
965 applicable structural/geometry checks and 131 package/basis/provenance
checks. M00-v2-R1 is closed; no blocking design finding remains. The
[decision record](evidence/M00_v3_decision/decision-pending.json) honestly
records user_agreed=false. Obtain that agreement before target calculations
or comparisons. G00/G05 software work can advance.
G07 exact prepared GAFF/AM1-BCC XML/charges/ledger freeze is later, as explicitly
required by the reviewed future matrix. No reference-design approval accepts
G05 chemistry, G07, protein ABFE/RBFE or M03.
