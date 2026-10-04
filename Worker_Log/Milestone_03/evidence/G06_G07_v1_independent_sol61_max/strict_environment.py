"""Run the unchanged installed validator with audit-only output destinations."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path('/workspace/atom-mlmm-g05-v2')
HERE = Path(__file__).resolve().parent
validator = ROOT/'validate.py'
assert validator.read_bytes() == Path('environment/cloud-cpu/validate.py').read_bytes()


def prior():
    files = [ROOT/'latest-validation.json', *(ROOT/'logs').rglob('*')]
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}


before = prior()
with (HERE/'strict-outputs-before.json').open('x') as stream:
    json.dump(before,stream,indent=2);stream.write('\n')
original = Path.__truediv__


def redirect(self,key):
    if self == ROOT and str(key) == 'logs':
        return original(HERE,'strict-logs')
    if self == ROOT and str(key) == 'latest-validation.json':
        return original(HERE,'strict-environment-result.json')
    return original(self,key)


sys.argv = [str(validator),'--root',str(ROOT),'--repository',str(Path.cwd())]
print('Unchanged validator SHA-256:',hashlib.sha256(validator.read_bytes()).hexdigest(),flush=True)
print('Only logs, prep and latest-result output paths are redirected to new audit evidence.',flush=True)
Path.__truediv__ = redirect
try:
    runpy.run_path(str(validator),run_name='__main__')
finally:
    Path.__truediv__ = original
    after = prior()
    with (HERE/'strict-outputs-after.json').open('x') as stream:
        json.dump(after,stream,indent=2);stream.write('\n')
    assert before == after,'prior environment validation evidence changed'
