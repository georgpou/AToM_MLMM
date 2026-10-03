# M00 v3 quantum launch and user-requested stop checkpoint

The explicitly approved quantum-only batch was launched from
`3124c6d275bf19a32ce364dfdb83b11115828ac5`; [launch metadata](launch-v1.json)
binds the actual program, approval and frozen input hashes. The user requested
pause and a same-branch fresh-session handoff on 2026-10-03. No calculation was
restarted to prepare this checkpoint.

`quantum-attempt-v1/` retains eight computed JSON records and their exact
orders, launcher receipts and Psi4 logs. It is about 0.40 MiB and contains no
complete coordinator manifest. Seven coordinator exit-zero receipts appear
in [observed output](coordinator-observed-output.txt); the eighth completed
worker saved `butane-acetamide-d3.4-r0` but its coordinator receipt was not
observed. [Interruption](interruption.json) preserves the transport error.

[Stop state](stop-state-20261003.json) lists all completed hashes, the 38
remaining names and resources at 10:58:48 UTC. [Checkpoint verification](checkpoint-verification.json)
rechecks eight finite, exact-provenance records, 270 source/input hashes,
46 frozen-plan hashes and the 105 reference packages. Replay from the repo
root after core activation:

```bash
python Worker_Log/Milestone_00/evidence/M00_reference_v3/verify-stop-state.py
```

The helper launches no model or quantum calculation; it refreshes its own
verification JSON if rerun. [Docs verification](checkpoint-docs.json) records
local-link checks only. Neither is independent scientific acceptance.
`checkpoint-whitespace.json` records native formatting diagnostics in raw
quantum output and a passing authored-file check. Preserve original log bytes.

Disk has about 14.28 GiB free. Container RAM is capped at 8 GiB with no swap;
its lifetime peak reached the cap, but no OOM/OOM-kill event was recorded.
The cause of transport loss is unknown; resource headroom needs measurement
before resumption. See the [fresh-session handoff](../../../../docs/project-0/handoffs/M03-G05-fresh-session.md)
for recovery requirements. Full G05 and model-versus-quantum scoring remain
pending; no partial bundle is admitted as ready.
