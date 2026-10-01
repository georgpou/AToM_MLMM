#!/usr/bin/env bash
set -euo pipefail
atom_mlmm_probe_root=/workspace/.onboarding/atom-mlmm-independent-audit-v1b
atom_mlmm_probe() {
    python - "$atom_mlmm_probe_root" "$1" <<'PY'
import json, os, shutil, sys
from pathlib import Path
import numpy
root, stage = Path(sys.argv[1]), sys.argv[2]
selected = root / ('amber-env' if stage == 'amber' else 'env')
commands = {name: shutil.which(name) for name in ['python','antechamber','parmchk2','tleap','sqm']}
assert Path(sys.executable) == selected/'bin/python', commands
assert numpy.__version__ == ('1.26.4' if stage == 'amber' else '2.4.6')
assert os.environ['AMBERHOME'] == str(root/'amber-env')
for name in ['antechamber','parmchk2','tleap','sqm']:
    assert commands[name] == str(root/'amber-env/bin'/name), commands
assert os.environ.get('PIP_CONSTRAINT') == (None if stage=='amber' else str(root/'constraints.txt'))
print(json.dumps(dict(stage=stage, interpreter=sys.executable, numpy=numpy.__version__, AMBERHOME=os.environ['AMBERHOME'],
                     commands=commands, PIP_CONSTRAINT=os.environ.get('PIP_CONSTRAINT'),
                     threads={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENMM_CPU_THREADS']})))
PY
}
source "$atom_mlmm_probe_root/activate.sh"
atom_mlmm_probe main_first
source "$atom_mlmm_probe_root/activate-amber.sh"
atom_mlmm_probe amber
source "$atom_mlmm_probe_root/activate.sh"
atom_mlmm_probe main_return
