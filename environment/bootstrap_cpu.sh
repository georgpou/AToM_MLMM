#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [[ "$(git branch --show-current)" == main ]]; then
    printf '%s\n' 'Switch to M00 or another work branch before environment setup.' >&2
    exit 1
fi
output="${1:-artifacts/g00-cpu}"
if [[ -e "$output" ]]; then
    printf '%s\n' 'Evidence path already exists; use a fresh attempt directory.' >&2
    exit 1
fi
if micromamba env list --json | python3 -c 'import json,sys; sys.exit(0 if any(p.endswith("/atm-mlmm-p0") for p in json.load(sys.stdin)["envs"]) else 1)'; then
    printf '%s\n' 'CPU prefix already exists; create a fresh workspace rather than updating it.' >&2
    exit 1
fi
mkdir -p "$output"
set +e
micromamba create -y -f ATM_MLMM_environment.yml 2>&1 | tee "$output/solver.log"
result=${PIPESTATUS[0]}
set -e
printf '%s\n' "$result" > "$output/solver.exit"
if [[ "$result" != 0 ]]; then exit "$result"; fi
micromamba run -n atm-mlmm-p0 bash environment/qualify_cpu.sh "$output"
