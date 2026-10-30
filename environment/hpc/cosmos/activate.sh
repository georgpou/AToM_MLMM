# Source this from Bash in any directory; no shell startup files are changed.
source "$(dirname -- "${BASH_SOURCE[0]}")/settings.sh" || return 1
source "${ATOM_MLMM_SETUP_ROOT}/activate.sh" || return 1
