"""Exercise the real CPU smoke and its process-wide loading-policy boundary."""
import os
from pathlib import Path
import subprocess
import sys


def test_cpu_smoke_preserves_safe_loading():
    smoke = Path(__file__).resolve().parents[2] / "environment/cloud-cpu/smoke_cpu.py"
    probe = """
import os
import runpy
import sys
import torch

before_slice = slice in torch.serialization.get_safe_globals()
runpy.run_path(sys.argv[1], run_name="__main__")
assert "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD" not in os.environ, (
    "MACECalculator left the global unsafe-loading override enabled"
)
assert (slice in torch.serialization.get_safe_globals()) == before_slice, (
    "The trusted e3nn slice allowance escaped its import scope"
)
"""
    environment = os.environ.copy()
    environment.pop("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", None)
    completed = subprocess.run(
        [sys.executable, "-c", probe, str(smoke)],
        env=environment, capture_output=True, text=True, timeout=180,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
