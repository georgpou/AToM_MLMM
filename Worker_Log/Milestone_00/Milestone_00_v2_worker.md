# M00 physical-reference proposal — v2 worker

**Scope:** previously open G05-T4/G07-T4 reference design only.\
**Outcome:** exact proposal ready for independent design review; user agreement pending.\
**Snapshot:** child `m03-reference-g05`, base `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`; the commit containing this report freezes the submitted plan/input bytes. No target model-versus-quantum comparisons have been performed or inspected.

## Changes

The [exact proposal](../../docs/project-0/reference/M00-neutral-reference-plan-v2.md),
[input manifest](../../fixtures/chemical_reference/input-manifest.json) and
[settings/limits](../../fixtures/chemical_reference/reference-settings.json)
declare 34 neutral singlet CHNO structures: four capped ethanol, four capped
butane, three methanol, three acetamide, and four contact families of five rows.
Each contact embeds exact neutral peptide-parent coordinates, baseline/uncut
choices and the admitted alternative isoleucine ethane cut. All 20 G07 contact
rows are planned now; their calculations and prepared-MM artifact freeze remain
G07 work. Proposed MM definition is GAFF 2.2.20/AM1-BCC on complete neutral
parent/ligand, using the inherited boundary ledger.

Preparation used deterministic ETKDGv3 seed 61705, converged MMFF94s and
prescribed torsions/rigid placements, with no learned-model or quantum scores.
The cap is fixed-length 1.09 angstrom for these new chemical fixtures; inherited
G04 cap parameters and definitions are unchanged. File hashes, atom order,
explicit hydrogens, charges/spin and transformations are frozen.

## Verification

Separate Psi4 1.10.2 / LibXC 7.0.0 reference prefix, 105-package SHA-256 lock;
main and Amber locks remain unchanged. Offline quantum-only methane pilot
completed in 56.72 s with finite energy and analytic gradient, D3(BJ) energy
present and VV10 zero. Finite-difference force errors were 0.0103/0.0911
kJ/mol/nm at 0.001/0.0001 angstrom. This confirms actual reference access,
not target chemical adequacy. Preserve the initial pre-calculation LibXC 7.1.2
import failure and compatible build evidence under
[M00_reference_v2](evidence/M00_reference_v2/working-libxc-7.0.0/methane-pilot.json.gz).

Commands: `python tools/prepare_neutral_references.py` (locked core, exit 0,
34 files); separate reference Python running
`Worker_Log/Milestone_00/evidence/M00_reference_v2/quantum_feasibility.py`
(first prefix exit 1 at import, compatible prefix exit 0). The complete logs,+explicit locks, installed package records and basis digests are preserved.

## Handoff

The user was asked to agree to the exact proposal, including profile limits
and a 12-hour / 2-thread / 5 GiB cap. No answer has yet been recorded. An actual
fresh-context gpt-6-astra/high reviewer must review this exact snapshot and
author no implementation. Both agreement and design acceptance precede target
comparison results. G05 software work may continue independently. Design
approval alone does not qualify chemistry, G05, G07 or M03.
