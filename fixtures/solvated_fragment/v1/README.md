# Sparse explicit-water controls

The [ABFE](abfe/config.json) and [RBFE](rbfe/config.json) configurations extend the
accepted 32/41-atom capped-fragment controls with eight neutral rigid TIP3P waters
(56/65 real atoms). Waters surround both ligand placements in a fixed 6.4 nm
orthorhombic cell. This is a solvent-coupling and runtime diagnostic with no
liquid-density, equilibrium or affinity claim.

Each manifest hashes the full SystemInput, unchanged ML partition and Snapshot,
and identifies the original solute file bytes. The SystemInput records the
locked OpenMM TIP3P XML digest, solute identity, masses, constraints and PME
convention. Solute charges, exceptions, bonded forces, cap definition and
complete ligand membership are retained. Solvent stays classical at both maps.
See the [amendment](../../../docs/project-0/specs/cloud-solvent-control-amendment.md)
and [runner guide](../../../examples/cloud_engine/README.md) for the declared
profile and commands.

Reproduction uses [build_solvent_control.py](../../../tools/build_solvent_control.py)
and the unchanged locked CPU environment. The source controls and older evidence
are preserved; generation requires an unused output directory.
