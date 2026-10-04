# Proposed admission: tiny cloud engine preflight

This amendment requests independent review for technical CPU scope. It does
not close G09, G10 or M05, and leaves G07/M03 physical qualification unchanged.
The user prioritizes a small cloud engine exercise, reserves T4 lysozyme L99A
for HPC, and defers cluster settings. No new quantum or long production run is
authorized by this amendment.

The shared partition admits `host` as an honest static role. Selected hosts must
be complete connected neutral singlet molecules. They are not protein fragments
and cannot be mobile transfer groups. Ligands still transfer whole; membership,
the protein C-C cut policy, cap distance/Jacobian, force ownership, units and
the existing element/chemistry restrictions are unchanged.

The new host fixture is 18-crown-6/methanol: 42+6 real atoms, H/C/O, two neutral
singlets, all atoms ML, vacuum, no caps. Original MM charge/LJ are explicitly
zero; this fixture does not qualify an MM parameterization. RDKit geometry
generation uses fixed ETKDG/MMFF seeds. A deterministic pose search considers
host oxygen order and outward/+z/-z approaches, admitting the first pose with
every host/guest distance at least 0.65 times summed Bondi radii. No model/QM or
binding score selects a pose. The rejected v1 pose and measurements remain
frozen; v2 uses the same threshold. The cutoff is a geometry guard, not a proof
of ML training coverage or experimental accuracy.

`workflow.py` consumes hashed typed SystemInput/PartitionSpec/Snapshot files,
explicit runtime/preparation settings, ABFE or RBFE, and an optional complete
typed ScheduleSpec. The initial runtime is nonperiodic Reference double NVT,
pinned MACE CPU float64, LangevinMiddle, timestep at most 0.0005 ps. Unsupported
solvent, CUDA, periodic workflow, integrator or undeclared settings reject.
Existing 32-atom ABFE and 41-atom unequal-ligand RBFE controls use this same path.

Preparation owns an all-active physical copy, bounded minimization, and strictly
increasing explicit temperature phases. Langevin seeds are assigned before
Context creation; velocities are seeded once and rescaled between fresh phase
contexts. Each phase records identity, actual temperature/timestep/mask/seed,
energy and maximum real force. This is not equilibrium or density qualification.

Only the AToM adapter owns pinned upstream translation and sealed worker loading.
The export includes actual PDB/System/high-precision State files, the sealed
bundle (maps, links, ledger, schedule, restraints), thermodynamic definition,
runtime, exact Python source, pinned environment declarations, model/license
and file hashes. Actual OMMWorkerATMSync construction executes preliminary PDB
evaluation and then loads the State. A sealed OMMSystem loader avoids adding
ATM/restraints/barostat twice and disables AtomUtils' zero-LJ repair. The common
evaluator adopts that actual worker Context after verifying System, integrator,
platform, routing and maps. Handover energy and every real force must match
before stepping at absolute 1e-8 kJ/mol and 1e-7 kJ/mol/nm, respectively.

The fixed-window pilot records unique explicit run/sample/walker/state/sequence
identities; full positions/velocities/forces; step/time/temperature/seed; complete
state parameters; and distinct raw/softened/expression/outside/total energies.
Both complete real maps are distance-guarded. Bulk guests clear all static
host/protein coordinates by model cutoff 0.45 nm plus margin 0.20 nm. Existing
model and cap validation runs on each actual evaluation. Saved raw records
reconstruct the full state matrix and are independently reevaluated in tests.
The unbounded vacuum pilot has no released ligand-domain or standard-state
definition: it deliberately does not run an estimator or return BindingResult.

Restart has a single-controller immutable journal of hash-bound JSON/State/
checkpoint chunks, published by directory rename with file and directory fsync.
Hashes, contiguous indices and explicit walker sequences are checked before
continuation. Same-profile checkpoint continuation and portable State restoration
have separate tests: only the former restores RNG continuation. Metadata, exact
bundled source, installed distribution identity and runtime profile must match.
Relocation is permitted; changing source/software is a new run. A complete
resume verifies the prefix without appending samples. Incomplete pending trees
and unknown entries reject and remain inspectable; automatic hard-crash repair
and concurrent controllers are outside this scope.

Fresh-process tests relocate the complete bundle, deny networking and reads
from the original checkout/run/caches, and continue actual workers using only
local assets. CPU device/float64 checks are inherited from the actual pinned
model loader and OpenMM Context validation. No GPU or multigpu evidence is
claimed. Solvent coupling, actual replica exchange, extended correlated-walker
analysis, protein qualification and combined M05 remain later work.
