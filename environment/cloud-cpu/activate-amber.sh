atom_mlmm_setup_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${atom_mlmm_setup_root}/conda/etc/profile.d/conda.sh"
conda activate "${atom_mlmm_setup_root}/amber-env"
export AMBERHOME="${atom_mlmm_setup_root}/amber-env"
export PIP_CACHE_DIR="${atom_mlmm_setup_root}/cache/pip"
export OMP_NUM_THREADS=2
unset PIP_CONSTRAINT
