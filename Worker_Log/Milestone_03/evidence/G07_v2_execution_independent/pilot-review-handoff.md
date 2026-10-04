# Actual G07 pilot review — graceful-stop handoff

Reviewer: actual independent GPT-6.1-sol / MAX. This addendum records read-only inspection of the actual pilot; numerical G06/G07 acceptance remains inherited. Work stopped immediately at the user's session-quota instruction. No additional testing, QM, cleanup deletion, ledger change or original-attempt edit was performed by the reviewer.

## Actual pilot findings

The worker ran on source `4e2cb06b0e5e0b3b081e379969428ec93a807866`. Original source attempt is `Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1/jobs/ethanol-methanol-d3-r0--full-parent/attempt-0001`.

- Actual worker exit **0**, reason **null**, whole-group cleanup verified. No matching live attempt processes were observed; private scratch was absent after cleanup.
- Generic frozen-record validation and all receipt-bound record/order/launch/diagnostic hashes passed. Energy is **−726.579702009341 hartree** and all **32 gradient rows** are finite. The maximum absolute gradient component is **0.03725669953695445 hartree/bohr**.
- Psi4 1.10.2 explicitly reports **“Energy and wave function converged.”** at log line 295. Final SCF iteration 18 has absolute energy change **1.14824e−11** and RMS commutator residual **5.77813e−11**, both below the frozen **1e−10** limits. Dispersion is present and VV10 is zero. The full printed gradient and final energy are present in the log.
- The admission checker required a different literal, **“SCF has converged.”**, so the immutable receipt correctly retains its original parser `validation_error`. This is an execution validation defect, not demonstrated SCF failure. The prior synthetic audit did not catch this actual-message compatibility gap. **0/30 records remain admitted.**
- Worker record wall time **2324.184968268 s**; actual receipt wall time **2325.623395559 s**; cumulative ledger debit **2325.643222641 s (38.760720 min)** and remaining budget **84074.356777359 s (23.353988 h)**. Preserve that debit without reset.
- **2315** resource samples: maximum group RSS/HWM **3,425,435,648 bytes (3.190 GiB)**; maximum conservative unreclaimable/dirty pressure **3,763,277,496 bytes (3.505 GiB)**; maximum scratch **9,679,518,016 bytes (9.015 GiB)**; minimum free disk **10,652,585,984 bytes (9.921 GiB)**. Maximum observed sample gap was **1.69271 s**.
- Cgroup current reached **8 GiB**, while group RSS stayed below 6 GiB. OOM/OOM-kill/group-kill deltas were **zero**; `memory.events max` increased by **220602**. This indicates significant cache pressure/reclaim activity, not a demonstrated worker-RSS guard failure or OOM.
- Independently recomputed reviewed 29-job remaining-time screen: **122992.524584018 s (34.164590 h)**, exceeding the **23.353988 h** left. **Do not continue the batch under this budget.** Future runtimes remain unmeasured; the screening result is not a guaranteed completion estimate.

Exact original receipt hash: `b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f`. Exact record hash: `c1e34ea209bf4949c0f200859a75a35072ee5cf6e1750f8d7a9044a7259f0eed`. A machine-readable hash/measurement summary is in [pilot-observations.json](pilot-observations.json).

## Recovery design reviewed in principle

A narrow validation-only correction can admit these already-computed bytes without another QM calculation. It must bind the exact original receipt/hash and exact known parser error, require original exit 0/reason null/verified cleanup, revalidate the full frozen record and unchanged logs/diagnostics, and verify no matching live worker/group under the canonical queue lease.

An append-only, durably published `attempt-0002` may contain byte-exact copies of the original inputs, record, logs, samples and identities; an original receipt copy; and an explicit correction statement. The new receipt must plainly identify **validation-only/no new worker launch**, hash the originals and correction, and distinguish historical copied launch/identity data from a new launch. Preserve original attempt/receipt bytes and the existing cumulative ledger; never reopen genuine failed exits, timeouts, resource stops, malformed/nonfinite data or unrelated validation failures through this exception. Normal recovery can then admit the new validated record and pause without QM.

**This is design agreement only.** The newly implemented recovery code was not independently audited, was not accepted by this reviewer, and was not applied to the actual attempt before the stop. Its pending unit/full regression outcomes and concrete source snapshot must be recorded by the worker. Future independent review must test the exact exception/rejection boundaries, lease/process checks, interrupted durable publication, immutable-original preservation, record promotion and unchanged budget before actual admission. Do not run another pilot to bypass the parser defect.

## Cleanup observations

The reviewed [cleanup strategy](../G07_v2/cleanup-strategy.md) preserves every scientific input/output/log/sample/receipt/ledger, all accepted references, model assets, active environments and locks. It removes only private scratch after full group cleanup and keeps receipt-referenced logs readable at their exact original paths. Compression is an archival copy unless a separately reviewed restoration path exists.

The candidate inventory was independently checked: **328 unique regular `.conda`/`.tar.bz2` archives**, all present within the task-owned package cache, **1,422,977,620 bytes** total, no symlinks and no observed open archive handles. No deletion was performed. The installer download and abandoned bootstrap prefix remain conditional candidates requiring their documented checksum/diagnostic and selector/symlink/process checks. Disk reclamation is optional headroom recovery; it cannot fix the reviewed time forecast or excessive anonymous worker RAM.

All seven prior physical sensitivity failures remain blocked. G07-T4 and combined M03 physical closure remain unqualified. Actual pilot convergence and a future validation-only admission do not accept those physical conditions.
