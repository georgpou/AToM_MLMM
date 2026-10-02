# M02 v2 acceptance and publication

The independent **gpt-6-astra / high** reviewer accepted G02-T1/T2/T3,
G03-T1/T2/T3, both gates and combined M02 for `core-analytic-cpu` on exact
submitted snapshot `6015a652c4a9a9c968ab7933c07ac7bbb4573e12`, carrying repaired
source/input commit `33daa6bebd91c49ad87f822d48cfa87e600deb6d`. M02-R1/R2/R3 are
closed. The [G02 audit](../../Gate_02_v2_audit.md) and
[combined G03/M02 audit](../../Gate_03_v2_audit.md) are the authoritative decisions;
[independent evidence](../M02_v2_independent/README.md) preserves actual runs and
the additional 120 rejection/9 positive probes. Worker evidence remains
[separate](../M02_v2/README.md). Historical v1 decisions and all 28 handoff
milestone files remain unchanged.

[AcceptanceRecord](acceptance.json) covers all 16 stable gate checks and their
11 requirement IDs. [The recorder](record_acceptance.py) derives each stable
node and requirement from the unchanged gate specifications and verifies
passed parameter cases in the independent verbose outputs. It also checks
all 127 source/input hashes, the actual review references and schema round trip.
Its [command capture](acceptance-command.json) records the result.

Independent full suite: **238 passed**; analytic: **237 passed/1 deselected**;
original G02/G03: **78/38 passed**; new admission regressions: **74 passed**;
strict environment: **9/9**; upstream UWHAM: **1 passed**, three datasets.
Preserved admission replay rejects all 18 negatives and retains both restoration
positives. Numerical replay passes 66 comparisons, eight full-coordinate FD
sweeps and eight upstream history cases with unchanged limits. Trusted offline
stale-artifact detection remains effective. Separate core/Amber locks, scientific
definitions, full-real-force/map contracts and trusted loading are unchanged.

The closure/publication commit adds only audits, evidence and STATUS to the
reviewed snapshot. [Publication verification](publication-verification.json)
checks its source/input equality, preserved handoff and worker submissions,
ancestry and protected remote tips before committing. Its exact commit is
identified by `git log -1 --format=%H -- Worker_Log/Milestone_02/evidence/M02_v2_closure/README.md`.
Only `m02-analytic-atm` is published; main and `m00-audit-m01-development` remain
at their recorded tips. [Reviewer model history](reviewer-model-history.md)
answers the model-provenance inquiry without inferring unavailable labels.

Acceptance remains seven-real-atom nonperiodic analytic Reference/CPU transfer
architecture, fixed complete ligand groups, float64 callbacks and NVT timestep
at most 0.0005 ps. Molecular ABFE/RBFE, chemical/protein accuracy, caps, GPU/full
pretrained-model, periodic/actual electrostatic physics, binding/corrections and
full asynchronous preparation/restart/exchange qualification remain deferred.
M00 physical-reference choices remain open before G05/G07 chemical comparisons.
G04 and G08 may proceed separately under their own prerequisites; this task
stops at analytic M02 closure.
