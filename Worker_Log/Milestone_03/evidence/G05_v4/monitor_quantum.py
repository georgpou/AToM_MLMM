"""Read-only live summary; every authoritative sample remains in the attempt."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3] / 'Milestone_00/evidence/M00_reference_v3/quantum-attempt-v2'
state = json.loads((root / 'progress.json').read_text())
session = state['sessions'][-1]
worker = session.get('active_worker')
data = dict(completed=len(state['record_hashes']), total=len(state['expected_names']),
            remaining_hours=round(state['remaining_wall_seconds'] / 3600, 3),
            session_status=session['status'], ready=state['ready_for_comparison'],
            updated_utc=state['updated_utc'])
if worker:
    attempt = Path(worker['attempt'])
    lines = (attempt / 'resources.jsonl').read_text().splitlines()
    if lines:
        last = json.loads(lines[-1])
        data.update(active=worker['name'], rss_gib=round(last.get('VmRSS', 0) / 2**30, 3),
                    peak_rss_gib=round(max(json.loads(s).get('VmHWM', 0) for s in lines) / 2**30, 3),
                    unreclaimable_gib=round(last.get('memory.pressure_bytes', 0) / 2**30, 3),
                    disk_free_gib=round(last['disk_free_bytes'] / 2**30, 2))
    log = attempt / 'record.psi4.txt'
    if log.exists():
        iterations = [line.strip() for line in log.read_text().splitlines() if '@DF-RKS iter' in line]
        if iterations:
            data['scf_latest'] = iterations[-1]
print(json.dumps(data))
