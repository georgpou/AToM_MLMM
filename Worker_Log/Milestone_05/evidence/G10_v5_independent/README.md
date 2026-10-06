# G10 v5 independent combined audit evidence

The sole independent `gpt-6.1-sol / max` reviewer audited the finished Tasks 1–4
batch at exact frozen HEAD `edd587679aaa110ea687cca29b9e3aee70b7b6f0` on
`g10-engine-next`, source/test-identical to submission
`ecace38b34e15fae65508b2ee9cd2f535a1b85c4`. The [audit report](../../Gate_10_v5_audit.md)
gives the complete **RED / changes_required** decision, seven findings and
minimal repair/regression requirements. Source, tests, specifications, worker
reports and failed scientific artifacts remained frozen. No repair was made.

Every scientific command used the exact activation shell below, ran serially,
and has its complete raw output here. The machine reports cgroup memory limit
`8589934592` bytes and CPU quota `200000 / 100000` (two CPUs). Jobs stayed on the
Reference double/MACE CPU float64 profile; there was no QM, GPU, package/model/
fixture replacement or extended sampling. The full saved 577-pass worker suite
was verified as retained evidence rather than redundantly rerun.

```bash
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

[commands.json](commands.json) records the complete shell commands, actual exit
statuses, counts, finished UTC and timestamp source. Characterization scripts
deliberately return **1** when a collected rejection/durability obligation fails;
their complete JSON results and logs preserve those failures. They do not
represent import/dependency failures. Fresh pytest outcomes total **47 passes,
zero skips**; the independent controls and **17 violating cases** are separately
counted and are not inflated into pytest totals.

| Probe/control | Reproducer | Full output/result |
| --- | --- | --- |
| Identity and immutable historical failures | [identity_probe.py](identity_probe.py) | [log](identity-probe.log), [results](identity-results.json): exit 0; 38 source files, 24 submitted hashes, 20 original frozen bundles and four gzip/raw log identities. |
| Fresh focused existing multistate/fault coverage | Exact pytest command in commands.json | [log](focused-pytest.log): exit 0, 42 passes, 20 deselected, 74.87 s. |
| Unchanged pair continuation and actual positive-threshold decisions | Exact pytest nodes in commands.json | [log](pair-compatibility-pytest.log): exit 0, 5 passes, 7.31 s. |
| Independent nonlinear analytic force/energy/permutation, exact stationarity/RNG and inert admission | [analytic_admission_probe.py](analytic_admission_probe.py) | [log](analytic-admission-probe.log), [results](analytic-admission-results.json): two passing numerical cases, stationarity/RNG pass, nine rejection challenges with seven violations; exit 1. |
| Restored timeline/geometry, actual postrename and report faults, ordered fsync trace | [transaction_restore_probe.py](transaction_restore_probe.py) | [log](transaction-restore-probe.log), [results](transaction-restore-results.json): five violating cases; exit 1. Syscall ordering is observed; no power-loss experiment is claimed. |
| Exact retained solvated ABFE/RBFE actual contexts and stale-coordinate rejection | [molecular_probe.py](molecular_probe.py) | [log](molecular-probe.log), [results](molecular-results.json): exit 0, both cases pass, 36 fresh schedule evaluations, eight attempted matrices; zero new integration/preparation frames. |
| Additional public selection and rehashed inert challenges | [additional_inert_probe.py](additional_inert_probe.py) | [log](additional-inert-probe.log), [results](additional-inert-results.json): 16 passing selection controls and five violating admission cases; exit 1. |

The fresh analytic prepared/prefix/failure trees are retained outside Git in
`/workspace/G10_v5_independent_artifacts/`. The molecular probe uses the exact
current-source successful trees at
`/workspace/G10_v5_artifacts/probe-fix1/{abfe,rbfe}` and copies the stale probe to
the independent artifact directory before challenge. Earlier worker bundles at
`/workspace/G10_v5_artifacts/{focused,repaired,repair2,final-focused}/{abfe,rbfe}`
were independently hash-verified inertly against their complete original source,
model and environment manifests; they were not migrated to current code.
Reproducing a failed historical run requires that run's frozen original source.

The report-only completion record is [completion-results.json](completion-results.json).
It records fresh documentation self-test, diff checks, unchanged reviewed trees,
permitted staged paths and evidence hash verification. The full documentation
output is [docs-self-test.log](docs-self-test.log). The first report-only checker
attempt found its own linked output file missing before that file was created;
the [original failed output](docs-self-test-first-attempt.log) and
[cause/correction](documentation-first-attempt.json) are preserved. Precreating
that log resolves the local link error without changing reviewed implementation.
[manifest.json](manifest.json) contains SHA-256 for every compact evidence file
except itself, plus final report/STATUS digests; committed Git trees provide
their durable identity. The exact
audit commit and final clean status are stated in the final handoff.

Existing 46 G05 records, seven G07 sensitivity exceedances, original pilot force
failures, 29 missing references and QM ledger `2325.6446500519996 / 86400 s` with
false continuation screen are unchanged. Full G10/M05, chemical accuracy,
protein, GPU/HPC/production, affinity, equilibrium/mixing/convergence and
exchanging-walker uncertainty remain open or blocked. `binding_result` remains
`not_evaluated`.
