"""Export one current-source worker on the retained synthetic two-cap input."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tests.cap_collection_oracle import input_case
from tests.analytic_oracle import production_parameters
from atm_mlmm.adapters.atom import build_atom, export_worker_run
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.hybrid import build_physical
from atm_mlmm.models.mace import model_spec
from atm_mlmm.partition import resolve_partition
from atm_mlmm.protocols.rbfe import make_protocol
from atm_mlmm.schedule import production_schedule
from atm_mlmm.schema import EmbeddingSpec, MobileGroup, RestraintSpec, RuntimeSpec

original, partition_spec, snapshot = input_case()
physical = build_physical(original, resolve_partition(original.topology, partition_spec),
                          model_spec(), EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"),
                          cap_distance_nm=.117)
groups = tuple(MobileGroup(f"mobile-{m.molecule_id}", m.atom_ids, (m.role,), m.molecule_id)
               for m in original.topology.molecules if m.role == "ligand")
transfer = resolve_protocol(physical, make_protocol(groups, (.3, 0., 0.)))
schedule = production_schedule(tuple((name, production_parameters(
    Lambda1=lam, Lambda2=lam, Umax=10000., Ubcore=500., Acore=0., W0=0., UOffset=0.))
    for name, lam in (("contact", 0.), ("middle", .5), ("separated", 1.))))
restraints = RestraintSpec("anchor", (snapshot.real_atom_ids[0],), 1., tuple(snapshot.positions_nm[0]))
runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "LangevinMiddle")
with build_atom(physical, transfer, schedule, restraints, runtime) as source:
    handover, digest = export_worker_run(source, Path(sys.argv[1]), snapshot, "middle")
print(json.dumps({"directory": str(handover.parent), "manifest_sha256": digest,
                  "real_atoms": len(snapshot.real_atom_ids), "caps": len(physical.links),
                  "scope": "fresh current-source synthetic worker; no dynamics"}, sort_keys=True))
