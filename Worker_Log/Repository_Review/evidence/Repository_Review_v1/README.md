# Repository Review v1 evidence index

[Main plain-language report](../../Repository_Review_v1_audit.md), [coverage/claim matrix](coverage.md), [equations and traces](scientific-trace.md), [confirmed findings](findings.md), [dependency backlog](backlog.md). One root reviewer, gpt-6.1-sol/max as confirmed by the user, no agents or repairs.

## Frozen identities and reuse

- [snapshot.json](snapshot.json): actual published HEAD/initial clean status, unused child report branch, reviewer setting provenance and environment availability.
- [frozen-input-sha256.json](frozen-input-sha256.json): 474 tracked source/test/input/model/environment/spec/gate hashes captured before probes. Ancillary script hashes are additionally in the inventory/component records.
- [reuse-verification.json](reuse-verification.json): 105/105 v8 source/test hashes match, complete 38-module source set matches, no anchor/latest-engine scientific diff. Anchor-to-HEAD contains only two handoff documents.
- [component-reuse.json](component-reuse.json): scientific lineage, each module's old/current byte comparison, five exact accepted quantum-tool/test comparisons, upstream pins, model/license/lock identities and scope-specific reused audits. Only exchange.py/exchange_journal.py differ from retained scientific source; every source module matches the exact final v8 review.
- [inventory.json](inventory.json): 38 source modules/6716 lines, 67 files under tests, 59 test-bearing files, 305 named test functions before parameter expansion; all 14 gates' planned nodes, 13 fixture-family/version groups and 17 ancillary Python programs. Planned-node presence is not a pass result.
- [physical-evidence.json](physical-evidence.json): all 46 accepted reference hashes match, unchanged model/reference trees, exact sensitivity/pilot/budget/progress identities. No reference was generated or changed.
- [retained-log-identities.json](retained-log-identities.json): raw SHA-256 and byte-exact gzip verification for v8 full suite, focused worker repair, tiny pilots and original clock RED. Canonical audit/evidence identities are also recorded in `provenance.json`.

Reused worker full suite: `python -m pytest -q`, 631 passed, zero skips, 1238.59 s. Raw log SHA-256 `55747b697c1fae7558058c2d2938dd717b49fd2dc57b6bd5c2f7f8f7f54dfd14`. Reused final independent checks: 8 passed/0 skipped/57 deselected, 4.26 s, plus four Decimal120 arithmetic controls. Reused v8 worker focused checks: seven passes; two fresh 64-water pilots. These are prior results; the present review did not rerun those campaigns. Exact matching source/profile is the basis for reuse.

Old local G10 artifact roots and `/workspace/m05-cpu-setup-v2` were absent. Written prior verification of 958 pilot files/eight bundles is reused; those original local trees were not rehashed again here. No attempt was resumed under another checkout. The new diagnostics used only fresh preparations/current source and a unique `restart-attempt-001`.

## Replacement environment

Unchanged `environment/cloud-cpu/install.sh` and locks built `/workspace/repository-review-cpu-v3`. [environment/validation-results.json](environment/validation-results.json) records 9/9 successful setup checks, Python 3.11.16, 156 exact main distributions/255 Conda artifacts and 80 Amber distributions/201 Conda artifacts. Main NumPy 2.4.6 and separate Amber NumPy 1.26.4 are retained; model torch/MACE/OpenMM/AToM pins are unchanged. Setup smoke checks are not scientific gate acceptance or trained-model physical evidence.

Installer command used `ATOM_MLMM_SETUP_ROOT=/workspace/repository-review-cpu-v3 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 bash environment/cloud-cpu/install.sh`; final exit 0. The [v3 installer log](environment/repository-review-cpu-install-v3.log) and validation timestamps/commands are retained. Three earlier failed invocations (initial v1, partial-prefix replay and v2) stopped on bootstrap/standard Conda-directory availability and are preserved in the other installer logs. Creating the standard `/home/agent/.conda` directory was approved by the tool approval review; no review action was rejected. Partial prefixes remain outside the source tree. No scientific test ran in those failed installations. Setup provenance is expanded in `provenance.json`.

## Preselected fresh checks, serial execution

[probe-plan.md](probe-plan.md) was saved before numerical execution. Every scientific command activated the v3 prefix and used:

```bash
source /workspace/repository-review-cpu-v3/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"
```

The first receipt's optional `environment_prefix` variable is null because activation does not export that variable; its Python executable unambiguously points to v3. Later receipts explicitly export it. All commands ran from `/workspace/AToM_MLMM-g10`, source HEAD `4ad8ee835809325ceec8a017222415043347967d`. Jobs were serial; measured check memory stayed below 8 GiB.

| Receipt / raw log | Actual UTC interval and outcome | What it proves |
|---|---|---|
| [selected-analytic.json](selected-analytic.json) / [log](selected-analytic.log) | 09:14:19.727–09:14:37.487 UTC, 2026-10-07; exit 0; **31 passed, 0 skips, 16.80 s pytest**; peak child RSS 637210624 bytes. | Independent nonlinear/cap force sweeps, Gaussian estimator/covariance/offset controls, finite-wall quadrature/sign/withholding/joint covariance, actual pair acceptance; plus a labeled reconstruction parity check. Exact nine requested test nodes/parameter cases are in the receipt. |
| [restart-diagnostics.json](restart-diagnostics.json) / [log](restart-diagnostics.log) | 09:15:29.733–09:15:29.978 UTC; exit 1. | Import-path setup failure before any preparation or diagnostic. Preserved; not a source/numerical defect. |
| [restart-diagnostics-invocation.json](restart-diagnostics-invocation.json) / [log](restart-diagnostics-invocation.log) | 09:15:47.035–09:15:49.764 UTC; exit 0; **four preselected cases reproduced**, peak child RSS 142700544 bytes. | RR-01 on two older APIs, RR-02 geometry-before-step ordering and RR-03 source-inventory admission. Invocation alone changed; script and reviewed code did not. |
| [independent-arithmetic.json](independent-arithmetic.json) / [log](independent-arithmetic.log) | 09:21:54.034–09:21:54.088 UTC; exit 0; peak child RSS 45826048 bytes. | Exact-SI beta/sign arithmetic and 1.5 kJ/mol Gaussian completion-of-square answer. Frozen ASE conversion is separately explained; no unit/tolerance change. |

[run_command.py](run_command.py) records argv/cwd/UTC/source/profile/exits/raw hashes/resource observations; [arithmetic_control.py](arithmetic_control.py) and [results](arithmetic-results.json) give independent formulas. [reproduce_restart.py](reproduce_restart.py) and [restart-results.json](restart-results.json) describe the minimal checkpoints/sentinels. Entire fresh attempts, original/altered checkpoint bytes, row/State/manifests, negative geometry and failure archives are preserved in `restart-attempt-001/`. A successful diagnostic exit means the requested proof completed, not that the affected source passed admission.

No full suite, molecular pilot, long MD, QM, GPU or cluster job was launched by this review. No deselected/empty/import-only outcome was counted as numerical evidence. Tests that only compare the producer to another path are marked parity, not independent mathematical proof.

## Completion

The only added repository paths are under `Worker_Log/Repository_Review/`. Source/tests/inputs/models/locks/contracts and historical reports are preserved. `documentation-final.json`/`.log`, `report-integrity.json`/`.log`, `completion.json` and `manifest.json` record the one final report-only documentation/whitespace/source-preservation checks and complete evidence identities. No repairs, repeated audit, changed threshold, merge, reset, rebase, push or new worker follows this pass.
