# Before-HPC audit fixes v2 worker

Implemented V2-F1 and V2-F3 on branch `before_HPC`, starting at
`0409da8dd7f6c8889a64bd37efbe7102cd9005ef`. F1 now rejects repeated
initialization identities across histories under both resampling methods while
retaining the persistent fingerprint and distinct-stream controls. F3 keeps the
worker-manifest SHA check and delegates journal source admission to the existing
recursive verifier; runtime/profile identity checks in the journal reader remain
in place. Tests cover both duplicate-refusal modes, distinct persistent streams,
undeclared nested modules, nested symlinks, and a relocated matching journal.

## Evidence

Checks ran serially in the main CPU environment; `/sys/fs/cgroup/memory.max` was
`8589934592` bytes. Each test shell sourced
`/workspace/before-hpc-cpu-v2/activate.sh` and exported
`OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
PYTHONPATH="$PWD/src"`. AmberTools was not invoked. Raw pytest output is kept
unchanged in the linked `.log` files.

RED ran against unchanged source at the base commit, with only the two regression
tests added. From `2026-10-07T19:58:30Z` to `19:58:38Z`, the command exited 1:
**3 failed, 1 passed, 7.73 s**. The synchronized-block duplicate and both
journal inventory challenges reproduced; the independent-run refusal and
relocated journal positive passed. See [RED output](evidence/audit-fixes-v2/red-f1-f3.log).

```bash
python -m pytest -q \
  tests/workflow/test_persistent_initialization_provenance.py::test_persistent_analyzer_rejects_duplicate_producer_streams_but_accepts_distinct_streams \
  tests/workflow/test_multistate_inert_repairs.py::test_multistate_journal_reader_checks_complete_recursive_source_inventory
```

GREEN used the same command from `2026-10-07T19:58:53Z` to `19:59:01Z` and
exited 0: **4 passed, 8.07 s**. See [GREEN output](evidence/audit-fixes-v2/green-f1-f3.log).

The bounded compatibility command ran from `2026-10-07T19:59:16Z` to
`19:59:27Z` and exited 0: **10 passed, 9.76 s**. It covers persistent analysis,
synthetic initialization controls, the journal reader, trusted-loader admission,
and recursive source verification. See [compatibility output](evidence/audit-fixes-v2/compatibility-f1-f3.log).

```bash
python -m pytest -q \
  tests/workflow/test_persistent_initialization_provenance.py \
  tests/sampling/test_exchange_uncertainty.py::test_mislabeled_iid_histories_and_reused_initializations_are_rejected \
  tests/sampling/test_exchange_uncertainty.py::test_independent_run_resampling_keeps_complete_runs_without_nested_blocks \
  tests/workflow/test_multistate_inert_repairs.py::test_multistate_journal_reader_checks_complete_recursive_source_inventory \
  tests/workflow/test_persistent_exchange.py::test_multistate_source_inventory_must_match_before_trusted_load \
  tests/workflow/test_runtime_source_inventory_recursive.py
```

Changed-file SHA-256 values at verification:

| File | SHA-256 |
|---|---|
| `src/atm_mlmm/exchange_analysis.py` | `1af086d9953abf15aff13dee53aaae9027ae9af2be3ab19f4dc3636eb684ffe8` |
| `src/atm_mlmm/exchange_journal.py` | `b90dbf6a93bb0080523a08ad80e3f40bbce199940d2051cf70806c8598a40094` |
| `tests/workflow/test_persistent_initialization_provenance.py` | `f8ebeda6122bb202c3db7e46dfde148a7f827126690f00b10fddf4dd1a3dd672` |
| `tests/workflow/test_multistate_inert_repairs.py` | `072f5851c2226f00bd2bf3dc1b8cd79e49c732c34d9bf14c6248d22ba21c65f3` |

No full-suite replay, package rebuild, dependency change, model/QM/dynamics,
cluster/GPU/production run, scientific threshold change, or sealed-worker
migration occurred. The independent audit and all scientific, release, C3,
full-suite, and hardware holds remain open for parent review.
