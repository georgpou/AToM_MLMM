# Equations, force ownership and workflow traces

This record derives the expectations used in the single pass from S01–S07 and their scoped amendments, then compares the implemented paths and applicable evidence. It is not a new physical definition or a universal proof. Individual source hashes and scope are in [coverage.md](coverage.md) and [inventory.json](inventory.json).

## Admission before a calculation

Declarative `SystemInput`, `TopologyView`, `PartitionSpec`, `Snapshot`, protocol, schedule and runtime records reject duplicate/unknown atom IDs, malformed or nonfinite arrays, incompatible units/parameters and unsupported combinations. Canonical identities retain source order and explicit old-to-new/final maps; immutable copies prevent a caller mutating a hashed record through a list or array alias.

`resolve_partition` checks connectivity and molecule membership. A selected ligand or host is a complete connected neutral singlet; mobile groups are complete ML ligands and exclude protein atoms. Protein hydrogens are completed by bonding rather than names. The present mechanical builder re-resolves the partition and admits zero/one transparent protein C–C cut; ring/aromatic/multiple/cross-molecule unsupported cuts reject. This is not a general protein chemistry validator or multi-cap implementation. The model manifest admits neutral H/C/N/O, even though the actual checkpoint contains ten elemental channels; the extra channels do not extend the accepted chemical profile.

Runtime capability metadata distinguishes declarations from qualification. Full workers require the exact Reference/CPU-model profile; source/platform/dtype/integrator/ensemble settings are checked. NVT and ≤0.5 fs are admitted; NPT/virials, general pressure preparation, GPU, electrostatic embedding, broader chemistry and new transform kinds need separate qualification.

## Mechanical Hamiltonian and every term

From S04, with all real coordinates R, fixed model membership M, derived cap coordinates h(R), box B and frozen model θ:

\[
U(R;B)=U_{\mathrm{retained,MM}}(R;B)+E_\theta(R_M,h(R);B).
\]

The dropped ledger is `original MM − retained MM`; it is not a separately parameterized capped-molecule energy. Thus adding the original MM energy and also retained MM, or subtracting an invented capped MM system, would double count. The code does neither.

`ledger.py` enumerates actual recognized force objects and compares original and retained terms. Fully selected bonded terms and the admitted internal nonbonded contributions are removed once; boundary/cross/outside terms remain. Masses, admitted constraints and old-to-new maps have explicit ownership. Real model charges/LJ are preserved for retained classical cross interactions; zero-mass hydrogen caps have no independent classical charge/LJ terms. Unknown/custom ownership, conflicting parameters and unsupported force conventions reject.

The orthorhombic PME convention is deliberately local: removing an internal pair by exclusions/exceptions does not remove every reciprocal-image/background contribution. S04/G06 define which residual terms remain. The ledger and saved original/retained XML match that convention; it must not be described as “all electrostatics among model atoms vanished.” Cutoff 0.9 nm, switching 0.75 nm, explicit PME alpha/mesh and dispersion disabled belong to the fixture/profile. LJPME, arbitrary dispersion changes or triclinic images are not covered. Retained ligand–water forces are part of U, including in bulk.

No new numerical issue was found in this accounting. Applicability relies on unchanged G06 proofs and the exact current v8 source/test baseline, with new analytic checks for the coupled force/routing path. It does not establish that mechanical MM cross interactions and a capped model are physically adequate: the saved G07 failures show that limitation directly.

## Cap derivative and native ownership

For real parents a (selected) and b (outside), fixed cap distance d, r=|b−a| and n=(b−a)/r:

\[
h=a+dn,\qquad A=\frac d r(I-nn^T),\qquad
\partial h/\partial a=I-A,\quad\partial h/\partial b=A.
\]

Since F=−∇E, a raw cap force Fh contributes `(I−A)^T Fh` to a and `A^T Fh` to b. Their sum is Fh; rotational accounting follows from the same derivatives. Direct forces on either real parent and any influencing environment atom must also remain. Force coverage cannot stop at model atoms.

The builder creates a zero-mass native virtual site with this geometry. Production supplies the raw model forces, recomputes virtual sites after positioning/mapping, and lets native OpenMM redistribute once. Real-force extraction uses the declared final indices. Manual projection is confined to independent test/reference formulas; production does not project an already redistributed force again.

Fresh selected cap/environment and force/torque tests use explicit algebra and all-real central differences at 10⁻³, 10⁻⁴, 10⁻⁵ and 10⁻⁶ nm. They pass the existing component/RMS assertions without changing tolerances. The fourth step was already part of the retained cap control, not introduced by this review. General collections of many protein cuts are still outside the present builder.

## Maps, model graphs and units

The fixed maps translate one whole ligand for ABFE; RBFE translates two complete groups with opposite vectors, including unequal atom counts. Every real particle and cap has an explicit map. Stationary protein and cap coordinates are retained. Translation has identity Cartesian Jacobian and unit measure; it does not by itself create a bound/bulk thermodynamic domain.

Every actual evaluation positions the full current coordinates and recomputes virtual sites/model neighbors. Periodic model inputs use the admitted orthorhombic convention and checks on component/image/cutoff connections; both coordinate maps matter. Bulk clearance checks all real static molecules, other ligands, caps and relevant images, not just the local model set. The 0.45+0.20 nm clearance and Bondi guard are engineering admission limits, not proof of chemical training coverage or an equilibrium restraint potential.

The pinned model outputs total energy, including its fixed atomic reference energies; changing composition requires same-composition relative/contact definitions rather than absolute-energy subtraction. Coordinates convert nm→angstrom by 10; forces convert energy/angstrom to energy/nm by another 10. The frozen ASE convention is explicitly CODATA 2014, `eV→kJ/mol=96.48533288249877`, hence `eV/angstrom→kJ/mol/nm=964.8533288249877`. The independent exact-SI arithmetic gives 964.8533212331001840, about 8 parts per billion lower. This documents the frozen convention; no constants, thresholds or references were changed or requalified from that small difference.

AToM displacement keys are angstrom, timestep is ps (0.5 fs = 0.0005 ps), soft-core input configuration energies are kcal/mol (divide kJ/mol by 4.184). The adapter converts once and verifies normalized actual native parameters. Model CPU float64 is separate from OpenMM precision: Reference is double; an OpenMM CPU control does not prove universal double precision on every backend.

## Native ATM expression and forces

Let u0 and u1 be the complete child physical energies at the two fixed maps, and K the explicitly outside energy. For direction D=±1 set `u=D(u1−u0−UOffset)`. For u above Ub with Acore=a>0, put H=Umax−Ub, q=(u−Ub)/(aH), z=1+2q+2q². The admitted soft-core function and derivative are

\[
s=U_b+H\tanh\bigl(\tfrac a2\log z\bigr),\qquad
s'=\operatorname{sech}^2\bigl(\tfrac a2\log z\bigr)\frac{1+2q}{z}.
\]

Otherwise s=u, s′=1. The branches connect with derivative 1 at the threshold. The softplus contribution is

\[
g(s)=\frac{\lambda_2-\lambda_1}{\alpha}\log[1+e^{-\alpha(s-U_h)}]+\lambda_2s+W_0,
\qquad
g'=\lambda_2-\frac{\lambda_2-\lambda_1}{1+e^{\alpha(s-U_h)}}.
\]

The unequal-lambda branch requires positive alpha; the equal-lambda limit omits the softplus division. Then `U_k=K+u0+g(s)` for D=+1, and `U_k=K+u1+g(s)` for D=−1. With `w=g′s′`, forces are `FK+(1−w)F0+wF1` for D=+1 and `FK+wF0+(1−w)F1` for D=−1. This derives the force accounting on all coordinates, including cap-parent forces already redistributed natively.

Fresh nonlinear controls check both directions, below/at/above the soft-core join, a large softened perturbation and 10⁻³/10⁻⁴/10⁻⁵ nm force sweeps on Reference and CPU (20 cases). The expectations are independent harmonic and mixer algebra in the test oracle. All pass. Outside force is counted once, not multiplied by the mixing derivative.

Routing uses reserved physical group 1, outside group 0 and native parent group 31, with recursive ownership/mask checks; nested/duplicated/unowned forces reject. The project avoids the pinned stock name-based route, which misses honestly named PythonForces. Raw native tuple order `(u1,u0,ATM expression)` is translated into named records; the tuple is not mistaken for a complete-system energy.

## Complete reduced energies and exchange

Using exact SI R=N_A k_B/1000 = 0.00831446261815324 kJ/mol/K and T=300 K:

\[
\beta=1/(RT)=0.400907850142420138\ldots\ \mathrm{mol/kJ},\qquad v_k=\beta U_k.
\]

For configurations x,y at states i,j the product-target ratio gives

\[
\Delta=v_i(y)+v_j(x)-v_i(x)-v_j(y),\qquad p=\min(1,e^{-\Delta}).
\]

All four evaluations are fresh actual-worker energies, including outside terms and the declared schedule biases/constants. State-independent terms can cancel in the exponent but must still be present in saved total/reconstruction records. No additional weighting measure is declared for these same-temperature state swaps. Velocities need no temperature rescaling; workers/configurations stay identified while state labels swap.

`attempt_pair_exchange` is the sole adapter to the pinned upstream decision. Inspection of `atom_openmm.gibbs_sampling.pairwise_metropolis_sampling` confirms positive Δ uses exp(−Δ) and negative/zero Δ accepts without positive-exponent overflow; large positive values underflow toward rejection. Nonfinite project energies reject before decision. Four fresh actual-worker tests set only the random variate and compare cross energies/acceptance to independently evaluated harmonic formulas, including outside energy and stale-cache poisoning; they pass.

Each connected pair kernel preserves the product target. A fixed ordered composition of kernels therefore preserves it, but is not generally reversible as a whole sweep. Neither this fact nor a short acceptance count proves finite-time mixing/convergence. The software's pilot results do not make those claims.

## Analysis, binding signs and uncertainty

`reduced_potentials` reconstructs every state from u0_raw, u1_raw and outside raw energy, including its exact direction, soft-core and bias. Observed sampled totals validate scope/units. Its fresh context-parity test is a reconstruction check, not an independent derivation of the Hamiltonian; the independent algebra above and pair/force controls supply that separate evidence.

Samples retain unique IDs, walker/state identities and increasing sequences. Analysis validates every original observation, then makes identical state-contiguous matrices/counts for both estimators. MBAR/UWHAM weights satisfy `sum_n W_nk=1` and `sum_k N_k W_nk=1`; the adapter returns UWHAM probability weights divided by Nk, includes state constants and uses the pinned objective with its Hessian refinement. Large constant offsets are a gauge; unsupported nonconstant reduced ranges reject rather than being clipped. Covariance must be finite, symmetric and positive semidefinite within the admitted arithmetic allowance. Connected overlap is necessary, not sufficient for conformational convergence; low effective contributions are explicitly flagged.

For the Gaussian control, completing the square with u0=kx²/2, u1=k(x+d)²/2, K=kr x²/2 gives

\[
F_\lambda-F_0=\tfrac12\lambda kd^2-\frac{\lambda^2k^2d^2}{2(k+k_r)},\quad
F_1-F_0=\tfrac12\frac{k k_r}{k+k_r}d^2=1.5\ \mathrm{kJ/mol}.
\]

The fresh estimator test draws independent Gaussians with analytically derived means/variances, checks the 1.5 answer, both solvers/covariances, common/state offsets and deliberately repeated fixed-state samples. No MD sampling was rerun. For fixed-state correlated histories, the code uses the largest inefficiency from u0,u1,their difference and outside energy. If a correlated walker changes states, it explicitly raises `UnsupportedCapability`; exported exchange records are marked correlated. Relabeling those data independent would be an unsupported scientific assumption, not qualification by the program.

S05 uses bound-minus-bulk for ABFE, and `ΔΔG_A→B=ΔG_bind(B)−ΔG_bind(A)` for relative binding (negative favors B). For the declared separable translational case,

\[
\Delta G^\circ_{\rm bind}=\Delta F_{b-u}-RT\ln(V_{\rm eff}/V^\circ)+\Delta G_{\rm release,bound}.
\]

For a flat-bottom sphere radius r0 and wall k, w=√(2RT/k), integrating the full wall tail gives

\[
V_{\rm eff}=4\pi[r_0^3/3+r_0^2\sqrt\pi w/2+r_0w^2+\sqrt\pi w^3/4].
\]

V°≈1.66054 nm³ at 1 M. Fresh independent radial quadrature checks the wall tail and sign; a hard-sphere-only volume would be wrong. For directional schedules S05 defines `F0−F1=D1−D0−δFm`; an unequal midpoint requires a bridge or jointly connected overlap-qualified analysis. One must not assume that active soft-core midpoint expressions are identical.

Endpoint weights sum to zero, so common energy-zero shifts cancel. Variance of a weighted state estimate is `a^T C a`; with corrections it is the same form on the combined state/correction vector with the full joint covariance, including cross terms. Fresh missing-correction and joint-covariance controls pass. Required orientation, conformation, state counting, releases, standard volume and midpoint obligations need evidence; unresolved obligations or uncertain corrections lacking joint covariance withhold final value/error. BindingResult embeds and validates its thermodynamic definition, preventing a serialized final value from bypassing that ledger. The result record itself is still not independent uncertainty evidence.

The common workflow deliberately exports raw correlated observations and `binding_result=not_evaluated`. It has no equilibrium binding-domain or complete molecular correction qualification. G11/G12 require new actual molecular evidence, including matched spectator effects; subtracting arbitrary ABFEs from a two-ligand box would not prove closure.

## Preparation, saved state and transaction boundaries

New configuration admission checks typed/hash-bound artifacts, declared whole ligands/maps/runtime/settings and both-map geometry. Preparation owns one all-active physical copy, constraints, minimization and temperature phases, with seeds assigned before each Context. It is bounded warming, not density or equilibrium proof. Production is assembled through the same Hamiltonian builder and explicit adapter. The actual pinned worker first reads safe PDB coordinates, then loads the high-precision State; direct/worker energies and every real force are compared before the first step.

Fixed-window chunks seal row + portable State + checkpoint and publish with file/directory fsync and directory rename. Pair rounds seal both workers, state history and both host RNG streams together. The newer multistate path also validates all source entries, full permutations/inverses, state/walker/sample histories, RNG shape, exact saved clocks/steps, full restored coordinates/velocities/box/parameters and freshly evaluated raw energies/forces before continuing. Its whole-worker preflight completes geometry admission before energy checks/steps. Failure archives use cached state and preserve the original error even if a secondary archive operation fails.

The final v8 elapsed-clock proof rejects backward time first and bounds finite repeated floating-point addition using a finite outward-rounded envelope. Exact saved/restored clocks and integer steps are separate equality checks. Valid negative origins, large-origin stagnation and the recorded 100,000/999,999-step arithmetic remain covered by that unchanged proof; no long integration or repeated arithmetic campaign was needed here.

An incomplete transaction rejects by default. Explicit recovery first copies/preserves the failure tree, rolls back to the last complete boundary and replays, including both host RNG states. Nested files/manifests/directories are sealed and synced before publication; post-rename failures recognize the published boundary as authoritative. Derived summaries can be rebuilt without duplicate/lost scientific records. Local controller locks and fsync are not an actual power-loss, network-filesystem or cluster trial.

The older fixed-window and pair paths are weaker: the fixed workflow steps before restored geometry/energy admission and loops over only declared source entries; both older paths omit saved/actual clock agreement. [Findings](findings.md) reproduce these differences with real worker checkpoints and precisely limited sentinels. No upstream-only issue is inferred from them.

## References, physical failures and provenance

Chemical references are admitted only with complete recorded plan/geometry/order, neutral singlet, method/basis/settings/lock identity, successful retained convergence/output provenance and finite energy/gradient. Forces use minus the gradient with frozen Hartree/Bohr conversions. Like-composition/family energy differences are used; absolute energies of different compositions are not subtracted. Cap projection is applied once in reference diagnostics, while all real retained MM forces remain.

All 46 accepted G05 records match their digests, and the model/reference fixture trees are unchanged from retained scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`. Original failures and the corrected pilot receipt remain separate immutable records. Q5's accepted neutral local chemistry does not qualify the larger G07 approximation.

The saved G07 region comparison has seven net-force sensitivity exceedances, max 0.12165016265111903 eV/angstrom against 0.05. The one contact's baseline hybrid versus full-parent QM has component RMS 0.3951254 and maximum atom vector 2.0543877 eV/angstrom, against 0.05 and 0.15. Capped QM plus retained MM gives 0.3942092/2.0543877, showing the boundary/partition approximation dominates that contact's full-real error. Same-cap MACE/QM is smaller (0.0127151 RMS/0.0759817 maximum); complete-parent MACE still fails other prescribed limits. Scalar RMS values are not additive error shares. Full-parent separated QM is absent, so full-parent contact-energy attribution cannot be completed.

The ledger has one admitted full-parent pilot and 29 missing new references (19 full-parent, 10 alternate-cap). Charged time is 2325.6446500519996 s of 86400 s; the saved conservative remaining runtime screen is 122992.52458401839 s versus 84074.355349948 s left. Screening is not a measured prediction for unrun jobs, but the recorded continuation decision is false. Scratch/RSS limits and original receipts are preserved. This audit launches no QM and does not reset a budget or relax a tolerance.

The known stock OpenMM water-boundary artifact is separately supported by the retained upstream-only six-atom TIP3P diagnostic. The dense synthetic fixture's accepted box-face formatting is an input convention, not a runtime Hamiltonian patch or a general upstream repair. No new upstream defect is attributed in this pass.

The 224/233-atom, 64-water fixtures and three-worker/two-boundary/one-step pilots demonstrate coupled execution, finite forces, complete records and restart behavior. They cannot establish liquid density, physical stability over a long trajectory, adequate exchange mixing, converged affinity or chemical accuracy. General protein, host–guest RBFE chemistry, cluster parity, GPU devices and release performance remain the separately itemized backlog.
