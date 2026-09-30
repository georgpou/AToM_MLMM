"""Archive non-Conda distributions as immutable wheels for the G00 lock."""
import hashlib
import json
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path


def _canonical_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def main():
    output = Path(sys.argv[1]).resolve()
    prefix = Path(sys.prefix)
    owned = set()
    for path in (prefix / "conda-meta").glob("*.json"):
        record = json.loads(path.read_text())
        owned.update(record.get("files", []))
        owned.update(p["_path"] for p in record.get("paths_data", {}).get("paths", []))
    owned_metadata = [(prefix / relative, metadata.PathDistribution((prefix / relative).parent))
                      for relative in sorted(owned) if relative.endswith(".dist-info/METADATA")]
    specs, sources = [], {}
    for dist in metadata.distributions():
        name = dist.metadata["Name"]
        if name.lower().replace("_", "-") == "atm-mlmm":
            continue  # project source is pinned by the repository commit
        # Conda can remove a wheel's RECORD while retaining dist-info metadata.
        # Locate that metadata directly; do not infer ownership from RECORD.
        if any(_canonical_name(owner.metadata["Name"]) == _canonical_name(name)
               and owner.version == dist.version
               and dist.locate_file(Path(path.parent.name) / "METADATA").resolve() == path.resolve()
               for path, owner in owned_metadata):
            continue
        origin = dist.read_text("direct_url.json")
        origin = json.loads(origin) if origin else None
        if origin and "vcs_info" in origin:
            commit = origin["vcs_info"]["commit_id"]
            spec = f'{name} @ git+{origin["url"]}@{commit}'
            sources[name.lower()] = origin
        elif origin:
            raise RuntimeError(f"Unreviewed non-VCS direct dependency: {name}: {origin}")
        else:
            spec = f"{name}=={dist.version}"
        specs.append(spec)
    (output / "pip-source-lock.txt").write_text("\n".join(sorted(specs)) + "\n")
    wheelhouse = output / "wheelhouse"
    wheelhouse.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir",
                    str(wheelhouse), "-r", str(output / "pip-source-lock.txt")], check=True)
    wheels = sorted(wheelhouse.glob("*.whl"))
    for name, origin in sources.items():
        matches = [p for p in wheels if p.name.split("-")[0].lower().replace("_", "-") == name.replace("_", "-")]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one archived source wheel for {name}")
        origin["wheel_sha256"] = hashlib.sha256(matches[0].read_bytes()).hexdigest()
    (output / "source-origins.json").write_text(json.dumps(sources, indent=2) + "\n")
    locks = [f"wheelhouse/{p.name} --hash=sha256:{hashlib.sha256(p.read_bytes()).hexdigest()}"
             for p in wheels]
    (output / "pip-wheels.lock").write_text("\n".join(locks) + "\n")
    # Exercise the actual archived files. Conda-owned distributions are untouched.
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "--no-index",
                    "--require-hashes", "--force-reinstall", "-r", "pip-wheels.lock"],
                   cwd=output, check=True)


if __name__ == "__main__":
    main()
