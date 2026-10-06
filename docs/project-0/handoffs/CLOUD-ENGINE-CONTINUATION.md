# Main engine continuation on Codex Cloud

**Latest continuation (2026-10-06):** G10 bounded multistate Tasks 1–4 plus repairs are **GREEN / accepted_for_scope**. See the [final handoff](G10-MULTISTATE-FINAL-HANDOFF.md) and [complete v8 audit](../../../Worker_Log/Milestone_05/Gate_10_v8_audit.md). Current child branch is `g10-engine-next`; source `3f93efa079ae36514d86d34f9dbc263722bcd1cd`, audited snapshot `2be9334aea5c8fc34a4bb7ca0ebf6c46802aee27`, audit `c28c04bc4d7507998044168f1a123bba1a4d23c3`. Full CPU631PASS/0skips and two fresh bounded v2 pilots passed. All20 scoped assertions and R1–R7 close. Historical v5/v7 RED findings and failures remain preserved. This supersedes the preparation-only scope below; physical safeguards/full-G10/M05/statistical limitations remain unchanged. The user requested publication of only this finished child branch, with no further audit this session.

**Prepared:** 2026-10-05 UTC. **Branch:** `cloud-engine-continuation`.
This is the current assignment; earlier handoffs describe historical snapshots.
Complete engine implementation using deterministic tests and bounded serial CPU
pilots. The user will transfer the finished code to HPC for demanding calculations.
This preparation task removes abandoned execution tooling and verifies the retained
engine; it does not implement or accept the next scheduler increment.

## Required orchestration and audit workflow

The chat agent is the **orchestrator**. It plans tasks, prepares detailed worker
instructions, checks task completion, coordinates audits and maintains the
handoff. Delegate implementation and repairs to **`gpt-6-luna` with reasoning
effort `max`**. The auditor is **`gpt-6.1-sol` with reasoning effort `max`**.
Use these exact model identifiers when spawning agents; do not silently substitute
a model or lower reasoning effort. If either is unavailable, report that limitation.

**Concurrency limit: the orchestrator plus at most one running side agent.**
Only the orchestrator may spawn agents. Workers and auditors must not spawn their
own agents. Finish the active worker or auditor before starting another. Never
run implementation, repairs or another audit alongside an active auditor.

Give each Luna worker a bounded, detailed assignment containing the task/gate,
exact starting snapshot, prerequisites, relevant files/contracts, required behavior,
independent numerical expectations, protected invariants, resource limits,
verification commands, completion criteria and expected code/log/evidence output.
Supply only relevant context; do not duplicate the complete conversation or rerun
accepted checks without a reason.

Follow this sequence:

1. Define the implementation batch and complete every task in it using Luna max
   workers **one at a time**. The orchestrator verifies that the expected outputs
   and required checks are present. Do not call the auditor for unfinished work
   or for each intermediate edit.
2. Once all tasks in the batch are finished, call one Sol 6.1 max auditor with
   the exact combined snapshot, compact diff, task requirements, worker reports
   and focused evidence. It must assess coding, physics/chemistry and mathematics:
   implementation/admission/restart correctness; Hamiltonian, chemical states,
   force ownership, caps and interaction accounting; and units, derivatives,
   exchange probabilities, thermodynamic signs and statistical claims.
3. **Let the auditor finish its complete report before any fix is implemented.**
   Do not interrupt it to start repairs, edit its reviewed source while it works,
   or act on provisional findings. Obtain the final findings and decision first.
4. If repairs are required, give small fixes to one Luna max worker. For complex
   findings, decide how many bounded repair tasks/workers are needed and their
   dependency order. Run those workers sequentially, never more than one alongside
   the orchestrator. Complete and verify the entire repair batch before auditing
   again; the orchestrator must not bypass delegation by implementing fixes itself.
5. Audit the repaired combined snapshot with Sol 6.1 max, again letting it finish.
   Repeat the repair/audit loop until the auditor explicitly gives GREEN for all
   applicable coding, physics/chemistry and mathematical assertions in the declared
   scope. Keep every failure, finding, repair and review decision in the logs.

Where an existing scientific contract requires design review before implementation,
finish a **standalone design task** first and audit that completed task. Then run
the implementation batch and its final audit. This preserves the concurrency and
finished-task rules while retaining required scientific design review.

A scoped implementation GREEN does not establish chemical accuracy or full-program
qualification while the physical blockers below remain. Mark unavailable hardware,
missing references and unresolved physical failures explicitly; do not waive them,
relax tolerances or label a blocked gate GREEN to finish the loop.

## Start and accepted baseline

Read [AGENTS](../../../AGENTS.md), [STATUS](../STATUS.md),
[DEVELOPMENT](../../DEVELOPMENT.md) and the [CPU setup guide](../../../environment/cloud-cpu/README.md).
On a fresh clone:

```bash
git clone --branch cloud-engine-continuation https://github.com/georgpou/AToM_MLMM.git
cd AToM_MLMM
git status --short --branch
git rev-parse HEAD
git merge-base --is-ancestor 2c02cc2713924140a82aefda37fd5885747e5837 HEAD
git switch -c g10-engine-next
```

Use an unused child branch name, record actual HEAD, and keep main and published
predecessors unchanged. Do not reset/rebase/force-push. This branch inherits accepted
report snapshot `2c02cc2713924140a82aefda37fd5885747e5837`, scientific source
`424a859732b77b2f91cd03b12bb3f0b8adf3f541` and reviewed submission
`bc6fd520308fba7e7448929138eb91e80ca6f063`. Their historical verification was
543 full CPU passes and 52 independent checks with additional numerical probes;
see [G09 v5](../../../Worker_Log/Milestone_05/Gate_09_v5_audit.md) and
[G10 v2](../../../Worker_Log/Milestone_05/Gate_10_v2_audit.md).

Retained source, scientific fixtures, package locks, model bytes and reference
ledgers match that baseline. Optional external-execution code and its tests are
removed. Accepted CPU definitions in the
[dense-solvent/pair-exchange amendment](../specs/m05-dense-exchange-amendment.md)
are unchanged. Old sealed workers retain their original source identities: do not
silently resume or migrate an older bundle using this checkout. Reconstruct old
evidence with its exact frozen source; make new attempts for new code.

## First implementation: G10 multi-state runtime

Read [G10-T2/T3](../gates/G10-restart-and-replica-exchange.md), relevant S05/S07
sections and `exchange.py`, `exchange_journal.py`, `workflow.py`, `persistence.py`
and `adapters/atom.py`. The accepted controller runs **two workers only**.
Extend it to a bounded serial CPU controller for an explicitly declared schedule
of at least three states; this is technical development beyond the accepted pair
scope, not full G10/M05 closure.

Before implementation, document and independently review the scheduling and
transaction extension. Use **GPT-6.1-sol / max** for review, with a compact diff,
exact snapshot and focused evidence. Preserve the original pair API/regressions.
Use the existing pinned AToM pair-decision adapter; do not create another
Hamiltonian or Metropolis implementation. Define pair selection/order, stable
walker identities and the full walker-to-state permutation explicitly.

Require fresh four-entry reduced energies for every attempted pair, including
outside terms; test against independent actual-context evaluations. Parameter
changes must refresh energies. Save unique sample IDs, raw records and complete
state histories. A whole scheduling boundary must commit all worker checkpoints
and both host RNG streams atomically. Fault tests must cover partial integration,
decision/refresh persistence, rename and derived-report failures. Default resume
must reject incomplete work; explicit rollback/replay must preserve failures,
restore the previous committed boundary and avoid duplicate/lost records.

Start with existing analytic controls, then small solvated ABFE and unequal-ligand
RBFE fixtures through the same shared engine. Bound frames/steps and run jobs
serially. Do not require production-length trajectories to demonstrate scheduling
or restart correctness. Log this increment as the next unused `Gate_10_vN_worker.md`
and record an independent audit only when actually performed.

## Subsequent cloud work

1. Qualify G08 analysis for exchanging correlated walkers before reporting its
   uncertainty. Raw-energy reconstruction already works; the existing fixed-state
   thinning profile does not qualify exchanging-walker statistics.
2. Advance [G11](../gates/G11-protein-abfe.md) and
   [G12](../gates/G12-dual-ligand-rbfe.md) technical implementation as their relevant
   runtime dependencies pass: generalize admitted manifests/cap collections as
   needed, preserve full real forces and both-map guards, and test one/two complete
   ligands through the common engine. Review new supported chemistry/partition
   definitions before claiming protein support. Start with tiny controls and
   fixed-coordinate/worker/restart checks.
3. Preserve the existing 18-crown-6/methanol ABFE fixture. The user's preferred
   host–guest RBFE starter is **methanol → ethanol in 18-crown-6**; a qualified
   two-guest input is still needed. The abandoned unreviewed notebook branch is
   not an accepted source for that input. Prepare it independently when needed,
   recording chemistry, parameterization, atom identities and both-map clearance.
4. Advance [G13](../gates/G13-performance-and-release.md) CPU resource measurements,
   reproducible packaging and support matrix after the relevant engine checks.
   GPU performance/device claims require actual hardware evidence. Full release
   acceptance retains the gate's earlier milestone requirements.

## Environment and bounded verification

This machine has a validated unchanged main/Amber setup at
`/workspace/m05-cpu-setup-v2`; activate in every scientific shell:

```bash
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python -m pytest tests/workflow/test_persistent_exchange.py tests/workflow/test_replica_exchange.py tests/workflow/test_evidence_export.py tests/workflow/test_solvated_process_restart.py -q
python tools/check_docs.py --self-test
```

A replacement machine uses `environment/cloud-cpu/install.sh` with its own
external prefix and the unchanged locks. Do not assume this session's environment
or untracked outputs exist elsewhere. The
[runner guide](../../../examples/cloud_engine/README.md) documents the shared
CLI and accepted fixtures. Test the changed requirements first; run the available
CPU suite after meaningful engine changes. Do not repeat prior scientific reviews
without a relevant change or new failure.

## Physical and HPC boundary

M03/G07-T4 remains physically blocked: seven boundary-sensitivity exceedances,
pilot force failures and 29 missing new references remain. Preserve all 46 accepted
G05 records, the accepted pilot and original receipts/failures. The
[reference handoff](G07-reference-remaining-v2.md) owns scientific settings and
resource decisions. Its historical G07-only prohibition on later technical work
is superseded by this assignment; its physical/reference safeguards remain.
The cumulative ledger has charged **2325.6446500519996 s**
of its original **86400 s**; its continuation screen remains false. Do not reset
that ledger, enlarge its budget or launch expensive QM as an engine test.

Local 64-water controls test coupling/runtime, not equilibrated liquid solvent or
converged affinity. Full M05, protein physical qualification and production remain
open. Defer long QM/solvent/protein sampling and HPC scripts until cluster details
and resources are available. Then qualify the exact cluster profile with a small
parity/checkpoint/restart trial before production. No cluster authorization or
account information is needed for the cloud implementation work above.
