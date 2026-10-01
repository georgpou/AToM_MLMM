#!/usr/bin/env bash
set -euo pipefail
atom_mlmm_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
atom_mlmm_install_root="${ATOM_MLMM_SETUP_ROOT:-/workspace/.onboarding/atom-mlmm}"
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]]
mkdir -p "${atom_mlmm_install_root}/bootstrap" "${atom_mlmm_install_root}/cache"
if [[ "${atom_mlmm_script_dir}" != "${atom_mlmm_install_root}" ]]; then
    for atom_mlmm_file in core-conda-linux-64.lock amber-conda-linux-64.lock pip-wheels.lock wheels.sha256 constraints.txt activate.sh activate-amber.sh smoke_cpu.py smoke_prep.py; do
        cp "${atom_mlmm_script_dir}/${atom_mlmm_file}" "${atom_mlmm_install_root}/${atom_mlmm_file}"
    done
    cp -a "${atom_mlmm_script_dir}/wheels" "${atom_mlmm_install_root}/"
fi
if [[ ! -x "${atom_mlmm_install_root}/conda/bin/conda" ]]; then
    atom_mlmm_installer="${atom_mlmm_install_root}/bootstrap/Miniforge3-26.7.2-0-Linux-x86_64.sh"
    curl -fL https://github.com/conda-forge/miniforge/releases/download/26.7.2-0/Miniforge3-26.7.2-0-Linux-x86_64.sh -o "${atom_mlmm_installer}"
    printf '%s  %s\n' 281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05 "${atom_mlmm_installer}" | sha256sum -c -
    bash "${atom_mlmm_installer}" -b -u -p "${atom_mlmm_install_root}/conda"
fi
export CONDA_PKGS_DIRS="${atom_mlmm_install_root}/mamba/pkgs"
export MAMBA_ROOT_PREFIX="${atom_mlmm_install_root}/mamba"
export XDG_CACHE_HOME="${atom_mlmm_install_root}/cache"
export PIP_CACHE_DIR="${atom_mlmm_install_root}/cache/pip"
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
for atom_mlmm_pair in 'env core-conda-linux-64.lock' 'amber-env amber-conda-linux-64.lock'; do
    read -r atom_mlmm_prefix_name atom_mlmm_lock_name <<< "${atom_mlmm_pair}"
    atom_mlmm_operation=create
    [[ ! -x "${atom_mlmm_install_root}/${atom_mlmm_prefix_name}/bin/python" ]] || atom_mlmm_operation=install
    "${atom_mlmm_install_root}/conda/bin/mamba" --no-rc "${atom_mlmm_operation}" --yes \
        --prefix "${atom_mlmm_install_root}/${atom_mlmm_prefix_name}" \
        --file "${atom_mlmm_install_root}/${atom_mlmm_lock_name}"
done
(cd "${atom_mlmm_install_root}" && sha256sum -c wheels.sha256)
"${atom_mlmm_install_root}/env/bin/python" -m pip install --no-index \
    --find-links "${atom_mlmm_install_root}/wheels" --require-hashes \
    -c "${atom_mlmm_install_root}/constraints.txt" -r "${atom_mlmm_install_root}/pip-wheels.lock"
source "${atom_mlmm_install_root}/activate.sh"
python -m pip check
"${atom_mlmm_install_root}/amber-env/bin/python" -m pip check
python -m openmm.testInstallation
