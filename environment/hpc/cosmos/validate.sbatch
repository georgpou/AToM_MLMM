#!/bin/bash
#SBATCH --job-name=atm-env-validate
#SBATCH --account=LU2025-2-123
#SBATCH --partition=lu48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:30:00
#SBATCH --output=.runtime/cosmos-cpu/logs/validate-%j.out
#SBATCH --error=.runtime/cosmos-cpu/logs/validate-%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the repository root}"
source environment/hpc/cosmos/activate.sh
python "${ATOM_MLMM_SETUP_ROOT}/validate.py" --repository "$PWD"
python -m pytest -m "not gpu and not model_assets and not slow" -q \
    --basetemp="${TMPDIR}/pytest-${SLURM_JOB_ID}"
