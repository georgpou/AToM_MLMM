"""Independent lightweight execution probes. No Psi4 or learned model launches.

Use reviewed-source-initial by default so repairs cannot alter initial evidence.
Every stand-in record is marked as synthetic by its enclosing audit directory.
"""
from pathlib import Path
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]
PLAN = REPO / 'fixtures/chemical_reference_v3'
MATRIX = REPO / 'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
PILOT = 'ethanol-methanol-d3-r0--full-parent'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


FAKE = '''
import json, os, signal, sys, time
from pathlib import Path
order = json.loads(Path(sys.argv[-1]).read_text())
geometry = order['structure']; record = Path(order['output'])
mode = os.environ.get('G07_INDEPENDENT_MODE', '')
if mode == 'stubborn':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    Path(os.environ['G07_INDEPENDENT_STARTED']).write_text(str(os.getpid()))
    time.sleep(25)
elif mode == 'wait':
    time.sleep(25)
data = dict(status='computed', name=order['job_name'], source_input_sha256=order['source_input_sha256'],
    method='wb97m-d3bj/def2-tzvppd', psi4_version='1.10.2', formal_charge=0, multiplicity=1,
    positions_angstrom=geometry['positions_angstrom'], atomic_numbers=geometry['atomic_numbers'],
    energy_hartree=-1., gradient_hartree_bohr=[[0.,0.,0.] for _ in geometry['atomic_numbers']],
    quantum_energy_variables={'DISPERSION CORRECTION ENERGY':-.001,'DFT VV10 ENERGY':0.},
    basis_file_sha256=order['basis_file_sha256'], settings=order['settings'], network_denied=True,
    wall_seconds=.001, threads=2, memory=order['runtime_memory'])
record.write_text(json.dumps(data))
if mode != 'no_log':
    record.with_suffix('.psi4.txt').write_text('SCF has converged.\\n' if mode != 'no_convergence' else 'SCF iteration incomplete.\\n')
if mode == 'computed_fail':
    sys.exit(23)
'''


def group_members(group):
    result = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path/'stat').read_text().rsplit(')', 1)[1].split()
            if fields[0] != 'Z' and int(fields[2]) == group:
                result.append(int(path.name))
        except (OSError, ValueError, IndexError):
            pass
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=EVIDENCE/'reviewed-source-initial')
    parser.add_argument('--label', default='initial')
    args = parser.parse_args()
    root = EVIDENCE/('probes-'+args.label)
    root.mkdir()
    approval_source = args.source_root/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
    if not approval_source.exists():
        approval_source = REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
    approved = json.loads(approval_source.read_text())
    runner = args.source_root/'tools/resume_joint_quantum.py'
    exe = root/'synthetic-reference/bin/python'
    exe.parent.mkdir(parents=True)
    exe.write_text('#!'+sys.executable+'\n'+FAKE)
    exe.chmod(0o755)
    for index, line in enumerate((PLAN/'reference-explicit.lock').read_text().splitlines()):
        if line.startswith('https://'):
            url, digest = line.rsplit('#', 1)
            write(exe.parents[1]/'conda-meta'/f'{index}.json', dict(url=url, sha256=digest))
    environment = {**os.environ, 'PYTHONPATH':str(REPO/'src')}
    outcomes = {'utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'source_hashes':{
        str(path.relative_to(args.source_root)):sha(path) for path in args.source_root.glob('tools/*.py')},
        'notice':'SYNTHETIC EXECUTION SOFTWARE EVIDENCE ONLY; no chemical results', 'checks':{}}

    def bind(name):
        case = root/name; case.mkdir()
        output = case/'output'; approval = case/'authorization.json'
        write(approval, {**approved, 'attempt_path':str(output)})
        return output, approval

    def command(output, approval, extras=()):
        return [sys.executable, str(runner), '--plan-root',str(PLAN), '--approval',str(approval),
            '--matrix',str(MATRIX), '--output',str(output), '--reference-python',str(exe), *extras]

    def run(output, approval, mode='', extras=()):
        result = subprocess.run(command(output, approval, extras), capture_output=True, text=True,
            env={**environment, 'G07_INDEPENDENT_MODE':mode}, timeout=40)
        with (output.parent/'commands.jsonl').open('a') as stream:
            stream.write(json.dumps(dict(command=command(output, approval, extras), mode=mode,
                exit=result.returncode, stdout=result.stdout, stderr=result.stderr))+'\n')
        return result

    # A fresh authorization copy is accepted despite selecting another ledger.
    out1, auth1 = bind('rebound-depleted-ledger')
    first = run(out1,auth1,'wait',['--wall-limit-seconds','1.2'])
    state1 = json.loads((out1/'progress.json').read_text())
    out2, auth2 = bind('rebound-new-ledger')
    second = run(out2,auth2)
    state2 = json.loads((out2/'progress.json').read_text())
    outcomes['checks']['authorization_rebinding_budget_reset'] = dict(
        first_exit=first.returncode, first_debit=state1['wall_seconds_debited'],
        first_stop=state1['sessions'][-1]['stop_reason'], second_exit=second.returncode,
        second_pilot_promoted=PILOT in state2['record_hashes'], second_debit=state2['wall_seconds_debited'],
        copied_authorizations_have_distinct_paths=True, copied_authorization_lease_paths=[str(auth1.parent/'queue-lease.lock'),str(auth2.parent/'queue-lease.lock')],
        unsafe_behavior_observed=PILOT in state2['record_hashes'])

    # Read-only reporting must not be confused with actual cumulative state.
    checked = run(out1,auth1,'',['--check-resume'])
    outcomes['checks']['read_only_check_ignores_existing_debit'] = dict(exit=checked.returncode,
        reported=json.loads(checked.stdout), actual_debit=state1['wall_seconds_debited'])

    # Known nonzero worker exit, even with a complete computed record.
    out, auth = bind('failed-computed-record')
    failed = run(out,auth,'computed_fail')
    failed_state = json.loads((out/'progress.json').read_text())
    receipt_path = next(out.glob('jobs/*/attempt-*/receipt.json')); original=receipt_path.read_bytes()
    retry = run(out,auth)
    retried = json.loads((out/'progress.json').read_text())
    outcomes['checks']['failed_exit_and_budget_carryover'] = dict(first_exit=failed.returncode,
        failed_records=len(failed_state['record_hashes']), failed_receipt=json.loads(original),
        retry_exit=retry.returncode,retry_records=len(retried['record_hashes']),
        budget_increased=retried['wall_seconds_debited']>failed_state['wall_seconds_debited'],
        original_receipt_unchanged=receipt_path.read_bytes()==original)

    for mode in ('no_log','no_convergence'):
        out,auth=bind(mode);result=run(out,auth,mode)
        state=json.loads((out/'progress.json').read_text())
        receipt=json.loads(next(out.glob('jobs/*/attempt-*/receipt.json')).read_text())
        outcomes['checks'][mode] = dict(exit=result.returncode,promoted=len(state['record_hashes']),validation_error=receipt.get('validation_error'))

    # Delete source convergence evidence after durable checkpoint admission.
    source_log=next(out2.glob('jobs/*/attempt-*/record.psi4.txt'))
    original_log=source_log.read_bytes();write(source_log.parent/'audit-original-log.json',{'text':original_log.decode(),'sha256':sha(source_log)})
    source_log.unlink()
    resumed=run(out2,auth2)
    state2_missing=json.loads((out2/'progress.json').read_text())
    outcomes['checks']['missing_checkpointed_convergence_log'] = dict(exit=resumed.returncode,
        source_log_exists=source_log.exists(), still_promoted=PILOT in state2_missing['record_hashes'],
        stop_reason=state2_missing['sessions'][-1].get('stop_reason'),
        unsafe_behavior_observed=resumed.returncode==1 and PILOT in state2_missing['record_hashes'])

    # Crash with a TERM-resistant stand-in; inspect retained flock and cleanup.
    out,auth=bind('coordinator-loss');started=out.parent/'worker-started.pid'
    crash=subprocess.Popen(command(out,auth),env={**environment,'G07_INDEPENDENT_MODE':'stubborn','G07_INDEPENDENT_STARTED':str(started)},
        stdout=(out.parent/'coordinator.txt').open('w'),stderr=subprocess.STDOUT)
    deadline=time.monotonic()+15
    while not started.exists() and crash.poll() is None and time.monotonic()<deadline:
        time.sleep(.02)
    assert started.exists(), 'stand-in worker never started'
    state=json.loads((out/'progress.json').read_text());group=state['sessions'][-1]['active_worker']['pid']
    crash.kill();crash.wait(timeout=5)
    lease=auth.parent/'queue-lease.lock';retained=False
    with lease.open('a') as stream:
        try:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
            fcntl.flock(stream,fcntl.LOCK_UN)
        except BlockingIOError:
            retained=True
    deadline=time.monotonic()+12
    while group_members(group) and time.monotonic()<deadline:
        time.sleep(.03)
    remaining=group_members(group)
    if remaining:
        os.killpg(group,signal.SIGKILL)
    resumed=run(out,auth)
    resumed_state=json.loads((out/'progress.json').read_text())
    outcomes['checks']['coordinator_loss_retained_lease_and_recovery'] = dict(
        coordinator_exit=crash.returncode,lease_retained_after_coordinator_loss=retained,
        remaining_group=remaining,resume_exit=resumed.returncode,
        interrupted_session_status=resumed_state['sessions'][0]['status'],
        interrupted_seconds=resumed_state['sessions'][0]['wall_seconds'],
        total_debit=resumed_state['wall_seconds_debited'],pilot_promoted=PILOT in resumed_state['record_hashes'])

    write(EVIDENCE/('independent-probes-'+args.label+'.json'),outcomes)
    print(json.dumps({key:value for key,value in outcomes['checks'].items()
        if key not in ('failed_exit_and_budget_carryover',)},indent=2))


if __name__=='__main__':
    main()
