"""Independent nonperiodic direct-MACE oracle (no ASE or adapter graph calls)."""
import numpy as np

from .schema import IdentityError, UnsupportedCapability


class NativeMACE:
    """Pinned CPU float64 total energy and autograd on one joint radius graph."""
    def __init__(self, checkpoint=None, manifest_path=None):
        from .models.mace import CHECKPOINT, load_model
        self.model = load_model(CHECKPOINT if checkpoint is None else checkpoint, manifest_path)
        self.numbers = tuple(int(z) for z in self.model.atomic_numbers)
        self.cutoff_angstrom = float(self.model.r_max)

    def evaluate(self, numbers, positions_nm):
        import torch
        from .models.mace import EV_TO_KJ_MOL, EV_A_TO_KJ_MOL_NM
        numbers = tuple(int(z) for z in numbers)
        r = np.asarray(positions_nm, dtype=float)
        if not numbers or r.shape != (len(numbers), 3) or not np.isfinite(r).all():
            raise IdentityError('native input needs ordered finite nonempty coordinates')
        if any(z not in self.numbers for z in numbers):
            raise UnsupportedCapability('native input element absent from checkpoint')
        xyz = r * 10.
        # Enumerate directed pairs ourselves. Distinct coincident atoms remain
        # edges so that diagnostic overlaps cannot silently disappear.
        edges = [(i, j) for i in range(len(r)) for j in range(len(r))
                 if i != j and np.linalg.norm(xyz[j] - xyz[i]) < self.cutoff_angstrom]
        indices = np.asarray(edges, dtype=np.int64).reshape((-1, 2)).T.copy()
        attrs = np.zeros((len(r), len(self.numbers)))
        for i, z in enumerate(numbers):
            attrs[i, self.numbers.index(z)] = 1.
        positions = torch.tensor(xyz, dtype=torch.float64, requires_grad=True)
        data = {
            'positions': positions,
            'node_attrs': torch.tensor(attrs, dtype=torch.float64),
            'edge_index': torch.tensor(indices, dtype=torch.int64),
            'shifts': torch.zeros((len(edges), 3), dtype=torch.float64),
            'unit_shifts': torch.zeros((len(edges), 3), dtype=torch.float64),
            'cell': torch.zeros((3, 3), dtype=torch.float64),
            'batch': torch.zeros(len(r), dtype=torch.int64),
            'ptr': torch.tensor([0, len(r)], dtype=torch.int64),
            'head': torch.zeros(1, dtype=torch.int64),
        }
        with torch.enable_grad():
            output = self.model(data, compute_force=False)
            energy = output['energy'].sum()
            gradient = torch.autograd.grad(energy, positions)[0]
        e = float(energy.detach())
        g = gradient.detach().numpy().copy()
        return {
            'numbers': list(numbers), 'positions_nm': r.tolist(),
            'box_nm': None, 'pbc': False, 'head': 'Default', 'dtype': 'float64',
            'energy_convention': 'energy', 'cutoff_angstrom': self.cutoff_angstrom,
            'directed_edges': indices.T.tolist(), 'energy_eV': e,
            'gradient_eV_angstrom': g.tolist(),
            'energy_kj_mol': e * EV_TO_KJ_MOL,
            'forces_kj_mol_nm': (-g * EV_A_TO_KJ_MOL_NM).tolist(),
            'finite': bool(np.isfinite(e) and np.isfinite(g).all()),
        }
