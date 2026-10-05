# M05 denser water and exchange transaction definition

**Status:** accepted_for_scope by the [G09 v5 audit](../../../Worker_Log/Milestone_05/Gate_09_v5_audit.md)
and [G10 v2 combined audit](../../../Worker_Log/Milestone_05/Gate_10_v2_audit.md),
2026-10-05 UTC. The initial construction/transaction definition was frozen before
results; the separately identified post-diagnosis fixture representation is
explicitly covered by that review. Earlier sparse/vacuum definitions are unchanged.

## Denser local-water control

Reuse the original capped ABFE/RBFE solutes, all inherited MM parameters, fixed
ML membership and complete ligands. Append 64 neutral classical rigid TIP3P
waters: 32 around each of the two ligand sites. The original 6.4 nm orthorhombic
cell, 2.4 nm transfer, 0.109 nm cap, Reference double/MACE CPU float64, NVT 300 K,
0.0005 ps, constraints, 0.9 nm cutoff, 0.75 nm LJ switching, PME tolerance 1e-7,
alpha 4.4/fixed 64 cubed mesh and disabled dispersion correction are unchanged.

Water candidates use a 0.32 nm cubic lattice with integer offsets -3 through 3
around the original first ligand carbon (input atom 26) and its translated site. Order candidates
by squared distance then integer coordinates. Use identical TIP3P geometry
(OH 0.09572 nm, HOH 104.52 degrees). Admit each whole water only when every
intermolecular atom pair at both maps has minimum-image Bondi ratio >= 0.80;
also check ligand-cap clearance and water-cap clearance at that same bound.
Compare against all real atoms, existing waters and the fixed cap geometry.
Take the first 32 admitted candidates per site, or fail construction. Geometry,
not energies or forces, determines selection. Freeze resulting hashes and
construction parameters in a new fixture version; never overwrite v1.

This is denser local hydration coverage (224/233 real atoms), not a homogeneous
liquid. It does not claim equilibrated density. All-active minimization and
10/100/300 K phases remain bounded workflow preparation. Start with the inherited
10 minimization iterations/two steps per phase and two steps per saved frame;
longer work requires measured resource preflight. S06 limits stay unchanged.
Required evidence includes preserved solute parameters/masses/constraints and
membership, brute-force geometry/images, independent both-map full forces,
cap-parent/solvent FD sweeps, actual worker export and raw pilot records.

The first ABFE sweep exposed an external Reference real-space periodic pair
artifact in the pinned `8.6.1.dev-b399af4` build: a reconstructed water hydrogen
at -1.11029e-17 nm contributed a +4.9022384396 kJ/mol jump. A six-atom system
created solely by stock OpenMM TIP3P reproduces a 0.11941625 kJ/mol real-space
jump (reciprocal contribution unchanged), with a 6.32435 kJ/mol/nm maximum
hydrogen force difference. This has no ML/caps/project builder. A single-water
stock control passes. Keep the reproducible diagnosis; further backend repair
is outside the user's method-development priority.

Synthetic water inputs therefore represent coordinates within eight box-length
floating-point ULPs of an integer box face as the exact face (7.10543e-15 nm in
this cell). Apply this only while formatting candidate fixture coordinates,
before the unchanged geometry selection. General runtime geometry and OpenMM
are unchanged. No meaningful coordinate, FD step, force, tolerance, constraint
or Hamiltonian term changes. Original failed inputs/records remain evidence;
the input representation needs independent review with the denser definition.
Old sealed inputs/bundles remain frozen and source-bound.

## Persistent pair exchange

The bounded controller uses two actual sealed workers sharing one complete
physical/alchemical/runtime identity at one temperature. Configurations,
velocities and stable walker IDs stay with their workers; only thermodynamic
state labels exchange. Select two explicit schedule states (first and last by
default); keep the complete schedule for raw-energy reconstruction.

One transaction contains both predecision samples, the adapter's fresh complete
four-entry energy matrix/decision, before/after state labels, both post-refresh
portable States/checkpoints and host RNG state. The pinned AToM routine consumes
both Python `random.choice` and NumPy legacy random draws. Persist both RNG states
as inert JSON, isolate their use from the caller's global RNGs and restore the
controller streams on continuation. No copied Metropolis implementation.

Each round starts in a unique `.pending-*` directory before integration. Persist
adapter phases `evaluated`, `decision`, `refreshed`; a failure to save a decision
is an error, never a rejection or successful swap. Hash-bind/fsync every final
artifact and publish the entire round by one directory rename plus parent fsync.
The committed round prefix is authoritative; summary/analysis files are derived
and rebuildable. Unique sample IDs bind run/walker/round; monotone walker sequences
and state histories are checked against the plan before executable loading.

Default resume rejects incomplete rounds without altering them. Explicit
`recover_pending=True` preserves each incomplete tree in a uniquely identified
failure archive, records rollback to the preceding committed boundary, restores
both workers' checkpoints and both RNG streams and replays the whole round.
Recovery never promotes partially completed work or silently drops a sample.
A completed rename remains authoritative even if later directory fsync/reporting
fails; resume verifies that round's hashes before using it. Single-controller
ownership is enforced with a nonblocking local process lock; mounted durable
storage is export-only and is not assumed to support local transaction semantics.

On failure, attempt both workers' cached original State/checkpoint and both
transformed coordinate-State archives independently, without energy/force reentry.
Preserve the original exception and secondary archive errors. Checkpoint replay
requires identical source/software/hardware profile. Portable-State restoration
checks fixed-coordinate observables and does not promise trajectory/RNG identity.

These changes affect G09-01..05 and G10-01..06, P0-REQ-003/005/012/015/018/019/
020/021/029/032. No raw field, physical Hamiltonian convention, cap derivative,
ensemble or numerical tolerance is changed. Old bundles use their exact frozen
source and cannot silently migrate. Correlated exchange records support exact
energy reconstruction; exchanging-walker statistical estimation remains
unqualified and no affinity is reported.

## TPU scope and review decision

TPU experiments use a separate profile and the identical approved checkpoint.
OpenMM remains CPU; an isolated MACE result cannot establish full-engine speedup.
Actual TPU hardware and arithmetic precision must be demonstrated. Unsupported
float64/operators, CPU fallback or missing hardware must be reported explicitly;
no untrained model, replacement weights, silent float32 or CUDA substitution.

The canonical audits accept the bounded denser control and transactional exchange
technical scope on scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`,
frozen submission `bc6fd520308fba7e7448929138eb91e80ca6f063`. Notebook delivery
does not supply actual Colab/TPU evidence or close full M05/M03.
