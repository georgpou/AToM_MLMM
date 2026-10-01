# Next assignment: close independent CPU-baseline audit findings

This is a repair assignment, not acceptance or a second progress register.
[STATUS.md](docs/project-0/STATUS.md) is the live authority. Read the independent
[reproduction v2 audit](Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md)
and its evidence first. The audit branch inherits setup tip
`28f89cb23bdb7081c3723b9794fbde7d9bb50dca`; the submitted worker snapshot was
`dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`.

## Branch and exact scope

Preserve existing changes. Fetch the published audit branch and create an unused
child from its current tip, for example:

```bash
git status --short --branch
git fetch origin refs/heads/m01-g00-environment-audit-v1:refs/remotes/origin/m01-g00-environment-audit-v1
atom_mlmm_repair_parent="$(git rev-parse refs/remotes/origin/m01-g00-environment-audit-v1)"
git switch --no-track -c m01-g00-environment-repair-v3 "$atom_mlmm_repair_parent"
test "$(git rev-parse HEAD)" = "$atom_mlmm_repair_parent"
git merge-base --is-ancestor 28f89cb23bdb7081c3723b9794fbde7d9bb50dca HEAD
test "$(git branch --show-current)" != main
```

If the name is used, inspect it and choose an unused suffix. Never reset or
force-update another submission. Do not create a worktree, push to main,
change package choices, combine Amber/main, download pretrained weights, or
change scientific definitions/tolerances to pass checks.

Read AGENTS.md, the maintained setup guide, the original audit assignment for
scope context and the new audit. Do not repeat the full audit by default:
rerun the affected regressions and any checks needed by actual new changes.
Do not implement a scientific gate as part of this cleanup.

## Required work

**A01: reconcile the missing scientific amendment.** Read the historical
Documentation v4 worker, verification JSON and manifest, then the audit's
`amendment-delivery-history.json`. Eighteen `docs/project-0/` files match the
recorded before hashes; P0-REQ-033, G05-T4/G07-T4 and the 93-node catalog are not
delivered. This has scientific significance beyond the two links.

Locate the original replacement-file overlay and verify its before/after hashes.
If it exists, restore only genuinely missing changes, preserving any newer work.
If the original cannot be recovered, do not claim hashes reconstruct the files.
Record a new proposed amendment with explicit rationale and provenance for each
reconstructed requirement, and obtain independent review. The recorded v4
change list/worker describe the intended limited chemistry references, nonlinear
ATM derivative checks, fixed-map guard, cap force/torque checks, early real
two-ligand routing, boundary comparisons and independent reverse sampling.
Preserve S02/S03, original IDs, physical architecture and existing tolerances.
Do not invent chemical thresholds: the relevant M00 review must decide them
before results are inspected. Do not rewrite the v4 worker, manifest or claimed
historical evidence. This reconstruction is not full M00 design approval.

**A02: repair meaningful source records once.** The anchors alone do not affect
CPU calculations. Both target paths are valid; the heading and U40/U41 source
entries are missing. Recover the original entries when their provenance is
available. Otherwise retrieve authoritative PyTorch Conda-publication and exact
conda-forge CPU-build evidence, recording the actual new date, URL, identity,
hash and scope. Label new retrievals as new and preserve the historical
30 September report unchanged. Do not add an empty heading just to silence
the checker or turn link-check success into scientific approval.

**A03: retain safe loading after both MACE imports.** Read
`environment/cloud-cpu/smoke_cpu.py`, installed/pinned MACE 0.3.16
`mace/__init__.py` and `mace/calculators/mace.py`. Both set the unsafe variable.
The current helper clears it only after the first import. The audit's
`loading_policy_regression.py` proves the original complete smoke exits 1 for
the policy postcondition, after numerical assertions pass. A scratch-only
candidate clearing the variable again immediately after the calculator import
passes, without package or scientific changes.

Implement the smallest justified second cleanup and postcondition, preserving
the existing scoped `safe_globals([slice])` for trusted e3nn constants. Update
setup/root handoff loading guidance as needed to describe both side effects.
Check whether another changed import/loader reintroduces the override rather
than assuming this supports arbitrary model loading. Do not edit installed
upstream packages, monkey-patch torch.load or enable global unsafe loading.
Update `bundle.sha256` for changed maintained helper/guide bytes. This repair
does not qualify a pretrained checkpoint.

**A04/A05: preserve closed dispositions.** The unchanged OpenCL symlink warning
is nonblocking for the tested Reference/CPU workflow; no package/link/stderr
change is needed. Current success/failure propagation passed. The historical
outer-driver cause remains unknown, but no current defect was reproduced.
Reopen either only for new relevant evidence; do not repeat speculative fixes.
**A06** administrative status/task-pointer correction is already delivered;
update live status with actual repair evidence, without accepting a gate.

## Logs, checks and closure

At audit time only main/setup branches were published and reproduction v1/v2
plus historical Documentation v1-v4 existed. Recheck branches/logs before
reserving the next attempts. Suggested repair records:

- `Worker_Log/Documentation/Cloud_CPU_Reproduction_v3_worker.md` for A03 and affected setup checks.
- `Worker_Log/Documentation/Documentation_v5_worker.md` for A01/A02 delivery/provenance reconciliation.

State base/result commits, actual model/setting metadata, resources, exact
changed files, failing/passing commands and each finding's closure evidence.
Use matching sibling audits only for actual independent reviews. Coordinate
attempt reservations; never overwrite an older submission.

Required checks are:

1. Reconcile all 22 historical replacement claims, with every recovered or new
   amendment file identified; validate the intended requirement/test coverage,
   original-ID/S02/S03 preservation and source-entry provenance.
2. `python tools/check_docs.py --self-test`: zero local errors, eight self-tests.
3. Execute the complete repaired weight-free smoke with the loading-policy
   regression; verify no unsafe variable remains and slice allowance is scoped.
4. Recompute affected bundle hashes, `sha256sum -c bundle.sha256`, and strict
   validation with both exact inventories/pip checks, CPU/prep/UWHAM checks.
   Preserve every underlying status and raw output.
5. Exercise controlled artifact failure if installer/bundle/entrypoint handling
   changes. Verify original scientific submissions, package locks/wheels,
   intended setup lineage and main remain preserved.
6. Independent review of the repaired snapshot and all A01-A03 dispositions.

The environment-only installer pass already has independent evidence; it is
not a clean-repository pass. Do not approve your own repair independently.
After required findings close, proceed to relevant M00 review and applicable
G00-T1/G01 tasks, using their actual prerequisites.
