#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/settings.sh"
if [[ ! -x "${ATOM_MLMM_SETUP_ROOT}/conda/bin/conda" ]]; then
    # The site's Conda 24 client can bootstrap Conda 26 but cannot read the
    # scientific SHA-256 URL locks. Disable its global registry before use.
    /sw/easybuild_milan/software/Anaconda3/2024.06-1/bin/conda --no-plugins create \
        --yes --quiet --solver classic --no-default-packages \
        --override-channels --channel conda-forge \
        --prefix "${ATOM_MLMM_SETUP_ROOT}/conda" python=3.12 conda=26.7.2
fi
"${ATOM_MLMM_SETUP_ROOT}/conda/bin/conda" list --prefix "${ATOM_MLMM_SETUP_ROOT}/conda" --explicit --sha256 \
    > "${ATOM_MLMM_SETUP_ROOT}/logs/bootstrap-conda-explicit.lock"
bash "${ATOM_MLMM_REPOSITORY}/environment/cloud-cpu/install.sh"
