# Fresh-agent handoff: make the ML/MM engine ready for cluster trials

**Historical assignment.** Use the [current engine continuation](CLOUD-ENGINE-CONTINUATION.md).
G08 and the bounded G09/G10 CPU work below have since been implemented/reviewed;
the original commands and next-work sequence are retained as history.

**Prepared:** 2026-10-04 UTC.\
**Repository:** <https://github.com/georgpou/AToM_MLMM>.\
**Continuation branch:** `m04-engine-readiness`.\
**Exact predecessor:** `m03-g06-g07` at `fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86`.

## The user's current assignment

Concentrate on making the computational pipeline work as an ML/MM engine: correct energies, full real-atom forces, cap redistribution, interaction accounting, ATM state construction, thermodynamic definitions, preparation, worker export, analysis, restart and exchange. Progress through the next gates and milestones using small deterministic checks and short runtime trials. Prepare a reproducible path for longer production and thorough physical tests on the user's HPC cluster.

This instruction supersedes the previous G07-only assignment and its prohibition on starting M04/G08. It also authorizes a **new branch copied from the G07 predecessor**. This handoff and cleanup are already on that new branch; continue it rather than creating another branch. No new gate implementation or production run was performed while preparing this handoff.

Keep three statements distinct: the implementation evaluates the declared Hamiltonian correctly; sampling estimates its equilibrium properties adequately; the Hamiltonian is physically accurate for the intended chemistry. Technical development can proceed while G07 physical qualification remains open. Longer trajectories cannot repair an incorrect derivative, wrong correction sign or physically inadequate model.

## Start on the prepared branch

In this cloud workspace use `/workspace/AToM_MLMM`. Its checkout is already on `m04-engine-readiness`, with no separate development worktree. Inspect local changes before fetching or switching. Preserve user work. On a fresh clone, fetch the **existing** published branch and track it:

```bash
git clone --branch m04-engine-readiness --single-branch https://github.com/georgpou/AToM_MLMM.git
cd AToM_MLMM
git status --short --branch
git rev-parse HEAD
git merge-base --is-ancestor fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86 HEAD
```

Match HEAD to the exact publication SHA supplied with this handoff, record actual HEAD, and retain its lineage. Do not start from main or an older handoff. Use normal commits and pushes to `m04-engine-readiness`; leave `m03-g06-g07` and main unchanged. Do not reset, rebase or force-push. A replacement environment does not authorize overwriting an existing checkout or resetting resource accounting.

## Read first

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md), [DEVELOPMENT](../../DEVELOPMENT.md), and the [CPU environment guide](../../../environment/cloud-cpu/README.md). Start with [G08](../gates/G08-thermodynamics-and-estimators.md) and its relevant [S03](../specs/S03-data-and-interface-contracts.md), [S05](../specs/S05-protocol-and-thermodynamic-contracts.md), and [S06](../specs/S06-validation-and-tolerances.md) sections. Read later gate sections as their work begins; the gate documents contain planned checks, not proof that those functions exist.

The existing core is in `src/atm_mlmm/`: `schema.py`, `schedule.py`, `atm.py`, `hybrid.py`, `ledger.py`, `geometry.py`, `derivatives.py`, `prepare.py`, `persistence.py`, `protocols/`, `models/`, and `adapters/atom.py`. Preserve those boundaries. `ThermodynamicSpec`, complete analysis, production observables and the new G08 sampling tests still need implementation; the present schedule and energy records are starting points.

## What is already established

M01/M02 analytic contracts and G04 link-boundary mechanics are independently accepted for their recorded CPU scopes. The actual **GPT-6.1-sol/MAX** [G06](../../../Worker_Log/Milestone_03/Gate_06_v1_audit.md) and [G07](../../../Worker_Log/Milestone_03/Gate_07_v1_audit.md) review accepted their small-system numerical assertions on source `c584086da68654b07f1a477d7ce1e48da42a9838`. This includes native/direct routing, full forces, periodic interaction accounting and joint cavity/ligand ATM single points. It qualifies **OpenMM Reference double / MACE CPU float64**, not general CPU PME precision, GPU execution, dynamics or protein binding accuracy. Do not repeat that numerical audit unless a relevant new change or failure warrants it.

The final G07 execution/recovery source is `fcc1de9619f58934ff0c5835e01ecf3848a8a48c`. Its recorded full CPU suite passed **416 tests**. The [v3 audit](../../../Worker_Log/Milestone_03/Gate_07_v3_audit.md) accepted the recovery repair; [v4](../../../Worker_Log/Milestone_03/Gate_07_v4_audit.md) accepted the actual pilot admission, partial physical arithmetic and decision to checkpoint. These are scoped decisions, not combined M03 physical acceptance.

The sole new full-parent QM pilot converged and exited zero. A parser initially rejected its actual affirmative convergence phrase; that defect was repaired and independently reviewed. Validation-only recovery admitted the original energy/gradient without rerunning QM. There is no outstanding parser/recovery repair on this snapshot.

## What remains physically blocked

G07 has **1/30** new references validated: `ethanol-methanol-d3-r0--full-parent`. **19 full-parent and ten alternative-cap calculations are missing**. The matrix reuses 20 exact baseline records; **all 46 accepted G05 records are preserved**. Seven earlier force-sensitivity exceedances remain, maximum **0.12165016265111903 eV/angstrom** against **0.05**.

The [pilot comparison](../../../Worker_Log/Milestone_03/evidence/G07_v2/pilot-force-comparison.json) provides a useful separation:

| Force comparison on the one contact | RMS, eV/angstrom | Meaning |
|---|---:|---|
| Same capped structure: projected MACE minus capped QM | 0.0127151 | Below the 0.05 RMS limit for this row. |
| Capped QM plus all retained MM minus complete-parent QM | 0.3942092 | Cap/partition and retained-MM approximation exceeds the limit. |
| Baseline hybrid minus complete-parent QM | 0.3951254 | Complete hybrid force error exceeds the limit. |

The independent audit checked the cap Jacobian and both real parents, verified retained-MM forces against OpenMM to approximately `1.50e-15 eV/angstrom`, and verified the vector decomposition. Thus this contact's accuracy failure does not itself demonstrate a bookkeeping or cap-derivative bug. Complete-parent MACE also exceeds maximum-atom and net-ligand force limits. Full-parent separated QM is missing, so complete contact-energy attribution is unavailable. Each description must use its **own contact-minus-separated energy zero**; never subtract unlike-composition absolute energies.

Preserve every failure and control. Do not relax limits or declare G07/M03 physically accepted to advance the roadmap. [G07 results](../../../Worker_Log/Milestone_03/evidence/G07_v2/RESULTS.md) and the [remaining-reference handoff](G07-reference-remaining-v2.md) preserve the details; their historical G07-only scope is superseded by this assignment.

## Work sequence and acceptance boundaries

1. **M04/G08 first:** implement all six stable assertions. Independently integrate the harmonic problem with `k=100`, `kr=50 kJ/mol/nm^2`, `d=0.3 nm`: `F1-F0=+1.5 kJ/mol`, reversed `-1.5`, and `kr=0` gives zero. Check the complete lambda curve and independent analytic samples before MD. Reconstruct every state's dimensionless reduced potential from raw endpoints, exact soft-core/softplus expression, outside terms, direction and offsets, and compare actual contexts. Deliberately create nonidentical directional midpoints; verify the bridge with the S05 sign. Check finite-wall volume and standard-state/release obligations; missing required corrections must prevent a final standard binding result. Run pinned PyMBAR and AToM Python UWHAM on the same states/data, including offsets, covariance, support and correlation. Only then run short repeated-seed analytic MD. S06 requires both three standard errors and an absolute error at most `0.1 kJ/mol` after adequate sampling.
2. **M05/G09 technical preparation and export:** after G08, work on the small solvated fixture, unchanged physical identity, all-active minimization/thermalization, constraints, periodic clearance in both maps and retained classical solvent coupling. Verify real AToM PDB/System/State export and fixed-coordinate worker reload before stepping. Preserve raw energies, state labels and counterfactual geometry diagnostics. G09 names G07/G08 as prerequisites: use the already accepted G07 numerical evidence only for explicitly scoped technical development. Its physical qualification remains incomplete; do not label the full G09/M05 molecular profile accepted on that basis.
3. **M05/G10 runtime reliability:** using the small technical handover, verify offline fresh-process reload, asset/code digests, energies/full real forces, box, constraints and parameters. Distinguish same-profile checkpoint continuation from portable State semantics. Compare actual two-state exchange exponents with independent cross-state energies; invalidate stale energies after parameter/state changes. Interrupt/resume and check unique sample IDs, append policy, walker/state histories and analysis continuity. Qualify GPU/model device placement only on hardware actually tested. Combined M05 closure retains its M03/M04 review requirements; report partial technical evidence honestly while M03 remains open.
4. **M06/G11 and M07/G12 technical preflight:** progress only with the relevant earlier runtime evidence. Prepare an explicitly reviewed protein manifest, matched all-MM/ligand-only/cavity-inclusive controls, every cap parent, full-map domain checks and worker parity. Extend the same engine to two complete ligands; check identity, reversal, state meanings and matched ABFE/RBFE closure definitions. Start with deterministic checks and bounded pilots. Defer long protein sampling, broad physical assessment and affinity claims to HPC and the missing qualifications.
5. **M08/G13 and HPC preparation:** measure startup, first evaluation, steady stepping, RSS, model copies and scratch before optimizing. Produce a reproducible runtime/support matrix and small demonstration bundle. Full G13/release acceptance still requires its stated evidence; a useful technical handover can remain partial. Prepare cluster scripts only after confirming scheduler, account/partition, CPU/GPU profile, scratch layout, wall limits and permitted connectivity. Pin environments/assets, use signal-safe checkpointing, immutable attempts, logs/receipts and unique sample IDs. Run a small cluster parity/restart trial before scaling production. A script or submitted job is not proof of a qualified cluster profile.

The new agent should continue this sequence autonomously within the user's technical scope, rather than stopping after a plan or waiting for expensive references to make every deterministic test possible. Record prerequisite limitations instead of silently changing gate definitions. Ask for missing cluster details when they actually become necessary; do useful local implementation while waiting. Do not start long QM/production runs or extend the old quantum budget merely because this technical assignment exists.

## Mechanics that must remain correct

- Fixed real ML membership; complete ligand transfer; undisplaced protein cap maps; recomputed cap geometry/periodic images/model graphs after coordinate changes.
- All influencing real-coordinate forces, including both cap parents, nearby MM and solvent. Native OpenMM virtual-site machinery projects cap forces once in production. Do not add another manual redistribution on top of it; manual projection belongs only in an independent raw-model/reference oracle.
- Exactly one contribution for every physical force, with explicit original/retained MM term dispositions and active preparation/production force groups. Mechanical embedding's declared cross interactions and long-range terms must remain consistent.
- Explicit units and ordered atom identities: OpenMM uses kJ/mol and kJ/mol/nm, model records eV and eV/angstrom, and QM records Hartree and Hartree/bohr gradients. Force is minus the gradient. Keep conversions explicit, including the angstrom/nm factor. Separate raw, outside, total and softened energies; differentiate the actual nonlinear mixing expression. The admitted `getPerturbationEnergy()` tuple is `(u1, u0, energy)`; name fields explicitly and verify their scope against direct contexts.
- Same Hamiltonian in direct/native/AToM/worker paths, with saved maps, schedules, restraint obligations, provenance and current state parameters. Reject unsupported chemistry/ensemble/hardware claims.
- Meaningful independent oracles, finite-difference step sweeps and deliberate faults for omitted/doubled forces, wrong signs/units/maps, lost cap derivatives, stale energies and missing corrections. Keep failures and nonfinite frames.

## Environments, commands and resources

Activate the **main** environment in every scientific shell:

```bash
cd /workspace/AToM_MLMM
source /workspace/atom-mlmm-g07/activate.sh
export OPENBLAS_NUM_THREADS=2
python -m pytest -q
python tools/check_docs.py --self-test
```

For direct source commands, set `PYTHONPATH=/workspace/AToM_MLMM/src`. Main NumPy 2 and Amber NumPy 1.26 remain separate; direct Amber Python uses `/workspace/atom-mlmm-g07/activate-amber.sh`. G08 does not need Psi4. Quantum work uses only the separate `/workspace/atom-mlmm-g07/activate-reference.sh` and unchanged reference lock/settings, **Psi4 1.10.2 / LibXC 7.0.0**. On a replacement machine inspect actual resources/network and rebuild the locked profile; these absolute installed paths are not portable assets.

The current cloud has a **two-CPU quota, 8 GiB cgroup RAM limit and no configured swap**. Serialize heavy tests/model workers, use two threads, and monitor process RSS plus cgroup events/statistics. Pilot group RSS peaked at **3.190 GiB** and OOM/OOM-kill events stayed zero; cgroup total reached its limit due to reclaimable file cache. Storage cleanup is not a cure for anonymous RAM. Do not infer OOM from total cgroup usage alone or run privileged cache-dropping commands.

Cleanup reclaimed **2,083,614,720 bytes**, with **20.294 GiB free immediately afterward**. Actual free space changes; remeasure before heavy work. The largest missing QM job's reviewed scratch screen is **16.7615 GiB plus the 5 GiB reserve**, still above that headroom. Reviewed remaining-time screening is **34.1646 h**, against **23.3540 h** left. The existing quantum ledger charges **2,325.644650052 s** of a cumulative **86,400 s** allowance; session quota resets do not reset it. Original authorization, matrix, attempts, guards and false continuation assessment remain unchanged. Do not run the G05 resume tool for G07 or create a fresh G07 budget ledger. Any future approved cluster quantum continuation must preserve completed identities, old receipts and all charged attempts, and separately bind its reviewed resource/budget plan.

Use the configured network proxy and CA trust. Inspect `/etc/codex/network-policy.json` and current environment status; GitHub and locked package hosts are allowed. This cloud has no configured private-cluster TCP/VPN access. Do not invent authentication, unset the proxy or start interactive login as a fallback.

## Cleanup performed and future policy

The [cleanup report](../../../Worker_Log/Documentation/evidence/Engine_Handoff_v1/cleanup-result.json) records exact sizes, hashes and free-space measurements. Removed: 328 SHA-verified package-download archives, the verified Miniforge installer, and ignored regenerable Python/pytest cache files. Installed environments, extracted package caches, installation logs, source, fixtures, weights, locks and all accepted data remain.

Two closed independent recovery-probe trees were replaced by lossless archives containing **all 1,606 original files**, including failed synthetic cases. Their manifests preserve original paths, hashes, sizes and modes. The primary audit logs/scripts/results stay readable. The canonical live quantum attempts, SCF logs, one-second samples, receipts and ledger were not archived or changed. Read [archive restoration instructions](../../../Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent/CLOSED-PROBES.md) before accessing those closed copies. Frozen older manifests describe their original submission snapshots; archived members are resolved through the new manifests, not treated as lost evidence.

For future cleanup, stop and verify the complete supervised group before touching its private scratch. Persist results, diagnostics and receipts first; remove only temporary scratch for that attempt. Preserve useful logs and failures. Never run blanket `git clean`, `mamba clean --all`, or recursive deletion over repository/evidence/environment roots. Only archive closed redundant evidence after per-file round-trip verification. Keep original paths required by a resumable queue readable. Active code, datasets, model assets and runtime environments are essential.

## Verification and delivery expected from the next agent

Use focused failing tests before implementation. For each meaningful code change run affected checks and the available full CPU suite. New G08 nodes are planned until implemented; missing/skipped tests do not establish acceptance. Record profiles, actual collection counts, independent expectations, tolerances, exit codes and relevant resource limits.

Start with an unused `Worker_Log/Milestone_04/Gate_08_vN_worker.md`; later tasks use their gate's folder/stem. Update STATUS as work completes. Deliver reproducible examples, exact source/results/assets, accepted versus partial scopes, physical/sampling limitations, remaining HPC work and the remote-verified branch SHA. Necessary independent gate/execution/physical reviews should use the user's chosen **GPT-6.1-sol at MAX reasoning** on the exact submission. Worker tests alone do not close a gate or milestone; avoid repeating unchanged accepted reviews.

The immediate next action is **G08-T1 known-answer thermodynamics on `m04-engine-readiness`**, then G08-T2/T3 and the scoped preparation/restart work above. The cloud goal is a dependable technical engine and cluster handover, with honest unresolved physical qualification.
