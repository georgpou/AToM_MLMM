"""Reproduce the frozen M05 local-water controls without overwriting inputs."""
from pathlib import Path
import sys

from atm_mlmm.solvent import build_dense_control

if __name__=='__main__':
    destination=Path(sys.argv[1])
    for kind in ('abfe','rbfe'):
        build_dense_control(kind,destination/kind)
