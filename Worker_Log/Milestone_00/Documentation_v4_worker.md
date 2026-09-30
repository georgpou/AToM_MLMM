# Scientific-plan amendment - attempt 4 - worker

**Outcome:** ready_for_audit for documentation and configuration changes only. No M00 approval or numerical qualification is claimed.  
**Task:** apply the scientific audit to the existing cleaned repository and deliver complete replacement/new files without a user-run patch.  
**Model/version:** Astra; GPT-6 Astra Pro. Exact model build: not exposed. **Reasoning setting:** not exposed.  
**Finished:** 2026-09-30T14:46:07+02:00.  
**Previous worker:** [Documentation v3](Documentation_v3_worker.md). **Previous independent audit:** none supplied for this amendment.

## Snapshot and references

The actual uploaded `AToM_MLMM.zip` is the base, SHA-256 `88268ba9ede3112e769f6827489cb37bf4e8606e0799d3a880e831363602f55c`. This attempt used its current cleaned files directly, not the older snapshot recovered during the preceding scientific audit. The isolated base contains 54 working files after excluding Git internals and macOS metadata. The ZIP and base files were not edited. No branch, commit, remote or push was changed. The delivery replaces 22 working files and adds this log plus two evidence files; it does not replace the repository or its Git history.

References actually used: the user's approved scientific-audit findings and replacement-file request; `AToM_MLMM_scientific_audit.md` (SHA-256 `21927c55978091e1a928ab97629adab407eaa22d7bde94835391f8551beb38f3`); the supplied plain-English writing preferences; current `AGENTS.md`, README, requirements/status, S01-S07, M00, all gate pages, the environment files, source register, worker template and previous packaging log. The [source register](../../docs/project-0/reference/sources.md#scientific-amendment-source-checks) identifies the upstream pages fetched on 30 September 2026 and distinguishes unrefetched inherited source pointers.

The [verification record](evidence/Documentation_v4/verification.json) gives the base/result file changes, actual document/configuration checks and limits. The [full working-file manifest](evidence/Documentation_v4/file-manifest.sha256) hashes the resulting non-Git tree, excluding the manifest itself. It does not include `.git` or macOS metadata and does not describe an installed environment.

## Changes and decisions

The replacement root files are `README.md`, `AGENTS.md`, `ATM_MLMM_environment.yml` and `ATM_MLMM_Environment.md`. Under `docs/project-0/`, the replacements are `REQUIREMENTS.md`, `STATUS.md`, specifications S01/S04/S05/S06/S07, M00, the source register and gates G00/G02/G03/G04/G05/G07/G11/G12/G13. Exact full paths and before/after hashes are in the verification record. No files are deleted. Existing milestone reviews remain in their gate files; no removed milestone pages are recreated.

Add P0-REQ-033 and G05-T4/G07-T4 for small capped-chemistry, uncut/partitioned and boundary/contact reference comparisons. M00 must review their reference choices and numerical limits before results are inspected. Keep native/adapter agreement separate from physical evidence; no universal chemical-error threshold is invented. Quantum reference data can be generated separately and frozen, without adding a runtime quantum backend.

Strengthen nonlinear ATM force tests, post-construction fixed-map checks, cap force/torque checks on an appropriate isolated potential, early real-model two-ligand single points, every protein boundary's Cartesian derivatives, and independent small-system reverse sampling. Preserve the existing cap Jacobian, restraint-volume integral, midpoint-bridge rules and matched-state closure. Benchmarking/reproducibility remain mandatory; optimization equivalence is conditional on proposing an optimization.

Keep all package version numbers and explicitly select the conda-forge CPU PyTorch build rather than implying the discontinued official PyTorch channel supplies 2.8.0. This changes a candidate recipe, not an installed or solved environment. GPU profiles remain separate. Preserve S02/S03 and every original requirement, task/test identifier and historical log. Eleven new planned tests bring the gate-local catalog from 82 to 93 nodes; none of these planned molecular tests was implemented or executed here.

These are amendments to unaccepted proposed contracts, not a new accepted scientific release. The proposed version-1 schema is unchanged; no runtime-record migration is introduced. All existing gate/milestone statuses remain `not_started`/`not_run`. Any separate checkout with later accepted evidence must assess these amendments against its own snapshot and rerun affected qualification; it cannot import this file package as retroactive approval. Keeping final G12 after G11 is a workflow choice, while G07 now checks real two-ligand routing earlier.

## Checks

The machine-readable record stores commands, exit codes and detailed results. The temporary amendment checker was run against the untouched base before editing: 8/22 checks passed and 14/22 failed because the proposed additions were absent. After editing, all 22 document/configuration assertions passed. These are text, structure, provenance and preservation checks, not energy/force or chemistry tests.

The unchanged repository command `python tools/check_docs.py --self-test` was run against the revised tree. Its local links and headings passed, along with all eight checker self-tests. The amendment check verified unique requirement/test references, task assignment and planned-command coverage, unchanged original requirements, unchanged S02/S03, unchanged historical files and unchanged numerical status. The YAML was parsed; it was not solved or installed.

Packaging verification applied the delivered file overlay to a fresh base copy and compared every working-file byte with the revised tree. It also checked safe ZIP paths, unchanged historical records, absence of deletions and preserved original gate/task/test IDs. The same documentation checks were rerun on that merged copy. Checks were self-reviewed by the author; no independent reviewer or scientific worker was dispatched.

## Findings and next handoff

No production engine code, molecular tests, reference quantum calculations, simulations, environment solve/install, numerical gate review, independent audit, Git commit or remote update was performed. Corrected planning requirements are not proof of engine accuracy. The initial fixed-map route and the complete software stack still need G00-G03 source/runtime qualification. G05/G07 reference data and acceptance limits still need the scoped M00 decision and numerical evidence.

The next independent review belongs at `Worker_Log/Milestone_00/Documentation_v4_audit.md`. Review this exact manifest, P0-REQ-033, G05/G07 reference scope, S05 map/force definitions, the CPU recipe and the package's manual-placement guide. Record acceptance or required repairs there; do not overwrite this worker log or older attempts.
