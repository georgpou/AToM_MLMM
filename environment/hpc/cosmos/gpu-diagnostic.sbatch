#!/bin/bash
#SBATCH --job-name=atm-gpu-diagnostic
#SBATCH --account=LU2025-2-123
#SBATCH --partition=gpua100i
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:05:00
#SBATCH --output=.runtime/cosmos-cpu/logs/gpu-diagnostic-%j.out
#SBATCH --error=.runtime/cosmos-cpu/logs/gpu-diagnostic-%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the repository root}"
source environment/hpc/cosmos/activate.sh
nvidia-smi
python - <<'PYCODE'
import openmm, torch
print('OpenMM:', openmm.__version__)
print('Platforms:', [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])
print('Plugin failures:', openmm.Platform.getPluginLoadFailures())
print('PyTorch:', torch.__version__, 'CUDA build:', torch.version.cuda, 'CUDA available:', torch.cuda.is_available())
print('Diagnostics only: the pinned PyTorch and current MACE callback are CPU-only.')
PYCODE
