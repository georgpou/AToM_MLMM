"""Verify the installed wheel, approved local asset route, and fresh actual worker."""
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
    raise AssertionError("installed local probe attempted network access")


socket.socket.connect = deny_network
socket.create_connection = deny_network
socket.getaddrinfo = deny_network
assert "PYTHONPATH" not in os.environ
package = Path(atm_mlmm.__file__).resolve()
assert package.is_relative_to(Path(sys.prefix).resolve())
source_root = Path(os.environ["ATOM_MLMM_SOURCE_ROOT"]).resolve()
assert not package.is_relative_to(source_root)
asset_root = Path(os.environ["ATOM_MLMM_MODEL_DIR"]).resolve()
assert ASSET.resolve() == asset_root
manifest = verify_asset()
manifest_bytes = (asset_root / "manifest.json").read_bytes()
assert hashlib.sha256(manifest_bytes).hexdigest() == "6d78f71f779798b67d73da573c67e2ce65ba6c2bfe1d1d3b8fa6c72d603a0926"
assert manifest["user_authorization"] == "I will use it for academic purposes."
assert manifest["files"]["MACE-OFF23_small.model"]["sha256"] == "165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f"
assert manifest["files"]["LICENSE.md"]["sha256"] == "6a77e88bfed86fe9476ed36e453e2ea1e154ff1ec464b0fdeb3e079b6112d71e"

worker_dir = Path(os.environ["ATOM_MLMM_WORKER_DIR"]).resolve()
worker_manifest_bytes = (worker_dir / "manifest.json").read_bytes()
worker_digest = hashlib.sha256(worker_manifest_bytes).hexdigest()
assert worker_digest == os.environ["ATOM_MLMM_WORKER_MANIFEST_SHA256"]
worker_manifest = json.loads(worker_manifest_bytes)
snapshot = from_json((worker_dir / "snapshot.json").read_text())
with load_worker_run(worker_dir, worker_digest, trusted=True) as worker:
    atoms = Atoms(symbols=[atom.element for atom in worker.bundle.physical.topology.atoms],
                  positions=np.asarray(snapshot.positions_nm) * 10.)
    atoms.calc = make_calculator()
    model_energy_ev = float(atoms.get_potential_energy())
    model_forces = np.asarray(atoms.get_forces())
    result = worker.evaluate(snapshot, worker_manifest["state_id"])
    worker_energy = float(result.total.energy_kj_mol)
    worker_forces = np.asarray(result.total.forces_kj_mol_nm)
assert math.isfinite(model_energy_ev) and np.isfinite(model_forces).all()
assert math.isfinite(worker_energy) and np.isfinite(worker_forces).all()
print(json.dumps({
    "scope": "installed final wheel; bundled local model; fresh source worker; fixed-coordinate evaluation",
    "package_location": str(package),
    "asset_directory": str(asset_root),
    "model_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    "checkpoint_sha256": manifest["files"]["MACE-OFF23_small.model"]["sha256"],
    "license_sha256": manifest["files"]["LICENSE.md"]["sha256"],
    "authorization": manifest["user_authorization"],
    "worker_directory": str(worker_dir),
    "worker_manifest_sha256": worker_digest,
    "atoms": len(snapshot.real_atom_ids),
    "model_energy_ev": model_energy_ev,
    "model_force_count": int(len(model_forces)),
    "worker_energy_kj_mol": worker_energy,
    "worker_force_count": int(len(worker_forces)),
    "network_access": "blocked",
    "finite_results": True,
}, sort_keys=True, allow_nan=False))
