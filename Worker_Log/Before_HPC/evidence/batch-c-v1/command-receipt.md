# Batch C command receipt

Checkout: `/workspace/AToM_MLMM-before-HPC`, branch `before_HPC`. Baseline
source was `07454097b0a1c9dafa9e0ce704f0c0a3e07b4b9a`. Frozen-design source
at qualification and final focused check was `911acc0909c7b43ac620b8bd5508f94f08f3f26b`.
The parent-owned `Worker_Log/Before_HPC/progress.md` was already modified at
dispatch and is excluded from this batch.

Every scientific command used the ready CPU v2 activation at
`/workspace/before-hpc-cpu-v2/activate.sh`, then
`OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2` and
`PYTHONPATH="$PWD/src"`. Activation script SHA256:
`ab4585b8dce374bf6976c03dd2163a1672096b1d4adeb5587e57ef6c75ddecae`.
No setup replay or full CPU suite was run.

## Qualification and final focused run

The qualification design was frozen before running controls. Its three
independent records are `design.json` SHA256
`ebb43b426d05a70155add2cbd5595b0db4c131946912ee433ece15f5539d226a`,
`seeds.json` SHA256
`fedab3ec2eef18b21e04cc619188a7c60303476ca408c4bcdf583d75f0f31783`, and
`expected.json` SHA256
`5b61c45779e3f7dc417d5c6976fc1e4d8f9a6c2c204b9bac2e47edae9f5bed06`.

| Run | Exact argv | CWD and UTC | Exit and result | Output |
|---|---|---|---|---|
| Frozen analytic qualification | `python -m pytest tests/sampling/test_exchange_uncertainty.py::test_frozen_analytic_seed_design_qualifies_known_answer_and_covariance -m slow -q -s` | CWD `/workspace/AToM_MLMM-before-HPC`; original wrapper did not stamp start time; output-file completion timestamp `2026-10-07T12:35:26.413520Z` | Exit 0; 1 passed in 54.01 s; 0 skipped | `qualification-attempt1.log` |
| Final focused regression | `python -m pytest tests/sampling/test_exchange_uncertainty.py tests/unit/test_relative_binding_result.py tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_binding_result_admission.py tests/unit/test_restraint_volume.py -m 'not slow' -q` | CWD `/workspace/AToM_MLMM-before-HPC`; start `2026-10-07T12:38:47Z`; end `2026-10-07T12:39:19Z` | Exit 0; 43 passed, 1 deselected (the separately qualified slow test), 30.94 s | `final-focused-attempt1.log` |

The qualification ran against the frozen design and analyzer source recorded
at that revision: HEAD `911acc0909c7b43ac620b8bd5508f94f08f3f26b`, exchange
module SHA256 `11de3aadc537a72459b4e02c1baa58e94c9d83413628350a0a767d5ea2e3eaf6`,
and the schema/analysis/test tracked-diff SHA256
`65e970bbf18c3119a312dc15049a18f34d5a187bf2987dcb5bf6574a137fe456`. The
final focused run used the same analyzer/schema; subsequent additions were
the relative-ledger JSON fixture, its admission test, and handoff text. The
relative-result template test is included in the 43-pass final run.

Qualification results: both PyMBAR and UWHAM estimated `1.540292044537`
kJ/mol with standard error `0.024280745297`; absolute error from `+1.5` was
`0.040292044537` kJ/mol. Estimator difference was `5.33e-15` kJ/mol. The
block-bootstrap variance to independent-run mean variance ratio was
`0.9944036622` (frozen interval `[0.5, 2.0]`); the complete-run bootstrap
ratio was `0.8231580172`. Correlated lag-one and same-frame cross-walker
correlations were `0.4997224` and `0.5011213`; independent-baseline values
were `0.0041002` and `0.0039837`. State marginal checks, the reverse
`-1.5` answer, zero-restraint quadrature, and both-estimator agreement passed.
All control data are synthetic and do not show scheduler mixing, molecular
convergence, or G08 acceptance.

## Preserved earlier attempts

All exploratory stdout is kept verbatim under this evidence directory;
failures were not overwritten, including pytest's original whitespace in
traceback excerpts. Their original command wrappers did not persist argv, CWD,
or start timestamps, so those fields are marked unavailable here rather than
reconstructed. The listed UTC is each output file's filesystem completion
time, not a claimed command start time. These attempts used the worktree before
the final docs/template addition; the qualification run had its own frozen
source/design identity above.

| Output | Invocation metadata | UTC output time | Exit/result |
|---|---|---|---|
| `red-attempt1.log` | argv/CWD/start unavailable | 2026-10-07 12:22:44.432235Z | 2 expected failures |
| `red-attempt2.log` | argv/CWD/start unavailable | 2026-10-07 12:26:58.228744Z | 17 expected failures, 1 slow test deselected |
| `focused-attempt1.log` | argv/CWD/start unavailable | 2026-10-07 12:29:47.983790Z | 16 passed, 1 failed, 1 deselected; fixture sign oracle corrected |
| `focused-attempt2.log` | argv/CWD/start unavailable | 2026-10-07 12:30:48.356873Z | collection syntax error preserved; then corrected |
| `focused-fixcheck-attempt1.log` | argv/CWD/start unavailable | 2026-10-07 12:30:02.640054Z | 17 passed, 1 deselected |
| `focused-fixcheck-attempt2.log` | argv/CWD/start unavailable | 2026-10-07 12:30:59.901079Z | 19 passed, 1 deselected |
| `focused-attempt3.log` | argv/CWD/start unavailable | 2026-10-07 12:32:07.226284Z | 19 passed, 1 deselected |
| `affected-attempt1.log` | argv/CWD/start unavailable | 2026-10-07 12:32:39.338859Z | 21 passed in 28.33 s |
| `focused-attempt4.log` | argv/CWD/start unavailable | 2026-10-07 12:33:35.671682Z | 19 passed, 1 deselected |
| `focused-attempt5.log` | argv/CWD/start unavailable | 2026-10-07 12:34:19.184398Z | 19 passed, 1 deselected |
| `template-generation-attempt1.log` | argv/CWD/start unavailable | 2026-10-07 12:36:44.473297Z | Exit 0; serialized six `required_uncomputed` corrections as schema 1.0 |

The final tested file identities were:

```text
src/atm_mlmm/analysis.py                        c1200815962d5459fdd2b22f24385ca119b2fef46714423740b4d3e863a22950
src/atm_mlmm/schema.py                          51054783c9690a328283b87f991b3a98f9a40d36e3859e00111587eef719a887
src/atm_mlmm/exchange_analysis.py               11de3aadc537a72459b4e02c1baa58e94c9d83413628350a0a767d5ea2e3eaf6
tests/sampling/test_exchange_uncertainty.py     4f43a3c5ed7a8ff9d8c288dfb314085270bb143cd50caeeb80b4b6d69555b291
tests/unit/test_relative_binding_result.py      25b5f6d9ce201b4f7dbdbb8d252e342c4ee64afe44b09de9fe3f8140a17b36f2
relative-binding-template.json                 c27cde19382bf0c0088ae5974636d00c9d98ba06bb802682b8f567d4c382a838
README.md                                       34115170acd678b342f7232902626230d5f20c4a40558b1745c9b88ca41c0d37
```
