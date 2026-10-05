# Next assignment: unattended Colab CPU MD and QM notebooks

**User steering:** defer TPU. Deliver notebooks the user can launch on Colab for
long runs without Codex monitoring/polling. Cover ABFE/RBFE MD and continuation
of the missing QM references. This is a future assignment, not executed evidence.

## Reuse completed work

Continue the published `m05-colab-workflows` lineage; inspect its current HEAD
and changes before editing. Exact accepted executable source:
`424a859732b77b2f91cd03b12bb3f0b8adf3f541`; reviewed submission:
`bc6fd520308fba7e7448929138eb91e80ca6f063`. The
[previous handoff](M05-after-colab-tooling.md) records 543 full CPU passes,
52 independent passes, denser-water pilots, offline export/restart and persistent
pair exchange. These are completed; do not redo implementation, historical QM,
full tests or independent review merely to onboard or change reporting.

The current [CPU notebook](../../../notebooks/m05_colab_cpu.ipynb) is a validation
wrapper, not yet the requested long-run MD/QM interface. No QM notebook exists.
Actual Colab execution has not been observed because no authorized executor was
available. Local notebook schema/orchestration checks are already complete.

## Meaning of the Colab check

A one-time small runtime smoke check establishes that the locked installation,
actual approved model, existing ABFE/RBFE control and checkpoint/export/resume
work on Colab's filesystem/runtime. Compare fixed-coordinate observables with
saved references. This checks deployment portability; it is not another method
implementation or repetition of all543 tests. Broaden checks only if a mismatch,
scientific change or new profile warrants them. If direct execution remains
unavailable, provide exact user-run cells and verify returned artifacts before
claiming Colab qualification.

## Requested notebook work

- Make MD launch settings visible: selected admitted input, exact source/profile,
  schedule, seed, steps, output path, checkpoint/export interval and resource
  bounds. Retain separate quick validation cells. Reuse the common engine and
  CLI; do not put a second scientific implementation in a notebook.
- Run in resumable bounded segments, stopping at committed safe points for
  complete verified durable snapshots. Preserve partial/failed attempts, unique
  samples, state/walker/RNG histories and original immutable exports. Authenticate
  storage only through the user. Export remains outside active source trees;
  mounted storage is not the transactional working filesystem. Display clear
  launch/resume instructions so the user can restart after runtime loss.
- Add a CPU QM notebook around the existing frozen reference queue/runner and
  separate Psi4 environment. Restore and verify the original progress ledger,
  receipts, inputs and accepted records; calculate only missing references.
  Keep existing scientific settings, parser and validation policies. Record
  resources/elapsed charges/results automatically; stop at budget/resource
  limits and persist committed job boundaries. No long QM launch in Codex solely
  to prove notebook orchestration.
- Check changed orchestration with focused tests and official notebook schema;
  perform required scientific checks if source behavior changes. Serialize jobs,
  keep heavy calculations in user-run Colab, and use one final reviewer for a
  ready submission while the root agent idles.

Current exchange supervision is two-worker, and controls are small capped
fragments. General replica scheduling, exchanging-walker statistics and actual
host–guest inputs need explicit method work/qualification if included in the
next delivery. Long notebook uptime does not itself qualify binding results.
Choose requirements for the actual target systems before implementation.

## Preserved constraints

Colab may terminate sessions; promise durable recovery, not unlimited uptime.
No new separately billed GCP service is assigned. TPU tooling remains preserved
but deferred. No accelerator substitution or CPU lock/model/tolerance changes.

There are29 missing QM references. The unchanged ledger has charged
2325.644650052/86400s, leaving84074.355349948s. The old two-CPU screen estimated
34.1646h versus23.3540h remaining and required16.7615GiB scratch plus5GiB reserve.
Reassess on actual Colab resources; do not reset the ledger or weaken limits.
See [remaining-QM provenance](G07-reference-remaining-v2.md). Notebook creation
is authorized; a budget extension is not implied, and launches must satisfy the
reviewed execution/resource conditions.

Preserve seven sensitivity failures, pilot force exceedances and M03 physical
blockers. Full M05 remains open. External OpenMM issues are examined/reported,
with repair secondary unless they seriously threaten method development.
