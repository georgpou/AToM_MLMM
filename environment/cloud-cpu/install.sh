#!/usr/bin/env bash
# Reproduce the two-environment core-analytic-cpu development installation.
set -euo pipefail
atom_mlmm_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
atom_mlmm_repo="${ATOM_MLMM_REPOSITORY:-$(cd -- "${atom_mlmm_script_dir}/../.." && pwd)}"
atom_mlmm_install_root="${ATOM_MLMM_SETUP_ROOT:-/workspace/.onboarding/atom-mlmm}"
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo 'These artifact locks require Linux x86_64.' >&2
    exit 2
fi
for atom_mlmm_command in bash curl sha256sum tar; do
    command -v "${atom_mlmm_command}" >/dev/null
done
test -f "${atom_mlmm_repo}/tools/check_docs.py"
mkdir -p "${atom_mlmm_install_root}"
atom_mlmm_install_root="$(cd -- "${atom_mlmm_install_root}" && pwd)"
if [[ "${atom_mlmm_install_root}" == "${atom_mlmm_repo}" || "${atom_mlmm_install_root}" == "${atom_mlmm_script_dir}" ]]; then
    echo 'Choose an installation prefix outside the repository.' >&2
    exit 2
fi
mkdir -p "${atom_mlmm_install_root}/logs" "${atom_mlmm_install_root}/bootstrap" "${atom_mlmm_install_root}/cache"
atom_mlmm_run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
exec > >(tee "${atom_mlmm_install_root}/logs/install-${atom_mlmm_run_id}.log") 2>&1
trap 'atom_mlmm_exit=$?; printf "Installer exit code: %s\n" "${atom_mlmm_exit}"; exit "${atom_mlmm_exit}"' EXIT

# Fail before any installation if the branch's reusable artifacts are incomplete.
(cd "${atom_mlmm_script_dir}" && sha256sum -c bundle.sha256)
if [[ "${atom_mlmm_script_dir}" != "${atom_mlmm_install_root}" ]]; then
    cp "${atom_mlmm_script_dir}"/*.lock "${atom_mlmm_script_dir}"/*.txt \
        "${atom_mlmm_script_dir}"/*.json "${atom_mlmm_script_dir}"/*.sh \
        "${atom_mlmm_script_dir}"/*.py "${atom_mlmm_script_dir}"/*.sha256 \
        "${atom_mlmm_script_dir}/README.md" "${atom_mlmm_install_root}/"
    cp -a "${atom_mlmm_script_dir}/wheels" "${atom_mlmm_install_root}/"
    mkdir -p "${atom_mlmm_install_root}/sources"
    cp "${atom_mlmm_script_dir}/sources/"*.tar.gz "${atom_mlmm_install_root}/sources/"
fi
export CONDA_PKGS_DIRS="${atom_mlmm_install_root}/mamba/pkgs"
export MAMBA_ROOT_PREFIX="${atom_mlmm_install_root}/mamba"
export XDG_CACHE_HOME="${atom_mlmm_install_root}/cache"
export PIP_CACHE_DIR="${atom_mlmm_install_root}/cache/pip"
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
test -r "${SSL_CERT_FILE}"

if [[ ! -x "${atom_mlmm_install_root}/conda/bin/conda" ]]; then
    atom_mlmm_installer="${atom_mlmm_install_root}/bootstrap/Miniforge3-26.7.2-0-Linux-x86_64.sh"
    curl --fail --location --retry 3 \
        https://github.com/conda-forge/miniforge/releases/download/26.7.2-0/Miniforge3-26.7.2-0-Linux-x86_64.sh \
        --output "${atom_mlmm_installer}"
    printf '%s  %s\n' 281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05 "${atom_mlmm_installer}" | sha256sum -c -
    bash "${atom_mlmm_installer}" -b -p "${atom_mlmm_install_root}/conda"
fi

# Explicit SHA-256 URL locks: no solver, channel substitution or version fallback.
for atom_mlmm_pair in 'env core-conda-linux-64.lock' 'amber-env amber-conda-linux-64.lock'; do
    read -r atom_mlmm_prefix_name atom_mlmm_lock_name <<< "${atom_mlmm_pair}"
    atom_mlmm_operation=create
    [[ ! -x "${atom_mlmm_install_root}/${atom_mlmm_prefix_name}/bin/python" ]] || atom_mlmm_operation=install
    "${atom_mlmm_install_root}/conda/bin/mamba" --no-rc "${atom_mlmm_operation}" --yes --quiet \
        --ssl-verify "${SSL_CERT_FILE}" \
        --prefix "${atom_mlmm_install_root}/${atom_mlmm_prefix_name}" \
        --file "${atom_mlmm_install_root}/${atom_mlmm_lock_name}"
done
(cd "${atom_mlmm_install_root}" && sha256sum -c wheels.sha256)
"${atom_mlmm_install_root}/env/bin/python" -m pip install --no-index \
    --find-links "${atom_mlmm_install_root}/wheels" --require-hashes \
    -c "${atom_mlmm_install_root}/constraints.txt" -r "${atom_mlmm_install_root}/pip-wheels.lock"

# Full pinned sources, including AToM's regression inputs, are supplied by Git.
"${atom_mlmm_install_root}/env/bin/python" - "${atom_mlmm_install_root}" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
root = Path(sys.argv[1])
for source in json.loads((root / 'upstream-sources.json').read_text()):
    target = root / 'sources' / source['directory']
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(['tar', '-xzf', str(root / source['archive']),
                    '-C', str(target)], check=True)
PY
source "${atom_mlmm_install_root}/activate.sh"
python "${atom_mlmm_install_root}/validate.py" --root "${atom_mlmm_install_root}" --repository "${atom_mlmm_repo}" --environment-only
echo "Activate ML/MM: source ${atom_mlmm_install_root}/activate.sh"
echo "Activate AmberTools Python: source ${atom_mlmm_install_root}/activate-amber.sh"
