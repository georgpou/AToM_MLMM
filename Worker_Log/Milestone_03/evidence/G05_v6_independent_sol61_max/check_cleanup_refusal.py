"""Independent bounded-refusal check; fake process and virtual time, no workers."""
from pathlib import Path
from types import SimpleNamespace
import datetime
import json
import runpy
import signal
import sys

E = Path(__file__).resolve().parent
REPO = E.parents[3]
sys.path.insert(0, str(REPO / 'tools'))
module = runpy.run_path(str(REPO / 'tools/resume_neutral_quantum.py'))
terminate = module['terminate_group']
namespace = terminate.__globals__
signals = []
waits = []
clock = [0.0]

class ReapedSupervisor:
    pid = 99999999
    returncode = -signal.SIGKILL
    def wait(self, timeout=None):
        waits.append(timeout)
        return self.returncode

namespace['group_members'] = lambda group: [99999998]
namespace['os'] = SimpleNamespace(killpg=lambda pid, sig: signals.append([pid, int(sig)]))
namespace['time'] = SimpleNamespace(monotonic=lambda: clock[0],
                                    sleep=lambda duration: clock.__setitem__(0, clock[0] + duration))
try:
    terminate(ReapedSupervisor())
except ValueError as error:
    assert str(error) == 'worker process group remains active; refuse further scheduling'
    assert signals == [[99999999, int(signal.SIGTERM)], [99999999, int(signal.SIGKILL)]]
    assert waits == [5, None]
    assert 5 <= clock[0] < 5.02
    result = {'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'persistent-group refusal after an already reaped supervisor; fake process and virtual time only',
              'actual_processes_launched': 0, 'signals': signals, 'wait_timeouts': waits,
              'virtual_elapsed_seconds': clock[0], 'error': str(error), 'passed': True,
              'ordering_inspection': 'run calls terminate_group at line 503 before receipt admission, promotion, scratch deletion or next scheduling; cleanup errors propagate through exception handling without reaching those operations'}
    with (E / 'cleanup-refusal-observed.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result))
else:
    raise AssertionError('Unverifiable cleanup was accepted')
