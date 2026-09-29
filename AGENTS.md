# AToM_MLMM: instructions for working agents

## What we are building

We are building a reusable tool for binding free-energy calculations. A machine-learning model (ML) describes a whole ligand and selected protein atoms. Classical molecular mechanics (MM) describes the rest. Artificial hydrogen link atoms close the protein bonds cut by that split. The Alchemical Transfer Method (ATM) evaluates the same physical energy model at two sets of coordinates.

Project 0 must show that the energies, forces, atom maps, link atoms, periodic boundaries, restart, and sampling machinery work correctly. It must support both absolute binding free energy (ABFE, one mobile ligand) and relative binding free energy (RBFE, two mobile ligands). Project 1 will then test useful physical accuracy on ordinary noncovalent binders. A plausible binding number is not enough to pass Project 0.

Start with mechanical embedding: ML-MM interactions remain classical. Future electrostatic embedding must fit behind the same shared inputs and outputs where possible. This does not mean electrostatic physics is already implemented or tested.

## Start from the assigned task, not the entire knowledgebase

The user will assign work by pointing to a milestone, gate, or section of a Markdown file. Read this file, then the assigned page's **Read for this task** section. It identifies the needed specifications, earlier results, and log folder. Use [the documentation map](docs/README.md) when the assignment is unclear. Consult [status](docs/project-0/STATUS.md) and the relevant earlier logs before changing code.

A milestone groups related results. A gate is a testable piece of that work. Each gate contains smaller tasks, such as `G01-T1`. By default, complete one assigned task or one clearly stated repair, not the whole milestone. A path to a milestone is not permission to run every gate. If no smaller part is named, choose its first unblocked unfinished task, record the choice, and stay within it. Stop if a prerequisite or scientific decision is genuinely missing.

Inspect the actual checkout and existing changes. These documents started as plans; file names under `src/` and `tests/` may not exist yet. Preserve other workers' changes. Do not treat an old log as proof that the current code still passes.

## Hard scientific and architecture rules

Keep ML membership fixed during each calculation. Include each transferred ligand completely in ML. For the first implementation, cuts and link atoms are only on the protein. The artificial ATM move leaves those protein atoms and caps undisplaced; ordinary dynamics still moves them.

Use one physical energy definition at both coordinate sets. Never choose a different model, atom set, or force rule because the ligand looks bound. Every real coordinate that affects an energy must receive its corresponding force, including MM atoms and link parents. Do not reuse a geometry-dependent electric field after the coordinates change. Do not clip forces separately from energy, replace nonfinite values with zero, or discard failing samples to hide a problem.

Keep these responsibilities separate:

- The **physical builder** owns the model, embedding, link atoms, and which MM terms remain.
- The **protocol builder** owns mobile ligand groups, coordinate maps, endpoint meaning, and required corrections.
- The **shared ATM and analysis code** consumes those definitions. Only the AToM adapter translates upstream-specific keys and units.

Do not create four separate engines for mechanical/electrostatic embedding crossed with ABFE/RBFE. Shared records use a collection of mobile groups and forces on all real atoms. Test one- and two-group cases, and a simple environment-dependent energy, early. Those simple tests do not qualify a real electrostatic model. See [S02](docs/project-0/specs/S02-architecture-and-dependencies.md) and [S03](docs/project-0/specs/S03-data-and-interface-contracts.md).

Count every physical force once and check that the integrator uses it in both preparation and production. Preserve stable atom identities through every index map. Common units are nm, kJ/mol, kJ/mol/nm, ps, and K. Keep raw endpoint energy, outside energy, total energy, and softened perturbation separate. A standard binding result needs an explicit sign, binding domain, restraints, midpoint connection, and all required corrections.

The first supported scope is neutral uncomplicated chemistry, a local ML model, mechanical embedding, fixed-volume and fixed-temperature production, whole-ligand translations, and conservative integration. Metals, reactions, changing protonation, adaptive regions, ligand cuts, long-range models, and actual electrostatic embedding need separate reviewed work. Reject unsupported requests rather than silently substituting a different physical model.

## Work from a specification, then a test, then code

Read the expected behavior before implementing it. Record the task and requirement IDs. Write the smallest useful failing test; verify that it fails for the intended reason; implement the smallest correct change; rerun that test and the affected earlier tests. Keep existing behavior protected while improving the code. Use [the working guide](docs/project-0/guides/spec-and-test-workflow.md).

Changes to units, energy meaning, cap rules, constraints, periodic rules, endpoint signs, or shared inputs and outputs need a recorded specification amendment. Do not solve a contradiction by quietly changing a test expectation. Ordinary internal cleanup does not need a new design document. Do not restart approved design discussions or reread every source on each assignment.

Candidate dependency versions are recorded in [the environment note](docs/project-0/reference/environment.md), not proof of a working installation. Read the relevant part before installing. Keep basic data tests independent of model weights and GPUs. Record exact software/model identities. Do not load untrusted model or serialized-system files, commit restricted weights, expose secrets, or download a different checkpoint silently.

## Required worker logs and audit handoffs

**Every worker assignment ends with a Markdown log, including partial or blocked work.** Write it in `Worker_Log/`, using the exact folder and task stem on the assigned page. For Milestone 01, Gate 01:

```text
Worker_Log/Milestone_01/
  Gate_01_v1_worker.md
  Gate_01_v1_audit.md
  Gate_01_v2_worker.md
  Gate_01_v2_audit.md
```

The worker creates the `_worker.md` file; the auditor creates the matching `_audit.md` file. They are siblings in the milestone folder. `v1`, `v2`, and so on count work attempts for that gate, including partial attempts. They are not model or code-release versions. A later task inside the same gate also takes the next number and states its smaller scope in the log. Never overwrite a submitted log. Follow [the complete logging rules](Worker_Log/README.md).

Use [the worker template](docs/project-0/templates/worker-log.md). Record the model label (Luna, Sol, Astra, or the actual reported label), reasoning setting, reference document paths and sections, completion time with timezone, exact code snapshot, work done, files changed, test commands and outcomes, remaining issues, and the next action. Use `not exposed` when model or reasoning metadata is unavailable; never guess or reveal private reasoning. Failed and unrun checks must remain visible.

An auditor starts from the assigned worker log, verifies its code snapshot, reads the relevant specification, and checks the implementation independently. Use [the audit template](docs/project-0/templates/audit-log.md). Each finding must explain the evidence, affected code, required correction, regression test, and acceptance condition so a new worker can act without guessing. Auditors normally report rather than edit production code. A self-check is not an independent audit.

The next worker reads the prior worker/audit pair, fixes the stated issues on the existing code, and writes the next numbered worker log. It must account for each finding. An audit accepting one small task does not accept a whole gate. A gate needs all applicable work and evidence; a milestone needs all its gates and a combined review. Missing hardware cannot count as a pass.

## Deliverables and stopping rules

Project 0 must leave a reusable builder, independent checks, small reference test systems, ABFE and RBFE examples, restart/exchange evidence, reproducible environments and model identities, and an honest support/performance report. Each assignment delivers only its requested part, with tests and a usable handoff.

Respect any stated task or resource budget. Do not launch a protein simulation, large dependency installation, paid service, or many agents for a task that only needs a small check. Stop at the agreed boundary and record the next unfinished step. A useful partial result with an accurate log is better than an unreviewable project-wide change.

Finish the user-facing response with the worker or audit log path, the result for the assigned scope, and any blocker. Update [status](docs/project-0/STATUS.md) and [the index](docs/project-0/plan-index.json) together only when the evidence supports it. Never claim a run, commit, push, independent audit, or accepted gate that did not happen.
