"""Record full Conda integrity evidence and print a compact check summary."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atm_mlmm.persistence import verify_conda_files

try:
    report = verify_conda_files(Path(sys.prefix))
except ValueError:
    # Report every shared file owner before rejecting an unreviewed collision.
    import hashlib
    from collections import defaultdict
    owners = defaultdict(list)
    prefix = Path(sys.prefix)
    for metadata_path in (prefix / "conda-meta").glob("*.json"):
        record = json.loads(metadata_path.read_text())
        for entry in record.get("paths_data", {}).get("paths", []):
            digest = entry.get("sha256_in_prefix") or entry.get("sha256")
            if digest and not entry.get("prefix_placeholder"):
                owners[entry["_path"]].append({"name": record["name"], "sha256": digest})
    collisions = []
    for relative, records in sorted(owners.items()):
        if len({p["sha256"] for p in records}) > 1 and not relative.endswith(".pyc"):
            path = prefix / relative
            collisions.append({"path": relative, "owners": records,
                               "installed_sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                               if path.is_file() else None})
    print("G00_COLLISION_DIAGNOSTIC " + json.dumps(collisions), flush=True)
    raise
Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({
    "status": report["status"],
    "checked_files": report["checked_files"],
    "regenerable_bytecode_count": len(report["regenerable_bytecode"]),
    "prefix_relocated_without_installed_hash_count": len(report["prefix_relocated_without_installed_hash"]),
    "documented_collisions": report["documented_collisions"],
}, indent=2))
