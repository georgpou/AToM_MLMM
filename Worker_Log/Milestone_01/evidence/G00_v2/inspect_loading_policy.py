"""Attribute fresh PyTorch initialization separately from scoped model loading."""
import json
import os
from pathlib import Path
import torch


def names():
    return sorted(getattr(value, '__module__', '') + '.' + getattr(value, '__qualname__', str(value))
                  for value in torch.serialization.get_safe_globals())


initial = names()
import torch._dynamo
import torch.distributed.tensor
initialized = names()
from atm_mlmm.models.mace import make_calculator
calculator = make_calculator()
after = names()
record = {'initial_torch_safe_globals': initial,
          'after_standard_torch_initialization': initialized,
          'after_trusted_model_loading': after,
          'model_loading_changed_initialized_policy': after != initialized,
          'slice_allowed_after': slice in torch.serialization.get_safe_globals(),
          'unsafe_override_present': 'TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD' in os.environ}
Path(__file__).with_name('loading-policy-diagnosis.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
assert after == initialized and not record['slice_allowed_after'] and not record['unsafe_override_present']
