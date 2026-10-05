# G10 v4 focused RED/GREEN evidence

Worker model/effort: GPT-6 Luna / max. Every pytest shell used
`source /workspace/m05-cpu-setup-v2/activate.sh` and
`export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"`.

The late RED blocks below preserve the failing assertion and pytest summary as
excerpts from actual tool output; they are not full raw pytest logs. Full raw
output is saved for the final required command and secondary-archive
regression. Earlier staged Task 1–3 runs were not tee'd to files and are
labeled as summaries rather than raw logs.

## Earlier staged Task 1–3 results (summaries)

- **Task 1 admission/mode/source inventory:** the first API probe failed while
  the new controller symbols were absent. A following test-harness attempt
  imported `read_multistate_boundaries` from `exchange` instead of
  `exchange_journal`; that collection error was corrected before the valid
  GREEN. The focused admission/mode/source-inventory run then passed **4 tests
  in 3.41 s**.
- **Task 2 scheduling and energy oracle:** the valid RED produced **4 expected
  `NotImplementedError` failures** for the missing multistate scheduler/oracle
  behavior while the **4 direct actual-adapter threshold controls passed**.
  The GREEN passed **8 tests in 5.52 s**. One earlier collection attempt had a
  test-only syntax error at a line break after `/`; it was fixed before the
  valid RED run.
- **Task 3 persistence/replay:** an initial partial-integration attempt used a
  monkeypatched acceptance draw on one branch but not the reference branch,
  so the checkpoint RNGs differed; removing that setup mismatch produced the
  valid partial-integration replay GREEN (**1 test in 2.89 s**). The durable
  phase-failure matrix passed **6 in 16.48 s**. Capture/seal/precommit and
  postrename/reporting checks passed **7 in 16.47 s** after fixing the test to
  explicitly allow pending work and match the `.json` artifact names. Tamper,
  fresh-restore, and controller-lock checks passed **8 in 9.13 s**. No
  secondary archive failure was observed in those early runs; it is injected
  and covered by the saved follow-up below.

These earlier outcomes are summaries from the interactive worker trace; their
original full commands/output were not saved to an artifact at the time.

## Runtime and initial-assignment admission

RED command:

```bash
python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_inert_admission_binds_runtime_and_initial_assignment -q
```

The sealed journal was given a rehashed `runtime_identity` of 64 zeroes. Before
the worker-contract cross-check, the inert reader accepted it:

```text
F [100%]
E       Failed: DID NOT RAISE <class 'ValueError'>
1 failed in 1.48s
```

The same test then altered the initial worker-0 report to a different valid
schedule state, resealed the initial tree, and updated the next boundary's
previous-manifest link. With the initial permutation check temporarily absent,
that inconsistent assignment was accepted:

```text
F [100%]
E       Failed: DID NOT RAISE <class 'ValueError'>
1 failed in 1.51s
```

After repair, the test passes. The journal reader binds bundle, runtime,
schedule, selected parameters, atom IDs, runtime mode and initial reports to
the sealed worker records before any trusted worker load.

## Complete restored energy report

RED command:

```bash
python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_fresh_restore_compares_complete_total_before_next_integration -q
```

The test altered only `total.diagnostics.platform` in a correctly resealed
committed report. The prior restore check compared energy, forces, atom IDs,
raw energies and parameters but accepted the changed diagnostic and integrated
the next boundary:

```text
F [100%]
E       Failed: DID NOT RAISE <class 'ValueError'>
1 failed in 2.51s
```

After repair, fresh evaluation compares every saved `EnergyForces` field,
with the existing tight numeric tolerances for energy and forces. A separate
portable-State regression changes a saved schedule parameter while preserving
coordinates and checkpoint bytes; it verifies rejection before another sample
is staged.

## Pre-loader runtime and geometry admission

RED command:

```bash
python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_runtime_and_geometry_are_admitted_before_worker_load -q
```

The prepared runtime JSON and worker manifest were consistently resealed as
`Verlet`. Before the exact runtime check, admission proceeded to the trusted
loader spy, proving the runtime was checked too late:

```text
F [100%]
E       AssertionError: trusted worker loader ran before exact runtime/geometry admission
1 failed in 0.98s
```

After the guard was added, the same regression passes for both the unsupported
integrator and a displacement that disagrees with the sealed transfer. The
trusted loader is not called and no output directory is created for either
case (`1 passed in 1.09s`).

## Secondary archive failure

`secondary-archive-regression.log` is the full raw output of
`python -m pytest tests/workflow/test_persistent_exchange.py::test_multistate_primary_error_survives_secondary_worker_archive_failure -q`.
The test injects a primary worker sample-capture `RuntimeError` and a secondary
worker-1 archive `OSError`; it passes in 2.44 s, with the original exception
preserved, the secondary operation retained in `pending/failure.json` and an
exception note, and unaffected worker archives captured.

## Final GREEN results

The four focused identity/RNG/restore controls passed together (`4 passed in
4.69s`). The final retained-engine command and complete output are in
[`required-pair-export-restart.log`](required-pair-export-restart.log): 73
passed in 195.08 seconds. It includes all persistent-pair, multistate,
replica-exchange, evidence-export and solvated-process-restart tests. The
independent docs self-test output is in [`docs-self-test.json`](docs-self-test.json):
zero errors, 212 Markdown files and 1,434 local links checked, including this
worker record and the updated STATUS entry.

## Evidence checksum verification

The first artifact-manifest check was invoked from the repository root even
though `artifact-hashes.txt` stores paths relative to this evidence directory;
that invocation reported five missing files. Re-running `sha256sum -c
artifact-hashes.txt` from `evidence/G10_v4/` passed all five entries. The source
manifest check from the repository root passed. No source or scientific test
result changed during this correction.

The first staged `git diff --check` also flagged trailing Markdown hard-break
spaces in the worker-record metadata. Those spaces were removed before the
final staged whitespace check.
