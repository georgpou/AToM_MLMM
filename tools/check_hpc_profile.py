#!/usr/bin/env python
"""Validate an explicit HPC profile; never submits or resumes a job."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atm_mlmm.hpc import check_profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--bundle-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text())
    bundle = None if args.bundle_manifest is None else json.loads(args.bundle_manifest.read_text())
    result = check_profile(profile, bundle_manifest=bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] != "held" else 2


if __name__ == "__main__":
    raise SystemExit(main())
