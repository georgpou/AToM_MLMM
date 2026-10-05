#!/usr/bin/env python
"""CPU reference export or separate experimental TPU component probe."""
import argparse
import json
from pathlib import Path
from atm_mlmm.tpu_experiment import export_cpu_reference,run_tpu

parser=argparse.ArgumentParser()
commands=parser.add_subparsers(dest='command',required=True)
cpu=commands.add_parser('cpu-reference'); cpu.add_argument('--output',type=Path,required=True)
tpu=commands.add_parser('tpu'); tpu.add_argument('reference',type=Path)
tpu.add_argument('--reference-sha256',required=True); tpu.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
if args.command=='cpu-reference': print(json.dumps(export_cpu_reference(args.output),indent=2))
else:
    status=run_tpu(args.reference,args.reference_sha256,args.output)
    print(status)
    raise SystemExit(0 if status=='component-numerical-pass' else 2)
