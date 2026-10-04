"""Small common command-line entry point; imports scientific code on demand."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(prog='python -m atm_mlmm')
    commands = parser.add_subparsers(dest='command',required=True)
    check = commands.add_parser('check',help='validate declarative inputs without executing artifacts')
    check.add_argument('configuration',type=Path)
    run = commands.add_parser('run',help='bounded fixed-window engine preflight')
    run.add_argument('configuration',type=Path)
    run.add_argument('--output',type=Path,required=True)
    run.add_argument('--trusted',action='store_true',help='authorize loading the supplied executable System/ML artifacts')
    resume = commands.add_parser('resume',help='continue the verified committed prefix on the identical profile')
    resume.add_argument('directory',type=Path)
    resume.add_argument('--trusted',action='store_true')
    args = parser.parse_args()
    from .workflow import load_configuration,run_configuration,resume_run
    try:
        if args.command == 'check':
            config = load_configuration(args.configuration)
            result = {'status':'valid','real_atoms':len(config.snapshot.real_atom_ids),
                      'runtime_identity':config.runtime.content_identity,
                      'states':[s.state_id for s in config.schedule.states]}
        elif args.command == 'run':
            result = run_configuration(args.configuration,args.output,trusted=args.trusted)
        else:
            result = resume_run(args.directory,trusted=args.trusted)
    except (ValueError,OSError) as error:
        print(f'{type(error).__name__}: {error}',file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
