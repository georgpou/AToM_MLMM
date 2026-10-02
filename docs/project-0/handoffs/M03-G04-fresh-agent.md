# Next-agent handoff: G04 after accepted analytic M02

Continue from [m02-analytic-atm](https://github.com/georgpou/AToM_MLMM/tree/m02-analytic-atm)
in a **new child branch**, suggested unused name `m03-link-boundary`. The assigned
next scope is **G04-T1/T2/T3 and all seven G04 checks** on analytic Reference/CPU.
Finish that gate and its independent review, then hand over. M03 comprises
G04–G07 and closes at G07; this assignment does not accept M03. G08 is a separate
M04 analysis path that can proceed under its own prerequisites.

## Branch and snapshot

| Item | Exact value |
|---|---|
| Repository | `https://github.com/georgpou/AToM_MLMM` |
| Accepted M02 publication | `8dcb75c4e720c0da3179e06d40ccc13c9f23f16f` |
| Independently reviewed M02 submission | `6015a652c4a9a9c968ab7933c07ac7bbb4573e12` |
| Repaired M02 source/input commit | `33daa6bebd91c49ad87f822d48cfa87e600deb6d` |
| Earlier repair handoff | `a8098a43d46df76b981861aa8dec0522d31be966` |
| Protected main | `2d7bcc94f901738e39f536f16de84699d4e8d631` |
| Protected M01 predecessor | `87146b4cc7fbd0b58d6688903a5ba081b813ac13` |

This handoff's publication commit is the commit adding this file; resolve it
with `git log -1 --format=%H -- docs/project-0/handoffs/M03-G04-fresh-agent.md`.
The accompanying chat prompt supplies that exact commit. Its changes are
documentation only over the accepted M02 publication.

Inspect the checkout and preserve existing changes before switching. Fetch
`refs/heads/m02-analytic-atm:refs/remotes/origin/m02-analytic-atm` explicitly:
some fresh clones fetch only main, so other remote-tracking refs can be absent.
Verify the supplied handoff commit is present and contains the accepted M02
publication as an ancestor. Create the unused child **at the exact handoff
commit**, without tracking or modifying the parent branch. If the suggested
name is already used, choose another unused child name; never reset/delete it.
Record starting HEAD and protected remote tips. Commit and push only the child.
Keep main, `m00-audit-m01-development` and `m02-analytic-atm` unchanged. A dirty
checkout requires preserving its changes, using isolation if needed.

## Read first

1. [AGENTS](../../../AGENTS.md), [README](../../../README.md),
   [DEVELOPMENT](../../DEVELOPMENT.md), [STATUS](../STATUS.md) and this handoff.
2. [G04](../gates/G04-link-boundary-and-derivatives.md), plus the relevant S01
   scope, S02 ownership, S03 identity/records, S04 boundary/environment, S05 full
   transfer maps, S06 thresholds and S07 loading/evidence sections it needs.
3. [M00 analytic design audit](../../../Worker_Log/Milestone_00/Milestone_00_v1_audit.md),
   [M01 v2 audit](../../../Worker_Log/Milestone_01/Gate_01_v2_audit.md),
   [G02 v2 audit](../../../Worker_Log/Milestone_02/Gate_02_v2_audit.md),
   [G03/M02 v2 audit](../../../Worker_Log/Milestone_02/Gate_03_v2_audit.md),
   and the [M02 acceptance/evidence guide](../../../Worker_Log/Milestone_02/evidence/M02_v2_closure/README.md).
4. [CPU environment guide](../../../environment/cloud-cpu/README.md). Inspect
   the pinned installed OpenMM-ML sources when integrating its boundary builder.
   Read G05/G06/G07 and G08 only as needed to understand later dependencies.

Old M02 v1 handoffs describe the earlier unaccepted snapshot. Their findings
are closed by the v2 audits; preserve them as history. No old overlay recovery
or new documentation-audit cycle is a prerequisite.

## Inherited implementation and baseline

M01 and combined M02 are independently accepted for `core-analytic-cpu` only.
The M02 v2 reviewer was explicitly configured `gpt-6-astra`, **high** reasoning.
All three admission defects are closed: actual ATM expression/required unique
globals agree with the schedule; physical globals remain fixed and cannot
collide with schedule names; rename/regroup cannot conceal duplicate force
content. Keep all three repairs and their positive controls.

Inherited independent results: **238 full-suite passes**, **237 analytic passes
/1 deselected**, **78 G02**, **38 G03**, **74 admission regressions**, **9/9 strict
environment checks**, **1 upstream UWHAM test** over three datasets. Preserved
admission replay gives 18 rejections/2 restoration positives; extra independent
probes give 120 rejections/9 positives. Numerical replay passes 66 comparisons,
eight full-coordinate FD sweeps and eight upstream A-B-A cases. The input
[manifest](../../../Worker_Log/Milestone_02/evidence/M02_v2/source-input-manifest.json)
identifies all 127 tested inputs; all 28 earlier handoff milestone files are
preserved. Establish your own baseline before implementing G04.

Existing code is under `src/atm_mlmm/`. `analytic.py` provides a real-particle-only
factory; it deliberately rejects caps. `geometry.final_positions` likewise
withholds derived-particle construction pending G04. `PhysicalBundle` currently
has no implemented `LinkRecord` field and its model map covers real ML IDs.
S03's proposed future records/signatures are not all shipped interfaces.
Extend the relevant records, map construction and physical builder deliberately,
with compatibility/version checks and independent evidence; removing a rejection
alone does not qualify cap support. `ledger.py` inventories original MM terms;
G04 must add the exact retained/removed boundary dispositions. Planned new
modules include `hybrid.py` and `embeddings/mechanical.py` under this package.

The existing [MACE link example](../../../examples/README.md) is useful upstream
integration provenance, but it supplies neither the analytic G04 oracle nor
complete G04 gate qualification. Begin with a registered analytic substitute
through the **actual OpenMM-ML boundary-building path**, without model weights.

## Work and verification

Implement G04 as specified: one neutral, chemically closed alkane-like C–C-cut
fixture; actual virtual-site type/distance/zero mass; explicit original-to-final
and model maps; each bond/angle/proper/improper/exception/constraint disposition;
independent cap Jacobian and Cartesian FD on both parents; cap-MM cross
derivatives; invariant force/torque control; both mapped states/intermediate
under ATM; and trusted fresh-process reload. Include nonidentity map and
deliberate omission/double-projection faults. Keep the protein boundary stationary
under ligand transfer and return every influencing real force exactly once.
Recompute virtual sites after perturbations and restore the saved state without
constraint projection in ordinary Cartesian FD checks. Measure nested ATM
virtual-site behavior before proposing a propagation repair.

Keep the S04 fixed-length cap rule and actual retained-MM Hamiltonian. Retain
real ML–MM electrostatics/LJ according to the reviewed policy. Model/coupling
and MM decisions belong to the physical builder; protocol and upstream keys
stay in their existing boundaries. Preserve the full-final-particle map and
all-real-force contracts, fixed physical/schedule identities and trusted loaders.

Write meaningful failing tests first, diagnose, implement minimal changes,
then run all seven G04 nodes plus the full available suite. Capture actual
collection, failures, commands, exits, fixtures and profile on one exact snapshot.
Use unchanged S06 limits: analytic Reference energy/force `1e-8`/`1e-7`,
direct/ATM `1e-4`/`5e-3` in common units, and FD steps `1e-3`, `1e-4`, `1e-5 nm`.
Characterize the new cap profile under those contracts; any justified scientific
definition/limit change requires a documented reviewed decision before acceptance.

Activate main Python in every shell. An existing installation in the prior
workspace was `/workspace/.onboarding/atom-mlmm-m02-v2`; it is not guaranteed in
a new chat. On a fresh machine install the unchanged bundle into a new writable
prefix using `ATOM_MLMM_SETUP_ROOT`, then activate that prefix. Keep NumPy 2
core and NumPy 1.26 Amber separate. Do not modify locks, install an unaccounted
editable distribution, replace weights or enable global unsafe loading.

Required checks, from the repository root after activation:

```bash
python -m pytest tests/integration/test_link_geometry.py tests/integration/test_boundary_ledger.py -v
python -m pytest -q
python -m pytest -m 'not gpu and not model_assets and not slow' -q
python <actual-setup-prefix>/validate.py --repository "$PWD"
python tools/check_docs.py --self-test
git diff --check
```

The G04 paths are planned until implemented. Also retain applicable G02/G03,
admission, trusted offline and upstream regression checks. Run the separate
UWHAM test from `<actual-setup-prefix>/sources/AToM-OpenMM` with
`python -m pytest -q tests/test_uwham.py`. Existing scripts can write beside
themselves: use a new explicit output path or a byte-verified copy in a new
evidence directory, preserving all old outputs.

## Required reviewer and delivery

Use an **independent fresh-context `gpt-6-astra` reviewer with `high` reasoning**.
For the available agent API, set `model="gpt-6-astra"`,
`reasoning_effort="high"`, `fork_turns="none"`; supply repository path, exact
frozen submission SHA, all G04 assertions/specs and worker/evidence paths.
The reviewer must author no implementation or repairs, inspect source and
independent oracles, run relevant numerical/rejection checks, and record the
actual configured model/reasoning and exact snapshot. Do not substitute Sol,
Luna or self-review. If Astra is unavailable, preserve a concrete review-ready
submission and explicitly leave acceptance pending until Astra high can finish.

Use unused attempts in `Worker_Log/Milestone_03/Gate_04_vN_worker.md` and matching
`Gate_04_vN_audit.md`. Resolve any findings with meaningful regressions and a
new reviewed snapshot/attempt. Update STATUS and acceptance records only from
the actual independent decision. Commit/push only the new child and verify
protected refs remain unchanged. Report branch, exact commit, numerical/test
results, reviewer identity/decision, outstanding issues and the next dependency.

## Open issues and later work

There is **no remaining confirmed blocking defect in the accepted M01/M02
analytic CPU scope** in the recorded v2 review. G04 cap geometry, ledger and
nested ATM propagation remain unqualified planned work, not established bugs.
The earlier runtime loading-policy and M02 admission findings are repaired.

**M00 physical-reference closure is still blocked**: exact G05/G07 conformer,
contact/separated and uncut/partitioned fixtures, quantum method/basis/convergence,
charge/spin, ordering/digests, metrics and limits require an independent reviewed
decision **before inspecting comparison results**. This does not block analytic
G04. An absent reference leaves the relevant real physical profile unqualified.

After G04 acceptance, G05 real-model qualification and G06 periodic/interaction
ledger work follow their prerequisites; G07 closes M03 with their combined
review. G08 separately closes M04 and must precede binding claims. Molecular
ABFE/RBFE, chemical/protein accuracy, GPU/full-model, periodic/actual electrostatic
physics, binding corrections and complete preparation/restart/exchange workflow
remain deferred under their gates. The shipped MACE example is integration
evidence only. Nonblocking CPU OpenCL/optional-acceleration warnings remain
historical unless new relevant failing evidence warrants reopening them.
