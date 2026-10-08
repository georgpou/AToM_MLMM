# Retained evidence and historical recovery

Closed-run copies of source code, environment archives, trajectories, checkpoints,
pytest scratch directories and notebook-era generated evidence have been removed
from the working tree. The cleanup retires 7,965 tracked files / 216,057,640 bytes.
The history is unchanged; this does not reduce the size of an existing Git clone.

The exact recovery snapshot is
[`590cb5258696042b29856df37f6053ba820d2f56`](https://github.com/georgpou/AToM_MLMM/tree/590cb5258696042b29856df37f6053ba820d2f56/Worker_Log).
For example, recover a historical directory outside the active checkout:

```bash
mkdir -p /tmp/atom-historical-evidence
git archive 590cb5258696042b29856df37f6053ba820d2f56 Worker_Log/Milestone_05/evidence \
  | tar -x -C /tmp/atom-historical-evidence
```

Remaining prior evidence is required by current acceptance hashes, reference
lineage or recovery tests. In particular, M00 neutral reference records/receipts,
the G07 authorization and charged QM ledger, and support-matrix audit/worker
evidence are preserved byte for byte. Retained historical Markdown reports are
also unchanged; active documentation points to exact Git history where an old
artifact has been retired. Frozen reference/model/environment bytes are retained.

New benchmark jobs belong under ignored `runs/` or an external run root.
Keep one concise worker record per task here; do not check generated trajectories,
environment installations or copied source trees into the repository.
