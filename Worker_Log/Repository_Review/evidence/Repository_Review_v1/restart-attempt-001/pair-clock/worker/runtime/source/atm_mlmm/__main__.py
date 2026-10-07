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
    exchange = commands.add_parser('exchange',help='bounded transactional two-worker exchange from a prepared run')
    exchange.add_argument('prepared_run',type=Path)
    exchange.add_argument('--output',type=Path,required=True)
    exchange.add_argument('--rounds',type=int,required=True)
    exchange.add_argument('--steps-per-round',type=int,required=True)
    exchange.add_argument('--seed',type=int,required=True)
    exchange.add_argument('--trusted',action='store_true')
    continuation = commands.add_parser('resume-exchange',help='continue verified complete exchange rounds')
    continuation.add_argument('directory',type=Path)
    continuation.add_argument('--trusted',action='store_true')
    continuation.add_argument('--recover-pending',action='store_true',
        help='preserve incomplete trees in failure archives, then rollback/replay from the last committed boundary')
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
        elif args.command == 'resume':
            result = resume_run(args.directory,trusted=args.trusted)
        elif args.command == 'exchange':
            from .exchange import run_exchange
            result = run_exchange(args.prepared_run,args.output,rounds=args.rounds,
                steps_per_round=args.steps_per_round,seed=args.seed,trusted=args.trusted)
        else:
            from .exchange import resume_exchange
            result = resume_exchange(args.directory,trusted=args.trusted,recover_pending=args.recover_pending)
    except (ValueError,OSError) as error:
        print(f'{type(error).__name__}: {error}',file=sys.stderr)
        for note in getattr(error,'__notes__',()):
            print(note,file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
