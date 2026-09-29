# S04: How ML, MM, and link atoms form one energy model

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../README.md) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

This page states what the first mechanical embedding computes, where its forces must go, and what must remain flexible for a later electrostatic embedding. The equations give independent expected results for the small tests.

**When to read it:** Read the boundary section for G04, the model section for G05, and the periodic section for G06. The gate pages point to exact sections.

The detailed names and equations below are kept precise because they define the behavior the tests must check. Unfamiliar terms are explained in [the glossary](../reference/glossary.md).

## The physical contract is broader than the first embedding

The embedding builder owns the complete physical Hamiltonian, including which classical contributions remain, which the model replaces, and any additional coupling. The transfer layer sees an energy and its real-coordinate derivatives. It must not assume that the model consults only ML coordinates or that environment forces are purely classical. A PythonForce selected-particle optimization must include every coordinate needed for its energy and returned derivatives, or use another explicitly validated force decomposition. Reusing a local-model ML-only subset for an environment-dependent provider is not an admissible optimization.

For the initial mechanical implementation, the operational definition is

$$U_{\mathrm{hyb}}(\mathbf R;\mathbf B)=U_{\mathrm{keep,MM}}(\mathbf R;\mathbf B)+E_\theta(\mathbf R_M,\mathbf h(\mathbf R);\mathbf B).$$

Here $\mathbf R$ is all real coordinates, $\mathbf B$ the box, $M$ the fixed ML set, $\mathbf h$ the derived cap coordinates, and $\theta$ the frozen model parameters. `keep,MM` means the actual retained classical force objects after construction, not an assumed separately parameterized capped molecule.

Save original MM, retained-MM, and hybrid descriptions. Define the removed classical contribution by the evaluated identity

$$D_{\mathrm{MM}}=U_{\mathrm{full,MM}}-U_{\mathrm{keep,MM}}.$$

Then $U_{\mathrm{hyb}}=U_{\mathrm{full,MM}}-D_{\mathrm{MM}}+E_\theta$. Do not subtract another capped-MM energy without deliberately changing the Hamiltonian. For a future electrostatic embedding, the retained and model/coupling terms may differ; the common builder must not hard-code this mechanical subtraction into ATM or analysis.

## Mechanical baseline and boundary policy

Keep classical real ML-MM electrostatics and Lennard-Jones interactions. Do not zero all real ML charges. Caps have no independent mass or unintended classical charge/Lennard-Jones interaction. Remove or retain bonded, exception, and constraint terms according to an explicit term ledger. Do not approximate the boundary rule by 'remove everything entirely in ML' when the actual boundary predicates also consider central atoms and connectivity.

Start with a single ordinary carbon-carbon cut; move to neutral side chains cut near C-alpha/C-beta when chemically appropriate. Include hydrogens using connectivity, not a brittle atom-name exclusion list. Initially reject rings, peptide cuts, charged or ambiguous fragments, disulfides, ligand cuts, and multiple caps on one MM parent. Record every cap distance actually constructed. A neutral formal fragment is not the same thing as a subset of inherited MM partial charges summing to zero.

For an ML parent $a$ and MM parent $b$, use the admitted cap rule

$$\mathbf r_h=\mathbf r_a+d_h\mathbf n,\quad \mathbf n=(\mathbf r_b-\mathbf r_a)/r,\quad r=|\mathbf r_b-\mathbf r_a|.$$

Here $d_h$ is the fixed cap bond length. Set

$$A=(d_h/r)(I-\mathbf n\mathbf n^{\mathsf T}).$$

A raw cap force $\mathbf F_h$ adds $(I-A)^{\mathsf T}\mathbf F_h$ to parent $a$ and $A^{\mathsf T}\mathbf F_h$ to parent $b$. These sum to the cap force and are generally not a fixed fractional split. Production uses the validated virtual-site machinery; the analytic formula is an independent expected answer, not a second force-redistribution layer.

For each perturbation in a force check, reconstruct virtual sites using the production convention. Do not project perturbed coordinates onto constraints unless intentionally checking a constrained derivative. A cap particle's raw force slot is not the final real-parent derivative. Repeat the parent derivative checks inside ATM; the revised plan flagged nested virtual-site handling as a question requiring direct evidence, not an established defect.

## Periodic and long-range accounting

The candidate initial configuration has one standard PME NonbondedForce, ordinary cutoff Lennard-Jones interactions, no charge offsets, no LJPME, and an orthorhombic box. Record cutoff, switching, PME tolerance/realized parameters, and dispersion-correction policy. The simplest ledger fixture disables analytical dispersion correction. A production change to that choice needs its own audit.

The revised source audit states that the local-model mechanical path retains a periodic-image electrostatic contribution. Therefore do not equate the removed contribution with all ML-subset PME energy or all cavity-ligand classical interaction. Inspect exceptions and retained terms numerically. The inherited source locations are in [the source register](../reference/sources.md).

For a charge-mask diagnostic, let $Q(S)$ be the PME energy with only atom set $S$ charged, using identical box/mesh/settings and consistently changed exceptions. The cross contribution is

$$Q(C\cup L)-Q(C)-Q(L)+Q(\varnothing).$$

Do not omit a neutralizing-background convention for nonneutral subsets or let independent mesh selection contaminate the difference. Lennard-Jones masks require their own consistent mixing and switching implementation. This is a diagnostic decomposition, not an automatically applicable binding correction.

Check a cut near a box face, whole-molecule wrapping, periodic reconnection of cavity/ligands/caps, and energy/force continuity across admitted image-choice boundaries. A model cutoff test does not prove smoothness of a complete periodic convention. A bulk site must clear the entire protein, not just its ML subset. Check allowed trajectory excursions, not only the initial structure. The proposed 0.2 nm beyond-cutoff guard is an initial engineering margin, not universal physics.

## Locality is a capability, not a core axiom

For an additive local model with no cross-component edges or additional global coupling, the disconnected ML contribution should equal the sum of compatible component contributions. Test the same cap/box/energy convention. This statement does not apply to the total hybrid energy, nor automatically to long-range or charge-equilibrating models.

Model input still contains the same joint ML set when it is bound or separated. Do not batch cavity and ligand as separate graphs at the bound endpoint. The actual model graph and an independent periodic distance check should both be inspected. A message-passing neighbor cutoff is not necessarily the total receptive distance through several layers; putting a cap one cutoff from a contact is not a sufficiency proof.

## Early environment-dependent contract probe

G02 introduces an analytic substitute, not electrostatic physics:

$$E_{\mathrm{env}}=\tfrac12\kappa|\mathbf r_m-\mathbf r_e|^2,$$

where $m$ is a selected model atom, $e$ is a real MM environment atom, and $\kappa$ has units kJ/mol/nm squared. Its forces are $\mathbf F_m=-\kappa(\mathbf r_m-\mathbf r_e)$ and $\mathbf F_e=-\mathbf F_m$.

Moving only $e$ must change the result. Translating $m$ under ATM must recompute the difference and change the force on $e$, even though the transform does not translate $e$. Returning only ML forces or using the original environment descriptor for both maps must fail. An A-B-A sequence of evaluations must reproduce the first A result, exposing stale state. G04/G07 repeat the probe with $m$ replaced by a derived cap to test both environment and link-parent derivatives.

## What a real electrostatic extension will additionally need

A later design must specify the electrostatic Hamiltonian, MM field/potential representation, near-boundary charge treatment, periodic long-range and self/background terms, double counting, charge/spin inputs, and force response on all influencing coordinates. If a field is constructed from coordinates, its derivative must be included; a detached array of field values is not sufficient merely because the model can consume it.

Environment descriptors must be reconstructed after each coordinate map. Any self-consistent polarization solve must be deterministic to its admitted convergence tolerance and independent of evaluation order; a warm start may speed convergence but cannot select a different energy. Its residual/convergence diagnostics belong in evidence. Static caches may hold immutable species or topology; geometry-dependent caches require a proven key/update policy covering coordinates, box, and relevant state.

Current NVT interfaces do not establish cell/virial correctness for NPT. That is a separate extension. No actual electrostatic backend is included or qualified here. The promise is that these additional requirements can be implemented inside the embedding/model boundary while reusing the same physical, transfer, recording, and analysis contracts.
