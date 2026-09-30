#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [[ "$(git branch --show-current)" == main ]]; then
    printf '%s\n' 'Switch to M00 or another work branch before environment setup.' >&2
    exit 1
fi
mkdir -p artifacts/g00-cpu
micromamba create -y -f ATM_MLMM_environment.yml 2>&1 | tee artifacts/g00-cpu/solver.log
micromamba run -n atm-mlmm-p0 bash environment/qualify_cpu.sh artifacts/g00-cpu
