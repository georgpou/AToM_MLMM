# G09 technical CPU implementation plan

Prerequisite: accepted G08 exact-snapshot review. Use accepted G07 numerical
evidence; preserve open G07/M03 physical qualification. No quantum or affinity run.
The handoff authorizes inline autonomous execution in the existing checkout.

1. Add a frozen solvated fixture and a reproducible preparation script. Reuse
   exact ethanol-parent/methanol chemistry, GAFF/AM1-BCC parameters, baseline
   protein cut and pinned MACE asset. Load canonical TIP3P water coordinates and
   parameters from pinned OpenMM; exclude complete waters that clash with either
   complete solute map. Merge actual water terms into the single original
   NonbondedForce, preserving all solute terms. Declare box, water removal rule,
   immutable inputs/hashes, PME and disabled dispersion convention. Choose the
   transfer from full-solute/image clearance, without selecting by energy.
2. Establish failing assertions for both maps, retained ligand-water Coulomb/LJ
   energy/full forces and deliberate removal of either coupling. Implement only
   admitted ordinary TIP3P solvent assembly; retain fixed ML membership.
3. Extend project-owned preparation with explicit phase settings. All physical
   forces remain active for minimization and gradual NVT thermalization. Each
   temperature phase uses an explicit RuntimeSpec, conserves physical identity,
   and records its actual constraints, parameters, bounded steps and raw outcome.
   No pressure or density-equilibration claim.
4. Export actual AToM basename.pdb, basename_sys.xml, basename_0.xml plus sealed
   bundle, runtime, protocol/schedule/restraint obligations, atom/link/force ledger,
   environment and model manifests. Verify preliminary PDB coordinates and the
   high-precision State independently. Instantiate actual OMMWorkerATMSync using
   project-owned loading of the already assembled sealed System, rather than
   applying stock force assembly twice. Compare every real force/energy,
   coordinates, box, masses, constraints and parameters before a single step.
5. Run a bounded multiwindow pilot only after parity. Preserve all raw endpoint,
   softened, expression, outside and total energies, full state parameters,
   walker/sample/sequence/time identities and high-precision representative
   frames. Independently reevaluate all states and monitor cap parents, graphs,
   periodic clearance and nonfinite alternate geometries. Uncomputed corrections
   and inadequate sampling prohibit a final standard binding estimate.
6. Run five required G09 assertions, affected checks and available full CPU suite
   serially. Preserve failed attempts. Submit an unused G09 worker/evidence pair
   and exact source to actual GPT-6.1-sol/MAX review for technical CPU scope only.

G10 next: offline relocated trusted assets; real constructor reload; separate
checkpoint/State guarantees; fresh cross-state exchange matrix through pinned
AToM worker/replica mechanism; immutable complete output chunks and resume IDs;
CPU device evidence with GPU unavailable. Never claim combined M05 closure while
M03 physical acceptance remains open.

Implementation notes from pinned-source inspection:
- OMMWorkerATMSync runs real constructor/body/context methods in process.
- Worker constructor reads PDB positions, optionally applies constraints and
  evaluates, loads basename_0.xml, then restores ommsystem.cparams. Export must
  supply current complete parameters rather than relying on XML defaults.
- Stock OMMSystemABFE.create_system assembles ATM/restraints/barostat; the project
  loader must deserialize and validate the already sealed ATM System instead.
- Pinned TIP3P coordinate cube is 3 nm, 895 complete waters. Use explicit
  whole-solute/image clearance to choose a smaller transfer appropriate to this
  box; preserve original molecular geometry and baseline cap selection.
- Physical builder accepts one protein C-C cut, neutral complete ligand(s),
  one standard PME NonbondedForce, and no analytical dispersion correction.
- Canonical TIP3P rigid-water constraints apply to MM waters, never to derived
  caps. Preserve them through original-to-final particle maps.
- MACE recipe is inert on XML reload, resolves the pinned asset locally, and
  verifies bytes/licence before CPU float64 deserialization. Portable execution
  needs relocated code+asset manifests with old checkout/cache denied.
- Actual pinned Gibbs sampler takes a complete state-by-walker swap matrix; its
  exponent is U[i,y]+U[j,x]-U[i,x]-U[j,y]. Build it from fresh raw contexts, with
  state labels kept separate from walker identity.
- G11 has no prepared protein target; T4 lysozyme L99A is only a suggested
  candidate. Do not promote the capped fragment to a protein claim.

Further worker-contract details:
- AtomUtils(system) defaults to a zero-LJ parameter repair; the sealed loader
  must instantiate it with fix_zero_LJparams=False to preserve physics.
- Actual OMMReplicaATM expects REStateId/RECycle/REMDSteps/RETemperature and
  diagnostic globals. They are energy-independent metadata, requiring explicit
  optional worker assembly before sealing, not post-Context mutation. Existing
  analytic constructor defaults must remain unchanged.
- Actual OMMWorkerATMSync with compute=True exercises preliminary constraints/
  PDB energy before portable-State load, without asynchronous queues.
- PDB-generated chain/residue labels are not authoritative atom identities;
  ordered atom/link maps in the sealed bundle/manifest remain authoritative.
- Replica output basename must be a plain filename, even if worker load paths
  are absolute; exercise real replica constructors in a dedicated child working
  directory to contain inherited r0/r1 output behavior.
- Full-source protein/image minimum for transfer +1.0 nm in a 3-nm cube is
  1.1776497910374808 nm from a geometry-only minimum-image calculation.

User steering (2026-10-04): prioritize a tiny cloud engine exercise; reserve
T4 lysozyme L99A for HPC, and defer all Slurm questions/settings. User explicitly
accepts unqualified MLIP accuracy while requiring an easy common system/settings
interface. Choose 18-crown-6 + methanol (42+6=48 real atoms, neutral singlets,
H/C/O) over the larger cyclodextrin candidate for the cloud smoke test. Retain
32-atom capped-fragment force controls and a bounded canonical-water plumbing
check. Start host-guest in vacuum; implicit solvent needs separate admitted
physical ownership/coupling and must not silently replace the Hamiltonian.
Use one manifest-driven execution path for admitted original system/partition,
protocol/maps, phases, schedule, runtime and thermodynamic obligations. Preserve
model/source/environment identity, raw records and immutable attempts; provide
actionable errors before expensive startup for unsupported choices.
A static whole-host role must be declared honestly, not relabeled as protein.
Neutral whole-host ML membership needs an explicit minimal role/admission
amendment and the same connectivity/chemistry tests. No per-host physics engine.

Final submitted scope decision: user-prioritized vacuum common runner and three
small fixtures take precedence over the original solvent-first sequence. Solvent
assembly/coupling and actual exchange are deferred, not implemented or accepted.
Review G09-T2/T3 vacuum analogues and G10-T1/T3 checkpoint/State/offline/journal
subsets only; do not close G09, G10 or M05. Current source 34cc6ba adds 22 tests
to the inherited 437-test suite. A bounded host stability pilot will use 20 frames
per state at five steps/frame (100 steps, 0.05 ps per state). No QM is rerun.
