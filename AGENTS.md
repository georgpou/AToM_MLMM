# Agent instructions

## Start and scope

The active benchmark workflow starts from `before_HPC` at `590cb5258696042b29856df37f6053ba820d2f56`; use the [benchmark guide](benchmarks/fkbp/README.md) for protein preparation and production. The [engine handoff](docs/project-0/handoffs/CLOUD-ENGINE-CONTINUATION.md) retains earlier scientific context. Retain the accepted setup and scientific lineage. Keep main unchanged and publish only your working branch. Preserve existing user changes; use the existing checkout unless isolation is actually needed.

Read [STATUS](docs/project-0/STATUS.md), the assigned gate and only its relevant specification sections. [README](README.md#roadmap) locates milestones; [DEVELOPMENT](docs/DEVELOPMENT.md) explains source layout, tools and test commands. [CPU setup](environment/cloud-cpu/README.md) is the environment authority. Historical audits are available in Git history and are not required onboarding.

For an assignment to finish M01, review the relevant M00 contracts, implement G00-T1 and G01-T1/T2/T3 on the analytic CPU profile, run their applicable checks and record the combined result. G00 model/GPU tasks stay pending until needed and available. For a smaller assignment, finish that scope and hand over its next dependency.

## Scientific rules

- Keep ML membership fixed and transfer complete ligands. Initial cuts/caps are on the protein; the transfer maps leave them undisplaced while ordinary dynamics moves them.
- Use the same physical Hamiltonian at both maps. Return forces on every influencing real coordinate, including MM atoms and cap parents. Recompute geometry-dependent inputs after mapping.
- The physical builder owns embedding, coupling and the MM ledger. Protocols own mobile groups, maps and thermodynamic meaning. Shared ATM/analysis consumes their records. Only `adapters/atom.py` translates AToM keys, units and routing.
- Support collections of mobile groups and full-real-force records from the first analytic tests. Keep model imports lazy at adapter boundaries and common records dependency-light.
- Count each physical force once and activate it in preparation and production. Preserve identities, units and distinct raw/outside/total/softened energies.
- Binding results require declared domains, signs, restraints, midpoint connection and correction obligations. Follow [S01](docs/project-0/specs/S01-scope-and-invariants.md) for supported chemistry/ensemble and explicit rejection of unsupported physics.
- Use independent energy/force oracles, finite-difference step sweeps and deliberate faults. Preserve failing samples and nonfinite results. Scientific definitions and tolerances require a documented rationale and review before change.
- Decide chemical-reference methods, inputs and numerical limits in M00 before looking at results. G05/G07 reference checks precede protein physical claims. Analytic architecture probes do not qualify actual electrostatic embedding.

## Implementation and tests

Establish the expected result, run a focused failing test, implement the smallest correct change and rerun affected checks. After a meaningful code change run the available CPU suite. A missing dependency, empty collection, skipped test or import success alone cannot establish a numerical pass.

Source modules belong under `src/atm_mlmm/`; `tests/`, `fixtures/` and `environment/` are root-relative. S03 defines shared records. Gate paths describe planned code until it is implemented. Create modules and fixtures as the task needs them; preserve the S02 boundaries.

Activate the main environment in every new shell. Keep its NumPy 2 stack separate from AmberTools' NumPy 1.26 environment. Preserve package locks and artifact verification. For a genuine dependency change, update and validate the affected profile deliberately. Do not silently download replacement weights or globally weaken checkpoint loading.

## Logs and handoff

Leave one concise worker log per assigned task at the folder/stem named in its gate. Create the folder when first used. Use an unused attempt number; the historical documentation attempts remain in Git. The [worker template](docs/project-0/templates/worker-log.md) lists the required facts: scope, base/result snapshot, changes, commands and actual outcomes, remaining limitations and next action. Keep larger validation output in a small evidence artifact or the run directory.

Update [STATUS](docs/project-0/STATUS.md) with actual task/profile evidence. It is the single live progress summary. Create a matching [audit log](docs/project-0/templates/audit-log.md) only when an independent review is performed. Self-checking is not independent approval.

## Acceptance

M00 review concerns scientific contracts and module boundaries. A gate needs its applicable tests on one reviewed snapshot; milestone closure also needs its closing gate's combined review. Record unavailable model/GPU profiles as pending. An accepted task or installation smoke does not accept a complete molecular gate.

Finish with the worker log, exact test results, branch/commit and next action. Reopen a retired environment warning only when new relevant evidence shows a real failure. Proceed with coding after actual prerequisites; recovering historical audit files is not a task prerequisite.
