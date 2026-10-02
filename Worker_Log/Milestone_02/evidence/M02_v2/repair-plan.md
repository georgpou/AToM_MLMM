# M02 admission repair plan — fresh continuation

Goal: close M02-R1/R2/R3 and obtain independent combined G02/G03/M02 review on one exact repaired snapshot, continuing handoff `a8098a43d46df76b981861aa8dec0522d31be966`.

The user authorizes implementation, independent closure, and publication only on `m02-analytic-atm`. Use the existing clean checkout as AGENTS directs. Implement repairs inline, then dispatch one fresh reviewer. The v1 draft remains historical and unexecuted; new tests are independently reassessed and written under `tests/contracts/test_m02_admission.py`.

Constraints: S01–S07 contract version 1, all-real derivatives, full maps, complete fixed ligand membership, physical ownership and units remain unchanged. Reference limits stay `1e-8 kJ/mol` / `1e-7 kJ/mol/nm`; FD steps stay `1e-3`, `1e-4`, `1e-5 nm` with the recorded final `1e-5` component limit. Preserve both exact locks, separate core/Amber environments, trusted hash-checked loading, all submitted v1 evidence and protected branch tips.

- [x] Verify published handoff, 126 source/input hashes and protected tips; install unchanged locked CPU bundle; run full baseline and preserved admission probes to new paths.
- [ ] R1: write wrong-expression and missing-global sealer/reload assertions, linear and harmless-whitespace controls. Confirm failures; add actual ATM expression/global validation in `atm.py` before sealing or Context construction. Compare expression tokens so whitespace inside an identifier is not accepted.
- [ ] R2: write direct/State physical and preparation mutation assertions, native/upstream collision assertions and independent positive energy/force controls including a permuted final map. Confirm failures; pin fixed globals in the common evaluator and reject schedule/physical collisions before construction, sealing and reload. Preserve explicit state changes and restoration.
- [ ] R3: write PythonForce/CustomExternalForce rename/regroup duplicate assertions and distinct-parameter controls. Confirm failures; add a separate label/group-independent duplicate fingerprint in `routing.py`, retaining name-preserving ownership/report identity.
- [ ] Run each repaired regression subset and affected gate checks. Run full/analytic suites, strict validation, upstream regression, preserved independent numerical/FD/history and stale-artifact probes to new output paths. Record all commands/exits and input hashes.
- [ ] Commit repaired source/tests/evidence and matching v2 workers. Fresh independent reviewer reads that exact snapshot, closes all findings, and explicitly reviews combined G02/G03/M02. Reviewer changes audit/evidence only; any further production repair requires fresh evidence and review on its new exact snapshot.
- [ ] Update STATUS and a schema-valid AcceptanceRecord from the actual independent decision; verify report-only differences, immutable v1 artifacts, protected remote tips and the handoff ancestor; commit and push only `m02-analytic-atm`.

Root-cause assessment: metadata-only schedule validation cannot bind executable semantics; Context parameters are separate mutable state from the serialized System; names/groups are labels, so they cannot define duplicate physical content. No new scientific definition or tolerance amendment is needed.

Review focus: missing or repeated required ATM globals; collisions on fixed as well as varying schedule names; both raw endpoints with a physical global on a transferred atom; state restoration with stale auxiliary values; same-name distinct parameters and old trusted artifacts. The final reviewer must also retain every stable G02/G03 assertion and M01's accepted prerequisites.
