# G09 bounded explicit-water controls — v3 worker

**Scope:** G09-T1/T2/T3 technical subsets on small capped ABFE/RBFE controls; same common runner, sparse rigid TIP3P, retained solvent coupling, orthorhombic PME, preparation/export/raw records and failure preservation. No full G09/M05 or molecular qualification.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-05T10:29:52.960176+00:00.\
**Model/version:** GPT-6-based Codex; exact model/version not exposed. **Reasoning setting:** not exposed.\
**Previous worker/audit:** [v2 worker](Gate_09_v2_worker.md) / [v2 audit](Gate_09_v2_audit.md).\
**Snapshot:** branch `m04-engine-readiness`, base `8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1`, tested implementation `5645db24f707adbdaff34dc7de6ac04b518d7d6b`. The following submission commit contains report/status/evidence only; the auditor records its exact SHA.

## Definition and decisions

Read AGENTS, STATUS/continuation and engine-readiness handoffs, runner/CPU guides, G09/G10, S02 force ownership, S04 periodic accounting/physical contract, S05 raw potentials, S06 numerical limits, S07 workers/artifacts/observables and the v2 audit. The [proposed amendment](../../docs/project-0/specs/cloud-solvent-control-amendment.md) is the exact new profile; independent review is pending.

The original 32/41 real-atom solutes gain 24 classical water atoms (56/65 real atoms). Solute particles, charges, exceptions, masses, bonds, ML partition, complete ligands and 0.109 nm cap are retained. Rigid TIP3P comes from hashed locked OpenMM XML. The 6.4 nm cell, 0.9 nm cutoff, 0.75 nm LJ switch, 1e-7 PME tolerance, fixed alpha 4.4/64-cubed mesh and disabled dispersion correction are explicit. NVT 300 K, Reference double, MACE CPU float64 and timestep 0.0005 ps stay within the bounded CPU profile.

Runner changes admit declared periodic inputs through the existing builder, preserve live boxes, and check minimum-image clashes and bulk clearance against the complete static solute, caps and other ligands. Actual periodic PDB export now attaches units to the complete box rather than individual vectors. Failure archives preserve the original State/checkpoint plus both fixed-map coordinate States without energy/force reentry or failed sample insertion; XML retains nonfinite values.

Rulings made:

- Sparse waters qualify coupling/runtime checks only. Dense-solvent equilibration and full gates remain open; larger systems need separate evidence.
- Reload coordinates/velocities compare exactly with the exported high-precision State, rather than a preparation Snapshot preceding periodic reconstruction. No tolerance is relaxed; an export error remains constrained by exact State and independent physical/image checks.
- Periodic anchors use minimum-image harmonic distance; vacuum Cartesian anchors are unchanged. The former Cartesian periodic expression failed the independent image oracle (50.567 versus 0.007 kJ/mol). This changes the previously unexercised periodic restrained Hamiltonian and remains proposed until review. Old sealed artifacts/source are retained, and source-identity guards reject silent migration.

## Actual checks

All scientific commands ran serially from `/workspace/AToM_MLMM` after `source /workspace/atom-mlmm-g09-v3/activate.sh`, with `OPENBLAS_NUM_THREADS=2` and `PYTHONPATH="$PWD/src"`. A replacement machine lacked the old installation; the unchanged locks were rebuilt at this prefix. Nine setup checks exited zero. Initial bootstrap/launcher failures remain in `/tmp`; no package, model or numerical limit was replaced.

| Command/check | Result |
|---|---|
| Baseline `python -m pytest -q` on the published source | 0; 461 passed in 414.00 s, no skips |
| Initial new tests before implementation | 11 expected failures: absent fixtures/API, rejected periodic input, missed image clashes/clearance, lost box |
| Actual-water preparation/export tests | Detected periodic PDB unit failure; repaired without changing PME/solute semantics |
| Failure-map and periodic-anchor regressions | Observed missing map files and image-energy mismatch, then passed after repairs |
| Focused RBFE other-ligand clearance regression | Observed `DID NOT RAISE`, then passed with unchanged 0.65 nm limit |
| `python -m pytest -q tests/workflow/test_solvated_handover.py tests/workflow/test_replica_exchange.py tests/workflow/test_failure_geometries.py tests/workflow/test_engine_restart.py tests/workflow/test_engine_failure_retention.py tests/workflow/test_worker_handover.py` | 0; 35 passed in 86.36 s before the final other-ligand regression; that additional regression separately passed |
| Intermediate full CPU suite | 0; 488 passed in 457.28 s |
| Final `python -m pytest -q --basetemp=/tmp/atom-mlmm-cloud-finalfull` | 0; **489 passed in 481.86 s**, no skips |
| `python -m atm_mlmm check fixtures/solvated_fragment/v1/abfe/config.json`; `run` for both water configurations with new outputs and `--trusted` | 0; **nine frames/18 sampling steps per control**, six preparation steps; complete 56/65 real-force arrays and unchanged boxes |
| `python -m atm_mlmm resume /workspace/cloud-engine-pilots/water-v3/abfe --trusted` | 0; completed attempt verified, no duplicate samples |
| `python tools/check_docs.py --self-test`; `git diff --check` | 0; zero documentation errors/eight self-tests; clean diff |
| Prior scientific artifacts/model/locks against base | No changed paths in M03/M04 evidence, chemical-reference data, models or environment; cumulative QM ledger unchanged |

Independent test oracles include raw native MACE plus independently evaluated retained MM, ligand charge/LJ masks demonstrating real solvent coupling at both maps, solvent O/H force component step sweeps (1e-3/1e-4/1e-5 nm), exact worker State/velocity parity, all-active preparation constraints, full cross-state reconstruction and both-map geometry/failure challenges. Established S06 limits are unchanged.

Full portable attempts are `/workspace/cloud-engine-pilots/water-v3/abfe` and `rbfe`. Initial CLI peak process RSS was 893,599,744 and 903,782,400 bytes respectively. No OOM/OOM-kill increments were observed. [Evidence](evidence/G09_v3/README.md) retains raw records, chunk States/checkpoints, settings, reports and 48 scientific source/input hashes; captures omit duplicate worker source/model/environment payloads and are not standalone installations.

## Limits and handoff

G09-R1 remains closed by the prior accepted audit and affected regressions. Sparse water controls establish numerical plumbing, not homogeneous liquid, equilibrium, affinity, MACE coverage/accuracy or full G09/G10/M05. Implicit solvent, GPU, pressure/virial and half-box restraint-seam behavior remain unqualified. Seven G07 sensitivity failures, pilot force failures, 29 missing new quantum references and the 2325.644650052/86400-second ledger remain unchanged. No new QM or production calculation ran. T4 lysozyme/Slurm work waits for the user.

Next: one independent G09 v3 / G10 v1 review of the frozen submission and amendment. Then specify dense-solvent preparation and persistent exchange/RNG/history coverage using new attempts. No independent acceptance is claimed by this worker.
