
from argparse import Namespace
from pathlib import Path
import hashlib,json,os,sys
config=json.loads(Path(sys.argv[1]).read_text())
sys.path[:0]=[config['source_tools'],config['src']]
import resume_joint_quantum as joint
# Test-process fixture substitution only; production source remains unmodified.
joint.APPROVAL_PATH=Path(config['approval']).resolve()
joint.APPROVAL_SHA256=hashlib.sha256(joint.APPROVAL_PATH.read_bytes()).hexdigest()
if config.get('trace_durability'):
    actual=os.fsync; synced=set(); seen=[]
    def trace(fd):
        path=Path(os.readlink('/proc/self/fd/'+str(fd)))
        if path.name=='progress.json.tmp':
            state=json.loads(path.read_text())
            for name in state['record_hashes']:
                source=Path(state['provenance'][name]['source'])
                receipt=json.loads(source.with_name('receipt.json').read_text())
                required=[source,source.with_name('receipt.json'),source.with_name('order.json'),source.with_name('launch.json')]
                required += [source.parent/filename for filename in receipt['diagnostic_sha256']]
                assert all(p in synced for p in required), ('checkpoint references unsynced evidence',required,synced)
                assert source.with_suffix('.psi4.txt') in synced
                seen.append(name)
        actual(fd);synced.add(path)
    os.fsync=trace
try:
    code=joint.run(Namespace(**config['args']))
    if config.get('trace_durability'):
        Path(config['trace_durability']).write_text(json.dumps(dict(checkpointed_names=seen,synced_paths=sorted(map(str,synced))),indent=2))
    raise SystemExit(code)
except (ValueError,KeyError,OSError,TypeError) as error:
    print('Synthetic fixture rejected:',repr(error),file=sys.stderr)
    raise SystemExit(2)
