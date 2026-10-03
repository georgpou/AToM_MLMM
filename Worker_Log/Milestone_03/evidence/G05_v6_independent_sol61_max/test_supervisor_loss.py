"""Focused independent process-lifecycle probe; explicit non-QM stand-ins only."""
from pathlib import Path
import json
import os
import runpy
import signal
import sys
import time

E=Path(__file__).resolve().parent
REPO=E.parents[3]
UNIT=runpy.run_path(str(REPO/'tests/unit/test_quantum_recovery.py'))


def test_coordinator_cleans_remaining_group_when_supervisor_is_killed():
    work=E/'supervisor-loss-probe'
    work.mkdir(exist_ok=False)
    original=UNIT['synthetic'].__wrapped__(work)
    marker=work/'orphan.json'
    later=work/'later-job.json'
    # Keep the stub inside its synthetic reference prefix so normal environment
    # validation succeeds. This replacement is new evidence, never production.
    replacement=original[2].with_name('audit-worker')
    header,body=original[2].read_text().split('\n',1)
    injection=(
        "\nimport signal\n"
        f"marker=Path({str(marker)!r});later=Path({str(later)!r})\n"
        "if name=='one':\n"
        "    marker.write_text(json.dumps({'pid':os.getpid(),'group':os.getpgrp(),'supervisor':os.getppid(),'kind':'SYNTHETIC NON-QM WORKER'}))\n"
        "    os.kill(os.getppid(),signal.SIGKILL)\n"
        "    time.sleep(30)\n"
        "elif not later.exists():\n"
        "    info=json.loads(marker.read_text())\n"
        "    try:\n"
        "        fields=(Path('/proc')/str(info['pid'])/'stat').read_text().rsplit(')',1)[1].split()\n"
        "        live=fields[0]!='Z'\n"
        "    except OSError:live=False\n"
        "    later.write_text(json.dumps({'name':name,'old_reference_child_live_at_next_launch':live,'old_reference_pid':info['pid']}))\n"
    )
    needle="mode=os.environ.get('QUANTUM_RECOVERY_TEST_MODE', '')\n"
    body=body.replace(needle,needle+injection)
    replacement.open('x').write(header+'\n'+body)
    replacement.chmod(0o755)
    synthetic=(*original[:2],replacement,original[3])
    orphan=None
    try:
        result=UNIT['run_synthetic'](synthetic)
        assert marker.exists(), 'Probe did not reach a running reference stub'
        orphan=json.loads(marker.read_text())
        assert later.exists(), 'Probe did not reach a subsequent launch'
        subsequent=json.loads(later.read_text())
        output=synthetic[-1]
        receipt=json.loads((output/'jobs/one/attempt-0001/receipt.json').read_text())
        pid_path=Path('/proc')/str(orphan['pid'])/'stat'
        live=pid_path.exists() and pid_path.read_text().rsplit(')',1)[1].split()[0]!='Z'
        observed={'coordinator_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
                  'first_supervisor_receipt':receipt,'orphan':orphan,'later_launch':subsequent,
                  'reference_child_live_after_coordinator_exit':live,
                  'published_records':sorted(p.stem for p in (output/'records').glob('*.json')),
                  'first_scratch_removed':not (output/'jobs/one/attempt-0001/scratch').exists(),
                  'requirement':'No subsequent reference launch until all same-group children from failed supervisor are gone'}
        with (work/'observed.json').open('x') as stream:json.dump(observed,stream,indent=2);stream.write('\n')
        assert not subsequent['old_reference_child_live_at_next_launch'], 'Coordinator scheduled another job while the previous reference child remained live'
        assert not live, 'Reference child survived coordinator completion'
    finally:
        if orphan is None and marker.exists():orphan=json.loads(marker.read_text())
        if orphan:
            try:os.killpg(orphan['group'],signal.SIGKILL)
            except ProcessLookupError:pass
            deadline=time.monotonic()+3
            while time.monotonic()<deadline:
                try:fields=(Path('/proc')/str(orphan['pid'])/'stat').read_text().rsplit(')',1)[1].split()
                except OSError:break
                if fields[0]=='Z':break
                time.sleep(.01)
