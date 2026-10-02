"""Quantum-only availability probe; never evaluates or imports an ML model."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import time


def deny_network(*args, **kwargs):
    raise RuntimeError('the quantum availability pilot must run offline')


socket.socket.connect = deny_network
socket.create_connection = deny_network
socket.getaddrinfo = deny_network

import numpy as np
import psi4

ROOT = Path(os.environ.get('ATOM_QUANTUM_PILOT_ROOT', '/workspace/atom-mlmm-reference-pilot'))
ROOT.mkdir(exist_ok=True)
psi4.set_num_threads(2)
psi4.set_memory('5 GiB')
psi4.core.IOManager.shared_object().set_default_path(str(ROOT))
psi4.set_output_file(str(ROOT / 'methane-pilot.dat'), False)

distance = 1.09 / np.sqrt(3.)
coordinates = np.array([[0., 0., 0.], [distance, distance, distance],
                        [distance, -distance, -distance],
                        [-distance, distance, -distance],
                        [-distance, -distance, distance]])
settings = {'basis': 'def2-tzvppd', 'df_basis_scf': 'def2-universal-jkfit',
            'reference': 'rhf', 'scf_type': 'df', 'e_convergence': 1e-10,
            'd_convergence': 1e-10, 'maxiter': 200, 'ints_tolerance': 1e-12,
            'dft_radial_points': 99, 'dft_spherical_points': 590}
psi4.set_options(settings)


def molecule(positions):
    rows = ['0 1'] + [element + ' ' + ' '.join(format(v, '.17g') for v in xyz)
                     for element, xyz in zip(['C', 'H', 'H', 'H', 'H'], positions)]
    rows += ['units angstrom', 'no_reorient', 'no_com', 'symmetry c1']
    return psi4.geometry('\n'.join(rows))


started = datetime.datetime.now(datetime.timezone.utc).isoformat()
clock = time.monotonic()
gradient, wavefunction = psi4.gradient('wb97m-d3bj', molecule=molecule(coordinates), return_wfn=True)
raw_gradient = np.asarray(gradient)
energy = float(wavefunction.energy())
variables = {key: float(value) for key, value in psi4.core.variables().items()
             if isinstance(value, (int, float)) and any(term in key for term in ['ENERGY', 'DISPERSION'])}
# CODATA 2014, recorded explicitly; gradients from Psi4 are Eh/bohr.
hartree_kj_mol = 4.359744650e-18 * 6.022140857e23 / 1000.
bohr_nm = 5.2917721067e-2
forces = -raw_gradient * hartree_kj_mol / bohr_nm
finite_differences = []
for step_angstrom in (1e-3, 1e-4):
    plus, minus = coordinates.copy(), coordinates.copy()
    plus[1, 0] += step_angstrom
    minus[1, 0] -= step_angstrom
    ep = float(psi4.energy('wb97m-d3bj', molecule=molecule(plus)))
    em = float(psi4.energy('wb97m-d3bj', molecule=molecule(minus)))
    fd = -(ep - em) * hartree_kj_mol / (2. * step_angstrom / 10.)
    finite_differences.append({'step_angstrom': step_angstrom,
                              'energies_hartree': [ep, em],
                              'force_kJ_mol_nm': fd,
                              'absolute_error_kJ_mol_nm': abs(fd - forces[1, 0])})
data_dir = Path(psi4.core.get_datadir())
basis_hashes = {}
for name in ('def2-tzvppd.gbs', 'def2-universal-jkfit.gbs'):
    path = data_dir / 'basis' / name
    basis_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
record = {'scope': 'quantum-only feasibility; no G05/G07 model comparison or chemical acceptance',
          'started_utc': started, 'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'wall_seconds': time.monotonic() - clock, 'psi4_version': psi4.__version__,
          'method': 'wb97m-d3bj', 'settings': settings, 'threads': 2, 'memory': '5 GiB',
          'formal_charge': 0, 'multiplicity': 1, 'elements': ['C', 'H', 'H', 'H', 'H'],
          'positions_angstrom': coordinates.tolist(), 'energy_hartree': energy,
          'gradient_hartree_bohr': raw_gradient.tolist(), 'forces_kJ_mol_nm': forces.tolist(),
          'hartree_to_kJ_mol': hartree_kj_mol, 'bohr_to_nm': bohr_nm,
          'quantum_energy_variables': variables, 'finite_difference_probe': finite_differences,
          'basis_file_sha256': basis_hashes, 'network_denied': True,
          'finite_energy_gradient_forces': bool(np.isfinite(energy) and np.isfinite(raw_gradient).all()
                                               and np.isfinite(forces).all())}
(ROOT / 'methane-pilot.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
print(json.dumps(record, indent=2, allow_nan=False))
assert record['finite_energy_gradient_forces']
