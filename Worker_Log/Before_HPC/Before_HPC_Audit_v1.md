# Before HPC A–E — independent audit v1

**Verdict: changes required for the identified admission/statistical gaps; scientific and release holds remain.** This review does not accept a whole gate, milestone, production calculation, or cluster profile.

Reviewed checkout: `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`, HEAD `a78af5ce9c74f09c8ddeba373187c99a7f72035b`, tree `edad75fcffe227bd1512ee9f65a48371462e003e`. Published base: `4ad8ee835809325ceec8a017222415043347967d`. Final implementation commit: `92a50000144d5407b397572d418c2d7402d77078`; `src/atm_mlmm` tree: `e92bc45eb34dcbdd62a019387bcce5d35d78c193`. The audit receipt's `source_tree` is the enclosing `src` tree (`51016ae33c65e6a19b553e623ccbb337a7c4aae1`), a different path, not a conflicting identity.

Reviewer: sole independently dispatched auditor, under the user's requested Astra/high audit scope; recorded 2026-10-07 UTC. The user's subsequent authorization supersedes the historical no-audit clause in the orchestrator handoff. Implementation remained frozen. No remediation, commits, publication, dependency installation, QM, dynamics, production sampling, or cluster work occurred during this audit.

## Scope and evidence

Read the applicable `AGENTS.md`, orchestrator handoff, parent plan and A–E packets; reviewed their implementation delta and relevant current source, test bodies, worker records, final summary, scientific guidance, and retained validation receipts. Particular attention went to A's shared loading/restoration paths, B's native cap mapping and chemistry records, C's grouping/resampling and final-result admission, D's generic input/recipe validators, and E's package/profile boundaries. This is a targeted independent implementation audit, not a fresh exhaustive numerical qualification.

The only fresh behavioral check was a serial, inert characterization script. Its [source](evidence/audit-v1/admission_probes.py), [output](evidence/audit-v1/admission-probes.log), and [exact command/environment/source receipt](evidence/audit-v1/admission-probes-receipt.json) are retained. It ran at **16:00:06.698–16:00:06.782 UTC**, exit 0, **0.084 s**, under `/workspace/before-hpc-cpu-v2`, with two BLAS/OpenMP/MKL threads. Exit 0 means the characterization assertions reproduced the documented behavior, not that the defective admissions passed an acceptance test. No executable model or dynamics was loaded.

The same check independently rehashed **all 386 supplied files** against `setup-v1/handoff-identity.json` and **all 44 final source modules** against `checkpoint-e-v1/identity.json`: zero mismatches. A read-only diff from `92a5000` to reviewed HEAD showed no source/tool/test/fixture/environment/package delta. The checkout was clean at audit entry; audit output consists only of this record and the new `evidence/audit-v1/` folder. Historical records, including failures and prior acceptance decisions, were preserved.

Retained worker results are evidence on their named snapshots, not fresh audit passes:

| Batch | Retained checks inspected | Interpretation |
|---|---|---|
| A | [84 passed](evidence/batch-a-v1/focused-final.log), 92.05 s; actual checkpoint/State and before-evaluation rejection test bodies | Substantive regression evidence for the three original restart contradictions. Finding F3 limits the complete-inventory claim. |
| B | [30 packet tests](evidence/batch-b-v1/focused-b-attempt2.log), [28 affected checks](evidence/batch-b-v1/single-cap-compat-attempt3.log); [command receipt](evidence/batch-b-v1/command-receipt.md) | Overlapping counts. Independent cap-force oracle, Cartesian step sweeps, deliberate missing-force faults, nonidentity map, PME ledger, MACE derivative and fresh-process controls support the narrow synthetic mechanism. |
| C | [43 focused passes](evidence/batch-c-v1/final-focused-attempt1.log), [one separate slow qualification pass](evidence/batch-c-v1/qualification-attempt1.log), [receipt/design results](evidence/batch-c-v1/command-receipt.md) | Frozen synthetic block/run controls support their stated design. They do not establish persistent-journal independence or molecular uncertainty. |
| D | [Evidence index](evidence/batch-d-v1/README.md): 9 packet, 3 structural and 4 affected host passes, overlapping | Host–guest mechanics and structural importer controls; no selected complete protein or physical liquid qualification. |
| E | [Evidence index](evidence/batch-e-v1/README.md): 31 focused and 7 machine-data passes, overlapping; [10 final affected passes](evidence/batch-e-v2/compat-fix-affected-001.log); [installed final worker pass](evidence/batch-e-v2/installed-final-worker-002.log) | Scoped package/CLI/compatibility evidence. The final worker proof requires the documented sidecars and source mirror. |

## Findings, ranked

### F1 — High: persistent-journal identity is mistaken for independent initialization

**Location:** `src/atm_mlmm/exchange_analysis.py:101`, `:131`, `:290`; producer `src/atm_mlmm/exchange.py:771`, `:789`, `:809`.

For persistent histories, the analyzer uses the hash of the entire initial manifest as its `initialization_identity`; the cross-run refusal only checks whether these hashes repeat. That manifest binds records containing the newly generated run UUID and walker IDs. Two runs from the same prepared state with identical integrator and host RNG seeds therefore receive different initialization identities merely because their run labels differ. The actual initialization evidence string is required to be nonempty but is not compared with a seed/state fingerprint in this path.

This does not meet C1's rejection of mislabeled independent histories. Repeating a deterministic trajectory under a fresh run name can evade the independence guard and be treated as another independent unit by `independent_runs`; duplicate trajectories can artificially reduce or collapse the reported sampling uncertainty. C's synthetic repeated-initialization test checks a repeated declaration string and does not cover this producer/adapter interaction.

**Evidence strength:** direct source/data-flow finding; no new trajectories, duplicate journal construction, or numerical uncertainty experiment was run. The already reported synthetic known-answer result is not contradicted.

**Minimal follow-up:** bind independent-initialization provenance to actual prepared state and relevant RNG streams, excluding incidental run/sample IDs; refuse repeated initialization streams or keep independence unresolved. Add one bounded producer-to-analyzer duplicate-initialization rejection control and a genuinely distinct-stream control before qualifying this path.

### F2 — Medium: HPC validation reports readiness for contradictory profiles and an unverified bundle

**Location:** `src/atm_mlmm/hpc.py:17`, `:35`, `:44`; `tools/check_hpc_profile.py:21`.

The checker tests presence and SHA-256 string shape, but does not validate schema version, positive resource values, checkpoint semantics, required storage safeguards, or whether profile artifact identities agree with verified bundle contents. The CLI reads the manifest JSON and passes it directly; it does not verify the bundle.

**Reproduced:** schema version 999, negative threads/memory, zero wall time/workers, storage testing disabled, `compatible_with="unknown"`, and `portable_state_promises_identical_rng=true`, together with a bundle containing only its format string, returned `ready_for_local_trial_dry_run`, with no errors or missing fields. See `contradictory_hpc_profile_and_format_only_bundle` in the audit output.

The tool does not submit jobs, which bounds the immediate impact. Its purported admission result nevertheless cannot be relied on to establish E4's declared profile/artifact/checkpoint prerequisites.

**Minimal follow-up:** validate typed profile semantics and require an actually verified, identity-matched bundle before the ready status. Preserve held status for unverified or contradictory declarations; add small rejection controls without running a cluster trial.

### F3 — Medium: complete source admission ignores undeclared bundled Python files

**Location:** `src/atm_mlmm/runtime_validation.py:48–65`; used by worker loading and fixed/pair/multistate continuation.

The helper compares declared Python paths with the current source tree and verifies declared bytes. It never enumerates the actual bundled Python tree. An additional `.py` file in `runtime/source/atm_mlmm/` is consequently invisible unless it is also declared in the manifest.

**Reproduced:** a copy of all 44 matching current modules passed; adding an inert, unmanifested 45th Python file still passed. The file was never imported. This establishes an inventory-contract defect, not an observed arbitrary-code execution exploit. It contradicts A1's required declared/current/bundled set equality and the worker report's unrestricted extra-file rejection claim (`Batch_A_v1_worker.md:40` also states nothing remains uncovered).

**Minimal follow-up:** compare the actual recursively enumerated bundle source set with both declared and current sets, retaining containment/symlink checks and relocation support. Add an undeclared-file rejection case alongside the existing declared-extra-entry control.

### F4 — Medium: physical-solvent stages can omit every declared force owner

**Location:** `tools/validate_solvent_recipe.py:192–194`.

The stage check requires only `set(stage_owners) <= set(owners)`. An empty set passes. D3 explicitly requires all-active preparation force ownership, so this validates a recipe that can omit the ML, MM, or outside contribution during preparation.

**Reproduced:** a deliberately artificial, shape-valid audit recipe declared owners `MM`, `ML`, and `outside`, but assigned an empty owner list to its preparation stage. It returned `validated_input_definition_only` with no missing fields. This probe is not a chemically valid recipe and was never executed; it isolates the ownership admission defect.

The checker still reports `physical_liquid=false` and `binding_result=not_evaluated`, so this finding does not assert that an incorrect liquid calculation has occurred.

**Minimal follow-up:** enforce complete active ownership for the admitted preparation definition, with explicit semantics for any separately authorized exception. Reject empty and partial owner lists in bounded input-only controls.

### F5 — Medium: generic protein admission confuses valid empty declarations with missing decisions

**Location:** `tools/prepare_protein_input.py:9–21`, `:26–37`, `:146–155`.

The complete-target precheck marks every `None`, empty list, or empty mapping as missing, including `system.periodic_box_nm`, `system.constraints`, and `model.permitted_c_c_cuts`. Those representations have legitimate meanings in the common records: a nonperiodic system has no box, an unconstrained system has an empty constraint tuple/list, and B's ligand-only mixed control has zero cuts. Thus the complete-target path cannot admit those otherwise supported configurations. The structural-control path bypasses this precheck, so its passing tests do not cover the incompatibility.

**Evidence strength:** direct source/schema comparison, not a new complete-protein execution. This is distinct from the user's deliberate deferral of selecting a real target.

**Minimal follow-up:** distinguish absent fields/unresolved choices from explicit none/empty values according to each field's contract, and exercise a complete input-only manifest for a zero-cut, unconstrained/nonperiodic case. No target selection or new chemistry is needed to test that distinction.

## Per-batch disposition and shared interfaces

| Batch | Audit disposition |
|---|---|
| A | Original restored-state/clock/geometry repairs are supported by retained actual-artifact regressions and inspected call ordering. Shared source admission remains incomplete under F3. No blanket A1–A3 completion endorsement. |
| B | No new blocking defect established in the reviewed zero/one/two-cap synthetic builder/force scope. Explicit chemistry, actual native-site matching, unique cap identities and once-only projection are substantively implemented/tested. Broader chemistry and protein acceptance remain unqualified; this is not acceptance of arbitrary cap collections. |
| C | Grouped resampling and safe incomplete-result records have meaningful synthetic evidence. F1 blocks qualification of persistent-run independence. The disclosed C3 physical-endpoint comparison/refusal service remains unimplemented. |
| D | Host–guest and two-cut structural mechanisms have scoped evidence. Generic input/recipe admission needs F4/F5 follow-up. Missing real target, crown/solvent parameters, physical correction definitions and molecular sampling are separate holds, not defects inferred from absent experiments. |
| E | Local packaging, asset refusal, CLI plumbing, final compatibility fixes and tiny resource measurements have useful evidence. F2 limits profile admission. Full-suite, final-source bundle, offline reproduction, licensing and actual hardware trials remain open. |

The A→B/D interface preserves public restart APIs and carries actual cap collections into the common builder/worker path. B's synthetic derivative proof can be reused for identical structural bytes, but cannot qualify a different target geometry. C→D/E correctly retains unresolved correction obligations and required covariance before final binding output; C3 matching must still precede any molecular closure interpretation. E's final own-project metadata exclusion is narrowly separated from dependency identity while exact project source remains guarded; the retained 10-node rerun supports the diagnosed compatibility repair, subject to F3's separate inventory completeness issue.

## Verification, scientific and release holds

The consolidated `python -m pytest -q` **did not pass**. Retained [start](evidence/final-cpu-v1/start.json) and [result](evidence/final-cpu-v1/result.json) show 15:09:16–15:22:42 UTC, 806.469 s, exit −9, six failure markers and no pytest summary. The 8 GiB cgroup peak and `oom_kill=1` are consistent with an OOM kill; there is no pre-event counter baseline. Collection recovered 725 nodes, but progress-order inference does not establish a complete test outcome. The diagnostic rerun produced seven actual failures and six passes. Final compatibility evidence shows ten affected passes, including all seven diagnosed failures. Neither that rerun nor the one installed-worker pass establishes a completed final full suite. No full-suite replay was attempted by this auditor.

Other holds remain explicit:

- **Code/definition:** C3 has no general physical-endpoint metadata/refusal contract. Matched analytic identity/reversal does not establish molecular closure. The live STATUS lower “Next work” text still says pause before Batch B (`docs/project-0/STATUS.md:509`); the v5 summary is the more current A–E handoff. This minor documentation inconsistency was not repaired.
- **Physical/scientific:** real protein selection was intentionally deferred; crown/physical-solvent parameters and applicable AToM ABFE correction equations/domains remain unresolved. Follow the documented upstream procedure once available; six ledger rows do not imply six nonzero additions. No adequate independent molecular sampling, complete linked covariance, qualified molecular closure, or final binding result exists. Preserve predeclared budgets and separate predictive Pearson/Kendall performance from convergence.
- **G07:** retain 29 missing references (19 full-parent, 10 alternate-cap), 46 preserved records, seven exceedances and original failures. The retained ledger remains 2325.6446500519996 s charged, 84074.355349948 s remaining, 122992.52458401839 s continuation estimate, authorization false. This audit did not launch or reset anything.
- **Release/hardware:** the verified bundle remains the earlier `b3504f0` snapshot; it is not the final-source bundle. Final wheel SHA-256 is `616248d419eb826bead381949a20101c91fa25e5006c94101165dc996e1ddcf7`. Its installed restart proof requires external CPU environment sidecars plus an exact installed-source mirror; a standalone wheel-only worker export is not established. Fully offline dependency reinstall, independent reproduction, project distribution licensing, actual storage/checkpoint parity and GPU/cluster qualification remain open. The model's academic noncommercial restriction persists.

Audit omissions were deliberate: no fresh full suite, numerical force sweep, synthetic statistical qualification, model/wheel reinstall, full bundle rehash, molecular journal analysis, target preparation, scientific correction calculation or cluster test. Prior support/requirement matrices are planning/evidence indexes, not independently reaccepted milestones. Tiny benchmark receipts support only their measured inputs/profile; no production or GPU throughput follows.

## Handoff and stop

The economical next implementation scope, **if separately authorized**, is the five bounded findings plus the already disclosed C3 contract, followed by targeted rejection/positive controls. Resolve the interrupted-suite verification plan explicitly rather than treating scoped passes as a whole-suite result. Scientific inputs, correction definitions, sampling budgets, cluster trials and distribution decisions require their own later work.

Only this audit record and audit-only characterization evidence were written. No follow-up action is authorized by this report, and the auditor stops here.
