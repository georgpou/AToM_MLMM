"""Run a CPU check and preserve output, one-second resources and actual exit.

This is validation telemetry, not a QM supervisor or an authorization mechanism.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time


CGROUP=Path('/sys/fs/cgroup')


def counters():
    return {line.split()[0]:int(line.split()[1]) for line in (CGROUP/'memory.events').read_text().splitlines()}


def resources(root_pid):
    processes={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            stat=(p/'stat').read_text().rsplit(')',1)[1].split()
            status=(p/'status').read_text().splitlines()
            rss=next((int(line.split()[1])*1024 for line in status if line.startswith('VmRSS:')),0)
            processes[int(p.name)]=(int(stat[1]),rss)
        except (OSError,ValueError,IndexError):continue
    descendants={root_pid}
    while True:
        added={pid for pid,(parent,_) in processes.items() if parent in descendants}-descendants
        if not added:break
        descendants|=added
    stats={line.split()[0]:int(line.split()[1]) for line in (CGROUP/'memory.stat').read_text().splitlines()}
    return dict(cgroup_current_bytes=int((CGROUP/'memory.current').read_text()),
        cgroup_anon_bytes=stats['anon'],cgroup_file_bytes=stats['file'],memory_events=counters(),
        process_tree_rss_bytes=sum(processes.get(pid,(0,0))[1] for pid in descendants),
        process_ids=sorted(descendants),free_disk_bytes=os.statvfs('.').f_bavail*os.statvfs('.').f_frsize)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args();command=args.command
    if command[:1]==['--']:command=command[1:]
    if not command:parser.error('a command is required')
    if args.output.exists():raise FileExistsError('preserve prior validation output')
    args.output.mkdir(parents=True)
    before=counters();samples=[];started=time.monotonic()
    with (args.output/'command.log').open('x') as log,(args.output/'resources.jsonl').open('x') as telemetry:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while True:
            sample=resources(process.pid)
            sample['elapsed_seconds']=time.monotonic()-started
            samples.append(sample);telemetry.write(json.dumps(sample)+'\n');telemetry.flush()
            status=process.poll()
            if status is not None:break
            time.sleep(1.)
    after=counters()
    result=dict(command=command,cwd=str(Path.cwd()),exit_code=status,wall_seconds=time.monotonic()-started,
        finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        memory_cap_bytes=int((CGROUP/'memory.max').read_text()),cpu_quota=(CGROUP/'cpu.max').read_text().strip(),
        peak_sampled_process_tree_rss_bytes=max(s['process_tree_rss_bytes'] for s in samples),
        child_maxrss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,
        peak_sampled_cgroup_bytes=max(s['cgroup_current_bytes'] for s in samples),
        memory_events_before=before,memory_events_after=after,memory_event_deltas={k:after[k]-before[k] for k in before},
        minimum_free_disk_bytes=min(s['free_disk_bytes'] for s in samples),samples=len(samples))
    with (args.output/'result.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2));return status


if __name__=='__main__':sys.exit(main())
