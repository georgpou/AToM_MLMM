# Supported setups: what each level of evidence means

A component saying it can support a feature is not proof that the complete setup works. A simple environment-dependent test is not a real electrostatic embedding. This initial matrix contains no numerical evidence from a live repository. Actual results belong in the worker/audit logs and [status](STATUS.md), with the tested setup stated explicitly.

| Physical provider | Protocol | Purpose | Current evidence in this package | Primary gates |
|---|---|---|---|---|
| Analytic local | ABFE one group | Coordinate, energy, units, ownership | Planned; not_run | G02-G03 |
| Analytic local | RBFE two unequal groups | No one-ligand assumptions in common code | Planned; not_run | G02-G03 |
| Analytic environment-coupled | ABFE one group | Full MM derivatives and mapped-environment reevaluation | Planned; not_run | G02, G04, G07 |
| Analytic environment-coupled | RBFE two groups | Protocol/provider independence | Planned; not_run | G02-G03, G07 |
| Local MACE + mechanical caps | Toy transfer | Native/adapter/link/PBC composition | Planned; not_run | G04-G07 |
| Local MACE + mechanical caps | Solvated workflow | Preparation, restart, exchange | Planned; not_run | G09-G10 |
| Local MACE + mechanical caps | Protein ABFE | Molecular absolute-binding profile | Planned; not_run | G11 |
| Local MACE + mechanical caps | Protein RBFE | Molecular relative-binding profile | Planned; not_run | G12 |
| Actual electrostatic embedding | ABFE or RBFE | Future new physical profile | Deferred; unsupported by this plan's numerical evidence | New extension gates required |
| Long-range/charge-aware new model | Either protocol | Future model/periodic bookkeeping | Deferred; unsupported by this plan's numerical evidence | New model/embedding qualification |
| Metals/reactive/adaptive regions | Either protocol | Future chemistry/method development | Out of initial scope | New scientific specification |

CPU/GPU, precision, timestep, model hash, environment lock, constraints, box convention and ensemble subdivide every relevant row. G13 admits only profiles with the required evidence. Completing one row cannot silently qualify its neighbor.

For each future admission, record: declared capabilities, applicable contracts, executed tests, fixture/source/model identities, physical limitations, skipped/unavailable checks, reviewer and evidence locations. A generic `supports_electrostatic: true` flag is not an admission mechanism.

The first admitted profile can be `core-analytic-cpu`, without actual neural weights. Mark real-model loader tests not applicable to that narrow claim; do not count them as passes. Upgrade the G00 asset/loader evidence before G05 and qualify the complete mechanical model combination in later gates. See S07 for applicability versus outcome.
