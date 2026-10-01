"""Verify both complete Python inventories and exact Conda artifacts."""
import importlib.metadata as metadata
import json
from pathlib import Path
import re
import sys

root, label = Path(sys.argv[1]), sys.argv[2]
normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
expected = {}
for line in (root / f"{label}-pip-inventory.txt").read_text().splitlines():
    name, version = line.split("==", 1)
    expected[normalize(name)] = version
actual = {normalize(dist.metadata["Name"]): dist.version for dist in metadata.distributions()}
assert actual == expected, json.dumps({
    "missing_or_changed": {name: {"expected": version, "actual": actual.get(name)}
                           for name, version in expected.items() if actual.get(name) != version},
    "unexpected": {name: version for name, version in actual.items() if name not in expected},
}, indent=2)
prefix = Path(sys.prefix)
assert sys.version_info[:2] == (3, 11), sys.version
locked = {line.strip() for line in (root / f"{label if label == 'core' else 'amber'}-conda-linux-64.lock").read_text().splitlines()
          if line.startswith("https://")}
installed = set()
for path in (prefix / "conda-meta").glob("*.json"):
    record = json.loads(path.read_text())
    installed.add(record["url"] + "#" + record["sha256"])
assert installed == locked, json.dumps({"missing": sorted(locked-installed),
                                       "unexpected": sorted(installed-locked)}, indent=2)
print(f"{label}: Python {sys.version.split()[0]}, {len(actual)} exact Python distributions, {len(installed)} exact Conda artifacts")
