# Project 0: Establishing a Correct and Reusable ATM–ML/MM Framework with Link Atoms

**Working technical note for internal discussion and review**  
**Status:** Brainstorming / design phase  
**Software landscape checked:** 29 September 2026

---

## 1. Purpose of this document

The long-term objective is to use machine-learning potentials (MLIPs) inside alchemical binding free-energy calculations, eventually for difficult systems such as metal-binding ligands and covalent binders. Before attempting those chemically difficult problems, however, we need to establish that the basic computational machinery is correct.

This document therefore focuses almost entirely on **Project 0**.

Project 0 is not intended to answer whether a machine-learning potential gives better binding free energies than a classical force field. Instead, Project 0 asks a more fundamental question:

> **Can we construct a mechanically embedded ML/MM Hamiltonian that contains part of the protein and the ligand, includes link atoms at covalent ML/MM boundaries, and can be evaluated correctly inside the Alchemical Transfer Method (ATM) for both absolute and relative binding free-energy calculations?**

If the answer is yes, this infrastructure can later be reused for increasingly difficult chemistry without redesigning the alchemical machinery every time.

Project 1 will then be the first scientific stress test: ordinary noncovalent protein–ligand systems with no metals, no covalent bond formation, no protonation changes, and no unusual electronic states. Project 1 is described only briefly at the end of this note.

The guiding philosophy throughout Project 0 should be:

1. solve the smallest scientifically correct problem first;
2. avoid adding generality that is not yet required;
3. test every layer independently before combining them;
4. keep the ML/MM energy engine separate from the ATM alchemical engine;
5. convert every important assumption into an automated test wherever possible.

---

# 2. The core architectural decision

The most important design decision is that **ATM should not need to know anything about the internal details of the ML/MM calculation**.

ATM should receive a valid potential-energy function and evaluate it at two coordinate states. The hybrid ML/MM machinery should be responsible for defining that potential correctly.

Conceptually:

```text
Classical molecular system
        |
        v
Define the ML subset
        |
        v
Construct a valid mechanically embedded ML/MM Hamiltonian
        |
        v
Validate energies, forces, boundaries, periodicity and serialization
        |
        v
Pass this Hamiltonian to ATM
        |
        v
ABFE / RBFE calculations
```

We should therefore avoid an architecture in which we modify MACE, FeNNix, or another MLIP specifically for ATM, or in which ATM contains special cases such as “if the ligand is in the solvent, call the MLIP differently.”

The desired separation is:

\[
\boxed{\text{ML/MM energy engine} \quad \perp \quad \text{ATM alchemical engine}}
\]

Here the symbol \(\perp\) is being used informally to mean **architecturally independent**, not mathematically perpendicular.

The practical consequence is that the same ML/MM `System` should be usable for ordinary molecular dynamics, minimization, and ATM. ATM should simply evaluate that system at different coordinate mappings.

---

# 3. Scope of Project 0

Project 0 should deliberately be restricted to the easiest physically meaningful case.

## 3.1 Included

Project 0 should support:

- a **local or short-range MLIP**;
- **mechanical embedding** between the ML and MM regions;
- a ligand entirely contained in the ML region;
- selected protein atoms contained in the ML region;
- covalent cuts through the protein handled by **hydrogen link atoms**;
- explicit-solvent periodic simulations;
- ATM absolute binding free energy (ABFE);
- ATM relative binding free energy (RBFE);
- OpenMM-based execution;
- reproducible restart and replica-exchange workflows.

## 3.2 Explicitly excluded for now

Project 0 should **not** attempt to solve:

- electrostatic embedding of the ML region;
- polarizable embedding;
- transition metals;
- changing oxidation states;
- changing spin states;
- proton transfer;
- covalent bond formation or breaking;
- dynamically changing the identity of the ML region;
- ML/MM boundaries through the ligand;
- adaptive QM/MM-like partitioning;
- charged alchemical transformations as the first test case;
- general PME-aware corrections between disconnected ML fragments unless we first show they are required;
- timestep optimisation or multiple-time-step acceleration.

These are all potentially important later, but adding them now would make failures difficult to diagnose.

---

# 4. Definitions and notation

Because this project mixes alchemical, ML, and MM concepts, it is useful to define the symbols once and use them consistently.

## 4.1 Atom sets

We define three main atom sets.

### \(L\): ligand atoms

\(L\) denotes the complete ligand.

For Project 0, the ligand should be **fully inside the ML region**. There should be no link atom cutting through the ligand.

### \(C\): cavity or protein ML atoms

\(C\) denotes the selected protein atoms that are treated by the MLIP.

These could be, for example, several binding-site side chains whose local interactions with the ligand we want to describe with a higher-level potential.

The letter \(C\) is chosen here for “cavity.” It does not imply that the atoms have to form a literal hollow cavity.

### \(E\): environment atoms

\(E\) denotes everything that remains classical MM:

\[
E = \text{remaining protein} + \text{water} + \text{ions}.
\]

The symbol \(+\) here means “combined atom sets,” not an energy addition.

## 4.2 ML region

The complete ML region is

\[
M = C \cup L.
\]

Here:

- \(M\) means the complete set of ML atoms;
- \(\cup\) means **set union**, i.e. all atoms belonging to either \(C\) or \(L\).

The important point is that \(M\) is defined **once** when the system is built. We should not redefine it according to whether the ligand is currently in the binding site or in bulk solvent.

## 4.3 Coordinates

Let

\[
\mathbf R
\]

represent the complete set of Cartesian coordinates of all particles in the simulation.

A bold symbol such as \(\mathbf R\) indicates a vector or collection of vectors rather than a single scalar number.

## 4.4 Energies

We use:

- \(U\) for a total potential energy;
- \(U_{\mathrm{MM}}\) for energy from the classical molecular-mechanics force field;
- \(E_{\mathrm{ML}}\) for energy returned by the machine-learning potential.

The distinction between \(U\) and \(E\) is only for readability here; both are energies.

---

# 5. What mechanical embedding means in this project

The simplest conceptual hybrid Hamiltonian is

\[
U_{\mathrm{hybrid}}(\mathbf R)
=
E_{\mathrm{ML}}(M)
+
U_{\mathrm{MM}}(E)
+
U_{\mathrm{MM}}(M,E)
+
U_{\mathrm{boundary}}.
\]

Every symbol should be interpreted as follows.

### \(U_{\mathrm{hybrid}}(\mathbf R)\)

This is the total potential energy of the complete hybrid ML/MM system for coordinates \(\mathbf R\).

### \(E_{\mathrm{ML}}(M)\)

This is the ML energy of atoms belonging to the ML region \(M\).

For Project 0:

\[
M=C\cup L.
\]

Thus the MLIP can describe interactions between the ligand and selected protein atoms when they are spatially close.

### \(U_{\mathrm{MM}}(E)\)

This is the ordinary classical force-field energy of the environment, including the remainder of the protein, solvent, and ions.

### \(U_{\mathrm{MM}}(M,E)\)

This is the classical interaction between atoms in the ML region and atoms in the MM region.

Under **mechanical embedding**, these cross-region interactions remain classical. The ML electronic structure is not explicitly polarised by the MM environment.

### \(U_{\mathrm{boundary}}\)

This symbol represents the bookkeeping required where covalent protein bonds cross the ML/MM boundary. It includes the effect of link atoms and whichever MM bonded terms must remain or be removed to avoid double counting.

It should not be interpreted as a new physical force field term that we invent independently.

OpenMM-ML 1.8 already provides a mechanical-embedding implementation and link-atom support for molecules that span the ML/MM boundary. Its documentation states that ML–MM interactions are computed with the MM force field under mechanical embedding, while link atoms cap bonds crossing the boundary for the ML calculation. Link atoms are implemented as virtual sites. OpenMM-ML also removes selected bonded MM terms that would otherwise double-count interactions represented by the ML region [1,2].

---

# 6. Why ATM is attractive for this problem

ATM does not require the underlying potential energy to be decomposed into conventional alchemical Lennard-Jones and Coulomb terms.

Instead, ATM evaluates a physical energy function at two coordinate mappings.

We write these as

\[
u_0 = U(\mathbf R)
\]

and

\[
u_1 = U(T\mathbf R).
\]

The meanings are:

- \(u_0\): potential energy of one ATM coordinate state;
- \(u_1\): potential energy of the alternate ATM coordinate state;
- \(T\): a coordinate transformation;
- \(T\mathbf R\): the coordinates after applying that transformation.

For ligand binding, \(T\) typically translates selected ligand atoms between a binding-site location and a bulk-solvent location.

OpenMM's `ATMForce` is explicitly designed around this principle. It accepts force objects whose energies change under displacement and evaluates the energy before and after the requested particle transformations. The documentation describes the two energy quantities as \(u_0\) and \(u_1\), and the alchemical potential can be defined as an algebraic function of them [3].

This feature is why ATM is unusually compatible with many-body ML potentials.

We do **not** need to ask an MLIP to provide a separately identifiable term such as

\[
U_{\mathrm{ligand-protein}}^{\mathrm{vdW}},
\]

where the superscript “vdW” means van der Waals interaction.

Instead, the full ML/MM Hamiltonian is evaluated twice.

---

# 7. The key conceptual idea: the ML region can become disconnected

One important concern is what happens when the ligand is displaced into bulk solvent while the cavity atoms remain in the protein.

The permanent ML atom set remains

\[
M=C\cup L.
\]

However, the geometry changes.

## 7.1 Bound state

When the ligand is in the binding site, the geometry is approximately

```text
[cavity ML atoms] <---- close contact ----> [ligand ML atoms]
```

The ML model therefore evaluates the ligand, the cavity fragment, and their local interactions jointly:

\[
E_{\mathrm{ML}}(C\cup L_{\mathrm{bound}}).
\]

The subscript “bound” indicates that the ligand coordinates place it inside the binding site.

## 7.2 Bulk-solvent state

After ATM translates the ligand to a distant solvent location:

```text
[cavity ML atoms]                  [ligand ML atoms]
       C                                  L
```

If the MLIP is local and there are no ML atoms bridging the two components, the ML graph becomes disconnected once every cavity–ligand pair is outside the model's local neighbour range.

For a strictly local energy model, this means

\[
E_{\mathrm{ML}}(C\cup L_{\mathrm{bulk}})
=
E_{\mathrm{ML}}(C)
+
E_{\mathrm{ML}}(L_{\mathrm{bulk}}).
\]

Here:

- \(L_{\mathrm{bulk}}\) means the same ligand atoms placed in the bulk-solvent location;
- the equality follows from the absence of ML interactions connecting the two disconnected components.

This is an important property because it means we should not need special code such as:

```python
if ligand_is_bound:
    evaluate_ml(cavity + ligand)
else:
    evaluate_ml(cavity)
    evaluate_ml(ligand)
```

Such state-dependent branching would be undesirable. The Hamiltonian would effectively change its definition according to a geometric condition.

The preferred behaviour is:

```text
Always evaluate the same ML atom set: C union L.
Let the ML neighbour graph determine whether C and L interact.
```

---

# 8. Do we need to fine-tune on cavity–ligand structures separated by 10 Å or more?

For a normal short-range MLIP, **not simply because ATM places the ligand far from the cavity**.

This point is important enough to state clearly.

Suppose the MLIP energy has a local atomic decomposition of the general form

\[
E_{\mathrm{ML}}
=
\sum_i \varepsilon_i.
\]

Here:

- \(i\) indexes atoms;
- \(\varepsilon_i\) is the atomic energy contribution predicted for atom \(i\);
- \(\sum_i\) means that the atomic contributions are summed over all ML atoms.

Each \(\varepsilon_i\) depends only on the local ML environment accessible to the architecture.

If the cavity and ligand are spatially disconnected, with no ML neighbour edge connecting them, the architecture already enforces the lack of short-range interaction. The model does not have to learn from examples that “a ligand at 10 Å should stop interacting.”

In fact, supplying high-level quantum calculations of a cavity and ligand separated by a large distance can be conceptually awkward for a purely local model. The reference quantum calculation may contain small but finite long-range electrostatic and dispersion contributions. A strictly local MLIP cannot reproduce those contributions after the graph disconnects.

Therefore, for Project 0 and the later Project-1 fine-tuning experiment, a more useful training set would consist of:

1. **bound cavity + ligand configurations**, to teach local protein–ligand interactions;
2. **cavity fragment alone**, represented exactly as it appears in the production ML/MM calculation, including caps;
3. **ligand alone**, covering relevant conformations;
4. thermally distorted and slightly compressed/stretched local contact geometries;
5. configurations sampling the ML/MM boundary and link-atom environment.

Symbolically, the important categories are

\[
C+L, \qquad C, \qquad L.
\]

Here \(+\) is shorthand for “included together in the same reference calculation,” not literal addition of energies.

We should not initially spend expensive reference calculations on arbitrary structures of the form

\[
C \cdots L
\]

at 10, 15, or 20 Å merely to reproduce the ATM displacement.

This conclusion applies to **short-range local models**. It will need to be reconsidered for long-range, charge-aware, or polarizable models in later projects.

---

# 9. Current software components that make Project 0 realistic

As of 29 September 2026, the most useful existing components are the following.

## 9.1 OpenMM 8.5

OpenMM 8.5 introduced `PythonForce`, which allows energies and forces to be computed by Python code and returned to OpenMM. This is particularly useful for supporting a wider range of ML potentials [4].

`PythonForce` can also be restricted to only a subset of particles. This matters for ML/MM because it avoids passing an entire 50,000–100,000 atom system to a model when only perhaps tens to hundreds of atoms are ML [5].

There is an important implementation constraint: OpenMM serializes the `PythonForce` computation function with Python's `pickle` mechanism. If the function cannot be pickled, the `System` cannot be serialized normally [5]. This must therefore be included in Project-0 testing.

## 9.2 OpenMM-ML 1.8

OpenMM-ML 1.8 was released on 16 September 2026. The release specifically added:

- link-atom support for molecules spanning the ML/MM boundary;
- a new embedding architecture;
- continued mechanical embedding as the currently released general embedding method;
- additional ML model support [1].

The link-atom implementation inserts hydrogen link atoms as virtual sites and returns an `oldToNew` index mapping when `returnInfo=True` is requested. This is important because introducing link atoms changes particle indexing in the resulting OpenMM `System` and `Topology` [2].

## 9.3 AToM-OpenMM 8.5

AToM-OpenMM 8.5 is currently the latest release. It is tested with OpenMM 8.5, supports OpenMM versions newer than 8.4, uses the native OpenMM `ATMForce`, and has moved much of its setup workflow toward APIs rather than only script-level operation [6].

This is a strong reason to build Project 0 around OpenMM/OpenMM-ML/AToM rather than introducing another molecular-dynamics engine at this stage.

## 9.4 Existing ML/MM + ATM precedent

ATM has already been used with a neural-network/MM model in which ANI-2x described the ligand while the remainder of the system was classical MM. That work demonstrated that ATM and a ligand-level NNP/MM model can be combined in practical RBFE calculations [7].

However, the new problem here is more difficult. If only the ligand is ML, translating the complete ligand does not change its intramolecular geometry. By contrast, once protein cavity atoms are also included in the ML region, the ML energy itself contains protein–ligand interactions in the bound state and loses them when the ligand is transferred to bulk solvent.

Thus, previous ligand-only NNP/MM ATM work is an important control and precedent, but it does not already solve the cavity-inclusive problem.

---

# 10. Project 0 Problem A: can the ML force be evaluated correctly inside `ATMForce`?

This is the first and most important technical gate.

OpenMM documentation says that `ATMForce.addForce()` adds force objects whose energies are evaluated under the two ATM coordinate states [3]. OpenMM-ML increasingly represents ML models through `PythonForce` [1,4].

However, the fact that the APIs are individually compatible does not substitute for a direct numerical test of their composition.

## 10.1 Risk

Potential failure modes include:

- `PythonForce` not behaving correctly when nested under `ATMForce`;
- transformed coordinates not being passed to the ML model as expected;
- force propagation behaving differently between \(u_0\) and \(u_1\);
- periodic box information not being propagated correctly;
- unexpected performance overhead from evaluating the ML force twice.

## 10.2 Lowest-effort correct test

Do **not** start with a protein.

Construct a tiny system with a trivial Python-defined potential.

Evaluate the system directly at coordinates \(\mathbf R\):

\[
U_{\mathrm{direct},0}=U(\mathbf R).
\]

Then manually move the atoms by the same displacement that ATM will use and evaluate again:

\[
U_{\mathrm{direct},1}=U(T\mathbf R).
\]

Next construct `ATMForce` and retrieve its internal perturbation energies:

\[
u_0,\quad u_1.
\]

The required numerical result is

\[
u_0 \approx U_{\mathrm{direct},0}
\]

and

\[
u_1 \approx U_{\mathrm{direct},1}.
\]

The symbol \(\approx\) means numerically equal within an explicitly chosen floating-point tolerance.

## 10.3 Acceptance criterion

Project 0 should not proceed to protein link atoms until:

- \(u_0\) matches the independent undisplaced evaluation;
- \(u_1\) matches the manually displaced evaluation;
- force vectors agree as well as energies.

Call this **Gate 0A**.

If Gate 0A fails, we should fix or redesign the force integration before doing any chemistry.

---

# 11. Project 0 Problem B: system construction order and atom-index remapping

Link atoms change the number and ordering of particles in the OpenMM `System`.

OpenMM-ML 1.8 can return:

- the modified `System`;
- a modified `Topology` containing link virtual sites;
- an `oldToNew` mapping between original and modified atom indices [2].

This means construction order is not a minor implementation detail.

## 11.1 Correct order

The safest build sequence is:

```text
1. Build the complete classical system.
2. Define the real atoms belonging to the ML region.
3. Ask OpenMM-ML to create the mixed ML/MM system and link atoms.
4. Retrieve the modified topology and old-to-new index map.
5. Remap every atom selection used by ATM.
6. Only then construct the ATM coordinate transformations.
```

Symbolically:

\[
\text{MM System}
\rightarrow
\text{ML/MM System}
\rightarrow
\text{index remapping}
\rightarrow
\text{ATM System}.
\]

## 11.2 Why this matters

Suppose the original ligand occupies atom indices 450–480. If link virtual sites are inserted before some of those atoms, the final particle indices may no longer be 450–480.

An ATM input file that blindly keeps the original indices could then translate the wrong particles.

This type of bug can be especially dangerous because the simulation may still run.

## 11.3 Required diagnostic

For every prepared system, automatically write a machine-readable and human-readable atom map such as:

```text
Original atom ID | New OpenMM particle ID | Region | ATM displacement
```

Every real ligand atom should receive the expected ATM transformation.

Every stationary cavity atom should receive zero ATM displacement.

Every link virtual site should receive zero explicit ATM displacement unless a future design gives a specific reason otherwise.

This mapping should be saved with every production setup.

---

# 12. Project 0 Problem C: choosing the ML/MM boundary

Link atoms make protein ML/MM partitioning possible, but they do not make every boundary equally sensible.

The general boundary problem is:

```text
ML fragment ---- covalent bond ---- MM fragment
```

The ML calculation cannot simply terminate at an unsatisfied valence. A fictitious hydrogen is therefore introduced to cap the ML fragment.

## 12.1 Low-effort boundary strategy

For Project 0 and Project 1, the simplest robust strategy is to choose **complete side chains** and cut near the Cα–Cβ bond whenever chemically reasonable.

A schematic example is:

```text
MM backbone -- Cα | Cβ -- side chain -- ligand
                 ^
              ML/MM cut
```

The exact orientation of which carbon remains ML or MM must be chosen consistently with the OpenMM-ML link convention. The conceptual goal is simply to keep the cut away from the chemically important ligand-contact region.

## 12.2 Why side-chain cuts are attractive

They tend to:

- introduce only one boundary per selected residue;
- place the artificial hydrogen farther from the ligand;
- avoid cutting directly through aromatic groups or other interaction motifs;
- avoid cutting peptide bonds whenever possible;
- keep the backbone classical and therefore reduce ML atom count.

## 12.3 What we should avoid initially

Avoid ML/MM boundaries through:

- the ligand;
- aromatic rings;
- conjugated functional groups;
- peptide bonds unless absolutely necessary;
- atoms directly participating in the interaction under study.

A general boundary optimiser is not required for Project 0. We only need a defensible fixed convention suitable for ordinary protein pockets.

---

# 13. Project 0 Problem D: link atoms and force consistency

A link atom is not an ordinary dynamical atom. OpenMM-ML implements it as a virtual site maintained at a defined location along the bond crossing the ML/MM boundary [2].

That introduces several things we must verify rather than assume.

## 13.1 Required questions

1. Does the link coordinate update correctly when the real boundary atoms move?
2. Are forces on the link virtual site redistributed correctly to the real atoms?
3. Does the presence of the link atom create any discontinuity or instability?
4. Are the correct MM bonded terms removed to avoid double counting?
5. Does the behaviour remain correct when the hybrid force is evaluated as \(u_0\) and \(u_1\) inside ATM?

## 13.2 Simplifying design choice

All link atoms should be associated with the stationary protein cavity region.

The ligand itself should contain no link boundaries.

Therefore:

\[
\Delta\mathbf r_L = \mathbf d,
\]

where:

- \(\Delta\mathbf r_L\) is the ATM coordinate displacement applied to each ligand atom;
- \(\mathbf d\) is the chosen ATM displacement vector.

For cavity atoms and their link sites:

\[
\Delta\mathbf r_C = \mathbf 0.
\]

Here \(\mathbf 0\) means a zero displacement vector.

This design avoids the need to translate virtual link sites with the ligand.

## 13.3 Validation

Build a tiny peptide containing one ML side-chain fragment and one ML/MM boundary.

Test:

- minimisation;
- short NVT dynamics;
- optionally short NVE dynamics for energy-drift diagnostics;
- finite-difference forces on atoms immediately around the boundary.

Do this before adding ATM.

Then repeat after wrapping the relevant force inside ATM with a trivial ligand displacement elsewhere in the system.

---

# 14. Project 0 Problem E: double counting and missing interactions

This is probably the most scientifically important subtlety in Project 0.

A mixed ML/MM construction must avoid two opposite errors:

1. **double counting** an interaction in both ML and MM;
2. **removing** an interaction from MM without actually replacing it in ML.

## 14.1 Bound state

When the ligand is close to the cavity, we want the ML model to describe their local interaction:

\[
E_{\mathrm{ML}}(C\cup L_{\mathrm{bound}}).
\]

If classical MM also retained a full cavity–ligand interaction at short range, the same physics could be counted twice.

OpenMM-ML's mixed-system machinery is specifically intended to replace interactions inside the ML subset while retaining ML–MM cross interactions under mechanical embedding [1,2].

## 14.2 Bulk state

The more subtle case occurs after ATM places the ligand far from the cavity.

A short-range MLIP can become disconnected:

\[
E_{\mathrm{ML}}(C\cup L_{\mathrm{bulk}})
=
E_{\mathrm{ML}}(C)+E_{\mathrm{ML}}(L_{\mathrm{bulk}}).
\]

But if the classical interaction between \(C\) and \(L\) was removed merely because both atom sets were declared ML, then their residual classical long-range electrostatics or dispersion may also be absent.

This creates a possible endpoint error.

## 14.3 Why this should be measured before it is “fixed”

For Project 0 and the first Project-1 systems, we should choose neutral, simple ligands and relatively nonpolar cavities.

Then explicitly measure the classical cavity–ligand interaction at the intended solvent displacement.

Let

\[
\Delta U_{\mathrm{tail}}
\]

denote the classical interaction energy between cavity ML atoms and the displaced ligand that would be present in the original all-MM system but may be absent from the mixed representation.

The subscript “tail” refers to the residual long-range interaction after the ligand has been moved far from the binding site.

We should evaluate both its mean and its fluctuations over representative configurations.

If this quantity is much smaller than our statistical precision target, the approximation may be acceptable for the simple Project-1 benchmark.

If it is comparable to the target free-energy uncertainty, then we must explicitly design a correction.

## 14.4 Why not build the correction immediately?

A fully general correction is not trivial.

One might want something conceptually like

\[
U_{C-L}(r)
\approx
\begin{cases}
U_{\mathrm{ML}}(r), & r \text{ small},\\
U_{\mathrm{MM}}(r), & r \text{ large}.
\end{cases}
\]

Here:

- \(r\) is a cavity–ligand separation coordinate;
- the first line says the local interaction is supplied by ML at short distance;
- the second says classical MM restores long-range interaction at large distance.

However, defining the switching region without double counting, while preserving PME electrostatics and smooth forces, can become a substantial method-development project of its own.

The optimal decision is therefore:

> **Measure the size of the problem first. Do not implement a general long-range correction unless the measurement shows that Project 1 actually needs it.**

This point should be treated as a formal go/no-go gate.

---

# 15. Project 0 Problem F: periodic boundary conditions

ATM places the ligand at a second physical location in the same periodic simulation box.

It is not sufficient to say that the ligand is, for example, “12 Å from the cavity” in the primary box.

The periodic images also matter.

## 15.1 Minimum periodic distance

Let

\[
d_{\min}^{C-L,\mathrm{PBC}}
\]

mean the smallest distance between any cavity ML atom and any ligand ML atom after considering all relevant periodic images.

The superscript “PBC” means periodic boundary conditions.

For a short-range ML model with interaction cutoff \(r_c\), where \(r_c\) is the model's neighbour cutoff distance, we need the intended bulk state to satisfy approximately

\[
d_{\min}^{C-L,\mathrm{PBC}} > r_c + \delta.
\]

Here:

- \(r_c\) is the ML cutoff;
- \(\delta\) is an additional safety buffer.

The exact value of \(\delta\) should be chosen pragmatically after inspecting the model and neighbour-list implementation.

## 15.2 Failure mode

If the box is too small, the ligand may be far from the cavity in the primary image but close to a periodic copy of the cavity.

Then the ML graph can reconnect unexpectedly:

```text
primary cavity                         primary ligand
     |                                      |
     |---------- periodic image ------------|
```

The simulation may not crash. It may simply produce a wrong free energy.

## 15.3 Required tool

Project 0 should include a pre-simulation validator that computes the minimum cavity–ligand distance under periodic boundary conditions for both ATM coordinate states.

A production run should not start if the intended separated state is still within the ML local interaction range through a periodic image.

---

# 16. Project 0 Problem G: what the ligand experiences in bulk solvent

When the ligand is displaced away from the cavity, it is **not** a vacuum ligand in the total hybrid Hamiltonian.

Under mechanical embedding:

- the ligand's internal energy is ML;
- the ligand interacts with MM water and ions through the classical ML–MM cross interactions;
- the cavity ML region likewise interacts classically with its surrounding MM environment.

Thus the total bulk-state energy schematically contains

\[
E_{\mathrm{ML}}(L)
+
U_{\mathrm{MM}}(L,\mathrm{water})
+
U_{\mathrm{MM}}(L,\mathrm{ions})
+
\cdots
\]

where the ellipsis \(\cdots\) means additional classical interactions with other MM environment atoms.

This is exactly the behaviour we want for **mechanical embedding**.

What is absent is electronic polarisation of the ML ligand by the MM solvent field. That limitation is accepted deliberately in Project 0 and Project 1.

---

# 17. Project 0 Problem H: ABFE and RBFE require slightly different ML sets

The machinery must ultimately work for both absolute and relative binding free energies.

## 17.1 ABFE

For ABFE, the permanent ML atom set is simply

\[
M=C\cup L.
\]

ATM evaluates a state with \(L\) in the cavity and a state with the same ligand atoms displaced to bulk solvent.

## 17.2 RBFE

In a typical ATM-RBFE setup, there are two actual ligand molecules in the simulation: ligand \(A\) and ligand \(B\).

Let their atom sets be

\[
L_A
\]

and

\[
L_B.
\]

The permanent ML set should then be

\[
M=C\cup L_A\cup L_B.
\]

In one state the geometry may be

```text
[cavity + ligand A]          [ligand B in bulk]
```

so that the short-range ML energy behaves approximately as

\[
E_{\mathrm{ML}}(C\cup L_A)+E_{\mathrm{ML}}(L_B).
\]

After ATM swaps their positions, the geometry becomes

```text
[cavity + ligand B]          [ligand A in bulk]
```

and the short-range ML energy becomes approximately

\[
E_{\mathrm{ML}}(C\cup L_B)+E_{\mathrm{ML}}(L_A).
\]

This is conceptually elegant because the ML atom membership remains fixed. Only the coordinates change.

## 17.3 Additional RBFE-specific tests

We must confirm that:

- the correct ligand is connected to the cavity ML graph in each state;
- the other ligand is disconnected from the cavity and from its periodic images;
- ligand A and ligand B do not accidentally enter each other's ML cutoff in bulk;
- index remapping does not exchange the identity of the two ligands.

---

# 18. Project 0 Problem I: analytical forces versus finite-difference forces

Correct energies are not sufficient for molecular dynamics.

A bookkeeping error may still produce plausible potential energies but incorrect gradients.

## 18.1 Force definition

For coordinate \(x_i\), the force is

\[
F_i=-\frac{\partial U}{\partial x_i}.
\]

Here:

- \(x_i\) is one Cartesian coordinate of one atom;
- \(U\) is the potential energy;
- \(\partial U/\partial x_i\) is the derivative of energy with respect to that coordinate;
- the minus sign means force points in the direction of decreasing potential energy.

A finite-difference estimate is

\[
F_i^{\mathrm{FD}}
\approx
-\frac{U(x_i+h)-U(x_i-h)}{2h}.
\]

Here:

- \(F_i^{\mathrm{FD}}\) means the finite-difference estimate of the force;
- \(h\) is a small displacement;
- \(x_i+h\) and \(x_i-h\) mean slightly moving that coordinate in the positive and negative directions.

## 18.2 Atoms that must be checked

At minimum, finite-difference tests should cover:

- an ordinary ligand atom;
- a cavity ML atom;
- the ML atom adjacent to a link boundary;
- the MM atom on the other side of the boundary;
- an ordinary MM protein atom;
- a nearby water atom.

## 18.3 States that must be checked

For ATM we should test:

- the \(u_0\) endpoint;
- the \(u_1\) endpoint;
- at least one intermediate alchemical state.

The goal is not to finite-difference every atom in a protein. The goal is to target the places most likely to contain implementation mistakes.

---

# 19. Project 0 Problem J: serialization, checkpoints, and replica exchange

Binding free-energy workflows are long and multi-replica calculations. Reproducible restart behaviour is therefore part of correctness, not merely convenience.

## 19.1 `PythonForce` serialization

OpenMM documentation states that `PythonForce` serializes its Python computation function with `pickle`. Functions that cannot be pickled prevent ordinary XML serialization [5].

Therefore, for each candidate MLIP backend we should test:

```text
construct System
    -> serialize System
    -> reload System
    -> compare energy and forces
```

Required result:

\[
U_{\mathrm{before}}\approx U_{\mathrm{after}}
\]

and

\[
\mathbf F_{\mathrm{before}}\approx\mathbf F_{\mathrm{after}}.
\]

Here \(\mathbf F\) represents the complete force vector over all particles.

## 19.2 Checkpoint test

Similarly:

```text
run short trajectory
    -> save checkpoint
    -> restart
    -> continue
```

The restarted state should preserve the expected coordinates, velocities, global alchemical parameters, and energy evaluation.

## 19.3 Replica exchange

Only after single-replica restart behaviour works should the system be moved to AToM's replica-exchange workflow.

Otherwise, a failure in replica exchange becomes impossible to distinguish from a lower-level ML serialization failure.

---

# 20. Project 0 Problem K: timestep and numerical stability

Speed optimisation should come after correctness.

Adding an ML region and removing some classical constraints can introduce fast vibrational modes, particularly involving hydrogen atoms.

Therefore the initial debugging timestep should be conservative.

A reasonable sequence is:

1. test minimisation;
2. test very short dynamics around \(0.5\) fs timestep if necessary;
3. establish whether \(1\) fs is stable;
4. only later investigate constraints, hydrogen-mass repartitioning, longer timesteps, or multiple-time-step methods.

The unit “fs” means femtosecond, or \(10^{-15}\) seconds.

Project 0 should not be declared unsuccessful merely because the first implementation cannot use the same long timestep as a heavily optimised classical force field.

The first question is whether the Hamiltonian is correct.

---

# 21. The recommended Project-0 validation ladder

The most efficient route is to increase complexity one layer at a time.

## Stage P0.1 — trivial force inside ATM

**System:** tiny synthetic system.  
**Purpose:** prove a Python-evaluated force behaves correctly inside `ATMForce`.

Tests:

- direct \(U(\mathbf R)\) versus ATM \(u_0\);
- direct \(U(T\mathbf R)\) versus ATM \(u_1\);
- analytical versus finite-difference force.

**Pass condition:** all energies and forces agree within documented numerical tolerance.

---

## Stage P0.2 — ligand-only ML/MM

**System:** small organic ligand in solvent or protein environment.  
**Purpose:** reproduce the already established style of ligand-only NNP/MM treatment before adding protein atoms to ML.

This creates an intermediate control between classical ATM and the new cavity-inclusive method.

**Pass condition:** stable simulation and correct endpoint energy evaluation.

---

## Stage P0.3 — one protein link boundary without ATM

**System:** tiny peptide or capped protein fragment with one ML side chain and one ML/MM boundary.  
**Purpose:** isolate link-atom mechanics.

Tests:

- link coordinates;
- boundary forces;
- finite differences;
- short dynamics;
- serialization.

**Pass condition:** stable and differentiable hybrid ML/MM simulation.

---

## Stage P0.4 — cavity fragment + ligand, no solvent

**System:** small cavity-like fragment plus ligand.  
**Purpose:** prove that \(E_{\mathrm{ML}}(C\cup L)\) changes correctly when ATM moves \(L\).

Tests:

- bound geometry;
- displaced geometry;
- explicit check that the local ML graph disconnects at large separation;
- direct versus ATM endpoint energies.

**Pass condition:** the same fixed ML atom set gives the correct connected and disconnected limits.

---

## Stage P0.5 — cavity fragment + ligand in explicit solvent

**Purpose:** introduce mechanical embedding, periodic boundaries, water, ions, and PME-level MM environment treatment.

Tests:

- ligand remains solvated in the bulk ATM state;
- periodic image distance validator;
- measure the residual cavity–ligand classical tail interaction;
- verify no unintended ML periodic reconnection.

**Pass condition:** stable explicit-solvent hybrid simulation with understood interaction bookkeeping.

---

## Stage P0.6 — real protein + one ligand

**Purpose:** test realistic topology, many protein atoms, multiple link sites, and atom remapping.

Tests:

- full setup/restart workflow;
- atom index audit;
- short ABFE-style ATM calculation;
- force stability at all link boundaries.

---

## Stage P0.7 — real protein + two ligands

**Purpose:** test RBFE coordinate swapping with a cavity-inclusive ML region.

Permanent ML region:

\[
M=C\cup L_A\cup L_B.
\]

Tests:

- correct ligand identity at each ATM endpoint;
- no unwanted graph connections;
- no incorrect ATM displacement after remapping.

---

## Stage P0.8 — short multi-window calculation

**Purpose:** test the complete AToM production machinery.

Tests:

- multiple alchemical states;
- replica exchange;
- checkpoint and restart;
- reproducibility;
- performance profiling.

Only after this stage should we call the infrastructure ready for Project 1.

---

# 22. Formal Project-0 completion checklist

Project 0 should be considered complete only when all of the following have been demonstrated.

## Hamiltonian and ATM integration

- [ ] A Python/ML force can be evaluated inside native OpenMM `ATMForce`.
- [ ] ATM \(u_0\) equals an independent evaluation of the undisplaced hybrid system.
- [ ] ATM \(u_1\) equals an independent evaluation of the manually displaced hybrid system.
- [ ] Analytical forces agree with finite-difference forces at representative atoms.

## ML/MM boundaries

- [ ] OpenMM-ML 1.8 link atoms function correctly in the chosen partition scheme.
- [ ] Boundary atoms remain stable during dynamics.
- [ ] Link virtual-site forces are redistributed correctly.
- [ ] The same boundary convention can be generated reproducibly from a structure.
- [ ] The selected boundary is sufficiently far from the chemically important ligand contacts.

## Indexing and coordinate transforms

- [ ] The `oldToNew` mapping is handled explicitly.
- [ ] All ligand atoms receive the intended ATM transformation.
- [ ] All stationary cavity atoms receive zero ATM displacement.
- [ ] Link virtual sites are handled consistently.
- [ ] A human-readable atom map is written for every prepared system.

## Locality and periodicity

- [ ] The cavity and bulk ligand are outside one another's ML neighbour range when intended.
- [ ] Periodic images cannot reconnect the cavity and ligand ML graphs.
- [ ] A pre-run periodic-distance validator is implemented.
- [ ] The effect of any missing cavity–ligand long-range interaction is measured rather than assumed negligible.

## ABFE and RBFE

- [ ] One-ligand ABFE-style transformation works.
- [ ] Two-ligand RBFE-style coordinate swapping works.
- [ ] The correct ligand is bound to the cavity in the correct endpoint.
- [ ] The alternative ligand is correctly evaluated as a disconnected ML component in bulk.

## Reproducibility

- [ ] The hybrid OpenMM system can be serialized and reloaded.
- [ ] Energies and forces are unchanged after reload within numerical tolerance.
- [ ] Checkpoint/restart works.
- [ ] Short replica-exchange runs work.
- [ ] Software versions and model checkpoints are pinned.

## Performance

- [ ] Wall-clock speed is benchmarked for classical MM, ligand-only ML/MM, and cavity-inclusive ML/MM.
- [ ] ML atom count is recorded.
- [ ] The cost of the duplicated ATM energy evaluation is quantified.
- [ ] Performance is acceptable before launching Project-1 production calculations.

---

# 23. Recommended software architecture

The lowest-effort scientifically sensible software stack appears to be:

```text
OpenMM / openmmforcefields or existing AToM preparation
        |
        v
fully classical OpenMM System
        |
        v
OpenMM-ML 1.8 createMixedSystem()
        |
        +-- fixed ML atom set
        +-- mechanical embedding
        +-- link atoms
        +-- oldToNew index mapping
        |
        v
validated hybrid ML/MM OpenMM System
        |
        v
native OpenMM ATMForce
        |
        v
AToM-OpenMM 8.5 workflows
        |
        v
ABFE / RBFE
```

This route is preferable to writing custom link-atom code, a new ML/MM engine, or an ATM-specific MACE implementation.

The main code that we are likely to need should therefore sit in **system assembly, validation, and bookkeeping**, rather than in the mathematical definition of ATM itself.

Likely custom components include:

1. an ML-region selector;
2. a reproducible boundary definition;
3. a wrapper around `createMixedSystem(..., returnInfo=True)`;
4. atom-index remapping into AToM selections;
5. periodic-distance validation;
6. endpoint energy cross-checks;
7. finite-difference force tests;
8. residual long-range cavity–ligand interaction diagnostics;
9. serialization/restart tests;
10. regression tests for all of the above.

---

# 24. Candidate MLIP strategy for Project 0

Project 0 is mainly an infrastructure project, so the first model should be chosen for **software stability and element compatibility**, not because we think it will ultimately be the best model for metals or covalent chemistry.

The ideal first model should:

- be supported directly by OpenMM-ML 1.8;
- operate as a local or clearly understood short-range model;
- support the H/C/N/O/S chemistry present in proteins and ordinary ligands;
- have straightforward GPU execution;
- allow us later to fine-tune if desired;
- not introduce charge/spin complications into Project 0.

OpenMM-ML 1.8 currently provides support for several MACE models, FeNNix-Bio1, AIMNet2, Orb, TorchMD-Net models, and arbitrary ASE calculators [1,8].

A final model choice should be made after a small compatibility benchmark rather than by committing immediately to a single architecture.

The model-selection benchmark should ask only:

- can it run as a mixed system with link atoms?
- can its force be nested under ATM?
- can the system serialize/restart?
- what is the speed for 50–150 ML atoms?
- is the energy stable for capped protein fragments?

Project 0 does not require proving chemical superiority.

---

# 25. A note on the ML region size

We should resist the temptation to make the ML region large simply because the model can handle it.

A larger ML region increases:

- compute cost;
- number of link boundaries unless entire contiguous regions are included;
- the chance of including chemistry outside the training domain;
- the size of any future fine-tuning dataset;
- the chance that two disconnected ML components retain unwanted periodic contacts.

For Project 1, a practical target could be approximately:

- full ligand: perhaps 20–50 atoms;
- a handful of complete interacting side chains: perhaps another 30–100 atoms;
- several link sites.

The exact number is not important. The principle is that the ML region should contain the interactions we explicitly want to improve and no more.

The same ML atom definition should be used for every ligand in a congeneric series whenever possible.

---

# 26. What Project 0 should deliver as software

A successful Project 0 should produce more than a single working notebook.

The reusable deliverables should include:

## 26.1 System builder

Input:

- prepared protein–ligand system;
- definition of ML cavity residues/atoms;
- ligand atom selection;
- selected MLIP and model checkpoint.

Output:

- mixed OpenMM `System`;
- modified `Topology`;
- link-atom information;
- atom-index mapping;
- ATM-ready particle selections.

## 26.2 Validator

The validator should automatically check:

- atom counts;
- ML membership;
- link boundaries;
- ligand displacement membership;
- PBC separation;
- ML graph separation at the bulk endpoint where possible;
- endpoint energy consistency;
- finite-difference forces for a small chosen subset;
- serialization/reload consistency.

## 26.3 Diagnostic report

Every prepared calculation should write a compact report containing:

```text
OpenMM version
OpenMM-ML version
AToM version
MLIP name
MLIP checkpoint/hash
number of real atoms
number of ML real atoms
number of link virtual sites
ML/MM boundary bonds
ATM-displaced particles
ATM displacement vector
ML cutoff or relevant local range
minimum cavity-ligand PBC distance at each endpoint
estimated residual C-L classical tail interaction
serialization test result
endpoint energy test result
force test result
```

This will make later debugging vastly easier.

## 26.4 Regression-test suite

Every bug discovered during Project 0 should become a permanent test.

The test suite is arguably one of the most important outputs because Projects 2 and 3 will add much more complex physics. We need to know immediately if a future code change breaks the simpler Project-0 behaviour.

---

# 27. What Project 0 should *not* try to prove scientifically

A Project-0 calculation should not be judged primarily by agreement with experimental binding affinity.

A perfectly implemented hybrid method could still produce a poor experimental result because:

- the pretrained MLIP is inaccurate for that chemistry;
- mechanical embedding is insufficient;
- the classical ML–MM cross interactions are poor;
- sampling is incomplete;
- protonation or tautomer selection is wrong;
- the protein structure is inappropriate.

Therefore Project 0's scientific standard is **internal correctness**, not experimental superiority.

The decisive questions are:

1. Is the Hamiltonian mathematically well-defined?
2. Are energies and forces evaluated correctly in both ATM coordinate states?
3. Are the link boundaries correct?
4. Is the result reproducible under serialization and restart?
5. Are there any missing or duplicated interactions large enough to matter?
6. Does the same machinery work for ABFE and RBFE?

Only after those are answered should experimental accuracy become the main metric.

---

# 28. Where this leads: brief outline of Project 1

Project 1 will be the first **scientific stress test** of the Project-0 infrastructure.

It should deliberately use easy, well-characterised noncovalent protein–ligand systems.

The ideal first systems should have:

- neutral ligands where possible;
- well-defined protonation states;
- high-quality crystal structures;
- little or no large conformational rearrangement upon binding;
- no metals;
- no covalent chemistry;
- no important changing water-network ambiguity if avoidable;
- experimentally measured binding affinities;
- a congeneric ligand series suitable for both ABFE and RBFE checks.

A simple hydrophobic cavity benchmark such as T4 lysozyme L99A is attractive for the earliest tests because failures are less likely to be obscured by difficult chemistry.

Project 1 should compare at least:

\[
\text{classical MM ATM}
\]

and

\[
\text{cavity-inclusive ML/MM ATM}.
\]

A ligand-only ML/MM calculation can also be retained as an intermediate control because ligand-only NNP/MM ATM already has precedent [7].

The most important Project-1 question is initially **not** whether ML/MM wins against classical MM.

Instead:

> Does the new cavity-inclusive ML/MM ATM method produce stable, reproducible, internally consistent ABFE and RBFE estimates on systems for which the chemistry itself should be easy?

Only after that should we test whether fine-tuning improves results.

A useful later fine-tuning comparison would be:

\[
M_0 = \text{pretrained model},
\]

\[
M_L = \text{model fine-tuned mainly on ligand configurations},
\]

and

\[
M_{CL} = \text{model fine-tuned on cavity + ligand environments}.
\]

Here:

- \(M_0\) is the unmodified foundation/pretrained model;
- \(M_L\) is the ligand-focused fine-tuned model;
- \(M_{CL}\) is the model fine-tuned using both the ligand and capped cavity environments.

The comparison would help distinguish whether errors arise mostly from ligand intramolecular energetics or from the local protein–ligand interaction surface.

Importantly, the reference data for \(M_{CL}\) should include the same capped protein fragments used in production. It is not necessary merely because of ATM to generate arbitrary cavity–ligand configurations at very large separation for a local MLIP.

Project 1 should finish with a clearly validated protocol that says:

1. how to choose the ML region;
2. how to place link boundaries;
3. how to prepare ATM ABFE and RBFE systems;
4. how to validate them before production;
5. when fine-tuning is required;
6. what reference configurations are needed for fine-tuning;
7. what errors and uncertainties remain.

That protocol would then become the foundation for the later metal-binding and electrostatic-embedding projects.

---

# 29. Recommended immediate next actions

The next work should be small and empirical rather than theoretical.

## First task

Create a minimal OpenMM test proving that a `PythonForce` or an OpenMM-ML force can be placed under `ATMForce` and reproduces independently evaluated \(u_0\), \(u_1\), and forces.

This is the highest-value test because failure changes the entire software architecture.

## Second task

Create the smallest possible OpenMM-ML 1.8 system containing one genuine ML/MM covalent boundary and verify the link atom independently of ATM.

## Third task

Combine the two: one stationary link-atom-containing cavity fragment plus one ATM-displaced ligand.

Only after these pass should we prepare a real protein.

This sequence is intentionally conservative. Each calculation should answer one question. If something fails, we should know which layer failed.

---

# 30. Central design decisions proposed for colleague review

The following are the main decisions in this note that should be challenged or confirmed before implementation.

1. **Use OpenMM/OpenMM-ML 1.8/AToM-OpenMM 8.5 as the initial software stack.**
2. **Do not modify the ATM mathematical formalism unless a direct compatibility test proves it necessary.**
3. **Keep the ML region fixed throughout an ATM calculation.**
4. **Treat the complete ligand as ML.**
5. **Allow the cavity and ligand portions of the ML region to become disconnected geometrically in the solvent endpoint.**
6. **Use mechanical embedding only in Projects 0 and 1.**
7. **Use link atoms only on the protein side and choose chemically simple boundaries away from the binding interaction.**
8. **Prefer side-chain-based protein partitions for the first benchmark.**
9. **Do not generate artificial 10–20 Å cavity–ligand fine-tuning structures solely because ATM separates the ligand.**
10. **Measure the magnitude of any missing long-range cavity–ligand interaction before designing a complicated correction.**
11. **Build explicit atom-index, periodic-distance, energy, force, serialization, and restart validators before production calculations.**
12. **Require both ABFE and RBFE compatibility before declaring Project 0 complete.**
13. **Use Project 1 for scientific validation and fine-tuning experiments, not Project 0.**

---

# 31. References and software documentation

The references below are primarily included so that the technical assumptions in this design note can be checked directly.

1. **OpenMM-ML 1.8 release notes.** Released 16 September 2026. The release notes identify link-atom support and the new embedding architecture as major ML/MM additions.  
   https://github.com/openmm/openmm-ml/releases

2. **OpenMM-ML 1.8 user guide — Embeddings / Mechanical Embedding / Molecules Spanning the ML-MM Region.** Documents mechanical embedding, link atoms as virtual sites, `returnInfo=True`, `oldToNew`, and removal of selected MM bonded terms.  
   https://openmm.github.io/openmm-ml/latest/userguide.html

3. **OpenMM `ATMForce` Python API.** Documents \(u_0\), \(u_1\), coordinate transformations, nested `Force` objects, and `getPerturbationEnergy()`.  
   https://docs.openmm.org/latest/api-python/generated/openmm.openmm.ATMForce.html

4. **OpenMM 8.5 release notes.** Documents the introduction of `PythonForce` and its intended use for machine-learning potentials.  
   https://github.com/openmm/openmm/releases

5. **OpenMM `PythonForce` Python API.** Documents subset-particle operation, periodic-boundary declaration, force/energy callbacks, and pickle-based serialization.  
   https://docs.openmm.org/latest/api-python/generated/openmm.openmm.PythonForce.html

6. **AToM-OpenMM release notes and repository.** AToM-OpenMM 8.5 is tested with OpenMM 8.5, uses native `ATMForce`, and provides API-based workflows for ABFE/RBFE preparation and production.  
   https://github.com/Gallicchio-Lab/AToM-OpenMM  
   https://github.com/Gallicchio-Lab/AToM-OpenMM/releases

7. **Enhancing Protein–Ligand Binding Affinity Predictions Using Neural Network Potentials.** Demonstrates ATM RBFE using a ligand-only ANI-2x/MM hybrid approach and therefore provides an important precedent/control for ML/MM + ATM, while not addressing the cavity-inclusive link-atom problem proposed here.  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11214867/

8. **OpenMM-ML repository.** Current model support includes MACE models, FeNNix-Bio1, AIMNet2, TorchMD-Net models, Orb, and ASE calculators.  
   https://github.com/openmm/openmm-ml

9. **Potential distribution theory of alchemical transfer.** Provides a formal description of ATM as a coordinate-transfer method connecting bound and unbound states.  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11803756/

10. **Validation of the Alchemical Transfer Method for the Estimation of Relative Binding Affinities of Molecular Series.** Describes practical ATM RBFE validation and the use of AToM-OpenMM.  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC10577236/

---

# 32. Final project definition in one paragraph

Project 0 should build and validate the smallest reusable OpenMM-based framework in which a ligand and selected protein cavity atoms are described by a local MLIP, the remaining protein and solvent are described by classical MM, covalent protein boundaries are capped with link atoms, and the complete hybrid Hamiltonian is evaluated correctly by native OpenMM `ATMForce` in both ABFE and RBFE settings. The work should focus on force/energy correctness, atom-index bookkeeping, link-boundary behaviour, periodic separation, missing/double-counted interactions, serialization, restart, and replica-exchange compatibility. It should deliberately avoid metals, electrostatic embedding, covalent chemistry, and other complications. Project 1 will then use this fixed machinery on simple, well-characterised noncovalent binders as the first stress test and as the platform for studying whether cavity-inclusive ML treatment and targeted fine-tuning improve binding free-energy predictions.
