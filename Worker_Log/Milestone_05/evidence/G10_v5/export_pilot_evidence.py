#!/usr/bin/env python3
"""Export compact, hashed summaries from the retained full G10 v5 pilots."""
import argparse
import hashlib
import json
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_case(root, kind):
    case = root / kind
    run = case / "multistate-run"
    pilot = read_json(case / "pilot-check.json")
    summary = read_json(run / "summary.json")
    resources = read_json(case / "resource-metrics.json")
    oracle = read_json(case / "actual-context-oracle.json")
    stale = read_json(case / "stale-coordinate-rejection.json")
    committed_tree_manifests = {
        "initial": sha256(run / "initial" / "manifest.json"),
        **{
            f"boundary-{index:06d}": sha256(
                run / "boundaries" / f"{index:06d}" / "manifest.json"
            )
            for index in range(2)
        },
    }
    boundaries = []
    for index in range(2):
        boundary_root = run / "boundaries" / f"{index:06d}"
        record = read_json(boundary_root / "record.json")
        samples = []
        for worker_index in range(3):
            sample = read_json(
                boundary_root / "samples" / f"worker-{worker_index:03d}.json"
            )
            maps = [row for row in sample["domain"] if "map" in row]
            samples.append({
                "sample_id": sample["sample_id"],
                "walker_id": sample["walker_id"],
                "walker_index": sample["walker_index"],
                "sequence_number": sample["sequence_number"],
                "capture_time_state_id": sample["state_id"],
                "real_atom_count": len(sample["real_atom_ids"]),
                "full_force_shape": [
                    len(sample["real_forces_kj_mol_nm"]),
                    len(sample["real_forces_kj_mol_nm"][0]),
                ],
                "box_present": sample["box_nm"] is not None,
                "velocities_present": sample["velocities_nm_ps"] is not None,
                "parameters": sample["parameters"],
                "raw": sample["raw"],
                "map_diagnostics": maps,
            })
        boundaries.append({
            "boundary_index": record["boundary_index"],
            "walker_to_state_start": record["walker_to_state_start"],
            "walker_to_state_final": record["walker_to_state_final"],
            "pair_count": record["pair_count"],
            "samples": samples,
        })
    return {
        "case": kind,
        "input_config_original_sha256": pilot["input_config_original_sha256"],
        "input_manifest_sha256": pilot["input_manifest_sha256"],
        "copied_input_hashes_unchanged": pilot["copied_input_hashes_unchanged"],
        "worker_manifest_sha256": sha256(case / "prepared-run" / "worker" / "manifest.json"),
        "prepared_metadata_sha256": sha256(case / "prepared-run" / "metadata.json"),
        "multistate_metadata_sha256": sha256(run / "metadata.json"),
        "committed_tree_manifests_sha256": committed_tree_manifests,
        "summary": summary,
        "resource_metrics": resources,
        "actual_context_oracle": oracle,
        "stale_coordinate_probe": stale,
        "boundaries": boundaries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    document = {
        "external_artifact_root": str(args.artifact_root.resolve()),
        "cases": [export_case(args.artifact_root, kind) for kind in ("abfe", "rbfe")],
        "qualification": "bounded CPU technical pilots only; binding_result=not_evaluated",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
