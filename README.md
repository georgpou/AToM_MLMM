# AToM ML/MM

Build a cavity-inclusive ML/MM Hamiltonian for ATM absolute and relative binding free energies. Start with mechanical embedding, complete neutral ligands and capped neutral protein fragments. Keep the physical energy builder independent of coordinate transfer and analysis.

**Current state:** the reproducible CPU setup, real-weight MACE link example and M01 analytic CPU records/identity/inventory checks are implemented. [STATUS](docs/project-0/STATUS.md) records exact review/qualification results; GPU and full pretrained-model profiles remain separate.

## Start here

Create your next working branch from the current development successor, `m00-audit-m01-development`. It preserves the `m01-g00-environment-audit-v1` setup lineage. Preserve existing changes and use an unused branch name:

```bash
git status --short --branch
git fetch origin refs/heads/m00-audit-m01-development:refs/remotes/origin/m00-audit-m01-development
git switch --no-track -c m02-analytic-atm origin/m00-audit-m01-development
```

Work and push on the child branch. Keep main unchanged. Later tasks inherit the completed predecessor.

From the repository root, install and activate:

```bash
bash environment/cloud-cpu/install.sh
source /workspace/.onboarding/atom-mlmm/activate.sh
python -m pytest -q
```

Read [AGENTS.md](AGENTS.md), the [CPU setup guide](environment/cloud-cpu/README.md), and [development guide](docs/DEVELOPMENT.md). The installer carries the exact locks, wheels and source archives; a fresh agent needs no previous agent's filesystem. Its default prefix is external to the checkout and can be customized.

**Current development successor:** `m00-audit-m01-development`. M00's analytic design review and combined M01 acceptance for G00-T1/G01-T1/T2/T3 are recorded in [STATUS](docs/project-0/STATUS.md). Follow the [M02 implementation and audit handoff](docs/project-0/handoffs/M02-implementation-and-audit.md) to create a child branch and continue with G02, then G03 and their combined review. Model assets, physical-reference decisions and GPU qualification remain with their relevant profiles.

## Quick MACE calculation

The small MACE-OFF23 checkpoint is bundled for the user's academic use. After activation, run:

```bash
python examples/mace_link_cpu.py --output /workspace/.onboarding/atom-mlmm/mace-link-result.json
```

The [example guide](examples/README.md) explains the 13-real-atom GAFF/MACE fixture, its one massless link atom, loading policy, energy/force checks and model licence. The run uses local weights and needs no download.

## Roadmap

Milestones group outcomes; gates contain separately assignable tasks. The final gate carries each milestone's combined-review criteria, except the initial M00 design review. Log folders are created when first used; no placeholder README or empty report is required.

| Milestone | Outcome | Gates / closing review | Earlier milestone reviews | Log folder |
|---|---|---|---|---|
| [M00](docs/project-0/milestones/M00-architecture-review.md) | Shared architecture and contracts | Design review | None | `Worker_Log/Milestone_00/` |
| [M01](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | Reproducible inputs and contracts | [G00](docs/project-0/gates/G00-environment-and-provenance.md), [G01](docs/project-0/gates/G01-identity-partition-and-contracts.md); [combined review](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | [M00](docs/project-0/milestones/M00-architecture-review.md) | `Worker_Log/Milestone_01/` |
| [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | Shared transfer kernel | [G02](docs/project-0/gates/G02-analytic-force-in-native-atm.md), [G03](docs/project-0/gates/G03-atom-routing-and-integration.md); [combined review](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | [M01](docs/project-0/gates/G01-identity-partition-and-contracts.md#m01-combined-review) | `Worker_Log/Milestone_02/` |
| [M03](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | Capped mechanical hybrid | [G04](docs/project-0/gates/G04-link-boundary-and-derivatives.md), [G05](docs/project-0/gates/G05-local-model-adapter.md), [G06](docs/project-0/gates/G06-periodicity-and-interaction-ledger.md), [G07](docs/project-0/gates/G07-joint-cavity-ligand-atm.md); [combined review](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review) | [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | `Worker_Log/Milestone_03/` |
| [M04](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | Thermodynamic accounting | [G08](docs/project-0/gates/G08-thermodynamics-and-estimators.md); [combined review](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | [M02](docs/project-0/gates/G03-atom-routing-and-integration.md#m02-combined-review) | `Worker_Log/Milestone_04/` |
| [M05](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | Solvated preparation and workflow | [G09](docs/project-0/gates/G09-solvent-preparation-and-export.md), [G10](docs/project-0/gates/G10-restart-and-replica-exchange.md); [combined review](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | [M03](docs/project-0/gates/G07-joint-cavity-ligand-atm.md#m03-combined-review), [M04](docs/project-0/gates/G08-thermodynamics-and-estimators.md#m04-combined-review) | `Worker_Log/Milestone_05/` |
| [M06](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | Protein ABFE | [G11](docs/project-0/gates/G11-protein-abfe.md); [combined review](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | [M05](docs/project-0/gates/G10-restart-and-replica-exchange.md#m05-combined-review) | `Worker_Log/Milestone_06/` |
| [M07](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | Protein RBFE | [G12](docs/project-0/gates/G12-dual-ligand-rbfe.md); [combined review](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | [M06](docs/project-0/gates/G11-protein-abfe.md#m06-combined-review) | `Worker_Log/Milestone_07/` |
| [M08](docs/project-0/gates/G13-performance-and-release.md#m08-combined-review) | Release and Project 1 handover | [G13](docs/project-0/gates/G13-performance-and-release.md); [combined review](docs/project-0/gates/G13-performance-and-release.md#m08-combined-review) | [M07](docs/project-0/gates/G12-dual-ligand-rbfe.md#m07-combined-review) | `Worker_Log/Milestone_08/` |

Each gate owns its direct prerequisites, task instructions, planned tests and closing review. Read the assigned gate and its linked specification sections. M03 physical work and M04 analysis can advance separately after their actual prerequisites pass; both precede M05.

## Scientific references

[S01](docs/project-0/specs/S01-scope-and-invariants.md) defines scope; [S02](docs/project-0/specs/S02-architecture-and-dependencies.md) owns module boundaries; [S03](docs/project-0/specs/S03-data-and-interface-contracts.md) owns records and units. [S04](docs/project-0/specs/S04-embedding-and-model-contracts.md), [S05](docs/project-0/specs/S05-protocol-and-thermodynamic-contracts.md), [S06](docs/project-0/specs/S06-validation-and-tolerances.md) and [S07](docs/project-0/specs/S07-artifacts-and-qualification.md) cover physical energy, thermodynamics, validation and saved evidence. Use the [requirement locator](docs/project-0/REQUIREMENTS.md), [upstream references](docs/project-0/reference/sources.md) and [glossary](docs/project-0/reference/glossary.md) as needed.

Before real-model/protein claims, G05-T4 and G07-T4 require small chemical-reference and boundary-sensitivity checks with limits decided in M00 before results are inspected. Numerical agreement between two adapters alone does not establish chemical adequacy.
