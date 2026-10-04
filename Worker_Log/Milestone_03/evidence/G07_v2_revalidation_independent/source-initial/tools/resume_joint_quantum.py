"""Execute only the frozen G07 matrix under its separate user authorization.

G05's scientific approval and records stay immutable. G07 has its own cumulative
24-hour ledger, one-hour pilot ceiling, and measured-assessment continuation.
All launches use the maintained durable coordinator and leased group supervisor.
"""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import sys

from generate_neutral_quantum import digest, validate_plan
import resume_neutral_quantum as recovery

PILOT = 'ethanol-methanol-d3-r0--full-parent'
APPROVAL_PATH = Path(__file__).resolve().parents[1]/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
APPROVAL_SHA256 = 'fb20e06a6179df03ef6ced63cc09a4d1bdc74e024fc08cb5c5e301bd1079d216'
REJECTED_PILOT_RECEIPT_SHA256 = 'b42dd4aff42a8e5e52f3ab00a0e857dd58d8de6bdcc1a819becbce5f885a5f1f'


def validate_authorization(root, approval_path, matrix_path):
    if Path(approval_path).resolve() != APPROVAL_PATH or digest(approval_path) != APPROVAL_SHA256:
        raise ValueError('G07 execution requires the exact recorded authorization; copied or altered approval rejected')
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
        converged = ('SCF has converged.' in text
                     or 'Energy and wave function converged.' in text)
        if not converged or 'SCF failed to converge' in text:
            raise ValueError('explicit SCF convergence is absent from the saved Psi4 log')
        recovery.sync_file(log)
    else:
        raise ValueError('saved SCF convergence log is missing')
    return record


def revalidate_pilot(output, root, approval, matrix, reference_python):
    """Correct one hash-exact parser rejection, preserving its original receipt.

    This creates a validation-only copy, never a worker launch or fresh budget.
    It cannot reopen failed workers, interrupted attempts or other rejections.
    """
    if output.resolve() != Path(approval['attempt_path']).resolve():
        raise ValueError('revalidation requires the canonical G07 output ledger')
    recovery.validate_environment(reference_python, root)
    with (output.parent/'queue-lease.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another coordinator holds this attempt lock')
        state = json.loads((output/'progress.json').read_text())
        expected = dict(approval_sha256=digest(APPROVAL_PATH),
                        input_manifest_sha256=approval['input_manifest_sha256'],
                        reference_settings_sha256=approval['reference_settings_sha256'], history={})
        if state['identity'] != expected or any(s['status'] == 'running' for s in state['sessions']):
            raise ValueError('revalidation ledger identity or closed-session status differs')
        if recovery.attempt_processes(output):
            raise ValueError('old quantum worker remains active; refuse revalidation')
        parent = output/'jobs'/PILOT
        source = parent/'attempt-0001'
        original_path = source/'receipt.json'
        if digest(original_path) != REJECTED_PILOT_RECEIPT_SHA256:
            raise ValueError('revalidation requires the exact original parser rejection receipt')
        receipt = recovery.completion_receipt(source/'record.json', PILOT)
        error = "ValueError('explicit SCF convergence is absent from the saved Psi4 log')"
        if (receipt['exit'] != 0 or receipt.get('reason') is not None
                or receipt.get('validation_error') != error
                or receipt.get('group_cleanup_verified') is not True):
            raise ValueError('only the completed parser-rejected pilot can be revalidated')
        identity = json.loads((source/'worker-identity.json').read_text())
        if recovery.group_members(identity['pid']):
            raise ValueError('original supervised process group remains active')
        settings = json.loads((root/'reference-settings.json').read_text())
        order = joint_queue(matrix, settings)[PILOT]
        validate_joint_record(source/'record.json', order, receipt['record_sha256'])
        if 'Energy and wave function converged.' not in (source/'record.psi4.txt').read_text():
            raise ValueError('actual Psi4 convergence message is absent')
        target = parent/'attempt-0002'
        if target.exists():
            saved = recovery.completion_receipt(target/'record.json', PILOT)
            if (saved.get('completion_kind') != 'validation_only_correction'
                    or saved.get('original_receipt_sha256') != REJECTED_PILOT_RECEIPT_SHA256
                    or not recovery.admitted(saved)):
                raise ValueError('existing revalidation evidence differs')
            validate_joint_record(target/'record.json', order, receipt['record_sha256'])
            return target/'receipt.json'
        staging = parent/'.revalidation-staging-v1'
        recovery.durable_mkdir(staging)  # Existing partial staging is preserved and rejected.
        copied = {}
        for path in sorted(source.iterdir()):
            if not path.is_file() or path.is_symlink():
                raise ValueError('unexpected original attempt entry: ' + str(path))
            name = 'original-receipt.json' if path.name == 'receipt.json' else path.name
            with (staging/name).open('xb') as stream:
                stream.write(path.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            copied[name] = digest(staging/name)
        recovery.sync_directory(staging)
        correction = dict(kind='validation_only_correction', revalidated_utc=recovery.utc(),
            original_attempt=str(source), original_receipt_sha256=REJECTED_PILOT_RECEIPT_SHA256,
            original_validation_error=receipt['validation_error'], copied_file_sha256=copied,
            validator_source_sha256=digest(Path(__file__)),
            note='No QM launch. Order, launch, worker identities, samples and wall time are historical copies. '
                 'Psi4 1.10.2 explicitly reports Energy and wave function converged.; strict validation passes. '
                 'Original rejection remains immutable; cumulative quantum debit is unchanged.')
        recovery.exclusive_dump(staging/'revalidation.json', correction)
        receipt = dict(receipt)
        receipt.pop('validation_error')
        receipt.update(completion_kind='validation_only_correction',
                       original_receipt_sha256=REJECTED_PILOT_RECEIPT_SHA256,
                       original_receipt_path=str(original_path), revalidated_utc=correction['revalidated_utc'])
        receipt['diagnostic_sha256'] = dict(copied, **{'revalidation.json':digest(staging/'revalidation.json')})
        recovery.exclusive_dump(staging/'receipt.json', receipt)
        os.rename(staging, target)
        recovery.sync_directory(parent)
        return target/'receipt.json'


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
                diagnostic_suffixes=('.psi4.txt', '.psi4.log'),
                stop_after_job=None if continuation else PILOT)


def pilot_evidence(output):
    state = json.loads((output/'progress.json').read_text())
    pilot = state['provenance'].get(PILOT)
    if pilot is None or PILOT not in state['record_hashes']:
        raise ValueError('assessment requires the completed pilot')
    source = Path(pilot['source'])
    receipt = recovery.completion_receipt(source, PILOT)
    if not recovery.admitted(receipt) or receipt is None or not receipt.get('group_cleanup_verified'):
        raise ValueError('pilot requires its successful completion receipt')
    samples_path = source.with_name('resources.jsonl')
    samples = [json.loads(line) for line in samples_path.read_text().splitlines()]
    if not samples or any(s.get('job_name') != PILOT for s in samples):
        raise ValueError('measured pilot samples are absent or have wrong identities')
    return dict(pilot_record_sha256=state['record_hashes'][PILOT],
        pilot_receipt_sha256=digest(source.with_name('receipt.json')),
        pilot_resources_sha256=digest(samples_path),
        pilot_wall_seconds=receipt['wall_seconds'],
        pilot_rss_peak_bytes=receipt['sampled_rss_peak_bytes'],
        pilot_scratch_peak_bytes=max(s.get('scratch_bytes', 0) for s in samples))


def validate_assessment(path, output, approval, matrix=None):
    if path is None:
        raise ValueError('continuation requires a measured pilot assessment')
    assessment = json.loads(Path(path).read_text())
    state = json.loads((output/'progress.json').read_text())
    measured = pilot_evidence(output)
    if (assessment.get('continue_authorized') is not True
            or assessment.get('matrix_sha256') != approval['matrix_sha256']
            or any(assessment.get(key) != value for key, value in measured.items())):
        raise ValueError('measured pilot assessment identities or values differ')
    seconds = assessment['projected_remaining_worker_seconds']
    rss = assessment['projected_max_rss_bytes']
    scratch = assessment['projected_scratch_bytes']
    if any(not math.isfinite(v) or v < 0 for v in (seconds, rss, scratch)):
        raise ValueError('invalid measured pilot projections')
    if matrix is None:
        matrix = json.loads((Path(__file__).resolve().parents[1]/approval['matrix_path']).read_text())
    pilot_size = sum(next(j for j in matrix['new_jobs'] if j['name'] == PILOT)['atomic_numbers'])
    remaining = [j for j in matrix['new_jobs'] if j['name'] not in state['record_hashes']]
    ratios = [sum(j['atomic_numbers']) / pilot_size for j in remaining]
    # Screening estimates, not scientific settings or guaranteed completion:
    # twice the measured wall time scaled cubically by composition size, and
    # at least the measured RSS and quadratically scaled scratch peak.
    time_floor = 2 * measured['pilot_wall_seconds'] * sum(r**3 for r in ratios)
    scratch_floor = measured['pilot_scratch_peak_bytes'] * max([1., *ratios])**2
    if seconds < time_floor or rss < measured['pilot_rss_peak_bytes'] or scratch < scratch_floor:
        raise ValueError('measured pilot projections are below the screening envelope')
    policy = execution_policy(approval, True)
    if (seconds > 86400 - state['wall_seconds_debited'] or rss > policy['rss_max_bytes']
            or scratch + policy['disk_min_bytes'] > recovery.measurements()['disk_free_bytes']):
        raise ValueError('pilot projections exceed the remaining resource/budget envelope')


def run(args):
    root = Path(args.plan_root).resolve()
    matrix_path = Path(args.matrix).resolve()
    approval, matrix = validate_authorization(root, args.approval, matrix_path)
    output = Path(args.output).resolve()
    if getattr(args, 'revalidate_pilot', False):
        if args.check_resume or args.continue_batch:
            raise ValueError('validation-only correction cannot be combined with preflight or batch continuation')
        revalidate_pilot(output, root, approval, matrix, args.reference_python)
    if output != Path(approval['attempt_path']).resolve():
        raise ValueError('attempt path differs from the separately bound G07 budget ledger')
    if args.memory_gib != 3:
        raise ValueError('G07 execution requires exactly 3 GiB internal allocation')
    if args.continue_batch:
        validate_assessment(args.pilot_assessment, output, approval, matrix)
    policy = execution_policy(approval, args.continue_batch)
    # One canonical lease is inherited by the supervisor, even across a crash.
    policy['queue_lease_path'] = output.parent/'queue-lease.lock'
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
    parser.add_argument('--revalidate-pilot', action='store_true',
                        help='correct the exact saved pilot convergence-parser rejection without new QM')
    try:
        sys.exit(run(parser.parse_args()))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print('G07 execution rejected:', error, file=sys.stderr)
        sys.exit(2)
