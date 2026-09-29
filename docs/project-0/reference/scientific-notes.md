# Scientific notes retained from the larger plan

This file collects cross-cutting reasoning that should not be copied into every gate. The shared specifications fix current proposed behavior; these notes explain diagnostics and later decisions.

## A diagnostic energy is not a free-energy correction

First identify the actual retained/removed classical terms under the admitted periodic convention. Then specify a scientifically defined alternative Hamiltonian. If it adds an energy difference delta U_s at endpoint s, its endpoint free-energy change is

$$\delta F_s=-RT\ln\left\langle e^{-\delta U_s/(RT)}\right\rangle_{s,\mathrm{hyb}}.$$

The average is over the original hybrid endpoint ensemble. The correction to a bound-minus-bulk result is delta F_bound minus delta F_bulk. A mean and standard deviation of delta U do not evaluate this exponential average or establish statistical overlap; rare configurations may dominate it.

Treat bulk-placement, box-size and boundary/region sensitivity separately from sampling error. If the declared physical approximation is too large, stop and choose a better-defined Hamiltonian or narrower application. Do not add a state-dependent switch that uses ML 'when bound' and MM 'when bulk' as an emergency repair.

## Model data and local disconnected fragments

For an additive local architecture, a graph with no intercomponent edges may enforce additivity. This does not require arbitrary 10-20 Angstrom separated training pairs merely to teach geometric disconnection. The result concerns the ML contribution, not the complete solvated hybrid energy; it does not automatically apply to long-range or charge-aware models.

Future useful data may include ligand conformers, exactly capped fragments, bound/contact geometries and the compressed/boundary distortions encountered in qualification. Charges, multiplicities, cap conventions and model energy definitions must match deployment. Hold out trajectory families or configuration sources rather than evaluating on nearly duplicate frames. Fine-tuning is not a repair for wrong units, maps, force ownership or unsupported model inputs.

## Performance arithmetic

Separate context construction, model loading, first evaluation and steady-state stepping. Synchronize accelerator timing. For timestep dt in fs and step time t in seconds:

$$\mathrm{ns/day}=0.0864\,dt/t.$$

For Nw windows, Nr independent repetitions, Tns nanoseconds per window and effective throughput s ns/day per occupied GPU:

$$\mathrm{GPU\ hours}\approx 24 N_wN_r T_{\mathrm{ns}}/s.$$

Do not double-count windows if measured throughput already aggregates them. Wall time and total GPU use differ. A larger timestep is not a pure backend speed improvement. Profile before implementing a new neighbor kernel, reducing the ML region, or training a smaller model.

## Path to Project 1

Project 0 establishes the declared numerical and thermodynamic platform. Project 1 evaluates ordinary noncovalent systems and the physical usefulness of cavity-inclusive ML/MM. Start with matched all-MM, ligand-only and cavity-inclusive comparisons on a small well-characterized series. Keep cavity, caps and model definitions fixed where cancellation is intended.

Experimental disagreement can arise from sampling, preparation, protonation, force-field cross interactions, embedding or model chemistry. Experimental agreement cannot prove that an implementation has the right gradients or correction signs. Later fine-tuning should test ligand-only versus cavity-plus-ligand training with appropriate independent data, not tune hidden corrections to match affinities.

Actual electrostatic embedding, metals and covalent reactions require new physical definitions and possibly new thermodynamic cycles. The current contracts make the transfer engine reusable; they do not solve those future chemistry problems.
