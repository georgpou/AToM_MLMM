# G11: Run the first protein ABFE example

**Part of:** [M06](../milestones/M06-abfe-demonstration.md). **Progress:** see [STATUS.md](../STATUS.md); this page defines the work, not its completion status.

## Why this gate exists

A real protein adds many atoms and several link boundaries. We need to show that the tested small-system rules survive that complexity before judging agreement with experiment.

## Expected outcome

One fully identified protein ABFE example, its controls, force/restart checks, thermodynamic corrections, and stated sampling and physical limits.

**Not part of this gate:** Do not treat experimental agreement as proof of correct code. Do not hide a change of constraints or cavity definition inside a control.

## Read for this task

Start with [AGENTS.md](../../../AGENTS.md). Read the assigned task below, the relevant parts of the following pages, and earlier worker/audit logs for that task. Use [the working guide](../guides/spec-and-test-workflow.md) for the test-first cycle. Do not read the entire archive by default.

| Read | Why |
|---|---|
| [M06: outcome and dependencies](../milestones/M06-abfe-demonstration.md) | See how this gate fits into the larger result. |
| [S01: The question Project 0 answers](../specs/S01-scope-and-invariants.md#the-question-project-0-answers) | Keep infrastructure correctness separate from agreement with experiment. |
| [S05: Binding definition and correction completeness](../specs/S05-protocol-and-thermodynamic-contracts.md#binding-definition-and-correction-completeness) | Do not label a result ABFE or RBFE while required terms are unresolved. |
| [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility) | Separate sampling uncertainty, correlation, and physical sensitivity. |
| [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested) | Tie a result to the actual code, checkpoint, input, and hardware. |
| [This gate's log folder](../../../Worker_Log/Milestone_06/README.md) | Find earlier work, open findings, and the next attempt number. |

A shared **contract** means the agreed inputs, outputs, and behavior used by other code. A **profile** means the exact software, model, hardware, and settings tested. Read [the glossary](../reference/glossary.md) only for unfamiliar terms. The task's specification takes precedence over historical notes.

## Before starting

Required earlier gates: [G10](../gates/G10-restart-and-replica-exchange.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

The gate dependencies control when implementation can start. A parent milestone's combined review can require additional gates; that does not create a hidden implementation dependency. Do not silently skip an explicit prerequisite.

## Inputs, outputs, and code to work on

**Use:** G10 reliable solvated execution and all G08 thermodynamic obligations; a reviewed prepared protein/ligand target manifest.

**Outputs used by later gates:** One reproducible protein ABFE profile, matched controls, per-boundary evidence, sampling/physical-sensitivity report and scoped limitations.

**Planned source/test paths:** `fixtures/protein_one_ligand/`, target manifests, `tests/workflow/test_protein_abfe.py`.

Source module paths are under `src/atm_mlmm/`; `tests/`, `fixtures/`, and `environment/` are relative to the repository root. These paths are plans, not a claim that implementation files already exist. Inspect existing code before creating replacements. Exact shared records and signatures are in [S03](../specs/S03-data-and-interface-contracts.md).

## Small tasks you can assign separately

Default to one named task per worker session. Where a task is still too large, name one acceptance test or repair within it. Carry unfinished work into the log rather than expanding the session silently.

| Task ID | Work | Main planned checks |
|---|---|---|
| `G11-T1` | Choose the easiest informative protein fixture | `P0-TEST-G11-01` |
| `G11-T2` | Run deterministic preflight and controls | `P0-TEST-G11-01`, `P0-TEST-G11-02`, `P0-TEST-G11-05` |
| `G11-T3` | Advance sampling only after preflight | `P0-TEST-G11-03`, `P0-TEST-G11-04`, `P0-TEST-G11-05` |

### G11-T1: choose the easiest informative protein fixture

Select one structurally inspected ordinary noncovalent complex with a small number of neutral side-chain ML fragments. The earlier plan suggested T4 lysozyme L99A as a candidate, not a mandatory target or an already prepared structure. Commit the actual chosen chemical/preparation manifest before running, including protonation, stereochemistry, alternate conformers, missing residues, water/ion decisions, and every boundary.

Preserve the original MM input and exact charges/parameters. The builder must not silently repair chemistry. Begin with a few transparent cuts; a larger region is not automatically a better first correctness test.

**Finish this part with:** the relevant test results above and a worker log that states `G11-T1` as its scope. Completing this part alone does not complete G11.

### G11-T2: run deterministic preflight and controls

Create all-MM, ligand-only ML/MM, and cavity-inclusive ML/MM controls. Match masses/constraints when asserting exact numerical equivalence. Where the physical model intentionally changes constraints, label it a different ensemble rather than an identity failure.

Repeat direct/native/worker energy comparisons on representative frames. Check each cap's parents, not only one convenient site. Record full periodic clearance and model graph edges, including the alternate coordinate geometry. Reuse G10's restart/exchange checks on the larger topology.

**Finish this part with:** the relevant test results above and a worker log that states `G11-T2` as its scope. Completing this part alone does not complete G11.

### G11-T3: advance sampling only after preflight

Run staged single-state and short schedule pilots before longer independently seeded sampling. Diagnose overlap and relevant conformational observables, not just total energy. Report raw restrained differences, midpoint bridge, standard-state term, all release terms, uncertainty/covariance and unresolved physical approximations separately.

Assess one admissible alternative bulk placement and a box-size check where needed to resolve residual periodic effects. Region-size changes are changes of model, not sampling error. Agreement with experimental affinity is useful later but is not this implementation gate's acceptance criterion.

**Finish this part with:** the relevant test results above and a worker log that states `G11-T3` as its scope. Completing this part alone does not complete G11.

## Checks and the answers they must establish

These are **planned tests**, not executed results. The named checks define the required behavior. A worker runs those relevant to its small task and the affected earlier tests. A full-gate audit must cover every applicable row, including work split across attempts.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G11-01 | `tests/workflow/test_protein_abfe.py::test_prepared_target_and_every_boundary` | All selected identities/caps and chemistry are reviewed; at least one derivative component per real parent pair is checked. | P0-REQ-002, P0-REQ-004 |
| P0-TEST-G11-02 | `tests/workflow/test_protein_abfe.py::test_control_ensemble_and_identity` | All-MM, ligand-only and cavity-inclusive controls distinguish exact matched-constraint checks from intentional different-model ensembles. | P0-REQ-003, P0-REQ-013 |
| P0-TEST-G11-03 | `tests/workflow/test_protein_abfe.py::test_abfe_result_correction_ledger` | The reported result includes explicit signs, restraints, midpoint connection and standard-state/release status. | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G11-04 | `tests/workflow/test_protein_abfe.py::test_bulk_placement_and_box_sensitivity_recorded` | Alternative admitted bulk placement and justified box-size checks produce a separate physical sensitivity record. | P0-REQ-005, P0-REQ-019 |
| P0-TEST-G11-05 | `tests/workflow/test_protein_abfe.py::test_protein_restart_exchange_and_domain` | Realistic topology retains admitted force, restart, graph and counterfactual-domain behavior before sampled interpretation. | P0-REQ-015, P0-REQ-020 |

## How to test and decide

Follow [specification -> failing test -> implementation -> regression checks](../guides/spec-and-test-workflow.md). Save the actual failure and pass results. Do not change scientific expectations or tolerances just to make a test pass. Use [S06](../specs/S06-validation-and-tolerances.md) for numerical limits.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_protein_abfe.py -v
```

For a small assignment, start with its named test rather than running unrelated expensive work. A missing package or hardware blocks that test setup; it is not a successful result. State what has and has not been checked.

**Stop and diagnose:** Classify failure as implementation, thermodynamic definition, model-domain/physical adequacy, or sampling before allocating more trajectories. Experimental agreement cannot excuse a deterministic failing test.

## Keep future changes possible

The protein is a larger input to the same builder/assembler/workflow. No protein-ABFE-specific force construction is permitted.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_06/`\
**Task stem:** `Gate_11`\
**Worker:** `Gate_11_vN_worker.md`\
**Matching audit:** `Gate_11_vN_audit.md`

N is the next available attempt number for this gate. The first is v1; a partial attempt or a later task inside the gate also uses the next number. State the smaller task IDs in the log. Follow [the logging rules](../../../Worker_Log/README.md), [worker template](../templates/worker-log.md), and [audit template](../templates/audit-log.md).

A worker submits evidence for its assigned scope. An auditor checks that scope on the recorded snapshot and gives directions for any repair. Whole-gate acceptance requires all applicable tasks, tests, and affected regressions together; a small accepted fix is not a full-gate pass. Update [status](../STATUS.md) and [the index](../plan-index.json) only when supported by that evidence.
