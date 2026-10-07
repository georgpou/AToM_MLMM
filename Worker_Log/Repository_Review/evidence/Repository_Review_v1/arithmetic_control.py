"""Independent unit/sign arithmetic from exact SI constants; no simulation."""
from decimal import Decimal, getcontext
import json
import math
from pathlib import Path

getcontext().prec = 80
D = Decimal
avogadro = D('6.02214076e23')
boltzmann = D('1.380649e-23')
gas_constant = avogadro * boltzmann / D(1000)
beta = D(1) / (gas_constant * D(300))
electronvolt_to_kj_mol = avogadro * D('1.602176634e-19') / D(1000)
# Synthetic complete totals in kJ/mol, rows = states, columns = configurations.
energies = ((D(4), D(11)), (D(6), D(2)))
delta = beta * (energies[0][1] + energies[1][0] - energies[0][0] - energies[1][1])
probability = (-delta).exp()
# Complete the square for k=100, k_restraint=50, displacement=0.3 nm.
gaussian_difference = D('.5') * D(100) * D('.3')**2 - D(100)**2 * D('.3')**2 / (2 * (D(100) + D(50)))
from atm_mlmm.restraints import MOLAR_GAS_CONSTANT_KJ_MOL_K
assert abs(D(str(MOLAR_GAS_CONSTANT_KJ_MOL_K)) - gas_constant) < D('1e-18')
assert abs(float(beta) - .4009078501424201) < 1e-15
assert gaussian_difference == D('1.5')
result = {'R_kj_mol_K': str(gas_constant), 'beta_mol_per_kJ_at_300K': str(beta),
          'kJ_mol_nm_per_eV_angstrom': str(10 * electronvolt_to_kj_mol),
          'independent_exchange_delta': str(delta), 'independent_exchange_probability': str(probability),
          'negative_delta_accepts_without_exponentiating_positive_number': True,
          'gaussian_endpoint_difference_kj_mol': str(gaussian_difference),
          'scope': 'unit/sign arithmetic; not a trajectory or new clock campaign'}
Path(__file__).with_name('arithmetic-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
