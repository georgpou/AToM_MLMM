# Batch B — general manifests and cap collections

**Worker:** gpt-6-luna/max; no subagents. Depends on A. Read S02–S04's builder/identity/boundary sections, G11/G12's deterministic requirements and the parent constraints. Do not redo accepted one-cap chemical-reference comparisons.

**Purpose:** Finish the common-engine implementation prerequisite B10, including the zero-cut mixed ligand-only control needed by later protein work. Multiple caps are an extension of the existing collection contract; new boundary chemistry is outside this task.

**Files:** `hybrid.py`, `embeddings/mechanical.py`, `schema.py`, `partition.py` and `models/analytic_boundary.py`; use a new `models/analytic_caps.py` for a collection probe if needed. Inspect `ledger.py`, `geometry.py`, `routing.py`, `endpoints.py`, protocol presets and `adapters/atom.py` only for collection assumptions. Extend `tests/unit/test_partition.py`, `tests/integration/test_boundary_ledger.py`; create `test_cap_collections.py`, `tests/contracts/test_general_input_admission.py` and a tiny `fixtures/two_cut_control/`.

**Interfaces:** Keep `build_physical(...) -> PhysicalBundle`, `resolve_partition(...) -> ResolvedPartition`, `PhysicalBundle.links`, full real/final/model maps and one/two-group `TransferDefinition`. Produce zero-, one- and two-cut examples using the same records. A new collection analytic probe must have explicit per-edge parameters and an importable callback; keep the existing single-cap callback/API intact. Report its exact signature to D.

## B1 — complete, explicit input admission

- [ ] Build a tiny neutral fixture with two distinct permitted C–C protein cuts, complete unequal ligand groups and deliberately interleaved real IDs. No ligand cut or shared MM cap parent. Freeze atom/bond/charge/multiplicity/parameter identities independently from the hybrid builder.
- [ ] Add structural rejection tests for partial ligands, stale/forged partitions, duplicate cap identity/parent, ring/peptide/disulfide/charged or ambiguous cuts, unknown model chemistry and inconsistent original MM masses/constraints/parameters. Keep existing rejected combinations rejected.
- [ ] Preserve neutral chemical-state declarations from the input through the resolved/sealed records, with explicit versioned compatibility if additional fields are needed. Do not infer a fragment's charge from a partial-charge sum or silently label arbitrary selected protein chemistry neutral/singlet. Validate every selected component against its explicit preparation/chemistry record.
- [ ] Support zero-cut **mixed** systems with complete disconnected ligand ML components and retained MM environment, as well as the existing all-ML zero-cut host control. Preserve interactions with the environment under the same ledger. This is required for ligand-only versus cavity-inclusive matched controls.

## B2 — construct and seal every cap from actual upstream output

- [ ] Replace the zero/one-count guards in `hybrid.py`, `seal_boundary_result` and `PhysicalBundle` with collection validation. Require a bijection between declared boundary edges and actual native H virtual sites, matched by mapped parent IDs/type/rule, not append order.
- [ ] For each link, validate positive fixed distance, zero mass/charge/LJ, model input index, final particle index and stable unique identity. Apply oldToNew to every real atom and ledger term. Record all actual cap distances and force ownership.
- [ ] Version the newly admitted boundary manifest explicitly. Retain version-1 zero/one semantics; use version 2 for the collection/general mixed extension and reject unknown versions. Do not retroactively broaden an old accepted profile merely by changing its prose.
- [ ] Generalize the weight-free probe to exercise every cap and a real MM environment derivative. Each analytic energy term needs one owner; avoid adding a ligand spring once per cap accidentally. Keep production cap redistribution native, with raw cap forces returned once.
- [ ] If pinned upstream construction cannot build an otherwise admitted collection, preserve a minimal upstream-only diagnostic and mark that part blocked. Do not patch vendored/upstream packages, replace locks or construct a second physics engine.

## B3 — independent force, map and ledger controls

- [ ] Write `test_two_cap_parent_cartesian_derivatives_both_maps`: for every real ML/MM parent, every x/y/z component and both full maps, compare forces with independent energy differences at 1e-3, 1e-4 and 1e-5 nm. Recompute virtual sites, do not constrain perturbed coordinates. Use existing S06 tolerances.
- [ ] Derive cap expectations from `h=a+d*n`, `A=d/|b-a|*(I-n*n.T)`; real contributions are `(I-A).T*Fh` and `A.T*Fh`. Verify a translation/rotation-invariant probe's force/torque balance. Do not apply that symmetry oracle to an externally restrained energy.
- [ ] Include a nearby MM influence, nonidentity particle permutation, exchanged complete unequal groups and map-dependent neighbor refresh. Removing one cap projection or one environment derivative must make the appropriate control fail.
- [ ] Check original/retained/dropped ledger ownership with two cuts, exclusions/cutoff/PBC where the current profile admits them, and caps absent from classical nonbonded accounting. Use fixed coordinates and the existing approved MACE asset for one small collection cross-check; this is derivative evidence, not chemistry acceptance.
- [ ] Export/reload the two-cap bundle in a fresh process. Check IDs, all parent forces, both maps, trusted loading and a bounded restart through A's common path. Keep full protein execution for D/HPC.
- [ ] Run the new test files and affected partition/boundary tests once after changes; rerun single-cap tests only where implementation changed their path. Commit and write `Batch_B_vN_worker.md`, including new manifest/probe contracts and the limits of the tested collection.

**Done:** common records/builder accept general admitted zero/one/two-cut examples and whole one/two ligands; all small full-force controls and reload checks pass. This does not accept every protein, arbitrary cap chemistry or the full G11/G12 physical gates.
