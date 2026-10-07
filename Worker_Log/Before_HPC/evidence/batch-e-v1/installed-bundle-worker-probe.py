"""Load the approved MACE asset and a fresh worker from a local release bundle."""
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import sys

import numpy as np
from ase import Atoms

import atm_mlmm
from atm_mlmm.adapters.atom import load_worker_run
from atm_mlmm.models.mace import ASSET, make_calculator, verify_asset
from atm_mlmm.schema import from_json


def deny_network(*args, **kwargs):
    raise AssertionError("local installed bundle attempted network access")


socket.socket.connect = deny_network
socket.create_connection = deny_network
socket.getaddrinfo = deny_network

bundle = Path(os.environ["ATOM_MLMM_BUNDLE_ROOT"]).resolve()
source = Path(os.environ["ATOM_MLMM_SOURCE_ROOT"]).resolve()
package = Path(atm_mlmm.__file__).resolve()
assert package.is_relative_to(Path(sys.prefix).resolve())
assert not package.is_relative_to(source)
assert ASSET.resolve() == Path(os.environ["ATOM_MLMM_MODEL_DIR"]).resolve()

manifest = verify_asset()
manifest_bytes = (ASSET / "manifest.json").read_bytes()
assert hashlib.sha256(manifest_bytes).hexdigest() == "6d78f71f779798b67d73da573c67e2ce65ba6c2bfe1d1d3b8fa6c72d603a0926"
assert manifest["user_authorization"] == "I will use it for academic purposes."
assert manifest["files"]["MACE-OFF23_small.model"]["sha256"] == "165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f"
assert manifest["files"]["LICENSE.md"]["sha256"] == "6a77e88bfed86fe9476ed36e453e2ea1e154ff1ec464b0fdeb3e079b6112d71e"

worker_dir = bundle / "inputs" / "worker-export"
worker_manifest_bytes = (worker_dir / "manifest.json").read_bytes()
worker_manifest_sha256 = hashlib.sha256(worker_manifest_bytes).hexdigest()
snapshot = from_json((worker_dir / "snapshot.json").read_text())
with load_worker_run(worker_dir, worker_manifest_sha256, trusted=True) as worker:
    atoms = Atoms(symbols=[atom.element for atom in worker.bundle.physical.topology.atoms],
                  positions=np.asarray(snapshot.positions_nm) * 10.)
    atoms.calc = make_calculator()
    model_energy_ev = float(atoms.get_potential_energy())
    model_forces_ev_angstrom = np.asarray(atoms.get_forces())
    worker_result = worker.evaluate(snapshot, worker.manifest["state_id"])
    worker_energy = float(worker_result.total.energy_kj_mol)
    worker_forces = np.asarray(worker_result.total.forces_kj_mol_nm)

assert math.isfinite(model_energy_ev) and np.isfinite(model_forces_ev_angstrom).all()
assert math.isfinite(worker_energy) and np.isfinite(worker_forces).all()
print(json.dumps({
    "scope": "installed wheel; explicit local model asset; fresh trusted worker; fixed-coordinate evaluation",
    "package_location": str(package),
    "bundle_root": str(bundle),
    "asset_directory": str(ASSET),
    "checkpoint_sha256": manifest["files"]["MACE-OFF23_small.model"]["sha256"],
    "license_sha256": manifest["files"]["LICENSE.md"]["sha256"],
    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    "authorization": manifest["user_authorization"],
    "worker_manifest_sha256": worker_manifest_sha256,
    "atoms": len(snapshot.real_atom_ids),
    "model_energy_ev": model_energy_ev,
    "model_force_count": int(len(model_forces_ev_angstrom)),
    "worker_energy_kj_mol": worker_energy,
    "worker_force_count": int(len(worker_forces)),
    "network_access": "blocked",
    "finite_results": True,
}, sort_keys=True, allow_nan=False))
