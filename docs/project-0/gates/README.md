# Gates: pick one testable task

Each gate page starts with why the work matters, the expected result, and a short reading route. It then lists smaller tasks, expected checks, and the exact handoff location. Task IDs such as `G01-T1` remain stable across worker attempts.

| Gate | Work | Earlier gates needed | Worker log from repository root |
|---|---|---|---|
| [G00](G00-environment-and-provenance.md) | Check the software and record exactly what is installed | M00 review | `Worker_Log/Milestone_01/Gate_00_vN_worker.md` |
| [G01](G01-identity-partition-and-contracts.md) | Give every atom a reliable identity and define shared records | [G00](G00-environment-and-provenance.md) | `Worker_Log/Milestone_01/Gate_01_vN_worker.md` |
| [G02](G02-analytic-force-in-native-atm.md) | Check ATM using energies and forces with known answers | [G00](G00-environment-and-provenance.md), [G01](G01-identity-partition-and-contracts.md) | `Worker_Log/Milestone_02/Gate_02_vN_worker.md` |
| [G03](G03-atom-routing-and-integration.md) | Make sure AToM evaluates and integrates every intended force | [G01](G01-identity-partition-and-contracts.md), [G02](G02-analytic-force-in-native-atm.md) | `Worker_Log/Milestone_02/Gate_03_vN_worker.md` |
| [G04](G04-link-boundary-and-derivatives.md) | Check one link atom and the forces on its real parents | [G01](G01-identity-partition-and-contracts.md), [G02](G02-analytic-force-in-native-atm.md) | `Worker_Log/Milestone_03/Gate_04_vN_worker.md` |
| [G05](G05-local-model-adapter.md) | Check one real ML model and its adapter | [G04](G04-link-boundary-and-derivatives.md) | `Worker_Log/Milestone_03/Gate_05_vN_worker.md` |
| [G06](G06-periodicity-and-interaction-ledger.md) | Check periodic images and which classical interactions remain | [G04](G04-link-boundary-and-derivatives.md), [G05](G05-local-model-adapter.md) | `Worker_Log/Milestone_03/Gate_06_vN_worker.md` |
| [G07](G07-joint-cavity-ligand-atm.md) | Combine the capped fragment, ligand, model, and ATM | [G03](G03-atom-routing-and-integration.md), [G04](G04-link-boundary-and-derivatives.md), [G05](G05-local-model-adapter.md), [G06](G06-periodicity-and-interaction-ledger.md) | `Worker_Log/Milestone_03/Gate_07_vN_worker.md` |
| [G08](G08-thermodynamics-and-estimators.md) | Check the free-energy calculation against a known answer | [G02](G02-analytic-force-in-native-atm.md), [G03](G03-atom-routing-and-integration.md) | `Worker_Log/Milestone_04/Gate_08_vN_worker.md` |
| [G09](G09-solvent-preparation-and-export.md) | Add solvent and hand the prepared system to a worker | [G07](G07-joint-cavity-ligand-atm.md), [G08](G08-thermodynamics-and-estimators.md) | `Worker_Log/Milestone_05/Gate_09_vN_worker.md` |
| [G10](G10-restart-and-replica-exchange.md) | Check restart, process boundaries, and replica exchange | [G09](G09-solvent-preparation-and-export.md) | `Worker_Log/Milestone_05/Gate_10_vN_worker.md` |
| [G11](G11-protein-abfe.md) | Run the first protein ABFE example | [G10](G10-restart-and-replica-exchange.md) | `Worker_Log/Milestone_06/Gate_11_vN_worker.md` |
| [G12](G12-dual-ligand-rbfe.md) | Run the first two-ligand RBFE example | [G11](G11-protein-abfe.md) | `Worker_Log/Milestone_07/Gate_12_vN_worker.md` |
| [G13](G13-performance-and-release.md) | Measure cost and decide what the release actually supports | [G11](G11-protein-abfe.md), [G12](G12-dual-ligand-rbfe.md) | `Worker_Log/Milestone_08/Gate_13_vN_worker.md` |

The matching audit uses the same name with `_audit.md`. Keep both in the parent milestone folder. Read [the logging rules](../../../Worker_Log/README.md) before choosing N. All listed dependencies require evidence for the features the task uses; unsupported profiles cannot pass by omission.

Return to [the roadmap](../README.md), [milestones](../milestones/README.md), or [current status](../STATUS.md).
