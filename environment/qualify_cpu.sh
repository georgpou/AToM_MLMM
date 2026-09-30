#!/usr/bin/env bash
# Run after a clean creation of ATM_MLMM_environment.yml; never change its pins.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
output="${1:-artifacts/g00-cpu}"
mkdir -p "$output"
output="$(cd "$output" && pwd)"
if [[ ! -f "$output/solver.exit" || -f "$output/project_install.exit" ]]; then
    printf '%s\n' 'Qualification requires a fresh successful solve attempt.' >&2
    exit 1
fi
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
record conda_integrity python -c 'import json,sys; from pathlib import Path; from atm_mlmm.persistence import verify_conda_files; print(json.dumps(verify_conda_files(Path(sys.prefix)), indent=2))'
record conda_packages micromamba list -n atm-mlmm-p0 --json
cp "$output/conda_packages.log" "$output/conda-packages.json"
record conda_explicit micromamba list -n atm-mlmm-p0 --explicit
cp "$output/conda_explicit.log" "$output/conda-explicit.txt"
record environment_export micromamba env export -n atm-mlmm-p0
cp "$output/environment_export.log" "$output/environment-resolved.yml"
python -m pip freeze --all > "$output/pip-freeze-initial.txt"
record archive_pip python tools/archive_pip.py "$output"
record pip_check python -m pip check
record openmm_installation python -m openmm.testInstallation
record api_check python -c 'import json; from atm_mlmm.persistence import check_required_apis; print(json.dumps(check_required_apis(), indent=2))'
python tools/capture_environment.py "$output"
record pytest python -m pytest -v --junitxml="$output/pytest.xml"
python -m pip freeze --all > "$output/pip-freeze.txt"
