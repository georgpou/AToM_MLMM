# S05: What the free-energy result means

**Design status:** proposed until a recorded M00 review or later approved amendment. **Scientific contract version:** 1; this documentation edit does not claim new numerical support.

[Roadmap](../README.md) | [Requirements](../REQUIREMENTS.md) | [Status](../STATUS.md)

## In plain terms

Moving a ligand correctly is not enough. We also need to know which two states we compare, what the sign means, and which restraint or standard-state corrections are required.

**When to read it:** Read it before changing a protocol, schedule, restraint, estimator, or reported binding value.

The detailed names and equations below are kept precise because they define the behavior the tests must check. Unfamiliar terms are explained in [the glossary](../reference/glossary.md).

## One protocol contract, two initial presets

ABFE uses a fixed real ML set $C\cup L$. Dual-ligand RBFE uses $C\cup L_A\cup L_B$. Here $C$ denotes protein ML atoms and $L$, $L_A$, $L_B$ complete real ligand molecules. Membership does not change along the calculation. The protocol preset validates its own ligand count and produces the same `TransferDefinition` type in both cases.

One coordinate map can be the identity. The other translates one complete ligand for ABFE or applies opposite fixed translations to two complete ligands for RBFE. All initial protein caps receive zero explicit displacement. The common assembler receives full per-particle maps and never needs to ask whether the requested calculation is ABFE or RBFE.

The two ligands may have different atom counts and disjoint noncontiguous IDs. They need not share an atom-mapping scaffold for whole-molecule ATM transfer. Relative input selection must not silently reorder their meaning. Future coordinate-dependent translations, swaps of subsets, or rotations require a separate map contract with derivative and measure/Jacobian analysis.

## Raw physical energies and alchemical energy

Let $V$ be the child physical potential placed inside ATM, and let $T_0,T_1$ be the maps. Define

$$u_0(\mathbf R)=V(T_0\mathbf R),\qquad u_1(\mathbf R)=V(T_1\mathbf R).$$

For schedule state $k$,

$$U_k(\mathbf R)=K(\mathbf R)+\Phi_k(u_0,u_1).$$

$K$ is the explicitly outside contribution, usually the declared restraint layer in the baseline. $\Phi_k$ is the exact mixing expression, including soft-core/softplus parameters and offsets. Raw child energies are not automatically full-system energies.

For the first analytic test use $\Phi_\lambda=(1-\lambda)u_0+\lambda u_1$ at 0, 0.37, and 1. Fixed translations have identity coordinate Jacobians, so the force is the weighted endpoint-force sum plus the outside force. This is a test oracle, not a replacement for the production ATM schedule.

The revised audit reports `getPerturbationEnergy()` returns `(u1, u0, energy)`. Name the fields explicitly and confirm against the admitted API in G00/G02. An independent direct evaluation must match the same child scope; include a nonzero outside restraint so a mistaken scope cannot pass accidentally.

## Binding definition and correction completeness

An unrestricted volume-preserving translation produces equal configurational integrals by change of variables. Binding calculations distinguish a bound domain from a bulk reference domain, including their restraint conventions. Therefore coordinate/force correctness alone does not define an ABFE.

Record the binding domain; bound and bulk state descriptions; translation/orientation/conformation restraints; reference atoms; standard concentration; symmetry/pose counting; and every restraint release or other required correction. The initial ABFE result convention is bound minus bulk. The relative target convention is

$$\Delta\Delta G_{A\to B}=\Delta G^\circ_{\mathrm{bind}}(B)-\Delta G^\circ_{\mathrm{bind}}(A).$$

A negative value means B binds more favorably under that convention. Input state order and upstream printed labels are mapped explicitly into this result definition. Do not infer signs from `dgb`, directory names, or ligand alphabetical order.

A correction record has an explicit status: `required_uncomputed`, `computed`, `zero_demonstrated`, or `not_applicable`. Only `computed` and evidence-backed zero/not-applicable entries satisfy an obligation. Missing is not zero. A final standard binding estimate is withheld when a required correction remains unresolved; the raw restrained result can still be reported with its correct label.

## Standard translational volume

For a separable bulk translation restraint $W(\mathbf r)$, define

$$V_{\mathrm{eff}}=\int e^{-W(\mathbf r)/(RT)}d^3\mathbf r.$$

$R$ is the molar gas constant and $T$ temperature. For a spherical flat-bottom radius $r_0$ with a harmonic exterior $W(r)=\tfrac12 k_r(r-r_0)^2$ for $r>r_0$, use the full integral $4\pi\int_0^\infty r^2 e^{-W(r)/(RT)}dr$, not simply the hard-sphere volume for a finite wall. Use the actual periodic domain when the infinite-space approximation is not justified.

For the declared bound-minus-bulk restrained difference,

$$\Delta G^\circ_{\mathrm{bind}}=\Delta F_{\mathrm{b-u}}-RT\ln(V_{\mathrm{eff}}/V^\circ)+\Delta G_{\mathrm{release,bound}}.$$

$V^\circ=1/(N_A C^\circ)$ is approximately 1.66054 nm cubed at 1 mol/L. This formula assumes the stated separable translational case. Do not apply it indiscriminately to coupled orientation/position restraints. An orientation fraction relative to $8\pi^2$ needs a justified factorization; symmetry and multiple poses require a nonduplicated state-counting convention.

## Directional midpoints

If two half-legs connect their endpoints to the same midpoint, with $D_0=F_m-F_0$ and $D_1=F_m-F_1$, then $F_0-F_1=D_1-D_0$. Equal nominal lambda values do not demonstrate equal midpoint Hamiltonians when directional soft-core functions or offsets differ.

More generally let $D_0=F_{m+}-F_0$, $D_1=F_{m-}-F_1$, and $\delta F_m=F_{m-}-F_{m+}$. Then

$$F_0-F_1=D_1-D_0-\delta F_m.$$

Save raw energies and evaluate both expressions on both midpoint ensembles. Include an overlap-qualified bridge or a common-midpoint connection when needed. A test deliberately using an active soft-core difference must fail if the bridge is silently omitted. A full reduced-potential analysis may connect both directional schedules, but requires adequate sampled overlap.

## Known nonzero analytic answer

Use $u_0(x)=kx^2/2$, $u_1(x)=k(x+d)^2/2$, and an outside $K(x)=k_r x^2/2$. Gaussian integration gives

$$F_1-F_0=\tfrac12\frac{kk_r}{k+k_r}d^2.$$

For $k=100$, $k_r=50$ kJ/mol/nm squared, and $d=0.3$ nm the result is +1.5 kJ/mol; reversing the reported difference gives -1.5. Setting $k_r=0$ gives zero. For the linear schedule,

$$F_\lambda-F_0=\tfrac12\lambda k d^2-\frac{\lambda^2k^2d^2}{2(k+k_r)}.$$

G08 checks these against independent quadrature and independent analytic samples before MD samples. It also tests constant energy-zero shifts, a finite-wall volume, missing correction rejection, and cross-analysis agreement.

## Shared analysis and molecular closure

At fixed-temperature NVT use dimensionless reduced potentials $v_k(\mathbf R_n)=U_k(\mathbf R_n)/(RT)$. Reconstruct the exact expression at all required states, with outside terms where needed, and verify selected rows by direct context evaluation. A protocol supplies endpoint weights and correction obligations; the estimator consumes energies, not embedding labels.

A-to-A RBFE has zero equilibrium free-energy difference only under the declared symmetric setup; instantaneous perturbations need not be zero. Compare RBFE and ABFE differences only for matched physical definitions. A two-ligand box contains a spectator molecule absent from a naive one-ligand ABFE subtraction; quantify that finite-box contribution or use matched controls before interpreting closure. Keep the same cavity, cap, model, and restraint conventions across a series whenever testing cancellation.
