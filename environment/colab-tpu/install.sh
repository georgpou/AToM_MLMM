#!/usr/bin/env bash
set -euo pipefail
cpu_root=${1:?usage: install.sh CPU_SETUP_ROOT UNUSED_TPU_PREFIX}
tpu_prefix=${2:?usage: install.sh CPU_SETUP_ROOT UNUSED_TPU_PREFIX}
script_dir=$(cd "$(dirname "$0")" && pwd)
if [[ -e "$tpu_prefix" ]]; then echo 'TPU prefix must be unused' >&2; exit 2; fi
"$cpu_root/conda/bin/conda" create --offline --yes --prefix "$tpu_prefix" --clone "$cpu_root/env"
"$tpu_prefix/bin/python" -m pip install --no-deps --require-hashes --only-binary=:all: -r "$script_dir/requirements.lock"
"$tpu_prefix/bin/python" -m pip check
"$tpu_prefix/bin/python" -m pip freeze > "$tpu_prefix/experimental-inventory.txt"
