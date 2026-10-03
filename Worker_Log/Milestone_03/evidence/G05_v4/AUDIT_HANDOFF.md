# G05 audit handoff

The user's requested implementation, reference calculations and reports are
complete. **Only independent full-G05 audit/acceptance remains for the scientific
assignment.** The user will choose how to audit; no reviewer was dispatched and
no new independent acceptance is claimed. Publication additionally awaits
explicit GitHub source/history export authorization after automatic review
rejected the push.

The immutable source/data commit is identified in `audit-snapshot.json`.
Calculation implementation is `419b64f7bd79199a0bf999e456f1564fc184cf75`, based on
published same-branch checkpoint `4bb2547`; only this child has local changes.
Main and accepted predecessor branches remain unchanged.

Read the [worker](../../Gate_05_v4_worker.md), [actual results](RESULTS.md),
[G05 assertions](../../../../docs/project-0/gates/G05-local-model-adapter.md),
[STATUS](../../../../docs/project-0/STATUS.md), relevant S06/S07 sections and the
exact approved M00 v3 plan. Inherited scoped software and G04 acceptance remain
in their canonical audits; onboarding does not require replaying historical
audits. The approval decision and input-manifest binding remain unchanged.

Review all G05-T1/T2/T3/T4 and eight stable assertions together on the exact
snapshot. Recovery also needs scrutiny of immutable attempt history, active-PID
and coordinator-lock protection, cumulative budget, process-group timeouts,
record integrity and conservative unknown-exit provenance. Reviewers report
findings rather than implementing repairs.

Observed worker results:

- 46 actual finite energy/full-gradient records; all logs explicitly converged.
  Eight original SHA-256 records reused; 38 new worker/coordinator exits zero.
- Ten monomer rotations and two finer grids pass all frozen limits before model
  comparison. The [bundle validation](quantum-bundle-validation.json) identifies
  the exact fixture and numerical-report hashes.
- Both stable chemical nodes pass with complete raw captures for all 34 cases,
  independent cap/full-parent projections and all 20 contact/sign rows.
- Full source suite: 312 passed. Recovery: 18 focused passes. Strict environment:
  9/9. RED/GREEN and intermediate failures remain preserved, not counted as passes.
- Cumulative debit 4.400612 h under 12 h; two threads, actual Psi4 allocation
  3 GiB under 5 GiB cap; largest new-worker RSS 4.670959 GiB. Total cgroup usage
  includes cache, reached 8 GiB, and recorded no OOM/OOM kill. Scratch cleaned.

Replay from `/workspace/AToM_MLMM-m03-reference-g05`:

```bash
source /workspace/atom-mlmm-g05-v2/activate.sh
python -m pytest -q
python -m pytest tests/integration/test_model_adapter.py tests/integration/test_locality.py tests/integration/test_model_domain.py tests/integration/test_chemical_reference.py -v
python /workspace/atom-mlmm-g05-v2/validate.py --repository "$PWD"
python tools/check_docs.py --self-test
```

Use a new capture directory if collecting fresh raw comparison files; existing
captures are exclusive and must be preserved. The complete quantum fixture
loads without a quantum runtime. **Do not regenerate QM, rerun the finalized
coordinator or overwrite completed attempt files during audit.** A different
machine should reproduce absent prefixes with maintained exact locks; no
replacement weights/packages/settings are authorized.

Leave model metadata unqualified until independent acceptance. G06/G07, protein
binding, periodic/GPU/electrostatic and complete ABFE/RBFE stay outside this
assignment. The named training-reference level does not establish identical
training numerics or exclude these structures from training.
