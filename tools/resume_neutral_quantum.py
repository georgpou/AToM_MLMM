"""Recover the frozen quantum queue without overwriting earlier attempts.

No learned model is imported. --check-resume is read-only. Each actual worker
gets a private scratch directory, immutable order/log/receipt, a process group,
and the remaining cumulative deadline. progress.json is atomically checkpointed
each second. An interrupted session is conservatively charged until recovery.
"""
import argparse
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from generate_neutral_quantum import digest, validate_plan


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_dump(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def exclusive_dump(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def queue(root, settings):
    paths = sorted((root / 'structures').glob('*.json'))
    paths += sorted((root / 'quadrature_controls').glob('*.json'))
    entries = [(p, False) for p in paths]
    entries += [(root / 'structures' / (name + '.json'), True)
                for name in settings['convergence_checks']['rows']]
    result = {}
    for path, fine in entries:
        data = json.loads(path.read_text())
        name = data['name'] + ('-fine-grid' if fine else '')
        if name != path.stem + ('-fine-grid' if fine else '') or name in result or Path(name).name != name:
            raise ValueError('invalid or duplicate frozen queue name')
        options = dict(settings['settings'])
        if fine:
            options.update(settings['convergence_checks']['settings'])
        result[name] = dict(structure=data, source_input_sha256=digest(path), settings=options,
                            basis_file_sha256=settings['basis_file_sha256'], job_name=name)
    return result


def memory_bytes(text):
    value, unit = text.split()
    if unit != 'GiB' or not math.isfinite(float(value)) or not 0 < float(value) <= 5:
        raise ValueError('runtime memory must be finite, positive and at most 5 GiB')
    return int(float(value) * 2**30)


def validate_record(path, order, expected_sha=None):
    if expected_sha is not None and digest(path) != expected_sha:
        raise ValueError('reused record digest differs: ' + str(path))
    data = json.loads(Path(path).read_text())
    geometry = order['structure']
    fields = dict(status='computed', source_input_sha256=order['source_input_sha256'],
                  method='wb97m-d3bj/def2-tzvppd', psi4_version='1.10.2', formal_charge=0,
                  multiplicity=1, positions_angstrom=geometry['positions_angstrom'],
                  atomic_numbers=geometry['atomic_numbers'], settings=order['settings'],
                  basis_file_sha256=order['basis_file_sha256'], network_denied=True, threads=2)
    if any(data.get(key) != value for key, value in fields.items()):
        raise ValueError('reference record convention/geometry/settings differs: ' + str(path))
    if data.get('name') not in (order['job_name'], geometry['name']):
        raise ValueError('reference record name differs')
    energy = float(data['energy_hartree'])
    gradient = data['gradient_hartree_bohr']
    if (not math.isfinite(energy) or len(gradient) != len(geometry['atomic_numbers'])
            or any(len(row) != 3 or any(not math.isfinite(float(v)) for v in row) for row in gradient)):
        raise ValueError('nonfinite or malformed reference energy/gradient')
    variables = data['quantum_energy_variables']
    if ('DISPERSION CORRECTION ENERGY' not in variables
            or abs(variables.get('DFT VV10 ENERGY', 0.)) > 1e-15
            or any(not math.isfinite(float(v)) for v in variables.values())):
        raise ValueError('reference dispersion convention differs')
    if not math.isfinite(float(data['wall_seconds'])) or data['wall_seconds'] < 0:
        raise ValueError('invalid worker wall time')
    memory_bytes(data['memory'])
    return data


def history(args, approval, orders):
    supplied = [args.resume_from, args.stop_state, args.prior_launch]
    if not any(supplied):
        return {}, 0., {}
    if not all(supplied):
        raise ValueError('recovery requires prior attempt, stop state and launch metadata together')
    previous = Path(args.resume_from).resolve()
    stop = json.loads(Path(args.stop_state).read_text())
    launch = json.loads(Path(args.prior_launch).read_text())
    if (launch['input_manifest_sha256'] != approval['input_manifest_sha256']
            or launch['approval_sha256'] != digest(args.approval)
            or stop['expected_count'] != len(orders)):
        raise ValueError('historical launch/stop plan identity differs')
    saved = {}
    for entry in stop['completed']:
        name = entry['name']
        if name not in orders or name in saved or entry['file'] != name + '.json':
            raise ValueError('invalid historical record name')
        path = previous / 'records' / entry['file']
        record = validate_record(path, orders[name], entry['sha256'])
        if record['wall_seconds'] != entry['wall_seconds']:
            raise ValueError('historical worker timing differs')
        saved[name] = path
    if (set(stop['remaining']) != set(orders) - set(saved)
            or stop['remaining_count'] != len(orders) - len(saved)):
        raise ValueError('historical queue accounting differs')
    observed = {p.stem for p in (previous / 'records').glob('*.json')}
    if observed != set(saved):
        raise ValueError('historical attempt contains unaccounted records')
    elapsed = (dt.datetime.fromisoformat(stop['recorded_utc'])
               - dt.datetime.fromisoformat(launch['recorded_utc'])).total_seconds()
    elapsed = max(elapsed, sum(json.loads(p.read_text())['wall_seconds'] for p in saved.values()))
    if not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError('invalid historical budget debit')
    identity = dict(attempt=str(previous), stop_state_sha256=digest(args.stop_state),
                    launch_sha256=digest(args.prior_launch), prior_wall_seconds=elapsed,
                    note='launch-to-stop debit includes coordinator overhead; no exit receipts inferred')
    return saved, elapsed, identity


def validate_environment(python, root):
    prefix = Path(python).resolve().parents[1]
    installed = {}
    for path in (prefix / 'conda-meta').glob('*.json'):
        entry = json.loads(path.read_text())
        installed[entry.get('url', '').rsplit('/', 1)[-1]] = entry.get('sha256')
    expected = {}
    for line in (root / 'reference-explicit.lock').read_text().splitlines():
        if line.startswith('https://'):
            url, sha = line.rsplit('#', 1)
            expected[url.rsplit('/', 1)[-1]] = sha
    if not expected or installed != expected:
        raise ValueError('reference environment differs from the frozen package lock')


def process_identity(pid):
    try:
        fields = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
        return fields[19] if fields[0] != 'Z' else None
    except (OSError, IndexError):
        return None


def measurements(pid=None):
    data = {}
    for name in ('memory.current', 'memory.peak', 'memory.max', 'memory.events'):
        path = Path('/sys/fs/cgroup') / name
        if path.exists():
            raw = path.read_text().strip()
            data[name] = int(raw) if raw.isdigit() else raw
    stat_path = Path('/sys/fs/cgroup') / 'memory.stat'
    if stat_path.exists():
        stats = {key: int(value) for key, value in
                 (line.split() for line in stat_path.read_text().splitlines())}
        data['memory.stat'] = stats
        # Clean page cache and reclaimable slab can be evicted under pressure.
        # Keep anonymous RAM, shared memory, unreclaimable kernel and dirty IO.
        data['memory.pressure_bytes'] = (stats.get('anon', 0) + stats.get('shmem', 0)
            + max(0, stats.get('kernel', 0) - stats.get('slab_reclaimable', 0))
            + stats.get('file_dirty', 0) + stats.get('file_writeback', 0))
    if pid is not None:
        try:
            for line in (Path('/proc') / str(pid) / 'status').read_text().splitlines():
                if line.startswith(('VmRSS:', 'VmHWM:')):
                    data[line.split(':')[0]] = int(line.split()[1]) * 1024
        except FileNotFoundError:
            pass
    data['disk_free_bytes'] = shutil.disk_usage('/workspace').free
    return data


def terminate_group(process):
    # A worker may have spawned a dispersion subprocess; terminate the group
    # even if its group leader has just exited.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def run(args):
    root = Path(args.plan_root).resolve()
    approval, _ = validate_plan(root, args.approval)
    settings = json.loads((root / 'reference-settings.json').read_text())
    orders = queue(root, settings)
    allocation = f'{args.memory_gib:g} GiB'
    allocated_bytes = memory_bytes(allocation)
    cap = approval['approved_resource_cap']
    if cap['cpu_threads'] != 2 or memory_bytes(cap['psi4_memory']) < allocated_bytes:
        raise ValueError('runtime exceeds the authorized resource cap')
    wall_cap = min(settings['wall_cap_hours'], cap['wall_hours']) * 3600
    if args.wall_limit_seconds is not None:
        if not math.isfinite(args.wall_limit_seconds) or args.wall_limit_seconds <= 0:
            raise ValueError('wall limit must be finite and positive')
        wall_cap = min(wall_cap, args.wall_limit_seconds)
    saved, prior_wall, historical = history(args, approval, orders)
    output = Path(args.output).resolve()
    identity = dict(approval_sha256=digest(args.approval),
                    input_manifest_sha256=digest(root / 'input-manifest.json'),
                    reference_settings_sha256=digest(root / 'reference-settings.json'),
                    history=historical)
    if args.check_resume:
        print(json.dumps(dict(expected_count=len(orders), reused_count=len(saved),
                              remaining=[name for name in orders if name not in saved],
                              prior_wall_seconds=prior_wall, remaining_wall_seconds=wall_cap - prior_wall)))
        return 0
    if not args.reference_python:
        raise ValueError('execution requires --reference-python')
    validate_environment(args.reference_python, root)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'coordinator.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another coordinator holds this attempt lock')
        progress_path = output / 'progress.json'
        if progress_path.exists():
            state = json.loads(progress_path.read_text())
            if state['identity'] != identity or set(state['expected_names']) != set(orders):
                raise ValueError('attempt progress identity differs')
            for session in state['sessions']:
                if session['status'] == 'running':
                    child = session.get('active_worker')
                    actual_identity = process_identity(child['pid']) if child else None
                    if actual_identity is not None and (child['start_ticks'] is None or actual_identity == child['start_ticks']):
                        raise ValueError('old quantum worker remains active; refuse concurrent recovery')
                    session['wall_seconds'] = max(session['wall_seconds'],
                        (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(session['started_utc'])).total_seconds())
                    session.update(status='interrupted', ended_utc=utc(),
                                   note='conservatively debited until recovery; no coordinator exit invented')
            for name, sha in state['record_hashes'].items():
                validate_record(output / 'records' / (name + '.json'), orders[name], sha)
        else:
            if any(p.name != 'coordinator.lock' for p in output.iterdir()):
                raise ValueError('unrecognized nonempty attempt directory')
            (output / 'records').mkdir()
            (output / 'jobs').mkdir()
            state = dict(identity=identity, expected_names=list(orders), record_hashes={},
                         provenance={}, sessions=[], prior_wall_seconds=prior_wall,
                         ready_for_comparison=False)
            for name, path in saved.items():
                target = output / 'records' / (name + '.json')
                with target.open('xb') as stream:
                    stream.write(path.read_bytes())
                state['record_hashes'][name] = digest(target)
                state['provenance'][name] = dict(source=str(path), recovered=True, coordinator_exit=None,
                                                note='verified completed worker record; exit receipt not inferred')
        # Recover a validated record saved just before a coordinator interruption.
        for name in orders:
            if name in state['record_hashes']:
                continue
            for record in sorted(output.glob('jobs/' + name + '/attempt-*/record.json'), reverse=True):
                data = json.loads(record.read_text())
                if data.get('status') != 'computed':
                    continue
                validate_record(record, orders[name])
                target = output / 'records' / (name + '.json')
                if target.exists():
                    if digest(target) != digest(record):
                        raise ValueError('uncommitted recovered record digest differs')
                else:
                    shutil.copyfile(record, target)
                state['record_hashes'][name] = digest(target)
                state['provenance'][name] = dict(source=str(record), recovered=True, coordinator_exit=None)
                break
        session = dict(started_utc=utc(), status='running', wall_seconds=0., runtime_memory=allocation,
                       wall_cap_seconds=wall_cap, resources_at_start=measurements())
        state['sessions'].append(session)
        began = time.monotonic()
        previous_debit = prior_wall + sum(s['wall_seconds'] for s in state['sessions'][:-1])

        def checkpoint():
            session['wall_seconds'] = time.monotonic() - began
            state['wall_seconds_debited'] = previous_debit + session['wall_seconds']
            state['remaining_wall_seconds'] = max(0., wall_cap - state['wall_seconds_debited'])
            state['ready_for_comparison'] = set(state['record_hashes']) == set(orders)
            state['updated_utc'] = utc()
            atomic_dump(progress_path, state)

        checkpoint()
        for name, original_order in orders.items():
            if name in state['record_hashes']:
                continue
            checkpoint()
            if state['remaining_wall_seconds'] <= .02:
                session['stop_reason'] = 'budget_exhausted'
                break
            parent = output / 'jobs' / name
            parent.mkdir(exist_ok=True)
            attempt = parent / f'attempt-{len(list(parent.glob("attempt-*"))) + 1:04d}'
            attempt.mkdir()
            scratch = attempt / 'scratch'
            scratch.mkdir()
            record = attempt / 'record.json'
            order = dict(original_order, output=str(record), scratch_directory=str(scratch),
                         runtime_memory=allocation, runtime_memory_bytes=allocated_bytes)
            exclusive_dump(attempt / 'order.json', order)
            command = [str(Path(args.reference_python).resolve()),
                       str(Path(__file__).with_name('generate_neutral_quantum.py').resolve()),
                       '--worker', str(attempt / 'order.json')]
            receipt = dict(name=name, command=command, started_utc=utc(),
                           resources_before=measurements(), runtime_memory=allocation)
            worker_started = time.monotonic()
            reason = None
            process = None
            try:
                with (attempt / 'launcher.txt').open('x') as log:
                    process = subprocess.Popen(command, cwd=attempt, stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    session['active_worker'] = dict(pid=process.pid, start_ticks=process_identity(process.pid),
                                                    name=name, attempt=str(attempt))
                    rss_peak = cgroup_peak = 0
                    with (attempt / 'resources.jsonl').open('x') as samples:
                        while process.poll() is None:
                            sample = dict(utc=utc(), **measurements(process.pid))
                            rss_peak = max(rss_peak, sample.get('VmHWM', 0), sample.get('VmRSS', 0))
                            cgroup_peak = max(cgroup_peak, sample.get('memory.current', 0))
                            samples.write(json.dumps(sample) + '\n')
                            samples.flush()
                            checkpoint()
                            if state['remaining_wall_seconds'] <= 0:
                                reason = 'timeout'
                            elif max(sample.get('memory.pressure_bytes', sample.get('memory.current', 0)),
                                     sample.get('VmRSS', 0)) > 7 * 2**30:
                                reason = 'memory_headroom_exhausted'
                            elif sample['disk_free_bytes'] < 2 * 2**30:
                                reason = 'scratch_disk_headroom_exhausted'
                            if reason:
                                terminate_group(process)
                                break
                            time.sleep(min(1., max(.001, state['remaining_wall_seconds'])))
                    receipt.update(exit=process.wait(), reason=reason,
                                   sampled_rss_peak_bytes=rss_peak, sampled_cgroup_peak_bytes=cgroup_peak)
            except BaseException:
                if process is not None:
                    terminate_group(process)
                session.update(status='interrupted', ended_utc=utc())
                checkpoint()
                raise
            finally:
                session.pop('active_worker', None)
            receipt.update(ended_utc=utc(), wall_seconds=time.monotonic() - worker_started,
                           resources_after=measurements())
            if receipt['exit'] == 0 and reason is None:
                try:
                    validate_record(record, order)
                except (ValueError, KeyError, OSError, TypeError) as error:
                    receipt['validation_error'] = repr(error)
                else:
                    target = output / 'records' / (name + '.json')
                    with target.open('xb') as stream:
                        stream.write(record.read_bytes())
                    state['record_hashes'][name] = digest(target)
                    state['provenance'][name] = dict(source=str(record), recovered=False,
                                                    coordinator_exit=receipt['exit'], receipt=str(attempt / 'receipt.json'))
            exclusive_dump(attempt / 'receipt.json', receipt)
            shutil.rmtree(scratch)
            checkpoint()
            print(name, 'exit', receipt['exit'], 'verified', name in state['record_hashes'],
                  'total', len(state['record_hashes']), '/', len(orders), flush=True)
            if reason:
                session['stop_reason'] = reason
                break
        session.update(status='finished', ended_utc=utc(), resources_at_end=measurements())
        checkpoint()
        if state['ready_for_comparison']:
            for name, sha in state['record_hashes'].items():
                validate_record(output / 'records' / (name + '.json'), orders[name], sha)
            manifest = dict(scope='independent quantum references only; no model comparison',
                            approval=approval, **{k: v for k, v in identity.items() if k != 'history'},
                            ready_for_comparison=True,
                            files={'records/' + name + '.json': sha for name, sha in state['record_hashes'].items()},
                            provenance=state['provenance'], sessions=state['sessions'], history=historical,
                            wall_seconds=state['wall_seconds_debited'])
            atomic_dump(output / 'manifest.json', manifest)
        return 0 if state['ready_for_comparison'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan-root', 'approval', 'output'):
        parser.add_argument('--' + name, required=True)
    for name in ('reference-python', 'resume-from', 'stop-state', 'prior-launch'):
        parser.add_argument('--' + name)
    parser.add_argument('--check-resume', action='store_true')
    parser.add_argument('--memory-gib', type=float, default=3.)
    parser.add_argument('--wall-limit-seconds', type=float,
                        help='optional stricter cumulative limit; never raises the approved cap')
    try:
        sys.exit(run(parser.parse_args()))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print('Recovery rejected:', error, file=sys.stderr)
        sys.exit(2)
