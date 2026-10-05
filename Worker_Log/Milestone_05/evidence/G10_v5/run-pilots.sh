#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AToM_MLMM-g10
source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2
export PYTHONPATH="$PWD/src"
export G10_PILOT_EVIDENCE=/workspace/G10_v5_artifacts
if [[ -z "${G10_PILOT_RUN_ID:-}" ]]; then
    G10_PILOT_RUN_ID="manual-$(date -u +%Y%m%dT%H%M%SZ)"
    export G10_PILOT_RUN_ID
fi

python -m pytest tests/workflow/test_multistate_exchange_pilots.py -q
