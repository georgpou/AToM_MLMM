#!/bin/bash
#SBATCH --job-name=atm-env-install
#SBATCH --account=LU2025-2-123
#SBATCH --partition=lu48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=01:00:00
#SBATCH --output=.runtime/cosmos-cpu/logs/install-%j.out
#SBATCH --error=.runtime/cosmos-cpu/logs/install-%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the repository root}"
source environment/hpc/cosmos/settings.sh
trap 'atom_mlmm_code=$?; printf "%s\n" "$atom_mlmm_code" > "${ATOM_MLMM_SETUP_ROOT}/logs/install-${SLURM_JOB_ID}.exit"; exit "$atom_mlmm_code"' EXIT
bash environment/hpc/cosmos/install.sh
source environment/hpc/cosmos/activate.sh
# The installer records all nine checks; require documentation as well.
python - <<'PYCODE'
import json, os
from pathlib import Path
p=Path(os.environ['ATOM_MLMM_SETUP_ROOT'])/'latest-validation.json'
r=json.loads(p.read_text())
assert r['environment_ok'] and r['documentation_ok'], str(p)
print('All nine installation checks passed.')
PYCODE
python -m pytest -m "not gpu and not model_assets and not slow" -q \
    --basetemp="${TMPDIR}/pytest-${SLURM_JOB_ID}" \
    > "${ATOM_MLMM_SETUP_ROOT}/logs/pytest-${SLURM_JOB_ID}.log" 2>&1
