"""Inspect installed modules and CPU identities, not just distribution labels."""
import hashlib
import importlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys
import torch
import openmm
from packaging.version import Version

root = Path('/workspace/.onboarding/atom-mlmm-independent-audit-v1b')
assert Path(sys.prefix) == root/'env'
assert torch.version.cuda is None and torch.version.hip is None
assert str(torch.ones(1, device='cpu').device) == 'cpu'
identities = {}
for module, distname in [('numpy','numpy'),('torch','torch'),('openmm','openmm'),('openmmml','openmmml'),
                         ('atom_openmm','atom-openmm'),('openmmforcefields','openmmforcefields')]:
    imported = importlib.import_module(module)
    path = Path(imported.__file__).resolve()
    assert path.is_relative_to(root/'env'), path
    dist = metadata.distribution(distname)
    identities[distname] = dict(version=dist.version, module_path=str(path), module_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                installed_direct_url=json.loads(dist.read_text('direct_url.json')) if dist.read_text('direct_url.json') else None)
assert metadata.version('atom-openmm') == str(Version('8.5.0beta')) == '8.5.0b0'
for name in ['atom-openmm','openmmml','openmmforcefields']:
    assert identities[name]['installed_direct_url'] is None, identities[name]
before = torch.serialization.get_safe_globals().copy()
import mace
unsafe_import_value = os.environ.pop('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD', None)
assert unsafe_import_value is not None
with torch.serialization.safe_globals([slice]):
    from mace import modules
    from mace.calculators import MACECalculator
after = torch.serialization.get_safe_globals()
# Importing PyTorch's Dynamo/DTensor modules registers their own trusted types.
# The audit checks the scoped slice allowance and records those package defaults.
assert (slice in before) == (slice in after)
added_safe_globals = set(after) - set(before)
assert all(item.__module__.startswith('torch.') for item in added_safe_globals)
unsafe_calculator_value = os.environ.get('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD')
assert not os.environ.get('TORCHANI_NO_WARN_EXTENSIONS')
platforms = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
assert 'CPU' in platforms and 'Reference' in platforms
from openmmforcefields import _version
versioneer = _version.get_versions()
assert versioneer['version'] == '0.16.0' and versioneer['full-revisionid'] == '3aa91626db3aeea8e8388c43c42a51bf1d99159e'
result = dict(interpreter=sys.executable, identities=identities, torch_cuda=torch.version.cuda, torch_hip=torch.version.hip,
              openmm_platforms=platforms, openmmforcefields_embedded_identity=versioneer,
              mace_import_unsafe_variable=unsafe_import_value,
              mace_calculator_import_unsafe_variable=unsafe_calculator_value,
              unsafe_override_cleared=(unsafe_calculator_value is None),
              scoped_slice_allowance_restored=True,
              pytorch_import_safe_globals_added=sorted(item.__module__+'.'+item.__qualname__ for item in added_safe_globals),
              pretrained_checkpoint_loading='not run; no weights authorized')
(Path(__file__).resolve().parent/'runtime-identities.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
sys.exit(1 if unsafe_calculator_value is not None else 0)
