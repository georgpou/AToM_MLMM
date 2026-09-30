# S01: What belongs in Project 0, and what does not

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../../../README.md#roadmap) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

This page sets the limits of the first working platform. It separates correct code, a correct free-energy calculation, and useful chemical accuracy. Those are three different questions.

**When to read it:** Use it when a task changes the allowed chemistry or claims that a result is complete.

## The question Project 0 answers

Can one well-defined, cavity-inclusive ML/MM Hamiltonian with protein link sites be evaluated, differentiated, serialized, and sampled correctly under ATM, for both one-ligand ABFE and dual-ligand RBFE? This retains the original plan's separation of the energy engine from the transfer engine. It is not an experiment showing that ML improves binding affinity predictions.

The first scientific implementation is deliberately narrow: a local model, mechanical embedding, fixed ML membership, complete neutral ligands, neutral uncomplicated capped protein fragments, explicit solvent, a documented periodic convention, fixed-temperature NVT production, and fixed whole-ligand translations. Initial timestep is 0.5 fs. Longer timesteps and multiple-time-step integration are separate qualification changes.

The common interfaces must nevertheless admit multiple mobile molecules and physical energies depending on the MM environment. This is an architectural requirement now, not a promise to implement electrostatic embedding now. Such a future embedding will require its own scientific specification, model, force and periodic treatment, and numerical qualification.

## Distinctions that must remain visible

Implementation correctness means the program returns the energy and derivatives of its declared Hamiltonian. Thermodynamic correctness means its states, restraints, sampling, estimator, and corrections measure the declared quantity. Physical adequacy means the declared approximation is useful for the selected chemistry. A pass in one category does not establish the others.

A **gate** is one piece of work with tests and saved results, with dependencies and a pass/fail decision. A **milestone** groups gates into a useful capability and requires a review of their combined meaning. A **specification** fixes behavior that other code or users rely on. A **plan** fixes the sequence of work. A **decision record** explains a reviewed change. A **qualification profile** identifies the complete software/model/embedding/protocol/hardware combination to which evidence applies.

## Permanent invariants

Real-atom identity and ML membership are fixed for an individual calculation. The complete transferred ligand is ML. Initial covalent cuts occur only in the protein, so the ATM transformation leaves both boundary parents and their cap unchanged explicitly. Those atoms still move during ordinary dynamics.

The same physical Hamiltonian is evaluated at both coordinate maps. Model selection, charges, cap geometry, cutoffs, and classical exclusions cannot change because a ligand appears bound or bulk. A cap is a derived coordinate, not a new independent thermal degree of freedom. All energy-dependent real coordinates receive forces. All physical contributions have one owner.

An unavailable or unsupported capability is an error, not an invitation to fall back silently. No NaN replacement, force clipping without a consistent energy, or removal of inconvenient samples is permitted as a stability repair. No result is called a standard binding free energy while a required correction is unresolved.

## Deferred scope

Actual electrostatic or polarizable embedding; metals; proton transfers; oxidation/spin changes; reactive or covalent chemistry; adaptive ML membership; cuts through ligands; general charged transformations; general long-range correction schemes; LJPME; general triclinic support; HMR; multiple-time-step dynamics; and multigpu qualification remain deferred unless a separately reviewed extension admits them. HMR means hydrogen-mass repartitioning, which changes masses to permit different integration settings.

The architecture reserves extension boundaries, not unsupported physics defaults. No production class should be created just to raise `NotImplementedError` for each imagined future model. Unsupported feature requests should be rejected through a small explicit capability check.

## Scope-changing decisions

Changing the Hamiltonian, supported chemical states, mass/constraint ensemble, periodic convention, or thermodynamic cycle requires a specification amendment. Changing an internal loop without changing those contracts does not. Promoting a proposed model to qualified support requires evidence for its full profile, not merely successful import.

M00 reviews these boundaries. G01 and G02 implement cheap structural and analytic guards. G07 checks that the real mechanical implementation respects them. G11 and G12 qualify molecular ABFE and RBFE. The original source and revised-plan distribution are recorded in [the coverage map](../../../README.md#history).
