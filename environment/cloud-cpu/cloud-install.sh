#!/usr/bin/env bash
# Cloud configuration entrypoint. Even a checkout initially on main can obtain
# setup artifacts without changing main or relying on a prepared filesystem.
set -euo pipefail
atom_mlmm_repository="${ATOM_MLMM_REPOSITORY:-/workspace/AToM_MLMM}"
cd "${atom_mlmm_repository}"
export ATOM_MLMM_REPOSITORY="${PWD}"
if [[ -f environment/cloud-cpu/install.sh ]]; then
    bash environment/cloud-cpu/install.sh
else
    git fetch origin m01-g00-cloud-environment-setup
    atom_mlmm_transfer_dir="$(mktemp -d /tmp/atom-mlmm-branch-setup.XXXXXX)"
    git archive FETCH_HEAD environment/cloud-cpu | tar -x -C "${atom_mlmm_transfer_dir}"
    bash "${atom_mlmm_transfer_dir}/environment/cloud-cpu/install.sh"
fi
