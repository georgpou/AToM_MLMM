# Agent instructions

## Branch and environment handoff

The user requires working branches to retain the lineage from
`m01-g00-cloud-environment-setup`, never `main`; subsequent repair/milestone/gate
branches inherit their recorded predecessor. Read [AGENT_HANDOFF.md](AGENT_HANDOFF.md) before
starting. The completed independent setup/baseline
[audit](Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md) and
[STATUS](docs/project-0/STATUS.md) identify the current required repairs in
[NEXT_AGENT_REPAIR_HANDOUT.md](NEXT_AGENT_REPAIR_HANDOUT.md), before M00 or gate
implementation. Repair successors inherit the audit branch, retaining the setup
lineage; the original [audit handout](NEXT_AGENT_AUDIT_HANDOUT.md) remains scope
history. For dependency setup, use the [branch-contained setup guide](environment/cloud-cpu/README.md)
and run `bash environment/cloud-cpu/install.sh` from the repository root. It
supplies all 51 wheels and exact source archives, and creates **two separate
environments**: main ML/AToM with NumPy 2 and AmberTools with NumPy 1.26. Activate
main through `/workspace/.onboarding/atom-mlmm/activate.sh` (or your chosen
installation prefix). Do not assume another agent inherits installed filesystem
state, and do not use the old evidence-directory installer or an absent tarball.

## Scope and reading

Build the smallest correct cavity-inclusive ML/MM platform for ATM ABFE and RBFE. Project 0 establishes numerical and thermodynamic correctness plus limited, reference-based chemical adequacy on small systems; Project 1 tests broader physical usefulness. Do not turn one assignment into the whole project.

Read this file, the assigned task and its task-specific reading links, relevant [status](docs/project-0/STATUS.md), and prior findings. Inspect the actual checkout and preserve other work. Use the [roadmap](README.md#roadmap) only to locate an assignment. A milestone-only assignment means its first unblocked unfinished task unless the user explicitly requests its combined review. Record that choice. Historical plans and unrelated logs are optional, not default reading.

Source/test paths in gate pages are planned, not proof that files exist. Source modules are under `src/atm_mlmm/`; `tests/`, `fixtures/` and `environment/` are root-relative. Shared interfaces are defined in [S03](docs/project-0/specs/S03-data-and-interface-contracts.md). Follow the gate's explicit prerequisites for the features being used; a milestone's later combined review does not add a hidden implementation prerequisite.

## Non-negotiable rules

Keep ML membership fixed and include each transferred ligand completely. Initial cuts and caps are only on the protein; ATM leaves them undisplaced, but ordinary dynamics still moves them. Use the same physical energy definition at both coordinate maps. Return forces on every influencing real coordinate, including MM atoms and cap parents. Recompute geometry-dependent inputs after mapping. Never clip forces independently, replace nonfinite results with zero, or discard failing samples to hide defects.

The physical builder owns the energy, embedding and MM ledger; the protocol owns mobile groups, maps and thermodynamic meaning; shared ATM/analysis consumes those definitions. Only the AToM adapter translates upstream keys/units. Do not create separate complete engines for each embedding/protocol pair. Keep collection-based mobile groups, full-real-force records and early two-group/environment-force probes; these do not qualify actual electrostatic physics.

Count physical forces once and activate them in preparation and production. Preserve stable identities, units and distinct raw/outside/total/softened energies. Binding results require explicit domains, signs, restraints, midpoint connection and corrections. [S01](docs/project-0/specs/S01-scope-and-invariants.md) defines initial neutral, local-model, mechanical, fixed-volume/temperature scope and exclusions. Reject unsupported requests rather than silently changing physics.

## Work and changes

Read the expected assertion, write a focused failing test, verify its intended failure, implement the smallest change, and rerun affected checks. Missing dependencies are not proof that a regression test detects its intended defect. Scientific definitions and tolerances cannot be relaxed to obtain a pass. For real-model acceptance, complete the G05/G07 chemical-reference checks with predeclared limits; native/adapter agreement or a finite trajectory cannot replace them. A missing reference calculation can leave an implementation task complete but the relevant physical profile unqualified.

Changing units, energy/force meaning, caps, constraints, masses, periodic rules, signs, corrections or shared fields needs a recorded specification amendment: rationale, affected requirements/tests and prior evidence, migration/rejection policy, reviewer decision. Keep proposed decisions proposed until reviewed. Internal cleanup needs no extra design document. Do not reopen approved decisions without a relevant change.

Read the [environment guide](ATM_MLMM_Environment.md) only when installing or qualifying dependencies. Keep basic data tests independent of weights/GPUs. Record exact source/model identities; never load untrusted serialized artifacts, expose secrets, redistribute restricted weights or silently download replacements. Respect the assigned resource budget; do not launch expensive simulations, installations or extra agents unnecessarily.

## Logs and handoff

Every assignment, even partial or blocked, leaves a [worker log](docs/project-0/templates/worker-log.md). Use the gate's folder and stem, for example `Worker_Log/Milestone_01/Gate_01_v1_worker.md`; its independent review is `Gate_01_v1_audit.md` in the same folder. Create absent folders when needed. M00 design reviews use `Milestone_00`; documentation maintenance uses `Documentation`.

Attempts increase across repairs and later tasks within a gate. Check both worker/audit files and coordinate reservations across branches; never reuse a submitted number or overwrite submitted logs. State the exact smaller task. Use `ready_for_audit`, `partial` or `blocked`. Record actual model label/version, exposed reasoning setting, references/sections, completion time with timezone, exact snapshot, changed files, actual test commands/outcomes, limits and next action. Use `not exposed` for unavailable metadata, never private reasoning. Without commits, deliver files plus a base identity and full hash manifest or reproducible patch.

An auditor reads the worker's exact snapshot, task assertions, relevant specs and unresolved findings; independently checks them; then writes the matching [audit log](docs/project-0/templates/audit-log.md). Findings need evidence, location, required repair, regression test and closure condition. Auditors report rather than silently repair production code. Self-checking is not independent approval. A repair worker accounts for each finding and preserves accepted work.

## Acceptance and stopping

One accepted task is not a gate pass. A gate needs all applicable tasks/tests together on the reviewed snapshot; milestone acceptance adds its closing gate's combined review and earlier milestone reviews. One audit may cover both when explicit. Hardware/model claims remain profile-specific; unavailable evidence is not a pass. Keep unresolved older findings visible.

[STATUS.md](docs/project-0/STATUS.md) is the only live progress summary; update it with evidence, not a second index. Stop at the assigned boundary or genuine blocker. Finish with the worker/audit log path, result for that scope and any blocker. Never claim unperformed tests, audits, commits, pushes or gate acceptance.
