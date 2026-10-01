# Source this file from Bash to activate the CPU development environment.
atom_mlmm_setup_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${atom_mlmm_setup_root}/conda/etc/profile.d/conda.sh"
conda activate "${atom_mlmm_setup_root}/env"
export CONDA_PKGS_DIRS="${atom_mlmm_setup_root}/mamba/pkgs"
export XDG_CACHE_HOME="${atom_mlmm_setup_root}/cache"
export PIP_CACHE_DIR="${atom_mlmm_setup_root}/cache/pip"
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export OPENMM_CPU_THREADS=2
export AMBERHOME="${atom_mlmm_setup_root}/amber-env"
case ":${PATH}:" in
    *":${atom_mlmm_setup_root}/amber-env/bin:"*) ;;
    *) export PATH="${PATH}:${atom_mlmm_setup_root}/amber-env/bin" ;;
esac
export MPLCONFIGDIR="${atom_mlmm_setup_root}/cache/matplotlib"
export PIP_CONSTRAINT="${atom_mlmm_setup_root}/constraints.txt"
# Keep PyTorch's safe default loading policy; no global unsafe-load override.
unset TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD
