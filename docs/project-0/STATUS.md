# Current status

M01's analytic CPU implementation is ready for independent combined review on `m00-audit-m01-development`, code snapshot `141c7fbcf2c5407e7880512d5481639bdc81bf57`. [G00 worker](../../Worker_Log/Milestone_01/Gate_00_v1_worker.md) records exact CPU APIs/provenance; [G01/M01 repair worker](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md) records identities, fixed partitions, immutable versioned records, capability rejection, MM inventory and evidence validation. The full available suite passed 47 tests; the analytic selection passed 46 with one model test deselected. Strict environment validation passed all nine checks. [Repair validation evidence](../../Worker_Log/Milestone_01/evidence/M01_v2/validation.json.gz) and [complete environment identity](../../Worker_Log/Milestone_01/evidence/M01_v1/environment-manifest.json.gz) identify the tested profile. These results do not accept a molecular gate.

The [independent M00 audit](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) accepts scientific contract version 1 for G00-T1/G01-T1/T2/T3 on `core-analytic-cpu`. Full M00 physical-reference closure remains open: exact G05/G07 references, quantum method/settings and profile limits need a separate reviewed decision before comparison results are inspected. The prior [repository preparation record](../../Worker_Log/Documentation/Repository_Ready_v1_worker.md) remains setup/example provenance.

## Available calculation

The academic MACE-OFF23-small checkpoint and its pinned provenance/licence are carried in `models/mace-off23-small/`. Run [the CPU ML/MM link example](../../examples/README.md) after activation. The real-weight single point has 13 real atoms and one massless link site; it checks full real forces, both boundary-parent derivatives and scoped loading. Chemical, protein, periodic, ATM and GPU qualification remain with their owning gates.

## Next work

The [v1 independent combined review](../../Worker_Log/Milestone_01/Gate_01_v1_audit.md) required M01-R1/R2 repairs. Both have failing/passing regressions in [v2](../../Worker_Log/Milestone_01/Gate_01_v2_worker.md); independent closure and combined acceptance remain pending. After acceptance, start [G02](gates/G02-analytic-force-in-native-atm.md) from this development predecessor. Keep G00 model/GPU profiles pending until needed, and resolve M00 physical-reference choices before any G05/G07 reference comparison.

| Scientific scope | Status | Next condition |
|---|---|---|
| M00 / analytic CPU design | accepted_for_scope | [Independent version 1 design review](../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md) |
| M00 / physical-reference closure | blocked | Predeclare/review exact G05/G07 reference inputs, method, metrics and limits |
| M01 / G00-T1, G01-T1/T2/T3 | ready_for_review | 47-test result; independent closure of M01-R1/R2 pending |
| M02-M08 / G02-G13 | not_started | Follow [roadmap](../../README.md#roadmap) and gate prerequisites |
| GPU profile | not_run | Separate environment/hardware and owning-gate numerical checks |
| Real-model chemical/protein qualification | not_run | G00/G05/G07 evidence and predeclared physical-reference limits |

## Retired audit distractions

The prior documentation/source-anchor delivery and audit workflow are superseded by the current maintained guides and scientific specs/gates. P0-REQ-033, G05-T4/G07-T4 and the substantive derivative/map/reference checks are now in their owning documents. There is no prerequisite to recover an old overlay or complete another documentation audit. Their scientific decisions remain part of normal M00 review.

The MACE smoke loading-policy bug is repaired after both imports and has a real failing/passing regression. The Cloud fallback now targets this development branch and is tested with real disposable Git branches, including failure propagation and checkout preservation.

The existing-link OpenCL and optional ML acceleration warnings were nonblocking for the tested CPU scope. No current exit-propagation defect reproduced the old driver report. Reopen these only for new relevant failing evidence or qualification of that hardware/profile; leave the historical cause unknown.

Historical plans, audits, failed probes and duplicate installers remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368`. They are not required onboarding. Keep one concise current task log and update this status from actual results; only a recorded independent review can accept a gate/milestone.
