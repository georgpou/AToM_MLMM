"""Installation smoke checks; no pretrained assets or project qualification."""
import os
import importlib.metadata as metadata
import numpy as np
import torch
import openmm as mm
from openmm import app, unit
from ase import Atoms
from ase.calculators.lj import LennardJones
from openmmml import MLPotential

assert torch.version.cuda is None and torch.version.hip is None
assert torch.ones(2, device="cpu").sum().item() == 2

# MACE 0.3.16 sets an unsafe-load environment override in its top-level import.
# Undo it before importing submodules; no pretrained checkpoints are loaded.
import mace
os.environ.pop("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", None)
with torch.serialization.safe_globals([slice]):
    from mace import modules
    from mace.calculators import MACECalculator
from e3nn import o3
import torchani

torch.manual_seed(7)
torch.set_default_dtype(torch.float64)
model = modules.ScaleShiftMACE(
    atomic_inter_scale=1.0, atomic_inter_shift=0.0,
    r_max=4.0, num_bessel=4, num_polynomial_cutoff=5, max_ell=1,
    interaction_cls=modules.RealAgnosticResidualInteractionBlock,
    interaction_cls_first=modules.RealAgnosticInteractionBlock,
    num_interactions=2, num_elements=1,
    hidden_irreps=o3.Irreps("8x0e + 8x1o"), MLP_irreps=o3.Irreps("8x0e"),
    atomic_energies=np.zeros(1), avg_num_neighbors=1.0,
    atomic_numbers=[1], correlation=2, gate=torch.nn.functional.silu,
    radial_MLP=[8, 8], heads=["Default"],
)
h2 = Atoms("H2", positions=[[0, 0, 0], [0.74, 0, 0]])
h2.calc = MACECalculator(models=model, device="cpu", default_dtype="float64")
assert np.isfinite(h2.get_potential_energy())
assert np.isfinite(h2.get_forces()).all()
print("Random, untrained MACE: finite CPU energy and forces; no weights downloaded")

aev = torchani.AEVComputer("ani2x", "ani2x", num_species=7, strategy="pyaev").double()
species = torch.tensor([[0, 0]], dtype=torch.long)
coordinates = torch.tensor([[[0., 0., 0.], [0.74, 0., 0.]]], requires_grad=True)
features = aev(species, coordinates)
assert torch.isfinite(features).all()
gradient = torch.autograd.grad(features.square().sum(), coordinates)[0]
assert torch.isfinite(gradient).all()
assert gradient.abs().max() > 0
print("TorchANI: CPU descriptors and coordinate derivatives work")

topology = app.Topology()
residue = topology.addResidue("AR", topology.addChain())
for i in range(2):
    topology.addAtom(f"Ar{i}", app.Element.getBySymbol("Ar"), residue)
positions_nm = np.array([[0., 0., 0.], [0.38, 0., 0.]])
calculator = LennardJones(epsilon=0.02, sigma=3.4)
atoms = Atoms("Ar2", positions=positions_nm * 10, calculator=calculator)
expected_energy = atoms.get_potential_energy() * 96.48533212331002
expected_forces = atoms.get_forces() * 964.8533212331002
system = MLPotential("ase").createSystem(topology, calculator=calculator)
context = mm.Context(system, mm.VerletIntegrator(0.001), mm.Platform.getPlatformByName("CPU"))
context.setPositions(positions_nm)
state = context.getState(getEnergy=True, getForces=True)
np.testing.assert_allclose(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole), expected_energy, rtol=1e-6)
np.testing.assert_allclose(state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer), expected_forces, rtol=1e-6, atol=1e-8)
del context
print("OpenMM-ML ASE bridge: CPU energy and forces match direct ASE")

child = mm.XmlSerializer.clone(system.getForce(0))
system.removeForce(0)
atm = mm.ATMForce("u0")
atm.addForce(child)
for i in range(2):
    atm.addParticle(mm.Vec3(0, 0, 0))
system.addForce(atm)
context = mm.Context(system, mm.VerletIntegrator(0.001), mm.Platform.getPlatformByName("CPU"))
context.setPositions(positions_nm)
state = context.getState(getEnergy=True, getForces=True)
np.testing.assert_allclose(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole), expected_energy, rtol=1e-6)
np.testing.assert_allclose(state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer), expected_forces, rtol=1e-6, atol=1e-8)
print("Native ATMForce accepts the ASE PythonForce on CPU")
print({name: metadata.version(name) for name in ["numpy", "torch", "mace-torch", "torchani", "e3nn", "openmm", "openmmml", "atom-openmm", "openmmforcefields"]})
