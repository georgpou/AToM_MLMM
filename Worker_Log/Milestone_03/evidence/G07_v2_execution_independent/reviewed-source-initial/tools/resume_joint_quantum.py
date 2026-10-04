"""Execute only the frozen G07 matrix under its separate user authorization.

G05's scientific approval and records stay immutable. G07 has its own cumulative
24-hour ledger, one-hour pilot ceiling, and measured-assessment continuation.
All launches use the maintained durable coordinator and leased group supervisor.
"""
import argparse
import json
import math
from pathlib import Path
import sys

from generate_neutral_quantum import digest, validate_plan
import resume_neutral_quantum as recovery

PILOT = 'ethanol-methanol-d3-r0--full-parent'


def validate_authorization(root, approval_path, matrix_path):
    approval = json.loads(Path(approval_path).read_text())
    if approval.get('user_agreed') is not True or approval.get('pilot_job') != PILOT:
        raise ValueError('G07 user authorization and exact pilot are required')
    repository = root.parents[1]
    expected = {'matrix_sha256': matrix_path,
                'input_manifest_sha256': root/'input-manifest.json',
                'reference_settings_sha256': root/'reference-settings.json',
                'reference_lock_sha256': root/'reference-explicit.lock',
                'scientific_decision_sha256': repository/approval['scientific_decision_path'],
                'numerical_audit_sha256': repository/approval['numerical_audit_path']}
    if any(approval.get(key) != digest(path) for key, path in expected.items()):
        raise ValueError('G07 authorization differs from frozen input/approval identities')
    decision, _ = validate_plan(root, expected['scientific_decision_sha256'])
    if digest(repository/decision['design_audit_path']) != decision['design_audit_sha256']:
        raise ValueError('inherited scientific audit identity differs')
    cap = approval['approved_resource_cap']
    required = dict(wall_hours=24, pilot_wall_seconds=3600, cpu_threads=2,
                    psi4_memory='3 GiB', process_group_rss_max_bytes=6*2**30,
                    disk_free_min_bytes=5*2**30)
    if cap != required:
        raise ValueError('G07 resource limits differ from the explicit user authorization')
    from atm_mlmm.joint_reference import quantum_job_matrix
    matrix = json.loads(matrix_path.read_text())
    if matrix != json.loads(json.dumps(quantum_job_matrix(root))):
        raise ValueError('matrix differs from the exact frozen scientific queue')
    return approval, matrix


def joint_queue(matrix, settings):
    numbers = {1:'H', 6:'C', 7:'N', 8:'O'}
    orders = {}
    jobs = sorted(matrix['new_jobs'], key=lambda j: (j['name'] != PILOT, j['name']))
    for job in jobs:
        if (job['formal_charge'] != 0 or job['multiplicity'] != 1 or job['units'] != 'angstrom'
                or job['method'] != 'wb97m-d3bj/def2-tzvppd'):
            raise ValueError('unsupported frozen G07 state or convention')
        structure = dict(job, elements=[numbers[n] for n in job['atomic_numbers']])
        orders[job['name']] = dict(structure=structure, source_input_sha256=job['source_input_sha256'],
            settings=settings['settings'], basis_file_sha256=settings['basis_file_sha256'],
            job_name=job['name'])
    return orders


def validate_joint_record(path, order, expected_sha=None):
    record = recovery.validate_record(path, order, expected_sha)
    if record['name'] != order['job_name'] or record['memory'] != '3 GiB':
        raise ValueError('G07 job identity or runtime allocation differs')
    log = Path(path).with_suffix('.psi4.txt')
    if log.exists():
        text = log.read_text()
        if 'SCF has converged.' not in text or 'SCF failed to converge' in text:
            raise ValueError('explicit SCF convergence is absent from the saved Psi4 log')
    elif expected_sha is None:
        raise ValueError('saved SCF convergence log is missing')
    return record


def execution_policy(approval, continuation):
    measurements = recovery.measurements()
    limit = measurements.get('memory.max')
    rss = 6*2**30
    pressure = 7.5*2**30
    if isinstance(limit, int):
        rss = min(rss, limit - 2*2**30)
        pressure = min(pressure, limit - 512*2**20)
    return dict(wall_hours=24, pilot_job=PILOT, pilot_wall_seconds=3600,
                rss_max_bytes=rss, pressure_max_bytes=pressure, disk_min_bytes=5*2**30,
                require_receipt=True, stop_on_failure=True,
                stop_after_job=None if continuation else PILOT)


def validate_assessment(path, output, approval):
    if path is None:
        raise ValueError('continuation requires a measured pilot assessment')
    assessment = json.loads(Path(path).read_text())
    state = json.loads((output/'progress.json').read_text())
    pilot = state['provenance'].get(PILOT)
    if pilot is None or PILOT not in state['record_hashes']:
        raise ValueError('assessment requires the completed pilot')
    receipt_path = Path(pilot['receipt'])
    receipt = json.loads(receipt_path.read_text())
    if (assessment.get('continue_authorized') is not True
            or assessment.get('matrix_sha256') != approval['matrix_sha256']
            or assessment.get('pilot_record_sha256') != state['record_hashes'][PILOT]
            or assessment.get('pilot_receipt_sha256') != digest(receipt_path)
            or not recovery.admitted(receipt) or not receipt.get('group_cleanup_verified')):
        raise ValueError('pilot assessment/receipt identity or success differs')
    seconds = assessment['projected_remaining_worker_seconds']
    rss = assessment['projected_max_rss_bytes']
    scratch = assessment['projected_scratch_bytes']
    if any(not math.isfinite(v) or v < 0 for v in (seconds, rss, scratch)):
        raise ValueError('invalid measured pilot projections')
    policy = execution_policy(approval, True)
    if (seconds > 86400 - state['wall_seconds_debited'] or rss > policy['rss_max_bytes']
            or scratch + policy['disk_min_bytes'] > recovery.measurements()['disk_free_bytes']):
        raise ValueError('pilot projections exceed the remaining resource/budget envelope')


def run(args):
    root = Path(args.plan_root).resolve()
    matrix_path = Path(args.matrix).resolve()
    approval, matrix = validate_authorization(root, args.approval, matrix_path)
    output = Path(args.output).resolve()
    if output != Path(approval['attempt_path']).resolve():
        raise ValueError('attempt path differs from the separately bound G07 budget ledger')
    if args.memory_gib != 3:
        raise ValueError('G07 execution requires exactly 3 GiB internal allocation')
    if args.continue_batch:
        validate_assessment(args.pilot_assessment, output, approval)
    policy = execution_policy(approval, args.continue_batch)
    # One canonical lease is inherited by the supervisor, even across a crash.
    policy['queue_lease_path'] = Path(args.approval).resolve().parent/'queue-lease.lock'
    args.resume_from = args.stop_state = args.prior_launch = None
    return recovery.run(args,
        plan_validator=lambda _root, _path: (approval, matrix),
        queue_builder=lambda _root, settings: joint_queue(matrix, settings),
        policy=policy, record_validator=validate_joint_record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan-root', 'approval', 'matrix', 'output'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--reference-python')
    parser.add_argument('--check-resume', action='store_true')
    parser.add_argument('--memory-gib', type=float, default=3.)
    parser.add_argument('--wall-limit-seconds', type=float)
    parser.add_argument('--continue-batch', action='store_true')
    parser.add_argument('--pilot-assessment')
    try:
        sys.exit(run(parser.parse_args()))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print('G07 execution rejected:', error, file=sys.stderr)
        sys.exit(2)
