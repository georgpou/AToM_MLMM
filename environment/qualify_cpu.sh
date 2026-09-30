#!/usr/bin/env bash
# Run after a clean creation of ATM_MLMM_environment.yml; never change its pins.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
output="${1:-artifacts/g00-cpu}"
mkdir -p "$output"
output="$(cd "$output" && pwd)"
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export ATM_MLMM_MANIFEST="$output/environment-manifest.json"
export OPENMM_CPU_THREADS=2 OMP_NUM_THREADS=2

record() {
    local name="$1"
    shift
    set +e
    "$@" 2>&1 | tee "$output/$name.log"
    local result=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$result" > "$output/$name.exit"
    return "$result"
}

# Always preserve partial evidence when a check fails.
trap 'python tools/capture_environment.py "$output"' EXIT
record project_install python -m pip install --no-deps -e .
micromamba list -n atm-mlmm-p0 --json > "$output/conda-packages.json"
micromamba list -n atm-mlmm-p0 --explicit > "$output/conda-explicit.txt"
micromamba env export -n atm-mlmm-p0 > "$output/environment-resolved.yml"
python -m pip freeze --all > "$output/pip-freeze-initial.txt"
record archive_pip python tools/archive_pip.py "$output"
record pip_check python -m pip check
record openmm_installation python -m openmm.testInstallation
record api_check python -c 'import json; from atm_mlmm.persistence import check_required_apis; print(json.dumps(check_required_apis(), indent=2))'
python tools/capture_environment.py "$output"
record pytest python -m pytest -v --junitxml="$output/pytest.xml"
python -m pip freeze --all > "$output/pip-freeze.txt"
