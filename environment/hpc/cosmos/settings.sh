# Source from Bash; all mutable installation/runtime paths stay in this repo.
atom_mlmm_cosmos_repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export ATOM_MLMM_REPOSITORY="${atom_mlmm_cosmos_repo}"
export ATOM_MLMM_SETUP_ROOT="${atom_mlmm_cosmos_repo}/.runtime/cosmos-cpu"
export ATOM_MLMM_CA_BUNDLE="${ATOM_MLMM_CA_BUNDLE:-/etc/pki/tls/certs/ca-bundle.crt}"
test -r "${ATOM_MLMM_CA_BUNDLE}" || return 1
export SSL_CERT_FILE="${ATOM_MLMM_CA_BUNDLE}" REQUESTS_CA_BUNDLE="${ATOM_MLMM_CA_BUNDLE}"
export PIP_CERT="${ATOM_MLMM_CA_BUNDLE}" GIT_SSL_CAINFO="${ATOM_MLMM_CA_BUNDLE}"
export ATOM_MLMM_PACKAGE_MANAGER=conda
export CONDA_REGISTER_ENVS=false
export CONDA_NOTIFY_OUTDATED_CONDA=false
export CONDA_NUMBER_CHANNEL_NOTICES=0
export CONDA_ENVS_PATH="${ATOM_MLMM_SETUP_ROOT}/named-envs"
export CONDA_PKGS_DIRS="${ATOM_MLMM_SETUP_ROOT}/mamba/pkgs"
export MAMBA_ROOT_PREFIX="${ATOM_MLMM_SETUP_ROOT}/mamba"
export XDG_CACHE_HOME="${ATOM_MLMM_SETUP_ROOT}/cache"
export XDG_CONFIG_HOME="${ATOM_MLMM_SETUP_ROOT}/config"
export XDG_DATA_HOME="${ATOM_MLMM_SETUP_ROOT}/data"
export PIP_CACHE_DIR="${XDG_CACHE_HOME}/pip"
export MPLCONFIGDIR="${XDG_CACHE_HOME}/matplotlib"
export HF_HOME="${XDG_CACHE_HOME}/huggingface"
export TORCH_HOME="${XDG_CACHE_HOME}/torch"
export NUMBA_CACHE_DIR="${XDG_CACHE_HOME}/numba"
export CUDA_CACHE_PATH="${XDG_CACHE_HOME}/cuda"
# AF_UNIX endpoints add a suffix; keep this repo-local path short.
export TMPDIR="${atom_mlmm_cosmos_repo}/.tmp"
export TMP="${TMPDIR}" TEMP="${TMPDIR}"
mkdir -p "${TMPDIR}" "${XDG_CACHE_HOME}" "${XDG_CONFIG_HOME}" "${XDG_DATA_HOME}" "${ATOM_MLMM_SETUP_ROOT}/logs"
export PYTHONNOUSERSITE=1
export PYTHONPATH="${atom_mlmm_cosmos_repo}/src"
export OPENBLAS_NUM_THREADS=2
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENMM_CPU_THREADS=2
