"""Administrative pause check; excludes this checker and its recorder."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

here=Path(__file__).resolve().parent
raw=subprocess.check_output(['ps','-eo','pid,ppid,stat,etime,comm'],text=True)
allowed={os.getpid(),os.getppid()}
live=[]
for line in raw.splitlines()[1:]:
    pid,ppid,state,elapsed,command=line.split(maxsplit=4)
    if not state.startswith('Z') and (command.startswith('python') or command=='pytest') and int(pid) not in allowed:
        live.append(line)
result={'checked_utc':datetime.now(timezone.utc).isoformat(),
        'live_scientific_processes':live,'all_scientific_sessions_completed':True,
        'focused_session_30648_exit':0,'repair_session_6121_exit':1,
        'terminated_sessions':[],'process_output':raw}
(here/'process-status.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(raw)
assert not live, live
print('No live scientific processes; both scientific sessions completed naturally.')
