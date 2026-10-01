# Next assignment: independent setup audit and clean-baseline findings

The user requests an independent audit of the delivered environment and all
currently flagged errors/inconsistencies before implementation advances.
Start with this assignment, ahead of M00 design review or gate implementation.
This handout is an assignment, not an audit verdict or a progress register.
[STATUS.md](docs/project-0/STATUS.md) remains the live progress authority.

## Branch from the current setup tip; never from main

Use the existing checkout. Inspect and preserve any user changes before switching.
From the repository root, fetch the published setup branch and create an unused
milestone/gate audit branch:

```bash
git status --short --branch
git fetch origin refs/heads/m01-g00-cloud-environment-setup:refs/remotes/origin/m01-g00-cloud-environment-setup
atom_mlmm_audit_parent="$(git rev-parse refs/remotes/origin/m01-g00-cloud-environment-setup)"
git switch --no-track -c m01-g00-environment-audit-v1 "$atom_mlmm_audit_parent"
test "$(git rev-parse HEAD)" = "$atom_mlmm_audit_parent"
test "$(git branch --show-current)" != main
git merge-base --is-ancestor "$atom_mlmm_audit_parent" HEAD
```

If that branch name exists, inspect it and choose an unused suffix; do not reset
or force-update it. These commands work with a single-branch clone too. Record
the actual parent commit. Every later repair branch inherits this audit branch
or its reviewed successor and retains the setup lineage. Never commit, merge,
rebase, reset or push work to main. Do not create a worktree unless requested.

## Read these files first

1. [AGENTS.md](AGENTS.md), especially logs, independent audits and acceptance.
2. [Reproduction v2 worker](Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_worker.md)
   and its linked raw v1/v2 evidence; read v1 as provisional history, not approval.
3. [Setup guide](environment/cloud-cpu/README.md), installer, cloud-install.sh,
   activate.sh, activate-amber.sh, check_versions.py and validate.py alongside it.
4. [Environment candidate guide](ATM_MLMM_Environment.md),
   [candidate YAML](ATM_MLMM_environment.yml), both exact Conda locks,
   pip-wheels.lock, both pip inventories, constraints, upstream-sources.json
   and package-identities.json in the setup directory.
5. [Audit template](docs/project-0/templates/audit-log.md),
   [status](docs/project-0/STATUS.md), [handoff](AGENT_HANDOFF.md), and
   [source register](docs/project-0/reference/sources.md).

Read additional scientific sections only if an actual finding requires them.
This task does not audit the whole scientific design or implement G00/G01.

## Identify exactly what you audit

The submitted reproduction v2 result is commit
`dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`. Its artifact delivery ancestor is
`be26b7c25e9a30f67f6d3a884001084fa710bd8c`. Audit the submitted result and also
check the latest inherited handout/setup instructions. Do not silently treat
the newer handout commit as the original worker snapshot.

Record both identities and inspect:

```bash
git merge-base --is-ancestor dcfd99d51e991f0cf6f838b81f2f14752b0a9afa HEAD
git diff --stat dcfd99d51e991f0cf6f838b81f2f14752b0a9afa HEAD
git log -1 --format=%H -- Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_worker.md
```

For exact submitted-tree execution, use `git archive` into a separate scratch
directory outside the checkout, rather than rewinding the working branch.
Point ATOM_MLMM_REPOSITORY at that archived repository when running its installer.
Compare runtime scripts/locks/wheels with the current branch before attributing
results to both snapshots. Handout/startup wording and bundle manifest updates
are later changes; package versions and artifacts must remain identifiable.

## Independent reproduction and checks

Use Linux x86_64 and two CPU threads. Check disk space first; the guide recommends
16 GB free for a fresh prefix/cache. Do not delete another worker's installation
to make room. If resources prevent an empty-prefix run, still complete independent
inspection and available checks, and state exactly what remains unverified.
Existing environments and archived success logs do not prove your fresh run.

The setup creates **two Python 3.11.16 environments**:

| Prefix subdirectory | Role | Required distinction |
|---|---|---|
| `env` | ML/AToM/OpenMM/analysis | NumPy 2.4.6, CPU PyTorch 2.8.0 |
| `amber-env` | AmberTools 26.0 preparation and Python utilities | NumPy 1.26.4; kept separate from main |

Main activation sets AMBERHOME and exposes Amber commands after main Python in
PATH; Amber scripts retain their own interpreter. Read the complete guide for
the other pinned versions, sources and network destinations. No external setup
tarball or model weights are needed.

From the repository being audited, select an unused absolute prefix and record
its initial absence. The following commands demonstrate the flow; substitute a
fresh name if this example already exists:

```bash
export ATOM_MLMM_AUDIT_PREFIX=/workspace/.onboarding/atom-mlmm-independent-audit-v1
test ! -e "$ATOM_MLMM_AUDIT_PREFIX"
(cd environment/cloud-cpu && sha256sum -c bundle.sha256)
ATOM_MLMM_SETUP_ROOT="$ATOM_MLMM_AUDIT_PREFIX" bash environment/cloud-cpu/install.sh
source "$ATOM_MLMM_AUDIT_PREFIX/activate.sh"
python "$ATOM_MLMM_AUDIT_PREFIX/validate.py" --root "$ATOM_MLMM_AUDIT_PREFIX" --repository "$PWD"
```

Capture every underlying status and raw output. Do not put `|| true` on checks
or lose status through tee/pipelines. Strict validate.py currently returns 1
for docs errors even when the eight environment checks pass. Its installer
invocation uses environment-only mode, which still executes/prints/records docs
failures. Neither status alone proves a clean repository.

Verify both full version/build comparisons and both pip checks independently;
check OpenMM Reference/CPU, the weight-free MACE/TorchANI/ASE/native ATM smoke,
main OpenFF/GAFF through separate AmberTools, and the pinned AToM UWHAM regression
(one test, three reference datasets). Inspect installed runtime identities as
well as metadata. Verify all 51 wheel hashes, source archive identities and
the AToM v8.5.0 tag versus distribution 8.5.0b0 distinction. Original-build
VCS metadata in package-identities.json is not fresh wheel-install metadata.

Source main → Amber → main again, recording interpreter, NumPy, AMBERHOME and
antechamber/parmchk2/tleap/sqm paths. Ensure constraints do not leak into Amber.
Confirm PyTorch CUDA/HIP runtime fields are None. OpenMM's permitted CUDA/ROCm
libraries do not establish GPU execution. Do not download any pretrained weights
or introduce global unsafe loading. Check the documented scoped e3nn loading
workaround and its stated limitations.

Repeat the installer on the same audit prefix to examine idempotence. Test the
Cloud entrypoint from a disposable checkout missing setup files; verify it
fetches the side-branch artifacts, propagates its return status, and leaves
tracked files/main unchanged. In a disposable copy only, test a missing or
corrupted artifact: installation and the wrapping entrypoint must fail nonzero
before installing packages. Preserve the failure output and do not modify the
real wheels, locks or another worker's prefix for this test.

## Questions that must receive a disposition

These are reported observations and audit questions, not preassigned findings
or verdicts. Use your own A01, A02, ... findings with evidence and severity.

| Item | Evidence/location | Required audit disposition |
|---|---|---|
| Two broken source-register anchors | Docs check; ATM_MLMM_Environment.md and historical Worker_Log/Milestone_00/Documentation_v4_worker.md | Reproduce both failures; identify the genuine source/provenance repair. The referenced heading and cited U40/U41 entries are absent at the handout base. Do not add an empty heading just to pass. Preserve the submitted historical report. |
| Historical documentation claim versus current tree | Documentation_v4_worker.md says links/self-tests passed; its linked manifest/verification records and current sources.md differ in their implications | Compare exact hashes/snapshots, distinguish historical claims from the current checkout, and record any verified missing delivery/provenance. Never invent fetched sources or backdate evidence. |
| First outer driver status 1 versus captured installer status 0 | Reproduction v2 worker and cloud-entrypoint-first.log.gz; later explicit status/replay logs | Independently test success and controlled failure propagation. Find a cause if reproducible; otherwise record the original cause as unknown and bound the claim using your new evidence, not an assumed fix. |
| OpenCL replay warning | Replay log: env/etc/OpenCL/vendors/ocl-icd-system symlink already exists | Inspect link target, package hook, repeat-run status and actual CPU functionality. Classify with evidence; do not suppress stderr or assume harmlessness. GPU/OpenCL qualification is outside scope. |
| Handoff, status and startup consistency | AGENT_HANDOFF.md, AGENTS.md, README.md, CLOUD_START.md, STATUS.md | Confirm this independent audit takes priority, the setup/Amber split and correct installer are clear, and no text mistakes provisional logs or smoke checks for acceptance. STATUS still points at older documentation cleanup; assess whether an evidence-based update is required. |
| Exact versions, source identities and failure semantics | Full locks/inventories, manifests, installer/check helpers, raw validation JSON | Detect substitutions, stale/missing artifacts, wrong interpreters, masked failures or unsupported claims. Treat missing APIs/tests and zero collected tests as failures for their claimed scope. |
| Working-tree and branch integrity | Before/after git status and ancestry; package/spec/history diff | Confirm setup writes outside the checkout, the child inherits the latest setup tip, scientific specifications and historical submissions remain intact, and main is unchanged. |

For the anchor/provenance repair, consult the historical amendment's recorded
sources and manifests; only claim a recovered original entry if evidence supports
it. New authoritative retrievals must have their actual retrieval date, identity
and scope. Repairs must leave historical reports intact and preserve scientific
meaning and package choices.

## Deliverables, repair handoff and stopping rule

Write the actual independent audit as
`Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md`, using the audit
template. If that sibling already exists, preserve it and record a uniquely
named supplemental review rather than overwriting a submission. Save your own
raw evidence in a new audit-specific folder and identify exact tested snapshots.
Do not create an empty audit placeholder or call this worker's handout an audit.

For each finding state observed versus required behavior, exact location,
reproduction/exit status, severity (blocking/required/optional), smallest repair,
meaningful regression and closure condition. Include a short user-facing account
of what passed, what failed, what remains unknown and any real blocker.

A clean baseline requires zero local documentation errors with all eight checker
self-tests passing, all applicable environment/workflow checks passing, correct
branch ancestry, complete reproducible artifacts and disposition of the listed
issues. An environment-only pass can be accepted narrowly; it cannot declare
the clean-baseline task accepted while required findings remain open. Scientific
M00/G00, pretrained models and GPUs are not accepted by this audit.

Audit first and record its verdict before repairs. As AGENTS.md requires,
auditors report findings rather than silently changing production setup code.
If changes are needed, provide a concrete repair assignment for a child of your
audit branch, for example `m01-g00-environment-repair-v3`, with the next unused
Cloud_CPU_Reproduction worker attempt (normally v3). Source-register documentation
repair uses the next unused Documentation attempt after inspecting existing
worker/audit numbers. The repair worker preserves accepted work, accounts for
every finding and reruns affected checks; repaired work needs independent review.
Do not label your own later repairs independently approved.

Commit/push the completed audit on your child branch and hand over its name,
commit, audit path and concrete repair scope. Never push to main or overwrite
the setup parent with audit/repair work. Update STATUS only with actual evidence
and the appropriate scope; do not mark a numerical gate accepted. After the
clean-baseline findings are closed, the next scientific prerequisite is relevant
M00 design review, followed by the applicable G00-T1/G01 work.
