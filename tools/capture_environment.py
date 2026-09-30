"""Write the G00 evidence record and artifact hashes, including failed checks."""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atm_mlmm.persistence import capture_environment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    checks = {p.stem: {"exit_code": int(p.read_text()), "log": f"{p.stem}.log"}
              for p in output.glob("*.exit")}
    report = capture_environment(root, Path(sys.prefix), checks)
    conda_records = [json.loads(p.read_text()) for p in (Path(sys.prefix) / "conda-meta").glob("*.json")]
    (output / "conda-metadata.json").write_text(json.dumps(conda_records, indent=2) + "\n")
    source_record = output / "source-origins.json"
    report["archived_source_origins"] = json.loads(source_record.read_text()) if source_record.exists() else {}
    report["artifact_hashes"] = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*")) if p.is_file()
        and p.name not in ("environment-manifest.json", "file-manifest.sha256")
    }
    report["actions"] = {k: os.environ.get(k) for k in
                          ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA", "GITHUB_REF")}
    (output / "environment-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    hashes = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(output)}"
              for p in sorted(output.rglob("*")) if p.is_file() and p.name != "file-manifest.sha256"]
    (output / "file-manifest.sha256").write_text("\n".join(hashes) + "\n")


if __name__ == "__main__":
    main()
