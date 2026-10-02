# Commands and actual outcomes

All repository reads use cwd `/workspace/AToM_MLMM-m00-review-v3`; only the authorized v3 audit/evidence paths in the implementing checkout are written.

1. Read `AGENTS.md`, `STATUS.md`, S01/S04/S06/S07, G05/G07, v3 plan/worker, v2 audit, exact settings/manifest, preparation/repair sources and prior independent audit scripts. Environment status was current/enforced; no network used.
2. `git rev-parse HEAD` → `a825f5f1c2d8cf4146133c2049ef1c4eca550e93`. `git status --porcelain=v1` → empty. `git symbolic-ref -q HEAD` → exit 1 as expected for detached HEAD.
3. `source /workspace/atom-mlmm-g05-v2/activate.sh`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v3/review.py`:
   - First attempt: reporting raised `TypeError` on NumPy int64; preserved in `review-initial-error.stdout`. The initial shell ended with `cat`, so its outer exit code 0 was not accepted as script success.
   - Second attempt after integer serialization correction: exit 1, 967/969 exploratory checks. Two additional isolated full-parent metadata screens were outside the declared ten-row G07 criterion. Script/result/stdout preserved with `exploratory-` prefix.
   - Final attempt with applicability corrected and diagnostics retained: **exit 0, 965/965**. No inputs, scientific limits or implementation changed. Regeneration target differs per attempt to preserve prior evidence.
4. Independent ad hoc NumPy distance inspection identified the flagged pairs as OH H p18–carbonyl O p9, and measured repaired former-clash pairs. Values are in the canonical audit and full row minima in `review-results.json`.
5. `source /workspace/atom-mlmm-g05-v2/activate.sh`; `PYTHONDONTWRITEBYTECODE=1 python /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v3/provenance_check.py` → **exit 0, 131/131**, zero target calculations. Reads actual separate quantum prefix package metadata and basis bytes without importing/calculating Psi4. Preserved prior independent exact-setting methane suffices.
6. Final frozen SHA and clean status rechecked in `evidence-manifest.json`.

To rerun `review.py`, select a new `repair.TARGET` subdirectory under this evidence directory; the preparation intentionally refuses overwriting a frozen bundle. Both scripts are self-contained aside from frozen source checks explicitly read from the reviewed commit and the named installed environments. No target quantum energies, gradients or model comparisons are accessed.
