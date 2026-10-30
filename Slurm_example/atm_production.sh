#!/bin/bash
#SBATCH -A LU2025-2-123
#SBATCH -p gpua100i
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH -t 1-00:00:00
#SBATCH -J atm_aceff2_prod
#SBATCH -o production_%j.out
#SBATCH -e production_%j.err
#SBATCH --mail-user=georgios.poulos@chem.lu.se
#SBATCH --mail-type=FAIL

set -euo pipefail

echo "===== ATM PRODUCTION JOB STARTED ====="
date
hostname
pwd

echo
echo "===== LOAD ENVIRONMENT ====="
module purge

# Activate the conda environment.
source /sw/easybuild_milan/software/Anaconda3/2024.06-1/etc/profile.d/conda.sh
conda activate atm_aceff

# Force OpenMM to use the CUDA-12 plugin bundled with the pip OpenMM install.
# This avoids the CUDA 13.3 plugin that causes CUDA_ERROR_UNSUPPORTED_PTX_VERSION.
export OPENMM_PLUGIN_DIR="$CONDA_PREFIX/lib/python3.10/site-packages/OpenMM.libs/lib/plugins"

# Make the conda environment libraries visible to dynamically loaded plugins.
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"

echo
echo "CONDA_PREFIX=$CONDA_PREFIX"
echo "OPENMM_PLUGIN_DIR=$OPENMM_PLUGIN_DIR"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"

echo
echo "===== GPU CHECK ====="
nvidia-smi

echo
echo "===== PYTHON / OPENMM CHECK ====="
python - <<'PY'
import sys
print("Python:", sys.executable)

import openmm
print("OpenMM:", openmm.version.version)

from openmm import Platform
for i in range(Platform.getNumPlatforms()):
    p = Platform.getPlatform(i)
    print("Platform", i, p.getName())

import torch
print("Torch:", torch.__version__)
print("Torch CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Torch CUDA device:", torch.cuda.get_device_name(0))
PY

echo
echo "===== RUN rbfe_production ====="
python - <<'PY'
from htmd.ui import *
from atm.rbfe_production import rbfe_production

config_file = "BEN_to_TOL_config.yaml"

print("Running rbfe_production on:", config_file)
rbfe_production(config_file)
print("rbfe_production completed.")
PY

echo
echo "===== OUTPUT FILES AFTER PRODUCTION ====="
find . -maxdepth 2 -type f | sort

echo
echo "===== ATM PRODUCTION JOB FINISHED ====="
date
