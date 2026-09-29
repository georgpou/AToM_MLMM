# Gate evidence checklist

Use this checklist inside, or as an attachment to, the mandatory [worker log](worker-log.md) and [audit log](audit-log.md). Do not maintain another competing report. A small assignment needs only the applicable parts; a whole-gate review needs its complete stated scope.

- [ ] Identify the gate, smaller task IDs, requirements, snapshot, and specification revisions.
- [ ] Identify the exact software/model/input/hardware setup. Record versions, hashes, units, precision, and relevant runtime settings.
- [ ] Map each applicable requirement to the actual test, independent expected answer, and observed result.
- [ ] Record the commands, working directory, exit codes, numerical limits, measured errors, and raw-output locations.
- [ ] Distinguish passed, failed, skipped, not run, and genuinely not applicable checks. Give reasons.
- [ ] Include affected earlier tests and the checks that deliberately introduce mistakes, where required by the gate.
- [ ] Record unresolved audit findings, changed assumptions, and any evidence invalidated by this change.
- [ ] For full acceptance, confirm that all required parts work together in the audited snapshot. Link the independent audit and its exact accepted scope.

The field names for scientific results remain defined by [S07](../specs/S07-artifacts-and-qualification.md). The log filenames and handoff rules remain defined by [Worker_Log](../../../Worker_Log/README.md).
