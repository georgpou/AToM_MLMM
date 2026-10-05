# Independent G09 v3 / G10 v1 review evidence

Reviewer: `gpt-6.1-sol`, MAX dispatch setting. Frozen HEAD:
`b11c16750ad111a2fcafcda7a2d51c6690254e97`. No production, submitted tests,
specifications, worker logs, status or prior evidence were edited.

The [G09 audit](../../Gate_09_v3_audit.md) records one Important finding,
G09-R2, and accepts the bounded amendment's scientific definition. The
[G10 audit](../../Gate_10_v1_audit.md) accepts only the single pair-exchange
boundary. Neither accepts full gates/M05.

Scientific commands ran serially from `/workspace/AToM_MLMM` with:

```bash
source /workspace/atom-mlmm-g09-v3/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH=/workspace/AToM_MLMM/src
python -m pytest -q tests/workflow/test_solvated_handover.py tests/workflow/test_replica_exchange.py tests/workflow/test_failure_geometries.py --basetemp=/tmp/atom-mlmm-cloud-independent-affected
python -m pytest -q Worker_Log/Milestone_05/evidence/cloud_v3_independent/probes.py --basetemp=/tmp/atom-mlmm-cloud-independent-final
python Worker_Log/Milestone_05/evidence/cloud_v3_independent/verify_manifests.py
```

`affected-tests.log`: exit 0; 28 passed in 92.83 s, no skips.
`probes.log`: exit 1; 7 passed, one expected safety-contract failure in 5.72 s.
The failing node is
`probes.py::test_map_archive_failure_does_not_hide_original_scientific_error`.
Only a mapped XML write is faulted after a real actual-worker step and an
independent scientific trigger. It causes an archival OSError to replace the
original NumericalDomainError before primary `error.json` is written.

`archive-failure/cli-characterization.json` captures the normal CLI boundary:
exit 2, stderr only `OSError: independent mapped State archive trigger`, no
primary error record and no samples. State/checkpoint/map0 that survived are
retained alongside that capture. Its separate command was:

```bash
python -m pytest -q Worker_Log/Milestone_05/evidence/cloud_v3_independent/probes.py::test_characterize_archive_failure_normal_cli_output --basetemp=/tmp/atom-mlmm-cloud-independent-cli
```

`archive-cli-test.log`: exit 0, 1 passed in 0.58 s. The final complete probe run
also performs that characterization. The probe's single overflow warning is
deliberate nonfinite-output fault injection, which rejects before Metropolis.

`manifest-verification.json` and `.log`: exit 0, 48 exact source/input hashes,
114 G09 and 11 G10 capture hashes, both complete local portable workers' 48
payload hashes, submitted frame/box/force integrity and captured exchange
matrix/exponent reconstruction all verified. The 27-image oracle uses the
actual preliminary PDBs in `/workspace/cloud-engine-pilots/water-v3`; those
installations remain required for replay of these local artifact probes.

`initial-probes.log` retains the first harness run: two PDB list-indexing errors
and a too-specific expected exception type were reviewer-probe mistakes,
corrected only in this new evidence file. They are not production findings.
`pre-cli-probes.log` is the subsequent 6-pass/one-finding run before adding the
normal CLI characterization. No submitted test was altered. The source,
reproducer and failing scientific contract remain available for repair/closure
review on a new snapshot; these logs do not claim that R2 is repaired.
