"""Weight-free reproduction of the helper's claimed loading-policy postcondition."""
import os
import runpy
import sys
import torch

before_slice = slice in torch.serialization.get_safe_globals()
runpy.run_path(sys.argv[1], run_name='__main__')
print('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD after smoke:', repr(os.environ.get('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD')))
assert slice in torch.serialization.get_safe_globals() if before_slice else slice not in torch.serialization.get_safe_globals()
assert 'TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD' not in os.environ, 'MACECalculator import re-enabled the global unsafe-loading override'
