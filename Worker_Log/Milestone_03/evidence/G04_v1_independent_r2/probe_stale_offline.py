"""Fresh process: explicit inherited trusted artifact, denied sockets/DNS, empty cache."""
import hashlib,json,os,pathlib,socket
out=pathlib.Path(__file__).parent.resolve();cache=out/'stale-empty-cache';cache.mkdir();assert not list(cache.iterdir())
os.environ['XDG_CACHE_HOME']=str(cache)
def deny(*args,**kwargs):raise AssertionError('review network/DNS access forbidden')
socket.socket.connect=deny;socket.create_connection=deny;socket.getaddrinfo=deny
from atm_mlmm.atm import evaluate_atm,load_bundle
from atm_mlmm.schema import QualificationError
from tests.analytic_oracle import REFERENCE,case,check,expected_linear
source=pathlib.Path('Worker_Log/Milestone_02/evidence/M02_v1')
meta=json.loads((source/'stale-detection.json').read_text());artifact=source/'stale-reproducer.json'
assert hashlib.sha256(artifact.read_bytes()).hexdigest()==meta['file_sha256']
b=load_bundle(artifact,meta['file_sha256'],trusted=True);s=case('rbfe')[-1]
actual=evaluate_atm(b,s,'middle',REFERENCE)
try:check(actual,expected_linear(s,'rbfe',.37))
except QualificationError as e:
 assert str(e)==meta['diagnostic'];print('Expected stale negative:',str(e))
else:raise AssertionError('stale artifact not detected')
print('Trusted legacy identity and fresh empty-cache/no-socket/no-DNS reload established')
