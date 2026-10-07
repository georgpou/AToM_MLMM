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
    multi = commands.add_parser('exchange-multistate',
        help='run the existing bounded serial 3–8-state controller from an explicit connected-pair plan')
    multi.add_argument('prepared_run',type=Path)
    multi.add_argument('plan',type=Path,help='JSON: state_ids, full connected state_pairs, boundaries, steps_per_boundary, seed')
    multi.add_argument('--output',type=Path,required=True)
    multi.add_argument('--trusted',action='store_true',help='authorize loading sealed System/ML artifacts')
    resume_multi = commands.add_parser('resume-multistate',
        help='resume the verified multistate prefix; pending recovery is explicit')
    resume_multi.add_argument('directory',type=Path)
    resume_multi.add_argument('--trusted',action='store_true')
    resume_multi.add_argument('--recover-pending',action='store_true',
        help='archive pending bytes, then rollback/replay from the last committed boundary')
    analysis = commands.add_parser('analyze',
        help='analyze declared exchange records with explicit thermodynamics, resampling and optional joint covariance')
    analysis.add_argument('input',type=Path,
        help='JSON with serialized histories, thermodynamics, resampling, estimator and optional joint covariance')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            from .workflow import load_configuration
            config = load_configuration(args.configuration)
            result = {'status':'valid','real_atoms':len(config.snapshot.real_atom_ids),
                      'runtime_identity':config.runtime.content_identity,
                      'states':[s.state_id for s in config.schedule.states]}
        elif args.command == 'run':
            from .workflow import run_configuration
            result = run_configuration(args.configuration,args.output,trusted=args.trusted)
        elif args.command == 'resume':
            from .workflow import resume_run
            result = resume_run(args.directory,trusted=args.trusted)
        elif args.command == 'exchange':
            from .exchange import run_exchange
            result = run_exchange(args.prepared_run,args.output,rounds=args.rounds,
                steps_per_round=args.steps_per_round,seed=args.seed,trusted=args.trusted)
        elif args.command == 'resume-exchange':
            from .exchange import resume_exchange
            result = resume_exchange(args.directory,trusted=args.trusted,recover_pending=args.recover_pending)
        elif args.command == 'exchange-multistate':
            plan = json.loads(args.plan.read_text())
            required = {'state_ids','state_pairs','boundaries','steps_per_boundary','seed'}
            if not isinstance(plan,dict) or set(plan) != required:
                raise ValueError(f'multistate plan must contain exactly {sorted(required)}')
            from .exchange import run_multistate_exchange
            result = run_multistate_exchange(args.prepared_run,args.output,
                state_ids=tuple(plan['state_ids']),
                state_pairs=tuple(tuple(pair) for pair in plan['state_pairs']),
                boundaries=plan['boundaries'],steps_per_boundary=plan['steps_per_boundary'],
                seed=plan['seed'],trusted=args.trusted)
        elif args.command == 'resume-multistate':
            from .exchange import resume_multistate_exchange
            result = resume_multistate_exchange(args.directory,trusted=args.trusted,
                recover_pending=args.recover_pending)
        else:
            document = json.loads(args.input.read_text())
            required = {'histories','thermodynamics','resampling','estimator','joint_covariance_kj2_mol2'}
            if (not isinstance(document,dict) or not {'histories','thermodynamics','resampling'} <= set(document)
                    or set(document) - required):
                raise ValueError(f'analysis input requires serialized histories, thermodynamics, resampling; optional fields are {sorted(required-{"histories","thermodynamics","resampling"})}')
            if not isinstance(document['histories'],list) or not document['histories']:
                raise ValueError('analysis histories must be a nonempty list of serialized records')
            from .schema import from_json,to_json
            from .exchange_analysis import analyze_exchange
            histories=tuple(from_json(json.dumps(item)) for item in document['histories'])
            thermodynamics=from_json(json.dumps(document['thermodynamics']))
            resampling=from_json(json.dumps(document['resampling']))
            result=analyze_exchange(histories,thermodynamics,resampling=resampling,
                estimator=document.get('estimator','pymbar'),
                joint_covariance_kj2_mol2=document.get('joint_covariance_kj2_mol2'))
            print(json.dumps({'scope':'explicit exchange analysis; final binding result remains subject to library admission',
                              'analysis_result':json.loads(to_json(result))},indent=2,allow_nan=False))
            return 0
    except (ValueError,OSError) as error:
        print(f'{type(error).__name__}: {error}',file=sys.stderr)
        for note in getattr(error,'__notes__',()):
            print(note,file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
