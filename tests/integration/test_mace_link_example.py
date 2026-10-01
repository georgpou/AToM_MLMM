"""Real local checkpoint and mechanical ML/MM link-atom calculation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


EXAMPLE = Path(__file__).resolve().parents[2] / "examples/mace_link_cpu.py"


def test_corrupt_checkpoint_is_rejected_before_loading(tmp_path):
    spec = importlib.util.spec_from_file_location("mace_link_example", EXAMPLE)
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    checkpoint = tmp_path / "corrupt.model"
    checkpoint.write_bytes(b"not the approved MACE checkpoint")
    with pytest.raises(ValueError, match="SHA-256"):
        example.load_calculator(checkpoint)


@pytest.mark.model_assets
def test_local_mace_link_calculation(tmp_path):
    output = tmp_path / "result.json"
    offline_probe = """
import runpy
import socket
import sys

def deny_network(*args, **kwargs):
    raise RuntimeError("Network access is forbidden in the local-checkpoint regression")

socket.socket.connect = deny_network
socket.create_connection = deny_network
socket.getaddrinfo = deny_network
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
    completed = subprocess.run(
        [sys.executable, "-c", offline_probe, str(EXAMPLE), "--output", str(output)],
        capture_output=True, text=True, timeout=180,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(output.read_text())
    assert result["platform"] == "CPU"
    assert result["real_particles"] == 13
    assert result["link_particles"] == 1
    assert result["link_mass_da"] == 0
    assert result["unsafe_loading_override_present"] is False
    assert result["loading_scope_restored"] is True
    assert result["finite_energy_and_real_forces"] is True
    assert abs(result["ml_energy_kJ_mol"]) > 1
    assert all(norm > 1e-8 for norm in result["ml_boundary_parent_force_norms_kJ_mol_nm"])
    assert result["boundary_parent_force_check_passed"] is True
    assert len(result["boundary_parent_force_errors_kJ_mol_nm"]) == 2
    assert all(len(parent) == 3 for parent in result["boundary_parent_force_errors_kJ_mol_nm"])
    assert max(error for parent in result["boundary_parent_force_errors_kJ_mol_nm"]
               for error in parent) <= 5e-3
