"""Audit-only command recorder: preserve raw bytes and the child's exit status."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--cwd", type=Path, default=Path.cwd())
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command
if command and command[0] == "--":
    command = command[1:]
if not command:
    parser.error("a command is required")
folder = Path(__file__).resolve().parent
record = folder / (args.name + ".json")
output = folder / (args.name + ".log")
if record.exists() or output.exists():
    parser.error("evidence name already used")
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with output.open("wb") as stream:
    child = subprocess.run(command, cwd=args.cwd, stdout=stream, stderr=subprocess.STDOUT)
record.write_text(json.dumps(dict(command=command, cwd=str(args.cwd.resolve()),
                                 started=started,
                                 finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                 exit_code=child.returncode, raw_output=output.name), indent=2) + "\n")
print(json.dumps(dict(name=args.name, exit_code=child.returncode, output=str(output))), flush=True)
sys.exit(child.returncode)
