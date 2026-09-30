"""Record full Conda integrity evidence and print a compact check summary."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atm_mlmm.persistence import verify_conda_files

report = verify_conda_files(Path(sys.prefix))
Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({
    "status": report["status"],
    "checked_files": report["checked_files"],
    "regenerable_bytecode_count": len(report["regenerable_bytecode"]),
    "prefix_relocated_without_installed_hash_count": len(report["prefix_relocated_without_installed_hash"]),
    "documented_collisions": report["documented_collisions"],
}, indent=2))
