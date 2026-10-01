# Repository preparation and local MACE link calculation — v1 worker

**Scope:** prepare this branch for practical CPU scientific development and run the user-requested academic MACE ML/MM/link-atom single point.
**Outcome:** ready_for_audit for this delivery; no M00, scientific gate or GPU acceptance.
**Finished:** 2026-10-01T16:32:47.342906+00:00.
**Snapshot:** `m01-g00-environment-audit-v1`, base `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`; tested working tree is delivered by this commit.
**Evidence:** [one compressed record](evidence/Repository_Ready_v1.json.gz) contains strict validation, real calculation, exact statuses and relevant regression logs.

## Changes

Removed 247 obsolete tracked audit/evidence/planning files and duplicate handouts/recipes from the active tree. Their original bytes remain in Git at the base commit. Onboarding now uses README, AGENTS, the CPU guide, development guide and live STATUS; the next assignment is relevant M00 review and M01 analytic CPU implementation.

Preserved every dependency lock, wheel, full upstream source and inventory; S02/S03 are byte-identical. Preserved all 32 original requirement rows and 82 planned test rows. Added the substantive scoped P0-REQ-033/reference, nonlinear derivative, fixed-map, cap force/torque, early two-ligand, every-boundary and independent reverse checks directly to their scientific specs/gates. All 93 planned nodes are unique, task-owned and covered by their gate commands. These are current proposed scientific requirements, not a reconstructed historical byte overlay or accepted M00 design; schema/units/architecture and existing numerical limits remain unchanged.

Repaired the MACE smoke after its calculator import and targeted Cloud fallback at the current development branch. Added three environment regression cases and two model-example cases. Bundled the unmodified 7.3 MB academic MACE-OFF23-small checkpoint with pinned provenance/licence after the user confirmed academic use. A frozen GAFF 2.2.20 ethane/methane fixture exercises one real carbon-carbon boundary and its massless cap via OpenMM-ML mechanical embedding and the ASE MACE calculator.

## Verification

Commands ran from the repository root after main activation, except the bundle hash check.

| Check | Command | Observed result |
|---|---|---|
| Maintained installer replay | `ATOM_MLMM_SETUP_ROOT=<independent-prefix> bash environment/cloud-cpu/install.sh` | Exit 0; all nine underlying checks 0. Reused the existing independently installed prefix. |
| Strict baseline | `python <independent-prefix>/validate.py --repository "$PWD"` | Exit 0; exact inventories, both pip checks, OpenMM CPU/Reference, ML/ATM smoke, separate Amber preparation, UWHAM and docs pass. |
| Available project suite | `python -m pytest -q` | Exit 0; **5 passed**. Actual model test runs offline in a fresh process. |
| CPU marker selection | `python -m pytest -m "not gpu and not model_assets and not slow" --collect-only -q` | Exit 0; 4 selected, 1 model-assets case deselected. |
| Real local model | `python examples/mace_link_cpu.py --output <result.json>` | Exit 0; 13 real atoms plus one massless link site, finite energy/forces and nonzero model force on both cap parents. |
| Documentation | `python tools/check_docs.py --self-test` | Exit 0; zero errors and 8/8 self-tests. |
| Integrity | `sha256sum -c bundle.sha256`, model/licence hashes and preservation checks | Exit 0; all 76 setup entries pass; protected package/scientific contracts unchanged. |

The MACE unsafe-loading regression initially failed after numerical checks, then passed with the second import cleanup. Both Cloud fallback cases initially selected the obsolete setup branch; they now select the development branch, preserve the fixture checkout and propagate installer statuses 0/17. The model-example tests initially detected the absent new entrypoint; actual numerical evidence comes from the subsequent real runs.

Tiny-step CPU nonbonded-energy rounding initially gave a maximum finite-difference discrepancy of 0.01349 kJ/mol/nm. Using the same Hamiltonian's Reference-platform energy oracle gives **0.00020694 kJ/mol/nm**, below the unchanged 0.005 absolute component limit. CPU/Reference energy difference is 1.8751598e-07 kJ/mol. The actual CPU total energy is -212834.88844269 kJ/mol, including MACE atom-reference energies; it is not a binding energy.

## Prior findings and handoff

A01's delivery hunt is superseded by the user-directed current scientific consolidation; its substantive checks are present and receive normal M00 review. A02's obsolete anchor consumers were removed and all current links pass. A03 is fixed and regression-tested. A04's OpenCL/optional acceleration warnings remain nonblocking for tested CPU work. A05's historical cause remains unknown, with no current propagation defect; new fallback tests preserve both statuses. A06's task pointers are replaced with the direct implementation path.

Proceed to the relevant M00 decisions and M01 G00-T1/G01 work on a child of this branch. No historical documentation repair/re-audit is a prerequisite. Real-model chemical references, protein/PBC/ATM workflows and GPU checks remain in their owning gates. No independent review, molecular trajectory or gate acceptance is claimed by this preparation.
