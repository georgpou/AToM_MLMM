#!/usr/bin/env python
"""Build a new local hash-bound source/wheel/input/asset/evidence bundle."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atm_mlmm.release import build_release_bundle, verify_release_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--evidence", type=Path, action="append", default=[])
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--asset-dir", type=Path,
                        default=Path(__import__("os").environ.get(
                            "ATOM_MLMM_MODEL_DIR", ROOT / "models/mace-off23-small")))
    parser.add_argument("--source-path", action="append", default=[])
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        result = verify_release_bundle(args.output)
    else:
        paths = args.source_path or ["pyproject.toml", "src/atm_mlmm", "tools",
                                     "tests", "docs/project-0/support-matrix.json",
                                     "docs/project-0/before-hpc-requirement-matrix.json"]
        result = build_release_bundle(args.output, source_root=args.source_root,
                                      source_paths=paths, wheel=args.wheel,
                                      inputs=args.input, assets=args.asset_dir,
                                      evidence=args.evidence)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
