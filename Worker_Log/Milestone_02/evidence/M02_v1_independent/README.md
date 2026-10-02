# Independent M02 v1 review evidence

Reviewer: independent Codex `/root/m02_independent_audit`, GPT-6 family; exact runtime backend/version and reasoning settings are not exposed. No implementation or repair was authored by this reviewer.

Exact submitted/reviewed HEAD: `a13019390f9770a42a5711bbb98025bd571ea40b`. Tested source/input SHA: `4c952dba5563572cf9e39527e64fe28ee201c385`. Diff base: `87146b4cc7fbd0b58d6688903a5ba081b813ac13`.

- `command-results.json.gz` and `run_commands.py`: independent G02/G03/full/analytic/strict/upstream/documentation/whitespace commands, outputs, exits and UTC timings.
- `strict-validation.json.gz`: newly run nine-check installation validation, copied from the actual run; preserves exact inventories and the core/Amber separation.
- `snapshot-check.json`: all 126 submitted source/input hashes independently match; source/tests/fixtures/environment diff from code SHA to review HEAD is empty.
- `probe_numerics.py` and `independent-numerics.json`: newly written independent Cartesian and nonlinear oracle; 66 native/upstream cases on a perturbed geometry and nonidentity final mapping, eight all-21-component FD sweeps and eight upstream A-B-A cases. Does not import worker/test oracles. Includes both protocols, providers and platforms; the extra ten transition cases use CPU.
- `probe_admission.py` and `admission-results.json`: three material findings plus unaffected controls. `--require-rejection` exits 1 on the submitted snapshot because 13 expected rejection probes are admitted. Default exit 0 means observations were captured, not acceptance.
- `worker-numerics-rerun.json.gz`: independently rerun worker-authored 16-case numerical script. This confirms replay of existing worker evidence and is separate from the new oracle above.
- `supplementary-results.json`: actual supplemental commands, observed exits and numerical/fault summaries.

From the repository root, activate main in every shell:

```bash
source /workspace/.onboarding/atom-mlmm-m02/activate.sh
python Worker_Log/Milestone_02/evidence/M02_v1_independent/run_commands.py
PYTHONPATH=src:. python Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_numerics.py
PYTHONPATH=src:. python Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_admission.py --require-rejection
```

The final command is deliberately RED until independent repair closure. Source/tests/fixtures/environment/STATUS were not changed. Canonical verdicts are in `Gate_02_v1_audit.md` and `Gate_03_v1_audit.md` in the parent milestone folder. Analytic transfer architecture only; no caps, molecular chemistry, GPU, periodic/electrostatic physics, binding correction or full asynchronous restart/exchange qualification.
