# G11: Run the first protein ABFE example

**Part of:** [M06](../../../README.md#roadmap). **Progress:** [STATUS.md](../STATUS.md).

## Why this gate exists

A real protein adds many atoms and several link boundaries. We need to show that the tested small-system rules survive that complexity before judging agreement with experiment.

## Expected outcome

One fully identified protein ABFE example, its controls, force/restart checks, thermodynamic corrections, and stated sampling and physical limits.

**Not part of this gate:** Do not treat experimental agreement as proof of correct code. Do not hide a change of constraints or cavity definition inside a control.

## Before starting

Required earlier gates: [G10](../gates/G10-restart-and-replica-exchange.md). Check evidence covering the features this task actually needs; a CPU-only result does not qualify a GPU or real-model claim. M00 must have reviewed the relevant design. All [S01 rules](../specs/S01-scope-and-invariants.md) still apply.

## Inputs, outputs, and code to work on

**Use:** G10 reliable solvated execution and all G08 thermodynamic obligations; a reviewed prepared protein/ligand target manifest.

**Outputs used by later gates:** One reproducible protein ABFE profile, matched controls, per-boundary evidence, sampling/physical-sensitivity report and scoped limitations.

**Planned source/test paths:** `fixtures/protein_one_ligand/`, target manifests, `tests/workflow/test_protein_abfe.py`.

## Small tasks you can assign separately

| Task ID | Work | Main planned checks |
|---|---|---|
| `G11-T1` | Choose the easiest informative protein fixture | `P0-TEST-G11-01` |
| `G11-T2` | Run deterministic preflight and controls | `P0-TEST-G11-01`, `P0-TEST-G11-02`, `P0-TEST-G11-05` |
| `G11-T3` | Advance sampling only after preflight | `P0-TEST-G11-03`, `P0-TEST-G11-04`, `P0-TEST-G11-05` |

### G11-T1: choose the easiest informative protein fixture

**Read:** [S01: The question Project 0 answers](../specs/S01-scope-and-invariants.md#the-question-project-0-answers); [S04: Mechanical baseline and boundary policy](../specs/S04-embedding-and-model-contracts.md#mechanical-baseline-and-boundary-policy).

Select one structurally inspected ordinary noncovalent complex with a small number of neutral side-chain ML fragments. The earlier plan suggested T4 lysozyme L99A as a candidate, not a mandatory target or an already prepared structure. Commit the actual chosen chemical/preparation manifest before running, including protonation, stereochemistry, alternate conformers, missing residues, water/ion decisions, and every boundary.

Preserve the original MM input and exact charges/parameters. The builder must not silently repair chemistry. Begin with a few transparent cuts; a larger region is not automatically a better first correctness test.

### G11-T2: run deterministic preflight and controls

**Read:** [S06: Starting numerical thresholds](../specs/S06-validation-and-tolerances.md#starting-numerical-thresholds); [S07: Evidence must identify what was tested](../specs/S07-artifacts-and-qualification.md#evidence-must-identify-what-was-tested).

Create all-MM, ligand-only ML/MM, and cavity-inclusive ML/MM controls. Match masses/constraints when asserting exact numerical equivalence. Where the physical model intentionally changes constraints, label it a different ensemble rather than an identity failure.

Repeat direct/native/worker energy comparisons on representative frames. Check each cap's parents, not only one convenient site. Record full periodic clearance and model graph edges, including the alternate coordinate geometry. Reuse G10's restart/exchange checks on the larger topology.

### G11-T3: advance sampling only after preflight

**Read:** [S05: Binding definition and correction completeness](../specs/S05-protocol-and-thermodynamic-contracts.md#binding-definition-and-correction-completeness); [S06: Sampling, covariance, and reproducibility](../specs/S06-validation-and-tolerances.md#sampling-covariance-and-reproducibility).

Run staged single-state and short schedule pilots before longer independently seeded sampling. Diagnose overlap and relevant conformational observables, not just total energy. Report raw restrained differences, midpoint bridge, standard-state term, all release terms, uncertainty/covariance and unresolved physical approximations separately.

Assess one admissible alternative bulk placement and a box-size check where needed to resolve residual periodic effects. Region-size changes are changes of model, not sampling error. Agreement with experimental affinity is useful later but is not this implementation gate's acceptance criterion.

## Checks and the answers they must establish

These are **planned tests**, not executed results. Use the rows for the assigned task; full-gate acceptance covers all applicable rows.

| Test ID | Planned pytest node | Required assertion | Requirements |
|---|---|---|---|
| P0-TEST-G11-01 | `tests/workflow/test_protein_abfe.py::test_prepared_target_and_every_boundary` | All selected identities/caps and chemistry are reviewed; at least one derivative component per real parent pair is checked. | P0-REQ-002, P0-REQ-004 |
| P0-TEST-G11-02 | `tests/workflow/test_protein_abfe.py::test_control_ensemble_and_identity` | All-MM, ligand-only and cavity-inclusive controls distinguish exact matched-constraint checks from intentional different-model ensembles. | P0-REQ-003, P0-REQ-013 |
| P0-TEST-G11-03 | `tests/workflow/test_protein_abfe.py::test_abfe_result_correction_ledger` | The reported result includes explicit signs, restraints, midpoint connection and standard-state/release status. | P0-REQ-016, P0-REQ-017 |
| P0-TEST-G11-04 | `tests/workflow/test_protein_abfe.py::test_bulk_placement_and_box_sensitivity_recorded` | Alternative admitted bulk placement and justified box-size checks produce a separate physical sensitivity record. | P0-REQ-005, P0-REQ-019 |
| P0-TEST-G11-05 | `tests/workflow/test_protein_abfe.py::test_protein_restart_exchange_and_domain` | Realistic topology retains admitted force, restart, graph and counterfactual-domain behavior before sampled interpretation. | P0-REQ-015, P0-REQ-020 |

## How to test and decide

Use [S06](../specs/S06-validation-and-tolerances.md) for applicable tolerances and independent checks.

Full-gate command, once the test code exists:

```bash
python -m pytest tests/workflow/test_protein_abfe.py -v
```

**Stop and diagnose:** Classify failure as implementation, thermodynamic definition, model-domain/physical adequacy, or sampling before allocating more trajectories. Experimental agreement cannot excuse a deterministic failing test.

## Keep future changes possible

The protein is a larger input to the same builder/assembler/workflow. No protein-ABFE-specific force construction is permitted.

## Required log and audit handoff

**Folder:** `Worker_Log/Milestone_06/`\
**Worker:** `Gate_11_vN_worker.md`; **audit:** `Gate_11_vN_audit.md`. Use the next attempt and name the smaller task; see [AGENTS.md](../../../AGENTS.md#logs-and-handoff).


## M06 combined review

**Review scope:** G11. **Earlier milestone reviews:** M05. These are combined-review conditions, not additional implementation prerequisites.

Review all selected side-chain cuts and the target input independently of the ML builder. Check at least one representative derivative component for every boundary-parent pair. Compare all-MM, ligand-only and cavity-inclusive controls with clear mass/constraint semantics.

Inspect the full thermodynamic result ledger and relevant sampling/overlap evidence. Review alternative bulk placement and justified box-size sensitivity as physical-model assessment, separate from sampling uncertainty. Confirm restart, exchange, graph and alternate-state domain checks remain valid at realistic system size.

G11 accepted for one explicit target/model/embedding/protocol/runtime profile. The result states what is deterministic validation, pilot evidence, sampled estimation and remaining physical limitation.

One audit may cover the closing gate and this milestone on the same recorded snapshot. Individual task acceptance is insufficient. Report the combined scope in this gate's worker/audit pair, or use `Milestone_06_vN_worker.md` / `_audit.md` in the same folder for a separately assigned milestone review.
