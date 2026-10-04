# Independent G09/G10 vacuum technical review

Actual independent reviewer: GPT-6.1-sol / MAX, explicitly requested dispatch.
Exact submission `9e7a84c91e8c252c33221b8e2331e595d54315ca`, scientific source
`34cc6ba0d3e618450128b4a679ffc64046c48733`. See the [canonical audit](../../Gate_09_v1_audit.md).

`snapshot_probe.py` verifies every tracked Git blob in the root and detached
checkout, the worker's 110-file source/input/test manifest and preservation of
all prior M04 artifacts. `snapshot-check.json` and `closing-preservation.json`
record exact snapshots and resources.

`command_runner.py` records command argv/cwd, exit codes, timestamps, wall time,
RSS and cgroup observations in each `.result.json`, with separate stdout/stderr.
`focused-new.*` contains the independent 22-test pass; frozen worker full-suite
evidence was inspected and carried forward, not represented as an auditor rerun.

`admission_probe.py` / `admission-report.json` describe 49 deliberate rejected
settings, chemistry, journal and actual worker inputs. `numerical_probe.py` /
`numerical-report.json` independently map the saved real coordinates and compare
direct physical/full-real-force and outside-restraint oracles at 12 frames with
36 actual worker state evaluations. The frozen crown capture remains in worker
evidence; `capped-controls/` retains useful independent control outputs, sealed
artifacts and high-precision State. Its capture manifest verifies exact bytes.
These are evidence subsets; source/environment/model payloads remain bound to
the exact submission and complete local attempts.

`integration_failure_probe.py` is the failing G09-R1 regression: a real worker's
integrator advances once and throws within `step`; the controller saves no
failure archive. `integration-failure-auditor-state.xml` and the companion
checkpoint are **auditor captures**, not production retention. The original
failure output/report is preserved.

The first numerical-harness invocation used the wrong RestraintSpec field name.
Its original script and exit-1 output are retained as `numerical_probe_initial.py`
and `numerical-probe-harness-error.*`; corrected numerical checks pass. Only
independent harness files were edited. Passing synthetic pytest temp trees were
not submitted; no frozen worker or prior G08 artifact was edited.
