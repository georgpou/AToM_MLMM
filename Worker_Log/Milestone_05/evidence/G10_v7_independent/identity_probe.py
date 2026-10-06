"""Frozen repair/source/evidence identity; never loads historical bundles."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
head = git('rev-parse','HEAD').decode().strip()
assert head == 'acfe9f6922d4029f1628aa69d530f0b642f4bb0d'
source = {p.relative_to(ROOT/'src').as_posix():sha(p.read_bytes())
          for p in sorted((ROOT/'src/atm_mlmm').rglob('*.py'))}
assert len(source) == 38
packet = ROOT/'Worker_Log/Milestone_05/evidence/G10_v7_review_packet'
manifest = json.loads((packet/'packet-manifest.json').read_text())
diffs = {}
for name, entry in manifest['diffs'].items():
    raw = gzip.decompress((packet/(name+'.diff.gz')).read_bytes())
    actual = git('diff',entry['base'],entry['end'],'--','src','tests')
    assert raw == actual and sha(raw) == entry['raw_sha256']
    diffs[name] = {'bytes':len(raw),'raw_sha256':sha(raw)}
assert not git('diff',manifest['worker_submission'],head,'--','src','tests','fixtures','environment')
protected = ['fixtures','environment','assets','models','docs/project-0/specs',
             'Worker_Log/Milestone_03','Worker_Log/Milestone_04',
             'Worker_Log/Milestone_05/evidence/G10_v5',
             'Worker_Log/Milestone_05/evidence/G10_v5_independent',
             'Worker_Log/Milestone_05/Gate_10_v5_audit.md']
assert not git('diff','a90e192ec0d87524e8fbf77a18d62b4b81a37195',head,'--',*protected)
changed_source = git('diff','a90e192',head,'--name-only','--','src').decode().splitlines()
assert changed_source == ['src/atm_mlmm/exchange.py','src/atm_mlmm/exchange_journal.py']
entries = []
for line in (ROOT/'Worker_Log/Milestone_05/evidence/G10_v7/sha256sums.txt').read_text().splitlines():
    match = re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
    if match:
        digest, name = match.groups()
        path = Path(name) if name.startswith('/') else ROOT/name
        assert sha(path.read_bytes()) == digest, name
        entries.append({'path':name,'sha256':digest})
assert len(entries) == 31
bundles = []
for worker in sorted(Path('/workspace/G10_v7_artifacts/v7-attempt-001').glob('*/*/worker')):
    doc = json.loads((worker/'manifest.json').read_text())
    prefix = 'runtime/source/'
    bundled = {name[len(prefix):]:digest for name,digest in doc['files'].items()
               if name.startswith(prefix) and name.endswith('.py')}
    assert bundled == source
    for name, digest in doc['files'].items():
        path = worker/name
        assert not path.is_symlink() and sha(path.read_bytes()) == digest
    bundles.append({'path':str(worker),'source_files':len(bundled),'manifest_files':len(doc['files'])})
assert len(bundles) == 8
logs = {}
root_record = json.loads((packet/'root-verification.json').read_text())
for name, entry in root_record['logs'].items():
    path = ROOT/'Worker_Log/Milestone_05/evidence/G10_v7'/name
    raw = gzip.decompress(path.read_bytes()) if name.endswith('.gz') else path.read_bytes()
    assert sha(raw) == entry['raw_sha256']
    logs[name] = {'raw_sha256':sha(raw),'tail':raw.decode().splitlines()[-3:]}
result = dict(reviewed_head=head, worker_submission=manifest['worker_submission'],
              source_sha256=source, changed_source=changed_source, diffs=diffs,
              verified_manifest_entries=entries, current_bundles=bundles, logs=logs,
              protected_trees_unchanged=protected,
              accepted_numerical_proof_reuse='unchanged equations/adapter/scientific inputs; v5 report retained',
              finished_utc=datetime.now(timezone.utc).isoformat(), exit_status=0)
(HERE/'identity-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'head':head,'source_files':38,'submitted_hashes':31,'bundles':8,'exit_status':0}))
