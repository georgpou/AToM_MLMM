#!/usr/bin/env python3
"""Plan, set up, prepare, or run the pinned FKBP benchmark with AToM."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def main():
    from atm_mlmm.benchmark_workflow import MODES, plan_jobs, run_stage
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['plan', 'setup', 'prepare', 'run'])
    parser.add_argument('--manifest', type=Path, default=ROOT / 'benchmarks/fkbp/benchmark.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/fkbp')
    parser.add_argument('--ligand', default='all')
    parser.add_argument('--mode', choices=MODES, default='cavity')
    parser.add_argument('--platform', choices=['CPU', 'Reference'], default='CPU',
                        help='platform recorded at setup; later stages use stored settings')
    parser.add_argument('--smoke', action='store_true', help='short explicit preparation/sampling settings at setup')
    parser.add_argument('--nodefile', type=Path, help='explicit local AToM worker allocation for run')
    args = parser.parse_args()
    if args.smoke and args.stage != 'setup':
        parser.error('--smoke must be recorded at setup; prepare/run use the saved settings')
    try:
        jobs = plan_jobs(args.manifest, args.output, mode=args.mode)
        if args.ligand != 'all':
            jobs = [job for job in jobs if job['ligand_id'] == args.ligand]
            if not jobs:
                raise ValueError(f'unknown ligand: {args.ligand}')
        if args.stage == 'plan':
            print(json.dumps(jobs, indent=2))
        else:
            for job in jobs:
                result = run_stage(args.manifest, args.output, job['ligand_id'], args.mode,
                                   args.stage, smoke=args.smoke, platform=args.platform,
                                   nodefile=args.nodefile)
                print(json.dumps(result, indent=2))
        return 0
    except (ValueError, FileExistsError, ImportError) as exc:
        parser.exit(2, f'benchmark: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
