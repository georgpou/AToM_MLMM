# How we work: agree on behavior, test it, then implement it

A **specification** says what must happen and why. A **test** checks that behavior on a case with a known expected answer. The code must satisfy both. A green test does not settle whether the test used the correct scientific definition.

The normal assignment is one small task inside a gate. Its result is handed to an auditor through [Worker_Log](../../../Worker_Log/README.md). Do not turn an assignment into a whole milestone or a speculative future framework.

## A small work cycle

1. Read the assigned task and its **Read for this task** links. Check prerequisites, relevant prior logs, and the actual checkout. State the task IDs and what this session will not do.
2. Identify the requirement and expected answer. Resolve a contradiction in the specification before choosing a test expectation. For reviewed design, do not repeat the approval process unless the proposed change alters it.
3. Write the focused test and run it. Confirm the expected failure. Missing packages are installation evidence, not proof that a scientific regression test detects the intended mistake.
4. Implement the smallest correct behavior. Rerun the focused test and affected earlier tests. Improve internal structure only while those tests still protect the same behavior.
5. Write the next worker log, including partial work or blockers. A new agent independently audits that snapshot and leaves the matching audit log. Repairs use a new worker attempt.

Use [the assignment template](../templates/task.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md). Exact filenames, metadata, and retry rules live in one place: [the logging rules](../../../Worker_Log/README.md).

## Example: a future embedding must be allowed to exert an MM force

G02 uses a deliberately simple energy, not an electrostatic model:

$$E=\tfrac12\kappa|\mathbf r_m-\mathbf r_e|^2.$$

Here `m` is a model atom, `e` is an MM environment atom, and kappa is a spring constant. With kappa=10 kJ/mol/nm squared, m at (0.2,0,0) nm and e at (0.5,0,0) nm, the energy is 0.45 kJ/mol and the x forces are +3 and -3 kJ/mol/nm. Moving m by +0.1 nm changes the energy to 0.20 and the forces to +2 and -2. Moving only e to 0.6 nm from the original geometry gives 0.80 and +4/-4.

These values provide an independent expected answer. A shared evaluator that returns only ML forces must fail. So must code that reuses the old distance after ATM moves the ligand. Test the same evaluator with one and two mobile groups. This protects the extension point without implementing electrostatic embedding now.

After the correct test passes, deliberately remove an environment force or reuse stale coordinates in an isolated test copy. The test must fail. This checks the test itself; never leave the deliberate mistake in production code.

## When the specification must change

A changed energy definition, units, cap rule, constraints or masses, periodic treatment, endpoint sign, correction, or shared field meaning requires a reviewed change. Use [the specification-change template](../templates/spec-change.md). Explain which earlier results are affected. Do not simply relax a tolerance or delete a failing case.

An internal cleanup that preserves those meanings does not require a new architecture decision. Backward-compatible fields need meaningful defaults; an absent charge, spin, force, or correction must not be guessed to make an old file load.

## Keep the workload small

Prefer one failing case and one cause at a time. Start with small CPU checks; run expensive model/GPU/sampling tests only when required for the claim or authorized assignment. Missing resources block the affected claim, not every unrelated task. A narrower test setup can be accepted only when its limits are explicit.

Do not change shared records independently in parallel branches. G04-G07 physical work and G08 analysis can proceed separately when their actual prerequisites pass, but they must use the same reviewed interfaces. The gate dependency list controls implementation readiness; milestone dependencies control the later combined review.

When a session cannot finish, preserve the usable work and write a partial log with the next command or test. Do not call an unrun test passed, and do not silently continue into another gate to compensate for a blocker.

## Acceptance

The worker submits a result for the assigned scope. The auditor decides whether that scope passed. Whole-gate acceptance needs all required tasks and applicable tests together on a recorded code snapshot. Milestone acceptance adds a combined review. Use [STATUS.md](../STATUS.md) for the summary; actual acceptance remains tied to the code, logs, and test evidence.
