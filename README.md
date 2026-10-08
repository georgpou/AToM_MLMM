# AToM ML/MM

Capped mechanical ML/MM binding calculations using the pinned AToM-OpenMM
preparation and production APIs. The initial protein benchmark is **FKBP12 with
BUT, PRP and neutral DAP**, taken from AToM's own fragment example.

<a id="start-here"></a>

## Run the benchmark

Read the [benchmark and run guide](benchmarks/fkbp/README.md) for the ligand
chemistry, MM comparison modes, preparation settings and worker allocation.
From the repository root:

```bash
bash environment/cloud-cpu/install.sh
source /workspace/.onboarding/atom-mlmm/activate.sh
python scripts/run_benchmark.py plan
python scripts/run_benchmark.py setup --ligand but --mode cavity --output runs/fkbp
python scripts/run_benchmark.py prepare --ligand but --mode cavity --output runs/fkbp
python scripts/run_benchmark.py run --ligand but --mode cavity --output runs/fkbp --nodefile /absolute/path/nodes.local
```

`plan` only validates inputs and lists jobs. `setup` builds systems without MD;
`prepare` minimizes, warms up and anneals; `run` calls AToM's production scheduler.
Run directories are ignored by Git. CPU and Reference are the current model
profile; GPU execution and quantitative protein affinities remain unqualified.

## Repository layout

| Path | Purpose |
|---|---|
| `src/atm_mlmm/` | Shared physical builder, transfer/analysis records and narrow AToM adapter |
| `scripts/` | Benchmark stage launcher |
| `benchmarks/fkbp/` | Versioned receptor, ligands, source hashes and AToM settings |
| `tests/`, `fixtures/` | Numerical regressions and retained scientific references |
| `environment/`, `models/` | Locked environments and approved model assets |
| `docs/` | Usage, scientific contracts and current status |
| `tools/`, `examples/` | Reference/release utilities and small demonstrations |
| `Worker_Log/` | Current task records and required prior acceptance/reference evidence |
| `runs/` | Untracked generated systems, states, trajectories and logs |

This work starts from `before_HPC` at
`590cb5258696042b29856df37f6053ba820d2f56` on the child branch
`hpc-atom-benchmark`. Main and the predecessor remain unchanged.
The [history guide](Worker_Log/README.md) explains recovery of retired run data.
There are no active Colab notebooks in this checkout; notebook-era generated
evidence has been retired with the other closed-run artifacts.

Read [AGENTS.md](AGENTS.md), [CPU setup](environment/cloud-cpu/README.md),
[development](docs/DEVELOPMENT.md), and [STATUS](docs/project-0/STATUS.md).
Environment locks, cached replay inputs, approved weights, accepted audits and
chemical-reference data are retained. The shared CPU engine's bounded numerical
acceptance does not establish protein accuracy or cluster parity.

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
