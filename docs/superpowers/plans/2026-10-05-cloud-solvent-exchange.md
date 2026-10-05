# Cloud solvent and exchange implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline; one independent review at the end. Preserve the existing branch and serialize scientific jobs.

**Goal:** Extend the common bounded engine with explicit classical water/PME controls and actual pinned AToM two-state exchange checks.

**Architecture:** Reuse the physical builder, periodic geometry, preparation and sealed worker. The runner admits the existing orthorhombic PME convention and records the actual box. AToM remains responsible for exchange decisions; project code supplies fresh complete cross-state energies.

**Tech Stack:** Unchanged locked Python/OpenMM/AToM/MACE CPU profile.

**Spec:** G09-T1/T2/T3, G10-T2 in `docs/project-0/gates/`; S04 periodic accounting; S05 raw potentials; S06 tolerances; the user's continuation handoff. The bounded scientific profile and implementation are independently accepted; G09-R2 is closed.

The precise physical/migration proposal is [cloud-solvent-control-amendment](../../project-0/specs/cloud-solvent-control-amendment.md).

## Global constraints

- Continue `m04-engine-readiness` from `8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1`; preserve earlier evidence and QM accounting.
- Reference double, MACE CPU float64, NVT 300 K, timestep 0.0005 ps, two threads; no new QM, GPU or production jobs.
- Retain complete ligands, fixed ML membership, cap parents and the existing PME/ledger convention. Dispersion correction disabled.
- Explicit small rigid TIP3P water controls in a 6.4 nm orthorhombic box are deliberately sparse. No density, equilibrium, implicit-solvent or molecular accuracy qualification.
- Same Hamiltonian at both maps; full solute/image clearance and nonoverlap including solvent; preserve all influencing real forces and failed states.
- Record exact water force-field source, constraints, PME and source/input identities. Old nonperiodic configurations remain valid; unsupported physics remains rejected.

## Review focus

1. Periodic images hide a clash or reconnect the separated ligand to any static solute atom.
2. Solvent accidentally enters ML membership, or its classical coupling/constraints disappear at export.
3. Live box is lost from saved snapshots, reevaluation or restart.
4. Exchange uses stale energies after state/coordinate restoration, or swaps walker identities instead of state labels.
5. Unsupported mixed definitions, state-dependent outside energies, or failures silently yield an exchange.

### Task 1: Periodic runner and explicit water control

**Files:** `src/atm_mlmm/workflow.py`; `fixtures/solvated_fragment/v1/`; `tools/build_solvent_control.py`; `tests/workflow/test_solvated_handover.py`.
**Interfaces:** Existing `load_configuration`, `_domain`, `_snapshot`, `run_configuration`, `resume_run`; existing `Snapshot.box_nm` and `orthorhombic-pme-v1` physical convention.

- [x] Write tests for image clashes/full static clearance, actual box preservation and periodic configuration admission. Run and observe rejection/lost-box defects.
- [x] Admit validated periodic inputs, use minimum-image distances, preserve actual periodic boxes, and select the existing periodic embedding.
- [x] Freeze ABFE/RBFE controls by appending rigid water from locked OpenMM `tip3p.xml` to unchanged solute MM inputs. Preserve solute forces/charges and partition; record hashes and explicit sparse scope.
- [x] Check retained ligand-water forces in both maps against independent MM/oracle and finite differences, preparation constraints/identity, actual worker reload and every saved cross-state potential; run bounded pilots/restart.
- [x] Run affected tests and full CPU suite; commit with worker evidence.

### Task 2: Actual two-state exchange boundary

**Files:** `src/atm_mlmm/adapters/atom.py`; `tests/workflow/test_replica_exchange.py`.
**Interfaces:** Consume sealed `WorkerRun.evaluate`, state parameters, snapshots, runtime and bundle identities; expose adapter `attempt_pair_exchange(workers, snapshots, state_ids, walker_ids)` returning explicit energies, exponent, decision and assignments.

- [x] Test fresh cross-state energies against independently evaluated potentials and pin upstream Metropolis draw at either side of its threshold. Test state-history/checkpoint restoration and incompatible identities.
- [x] Evaluate all four actual worker potentials, restore original coordinates/state before calling pinned AToM `pairwise_metropolis_sampling`, and apply accepted state labels through the actual worker method. Keep walker identities fixed; propagate failures.
- [x] Exercise on ABFE and unequal-ligand RBFE water controls, with nonlinear parameters/offsets and outside energies; preserve all evidence. This bounded exchange adapter does not add a production exchange controller or qualify exchanging-walker estimators.
- [x] Run affected tests and full CPU suite; commit and submit one sequential independent review, fix any important findings, and update STATUS/worker logs.

## Progress and rulings

- Recovered the published branch from a documentation-only checkout. Rebuilt unchanged locks at `/workspace/atom-mlmm-g09-v3`; old absolute activation path was absent. Setup validation passed. Initial failed bootstrap logs are preserved under `/tmp`.
- Scope ruling: sparse explicit-water controls establish coupling/export/runtime correctness while dense-solvent equilibration and full G09/G10/M05 acceptance remain open. This follows the handoff's small-system/resource boundary; the cost is that larger solvated systems still need their own evidence.
- Oracle ruling: compare worker coordinates/velocities to the exported high-precision State rather than the pre-export preparation snapshot. The established bonded periodic reconstruction can move complete water molecules by one cell. Keep exact State equality; no tolerance is relaxed. Cost if wrong: an unnoticed export-coordinate error, mitigated by exact State parity and independent physical/image oracles.
- Scientific ruling: use a minimum-image harmonic anchor for explicitly periodic inputs, preserving the vacuum Cartesian expression. The Cartesian anchor failed the independent periodic image oracle (50.567 versus 0.007 kJ/mol). The amendment is independently accepted for the bounded domain. Cost if wrong: a changed periodic restrained Hamiltonian; old artifacts/source are frozen and cannot silently resume with changed source.
- RED evidence: `/tmp/atom-mlmm-g09-v3-red.log` (11 expected failures); `/tmp/atom-mlmm-g09-v3-solvent.log` (periodic PDB vector/unit export failure); `/tmp/atom-mlmm-g09-v3-failure-red.log` (two missing mapped-State artifacts); `/tmp/atom-mlmm-g09-v3-anchor-red.log` (independent image-energy mismatch).
- GREEN submission evidence: 18 solvent checks, 8 exchange checks, 4 failure checks; final source passed **489 tests in 481.86 s**, no skips. The initial snapshot assertion incorrectly ignored canonical images and was corrected to compare the actual/exported State exactly.
- Full CPU run after the anchor/failure changes: **488 passed in 457.28 s**, no skips. A subsequent focused RBFE test exposed missing other-ligand bulk clearance (`DID NOT RAISE`); the guard now checks complete other ligands with the existing 0.65 nm threshold. That test and the final 489-test submission passed.
- Independent review of frozen `b11c16750ad111a2fcafcda7a2d51c6690254e97`: 28 affected passes, seven independent passes and one intentional contract failure. Scientific amendment and G10 pair scope accepted. G09-R2 is Important because a secondary archive error hides the scientific cause in the CLI and omits primary metadata. No Minor findings were deferred.
- R2 repair: 12 new regressions first failed; primary exception identity/provenance and every available independent artifact are now preserved. Archive errors are explicit metadata/exception notes and displayed by the CLI. Directory, State capture/serialization/write, checkpoint capture/write, both map writes and metadata replacement faults are covered, with no evaluation reentry or sample insertion. Source `027f8173babc13606afb24d96f58148704e38b1b` passes 19 affected and **501 full CPU tests in 498.74 s**, no skips.
- Focused sequential closure review on `09a85d979fe9fce2ceca23da74509846254df9b1`: **21 independent focused passes and six additional probes**, all 49 hashes matched. G09-R2 closed; bounded scientific/G09/G10 pair acceptance carried forward. No blocking or Minor findings remain. Root stayed idle during both review phases. Full gates/M05 and the stated later scientific/production profiles remain open.
