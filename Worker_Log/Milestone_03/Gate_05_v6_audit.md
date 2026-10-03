# G05 final R2 closure and combined neutral CPU scope — v6 audit

**Reviewed worker/snapshot:** [Gate_05_v6_worker.md](Gate_05_v6_worker.md), branch `m03-reference-g05`; immutable repair source **`ac414dcb4a5f401312616f08faa17ece5ea35e9e`**, base **`8738d16f8d3813f03c6f05a5c89a4be107159c19`**, review HEAD **`ca12e023f6a6e67321fafd4af642c0975041d7f6`**. HEAD adds worker/evidence/STATUS only. Scientific snapshot remains **`a99a4448f14386e79c1546dd32fd83a33b9ac424`**, calculated with **`419b64f7bd79199a0bf999e456f1564fc184cf75`**.\
**Scope/profile:** Final supervisor-loss R2 closure, combined with unchanged [v4 independent scientific evidence](Gate_05_v4_audit.md) and [v5 R1/R3 closure](Gate_05_v5_audit.md), for all G05-T1/T2/T3/T4 and eight stable assertions on the fixed neutral nonperiodic CPU local-reference profile.\
**Reviewer and finished time:** Independent Codex `/root/g05_sol61_max_audit`, explicitly configured **GPT-6.1 Sol / MAX reasoning**; continuation of the original fresh-context independent review, not a new-context claim. Serving build is not exposed. UTC completion is in [final-state.json](evidence/G05_v6_independent_sol61_max/final-state.json).\
**Verdict:** **`accepted_for_scope`**. R1, R2 and R3 are closed; no remaining finding within the reviewed scope.

## Evidence

Read AGENTS first, then the final worker/snapshot, source delta, maintained regression and preserved execution logs. The submitted tree was initially clean. Ancestry, exact identities and five repair-lineage hashes match the frozen snapshot. Only `tools/resume_neutral_quantum.py` and `tests/unit/test_quantum_interruptions.py` changed after the v5-reviewed base. No source, data, STATUS or model metadata edits, commits, publication, delegation, QM calculations, reference generation or finalized coordinator launch occurred. New reviewer evidence uses exclusive writes in [G05_v6_independent_sol61_max](evidence/G05_v6_independent_sol61_max/README.md).

Each independent command activated `/workspace/atom-mlmm-g05-v2/activate.sh` and used `PYTHONPATH="$PWD:$PWD/src"`. Receipts preserve argv, cwd, UTC times and exit codes.

| Check | Actual outcome |
|---|---|
| Exact byte-identical v5 independent supervisor-loss probe, relocated into the new v6 evidence directory | **1 passed in 3.18 s**, exit 0; actual synthetic supervisor SIGKILL and surviving reference-child cleanup |
| `python -m pytest tests/unit/test_quantum_interruptions.py::test_supervisor_loss_cleans_reference_group_before_next_launch -v --tb=short` | **1 passed in 3.14 s**, exit 0 |
| Independent persistent-group refusal check | Exit 0; fake already-reaped supervisor, TERM then KILL, **5.01 virtual seconds** of post-reap waiting, then required refusal exception. No real process/signal in this check. |
| Independent byte/lineage preservation | Exit 0; all **46** QM records and **1,435** unaffected v4 manifest entries unchanged; exact input/quantum manifests and reference lock preserved. Entire scientific/model/source/history and v4/v5 reviewer evidence subtrees unchanged. R1/R3 helper bodies are AST-identical to the v5 base. |
| Preserved worker checks on the final frozen source, inspected rather than rerun | **336 passed in 213.92 s**, including **42** recovery cases and all eight G05 assertions/both chemical comparisons; strict environment **9/9**; docs **0 errors / all 8 self-tests**. Targeted lifecycle GREEN **11 passed in 33.39 s** and intended supervisor-loss RED retained. |

The broad scientific audit and complete suite were not repeated. Their applicability is established by byte preservation and final-source worker execution. The original independent scientific review checked all 46 real records and actual convergence/gradient logs, eight exact historical reuses, 38 zero-exit resumed workers, all 12 numerical controls before comparison, 34 chemical rows, 28 cap/full-parent projections and required attraction/compression signs. Both chemical comparisons satisfy the unchanged predeclared limits. Reference method, lock, basis, model, geometries, settings and thresholds remain fixed. Allocation and RSS remain distinct: 3 GiB Psi4 allocation under the approved 5 GiB allocation cap; observed peak RSS 4.670959 GiB. Cumulative charged wall time remains 4.400612 h under 12 h. No new QM or actual power-failure qualification is claimed.

## Closure decisions

| Finding and prior severity | Decision and concrete evidence |
|---|---|
| **R1 — known failure admitted as unknown; P1/high** | **Closed in v5 and retained.** Receipt/admission helpers at `tools/resume_neutral_quantum.py:139` and `:152`, checkpoint validation/salvage, generator, guard and recovery tests remain unchanged except the reviewed group-exit ordering. Known negative supervisor exit remains **-9**, fails admission and does not produce the failed job's promoted record or ready manifest. |
| **R2 — orphan/concurrent worker protection; P1/high** | **Closed.** `tools/resume_neutral_quantum.py:273` enumerates live same-group members, excluding zombies; `:287` terminates children even after leader reaping and refuses if they survive. At `:498` the coordinator records the exit/survivors, and `:503` verifies cleanup before identity clearing (`:516`), receipt (`:527`), promotion (`:530`), scratch deletion (`:534`) and another launch. Cleanup failures propagate without reaching those operations. [Exact independent observations](evidence/G05_v6_independent_sol61_max/supervisor-loss-probe/observed.json) capture the surviving child, `group_cleanup_verified: true`, exit **-9**, no old child at the subsequent launch or coordinator completion, and no failed record publication. The maintained regression preserves this case. The original inherited lease/authorization/coordinator-loss protection remains unchanged. |
| **R3 — durable progress preceded record durability; P2/medium** | **Closed in v5 and retained.** Generator durable record writes and recovery `atomic_dump`, `exclusive_dump`, directory creation, sync and publication helpers are unchanged. Existing v5 fsync/rename/directory-order, interruption-boundary and validated-copy restoration evidence remains applicable; current full source execution passes. |

There are **no new remaining findings**. Historical v4/v5 `changes_required` decisions and their RED evidence remain intact; this decision records closure on the new exact source.

## Decision and handoff

The **combined full G05 scope is accepted_for_scope for the fixed neutral nonperiodic CPU local-reference profile**, including inherited adapter T1/T2/T3 and completed chemical T4 evidence. Acceptance does not qualify protein binding, periodic systems, GPU, electrostatic embedding, dynamics/sampling, broader chemistry or complete ABFE/RBFE. G06/G07 are not closed here; **M03 still requires G07 combined review**. Model qualification metadata was not altered by this reviewer.

Final verification confirms unchanged HEAD, index, submitted source/data and old evidence, with only this audit and new reviewer evidence added; no unexpected root artifact or active real/synthetic quantum worker remains. The implementer may record the actual scope decision in STATUS and publish the explicitly authorized working branch. This reviewer performed neither action.
