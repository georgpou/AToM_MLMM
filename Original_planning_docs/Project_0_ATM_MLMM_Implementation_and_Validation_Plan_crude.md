# Project 0: ATM-ML/MM Implementation and Validation Plan

**Version:** 2.0 - researched replacement for the original design note  
**Research date:** 29 September 2026  
**Status:** Proposed implementation plan; source-code audit completed, numerical qualification not performed  
**Original specification:** `Project_0_ATM_MLMM_Design_and_Validation_Plan.md`  
**Audience:** Scientific developers, computational chemists, and colleagues reviewing the assumptions  
**Goal:** Build the smallest reusable platform that correctly evaluates a fixed, cavity-inclusive, mechanically embedded ML/MM Hamiltonian with protein link atoms in ATM absolute and relative binding free-energy calculations.

**Architecture:** OpenMM-ML constructs the physical hybrid Hamiltonian. A small project-owned layer checks its atoms, boundaries, interactions, and numerical behavior. Native OpenMM `ATMForce` applies coordinate transformations, and a narrowly defined AToM adapter handles production execution without silently changing the Hamiltonian.

**Proposed core stack:** OpenMM 8.6.1, OpenMM-ML 1.8, AToM-OpenMM tag `v8.5.0`, and an initially local MACE-OFF23-small checkpoint. The combined stack remains a candidate until the gates below pass.

> For implementation workers: implement one work package at a time, beginning with its tests. Review its evidence before proceeding. This document authorizes planning, not an assertion that the platform already works. Automated coding agents should use their test-driven execution and independent-review workflows rather than implementing every stage in one unreviewed change.

## Reading guide

Read Sections 1-4 first for the audit outcome and the proposed scientific definition. Sections 5-9 explain the software, interfaces, and difficult implementation details. Section 10 is the ordered work plan. Sections 11-15 specify acceptance, analysis, handover, and future expansion. The appendices provide source traceability and a glossary.

This document uses four kinds of statements:

- **Verified:** supported by inspected documentation, a release, or tagged source code. A source identifier such as [S04] links to that evidence.
- **Derived:** a mathematical consequence of an explicitly stated Hamiltonian or coordinate transformation.
- **Proposed:** a project decision, test, tolerance, or implementation requirement. These are recommendations, not claims about an existing tested package.
- **Unresolved until tested:** something source inspection cannot establish, particularly the interaction between nested forces, virtual sites, accelerators, and replica workers.

The scientific equations and proposed tests below are not results from simulations conducted during this review. No GPU benchmark, model qualification, free-energy calculation, or installation of the proposed combined environment was performed.

---

# 1. Overall assessment

## 1.1 What should be retained from the original plan

The original plan has the right central separation: construct one valid physical ML/MM energy function, then let ATM evaluate it at different coordinates. Keep the ML membership fixed. Keep the whole ligand inside that membership. Put link boundaries on stationary protein fragments rather than on the transferred ligand. Start with mechanical embedding and uncomplicated chemistry. These are the original design choices, retained here rather than replaced by a different research project.

The new work should therefore **not** begin by modifying the MACE architecture to contain an alchemical parameter, designing a new soft-core neural network, or rewriting ATM. It should begin by proving that the existing components implement the intended combined calculation.

The original distinction between Project 0 and Project 1 is also retained. Project 0 establishes a platform and its declared limitations. Project 1 asks how useful that platform is on ordinary protein-ligand binding problems. Agreement with experiment is not a substitute for Project-0 tests, and passing those tests is not proof of experimental accuracy.

## 1.2 What must change

The original note is not yet an implementation-ready specification. Several statements need correction, and some important failure modes were missing.

| Finding | Audit result | Required consequence |
|---|---|---|
| A01. Software floor | OpenMM-ML 1.8 explicitly requires OpenMM >=8.6.1. OpenMM 8.5 is not the appropriate baseline. PythonForce particle subsets arrived in 8.6, not 8.5. [S02], [S04] | Start qualification with 8.6.1. Do not force installation against 8.5. |
| A02. AToM force routing | The tagged AToM implementation does not select `PythonForce` in its default name-based route. [S14] | Explicitly route physical forces; otherwise cavity-ligand ML interactions can remain outside ATM. |
| A03. Preparation differs from production | The ABFE no-ATM preparation path does not apply the same variable-force-group handling as RBFE. Preparation also contains its own timestep and alchemical-parameter assignments. [S15], [S16] | Own a small, audited preparation layer, or submit a focused upstream fix. Do not assume a production setting governs preparation. |
| A04. PME bookkeeping | For short-range ML, OpenMM-ML retains a periodic-image electrostatic contribution rather than removing the entire ML-subset PME energy. [S07] | Replace the vague missing-tail argument with an exact interaction ledger and a clearly defined approximation assessment. |
| A05. Link indexing | Version 1.8 currently appends link sites, so its real-atom mapping is identity. Its public return value is a dictionary. [S06], [S08] | Still consume and validate the map. Do not describe current renumbering as an observed behavior. |
| A06. Boundary terms | Removing only bonded terms whose every atom is ML would not reproduce the implemented boundary convention. [S08] | Audit bonds, angles, proper and improper torsions, and constraints individually. |
| A07. Endpoint API | `getPerturbationEnergy()` returns `(u1, u0, energy)`. These are energies of the forces inside ATM, not automatically the entire system. [S09] | Name the values explicitly and compare quantities with matching scope. |
| A08. Binding thermodynamics | Coordinate/force checks alone do not define a standard binding free energy. The binding domain, restraints, signs, and standard-state conversion must be specified. [S29], [S30] | Add a thermodynamic-cycle gate before calling any result ABFE or RBFE. |
| A09. Model behavior in counterfactual states | Every ATM step can evaluate geometries that the current weighted state barely occupies. A finite soft-core formula cannot repair a neural network returning NaN or an unphysical attractive collapse. | Add compressed-contact and intermediate-state model-admissibility tests before production. |
| A10. Evidence strength | The ligand-only ANI/MM precedent does not validate a joint cavity-ligand model with caps. [S28] | Retain it as a control, not as proof that this extension works. |

The recommendation is **proceed with a gated prototype**, not proceed directly to target production. There is a plausible low-change route, but it includes an actual integration layer; merely connecting package names is insufficient.

## 1.3 Three separate meanings of success

**Implementation correctness:** for the chosen mathematical energy function, the code returns the right energy, forces, coordinates, and parameters.

**Thermodynamic correctness:** the sampled states and reported estimator correspond to the stated restrained binding cycle, including its sign and corrections.

**Physical adequacy:** the model and embedding describe the selected chemistry well enough, and their approximations are small enough, to justify the intended application.

A differentiable but chemically poor potential may pass the first level. A stable simulation with an incorrect standard-state conversion may fail the second. A perfect estimator cannot repair missing physics. The project report must state which level each piece of evidence addresses.

## 1.4 Global constraints

The first qualified configuration will have fixed ML membership, neutral closed-shell ligands and neutral capped protein fragments, local ML, mechanical embedding, fixed displacement vectors, fixed-volume production, and no link boundary through either ligand. It will not include metals, reaction chemistry, changing protonation, adaptive regions, electrostatic embedding, LJPME, hydrogen-mass repartitioning, or multiple-time-step integration.

All production inputs must have explicit units, exact model identity, a force-routing report, and a record of retained constraints. Unsupported chemistry or force classes must produce an error before dynamics, not a warning followed by an attempted calculation.

---

# 2. Define the calculation before choosing optimizations

## 2.1 Atom sets and coordinates

Let $L$ be all real atoms of one ligand. Let $C$ be the real protein atoms selected for ML treatment. Let $E$ be all remaining real atoms, including the rest of the protein, water, and ions.

For ABFE, the real ML set is

$$M=C\cup L.$$

The symbol $\cup$ means set union: include every atom belonging to either set, without duplication.

For dual-ligand RBFE, use

$$M=C\cup L_A\cup L_B,$$

where $L_A$ and $L_B$ are the two actual ligand molecules present in the box. Their identities do not change when their positions are exchanged.

Let $H$ denote the artificial hydrogen link sites. They are inputs to the ML model but are not independent physical particles with their own thermal motion. Let $\mathbf R$ denote the coordinates of all real atoms. Their derived positions are $\mathbf h(\mathbf R)$. Let $\mathbf B$ contain the three periodic box vectors.

The first implementation must distinguish **real-atom identity**, **OpenMM particle index**, and **model input index**. These are different concepts, even when some numbers happen to coincide.

## 2.2 An operational definition of the hybrid Hamiltonian

Use the following definition rather than an unspecified boundary-energy symbol:

$$
U_{\mathrm{hyb}}(\mathbf R;\mathbf B)
=U_{\mathrm{keep,MM}}(\mathbf R;\mathbf B)
+E_\theta(\mathbf R_M,\mathbf h(\mathbf R);\mathbf B).
$$

Here $U_{\mathrm{hyb}}$ is the total physical hybrid potential energy. $U_{\mathrm{keep,MM}}$ is the energy of the actual retained classical force objects after the embedding builder has made its modifications. $E_\theta$ is the chosen ML model with fixed parameters $\theta$, evaluated on the selected real atoms and link hydrogens. The subscript $M$ means select coordinates belonging to $M$.

This definition is deliberately operational: the exact retained force objects, their parameters, and the cap-coordinate rule are part of the Hamiltonian. The words "mechanical embedding" alone are not a complete specification.

For diagnostics define

$$D_{\mathrm{MM}}=U_{\mathrm{full,MM}}-U_{\mathrm{keep,MM}},$$

where $U_{\mathrm{full,MM}}$ is the original all-MM energy. Then, by construction,

$$U_{\mathrm{hyb}}=U_{\mathrm{full,MM}}-D_{\mathrm{MM}}+E_\theta.$$

This identity is a bookkeeping check. It does not mean that $D_{\mathrm{MM}}$ is necessarily the MM energy of a separately parameterized capped molecule. Do not introduce an additional capped-MM subtraction unless deliberately defining and validating a different Hamiltonian.

**Proposed implementation:** save the original MM system, the retained-MM system, and the hybrid system as separate immutable artifacts. Make it possible to evaluate all three on the same real coordinates and box.

## 2.3 What remains classical

Under the initial definition, real ML atoms retain their classical coupling to the MM environment. Consequently, a ligand displaced into the solvent has ML intramolecular energetics and classical interactions with MM solvent. It is not a gas-phase ligand in the complete simulation.

The model does not receive the surrounding MM electric field as an electronic embedding input. Keeping classical partial charges for cross-region interactions is not equivalent to polarizing the ML model. That limitation is intentional and must appear in the eventual methods description. The released mechanical-embedding behavior is documented in [S05], [S07].

Do not zero every ML atom's charge in the original `NonbondedForce`: that would remove desired ML-MM electrostatics. Do not assign the artificial cap a standard charged MM hydrogen type: it would introduce an additional classical interaction center not present in the intended system.

## 2.4 Locality and disconnected fragments

For an additive local model, a graph with no edge between two components can give

$$E_\theta(C\cup L\cup H)=E_\theta(C\cup H)+E_\theta(L).$$

This equality concerns the **ML contribution**, not the entire hybrid energy. It requires that the model has no additional global charge equilibration, long-range coupling, or non-additive graph-wide operation that connects the components.

Keep a single model evaluation on the joint ML set. At the bound geometry, this allows protein-ligand interactions. At the separated geometry, the neighbor graph should disconnect naturally. Evaluating each residue or ligand as a separate batch item would remove the very bound-state interactions the project is trying to model.

A model's neighbor cutoff is not necessarily the full distance through which information can propagate over several message-passing layers. Nevertheless, **absence of every intercomponent edge** is sufficient to disconnect the graph. Conversely, placing a cap one neighbor cutoff from a ligand is not, by itself, proof that the cap cannot influence the predicted interaction indirectly.

Test additivity, do not assume it from a model's name. The test must include the same caps, precision, energy convention, and periodic settings as production.

## 2.5 Formal charge is not a sum of arbitrary partition charges

A chemically neutral capped fragment can have real atoms whose inherited MM partial charges sum to a noninteger value. These are different descriptions serving different purposes. The formal charge describes the chemical ML input; the inherited partial charges define the classical embedding.

The first fixtures should make both easy to inspect: neutral ligands and neutral side-chain fragments with an unambiguous valence pattern. Do not repair a partition by renormalizing its partial charges without specifying a new force field and testing its consequences.

An unsupported charged fragment is not made suitable for a neutral-molecule model merely because the complete protein-plus-solvent box is electrically neutral.

---

# 3. Link boundaries, constraints, and their derivatives

## 3.1 Start with one uncomplicated cut

Use a tiny alkane chain with one carbon-carbon cut for the first geometry test. For the first peptide fixture, an alanine side chain treated as ML and capped across the $C_\alpha-C_\beta$ bond gives a small, understandable fragment. Here $C_\alpha$ is the backbone alpha carbon and $C_\beta$ is the first side-chain carbon.

This does not establish that every side chain is safe. A residue selector must follow the actual covalent graph, include the selected side chain's hydrogens, and enumerate every edge crossing the boundary. Do not implement it as "all atoms except N, CA, C, O": atom naming variants and extra bonds make that brittle.

Initially reject charged side chains, ambiguous histidines, disulfide-linked cysteines, ring cuts, peptide-bond cuts, proline partitions needing more than one cut, incomplete residues, and multiple proposed caps tied to one MM parent. These restrictions deliberately keep the first proof small. Later lifting a restriction requires a new fixture and a documented reason.

## 3.2 The cap-position rule

For one boundary, let $a$ be the real ML parent, $b$ its bonded MM neighbor, and $h$ the link hydrogen. Define

$$\mathbf v=\mathbf r_b-\mathbf r_a,\qquad r=|\mathbf v|,\qquad \mathbf n=\mathbf v/r,$$

and

$$\mathbf r_h=\mathbf r_a+d_h\mathbf n.$$

The vector $\mathbf v$ points from the ML parent toward the MM parent. Its length is $r$, and $\mathbf n$ is the corresponding unit vector. The constant $d_h$ is the chosen ML-parent-to-hydrogen distance. Therefore the cap stays at a fixed bond length even when the original boundary bond stretches.

The 1.8 implementation uses a `LocalCoordinatesSite`, adds a zero-mass site, and supplies default distances from covalent radii; explicit distances can be supplied. It currently appends sites to the topology. [S08]

**Proposed rule:** record the actual distance from the constructed virtual site in `links.json`, rather than relying on a remembered default. Use one fixed distance convention across training structures, validation, and production. Do not tune cap lengths to improve individual ligand affinities.

## 3.3 Where the cap force goes

The cap coordinate depends on two real atoms. If the model exerts a force on the cap, that force must be transferred to those real atoms using the derivative of the coordinate rule.

For the nonperiodic local geometry above, define the matrix

$$A=\frac{d_h}{r}(I-\mathbf n\mathbf n^{\mathsf T}),$$

where $I$ is the three-dimensional identity matrix, and the superscript $\mathsf T$ means transpose. The matrix removes the part parallel to the boundary bond and scales the perpendicular part. Differentiating gives

$$\frac{\partial\mathbf r_h}{\partial\mathbf r_a}=I-A,\qquad
\frac{\partial\mathbf r_h}{\partial\mathbf r_b}=A.$$

Thus a model force $\mathbf F_h$ on the cap contributes

$$\Delta\mathbf F_a=(I-A)^{\mathsf T}\mathbf F_h,\qquad
\Delta\mathbf F_b=A^{\mathsf T}\mathbf F_h.$$

These are additional contributions, not replacements for the parents' other forces. They sum to the cap force. They are not generally a fixed 50:50 split, nor the split appropriate for a hydrogen placed at a fixed fraction of the original bond length.

**Proposed tests:** implement this independent analytic calculation for a toy cap potential; compare it with the real-parent forces returned by OpenMM; then repeat under ATM. The production code should use OpenMM's virtual-site machinery rather than manually redistributing a second time.

## 3.4 Why ATM makes the virtual-site test important

Tagged native ATM code constructs internal systems and clones child forces. Its internal system-copy routine does not copy the outer virtual-site definitions. [S11]

That observation is **not a proof of failure**. A stationary derived site may be evaluated using outer coordinates and have its force redistributed by the outer context. It does mean that correctness has to be checked at the level of real parent forces. An energy comparison alone cannot settle whether a cap force has been redistributed zero, one, or two times.

The initial transformation leaves both protein parents undisplaced, so the correct cap is also undisplaced in both ATM coordinate states. "Stationary" here means not moved by the artificial ATM transformation. The protein atoms and cap still move during ordinary molecular dynamics.

Do not attempt to fix this by copying virtual sites into internal contexts before demonstrating a failing derivative test. Such a patch could introduce double redistribution.

## 3.5 Periodic coordinates around a cut

A physically short covalent bond can appear long when its endpoints are stored in different periodic images. The cap-construction test must therefore cover whole-molecule wrapping and a boundary bond near a box face.

For the first production configuration, maintain a consistent unwrapped representation of each covalent molecule when constructing and diagnosing its caps. Test the actual coordinate representation passed through OpenMM and the ML adapter. Never silently apply a minimum-image rule in the independent validator while the production virtual site uses another rule: the two calculations would no longer validate the same function.

A failure here blocks periodic production. The preferred repair is a documented, consistent coordinate convention or an upstream virtual-site handling fix, not a state-dependent relocation of caps.

## 3.6 Which classical boundary terms are retained

Create an explicit table of every original term touching an ML or boundary atom. Record its type, atom identities, original parameters, and whether it survives. The implemented convention is more selective than "remove terms entirely within ML": in particular, boundary-adjacent angles and torsions can be removed according to their central atoms and local connectivity. [S08]

The independent test fixture should contain a bond, angle, proper torsion, improper torsion, nonbonded exception, and a boundary constraint. Give the terms distinctive parameters so a missing or duplicated term is recognizable. Start with the standard Amber-style force classes; reject an unfamiliar class rather than pretending the same rules necessarily apply.

Do not keep an extra classical angle merely because it feels stabilizing. First establish whether the cap geometry already represents that degree of freedom in the model, and whether adding the term defines unwanted double counting.

## 3.7 Constraints are part of the ensemble

The public mixed-system builder can remove constraints between selected ML atoms. [S06] The proposed baseline uses this behavior and verifies the resulting list. Retain rigid water and appropriate MM constraints, but avoid classical bond constraints inside the ML region for the initial proof.

Record particle masses and constraints before and after conversion. All ATM states of one calculation must have the same masses and constraints. All comparisons intended as exact identities must use the same constrained coordinate space.

A model-changing control with different constraints can be scientifically useful, but it is not an exact Hamiltonian-equivalence test. Likewise, setting an MM-to-ML interpolation parameter to zero is not automatically a return to the original MM ensemble if the constraints have changed.

During finite-difference force tests, perturb a real coordinate and recompute virtual sites. Do **not** additionally project the coordinates back onto constraints unless intentionally checking a derivative along that constrained path. The usual energy-gradient test compares unconstrained Cartesian energy derivatives with the reported force before integration constraints are applied.

---

# 4. Periodic electrostatics and the physical approximation gate

## 4.1 Replace "the C-L tail is missing" with a precise question

For the local-model path, OpenMM-ML changes ML-ML nonbonded exceptions while retaining the real-atom charges. Its documented intention is to retain an MM approximation to interactions between periodic copies of ML atoms when the model itself is short-range. Setting `mlLongRange=True` selects a different electrostatic bookkeeping path; it does not add long-range physics to a local model. [S05], [S07]

Therefore these questions must be kept separate:

1. Which nearest-image classical interactions were removed?
2. Which periodic electrostatic contributions remain?
3. Which interactions can the local model represent at the current geometry?
4. Which Hamiltonian do we actually intend to call our physical approximation?

The answer matters both when the ligand is bound and when it is displaced. It also matters between separately capped protein fragments, and between the two ligand molecules in RBFE. A diagnostic restricted to the bulk cavity-ligand pair is incomplete.

## 4.2 The first supported electrostatic configuration

**Proposed baseline:** one standard `NonbondedForce`, PME electrostatics, ordinary cutoff Lennard-Jones interactions, explicit rigid water, no LJPME, no custom charge offsets, and no extra polarizable particles. Keep the exact cutoff, switching behavior, PME tolerance, and dispersion-correction setting in the manifest.

For the first synthetic ledger fixture, disable analytical dispersion correction to make the pair accounting transparent. For the first solvated qualification, retain that explicitly declared setting in all corresponding controls. A later enabling of dispersion correction needs its own bookkeeping and box-size check; it is not an invisible performance option.

Use an orthorhombic box first. Supporting arbitrary triclinic boxes, multiple periodic image contacts, or very small boxes requires extra geometry tests, not just replacing a distance formula.

## 4.3 Exact bookkeeping before approximate physics

For saved coordinates, compare the original classical system with the retained-MM system. The difference is the actual removed energy $D_{\mathrm{MM}}$, including any changes to exceptions and boundary terms. This is the first diagnostic because it directly tests what the builder did.

Do not label the entire all-MM cavity-ligand interaction "missing" without comparing it with the retained-MM contribution. Some periodic pieces may still be present. Conversely, a zero ML cross-component contribution does not show that all classical long-range interactions were restored.

Audit ordinary ML-MM cross interactions using a tiny charged fixture in which an MM test particle is moved near an ML real atom. Audit caps separately: moving an MM test particle near a cap must not create a new classical cap charge or Lennard-Jones interaction.

## 4.4 A PME-compatible cross-interaction diagnostic

A force group does not generally provide a protein-ligand decomposition of a single PME force. For a diagnostic, use independent charge-mask evaluations with identical box and electrostatic settings.

Let $Q(S)$ be the PME energy with only the charges of atom set $S$ retained and all other charges zero. Then the quadratic nature of fixed-charge electrostatics gives the cross term

$$Q(C\cup L)-Q(C)-Q(L)+Q(\varnothing).$$

The symbol $\varnothing$ means the empty set. This expression extracts a cross contribution under the specified periodic convention. It is not simply a vacuum Coulomb sum.

Implementation requirements are to set Lennard-Jones terms to zero for this diagnostic, update exception charge products consistently, preserve explicit PME parameters, and keep any charge-background contribution consistently across the four evaluations. Nonneutral subsets make that last point particularly important. A changing PME mesh chosen separately in each context can contaminate a tiny difference, so obtain the realized parameters and control them.

Use a separate mask procedure for Lennard-Jones interactions with the original mixing and switching conventions. A force with offsets or a nonstandard mixing rule needs its own implementation. The initial validator should refuse such input rather than silently approximate it.

## 4.5 An energy average is not a free-energy correction

Suppose a scientifically specified alternative Hamiltonian adds $\delta U_s$ at endpoint $s$. The free-energy change at that endpoint is

$$\delta F_s=-RT\ln\left\langle\exp[-\delta U_s/(RT)]\right\rangle_{s,\mathrm{hyb}}.$$

Here $R$ is the molar gas constant, $T$ is temperature, and the brackets mean an equilibrium average in the original hybrid endpoint ensemble. Energies in this equation are molar energies, for example kJ/mol. This identity follows by taking the ratio of the two configurational partition functions.

The correction to a bound-minus-bulk difference is $\delta F_{\mathrm{bound}}-\delta F_{\mathrm{bulk}}$. Reporting only the mean and standard deviation of $\delta U$ does not evaluate that expression or prove adequate statistical overlap. Exponential reweighting may be dominated by a few configurations.

**Proposed decision:** first quantify the defined approximation, including displacement and box sensitivity. If it exceeds the predeclared application budget, stop progression to Project 1 and decide between a better long-range Hamiltonian and a deliberately narrower application. Do not add a distance switch between "ML when bound" and "MM when unbound" as an emergency repair.

The original recommendation not to overengineer long-range corrections is retained. What changes is the rigor of the diagnostic and the fact that the physical approximation must be named before it can be assessed.

## 4.6 Check periodic image-choice boundaries as well as model cutoffs

A nearest-image interaction convention can change which periodic image is used when a pair crosses a box midplane. Consequently, continuity of the model at its cutoff does not by itself establish continuity of the complete hybrid force at an image-choice boundary. This is a mathematical risk to test, not a claim that an observed trajectory has failed.

For the declared exception and coordinate conventions, scan energy and forces across these image-choice boundaries in the tiny periodic fixture. Distinguish a harmless whole-molecule rewrapping from a physical pair crossing the image-selection seam. If a force discontinuity enters the admitted sampling domain, qualify a different convention or a restriction that keeps the domain away from the seam; account for any added restraint in the thermodynamic definition. A large minimum cavity-ligand distance alone does not prove this gate passes.

# 5. Software versions, installation, and model choice

## 5.1 A candidate baseline, not an invented tested environment

The distinction between a package's documented requirement and a combination we propose to test is essential.

| Component | Initial choice | Evidence and qualification status |
|---|---|---|
| Operating system | Linux x86-64 for the first GPU qualification | Project choice. Record distribution, kernel, GPU, and driver. Do not promise the same environment on macOS. |
| Python | 3.11; freeze the resolved patch version | Project choice within the inspected MACE requirements. [S21] |
| OpenMM | **8.6.1** | Required floor of OpenMM-ML 1.8; also contains relevant PythonForce fixes. [S02], [S04] |
| OpenMM-ML | **1.8**, tagged source | Contains the new embedding/link-site implementation being audited. [S03], [S04] |
| AToM-OpenMM | **tag `v8.5.0`** | Its release was tested against OpenMM 8.5, not evidence that our 8.6.1 composition is already qualified. [S12] |
| MACE package | **mace-torch 0.3.16** | Candidate selected from the inspected release. Its required `e3nn` version is 0.4.4. [S20], [S21] |
| Model | **MACE-OFF23-small**, frozen local checkpoint | Initial local organic model; subject to license and numerical-admissibility gates. [S19], [S23] |
| PyTorch | **2.8.0** for initial qualification | A deliberate candidate, not a claim that it is the newest release. Official CPU and CUDA 12.6 wheel options exist. [S24] |
| Independent estimator | **PyMBAR 4.0.3** | Deliberately versioned API for the independent validation implementation. [S33], [S34] |
| AToM estimator | Python implementation bundled in the pinned AToM source | Do not install R merely because older ATM workflows used R UWHAM. [S13], [S18] |
| Structure preparation | Reuse a documented prepared MM fixture first | Avoid making a new parameterization pipeline a prerequisite for testing ATM. |
| Optional template generation | openmmforcefields **0.16.0** | Separate qualification track; explicitly specify the force-field identity. [S35] |
| Testing/configuration | pytest, NumPy, SciPy, PyYAML; resolve then lock exact builds | These exact resolved versions cannot honestly be called a working lock before solving and testing the environment. |

The AToM tag and its package metadata are not identical: the inspected tagged `pyproject.toml` still reports `8.5.0beta`. Therefore record the Git tag, resolved full commit hash, source-tree hash, and package-reported version. Do not treat a version string alone as an unambiguous source identifier. [S13]

Do not install the historical separate ATM force plugin for this route. The plan uses native `openmm.ATMForce`.

## 5.2 Installation in two environments

First create a CPU qualification environment. It should run the analytic fixtures, topology logic, serialization tests, and small model checks. Then create a separate GPU environment. Do not repeatedly replace CPU and CUDA packages in the same environment and call the result reproducible.

The following is a **candidate installation recipe to execute during Gate G00**, not a recipe tested in this review:

```bash
python3.11 -m venv .venv-p0-cpu
. .venv-p0-cpu/bin/activate
python -m pip install --upgrade pip
python -m pip install "openmm==8.6.1"
python -m pip install "torch==2.8.0" --index-url https://download.pytorch.org/whl/cpu
python -m pip install "mace-torch==0.3.16" "pymbar==4.0.3" pytest pyyaml
python -m pip install "openmmml @ git+https://github.com/openmm/openmm-ml.git@1.8"
python -m pip install "atom-openmm @ git+https://github.com/Gallicchio-Lab/AToM-OpenMM.git@v8.5.0"
python -m pip check
python -m openmm.testInstallation
python -m pip freeze --all > environment-cpu.resolved.txt
```

Package extras and available builds must be checked for the actual machine. OpenMM's current installation instructions distinguish the CPU/OpenCL/Reference wheel from CUDA extras and document `python -m openmm.testInstallation`. PyTorch publishes version-specific wheel commands. [S24], [S26]

For a separately created CUDA-12 qualification environment, the corresponding candidate changes are:

```bash
python -m pip install "openmm[cuda12]==8.6.1"
python -m pip install "torch==2.8.0" --index-url https://download.pytorch.org/whl/cu126
```

Then install the same pinned project packages, check the complete dependency solve, and run the gates again. The driver's supported runtime, OpenMM plugin build, PyTorch CUDA runtime, and GPU architecture must all be recorded. Do not install an arbitrary additional CUDA toolkit as a guessed remedy for an import failure.

The final deliverable from G00 is a tested lock with all transitive versions, build identities, and downloadable artifact hashes. The recipe above is not that lock. Once qualification passes, replace tag-based source requirements with resolved immutable commits or locally archived source wheels. Retest any dependency change.

## 5.3 Why choose one local model first

Model comparison is not the first engineering milestone. The smallest useful sequence is an analytic callback, then one supported local model, then a second model only after the interface contract passes.

MACE-OFF23-small is proposed for the first organic fixtures because the inspected OpenMM-ML adapter recognizes it as local. Use simple neutral fragments before testing more diverse protein chemistry. MACE-OFF24-medium can be a later size/accuracy comparison, not a simultaneous requirement for initial completion. Models with long-range electrostatics, global charge handling, or polarization do not inherit the local-model qualification automatically. [S19]

The MACE-OFF checkpoint repository specifies an Academic Software License and excludes commercial use under that license. Verify that the intended collaboration and computing arrangement are permitted before distributing weights or launching a project around them. The package code license and the model-weight license are distinct. [S23]

If licensing or model-admissibility fails, choose another model deliberately and repeat the relevant gates. Do not conceal a change of weights behind the same display name.

## 5.4 Store the actual model, not just a cache alias

Archive the approved checkpoint in a controlled model directory and compute its SHA-256 digest. Record the source URL and source revision, architecture, supported elements, cutoff, precision, energy-output convention, and allowed use. Pretrained loader URLs can refer to mutable repository branches, so a cached filename is not sufficient identity. [S22]

Production workers should be able to start with networking disabled. A cache miss must not silently download a different model. The model manifest must be checked before reading a pickle-based artifact. Only load trusted model files and trusted serialized systems.

The independent model test uses the same checkpoint directly through its native interface. It must not simply call the same OpenMM callback under a different function name.

**Checkpoint-loader compatibility is an explicit G00/G05 issue.** The inspected generic MACE adapter and foundation-model loader call `torch.load` without specifying `weights_only`. PyTorch changed the default to `weights_only=True` from version 2.6; a checkpoint containing a complete Python model can therefore require explicit handling rather than loading like a tensor-only state dictionary. This is a source-identified compatibility risk for the proposed PyTorch 2.8 environment, not a runtime failure demonstrated here. [S19], [S22], [S39]

Test the approved file in a fresh process before trying a mixed system. Record relevant loader environment variables and any imported compatibility configuration. If the default rejects the trusted full-model checkpoint, prefer a narrowly reviewed loader change that explicitly sets the required policy for that approved artifact, or a supported reconstruction from architecture plus weights. Do not globally replace `torch.load` or disable safe loading for arbitrary files. Freeze any required adapter patch, add a regression test, and qualify serialization again. Merely changing the PyTorch version to make the error disappear is not an adequate provenance record.

## 5.5 Energy conventions and units

The inspected MACE adapter's default `interaction_energy` is not a ligand-protein pair energy. It excludes atomic reference contributions from the model's total-energy convention. The baseline here explicitly requests `returnEnergyType="energy"` and uses the same convention in the independent model evaluator. [S19]

For a fixed set of real ML atoms and caps, a constant atomic reference shift cancels from the ATM perturbation. It does not justify comparing raw absolute energies of systems with different atom counts. Add a test that deliberately changes an energy-zero constant and checks that the final free-energy difference remains unchanged.

Use nm and kJ/mol inside the project interfaces. Convert once at the model boundary. The force conversion must include both the energy conversion and the inverse-length conversion. A missing factor of ten can leave apparently plausible energies and completely wrong dynamics.

The versioned MACE adapter uses a rounded eV-to-kJ/mol factor, 96.4853, and a factor of ten for Angstrom-to-nm force conversion. Match that convention when checking adapter identity, or explicitly allow the known conversion rounding rather than misdiagnosing it as a force bug. [S19]

## 5.6 Structure preparation should not become the bottleneck

The first fixtures should be generated deterministically and carry checked-in topologies and parameters. For a first real protein, reuse one documented Amber-style protein/water/ligand setup rather than simultaneously comparing protein force fields or charge methods.

A defensible continuity choice is ff14SB/TIP3P with GAFF2 ligand parameters, with every parameter file and ligand charge vector archived. The earlier ligand-only NNP/ATM paper used that general family, but its older software and settings are historical precedent, not a compatibility specification for this project. [S28]

If generating templates through openmmforcefields 0.16.0, explicitly name the desired force field; its release changed template-generator behavior so an omitted force-field name is no longer the old automatic choice. [S35], [S36] Record the actual AmberTools or OpenFF toolkit build if used. Neither belongs in the minimal analytic-test runtime just because it may be useful later.

Missing residues, protonation, tautomer choices, alternate conformers, metal removal, and ligand stereochemistry must be resolved in the prepared-input report. An ML/MM builder should not silently perform chemical structure repair.

---

# 6. ATM energy, force routing, and binding thermodynamics

## 6.1 Separate the two coordinate states from the alchemical state

Let $T_0$ and $T_1$ be two prescribed coordinate maps. For the first ABFE test, take $T_0$ as the identity map and let $T_1$ translate every ligand atom by one fixed vector $\mathbf d$. All protein atoms, waters, ions, and stationary protein caps have zero explicit displacement.

Let $V$ be the physical potential-energy contribution placed inside ATM. In the baseline, $V=U_{\mathrm{hyb}}$: all physical forces are inside. Define

$$u_0(\mathbf R)=V(T_0\mathbf R),\qquad
u_1(\mathbf R)=V(T_1\mathbf R).$$

The numeric subscripts are labels, not universal synonyms for bound and bulk. Each exported calculation must state which actual geometry they denote.

An alchemical state $k$ is then defined by

$$U_k(\mathbf R)=K(\mathbf R)+\Phi_k(u_0,u_1).$$

Here $K$ contains terms deliberately kept outside ATM, such as specified reference-coordinate restraints. $\Phi_k$ is the exact ATM energy expression at state $k$. It may include soft-core and softplus parameters; it is not necessarily a simple linear average.

**Important scope convention:** the $u_0$ and $u_1$ supplied to $\Phi_k$ are always the child-force energies. In the baseline, they equal the full physical hybrid energy at the two coordinate maps; $K$ contains only separately defined outside contributions. A later optimization that moves a physical term into $K$ must prove that term is invariant under both maps and update $V$ accordingly. The export report must state the scope explicitly.

## 6.2 Use a linear expression only for the first numerical oracle

For a synthetic fixture, use

$$\Phi_\lambda(u_0,u_1)=(1-\lambda)u_0+\lambda u_1,$$

where the dimensionless parameter $\lambda$ is between zero and one. Check zero, one, and an intermediate value such as 0.37.

For fixed translations, the coordinate-map derivative is the identity. Therefore the expected real-coordinate force is the same weighted sum of the two endpoint forces, plus the outside force. For a coordinate-dependent displacement, a Jacobian is required: the Jacobian is the matrix describing how each transformed coordinate changes when an original coordinate changes. That more general case is explicitly deferred.

The toy wrapper can use this public-API pattern:

```python
atm = openmm.ATMForce("u0 + lambda_atm*(u1-u0)")
atm.addGlobalParameter("lambda_atm", 0.37)
# Add owned child-force copies and one particle entry per final System particle.
# Force a fresh Context energy evaluation before retrieving diagnostic values.
u1_raw, u0_raw, atm_expression_energy = atm.getPerturbationEnergy(context)
```

This is an API sketch, not a complete runnable simulation. `lambda_atm` is a project-specific toy parameter, not a replacement name for AToM's production schedule. The return order and nested-force semantics are documented in [S09].

## 6.3 The safest first force-routing policy

Initially put **all physical potential-energy forces** inside ATM. This may evaluate invariant protein or solvent terms twice, but it avoids having to prove a large collection of invariance assumptions before the framework works.

Keep the thermostat/integrator, center-of-mass motion removal, disabled production barostat, and explicitly defined restraint/bias layer outside. A barostat is not an ordinary potential-energy child to be translated. Restraints are not classified by their class name: a `CustomExternalForce` can be a physical contribution or an artificial restraint depending on what it represents.

Give every original force a stable project identifier and a routing decision. Copy child forces into the ATM object and remove their originals from the outer system. Do not reuse the same owned object in two systems or leave an original behind to be counted twice.

For the AToM adapter, reserve group 1 for physical forces in the **pre-ATM export** and use `VARIABLE_FORCE_GROUP: 1`. Other outside contributions remain group 0. After AToM has moved the group, verify that every physical force appears exactly once under ATM and that all active outer forces are included in the integrator's mask. This proposal uses an inspected explicit selection path rather than AToM's default name matching. [S14]

Do not "solve" the routing issue by renaming a `PythonForce` to look like a nonbonded force. That would couple correctness to a misleading label and potentially trigger unrelated classical processing.

## 6.4 Own preparation as well as production handover

A physical hybrid system used for ordinary dynamics should have an unambiguous all-active force configuration. Keep its physical forces in group 0 in the project-owned preparation context. Only create the reserved-group export after preparation, in a separate copy.

The baseline project should implement its own small `prepare.py`: minimization, thermalization, optional separately qualified density equilibration, and fixed-volume endpoint/intermediate preparation. It should use the same validated Hamiltonian, cap handling, and restraint specification as production. It should not reimplement the replica-exchange scheduler.

Export the filenames and state contents that the pinned AToM worker expects: a final-particle topology/PDB, a physical pre-ATM system XML, and the prepared initial State. The observed worker handover uses `<basename>_0.xml`; the topology and physical system use `<basename>.pdb` and `<basename>_sys.xml`. [S15], [S17] The exact complete handover is tested in G09-G10 and repeated for RBFE in G12, including parameter overrides after loading.

This avoids feeding the group-1 physical system into an unqualified no-ATM preparation path. The alternative is a small reviewed upstream patch to unify force-group handling, with the same tests. Do not maintain both strategies initially.

Stock preparation also assigns its own timestep and some intermediate parameters. Treat those as behavior to inspect, not universal scientific defaults. Our preparation layer makes them explicit inputs instead. [S15], [S16]

## 6.5 Restraints are what make the binding question specific

There is a fundamental reason that simply comparing two translated Hamiltonians is not enough. If $T$ is a one-to-one volume-preserving transformation over the entire unrestricted configuration space, then a change of integration variables gives

$$\int e^{-U(\mathbf R)/(RT)}\,d\mathbf R
=\int e^{-U(T\mathbf R)/(RT)}\,d\mathbf R.$$

The two unrestricted partition functions are equal. A binding calculation distinguishes a binding-site domain from a bulk reference domain, normally through the coordinate convention and restraints. The ATM theory provides this restricted-state setting; it is not merely a calculation of arbitrary translated full-box energies. [S29], [S30]

Every ABFE setup must therefore record: the binding-site definition; the physical bound and bulk states; translational restraints; any orientational or conformational restraints; restraint reference atoms; and every correction needed to obtain the reported standard quantity.

A run with no defined binding domain should be described as an energy/force or transfer test, not as a validated binding free energy.

## 6.6 The standard-state conversion

For a simple separable translational restraint $W_{\mathrm{tr}}(\mathbf r)$ in homogeneous bulk, define the effective volume

$$V_{\mathrm{eff}}=\int \exp[-W_{\mathrm{tr}}(\mathbf r)/(RT)]\,d^3\mathbf r.$$

The vector $\mathbf r$ describes the ligand's relative position. This integral counts the spatial volume accessible under the restraint, with energetically penalized regions contributing less.

For a spherical flat-bottom restraint, zero inside radius $r_0$ and harmonic outside,

$$W_{\mathrm{tr}}(r)=\begin{cases}0,&r\leq r_0,\\
\tfrac12 k_r(r-r_0)^2,&r>r_0,
\end{cases}$$

where $k_r$ is a force constant in energy per length squared. Then

$$V_{\mathrm{eff}}=4\pi\int_0^\infty r^2e^{-W_{\mathrm{tr}}(r)/(RT)}\,dr.$$

It is **not** exactly $4\pi r_0^3/3$ for a finite-strength harmonic wall. Evaluate the full integral and test its hard-wall and zero-radius limits. The infinite-space form is valid only when the restraint support is effectively contained in the chosen periodic domain; otherwise use the actual domain.

For our explicitly chosen convention $\Delta F_{\mathrm{b-u}}=F_{\mathrm{bound,restr}}-F_{\mathrm{bulk,restr}}$, the simple translational correction is

$$\Delta G^\circ_{\mathrm{bind}}=\Delta F_{\mathrm{b-u}}
-RT\ln(V_{\mathrm{eff}}/V^\circ)
+\Delta G_{\mathrm{release,bound}},$$

where $V^\circ=1/(N_A C^\circ)$ is the volume per molecule at the standard concentration $C^\circ$, $N_A$ is Avogadro's constant, and $\Delta G_{\mathrm{release,bound}}$ releases any bound-state restraint not included in the intended binding-state definition. For 1 mol/L, $V^\circ$ is approximately 1.66054 nm cubed.

This simplified expression assumes the specified translational setup and no unaccounted orientational restriction. Orientational restraints require their own integral and release terms. An orientation fraction $\Omega_{\mathrm{eff}}/(8\pi^2)$ can be used only when the corresponding factorization is justified; $8\pi^2$ is the volume of unrestricted three-dimensional rigid-body orientation space. Do not automatically apply that factor to a coupled six-coordinate restraint.

Multiple binding poses and molecular symmetry likewise require an explicit state-counting convention. Do not add both a symmetry correction and a pose multiplicity factor for the same degeneracy.

## 6.7 Signs, half-legs, and the midpoint are acceptance tests

Let state 0 be bound and state 1 bulk for the following derivation. If both half-legs end at an identical intermediate of free energy $F_m$, define

$$D_0=F_m-F_0,\qquad D_1=F_m-F_1.$$

Then the bound-minus-bulk difference is

$$F_0-F_1=D_1-D_0.$$

Changing which endpoint is called 0 changes how this relates to an application's displayed result. The AToM adapter must infer its output sign from explicit state metadata and a known-answer test, not from a guess about a variable named `dgb`.

A second subtlety is that "both legs have lambda 0.5" does not prove their energy functions are identical. For zero offset, consider the two expressions

$$U_m^+=K+u_0+\tfrac12 S(u_1-u_0),$$
$$U_m^-=K+u_1+\tfrac12 S(u_0-u_1),$$

where $S$ is the soft-core perturbation function. They coincide with $K+(u_0+u_1)/2$ when the soft-core modification is inactive on the relevant perturbations. They need not coincide everywhere when it is active. Nonzero offsets require further bookkeeping. This issue follows directly from the directional energy expression and should be checked against the actual exported expression, not a schematic drawing. [S14], [S31]

**Proposed resolution:** begin with zero perturbation offset and a conventional schedule. Save raw endpoint energies. Evaluate both midpoint expressions on samples from both midpoint ensembles. If they differ, estimate the bridge free energy with adequate overlap or connect both legs to an explicitly defined common midpoint through reweighting. Do not silently assume the bridge is zero.

More generally, with $D_0=F_{m+}-F_0$, $D_1=F_{m-}-F_1$, and $\delta F_m=F_{m-}-F_{m+}$,

$$F_0-F_1=D_1-D_0-\delta F_m.$$

A full reduced-potential MBAR analysis of both directional schedules can include this connection directly if their sampled states overlap. For the first pure analytic test, use the linear function so the midpoint identity is exact. For real molecular production, qualify the actual soft-core schedule and its bridge rather than replacing ATM's physics with the toy interpolation.

## 6.8 RBFE adds a second ligand, not a new embedding definition

For fixed-displacement RBFE, one coordinate state contains A near the cavity and B in bulk. The other contains B near the cavity and A in bulk. Use opposite fixed displacements for the two complete molecules and zero displacement for the protein and caps.

Keep the same cavity atoms, cap convention, model, embedding, force-field parameters, temperature, and state definitions across a congeneric series whenever comparing a network or ABFE/RBFE closure. Different cavity regions for different ligands define different receptor models and can destroy the intended cancellation.

The target relative quantity is

$$\Delta\Delta G_{A\rightarrow B}=\Delta G^\circ_{\mathrm{bind}}(B)
-\Delta G^\circ_{\mathrm{bind}}(A).$$

A negative value means B binds more favorably under this convention. AToM's actual endpoint ordering is recorded separately. Alignment or bulk restraints may help sampling, but they must either cancel by a demonstrated symmetry or appear in the thermodynamic accounting. Similar-looking restraints are not proof of cancellation.

Do not add atom-based common/variable-region coordinate swapping in the first implementation. That is a later coordinate-map plugin with its own Jacobian, constraints, and link-parent tests.

# 7. Repository design and interfaces to implement

## 7.1 Keep the project-owned layer small

The following paths describe the **proposed repository**. They are not files implemented during this review. The objective is an auditable package, not a large framework that duplicates OpenMM, MACE, or AToM.

```text
atm-mlmm-p0/
  pyproject.toml
  README.md
  environment/
    cpu.in
    gpu.in
    locks/
  src/atm_mlmm/
    schema.py                 # Validated configuration and typed records
    identity.py               # Stable atom IDs and index-map checks
    partition.py              # Fixed ML selection and boundary enumeration
    hybrid.py                 # OpenMM-ML assembly and retained-MM extraction
    ledger.py                 # Force, parameter, constraint, and mass audit
    model_reference.py        # Independent native-model evaluation
    geometry.py               # Transforms, PBC separation, graph checks
    routing.py                # Explicit force ownership and group membership
    endpoints.py              # Direct-vs-ATM energy and force comparisons
    derivatives.py            # Finite differences and analytic cap oracle
    restraints.py             # Restraint definitions and volume integration
    schedule.py               # Exact state expressions and unit conversion
    prepare.py                # Project-owned physical and ATM preparation
    atom_adapter.py           # Narrow, pinned AToM production handover
    observables.py            # Raw energies, state identity, audit records
    analysis.py               # Reduced potentials, MBAR, UWHAM cross-check
    persistence.py            # Bundles, manifests, checkpoint/State handling
    report.py                 # Machine-readable and human-readable reports
    cli.py                    # Thin command-line entry points
  tests/
    unit/
    integration/
    workflow/
    sampling/
  fixtures/
    analytic/
    one_cut_alkane/
    capped_alanine/
    fragment_ligand/
    solvated_fragment/
    protein_one_ligand/
    protein_two_ligands/
  docs/
    hamiltonian.md
    source-audit.md
    qualification.md
    decisions/
```

Modules may be combined when genuinely small. Keep the responsibilities separate even if the file count changes. Avoid a single notebook in which atom selection, model loading, force modification, and free-energy analysis depend on execution order.

## 7.2 Shared data records

Implement frozen configuration records, with validation at construction. Arrays should be copied or treated as read-only where practical; OpenMM objects themselves require careful ownership because they are mutable.

**`AtomIdentity`:** original chain ID, residue ID, insertion code, residue name, atom name, element, and a stable per-input unique ID. Detect duplicates instead of trusting PDB serial numbers.

**`PartitionSpec`:** sorted unique real ML IDs, ligand-A IDs, optional ligand-B IDs, protein ML IDs, boundary policy, expected formal charges of each capped component, and allowed chemistry.

**`ModelSpec`:** backend, checkpoint path, SHA-256, model-output convention, intended precision/device, locality class, supported elements, and recorded training-domain limitations. Extract the actual cutoff from the model and record it; do not use a user-specified cutoff to change a pretrained Hamiltonian accidentally.

**`LinkRecord`:** ML parent ID/index, MM parent ID/index, cap particle index, cap model-input index, virtual-site type, and cap distance in nm.

**`PhysicalBundle`:** `system`, `topology`, `positions_nm`, `box_nm`, atom map, partition, links, retained constraints, model manifest, and force ledger. `positions_nm` has shape `(N, 3)` for the final $N$ particles, including derived sites.

**`TransformSpec`:** one displacement vector per final particle for state 0 and state 1; the endpoint descriptions; and a declaration that this first implementation uses fixed translations. Store nm internally.

**`ThermodynamicSpec`:** temperature, ensemble, bound-state definition, restraint definitions, schedule, endpoint sign convention, standard concentration, and required corrections.

**`ValidationReport`:** test ID, fixture hash, environment hash, measured errors, thresholds, pass/fail status, and paths to reproducible failure data. "Passed" without the tested configuration's identity is not a useful report.

## 7.3 Public function contracts

The names below are proposed project interfaces, not upstream functions:

```python
resolve_partition(topology, spec: PartitionSpec) -> ResolvedPartition
build_hybrid(mm: PhysicalBundle, partition: ResolvedPartition,
             model: ModelSpec) -> PhysicalBundle
build_transforms(bundle: PhysicalBundle, spec: TransformSpec) -> CoordinateMaps
inspect_ledger(original: PhysicalBundle, mixed: PhysicalBundle) -> ForceLedger
validate_geometry(bundle: PhysicalBundle, maps: CoordinateMaps) -> ValidationReport
compare_endpoints(bundle: PhysicalBundle, maps: CoordinateMaps,
                  frames, platform_spec) -> ValidationReport
check_real_atom_derivatives(bundle: PhysicalBundle, frames,
                            atom_ids, step_sizes_nm) -> ValidationReport
prepare_bundle(bundle: PhysicalBundle, thermo: ThermodynamicSpec,
               run_spec) -> PreparedBundle
export_atom(prepared: PreparedBundle, thermo: ThermodynamicSpec,
            directory) -> AtomRunBundle
reconstruct_reduced_potentials(records, thermo: ThermodynamicSpec) -> ReducedData
analyze_binding(data: ReducedData, thermo: ThermodynamicSpec) -> BindingResult
```

Define `ResolvedPartition`, `CoordinateMaps`, `ForceLedger`, `PreparedBundle`, `AtomRunBundle`, `ReducedData`, and `BindingResult` in `schema.py` alongside the records above. Their fields must carry the input identities and units rather than just arrays detached from provenance.

`BindingResult` must separate the raw restrained difference, midpoint bridge, standard-state term, other restraint releases, final binding result, statistical uncertainty, and unresolved physical limitations. No function should silently combine an uncomputed correction with zero.

## 7.4 The mixed-system call

For a trusted local checkpoint loaded through the generic MACE path, the intended call has this form:

```python
potential = MLPotential("mace", modelPath=str(model.checkpoint_path))
info = potential.createMixedSystem(
    mm.topology,
    mm.system,
    resolved.real_ml_indices,
    embedding="mechanical",
    returnInfo=True,
    removeConstraints=True,
    interpolate=False,
    forceGroup=0,
    mlLongRange=False,
    precision="double",
    returnEnergyType="energy",
    device="cpu",
)
mixed_system = info["system"]
mixed_topology = info["topology"]
old_to_new = info["oldToNew"]
```

This is a proposed assembly sketch, to be tested in G04-G05. It does not construct the new position array or perform validation by itself.

For a named pretrained model whose long-range classification is already known to OpenMM-ML, **omit** `mlLongRange`; the inspected embedding rejects an explicit override for such a model. For a generic local checkpoint, explicitly setting it is appropriate only after verifying the checkpoint is local. The precise public return keys and generic options are documented in [S06], [S07].

Create the final position array using `oldToNew`, populate real positions, initialize derived sites, and ask the context to compute virtual sites before any energy comparison. Derive the set of new caps from the topology/System difference and inspect the actual virtual-site definitions. Do not infer cap identity solely from residue names.

## 7.5 Configuration: separate project units from AToM units

The project schema should use unit-bearing names:

```yaml
schema_version: 1
calculation: abfe
embedding: mechanical
model:
  backend: mace
  asset_id: mace_off23_small_approved
  energy_output: energy
  precision: double
  device: cpu
  locality: local
partition:
  fixed_membership: true
  ligand_policy: complete_molecule
  protein_boundary_policy: neutral_sidechain_single_cut
  reject_multiple_caps_per_mm_parent: true
numerics:
  temperature_K: 300.0
  timestep_fs: 0.5
  friction_per_ps: 1.0
  production_ensemble: NVT
  integrator: LangevinMiddle
  hydrogen_mass_repartitioning: false
  multiple_time_steps: false
validation:
  require_raw_endpoint_records: true
  require_midpoint_bridge_check: true
  require_independent_model_reference: true
```

This fragment is a **schema example**, not a runnable molecular input: structure files, concrete atom identities, the approved asset manifest, box, displacement, and restraints must be supplied by fixture/target configuration and resolved before export.

At the adapter boundary, convert to AToM's actual keys. For example, 0.5 fs becomes `TIME_STEP: 0.0005`, because that field is interpreted in ps. AToM's `DISPLACEMENT` is in Angstrom, whereas the project stores nm. Use `LIGAND_ATOMS` for the one-ligand route and `LIGAND1_ATOMS`/`LIGAND2_ATOMS` for dual-ligand RBFE. The exact names are version-sensitive adapter knowledge, not names to scatter throughout the project. [S14]

The adapter must reject mismatched schedule lengths, duplicated or missing state IDs, nonfinite values, accidental nested ATM objects, and a force group that conflicts with an already assigned group.

## 7.6 Unsupported inputs fail closed

The initial builder should stop on an unknown element, nonneutral selected chemical fragment, unrecognized force class, charge offsets, missing parent, incomplete ligand selection, ligand boundary bond, duplicate atom identity, disconnected coordinate metadata, wrong checkpoint hash, or unsupported periodic cell.

Every refusal must state the unsupported feature and the relevant atom/force/model identifier. "Model failed" is not enough information for a colleague to diagnose a chemical or indexing problem.

---

# 8. Numerical validation methods

## 8.1 Three independent levels of comparison

First compare an analytic expression with a direct OpenMM force. Next compare that direct system with ATM evaluation of the same coordinates and independently transformed coordinates. Finally compare the native ML model with the ML contribution inside the mixed system and ATM.

Do not use the same transformation helper to generate both the alleged reference and the tested transformation without another check. A shared sign error would then pass. Tiny fixtures should have hand-written expected transformed coordinates and labeled atoms.

The full test should also ask: does moving the ligand change forces on the protein ML atoms in the bound state? An implementation that evaluates ligand and cavity as separate graphs can return smooth ligand forces while completely missing their interaction.

## 8.2 A trustworthy analytic callback

Use an explicitly differentiated potential such as

$$E=\tfrac12\sum_i k_i|\mathbf r_i-\mathbf c_i|^2,$$

with forces

$$\mathbf F_i=-k_i(\mathbf r_i-\mathbf c_i).$$

Here $k_i$ is an assigned force constant and $\mathbf c_i$ is an assigned center. Add a simple interparticle term in another fixture to make cross-particle force propagation observable. The callback must be a top-level importable function or a demonstrably serializable callable, not a notebook-local lambda.

PythonForce returns energy and forces in OpenMM's units when plain numerical arrays are used. Its selected-particle array order follows the selected indices. Both the unit convention and pickle-based serialization are documented in [S10]. Test a deliberately permuted selection, for example `[2, 0]`, so assuming sorted/global array order cannot pass accidentally.

Independently differentiate every copied demonstration formula. Documentation examples are not a replacement for the analytic oracle.

## 8.3 Force finite differences

For one Cartesian coordinate $x_i$, use

$$F_i^{\mathrm{FD}}(h)=-\frac{U(x_i+h)-U(x_i-h)}{2h}.$$

The quantity $h$ is a small coordinate displacement. Compare several values rather than one: proposed initial values are $10^{-3}$, $10^{-4}$, and $10^{-5}$ nm. Too large a step causes truncation error; too small a step amplifies floating-point subtraction noise. A good result has a consistent interval of agreement.

Probe a ligand atom, a cavity atom, both real parents of each boundary type, an MM atom near the cavity, and a solvent atom. Repeat at both raw endpoint geometries and several intermediate alchemical states. Recompute virtual sites after every perturbation and restore the entire saved state afterward.

Do not compare a cap particle's apparent force slot as though it were an independent physical degree of freedom. The decisive comparison is the derivative with respect to real coordinates.

## 8.4 Periodicity and graph tests

For each endpoint, record minimum distances under the actual periodic box between cavity-plus-caps and bulk ligand, between the two ligands in RBFE, and between every component and relevant images of other components. Check the full protein as well: being outside the ML cutoff does not guarantee a true bulk-solvent placement outside the MM protein.

For an orthorhombic box, validate a simple minimum-image implementation against explicit nearby image enumeration. For triclinic support, do not assume rounding fractional coordinates always produces the globally shortest image for an arbitrary cell; define the admitted cell convention and test an appropriate image search.

Also examine the graph produced by the actual model neighbor routine. A distance validator and a backend graph validator can catch each other's assumptions. Include cap nodes, periodic shifts, self-image edges, and every selected real atom.

A proposed setup guard is a minimum separated-component distance at least 0.2 nm beyond the actual neighbor cutoff, followed by checks along pilot trajectories. This is an engineering safety buffer, not a universal physical threshold. Restraint excursions, side-chain motion, and box changes must be considered. A single initial distance is not a production guarantee.

## 8.5 Precision and thresholds

Use Reference/CPU analytic tests first, then double-precision model tests, then the intended GPU production precision. OpenMM precision and the model tensor precision are separate settings; record both.

Proposed initial tolerances are listed in Section 11. Calibrate them against direct repeated evaluations and precision comparisons before freezing them. A tolerance may not be enlarged merely to make a failing implementation pass.

Use absolute errors and error relative to a meaningful force scale. A relative energy error divided by the enormous total energy of a solvated protein can conceal a binding-scale discrepancy. Examine perturbation energies and local forces explicitly.

## 8.6 Prove that the tests can detect mistakes

Deliberately inject each of the following into a toy copy: omit the ML force from ATM; translate the wrong atom; reverse the displacement; remove the cap's force contribution; apply the nm/Angstrom conversion incorrectly; fail to update the box; and keep a duplicate child force outside ATM.

The corresponding tests must fail for the expected reason. This adversarial check is particularly important because several errors can produce a trajectory that looks stable.

---

# 9. Model admissibility and difficult counterfactual geometries

## 9.1 Why ordinary endpoint stability is insufficient

ATM evaluates two geometries at each configuration. A favorable weighted configuration can have a strongly compressed or otherwise unusual alternate geometry. Thus ordinary stable ML/MM dynamics at the bound endpoint does not prove that the model is safe throughout the ATM path.

The soft-core function acts on an energy difference that must already have been computed. It cannot make an undefined model evaluation meaningful. It also does not automatically cure a neural network that predicts an unphysical, strongly negative attraction at very short distance.

This is an implementation/sampling gate even before a full chemical-accuracy study. A model that fails to define a finite usable potential on encountered states cannot be accepted merely because Project 0 is "only infrastructure."

## 9.2 The required scan set

Before solvated ATM dynamics, construct controlled scans of a ligand approaching a capped cavity fragment. Include typical contacts, modest compression, deliberate severe overlap for failure characterization, separation through the cutoff, and rotations near a cap. Do not drive all atoms to coincident coordinates and then demand that every model support that singular input; establish and document the admitted domain.

For each evaluated point store raw ML energy, total hybrid energy, maximum real-atom force, graph edges, and whether both energy and forces are finite. Inspect the repulsive direction rather than merely asking whether the number is large.

Repeat on snapshots from short ATM pilots, including the less favorable coordinate state. A counterfactual configuration should not disappear from the diagnostic just because its current statistical weight is small.

## 9.3 What to do when the model fails

Stop the run, save the failing coordinates and both transformed geometries, and reproduce the problem in the smallest fixture. Determine whether the issue is units, indices, graph construction, cap geometry, numerical precision, or the learned potential itself.

If it is a model-domain failure, the scientifically legitimate responses are to choose a suitable model, add explicitly designed training data, or define a smooth additional interaction as part of a new Hamiltonian and rerun its validation. A residual repulsive term is not automatically harmless: its energy and derivative must be included at every state and its effect on the intended physical endpoints must be assessed.

Do not clip forces independently of energies, replace NaN with zero, reject inconvenient frames from the estimator, or switch models according to whether a ligand looks bound. These actions can destroy the sampled equilibrium distribution.

## 9.4 What reference data are useful later

Retain the original plan's conclusion that arbitrary 10-20 Angstrom separated complexes are not required merely to teach a strictly local architecture to disconnect. A more useful future reference set contains ligand conformers, precisely capped protein fragments, bound/contact configurations, and the boundary/contact distortions identified by qualification.

However, geometric disconnection is not an accuracy guarantee. Training-domain coverage, cutoff continuity, and the physical long-range approximation still require separate assessment. Reference fragment charges, multiplicities, and cap conventions must match the deployed model definition. Split validation data by configuration source or trajectory family to avoid overstating accuracy through nearly duplicated frames.

Fine-tuning is a later scientific experiment unless the initial model fails the basic admissibility gate. Do not begin an expensive reference-data campaign before locating the actual failure mechanism.

---

# 10. Ordered implementation work packages

## 10.1 Dependency order and review discipline

The recommended execution order is:

```text
G00 environment and evidence capture
  -> G01 immutable MM input, atom identity, and force inventory
  -> G02 analytic PythonForce inside native ATM
  -> G03 explicit AToM routing and integration-mask test
  -> G04 one link boundary with analytic forces
  -> G05 one real local ML model
  -> G06 periodic embedding and nonbonded ledger
  -> G07 combined capped cavity + transferred ligand
  -> G08 known-answer thermodynamics and estimators
  -> G09 solvated fragment and complete preparation/export
  -> G10 fresh-process restart and small replica exchange
  -> G11 one protein ABFE qualification
  -> G12 dual-ligand RBFE qualification
  -> G13 performance, documentation, and release decision
```

G08's analytic analysis can be developed in parallel with G04-G07 by a different colleague; it depends primarily on G02-G03, not on protein chemistry. Keep the acceptance order: no molecular binding claim before G08 passes. Likewise, topology tests can proceed while a model license is being resolved, but that does not qualify the model.

Each work package follows one review cycle: write the test, show that the absent or deliberately broken behavior fails, implement the minimum change, rerun the test, save the evidence, and commit the reviewed result. Do not merge a later stage to obscure a failing earlier gate.

## G00. Establish the candidate environment and provenance capture

**Question:** Can the specified packages be installed, imported, and identified unambiguously on the target machine?

**Files:** `environment/cpu.in`, `environment/gpu.in`, `schema.py`, `persistence.py`, `tests/unit/test_environment.py`.

- [ ] Write `test_required_apis_exist`, checking `ATMForce`, `PythonForce`, selected-particle support, XML serialization, and the mixed-system API. Test reported package versions and resolved source identities separately.
- [ ] Run the CPU installation recipe and `python -m pip check`. Record all output, including warnings. Do not suppress a failed dependency requirement by forcing `--no-deps`.
- [ ] Implement `capture_environment()` to record Python, package/build versions, Git revisions, platform properties, operating system, numerical-library versions, and source/weight hashes. Store an explicit "not qualified" state until the later gates pass.
- [ ] Ingest one trusted model asset only after checking its permitted use. Store its digest and license reference. An absent asset or wrong digest must stop model tests with a specific error.
- [ ] Run `python -m openmm.testInstallation`, then `pytest tests/unit/test_environment.py -v`. Repeat for the GPU environment when one is available.

**Deliverable:** resolved environment records and a source/model manifest. The environment may be called installed if these checks pass; it may not yet be called ATM-ML/MM compatible.

**Pass:** required APIs import, dependencies are consistent, provenance is complete, and the platform test succeeds. **Failure action:** identify the incompatible package/build before chemistry or simulation. Do not downgrade OpenMM below the declared OpenMM-ML requirement to imitate an old tutorial.

## G01. Make atom identity and the original MM system auditable

**Question:** Do we know exactly which real atom, parameter, and force is being modified?

**Files:** `identity.py`, `partition.py`, `ledger.py`, `tests/unit/test_identity.py`, `tests/unit/test_partition.py`, `tests/unit/test_force_inventory.py`.

- [ ] Create tiny topologies with duplicate residue numbers on different chains, insertion codes, noncontiguous ligand indices, and reordered atoms. Write tests that distinguish them correctly and reject ambiguous selections.
- [ ] Implement `resolve_partition()` from chemical connectivity and stable IDs. Require complete ligands and enumerate every boundary edge. Verify that selected hydrogen atoms follow the intended fragment.
- [ ] Implement `inspect_force_inventory()` and constraint/mass capture before any ML conversion. The output includes force class/name/group, particle parameters, exceptions, exclusions, bonded terms, box settings, and offsets.
- [ ] Test a deliberately malformed system: particle/topology count mismatch, incomplete ligand, forbidden ring cut, missing bond, unsupported force type, and two cuts to one MM parent. Each must stop before building a context.
- [ ] Save a checked-in all-MM fixture, high-precision coordinates, and expected inventory. Run `pytest tests/unit/test_identity.py tests/unit/test_partition.py tests/unit/test_force_inventory.py -v`.

**Deliverable:** an immutable MM fixture and readable `atoms.tsv`/`forces.json`/`constraints.json` records.

**Pass:** every selection is unique, reproducible, and invariant to permitted input reordering; the inventory reconstructs the original system's identity. **Failure action:** repair selection or preparation logic. No model should be asked to compensate for uncertain connectivity.

## G02. Prove analytic PythonForce composition with native ATM

**Question:** Does ATM evaluate the supplied Python potential at the intended two geometries and return the correct derivatives?

**Files:** `endpoints.py`, `derivatives.py`, `fixtures/analytic/`, `tests/integration/test_pythonforce_atm.py`.

- [ ] Write an importable analytic callback with an independently differentiated energy. Include three particles, a nontrivial subset order, and a coupling term between two selected particles.
- [ ] Write hand-calculated coordinate expectations for zero displacement, a nonzero displacement, and opposite displacements. Directly evaluate the physical system at each expected geometry in independent contexts.
- [ ] Construct the linear ATM test at lambda 0, 0.37, and 1. Unpack `(u1, u0, energy)` explicitly. Compare raw child energies, total expression energy, and real-particle forces.
- [ ] Add an outside harmonic restraint. Verify that raw child energies exclude it and total system energy includes it exactly once. Check the weighted-force identity and finite differences.
- [ ] Serialize and reload the system in a fresh Python process. Deliberately introduce reversed tuple unpacking, a wrong subset map, and a duplicate force to prove the tests reject them.

Run `pytest tests/integration/test_pythonforce_atm.py -v` first on Reference and then on the admitted CPU/GPU platforms.

**Deliverable:** a very small reproducer independent of MACE, solvent, and protein setup.

**Pass:** analytical/direct/ATM energies and forces agree within the analytic tolerances, including after a fresh-process reload. **Failure action:** stop at the OpenMM composition layer and prepare an upstream reproducer. Do not add link atoms yet.

## G03. Prove AToM routes and integrates the intended forces

**Question:** Does the pinned production path preserve the already-correct analytic system?

**Files:** `routing.py`, `atom_adapter.py`, `tests/workflow/test_atom_force_routing.py`, `tests/workflow/test_active_force_groups.py`.

- [ ] Use the G02 fixture to construct the physical pre-ATM export. Give all physical potential forces the reserved group and keep the independently specified restraint outside.
- [ ] Write `test_default_route_does_not_qualify_pythonforce` as a regression demonstration: the default stock route must not be accepted as our cavity-inclusive configuration.
- [ ] Implement the explicit group-based handover. Enumerate every force recursively after construction and verify ownership exactly once. Check that no physical force is left in an inactive outer group.
- [ ] Compare full forces with the forces selected by the actual integrator's integration mask. Make an omitted group's force deliberately large in the fixture so an omission cannot hide in tolerance.
- [ ] Test both ABFE and RBFE construction classes, with `INTEGRATOR: LangevinMiddle` and the explicit converted timestep. Test ordinary no-ATM preparation separately using the project's group-0 preparation clone.

Run `pytest tests/workflow/test_atom_force_routing.py tests/workflow/test_active_force_groups.py -v`.

**Deliverable:** the smallest version-pinned AToM adapter and its force-routing report. The adapter is not allowed to select by misleading force names.

**Pass:** AToM construction matches the native-ATM oracle and all intended forces contribute to integration in every admitted preparation/production stage. **Failure action:** first change the adapter; if an upstream change is needed, keep it focused on routing and submit the reproducer. Do not fork the alchemical method.

## G04. Validate one link boundary without a real neural model

**Question:** Are cap positions, force transfer, and boundary bookkeeping correct independently of chemical model quality?

**Files:** `hybrid.py`, `derivatives.py`, `ledger.py`, `fixtures/one_cut_alkane/`, `tests/integration/test_link_geometry.py`, `tests/integration/test_boundary_ledger.py`.

- [ ] Construct a propane-like fixture with two connected carbons and their hydrogens selected as ML, leaving the final methyl group classical. The capped selected fragment then has a simple closed valence. Also create a small dedicated bonded-term graph fixture for each removal predicate.
- [ ] Use a registered test potential or analytic model substitute to exercise OpenMM-ML's real link construction without loading MACE. Give the cap a known harmonic energy whose derivative with respect to both parents is available from Section 3.
- [ ] Test cap mass, MM nonbonded parameters, parent identities, distance, particle count, and mapping. Verify the actual 1.8 appended-site behavior while also testing a synthetic nonidentity map in the project mapping utility.
- [ ] Independently enumerate which fixture terms should remain under the documented convention. Compare each term, not just the total count. Test constraints separately.
- [ ] Perturb each parent along and perpendicular to the boundary bond; recompute sites; compare analytic and finite-difference real-atom forces. Reload and repeat. Add the stationary boundary to the G02 ATM fixture and repeat once inside ATM.

Run `pytest tests/integration/test_link_geometry.py tests/integration/test_boundary_ledger.py -v`.

**Deliverable:** a cap-force oracle, a term-by-term boundary ledger, and a minimal serialized capped system.

**Pass:** the cap is constructed as specified, exactly one force redistribution is observed on real atoms, and every boundary term has a justified status. **Failure action:** isolate virtual-site, cap geometry, or term-removal behavior before involving a learned potential.

## G05. Qualify one actual local model and its OpenMM adapter

**Question:** Does the selected checkpoint produce the same energy/forces through its native interface and through OpenMM?

**Files:** `model_reference.py`, `hybrid.py`, `fixtures/capped_alanine/`, `tests/integration/test_model_adapter.py`, `tests/integration/test_locality.py`, `tests/integration/test_model_domain.py`.

- [ ] Evaluate a neutral ligand, a capped side-chain fragment, and a contacting joint complex directly with the trusted model. Store exact model input order, elements, coordinates, box, output convention, and precision.
- [ ] Build the corresponding OpenMM-ML force. Compare energies and selected-atom forces, accounting explicitly for the conversion convention. Check the real boundary-parent forces after cap redistribution separately from raw native cap forces.
- [ ] Test translations, joint rotations, and consistent atom permutations. Do not demand rotational invariance while holding an anisotropic periodic box fixed under a rotation that changes its physical geometry; rotate the complete admitted nonperiodic fixture or box consistently.
- [ ] Separate the components beyond all neighbor edges. Compare joint energy and forces with separate component evaluations using the same periodic convention. Test that a contacting joint graph does not accidentally equal a forced separate-batch calculation.
- [ ] Run the contact/cutoff/overlap scans from Section 9. Test fresh-process serialization on CPU before allocating multiworker GPU jobs.

Run `pytest tests/integration/test_model_adapter.py tests/integration/test_locality.py tests/integration/test_model_domain.py -v`.

**Deliverable:** a checkpoint-specific compatibility card and reference snapshots.

**Pass:** native/adapter agreement, correct locality behavior, finite admitted-domain energies/forces, and successful serialization. **Failure action:** distinguish model-domain problems from adapter problems. Do not fine-tune a model to fix a unit conversion or missing graph edge.

## G06. Audit periodic embedding and nonbonded bookkeeping

**Question:** Does the mixed system keep and remove exactly the declared periodic interactions?

**Files:** `ledger.py`, `geometry.py`, `tests/integration/test_mechanical_pme.py`, `tests/integration/test_periodic_geometry.py`, `tests/integration/test_masked_interactions.py`.

- [ ] Begin with a tiny periodic charged fixture, no protein, and an analytic ML substitute. Make the expected short-range exception changes inspectable. Compare original and retained-MM systems at identical coordinates.
- [ ] Verify ML-MM Coulomb and Lennard-Jones interactions survive; cap MM interactions do not appear; selected ML-ML exceptions are as specified; and the periodic electrostatic convention is the one actually being used.
- [ ] Implement the charge-mask cross-energy diagnostic and validate it against direct quadratic scaling of the complete electrostatic fixture. Include nonneutral subsets so a hidden neutralizing-background assumption is tested.
- [ ] Test whole-molecule wrapping, box changes, a boundary near a box face, and a ligand near a periodic copy of the cavity. Add cases in which a naive nonperiodic distance would incorrectly pass. Include energy/force scans at the image-choice seams described in Section 4.6.
- [ ] Compare the independent image-distance check with actual model neighbor edges. Record and test the chosen Lennard-Jones dispersion-correction policy.

Run `pytest tests/integration/test_mechanical_pme.py tests/integration/test_periodic_geometry.py tests/integration/test_masked_interactions.py -v`.

**Deliverable:** an exact periodic interaction report and rejection examples for unsafe geometry.

**Pass:** the retained Hamiltonian is numerically reproducible, cross-region interactions are present, and the validator catches periodic reconnection. **Failure action:** fix the bookkeeping or narrow the supported cell/force configuration. Do not add a PME correction until identifying the precise interaction to correct.

## G07. Combine a capped cavity fragment and transferred ligand

**Question:** Does the full intended physical model work under ATM before solvent and workflow complexity are added?

**Files:** `fixtures/fragment_ligand/`, `endpoints.py`, `tests/integration/test_joint_hybrid_atm.py`.

- [ ] Assemble one stationary capped neutral fragment and one complete neutral ligand in a nonperiodic fixture. Use the real checkpoint and the already-qualified cap builder.
- [ ] Evaluate a close-contact geometry and a separated geometry directly. Build native ATM using all physical force objects, then build the same calculation through the AToM adapter.
- [ ] Compare energies and real-parent forces across all three routes at both endpoints and at intermediate parameters. Include force on an MM boundary parent: that is where missing cap force transfer can be hidden.
- [ ] Repeat the graph-disconnection/additivity checks in the actual combined system. Verify that only the intended ligand atoms move in the artificial coordinate map.
- [ ] Test a periodic version only after the nonperiodic fixture passes. Archive both raw coordinate states on any failure, together with the force ledger.

Run `pytest tests/integration/test_joint_hybrid_atm.py -v`.

**Deliverable:** the first genuinely cavity-inclusive, capped ML/MM ATM reproducer, still small enough for a reviewer to understand completely.

**Pass:** direct, native-ATM, and AToM-built energy/force results agree; geometry and graph membership are correct. **Failure action:** return to the failing lower-level gate. No protein preparation is justified until this combination passes.

## G08. Validate thermodynamics, sign, midpoint connection, and estimators

**Question:** Can the complete sampling/analysis logic recover a known nonzero free energy, not just produce stable energies?

**Files:** `restraints.py`, `schedule.py`, `analysis.py`, `fixtures/analytic/`, `tests/sampling/test_analytic_free_energy.py`, `tests/unit/test_restraint_volume.py`, `tests/unit/test_schedule.py`.

Use an exactly solvable translated harmonic system. In the displaced dimension, set

$$u_0(x)=\tfrac12 kx^2,\qquad u_1(x)=\tfrac12 k(x+d)^2,\qquad K(x)=\tfrac12 k_r x^2.$$

Here $x$ is a coordinate, $d$ a fixed displacement, $k$ the physical force constant, and $k_r$ an outside-restraint constant. Other dimensions can have identical confining terms that cancel from the difference. Gaussian integration gives

$$F_1-F_0=\frac12\frac{kk_r}{k+k_r}d^2.$$

For $k=100$ and $k_r=50$ kJ/mol/nm squared, with $d=0.3$ nm, the answer is **+1.5 kJ/mol**. Setting $k_r=0$ gives zero, exposing the unrestricted-translation issue. Reversing the reported difference must give -1.5 kJ/mol.

For linear interpolation, the full known curve is

$$F_\lambda-F_0=\tfrac12\lambda k d^2-
\frac{\lambda^2k^2d^2}{2(k+k_r)}.$$

- [ ] Test the formulas through independent numerical quadrature. Generate independent analytic samples before testing MD-generated samples, so estimator failures are distinguishable from sampling failures.
- [ ] Reconstruct the complete reduced-potential matrix and compare PyMBAR with the pinned AToM Python UWHAM implementation on a compatible schedule. Record sign conversion explicitly.
- [ ] Test all schedule values against the actual context energy expression. Include raw endpoint energies, outside terms, energy offsets, and a deliberate schedule-unit error.
- [ ] Create a synthetic soft-core example whose two nominal midpoints differ. The analysis must detect the difference and recover the correct result when the bridge is included. A test that only uses inactive soft-core would not protect this case.
- [ ] Test the effective-volume integral, the standard-state sign, a finite-wall correction, and a deliberately missing orientation/release specification. An uncomputed required correction must prevent a final ABFE label.

Run `pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_restraint_volume.py tests/unit/test_schedule.py -v`.

**Deliverable:** a known-answer thermodynamic suite and a documented sign/correction convention.

**Pass:** deterministic formulas and quadrature agree; sampled estimates agree within predeclared uncertainty and absolute-error criteria; two independent analyses agree on identical inputs. **Failure action:** fix the state definition or estimator before analyzing molecular binding.

## G09. Add explicit solvent and complete preparation/export

**Question:** Does the validated small molecular system remain correct with solvent, PME, preparation, and the actual worker input format?

**Files:** `fixtures/solvated_fragment/`, `prepare.py`, `persistence.py`, `atom_adapter.py`, `tests/workflow/test_solvated_handover.py`.

- [ ] Solvate the capped-fragment/ligand fixture with the fixed MM convention. Choose a box with two admissible ligand locations and verify the bulk site is clear of the entire solute, including periodic images.
- [ ] Prepare with the project-owned all-active physical context: minimize, thermalize conservatively, and run short fixed-volume dynamics. Begin at 0.5 fs. Record maximum forces, cap geometry, constraints, and both mapped endpoint energies.
- [ ] Construct the actual alchemical schedule and initial states using the validated expression evaluator. Make the initial positions in the PDB safe for the worker's preliminary evaluation as well as the higher-precision State used afterward.
- [ ] Export `<basename>.pdb`, `<basename>_sys.xml`, `<basename>_0.xml`, configuration, and manifests. Reload in the pinned AToM construction/worker path, then compare coordinates, box, constraints, active force groups, parameters, energies, and forces before advancing dynamics.
- [ ] Run a short multiwindow calculation without claiming convergence. Reevaluate saved snapshots at all states; check the midpoint connection, periodic separation, and alternate-geometry model domain.

Run `pytest tests/workflow/test_solvated_handover.py -v`, followed by the proposed CLI `atm-mlmm pilot fixture.yaml --output run-g09` once that CLI is implemented.

**Deliverable:** a fully self-contained solvated toy run bundle and an actual worker handover test.

**Pass:** preparation and production use the same intended Hamiltonian, all initial states are well defined, direct/worker results agree, and no cap/PBC/model-domain failures occur. **Failure action:** reduce to G06 or G07 before adding a real protein.

## G10. Fresh-process restart and small replica exchange

**Question:** Can the validated system survive process boundaries and parameter exchanges without changing its meaning?

**Files:** `persistence.py`, `observables.py`, `tests/workflow/test_fresh_process.py`, `tests/workflow/test_restart.py`, `tests/workflow/test_replica_exchange.py`.

- [ ] Save system, State, and checkpoint artifacts. Reload the system plus State in a new process with network disabled. Move or hide the source cache to expose unrecorded model dependencies.
- [ ] Compare pre/post-load energy and real-particle forces at fixed coordinates. Test a checkpoint continuation on the same admitted platform and a portable State continuation separately.
- [ ] Run two thermodynamic states through the real worker mechanism. After every parameter change, verify context parameters and independent cross-state energies. Test state-label swaps rather than assuming file-directory names still identify thermodynamic states.
- [ ] Check exchange acceptance against the independently computed reduced-energy difference for the proposed swap. At one temperature it should use the same Hamiltonians as the integrator. Reject stale energies or mismatched state IDs.
- [ ] Test process interruption, restart, duplicate-output prevention, and GPU-device identity. When multiple GPUs are used, ensure the OpenMM context and the callback's tensors reside on the intended worker device, not all on device zero.

Run `pytest tests/workflow/test_fresh_process.py tests/workflow/test_restart.py tests/workflow/test_replica_exchange.py -v`. Repeat GPU-marked tests on the production hardware.

**Deliverable:** restart and small replica-exchange evidence on the solvated fixture, before protein-scale expense.

**Pass:** recreated states reproduce observables, exchange uses the intended energies, no unknown model download occurs, and logs preserve state/replica identities across restart. **Failure action:** isolate serialization, worker placement, or schedule propagation. Do not expand the number of workers to hide a reproducible failure.

## G11. First protein and one-ligand ABFE qualification

**Question:** Does the platform survive realistic topology and multiple protein cuts while retaining the validated thermodynamic definition?

**Files:** `fixtures/protein_one_ligand/`, `tests/workflow/test_protein_abfe.py`, target-specific input/partition/thermodynamic manifests.

Use one structurally inspected, ordinary noncovalent complex. A T4 lysozyme L99A fixture, as proposed in the original note, is a candidate rather than a requirement. Select only a few neutral side chains initially. Do not add a difficult polar pocket merely to make the first demonstration more ambitious.

- [ ] Prepare and archive the original MM input independently. Review ligand chemistry, cap fragments, and every boundary bond before building the mixed system.
- [ ] Build three controls: all-MM, ligand-only ML/MM, and cavity-inclusive ML/MM. Match constraints for exact numerical comparisons; document any intentional model-specific ensemble differences in scientific comparisons.
- [ ] Run the complete preflight on representative frames. Test at least one force component on each link-parent pair, not just one convenient boundary in the protein.
- [ ] Perform staged pilots, beginning with short single-state runs, then a short schedule, then multiple independently seeded runs if the earlier evidence warrants them. Set duration by diagnostics rather than importing a publication's trajectory length as a guarantee.
- [ ] Report the restrained result, midpoint bridge, standard-state calculation, required releases, graph/PBC behavior, sensitivity to one alternative bulk placement, and a larger-box check where needed to resolve the physical approximation budget.

Run `pytest tests/workflow/test_protein_abfe.py -v` for deterministic checks and the versioned pilot command for sampled evidence.

**Deliverable:** one reproducible protein ABFE qualification bundle, including controls and unresolved limitations.

**Pass:** all lower-level gates continue to pass, the estimator sees connected overlap, restart/exchange remain correct, and the result has an explicit uncertainty and correction ledger. Agreement with experiment is informative but is not this gate's pass criterion.

**Failure action:** classify failure as implementation, sampling, or physical adequacy. Expand sampling only when the evidence identifies sampling, not when a missing force or undefined endpoint remains possible.

## G12. Dual-ligand RBFE and closure checks

**Question:** Can the same platform exchange two complete ML ligands around the same capped cavity without changing the embedding definition?

**Files:** `fixtures/protein_two_ligands/`, `tests/workflow/test_rbfe_transforms.py`, `tests/sampling/test_binding_closure.py`.

- [ ] First add a second ligand to the small solvated fixture. Use hand-checked opposite displacement maps and test both raw geometries, including zero explicit displacement of every protein cap.
- [ ] Verify the bound ligand's graph connects to the cavity and the other ligand's graph does not. Test unwanted ligand-ligand and periodic contacts at both states and along pilot trajectories.
- [ ] Run an A-to-A identity calculation with symmetric restraints and identical ligand models. Its equilibrium free-energy difference should be zero; its instantaneous perturbation energy need not be zero when the two molecules have different conformations or environments.
- [ ] Run a nontrivial A-to-B pair and its reversed endpoint labeling. Confirm the sign convention and the same cavity/model/cap identities. Re-run serialization and two-worker tests with the larger joint ML input.
- [ ] Compare an RBFE with corresponding ABFE differences and, when appropriate, a small closed cycle. Match thermodynamic states carefully: finite-box spectator-ligand interactions can make a two-ligand RBFE differ from a naive subtraction of separate one-ligand ABFEs. Use spectator controls or quantify this difference before calling it a code failure.

Run `pytest tests/workflow/test_rbfe_transforms.py tests/sampling/test_binding_closure.py -v` plus the admitted sampled pilots.

**Deliverable:** one nontrivial dual-ligand qualification, an identity control, and a transparent closure report.

**Pass:** no new force/index/graph failures, identity and reversal controls hold, and closure is consistent with the matched-state definition and uncertainty budget. **Failure action:** check ligand ordering, restraints, spectator interactions, and maps before blaming the model's chemical accuracy.

## G13. Performance qualification and release decision

**Question:** Is the correct implementation usable and documented well enough to hand to Project 1?

**Files:** `report.py`, benchmark scripts, `docs/qualification.md`, `docs/hamiltonian.md`, `README.md`, release manifests.

- [ ] Benchmark all-MM, ligand-only ML/MM, capped cavity-inclusive ML/MM, and ATM versions on the same hardware. Separate context startup/model loading from steady-state stepping.
- [ ] Record real/ML/cap atom counts, graph size, model dtype, OpenMM precision, timestep, force evaluations, memory per worker, throughput, and synchronization or data-transfer overhead.
- [ ] Measure one worker before several. Check whether model copies in nested contexts and worker serialization dominate memory. Do not assume ATM costs exactly twice a conventional hybrid simulation.
- [ ] Run the full regression suite from a clean environment and offline model bundle. Have a colleague inspect a raw failure-injection example and independently reproduce the smallest correct example.
- [ ] Publish the supported-configuration matrix, known limitations, source/weight identities, gate reports, and an explicit decision: qualified for specified Project-1 trials, qualified only for a narrower configuration, or not yet qualified.

Run the full deterministic suite plus the admitted hardware/sampling qualification jobs. "Tests passed" must name what was run; optional GPU or long-sampling tests skipped on another machine do not constitute a GPU qualification.

**Deliverable:** a tagged project release and a reproducible qualification report. **Pass:** both ABFE and RBFE are supported within the declared scope, not merely a single favorable notebook trajectory.

---

# 11. Acceptance criteria and error budgets

## 11.1 Numerical checks

These are **proposed starting thresholds**, not values established by benchmarks in this review. Freeze the final numbers after characterizing the admitted double-precision reference calculation. Any later relaxation needs a written numerical justification and review.

| Check | Proposed starting requirement | Meaning |
|---|---|---|
| Atom identity and force ownership | Exact match; no tolerance | No missing/duplicate real atoms, cap parents, or physical force objects. |
| Analytic Reference energy | Absolute error <= $10^{-8}$ kJ/mol | Applies to the small analytic oracle, not an entire mixed-precision protein. |
| Analytic Reference force | Maximum component error <= $10^{-7}$ kJ/mol/nm | Tests the known derivative and coordinate-map composition. |
| Small-system double-precision direct/ATM energy | Absolute error <= $10^{-4}$ kJ/mol | Compare quantities with identical force scope, coordinates, and energy convention. |
| Small-system double-precision direct/ATM force | Maximum component error <= $5\times10^{-3}$ kJ/mol/nm | Include real boundary parents. Investigate systematic error even below a loose maximum. |
| ML finite-difference force | A convergent step-size interval; RMS error <= $10^{-3}$ kJ/mol/nm plus $10^{-4}$ times the RMS reference force | RMS means root-mean-square over the selected force components. Also inspect each boundary component. |
| Disconnected local-model limit | Same energy/force tolerances as the native-model comparison | Requires compatible periodic and model conventions, not just visual separation. |
| XML/fresh-process reconstruction | Same fixed-coordinate energy/force tolerances | Not a promise of bitwise-identical stochastic trajectories on other hardware. |
| Model-domain safety | No nonfinite energy/force on admitted pilot configurations | A single unexplained failure blocks production. |
| Analytic sampled free energy | Within 3 reported standard errors and within 0.1 kJ/mol of the known value after adequate sampling | Both uncertainty and absolute accuracy matter; increasing the error bar is not a pass strategy. |
| Independent estimators on identical data | Agreement to solver precision for the same mathematical state set | Differences in midpoint handling or restraint corrections must be resolved first. |

GPU production precision requires a separate comparison with the admitted reference. Do not apply a small-toy threshold blindly to a large PME system, but do not normalize errors by its enormous total energy either. Quantify errors in the perturbation energy, forces near links, and final known-answer free energy. Store the observed error distribution and worst cases.

## 11.2 Dynamics diagnostics

Begin with 0.5 fs and a simple LangevinMiddle integrator at an explicitly chosen temperature and friction. For diagnostic energy-conservation runs, use a suitable nonthermostatted integrator on an admitted fixture and disable energy-changing operations. Compare shorter timesteps and precision modes.

A thermostat can conceal some integration problems by continually adding or removing energy. Stable temperature is therefore not a sufficient force check. Likewise, a small average drift can conceal individual discontinuities; examine energy changes around neighbor-list changes, cap motion, and periodic image choices.

Do not optimize timestep, hydrogen masses, constraints, or multiple-time-step splitting before the baseline is qualified. Each is a later numerical-method change with a measurable speed/accuracy tradeoff.

## 11.3 Sampling acceptance is more than an error bar

For molecular pilots, inspect overlap between neighboring and connecting states, effective sample counts, trajectory correlation, replica state visits, restart continuity, and reproducibility across independent seeds. No single overlap threshold proves convergence, and successful exchange is not proof of adequate protein conformational sampling.

As a starting operational screen, flag an endpoint supported by fewer than 100 effectively contributing samples, an overlap graph that is disconnected, or a result whose last-half and full-run estimates differ beyond their uncertainty. These are escalation triggers, not universal convergence laws. A scientific reviewer may require more stringent evidence.

For a Project-1 readiness pilot, a proposed uncertainty target is at most 0.5 kcal/mol per reported binding estimate, with a separately budgeted implementation/physical-approximation sensitivity target of 0.2 kcal/mol. These values are planning choices. They must not replace the much tighter deterministic code checks or be used to excuse a known missing contribution.

## 11.4 Physical sensitivity checks

Vary the bulk placement while preserving its admitted domain. Increase the box when periodic residual interactions may matter. Test a modest, chemically defensible change in the cavity partition as a model-sensitivity experiment, not an exact-equivalence test. Evaluate boundary geometries and contact energies before running another full free-energy calculation.

A change of ML region changes the model. It should not be hidden inside a statistical error bar. Report this sensitivity separately from the uncertainty caused by finite sampling.

The missing-long-range question is not resolved by selecting neutral ligands alone: neutral systems can still have electrostatic multipoles, dispersion, and local chemical effects. The decision to proceed must be based on the declared Hamiltonian and observed sensitivity, not on the word "neutral."

---

# 12. Data recording, estimation, and reproducibility

## 12.1 Minimum per-sample record

The project-owned record should include sample ID, simulation time/step, replica ID, current thermodynamic state ID, direction, temperature, box, full schedule parameters, and the following separately named energies:

```text
u0_raw_kJ_mol
u1_raw_kJ_mol
delta_u_raw_kJ_mol
delta_u_softcore_kJ_mol
atm_expression_energy_kJ_mol
outside_energy_kJ_mol
system_total_energy_kJ_mol
```

Save high-precision coordinates often enough to independently reevaluate a representative subset, including each state and restart segment. The exact record interval is an explicit run setting, not a universal recommendation.

Do not confuse AToM's schedule parameter named `U0` or an analysis column named `u0` with the raw endpoint energy. The pinned analysis schema uses names that require an explicit adapter translation. [S18] Keep the project schema unambiguous.

## 12.2 Reconstruct the actual sampled energy

For a fixed-temperature NVT calculation define the reduced energy

$$v_k(\mathbf R_n)=U_k(\mathbf R_n)/(RT),$$

where $k$ labels an alchemical state and $n$ a saved sample. "Reduced" means dimensionless: energy divided by the thermal energy scale.

Evaluate the exact schedule expression for every required state on each sample, including the outside terms when they do not cancel. Compare a subset with direct OpenMM context evaluations at those states. This detects a mismatch between what the integrator sampled and what the estimator assumes.

Do not introduce NPT or multiple temperatures merely by adding a field to the file. They require the corresponding reduced-potential terms and an estimator/worker path that supports them. The inspected bundled UWHAM route is restricted to a single temperature; that is one reason for the initial fixed-temperature scope. [S18]

## 12.3 Independent analysis and uncertainty

Use PyMBAR on the full reduced-potential data as an independent check. Its documented interface takes energies evaluated across states and provides free-energy differences, overlap information, and effective sample counts. Its uncertainty assumptions require attention to correlated data. [S33]

Estimate equilibration and correlation using several relevant observables, not only total potential energy. PyMBAR's timeseries tools can estimate statistical inefficiency and construct subsampled data. [S34] Preserve full data for block-based checks and plot estimates as a function of retained trajectory length.

For replica exchange, distinguish the continuous history of a physical walker from the history of samples assigned to one thermodynamic state. A sequence made by combining state visits is not automatically a set of independent samples. Resample contiguous trajectory blocks or whole independently seeded runs as appropriate, preserving dependence between quantities entering the final difference.

For a result $X-Y$, uncertainty is

$$\mathrm{Var}(X-Y)=\mathrm{Var}(X)+\mathrm{Var}(Y)-2\mathrm{Cov}(X,Y).$$

Here variance measures uncertainty squared, and covariance measures shared fluctuation. The familiar square root of the sum of squared uncertainties is appropriate only when covariance can be neglected. Report uncertainty of the final mean separately from the standard deviation across repeated calculations.

The stock estimator is useful as a comparison, but do not simply copy its uncertainty combination when the analysis introduces shared data, a midpoint bridge, or correlated corrections.

## 12.4 Restart artifacts

Save both an OpenMM binary checkpoint and a portable State when useful. A checkpoint includes internal simulation state but is specific to the same system/platform/version/hardware. A State is more portable but does not preserve the random-number-generator state needed for an identical stochastic continuation. [S27]

The checkpoint is not the complete research archive. Preserve system XML, topology, all real/cap identities, high-precision coordinates, box, constraints, force routing, restraint references, schedule, model asset, source hashes, environment, and analysis scripts.

System serialization involving a Python callback is also a code-loading mechanism. Treat the XML and model bundle as trusted executable artifacts, not harmless text supplied by an unknown party.

## 12.5 GPU workers

PyTorch documents the need for a suitable process-start method when CUDA is used in subprocesses. The inspected AToM worker already requests `spawn`; preserve and test that behavior rather than replacing it with a presumed default. [S25], [S17]

A serialized callback may carry tensors associated with a particular device. Verify their device after worker startup, including the case where only one physical GPU is visible under `CUDA_VISIBLE_DEVICES`. Local device index zero can then refer to a different physical GPU in each process. Do not assume that setting OpenMM's `DeviceIndex` also relocates a previously created PyTorch model.

The baseline multiwindow demonstration may use a single GPU with workers scheduled onto that one device. Multigpu execution is a separately admitted configuration, not an implicit consequence of single-GPU success. If relocation requires changes, use a small worker/model initialization interface with a fresh-process test, not an undocumented global device override.

---

# 13. Performance and the smallest reasonable optimization path

First measure context construction, model deserialization, first evaluation, and steady-state step time separately. Synchronize the accelerator appropriately for timing so asynchronous work is not reported as completed execution time.

At minimum compare ordinary MM, ligand-only ML/MM, cavity-inclusive ML/MM without ATM, native ATM, and the AToM worker route. Use the same fixture, timestep, and precision where meaningful. A change of timestep must not be presented as a pure backend speed improvement.

For a step time $t_{\mathrm{step}}$ in seconds and timestep $\Delta t$ in fs, the approximate throughput is

$$\mathrm{ns/day}=0.0864\,\Delta t/t_{\mathrm{step}}.$$

This follows from 86,400 seconds per day and one million femtoseconds per nanosecond. It excludes startup and scheduling overhead unless they are included in the measured step time.

For $N_w$ windows, $N_r$ independent repetitions, and $T_{\mathrm{ns}}$ nanoseconds per window, a first resource estimate is

$$\mathrm{GPU\ hours}\approx24\,N_wN_rT_{\mathrm{ns}}/s,$$

where $s$ is measured ns/day **per effectively occupied GPU** under the intended scheduling pattern. Do not count replicas twice if the quoted throughput already includes all windows, and do not treat wall time as identical to total GPU usage.

Only after profiling should optimization proceed in this order: remove avoidable Python/host-device transfers; reuse safe static model data; review repeated context/model copies; test production precision; then consider excluding rigorously invariant terms from ATM. Longer timesteps or multiple-time-step integration come later.

If moving an invariant contribution $K$ outside ATM, verify both coordinate invariance and the algebraic identity required by the chosen mixing function, namely that adding the same contribution to both endpoint energies shifts the final physical energy correctly. Test forces as well as energies. It is not enough that a term happened to be constant on one snapshot.

Do not implement a new GPU neighbor-list kernel or train a smaller model before establishing that those are the bottlenecks. The cost of a wrong free-energy calculation is much greater than the cost of an initially redundant force evaluation.

---

# 14. How this expands without redesigning the core

## 14.1 A second local ML model

A new local model implements the same checkpoint/input/output contract. It must pass element/charge checks, unit tests, native-adapter agreement, cap force transfer, disconnected-graph behavior, counterfactual-geometry tests, and serialization. Its name appearing in OpenMM-ML's supported-model list is not equivalent to satisfying this project's contract.

The smallest second-model demonstration is the capped-fragment/ligand fixture plus a short solvated calculation. It does not need a complete new protein benchmark merely to establish interface compatibility.

## 14.2 Long-range or charge-aware ML

A long-range model changes the disconnected-fragment assumption and the MM subtraction. It needs an explicit definition of electrostatics within ML, interactions across periodic cells, charge assignment across disconnected components, and compatibility with caps. The generic `mlLongRange` switch cannot supply missing model physics.

Before any long-range-plus-link attempt, audit all internal auxiliary force particle counts after caps are added, not only the top-level system count. Recheck global charge/spin inputs, self/background terms, and the exact retained-MM Hamiltonian. This is a new qualification branch, not a one-line configuration change.

## 14.3 Electrostatic embedding

Electrostatic embedding additionally requires the model to respond to the MM electrostatic environment and to return consistent forces on every coordinate that influences that response, including MM atoms and boundary parents. A model with internal long-range electrostatics does not automatically provide that capability.

Define the external-field representation, treatment of near-boundary charges, periodic electrostatics, polarization/double-counting convention, and training requirements first. Then reuse the existing ATM endpoint and derivative tests. This is where preserving the separation between energy engine and transfer engine pays off.

## 14.4 New alchemical coordinate maps

Coordinate swapping, attachment-atom-dependent displacement, restrained rotations, or other maps need their own forward transformation, inverse/domain definition, derivative, and measure/Jacobian analysis. They also need tests showing that any constraints and virtual sites are transformed consistently.

Do not generalize from fixed whole-ligand translations merely because both operations can be represented by arrays. The existing independent endpoint oracle is reusable; the map-specific mathematical proof is new.

## 14.5 Metals and covalent chemistry

Those applications require a chemically appropriate electronic-state model and a clearly defined thermodynamic cycle, potentially including proton transfer, reaction equilibria, and additional sampling coordinates. They remain outside Project 0.

The platform should preserve the hooks needed to evaluate more general energy functions. It should not claim those difficult physical problems have been solved because an energy function can be nested in ATM.

---

# 15. Completion, handover, and colleague review

## 15.1 Minimum deliverables

A release candidate must contain the importable builder/validator/adapter package; small fixtures with independent expected answers; a pinned supported environment; a trusted model manifest; an exact Hamiltonian and restraint specification; and saved gate reports.

It must also contain one reproducible solvated capped-fragment ATM example, one protein ABFE example, one nontrivial dual-ligand RBFE example, an A-to-A control, an estimator known-answer example, and restart/replica-exchange evidence.

Every example must state whether it demonstrates deterministic correctness, a smoke test, an adequately sampled free energy, or physical-accuracy assessment. A short demonstration trajectory must not be described as a converged benchmark.

## 15.2 Formal completion checklist

- [ ] The exact supported environment and model asset are identified and reproducible.
- [ ] Every physical force is counted once and included in the active integrator configuration.
- [ ] The original and retained MM terms, including boundaries and periodic exceptions, are explained and tested.
- [ ] Caps have the intended coordinates, zero independent mass, correct classical treatment, and correct real-parent forces inside and outside ATM.
- [ ] Direct, native-ATM, and AToM-built endpoint/intermediate evaluations agree.
- [ ] Periodic geometry, graph connectivity, counterfactual model behavior, and trajectory safety checks pass.
- [ ] Binding domains, restraints, signs, midpoint connection, and standard-state corrections are explicit.
- [ ] Known-answer analysis, identity/reversal tests, and qualified ABFE/RBFE comparisons pass.
- [ ] Fresh-process reload, restart, state changes, and small replica exchange are demonstrated on the supported hardware.
- [ ] Numerical errors, sampling uncertainty, physical sensitivities, and performance are reported separately.

## 15.3 What moves to Project 1

Project 1 should use the frozen platform on a small, well-characterized noncovalent series. Begin with the MM, ligand-only ML/MM, and cavity-inclusive ML/MM comparison. Only then ask whether targeted fine-tuning improves intramolecular conformations, capped-fragment energetics, and binding predictions.

The Project-1 report should preserve a fixed cavity convention across the series and report experiments as an external test, not a way to tune hidden corrections until an answer looks right. Poor agreement should be diagnosed among sampling, model chemistry, embedding, structure preparation, and experimental comparability.

## 15.4 Questions colleagues should challenge before implementation

The principal review question is whether the operational retained-MM-plus-ML Hamiltonian is the intended physical approximation, especially its periodic and boundary conventions. Next, challenge whether the selected neutral capped fragments are chemically justified, whether the binding/standard-state definition is complete, and whether the proposed environment can be reproduced on the intended hardware.

Also challenge the midpoint-bridge treatment, the proof that restraints cancel or are corrected, the meaning of ABFE/RBFE closure in the finite dual-ligand box, and whether the admitted model domain covers the actual alternate ATM geometries. These are more consequential than the choice of module names.

**Final recommendation:** build the small deterministic and thermodynamic oracles first; admit one local checkpoint and one embedding convention; then validate the complete solvated worker path before touching a protein. This retains the original plan's low-effort philosophy while removing the assumptions most likely to produce a plausible but incorrect result.

---

# Appendix A. Traceability to the original plan

The original document remains the record of the initial brainstorming. The changes below are explicit corrections or expansions, not claims that the original already contained these details.

| Original sections | Treatment in this revision |
|---|---|
| 1-3: purpose, architecture, scope | Retained; added separate implementation, thermodynamic, and physical-adequacy levels. |
| 4-6: notation, embedding, ATM | Replaced the schematic boundary energy with an operational Hamiltonian and explicit child/outside energy scope. |
| 7-8: disconnected ML graph and distant training data | Retained with additive-model, periodic, and model-domain qualifications. |
| 9: software landscape | Corrected OpenMM floor and PythonForce subset history; separated candidate stack from tested interoperability. |
| 10: Python/ML force in ATM | Expanded to API return order, independent oracles, ownership, force masks, and known-answer controls. |
| 11: indexing | Corrected current append-only behavior while retaining a future-safe mapping contract. |
| 12-13: cuts and cap forces | Added precise cap derivatives, periodic-coordinate tests, and a chemically restricted first fixture. |
| 14: double counting and missing interactions | Replaced the general tail narrative with retained-PME accounting, pair-mask diagnostics, and a defined free-energy sensitivity test. |
| 15-16: periodicity and solvent endpoint | Expanded to full-solute clearance, cap/image edges, trajectory excursions, and explicit bulk-state physics. |
| 17: ABFE/RBFE | Added restraint/standard-state/sign definitions, midpoint connection, fixed-cavity consistency, and spectator effects. |
| 18: finite-difference forces | Added step-size sweeps, constraint treatment, independent cap-force oracle, and force-scope checks. |
| 19: serialization and replica exchange | Expanded to fresh processes, offline assets, worker devices, parameter overrides, and correlated state histories. |
| 20: stability/timestep | Retained conservative timesteps; added counterfactual model-domain and integration-mask checks. |
| 21-23: ladder, completion, architecture | Replaced with G00-G13 work packages and explicit outputs/failure decisions. |
| 24-25: model strategy and region size | Narrowed to one first model/checkpoint and chemistry domain; general model support becomes staged qualification. |
| 26-27: software deliverables and scientific standard | Retained; added exact interfaces, data contracts, reference fixtures, and error-budget separation. |
| 28: Project 1 | Retained as a later scientific stress test, not a substitute for Project-0 correctness. |
| 29-32: immediate actions, decisions, references, final definition | Updated to source-verified versions, explicit dependencies, and a revised handover definition. |

# Appendix B. Source register

Sources were inspected on 29 September 2026. Tagged source is preferred for implementation claims; moving documentation is useful for explanations but is not an environment lock. Reference identifiers used in the text link to the corresponding source below. The original uploaded file is the design basis, not independent verification of software behavior.

**S01.** Original user-supplied `Project_0_ATM_MLMM_Design_and_Validation_Plan.md`. See Appendix A for the disposition of its sections.

**S02.** OpenMM release history: distinction between 8.5 PythonForce introduction, 8.6 subset support, and 8.6.1 fixes. [S02]

**S03.** OpenMM-ML release history: version 1.8 and the link/embedding additions. [S03]

**S04.** OpenMM-ML tag 1.8, `setup.py`: explicit OpenMM >=8.6.1 requirement. [S04]

**S05.** OpenMM-ML user guide: mechanical embedding, periodic conventions, link sites, and returned information. [S05]

**S06.** OpenMM-ML tag 1.8, `mlpotential.py`: public mixed-system API, constraint handling, and device selection. [S06]

**S07.** OpenMM-ML tag 1.8, `embeddings/mechanicalembedding.py`: operational nonbonded and long-range handling. [S07]

**S08.** OpenMM-ML tag 1.8, `embeddings/utilities.py`: link construction, index mapping, and bonded-term predicates. [S08]

**S09.** OpenMM `ATMForce` Python API: child-force ownership, transformations, and diagnostic return values. [S09]

**S10.** OpenMM `PythonForce` Python API: callback contract, selected particles, units, and serialization. [S10]

**S11.** OpenMM tag 8.6.1, `ATMForceImpl.cpp`: internal system/context construction and cloned child forces. [S11]

**S12.** AToM-OpenMM release history: v8.5.0 and documented tested OpenMM release. [S12]

**S13.** AToM-OpenMM tag v8.5.0, `pyproject.toml`: package metadata, dependencies, and executable entry points. [S13]

**S14.** AToM-OpenMM tag v8.5.0, `ommsystem.py`: force selection, integrator masks, displacement inputs, and alchemical expressions. [S14]

**S15.** AToM-OpenMM tag v8.5.0, `abfe_structprep.py`: no-ATM preparation and state handover. [S15]

**S16.** AToM-OpenMM tag v8.5.0, `rbfe_structprep.py`: preparation group handling and preparation settings. [S16]

**S17.** AToM-OpenMM tag v8.5.0, `ommworker.py`: process creation, context/device setup, state loading, and diagnostics. [S17]

**S18.** AToM-OpenMM tag v8.5.0, `uwham.py`: bundled Python estimator, input schema, schedule handling, and leg analysis. [S18]

**S19.** OpenMM-ML tag 1.8, `models/macepotential.py`: model identifiers, locality flags, callback construction, energy-output convention, and unit conversion. [S19]

**S20.** MACE release history, including v0.3.16. [S20]

**S21.** MACE tag v0.3.16, `setup.cfg`: supported Python floor and dependency constraints. [S21]

**S22.** MACE tag v0.3.16, `foundations_models.py`: foundation-model loading and checkpoint sources. [S22]

**S23.** MACE-OFF model repository README: model identity and Academic Software License statement. [S23]

**S24.** Official PyTorch previous-version installation instructions: 2.8.0 CPU/CUDA wheels. [S24]

**S25.** PyTorch 2.8 multiprocessing guidance: accelerator subprocess initialization. [S25]

**S26.** OpenMM installation guide: package-manager options, accelerator extras, and installation test. [S26]

**S27.** OpenMM `Simulation` API: checkpoint versus portable State behavior. [S27]

**S28.** *Enhancing Protein-Ligand Binding Affinity Predictions Using Neural Network Potentials* (2024), DOI 10.1021/acs.jcim.3c02031. Primary ligand-only ANI/MM ATM precedent; not validation of the capped cavity-inclusive extension. [S28]

**S29.** *Potential distribution theory of alchemical transfer*. Primary discussion of transfer thermodynamics, restricted binding states, and alchemical schedules. [S29]

**S30.** AToM-OpenMM theory documentation. [S30]

**S31.** AToM-OpenMM tag v8.5.0, FKBP ABFE example `defaults.yaml`: an inspectable directional schedule, not a universal production prescription. [S31]

**S32.** AToM-OpenMM tag v8.5.0, CDK2 RBFE example `defaults.yaml`: corresponding dual-ligand workflow schedule example. [S32]

**S33.** PyMBAR 4.0.3 MBAR API: reduced-potential inputs, free energies, overlap, and effective sample counts. [S33]

**S34.** PyMBAR 4.0.3 timeseries API: equilibration and correlation tools. [S34]

**S35.** openmmforcefields release history, including 0.16.0 and explicit template force-field selection. [S35]

**S36.** openmmforcefields repository documentation: force-field/template-generation scope. [S36]

**S37.** AToM-OpenMM ABFE workflow guide. [S37]

**S38.** AToM-OpenMM RBFE workflow guide. [S38]

**S39.** PyTorch 2.8 serialization semantics: `weights_only` defaults, trusted full-module loading, and loader environment variables. [S39]

[S02]: https://github.com/openmm/openmm/releases
[S03]: https://github.com/openmm/openmm-ml/releases
[S04]: https://raw.githubusercontent.com/openmm/openmm-ml/1.8/setup.py
[S05]: https://openmm.github.io/openmm-ml/latest/userguide.html
[S06]: https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/mlpotential.py
[S07]: https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/embeddings/mechanicalembedding.py
[S08]: https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/embeddings/utilities.py
[S09]: https://docs.openmm.org/latest/api-python/generated/openmm.openmm.ATMForce.html
[S10]: https://docs.openmm.org/latest/api-python/generated/openmm.openmm.PythonForce.html
[S11]: https://raw.githubusercontent.com/openmm/openmm/8.6.1/openmmapi/src/ATMForceImpl.cpp
[S12]: https://github.com/Gallicchio-Lab/AToM-OpenMM/releases
[S13]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/pyproject.toml
[S14]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/ommsystem.py
[S15]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/abfe_structprep.py
[S16]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/rbfe_structprep.py
[S17]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/ommworker.py
[S18]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/uwham.py
[S19]: https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/models/macepotential.py
[S20]: https://github.com/ACEsuit/mace/releases
[S21]: https://raw.githubusercontent.com/ACEsuit/mace/v0.3.16/setup.cfg
[S22]: https://raw.githubusercontent.com/ACEsuit/mace/v0.3.16/mace/calculators/foundations_models.py
[S23]: https://raw.githubusercontent.com/ACEsuit/mace-off/main/README.md
[S24]: https://pytorch.org/get-started/previous-versions/
[S25]: https://docs.pytorch.org/docs/2.8/notes/multiprocessing.html
[S26]: https://docs.openmm.org/latest/userguide/application/01_getting_started.html
[S27]: https://docs.openmm.org/latest/api-python/generated/openmm.app.simulation.Simulation.html
[S28]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11214867/
[S29]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11803756/
[S30]: https://gallicchio-lab.github.io/AToM-OpenMM/theory/
[S31]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/examples/ABFE/fkbp/scripts/defaults.yaml
[S32]: https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/examples/RBFE/cdk2/scripts/defaults.yaml
[S33]: https://pymbar.readthedocs.io/en/4.0.3/mbar.html
[S34]: https://pymbar.readthedocs.io/en/4.0.3/timeseries.html
[S35]: https://github.com/openmm/openmmforcefields/releases
[S36]: https://github.com/openmm/openmmforcefields
[S37]: https://gallicchio-lab.github.io/AToM-OpenMM/user-guide/abfe/
[S38]: https://gallicchio-lab.github.io/AToM-OpenMM/user-guide/rbfe/
[S39]: https://docs.pytorch.org/docs/2.8/notes/serialization.html

# Appendix C. Short glossary

**ABFE:** absolute binding free energy, with a specified standard state and binding-state definition.

**RBFE:** relative binding free energy, the difference between the binding free energies of two ligands under a declared sign convention.

**ATM / AToM:** ATM is the Alchemical Transfer Method; AToM-OpenMM is the workflow software used here to run it.

**Hamiltonian:** the mathematical energy model defining the simulated system. This plan mainly discusses its potential-energy part.

**Mechanical embedding:** ML-region internal interactions are replaced by ML while the cross-region coupling is classical under an explicitly defined bookkeeping convention.

**Link atom / cap:** an artificial hydrogen used to close a selected fragment's valence for the model. Here it is a derived virtual site, not an independently moving physical hydrogen.

**Virtual site:** a particle position computed from other particles rather than integrated as an independent coordinate.

**PME:** particle-mesh Ewald, a periodic electrostatic calculation. It cannot generally be decomposed into arbitrary group energies by simply assigning a force group.

**Neighbor graph:** the model's set of local atom connections, including relevant periodic shifts. Different connected components can become independent for an additive local model.

**Counterfactual geometry:** the alternate coordinate state evaluated by ATM at the same stored molecular configuration, even when that state has a small current alchemical weight.

**Force group:** an OpenMM label used to select collections of force objects. It is not automatically a chemical interaction decomposition.

**Oracle:** a simpler independent calculation with a known expected answer, used to check the implementation under test.

**Gate:** an explicit testable condition that must pass before a more complex calculation is admitted.

**Phase-space overlap:** the extent to which configurations important in one thermodynamic state are represented by samples from another. Poor overlap makes reweighting unreliable.

**Standard error:** estimated uncertainty in an estimated mean or free energy. It is not the same as the spread of individual instantaneous energies.

**Provenance:** the record of which inputs, software, model weights, settings, and analysis produced a result.

**Qualification:** evidence that a specified configuration works within declared limits. It is not a guarantee for every model, target, or hardware platform.
