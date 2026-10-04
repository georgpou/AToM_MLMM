"""Hold the queue lease and stop an entire worker group on coordinator loss.

The coordinator passes a lock descriptor and an authorization/liveness pipe.
No reference executable starts until its supervisor identity is checkpointed.
This module imports only the standard library and JSON publication helpers.
"""
import argparse
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time

from generate_neutral_quantum import dump


def group_members():
    group = os.getpgrp()
    members = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit() or int(path.name) == os.getpid():
            continue
        try:
            fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            if fields[0] != 'Z' and int(fields[2]) == group:
                members.append(int(path.name))
        except (OSError, IndexError, ValueError):
            continue
    return members


def stop_group():
    # This supervisor is the live session/group leader. Keeping it alive during
    # SIGTERM prevents PGID reuse; SIGKILL includes it if descendants persist.
    os.killpg(os.getpgrp(), signal.SIGTERM)
    deadline = time.monotonic() + 5
    while group_members() and time.monotonic() < deadline:
        time.sleep(.02)
    if group_members():
        os.killpg(os.getpgrp(), signal.SIGKILL)


def supervise(launch_path, lease_fd, control_fd):
    if os.getpgrp() != os.getpid():
        raise ValueError('supervisor requires its own process group')
    os.fstat(lease_fd)  # The inherited open-file description holds the flock.
    launch = json.loads(Path(launch_path).read_text())
    stopped = False

    def request_stop(*_):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    fields = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()
    dump(Path(launch_path).with_name('worker-identity.json'),
         dict(pid=os.getpid(), start_ticks=fields[19], group=os.getpgrp()))
    # EOF before authorization means the coordinator never committed launch.
    while not stopped:
        readable, _, _ = select.select([control_fd], [], [], .1)
        if readable:
            if os.read(control_fd, 1) != b'G':
                return 125
            break
    else:
        return 125
    process = None
    try:
        # Keep both lease holders in this group; only the supervisor inherits
        # the pipe so that coordinator death reliably produces EOF.
        process = subprocess.Popen(launch['command'], cwd=Path(launch_path).parent,
                                   pass_fds=(lease_fd,))
        try:
            fields = (Path('/proc') / str(process.pid) / 'stat').read_text().rsplit(')', 1)[1].split()
            start_ticks = fields[19]
        except (OSError, IndexError):
            start_ticks = None  # An already-exited child is still waited below.
        dump(Path(launch_path).with_name('reference-worker-identity.json'),
             dict(pid=process.pid, start_ticks=start_ticks, group=os.getpgrp()))
        while process.poll() is None:
            readable, _, _ = select.select([control_fd], [], [], .1)
            if stopped or (readable and os.read(control_fd, 1) == b''):
                stop_group()
                process.wait()
                return 125
        code = process.wait()
        if group_members():
            stop_group()
        return code if code >= 0 else 128 - code
    except BaseException:
        stop_group()
        if process is not None:
            process.wait()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch', required=True)
    parser.add_argument('--lease-fd', required=True, type=int)
    parser.add_argument('--control-fd', required=True, type=int)
    args = parser.parse_args()
    raise SystemExit(supervise(args.launch, args.lease_fd, args.control_fd))
