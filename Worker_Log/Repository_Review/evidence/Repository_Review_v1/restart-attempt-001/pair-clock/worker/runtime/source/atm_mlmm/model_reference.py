"""Independent direct-MACE oracle (no ASE or adapter graph calls)."""
import itertools
import numpy as np

from .schema import IdentityError, UnsupportedCapability


class NativeMACE:
    """Pinned CPU float64 total energy and autograd on one joint radius graph."""
    def __init__(self, checkpoint=None, manifest_path=None):
        from .models.mace import CHECKPOINT, load_model
        self.model = load_model(CHECKPOINT if checkpoint is None else checkpoint, manifest_path)
        self.numbers = tuple(int(z) for z in self.model.atomic_numbers)
        self.cutoff_angstrom = float(self.model.r_max)

    def evaluate(self, numbers, positions_nm, *, box_nm=None):
        import torch
        from .models.mace import EV_TO_KJ_MOL, EV_A_TO_KJ_MOL_NM
        numbers = tuple(int(z) for z in numbers)
        r = np.asarray(positions_nm, dtype=float)
        if not numbers or r.shape != (len(numbers), 3) or not np.isfinite(r).all():
            raise IdentityError('native input needs ordered finite nonempty coordinates')
        if any(z not in self.numbers for z in numbers):
            raise UnsupportedCapability('native input element absent from checkpoint')
        xyz = r * 10.
        # Enumerate pairs/images ourselves; do not call ASE neighbor helpers or
        # production geometry. Distinct coincident atoms remain diagnostic edges.
        cell = np.zeros((3,3)) if box_nm is None else np.asarray(box_nm)*10.
        if box_nm is not None and (cell.shape!=(3,3) or not np.isfinite(cell).all()
                or np.any(cell!=np.diag(np.diag(cell))) or np.any(np.diag(cell)<=2*self.cutoff_angstrom)):
            raise UnsupportedCapability('native periodic oracle requires a safe orthorhombic cell')
        edges, unit_shifts = [], []
        for i in range(len(r)):
            for j in range(len(r)):
                if i == j: continue
                delta = xyz[j]-xyz[i]
                center = np.zeros(3,dtype=int) if box_nm is None else -np.floor(delta/np.diag(cell)).astype(int)
                candidates = ((0,0,0),) if box_nm is None else itertools.product((-1,0,1),repeat=3)
                for candidate in candidates:
                    shift = center+candidate
                    if np.linalg.norm(delta+shift@cell) < self.cutoff_angstrom:
                        edges.append((i,j));unit_shifts.append(shift)
        indices = np.asarray(edges, dtype=np.int64).reshape((-1, 2)).T.copy()
        unit_shifts = np.asarray(unit_shifts,dtype=float).reshape((-1,3))
        attrs = np.zeros((len(r), len(self.numbers)))
        for i, z in enumerate(numbers):
            attrs[i, self.numbers.index(z)] = 1.
        positions = torch.tensor(xyz, dtype=torch.float64, requires_grad=True)
        data = {
            'positions': positions,
            'node_attrs': torch.tensor(attrs, dtype=torch.float64),
            'edge_index': torch.tensor(indices, dtype=torch.int64),
            'shifts': torch.tensor(unit_shifts@cell,dtype=torch.float64),
            'unit_shifts': torch.tensor(unit_shifts,dtype=torch.float64),
            'cell': torch.tensor(cell,dtype=torch.float64),
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
            'box_nm': None if box_nm is None else np.asarray(box_nm).tolist(),
            'pbc': box_nm is not None, 'head': 'Default', 'dtype': 'float64',
            'energy_convention': 'energy', 'cutoff_angstrom': self.cutoff_angstrom,
            'directed_edges': indices.T.tolist(), 'energy_eV': e,
            'unit_shifts':unit_shifts.astype(int).tolist(),
            'gradient_eV_angstrom': g.tolist(),
            'energy_kj_mol': e * EV_TO_KJ_MOL,
            'forces_kj_mol_nm': (-g * EV_A_TO_KJ_MOL_NM).tolist(),
            'finite': bool(np.isfinite(e) and np.isfinite(g).all()),
        }
