#!/bin/bash
#SBATCH -J ligands_prep
#SBATCH -A LU2025-2-123
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -t 01:00:00

set -euo pipefail

# =============================================================================
# ENVIRONMENT
# =============================================================================

source /sw/easybuild_milan/software/Anaconda3/2024.06-1/etc/profile.d/conda.sh
conda activate atm_aceff


# =============================================================================
# SETTINGS
# =============================================================================

PYTHON_SCRIPT="parameterize_ligands_ATM.py"

LIGANDS=(
    L1A
    L1G
    L1H
    L2A
    L2C
    L2D
)

declare -A CHARGES=(
    [L1A]=1
    [L1G]=1
    [L1H]=1
    [L2A]=1
    [L2C]=1
    [L2D]=1
)


# =============================================================================
# PARAMETERIZE ALL LIGANDS
# =============================================================================

echo "Starting ligand parameterization"
echo "============================================================"

for ligand in "${LIGANDS[@]}"; do

    input_file="${ligand}.mol2"
    net_charge="${CHARGES[$ligand]}"

    echo
    echo "============================================================"
    echo "Parameterizing: ${input_file}"
    echo "Net charge:     ${net_charge}"
    echo "============================================================"

    if [[ ! -f "${input_file}" ]]; then
        echo "ERROR: ${input_file} does not exist."
        exit 1
    fi

    # Temporary copy of the Python parameterization script.
    tmp_script="parameterize_${ligand}_tmp.py"

    # Replace:
    #   INPUT_FILE = Path(...)
    #   NET_CHARGE = ...
    #
    # Everything else in the Python script remains unchanged.
    sed \
        -e "s|^INPUT_FILE = Path(\".*\")|INPUT_FILE = Path(\"${input_file}\")|" \
        -e "s|^NET_CHARGE = .*|NET_CHARGE = ${net_charge}|" \
        "${PYTHON_SCRIPT}" > "${tmp_script}"

    python "${tmp_script}"

    rm -f "${tmp_script}"

    echo "Finished: ${input_file}"

done


echo
echo "============================================================"
echo "All ligand parameterizations finished successfully."
echo "============================================================"
