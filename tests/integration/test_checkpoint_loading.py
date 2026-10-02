"""G00-T2 trusted asset loading, with a pre-deserialization authorization guard."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import os

import pytest


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'models/mace-off23-small'


@pytest.mark.model_assets
def test_authorization_is_checked_before_deserialization(tmp_path, monkeypatch):
    # Exercise the inherited entry point, rather than an absent new API.
    spec = importlib.util.spec_from_file_location('mace_link_loading_probe',
                                                ROOT / 'examples/mace_link_cpu.py')
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    example.load_calculator()  # Complete trusted imports before the sentinel.
    import torch

    checkpoint = tmp_path / 'MACE-OFF23_small.model'
    shutil.copyfile(ASSET / checkpoint.name, checkpoint)
    shutil.copyfile(ASSET / 'LICENSE.md', tmp_path / 'LICENSE.md')
    manifest = json.loads((ASSET / 'manifest.json').read_text())
    manifest.pop('user_authorization')
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest))

    def deserialization_sentinel(*args, **kwargs):
        raise AssertionError('checkpoint deserialization preceded authorization validation')

    monkeypatch.setattr(torch, 'load', deserialization_sentinel)
    with pytest.raises(ValueError, match='authorization'):
        example.load_calculator(checkpoint)


@pytest.mark.model_assets
def test_trusted_checkpoint_loads_in_fresh_process(tmp_path):
    probe = '''
import json, os, pickle, socket
def deny(*args, **kwargs):
    raise AssertionError('network access attempted by offline model loading')
socket.socket.connect = deny
socket.create_connection = deny
socket.getaddrinfo = deny
import torch
# Initialize standard PyTorch components before checking the loader's scope.
# Their lazy imports register Torch's own safe tensor types; that is distinct
# from a custom model/slice allowance or a global unsafe-load override.
import torch._dynamo
import torch.distributed.tensor
before = set(torch.serialization.get_safe_globals())
from atm_mlmm.models.mace import make_calculator
calculator = make_calculator()
model = calculator.models[0]
assert set(torch.serialization.get_safe_globals()) == before
assert 'TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD' not in os.environ
assert all(t.dtype == torch.float64 for t in model.parameters())
class Untrusted:
    pass
target = os.path.join(os.environ['XDG_CACHE_HOME'], 'untrusted.pt')
torch.save(Untrusted(), target)
try:
    torch.load(target)
except pickle.UnpicklingError:
    pass
else:
    raise AssertionError('default torch.load no longer rejects arbitrary full-module pickle')
print(json.dumps({'architecture': type(model).__name__, 'r_max': float(model.r_max),
                  'head': calculator.head, 'energy_units_to_eV': calculator.energy_units_to_eV,
                  'length_units_to_A': calculator.length_units_to_A,
                  'global_policy_restored': True}))
'''
    environment = os.environ.copy()
    cache = tmp_path / 'empty-cache'
    cache.mkdir()
    environment.update(XDG_CACHE_HOME=str(cache), TORCH_HOME=str(cache / 'torch'),
                       MACE_CACHE_DIR=str(cache / 'mace'), PYTHONPATH=str(ROOT / 'src'))
    environment.pop('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD', None)
    result = subprocess.run([sys.executable, '-c', probe], env=environment,
                            capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    assert report == {'architecture': 'ScaleShiftMACE', 'r_max': 4.5, 'head': 'Default',
                      'energy_units_to_eV': 1., 'length_units_to_A': 1.,
                      'global_policy_restored': True}
