# Branch-contained CPU environment reproduction - attempt 2 - independent audit

**Worker log:** [Cloud_CPU_Reproduction_v2_worker.md](Cloud_CPU_Reproduction_v2_worker.md).\
**Audited scope:** Delivered two-environment CPU setup, artifact/source identities, reproduction, failure propagation and flagged repository inconsistencies. No molecular-platform implementation or complete M00/G00 review.\
**Submitted snapshot:** `dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`; artifact delivery ancestor `be26b7c25e9a30f67f6d3a884001084fa710bd8c`.\
**Inherited setup/handout snapshot:** `28f89cb23bdb7081c3723b9794fbde7d9bb50dca`; audit branch `m01-g00-environment-audit-v1` starts exactly there.\
**Model/version; reasoning setting:** Codex, GPT-6 family; exact served build and reasoning setting not exposed.\
**Finished:** 2026-10-01T15:00:33.469899+00:00.\
**Verdict:** `changes_required` for the clean-baseline assignment. The narrow CPU installation/runtime checks pass; A01-A03 remain open. No clean-baseline, scientific gate, model-loading or GPU acceptance.

The broken anchors do not affect calculations. Their runtime impact is low, but the missing source entries are real and the historical delivery discrepancy extends to scientific requirements. The important findings are the missing documentation amendment and a reproducible loading-policy defect in the smoke helper. The OpenCL replay warning requires no CPU repair. The earlier outer-driver failure was not reproduced; its historical cause remains unknown.

## Independent checks

Read both supplied assignment files, AGENTS.md, the audit/worker templates, reproduction v1/v2 reports and linked raw evidence, setup v1/v2 context, both environment guides, candidate YAML, every setup helper, both full locks/package/Python inventories, pip locks/constraints, source manifests, source register, handoff/startup instructions and STATUS. The actual missing-delivery finding additionally required inspecting the v4 verification/manifest, requirement and gate catalogs, and relevant G05/G07/G12/S06 text. This is not a review of the entire scientific design.

The exact submitted tree was extracted with `git archive` outside the checkout at `/workspace/.onboarding/atom-mlmm-audit-v1-submitted-tree`. Static comparison shows only `CLOUD_START.md`, setup `README.md` and `bundle.sha256` differ within the setup directory at the inherited tip; runtime scripts, locks, wheels and source archives are identical. Both snapshots' 76 bundle entries and 51 wheel checks pass. Later handoff wording is not attributed to the submitted worker. [Initial state](evidence/Cloud_CPU_Reproduction_v2_audit/initial-state.json), [static inspection](evidence/Cloud_CPU_Reproduction_v2_audit/static-inspection.json) and [command records](evidence/Cloud_CPU_Reproduction_v2_audit/commands.json) identify the inputs and exact commands/statuses.

Profile: Linux x86_64, two computational threads, 8 GiB cgroup memory, approximately 30 GB free initially. No existing worker installation/cache was present or reused. The first absent prefix, `/workspace/.onboarding/atom-mlmm-independent-audit-v1`, stopped during Miniforge bootstrap at the sandbox's standard Conda registry mkdir. That failure remains preserved. After narrow access for `/home/agent/.conda`, a second independently absent prefix, `/workspace/.onboarding/atom-mlmm-independent-audit-v1b`, used its own downloaded bootstrap and package cache. HOME, TLS verification, hashes, versions and environment separation were preserved. [Prefix absence](evidence/Cloud_CPU_Reproduction_v2_audit/fresh-prefix-v1b.json) and [execution context](evidence/Cloud_CPU_Reproduction_v2_audit/execution-context.json) distinguish the resolved sandbox prerequisite from a package defect.

Unless specified otherwise, recorder commands ran from `/workspace/AToM_MLMM`. Each command has a JSON record and raw `.log.gz` in the [audit evidence folder](evidence/Cloud_CPU_Reproduction_v2_audit/). Validation JSON retains every underlying command, working directory, output and status.

| Independent check | Actual command/input and result |
|---|---|
| Fresh submitted-tree installation | `ATOM_MLMM_SETUP_ROOT=<v1b> ATOM_MLMM_REPOSITORY=<submitted-tree> bash <submitted-tree>/environment/cloud-cpu/install.sh`; exit **0**. [Raw output](evidence/Cloud_CPU_Reproduction_v2_audit/fresh-install-v1b.log.gz), [nine individual results](evidence/Cloud_CPU_Reproduction_v2_audit/fresh-validation.json). |
| Main complete inventory/build comparison | `env/bin/python check_versions.py <v1b> core`; exit **0**: Python 3.11.16, **156** Python distributions, **255** exact Conda URL/SHA-256 artifacts. NumPy 2.4.6; CPU Torch 2.8.0. |
| Amber complete inventory/build comparison | `amber-env/bin/python check_versions.py <v1b> amber`; exit **0**: Python 3.11.16, **80** Python distributions, **201** exact Conda artifacts. AmberTools 26.0 CPU; NumPy 1.26.4. |
| Both dependency checks | Each interpreter's `-m pip check`; both exit **0**. Independently repeated by strict validation, installer replay and Cloud fallback. |
| OpenMM Reference/CPU | Main `-m openmm.testInstallation`; exit **0**, both platforms compute forces; fresh median relative difference **6.29108e-06**, within upstream tolerance. CUDA/HIP Torch runtime fields are **None**, and an explicit tensor is on CPU. |
| Weight-free ML/native ATM | `python <v1b>/smoke_cpu.py`; exit **0**: random untrained MACE finite E/F, TorchANI descriptor derivatives, ASE/OpenMM E/F agreement and native ATMForce containing ASE PythonForce. This does not qualify mapped molecular physics or pretrained loading. |
| Separate Amber preparation | `python <v1b>/smoke_prep.py` in a fresh validation prep directory; exit **0**, main OpenFF/GAFF 2.2.20 uses separate AmberTools; five-particle methane has finite CPU E/F. |
| Pinned upstream UWHAM | Main `-m pytest -q tests/test_uwham.py` in extracted AToM sources; exit **0**, **1 test passed**. Inspected `_test_uwham_analysis`, pytest collection configuration and all three reference datasets, including sample-count/energy/error assertions. |
| Documentation and strict validation | Submitted/inherited `python tools/check_docs.py --self-test`; both exit **1**, exactly two missing anchors, **all eight self-tests pass**. After activation, `python <v1b>/validate.py --root <v1b> --repository /workspace/AToM_MLMM` exits **1**; all eight environment checks are **0**, docs are **1**. [Strict results](evidence/Cloud_CPU_Reproduction_v2_audit/strict-validation.json). |
| Activation main → Amber → main | [Probe](evidence/Cloud_CPU_Reproduction_v2_audit/activation_probe.sh); exit **0**. Interpreter/NumPy are main/2.4.6 → Amber/1.26.4 → main/2.4.6. AMBERHOME and all four Amber executable paths are correct; core constraints disappear in Amber and return in main. [Raw observations](evidence/Cloud_CPU_Reproduction_v2_audit/activation-switching.log.gz), [Amber script interpreters](evidence/Cloud_CPU_Reproduction_v2_audit/amber-python-shebangs.json). |
| Installer replay on same prefix | Same submitted installer/prefix; exit **0** with all eight environment checks passing and the expected docs failure. Inventories remain exact. [Replay results](evidence/Cloud_CPU_Reproduction_v2_audit/replay-validation.json). |
| Real Cloud fallback | Disposable HTTPS-origin clone detached at original base `2d7bcc94f901738e39f536f16de84699d4e8d631`, initially missing setup. Current `cloud-install.sh` fetches `28f89cb`, archives artifacts and replays the audit prefix; outer/installer exit **0**. All eight environment checks pass. [Before](evidence/Cloud_CPU_Reproduction_v2_audit/cloud-checkout-before.json)/[after](evidence/Cloud_CPU_Reproduction_v2_audit/cloud-checkout-after.json) prove unchanged HEAD, tracked bytes, clean checkout and no setup overlay. |
| Controlled failure propagation | [Disposable-copy probe](evidence/Cloud_CPU_Reproduction_v2_audit/failure_probe.py): missing and corrupted wheel, each through direct installer and local Cloud wrapper; corrupted side-branch fixture through fetch/archive fallback. **All five underlying exits are 1**, before bootstrap/main/Amber installation. Probe exit **0** means expected failures were observed. [Summary](evidence/Cloud_CPU_Reproduction_v2_audit/failure-probe-summary.json). No real artifact/prefix was corrupted. |
| Source/artifact/runtime identities | All 51 wheel hashes match lock/METADATA; every archive entry and uncompressed archive byte matches independently fetched upstream tags after preserving archive ref decorations. AToM `v8.5.0` is commit `9e26c5a…`, whose `8.5.0beta` metadata normalizes to **8.5.0b0**. Installed source-wheel distributions have **no VCS direct_url**, as expected; original-build VCS metadata is not fresh-install metadata. [Runtime identities](evidence/Cloud_CPU_Reproduction_v2_audit/runtime-identities.json), [upstream comparisons](evidence/Cloud_CPU_Reproduction_v2_audit/upstream-openmmforcefields-comparison.json). |
| Loading-policy regression | [Probe](evidence/Cloud_CPU_Reproduction_v2_audit/loading_policy_regression.py) executes the complete weight-free smoke then checks the override: original exits **1** after CPU assertions pass; scratch-only second cleanup exits **0**. [Original](evidence/Cloud_CPU_Reproduction_v2_audit/loading-policy-original.log.gz)/[candidate](evidence/Cloud_CPU_Reproduction_v2_audit/loading-policy-scratch-candidate.log.gz). Production helper remains unchanged. |
| Branch and file preservation | Setup/submitted ancestry passes; all **204 inherited files** remained byte-identical after runtime tests. [Integrity record](evidence/Cloud_CPU_Reproduction_v2_audit/post-runtime-integrity.json). Audit delivery changes only reporting/handoff documents plus new evidence; scientific specifications, candidate, setup artifacts and submitted worker history remain unchanged. Main remains `2d7bcc94…`. |

## Findings

### A01 - blocking for the scientific baseline: missing Documentation v4 delivery

**Observed versus required:** The historical report/verification/manifest describe 22 replacements, 93 planned test nodes and a revised source register. **18 files under `docs/project-0/` exactly match the recorded before hashes**, both in the submitted result and inherited tip. The current catalog has **82** nodes; P0-REQ-033, G05-T4 and G07-T4 are absent. G05 still says chemical accuracy is a separate study, while README/AGENTS require the amendment's limited physical-reference checks. This is a genuine incomplete delivery, not a renamed legacy folder.

**Location/evidence:** [v4 report](../Milestone_00/Documentation_v4_worker.md), [historical verification](../Milestone_00/evidence/Documentation_v4/verification.json), [complete missing-file/history inventory](evidence/Cloud_CPU_Reproduction_v2_audit/amendment-delivery-history.json). Source-register actual SHA-256 is `b9cc660a894c3847ff471d91d76f27159ab50b954da7ee24bcb69af2a03ffff3` (recorded before), rather than claimed after `42968f71afa21b1fc2ae8e12bcd568c9585d3ca7e3f641520418365e5a79bf91`. The claimed 18 after hashes were not found in currently reachable fetched path history. Unavailable external ZIPs were not inspected.

**Importance:** No current calculation is invalidated: the molecular program is not implemented. Proceeding against an allegedly amended but incomplete plan could omit chemical-reference, nonlinear force, cap/torque, boundary and reverse-sampling safeguards. This blocks claiming the intended scientific baseline complete.

**Smallest repair:** Recover the actual v4 replacement files/overlay and verify their hashes before restoring only missing content. If unavailable, record a new, explicitly reviewed amendment from the documented requirements; identify it as newly reconstructed, preserve existing invariants/IDs/tolerances and do not fabricate the original bytes or approval. Preserve the historical report/manifest unchanged and keep numerical gates unaccepted.

**Regression/closure:** A before/after delivery reconciliation for all 22 claimed replacements; presence and unique coverage of P0-REQ-033/G05-T4/G07-T4 and the intended additional assertions; unchanged S02/S03 and original IDs; explicit provenance for recovered versus reconstructed content; independent amendment review. Eight passing link self-tests alone cannot close A01.

### A02 - required for documentation baseline; low runtime impact: source anchors/provenance

**Observed versus required:** Both target files exist; the heading `scientific-amendment-source-checks` and U40/U41 entries are absent. Thus these are not obsolete folder paths. Documentation checks exit **1** on exactly these two anchors; all eight self-tests pass.

**Location/evidence:** `ATM_MLMM_Environment.md:32` and historical `Documentation_v4_worker.md:13`; [submitted](evidence/Cloud_CPU_Reproduction_v2_audit/docs-submitted-output.json)/[inherited](evidence/Cloud_CPU_Reproduction_v2_audit/docs-inherited-output.json) outputs.

**Importance:** The links do not threaten installed CPU execution or scientific equations. Fix them once as part of the missing source-register delivery rather than repeatedly treating them as an environment failure. They still prevent the assignment's zero-documentation-error baseline and erase the claimed PyTorch source-check trail.

**Smallest repair:** Recover the authentic source entries under A01, or add authoritative PyTorch Conda-publication/conda-forge CPU-build evidence with actual new retrieval date, URL, digest and scope. Clearly distinguish newly retrieved records from the unrecovered 30 September claims. Do not add an empty heading or edit the historical worker claim to manufacture a pass.

**Regression/closure:** Documentation check exits **0**, zero local errors and eight self-tests; source/provenance assertions establish meaningful U40/U41 records and both links resolve; historical report stays byte-identical. This is a documentation closure, not CPU/G00 qualification.

### A03 - required: calculator import re-enables unsafe loading in the smoke process

**Observed versus required:** `smoke_cpu.py:17-21` clears the override after `import mace`, but installed `mace/calculators/mace.py:15` sets `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` again. The complete smoke leaves it **'1'** in its process. The guide's claim that this helper maintains the safe default is incomplete.

**Evidence:** [Runtime probe](evidence/Cloud_CPU_Reproduction_v2_audit/runtime-identities.json) and [original regression](evidence/Cloud_CPU_Reproduction_v2_audit/loading-policy-original.log.gz), exits **1** for the policy postcondition after all numerical smoke assertions pass. The scoped `slice` allowance does disappear correctly; PyTorch's own Dynamo/DTensor imports add their trusted types separately.

**Importance:** No external/pretrained weight was loaded; the override is confined to the validation subprocess and does not modify the activating parent shell. Existing weight-free CPU results remain valid. Reusing this pattern for later checkpoint loads would silently change the process-wide deserialization policy, so it is a real required helper repair, not a numerical/architecture defect.

**Smallest repair:** Clear the override again immediately after importing `MACECalculator`, before later calculator/model use, and assert it stays absent. Retain the scoped trusted-e3nn constant handling and current import order. Update the loading guidance to name both import side effects. No package upgrade, upstream installed-file edit, global unsafe override or model download is needed. [Scratch candidate](evidence/Cloud_CPU_Reproduction_v2_audit/loading-policy-candidate.json) confirms this small change passes the same complete smoke/postcondition, exit **0**; it is not a production repair or independent approval.

**Regression/closure:** Original policy regression must fail for the intended reason; repaired complete smoke passes and leaves the override absent with `slice` allowance restored. Rerun affected CPU validation, update the bundle manifest if the maintained helper/guide changes, verify hashes/failure semantics and independently review the repair. General pretrained loading remains unqualified.

### A04 - optional, closed for this CPU scope: OpenCL and acceleration warnings

The locked `ocl-icd-system` post-link hook is `ln -s /etc/OpenCL/vendors .../${PKG_NAME} || true`. Replay emits the existing-link warning; the actual symlink remains `/etc/OpenCL/vendors` before/after. The system target is absent on this host, and only Reference/CPU platforms are available. Installer status is **0** and all CPU checks still pass. [Before](evidence/Cloud_CPU_Reproduction_v2_audit/opencl-before-replay.json)/[after](evidence/Cloud_CPU_Reproduction_v2_audit/opencl-after-replay.json) record the hook, target, warning and functionality.

No CPU fix is needed: deleting the link, changing locked packages or suppressing stderr would add needless risk. Missing cuequivariance/TorchANI compiled accelerators and TorchScript annotation warnings likewise accompany passing CPU checks; they do not qualify those optional acceleration/serialization paths. **Closed as nonblocking for CPU; do not repeatedly reopen absent a changed target/status/CPU result.** OpenCL/GPU or serialization qualification must reassess the applicable warnings.

### A05 - optional historical uncertainty; current failure propagation verified

The preserved first replay log ends with installer **0**, while the worker records an enclosing driver **1**. The original outer driver's complete source/terminal status trace is unavailable; its original cause is **unknown**. A current direct replay and real Cloud fallback return **0**; all five controlled missing/corrupt-artifact paths return **1** before installation, with checkout preservation. No current masking/entrypoint failure was reproduced.

No speculative production repair is justified. **Closed as no reproduced defect in the tested current entrypoint**, with the historical unknown explicitly retained. Reopen only with a reproducible outer-driver command and captured individual statuses. Do not relabel the historical outer **1** as a historical pass or assume the OpenCL warning caused it.

### A06 - required reporting inconsistency, closed by this audit delivery

Inherited STATUS called Documentation v2 the current cleanup and omitted the later reproduction/audit disposition. Operational handoff/startup instructions otherwise correctly prioritized independent audit, the branch installer and the two-environment split, and did not claim gate acceptance. The root candidate guide is historical candidate context, not the maintained operational replay recipe.

This delivery updates only the live status and root task-entry pointers to the actual audit/findings and [repair assignment](../../NEXT_AGENT_REPAIR_HANDOUT.md). Gate/milestone labels remain unaccepted. Closure is the report-pointer/status consistency check and unchanged runtime/specification/submission hashes; this administrative closure does not self-approve any A01-A03 repair.

## Accepted scope and next action

Independent evidence supports the submitted CPU package reproduction, exact identities, both dependency inventories, weight-free numerical smokes, separate Amber preparation, UWHAM regression, activation and current installer/Cloud status propagation. The previously missing 51-wheel delivery is independently confirmed resolved. There is no remaining network/package-installation blocker on this tested host.

The complete assignment verdict remains **changes_required**: A01 blocks the intended scientific-document baseline, A02 needs a small provenance repair, and A03 needs the demonstrated helper-policy correction. Historical submissions/specifications/setup artifacts were not repaired in this audit. No pretrained models, GPU/OpenCL execution, protein dynamics, ABFE/RBFE result, full M00 review or G00/G01 tests were accepted or executed.

Continue on an unused child of the published audit branch, suggested `m01-g00-environment-repair-v3`; do not restart from main or discard the audit lineage. Use the next unused reproduction v3 and documentation v5 worker attempts after rechecking reservations. Follow [NEXT_AGENT_REPAIR_HANDOUT.md](../../NEXT_AGENT_REPAIR_HANDOUT.md); obtain independent repair review before declaring a clean baseline. Relevant M00 review, then applicable G00-T1/G01 work, follow required closure. [STATUS](../../docs/project-0/STATUS.md) remains the live authority.
