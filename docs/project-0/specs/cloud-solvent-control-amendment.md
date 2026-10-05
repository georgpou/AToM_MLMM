# Bounded explicit-water cloud control amendment

**Status:** scientific definition and bounded implementation accepted for scope by the G09 v3/v4 and G10 v1 independent reviews; G09-R2 closed. This extends technical coverage; it does not qualify liquid density, molecular accuracy or full M05.

## Scientific definition and rationale

Reuse the accepted capped-fragment ABFE/RBFE solute, fixed ML membership, complete ligands, 0.109 nm protein cap and orthorhombic-pme-v1 mechanical ledger. Append eight neutral rigid TIP3P waters from the locked OpenMM `tip3p.xml`. Preserve all solute particles, charges, exceptions and bonded terms; waters remain classical. The frozen source/force-field hashes, masses, 24 water constraints and actual serialized PME settings are in each input. NVT is 300 K with 0.0005 ps LangevinMiddle steps, cutoff 0.9 nm, LJ switching at 0.75 nm, PME tolerance 1e-7, alpha 4.4 / fixed 64 cubed mesh, dispersion correction disabled, and a fixed 6.4 nm orthorhombic box.

The waters surround both contact and separated placements. This sparse control makes full solvent derivatives and export/restart affordable on the two-CPU/8-GiB cloud machine. It does not establish a homogeneous liquid or replace later dense-solvent preparation.

Periodic harmonic static anchors use `k/2 * periodicdistance(r,r0)^2`. The existing vacuum Cartesian anchor remains unchanged. Molecule/image reconstruction must not change an anchored periodic configuration's energy or force. This corrects the previously unexercised active periodic-anchor case; the independent image test initially measured 50.567 rather than 0.007 kJ/mol with the Cartesian expression. No earlier accepted active periodic-anchor evidence is claimed. The minimum-image harmonic is only differentiable away from half-box seams; the bounded profile does not admit those excursions as a smooth restraint domain.

## Requirements and evidence

G09-01 through G09-05 / P0-REQ-003,005,012,015,018,020,021 cover full static-solute/image clearance, ligand-water coupling at both maps, unchanged solute/ML identities, all-active preparation/constraints, actual PDB/System/State parity, full real forces, raw-state reconstruction and both-map failure preservation. S04 PME accounting and S06 energy/force and step-sweep limits are unchanged. G10-03/04 cover a single actual-worker pair exchange, fresh four-entry reduced-energy matrices including outside terms, fixed walker identities, state changes and checkpoint/portable-State history. The adapter delegates the decision to pinned AToM `pairwise_metropolis_sampling`; it does not create an asynchronous exchange controller or qualify correlated-walker estimators.

## Migration and rejection

Existing nonperiodic inputs/anchors retain their definition. Periodic inputs explicitly declare their cell and hashed physical System; the common runner selects the existing periodic builder convention. Triclinic/unsafe PME cells, unknown settings, altered source/assets/runtime, incompatible exchange Hamiltonians and invalid state/walker labels are rejected. Old sealed worker Systems remain frozen; resume already requires identical bundled source and profile, so this change cannot silently alter an existing attempt. Relocated old attempts use their own bundled source. Any broader periodic restraint or solvent profile needs independent evidence.

Failures retain original cached State/checkpoint and both transformed coordinate States without energy/force reevaluation. Raw mapped States preserve nonfinite XML values and copy cached parameters/velocities; their energies are not reevaluated and they are diagnostic artifacts.

## Reviewer decision

The [G09 v3 audit](../../../Worker_Log/Milestone_05/Gate_09_v3_audit.md) accepts the sparse-water/PME/minimum-image-anchor definition. The [G10 v1 audit](../../../Worker_Log/Milestone_05/Gate_10_v1_audit.md) accepts the single pair-exchange boundary for scope. V3 exposed G09-R2: a secondary archive error obscured the original scientific failure. The [G09 v4 audit](../../../Worker_Log/Milestone_05/Gate_09_v4_audit.md) closes R2 on the frozen repair submission and carries forward both scientific and pair-scope acceptance. Available artifacts are attempted independently; primary provenance is written first, and secondary archive errors are explicit metadata/exception notes displayed by the CLI. The v3 submission stays frozen. Prior G05/G07 physical failures, all reference artifacts, the cumulative QM ledger, G08/M04 acceptance and hardware limitations are unchanged.
