# G09 denser local water and Colab orchestration — v5 independent audit

**Reviewed worker:** [Gate_09_v5_worker.md](Gate_09_v5_worker.md).  
**Snapshot:** branch `m05-colab-workflows`; base `fab6388b041acc4362f30b5ff7d3789a33fc536f`; frozen submission `bc6fd520308fba7e7448929138eb91e80ca6f063`; tested scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.  
**Reviewer:** independent agent `/root/m05_combined_review`, one combined scientific/code review; 2026-10-05 UTC.  
**Verdict:** **accepted_for_scope** — the bounded G09 CPU increment and its scientific definition. Combined G09/G10 decision: [G10 v2 audit](Gate_10_v2_audit.md). Full gates, M05 and M03 remain open.

## Scope and scientific decision

Reviewed the assigned handoff, implementation plan/ledger, G09/G10, relevant S04–S07 contracts, changed source/tests/notebooks and the [proposed amendment](../../docs/project-0/specs/m05-dense-exchange-amendment.md). Accept its 64-water geometry-only local-hydration definition for the frozen ABFE/RBFE inputs: 224/233 real atoms, fixed complete-ligand ML membership, inherited retained-MM/PME accounting, 0.109 nm caps, Reference double / approved MACE CPU float64, NVT 300 K and 0.0005 ps. This extends G09-01..05 technical coverage; it is not liquid-density equilibration or a physical accuracy result.

The box-face formatting amendment was made after a diagnosed numerical failure; this review explicitly covers that amendment rather than treating it as part of the original pre-result definition. Comparing the preserved failed inputs with the final fixtures found only 109/99 changed water-coordinate components, maximum **1.6653345369377347e-17 nm**. Solute coordinates, topology, masses, constraints and System XML are identical. This is a separately identified fixture representation, with the original failures retained. The production geometry module, OpenMM, CPU locks, approved model bytes and S06 limits are unchanged. Accept the bounded input change; it does not establish general periodic-boundary continuity or repair the external Reference artifact.

## Independent evidence

All scientific commands ran serially in `/workspace/AToM_MLMM`, activating `/workspace/atom-mlmm-m05/activate.sh` in each shell and setting `OPENBLAS_NUM_THREADS=2`, `OMP_NUM_THREADS=2`, `PYTHONPATH=$PWD/src`. Raw reviewer scripts, logs, JUnit, extracted immutable evidence and JSON results are retained in the previously unused `/workspace/m05-evidence/reviewer-v1`.

The shared affected command was:

```bash
python -m pytest tests/workflow/test_evidence_export.py tests/environment/test_m05_notebooks.py tests/workflow/test_persistent_exchange.py tests/workflow/test_dense_solvent.py tests/workflow/test_solvated_process_restart.py tests/environment/test_tpu_experiment.py -q -k 'not actual_cpu_reference' --basetemp=/workspace/m05-evidence/reviewer-v1/pytest --junitxml=/workspace/m05-evidence/reviewer-v1/focused.xml
```

**41 passed, 1 deliberately deselected, 0 skipped; 86.32 s, exit 0.** The deselected expensive CPU-reference regeneration already has frozen full-suite evidence; independent checks of its actual saved arrays are in G10. Fresh affected tests exercised the actual model, independent retained-MM/native-MACE full-force oracle, both maps, parent/ligand/solvent three-step FDs, exact fixture regeneration, partial/tampered evidence copies, environment subprocess isolation, and solvated offline/checkpoint behavior.

Additional independent probes:

| Command / retained result | Actual outcome |
|---|---|
| `python /workspace/m05-evidence/reviewer-v1/geometry_probe.py` → `geometry-check.json` | Explicit 27-image enumeration, both maps: minimum water/other Bondi ratios **0.8032818748 ABFE / 0.8001337768 RBFE**; water/cap minimum **1.1810063666**; ligand/cap minimum **1.3427901004**. All exceed the amendment's 0.80 construction bound. |
| Inline Python comparison of failed/final input records → `roundoff-check.json` | Only the water-coordinate representation changes described above; no solute or force-field mutation. |
| `python /workspace/m05-evidence/reviewer-v1/check_evidence.py` → `evidence-check.json` | **120 scientific hashes, 43 evidence hashes, six compressed archive hashes, five seals / 449 files verified**; no mismatch. Both dense pilots retain nine samples and both exchange pilots four rounds/eight samples. |
| Git source comparison | Executable source, tests, tools, fixtures, environments and notebook code are identical between tested source and submission. The later notebook README additions are reporting/instructions. |

The first reviewer hash-script invocation stopped on an overbroad assertion that included that README; corrected the reviewer script to compare executable notebook files and reran successfully. Both logs remain. This was not a submission defect.

Independently inspected submitted full-suite JUnit/log and hash bindings: **543 tests, 0 failures/errors/skips**, reported pytest duration 606.45 s (JUnit 606.434 s), process exit 0. This is verified submitted evidence, not a second reviewer full-suite run. The original nine strict setup passes are likewise carried evidence; the unchanged environment was used for the fresh checks above.

## Findings and closure checks

**No Critical or Important defect found; no required repair.** Architecture retains one physical builder/ATM adapter; the solvent module constructs frozen inputs only. Independent full-force/FD checks and the explicit image oracle support the declared local-water scope. Complete-tree copy verification rejects partial, changed, unsafe and symlinked evidence; active writers must remain stopped as documented.

Colab CPU execution remains **not_run**, not accepted. The CPU notebook supplies an immutable baseline pin, explicit extension source pin instructions, isolated repeated activation, approved-weight verification, bounded subprocesses, full stopped exports and resume instructions. The documented user-run fallback is adequate. Closure of actual Colab coverage requires returned complete exports, command/profile/device evidence and successful inert verification on that host; a saved notebook or this local audit cannot supply it.

Declined to judge: general OpenMM repair/root cause beyond the retained stock reproducer; arbitrary periodic seam crossings; long-time solvent stability, equilibrium/density, NPT/virial, molecular/protein accuracy, affinity, CUDA/multigpu/TPU performance and M03 physical closure. The user's method-development priority does not require repairing the external engine. No QM ran and no QM ledger change is authorized by this acceptance.
