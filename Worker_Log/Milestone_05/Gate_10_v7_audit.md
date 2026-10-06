# G10 Tasks 1–4 plus repairs — v7 independent audit checkpoint

**PAUSED at the user's usage-limit checkpoint request; no final decision.**
The combined review is incomplete. No scoped GREEN or repair closure is claimed;
the complete [v5 RED audit](Gate_10_v5_audit.md) remains the prior decision.
Continue this same audit before any implementation repair.

Actual sole auditor: **gpt-6.1-sol / max**, `/root/g10_combined_audit_v7`;
no auditor subagents. Branch `g10-engine-next`, frozen reviewed HEAD
`acfe9f6922d4029f1628aa69d530f0b642f4bb0d`; worker submission
`883d5a8c5dbe4953d32fc0125c7c42b41d99db21`, code/result
`27e1639fefdde8ccca62263846204237391bf621`.

Completed fresh evidence: **53 focused pytest passes, 0 skips, 44 deselected,
42.53 s**; **three additional inert NumPy challenges pass** with no loader calls
or tree mutation. Independent identity checks verify all 31 submitted hashes,
eight current bundles with 38 source files each, exact repair/full diffs, raw
log hashes and unchanged protected trees. The repair diff raw SHA-256 is
`cba3d4f680908fd82d6989487f5b1e07c696acdd7bd5fca8584d3f46b3aa402c`.

The broader independent repair script stopped with exit 1 at its fourth case:
the audit harness used strict `write_json` to construct infinity, which rejected
the declaration before the intended validator. This is a **harness error**, not
a product finding; raw trace, partial results and exact artifacts are preserved.
The current molecular script was drafted but never launched. No full suite,
new molecular preparation/integration, QM, GPU, HPC or production run was added.

The reviewer read the complete R1–R7 report, completed v6/v7 workers, relevant
contracts and repair source. Focused regressions cover every R1–R7; broader
independent arithmetic, actual syscall fault/ordering and current molecular
checks remain pending. Two clock-domain concerns identified during inspection
are **unproven hypotheses**, recorded precisely in the continuation. There are
no complete new findings or C1–C9/P1–P5/M1–M6 category decisions yet.

The worker's preserved full suite is 626 passes/0 skips in 1221.89 s; current
required collection is 60+14+8+4=86, not the cache containing three stale nodes.
These retained outcomes do not finish this independent audit.

Resume from [CONTINUATION.md](evidence/G10_v7_independent/CONTINUATION.md), with
exact commands, completed/pending assertion coverage, harness correction needed,
process status and preserved evidence. [Evidence index](evidence/G10_v7_independent/README.md)
links the raw results. Pause/checkpoint UTC and verification are recorded there.

All 46 G05 records, seven G07 sensitivity exceedances, original pilot force
failures, 29 missing references and charged QM ledger
`2325.6446500519996 / 86400 s` with continuation false remain unchanged.
Full G10/M05, chemical accuracy/protein, production/release, GPU/HPC,
equilibrium/mixing/convergence/affinity and exchanging-correlated-walker
uncertainty stay open/blocked. `binding_result=not_evaluated`.
