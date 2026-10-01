# Current status

The branch is prepared for scientific implementation. The maintained CPU environment and local academic MACE link-atom example are implemented. Scientific platform modules and gate tests remain to be implemented; setup/example passes do not accept M00 or molecular gates. [Current preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) contains the tested snapshot and [validation/calculation evidence](../../Worker_Log/Documentation/evidence/Repository_Ready_v1.json.gz). Strict validation passed all nine checks; all five available project tests passed; documentation has zero errors and all eight self-tests pass.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

From the current tip of `m01-g00-environment-audit-v1`, create an unused child for M00/M01. Read the [development guide](../DEVELOPMENT.md) and the assigned gate's linked sections.

1. Complete the relevant [M00 design review](milestones/M00-architecture-review.md): Hamiltonian, cap rule, force/map/unit contracts, two-environment setup and proposed physical-reference checks. Record scoped decisions; choose reference methods/limits before inspecting results.
2. Implement the analytic CPU scope of [G00-T1](gates/G00-environment-and-provenance.md), then [G01-T1/T2/T3](gates/G01-identity-partition-and-contracts.md). Reuse the maintained setup and implement the gate's API/record/identity assertions.
3. Run applicable tests and record M01 combined review. Model/GPU tasks remain pending until their profiles need them. Continue through each later gate's real prerequisites.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 | not_started | Recorded review of relevant proposed contracts |
| M01 / G00-G01 | not_started | Implement and review analytic CPU API/identity/record scope |
| M02-M08 / G02-G13 | not_started | Follow [roadmap](../../README.md#roadmap) and gate prerequisites |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model chemical/protein qualification | not_run | G00/G05/G07 evidence and predeclared physical-reference limits |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
