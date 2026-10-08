# M00 small neutral reference plan — exact proposal v2

**State:** exact proposed inputs are frozen; explicit agreement on the chemical
limits and independent design review are pending. No
G05-T4/G07-T4 model-versus-quantum comparison has been performed or inspected.
This extends the accepted analytic M00 design only in its previously open
physical-reference scope. The exact frozen version needs a fresh-context
gpt-6-astra/high review before chemical comparisons.

## Purpose and recommended starting set

Test whether the bundled MACE-OFF23-small checkpoint describes the exact capped
chemistry and small contacts used by the first mechanical profile. Software
agreement and chemical adequacy have separate acceptance decisions. The first
set deliberately covers only neutral closed-shell C/H/N/O molecules, ordinary
protein C–C cuts, alcohols, saturated hydrocarbons and a primary amide.

| Role | Exact chemical connectivity | What the test probes |
|---|---|---|
| Threonine side chain, cut C-alpha–C-beta and H capped | Ethanol, `CCO`, C2H6O | Alcohol torsions, a polar group near the cap, hydrogen bonds |
| Isoleucine side chain, cut C-alpha–C-beta and H capped | n-Butane, `CCCC`, C4H10 | Anti/gauche torsions and hydrocarbon packing |
| Complete ligand A | Methanol, `CO`, CH4O | Small alcohol donor/acceptor contacts |
| Complete ligand B | Acetamide, `CC(N)=O`, C2H5NO | Carbonyl acceptor, amide planarity and a ligand larger than A |

All four molecules have formal charge 0, closed-shell singlet multiplicity 1,
ordinary valence, explicit hydrogens, and no protonation ambiguity. Inherited MM
partial charges are neither formal charges nor evidence of fragment neutrality.
These small ligands are reference probes, not a claim that a drug or protein
binding calculation is qualified.

## Structures to freeze before comparison

The proposed G05 batch contains **34 energy-and-gradient structures**:

- Four ethanol capped conformers, with C-gamma–C-beta–O–H torsions 180, +60,
  -60 and 120 degrees.
- Four butane capped conformers, with C-gamma2–C-beta–C-gamma1–C-delta1 torsions
  180, +60, -60 and 120 degrees.
- Three complete methanol configurations: the declared baseline, a 60-degree
  hydroxyl rotation, and a 0.03 angstrom C–O stretch from that baseline.
- Three complete acetamide configurations: the declared planar baseline and
  rotations of the NH2 group by +20 and -20 degrees about C–N.
- Five structures in each of four contact families: ethanol/methanol with the
  ethanol OH donating, ethanol/acetamide with OH donating to the carbonyl,
  butane/methanol with carbon faces presented, and butane/acetamide with methyl
  faces presented. Each family has three distances, one off-axis orientation,
  and one separated control. The polar heavy-atom distances are 2.6, 3.0 and
  3.5 angstrom; carbon-face distances are 3.4, 3.8 and 4.5 angstrom. The off-axis
  case rotates the ligand 60 degrees about its contact anchor at the middle
  distance. The separated case uses a 15 angstrom minimum intercomponent
  distance, checked against every actual model edge.

Coordinates are prepared without evaluating MACE: deterministic conformer
construction, a recorded classical geometry preparation, then the prescribed
torsions/distortions and rigid contact placements. Contact monomers retain
their exact intramolecular coordinates. The cap uses the accepted fixed-length
geometry rule, with its distance, parent identities and construction recorded
in the exact fixture. A terminal cap cannot acquire independent classical
charge, Lennard-Jones parameters, mass or dynamics.

The [input manifest](../../../fixtures/chemical_reference/input-manifest.json)
now includes 34 full-precision JSON structures and hashes, with explicit atom
and bond lists, named dihedral/anchor indices, protein parent coordinates,
cap maps, file units and SHA-256 hashes. Angstrom quantum coordinates and nm
project coordinates must describe the same structures. The counts above are
design choices. Preparation uses
[the score-free script](../../../tools/prepare_neutral_references.py) in the
locked RDKit 2026.3.6 environment: ETKDGv3 seed 61705, one thread, converged
MMFF94s optimization (maximum 2000 iterations). Each JSON embeds the complete
parent coordinates and retained source atom identities. New chemical fixtures
use a 1.09 angstrom C–H cap; this is a new declared input parameter, not a change
to the inherited G04 1.17 angstrom fixture or cap formula. Separate contact
anchors use 15 angstrom plus each monomer's maximum anchor radius, guaranteeing
at least 15 angstrom actual separation. No structure will be selected or omitted based on a
model score.

## Independent quantum reference and feasibility

Recommend **restricted omega-B97M-D3(BJ)/def2-TZVPPD** single-point energies and
Cartesian gradients, matching the published SPICE reference level used for
MACE-OFF23. Psi4 supports this named functional with D3(BJ) replacing VV10, not
both dispersions. Verify the checkpoint-specific training provenance in the
frozen submission. This tests agreement with a defensible training-level
electronic-structure reference; it does not turn DFT into experimental truth.

Fixed proposed settings: Psi4 1.10.2 / LibXC 7.0.0, C1 symmetry, no reorientation or center-of-mass
translation, restricted singlet, density-fitted SCF, `def2-universal-jkfit`
auxiliary basis, energy and density convergence 1e-10, maximum 200 SCF iterations,
integral screening 1e-12, and 99 radial / 590 spherical grid points. Freeze the
resolved software/builds, dispersion engine, basis files and hashes in the
[105-package SHA-256 lock](../../../fixtures/chemical_reference/reference-explicit.lock)
and [exact settings/limits](../../../fixtures/chemical_reference/reference-settings.json).
Use `wcombine=false` as in SPICE's published sample. The dispersion engine is
simple-dftd3/dftd3-python 1.6.0; D3(BJ) two-body parameters are s6=1,
s8=0.3908, a1=0.5660, a2=3.1280. Store total
electronic plus D3 energy and the corresponding analytic gradient. Convert
forces as minus the gradient using documented Hartree/bohr constants.

A quantum-only methane feasibility calculation completed offline in 56.72 s,
with finite analytic gradients, explicit D3 energy and zero VV10 energy. Its
two finite-difference probes differ by 0.0103 and 0.0911 kJ/mol/nm, far below
the proposed chemical force budget. It is not a G05/G07 chemical comparison.
The first environment failed before calculation because LibXC 7.1.2 removed a
functional expected by Psi4's registry; both environments and failed evidence
are preserved. Only the compatible 7.0.0 build is proposed. See
[quantum-only evidence](https://github.com/georgpou/AToM_MLMM/blob/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log/Milestone_00/evidence/M00_reference_v2/working-libxc-7.0.0/methane-pilot.json.gz).
Convergence confirmation on acetamide-0 and ethanol-acetamide-d3-r0 uses
199 radial / 974 spherical points, energy convergence 1e-12 and density
convergence 1e-11. Require absolute energy repeatability within 0.02 kcal/mol,
force-component RMS within 0.002 eV/angstrom and maximum atom-vector difference
within 0.005 eV/angstrom. Failed convergence remains a failed/missing
reference; no alternate method is substituted silently.

On this machine there are 3 CPUs and approximately 10 GB RAM. The initial budget
option presented to the user is at most **12 wall-hours, 2 CPU threads and 6 GB
RAM**, using a separate reference prefix. Single points avoid expensive quantum
geometry optimization. The practical estimate is several hours for the small
34-structure batch, subject to a measured feasibility run; this is an estimate,
not a timing claim. No paid quantum service is proposed. Pause for a concrete
budget decision if the batch exceeds the agreed cap. Keep both locked main and
Amber environments unchanged.

Existing frozen quantum data would avoid computation only if the exact desired
coordinates, atom order, method, gradients and complete provenance match. No
such matching data have yet been identified, so fresh calculations are the
recommended route.

## Energy zero and metrics

Use the model's `energy` output, including its atomic reference energies.
`interaction_energy` is not a ligand–protein pair-energy decomposition.
Never compare absolute energies of ethanol, butane or differently capped
partitions to one another.

For each fixed-composition conformer family, define relative energies against
its predeclared baseline structure. For a frozen contact geometry define
interaction energy as E(fragment+ligand) minus E(fragment) minus E(ligand), all
at exactly those monomer coordinates, with the same method/output convention.
Also compare each joint contact against its declared separated structure of
identical composition. Use uncorrected finite-basis quantum interaction energies
as the primary convention, consistent with the reference level's total-energy
training target; record this convention explicitly rather than silently mixing
counterpoise-corrected and uncorrected numbers.

Compute RMS and maximum absolute relative-energy errors by family and across
the entire set. For forces report Cartesian component RMS, maximum atom-vector
error, every cap force, independently projected forces on both real parents,
and net ligand interaction-force errors. Equal sample weighting and equal
Cartesian-component weighting are fixed; no per-atom normalization of energy
and no protein-total-energy scaling can hide a discrepancy.

**Proposed profile limits, subject to user agreement and independent review:**

| Chemical check | RMS error | Maximum error |
|---|---:|---:|
| Relative conformer/configuration energy, each family | 1.0 kcal/mol (4.184 kJ/mol) | 2.0 kcal/mol (8.368 kJ/mol) |
| Interaction and contact-minus-separated energy, each family | 0.5 kcal/mol (2.092 kJ/mol) | 1.0 kcal/mol (4.184 kJ/mol) |
| Raw Cartesian forces, each structure | 0.05 eV/angstrom | 0.15 eV/angstrom maximum atom-vector error |
| Net ligand interaction force, each contact | — | 0.05 eV/angstrom vector error |

The relative-energy limits admit only a small chemical adequacy demonstration,
not quantitative binding-affinity prediction. The tighter contact budget prevents
large errors in the interaction scale being hidden by much larger internal
energies. The force budget probes whether local slopes remain useful near the
frozen conformers and cap; a separate maximum catches a localized boundary
defect that RMS would conceal. Report weak-contact signs and forces even when
their energy magnitude is below the energy budget. Require the model to preserve
the sign of a quantum attraction of at least 1 kcal/mol and the direction of
the repulsive approach response at the compressed declared samples.

These are proposal-specific chemical limits, not universal accuracy thresholds
and not sampling uncertainty targets. S06 numerical adapter/finite-difference
tolerances remain unchanged and are checked separately.

## G07 boundary controls planned now, evaluated later

Prepare neutral N-acetyl-L-threonine-N-methylamide and
N-acetyl-L-isoleucine-N-methylamide parent structures, with explicitly fixed
stereochemistry, atoms, hydrogen connectivity, coordinates and hashes. Their
amide terminal groups avoid charged peptide termini. The baseline partition
is the C-alpha–C-beta cut producing the G05 ethanol/butane model inputs. Include
the all-ML uncut parent and an alternative admitted isoleucine
C-beta–C-gamma1 cut producing capped ethane. Do not cut peptide bonds, rings,
ligands or disulfides. The complete ligand and fixed real identities remain
present for every contacting and separated comparison.

For each choice construct a quantum capped surrogate Qcap plus the **actual**
retained-MM ledger, and an uncut full-parent quantum reference Qfull. Compare
within-description relative energies, contact-minus-separated energies and
full-real-coordinate forces. Different model atom counts require independent
within-description zeros, never an absolute cross-composition subtraction.

Use the accounting identity, separately for each geometry difference:

`hybrid - Qfull = (MACE - Qcap) + (Qcap + retained MM - Qfull)`.

The first term measures model error on identical capped inputs. Split the
second term into the explicit retained-MM change and the capped-versus-uncut
quantum change; together they measure the declared partition approximation.
Project cap derivatives using an independent Jacobian oracle and retain the
full MM forces. Do not subtract a second capped-MM energy, assume Hamiltonian
equality, or interpret a diagnostic energy difference as a binding correction.

The proposed G07 contact/region sensitivity budget is 1.0 kcal/mol maximum
contact-minus-separated energy deviation and 0.05 eV/angstrom maximum net ligand
force deviation between admitted descriptions. Full-real force RMS and maximum
are reported against the same force limits above. This budget limits the small
boundary approximation for these fixtures only. The precise G07 fixture matrix
and hashes must be part of the frozen plan, even though its comparisons remain
future G07-T4 work.

## Review, failures and applicability

User selection → exact fixture/method/metric freeze → independent Astra/high
design audit → quantum references and model comparisons → independent G05
implementation/qualification audit. Design approval is not a chemical pass.
Keep all failures, nonfinite outputs, convergence failures and attempted
samples. Missing reference data block G05-T4 and full physical acceptance.
Exceeded limits block the proposed profile; a narrower scope or physical change
requires a justified new review. Never tune a threshold, choose a new molecule,
replace a checkpoint, add residual repulsion or discard a sample to gain a pass.

An accepted G05 profile would cover these small nonperiodic neutral capped
systems on CPU with this exact checkpoint and mechanical Hamiltonian. Periodic
systems, protein ABFE/RBFE, GPU, electrostatic embedding, full workflows and
broader drug chemistry remain with their owning gates. Stop at G05 acceptance;
hand G06/G07 to the next assignment.
